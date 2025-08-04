"""
PM2 log management for the monitoring dashboard.

This module provides PM2 log viewing, monitoring, and analysis capabilities
including real-time log streaming, log file management, and log parsing.
"""

import logging
import json
import re
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Generator, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from threading import RLock, Thread
from collections import deque, defaultdict
import time
import glob

from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Represents a single log entry."""
    timestamp: datetime
    process_name: str
    process_id: Optional[int]
    log_type: str  # stdout, stderr, pm2
    message: str
    level: str = "info"  # debug, info, warn, error
    raw_line: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'process_name': self.process_name,
            'process_id': self.process_id,
            'log_type': self.log_type,
            'message': self.message,
            'level': self.level,
            'raw_line': self.raw_line
        }


@dataclass 
class LogFile:
    """Information about a log file."""
    path: str
    process_name: str
    log_type: str  # stdout, stderr, pm2
    size: int
    modified: datetime
    line_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'path': self.path,
            'process_name': self.process_name,
            'log_type': self.log_type,
            'size': self.size,
            'modified': self.modified.isoformat(),
            'line_count': self.line_count
        }


@dataclass
class LogStats:
    """Log statistics for a process."""
    process_name: str
    total_lines: int
    error_count: int
    warning_count: int
    recent_activity: datetime
    log_files: List[LogFile]
    size_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'process_name': self.process_name,
            'total_lines': self.total_lines,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'recent_activity': self.recent_activity.isoformat(),
            'log_files': [f.to_dict() for f in self.log_files],
            'size_mb': self.size_mb
        }


class LogPatternMatcher:
    """Matches log patterns and extracts log levels."""
    
    def __init__(self):
        # Common log level patterns
        self.level_patterns = [
            (re.compile(r'\b(ERROR|ERR)\b', re.IGNORECASE), 'error'),
            (re.compile(r'\b(WARN|WARNING)\b', re.IGNORECASE), 'warn'),
            (re.compile(r'\b(INFO|INFORMATION)\b', re.IGNORECASE), 'info'),
            (re.compile(r'\b(DEBUG|DBG)\b', re.IGNORECASE), 'debug'),
            (re.compile(r'\b(FATAL|CRITICAL)\b', re.IGNORECASE), 'error'),
        ]
        
        # PM2 timestamp patterns
        self.timestamp_patterns = [
            re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'),  # YYYY-MM-DD HH:MM:SS
            re.compile(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})'),  # MM/DD/YYYY HH:MM:SS
            re.compile(r'(\w{3} \d{2} \d{2}:\d{2}:\d{2})'),        # Mon DD HH:MM:SS
        ]
    
    def parse_log_line(self, line: str, process_name: str, log_type: str) -> LogEntry:
        """Parse a raw log line into a LogEntry."""
        # Extract timestamp
        timestamp = self._extract_timestamp(line)
        
        # Extract log level
        level = self._extract_level(line)
        
        # Clean message (remove timestamp and other prefixes)
        message = self._clean_message(line)
        
        # Extract process ID if present
        process_id = self._extract_process_id(line)
        
        return LogEntry(
            timestamp=timestamp,
            process_name=process_name,
            process_id=process_id,
            log_type=log_type,
            message=message,
            level=level,
            raw_line=line.strip()
        )
    
    def _extract_timestamp(self, line: str) -> datetime:
        """Extract timestamp from log line."""
        for pattern in self.timestamp_patterns:
            match = pattern.search(line)
            if match:
                timestamp_str = match.group(1)
                try:
                    # Try different timestamp formats
                    formats = [
                        '%Y-%m-%d %H:%M:%S',
                        '%m/%d/%Y %H:%M:%S',
                        '%b %d %H:%M:%S'
                    ]
                    
                    for fmt in formats:
                        try:
                            return datetime.strptime(timestamp_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    pass
        
        # Default to current time if no timestamp found
        return datetime.now()
    
    def _extract_level(self, line: str) -> str:
        """Extract log level from log line."""
        for pattern, level in self.level_patterns:
            if pattern.search(line):
                return level
        
        return "info"  # Default level
    
    def _clean_message(self, line: str) -> str:
        """Clean log message by removing timestamps and PM2 prefixes."""
        # Remove common PM2 prefixes
        cleaned = re.sub(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\s*', '', line)
        cleaned = re.sub(r'^\w+\s+\|\s*', '', cleaned)
        cleaned = re.sub(r'^\[\w+\]\s*', '', cleaned)
        
        return cleaned.strip()
    
    def _extract_process_id(self, line: str) -> Optional[int]:
        """Extract process ID from log line if present."""
        # Look for PID patterns
        pid_match = re.search(r'\bPID[:\s]+(\d+)\b', line, re.IGNORECASE)
        if pid_match:
            return int(pid_match.group(1))
        
        return None


class PM2LogManager:
    """
    Manages PM2 log viewing and monitoring.
    
    Provides log file discovery, real-time monitoring, log parsing,
    and log analysis capabilities for PM2 processes.
    """
    
    def __init__(self, pm2_home: Optional[str] = None):
        """
        Initialize PM2 log manager.
        
        Args:
            pm2_home: PM2 home directory (default: ~/.pm2)
        """
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # PM2 paths
        self.pm2_home = Path(pm2_home) if pm2_home else Path.home() / ".pm2"
        self.logs_dir = self.pm2_home / "logs"
        
        # Log pattern matcher
        self.pattern_matcher = LogPatternMatcher()
        
        # Log buffers for real-time viewing
        self._log_buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._monitoring_threads: Dict[str, Thread] = {}
        self._monitoring_active: Dict[str, bool] = {}
        
        # Create logs directory if it doesn't exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"PM2LogManager initialized with logs directory: {self.logs_dir}")
    
    def get_log_files(self) -> List[LogFile]:
        """
        Get list of all PM2 log files.
        
        Returns:
            List of LogFile objects
        """
        with self._lock:
            log_files = []
            
            try:
                # Search for log files in PM2 logs directory
                patterns = [
                    "*.log",
                    "*.out",
                    "*.err"
                ]
                
                for pattern in patterns:
                    for file_path in self.logs_dir.glob(pattern):
                        try:
                            stat = file_path.stat()
                            
                            # Parse filename to get process name and log type
                            process_name, log_type = self._parse_log_filename(file_path.name)
                            
                            log_file = LogFile(
                                path=str(file_path),
                                process_name=process_name,
                                log_type=log_type,
                                size=stat.st_size,
                                modified=datetime.fromtimestamp(stat.st_mtime)
                            )
                            
                            log_files.append(log_file)
                            
                        except Exception as e:
                            logger.warning(f"Failed to process log file {file_path}: {e}")
                
                # Sort by modification time (newest first)
                log_files.sort(key=lambda x: x.modified, reverse=True)
                
                logger.debug(f"Found {len(log_files)} log files")
                return log_files
                
            except Exception as e:
                logger.error(f"Failed to get log files: {e}")
                return []
    
    def get_process_names(self) -> List[str]:
        """
        Get list of process names that have log files.
        
        Returns:
            List of process names
        """
        log_files = self.get_log_files()
        process_names = list(set(lf.process_name for lf in log_files))
        return sorted(process_names)
    
    def read_log_file(self, file_path: str, lines: int = 100, offset: int = 0) -> List[LogEntry]:
        """
        Read log entries from a file.
        
        Args:
            file_path: Path to log file
            lines: Number of lines to read
            offset: Line offset to start from
            
        Returns:
            List of LogEntry objects
        """
        try:
            log_path = Path(file_path)
            
            if not log_path.exists():
                logger.error(f"Log file not found: {file_path}")
                return []
            
            # Parse filename to get process info
            process_name, log_type = self._parse_log_filename(log_path.name)
            
            entries = []
            
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read all lines first to handle offset properly
                all_lines = f.readlines()
                
                # Apply offset and limit
                start_idx = max(0, len(all_lines) - offset - lines)
                end_idx = len(all_lines) - offset if offset > 0 else len(all_lines)
                
                selected_lines = all_lines[start_idx:end_idx]
                
                for line in selected_lines:
                    if line.strip():
                        entry = self.pattern_matcher.parse_log_line(line, process_name, log_type)
                        entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to read log file {file_path}: {e}")
            return []
    
    def get_process_logs(self, process_name: str, lines: int = 100, include_stderr: bool = True) -> List[LogEntry]:
        """
        Get log entries for a specific process.
        
        Args:
            process_name: Name of the process
            lines: Number of lines to return
            include_stderr: Whether to include stderr logs
            
        Returns:
            List of LogEntry objects sorted by timestamp
        """
        with self._lock:
            all_entries = []
            
            # Get log files for this process
            log_files = [lf for lf in self.get_log_files() if lf.process_name == process_name]
            
            # Filter by log type if needed
            if not include_stderr:
                log_files = [lf for lf in log_files if lf.log_type != 'stderr']
            
            # Read entries from each file
            for log_file in log_files:
                entries = self.read_log_file(log_file.path, lines)
                all_entries.extend(entries)
            
            # Sort by timestamp (newest first)
            all_entries.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Limit to requested number of lines
            return all_entries[:lines]
    
    def get_live_logs(self, process_name: str, max_lines: int = 50) -> List[LogEntry]:
        """
        Get live log entries from buffer for a process.
        
        Args:
            process_name: Name of the process
            max_lines: Maximum number of lines to return
            
        Returns:
            List of recent LogEntry objects
        """
        with self._lock:
            buffer = self._log_buffers.get(process_name, deque())
            return list(buffer)[-max_lines:]
    
    def start_live_monitoring(self, process_name: str) -> bool:
        """
        Start live log monitoring for a process.
        
        Args:
            process_name: Name of the process to monitor
            
        Returns:
            True if monitoring started successfully
        """
        with self._lock:
            try:
                if process_name in self._monitoring_threads:
                    logger.info(f"Live monitoring already active for {process_name}")
                    return True
                
                # Create monitoring thread
                self._monitoring_active[process_name] = True
                thread = Thread(
                    target=self._monitor_process_logs,
                    args=(process_name,),
                    daemon=True
                )
                
                self._monitoring_threads[process_name] = thread
                thread.start()
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.MONITORING,
                    change_type=ChangeType.CREATE,
                    description=f"Started live log monitoring for {process_name}",
                    details={
                        'process_name': process_name,
                        'monitoring_type': 'live_logs'
                    }
                )
                
                logger.info(f"Started live log monitoring for {process_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to start live monitoring for {process_name}: {e}")
                return False
    
    def stop_live_monitoring(self, process_name: str) -> bool:
        """
        Stop live log monitoring for a process.
        
        Args:
            process_name: Name of the process
            
        Returns:
            True if monitoring stopped successfully
        """
        with self._lock:
            try:
                if process_name not in self._monitoring_threads:
                    logger.info(f"No live monitoring active for {process_name}")
                    return True
                
                # Stop monitoring
                self._monitoring_active[process_name] = False
                
                # Wait for thread to finish (with timeout)
                thread = self._monitoring_threads[process_name]
                thread.join(timeout=5.0)
                
                # Clean up
                del self._monitoring_threads[process_name]
                del self._monitoring_active[process_name]
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.MONITORING,
                    change_type=ChangeType.DELETE,
                    description=f"Stopped live log monitoring for {process_name}",
                    details={
                        'process_name': process_name,
                        'monitoring_type': 'live_logs'
                    }
                )
                
                logger.info(f"Stopped live log monitoring for {process_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to stop live monitoring for {process_name}: {e}")
                return False
    
    def get_log_stats(self, process_name: Optional[str] = None) -> List[LogStats]:
        """
        Get log statistics for processes.
        
        Args:
            process_name: Specific process name, or None for all processes
            
        Returns:
            List of LogStats objects
        """
        with self._lock:
            try:
                log_files = self.get_log_files()
                
                # Group by process name
                process_files: Dict[str, List[LogFile]] = defaultdict(list)
                for lf in log_files:
                    if process_name is None or lf.process_name == process_name:
                        process_files[lf.process_name].append(lf)
                
                stats_list = []
                
                for proc_name, files in process_files.items():
                    # Calculate statistics
                    total_size = sum(f.size for f in files)
                    size_mb = total_size / (1024 * 1024)
                    
                    # Get recent activity
                    recent_activity = max(f.modified for f in files) if files else datetime.now()
                    
                    # Count lines and analyze log levels (sample from recent logs)
                    total_lines = 0
                    error_count = 0
                    warning_count = 0
                    
                    # Sample recent entries for analysis
                    recent_entries = self.get_process_logs(proc_name, lines=200)
                    total_lines = len(recent_entries)
                    
                    for entry in recent_entries:
                        if entry.level == 'error':
                            error_count += 1
                        elif entry.level == 'warn':
                            warning_count += 1
                    
                    stats = LogStats(
                        process_name=proc_name,
                        total_lines=total_lines,
                        error_count=error_count,
                        warning_count=warning_count,
                        recent_activity=recent_activity,
                        log_files=files,
                        size_mb=size_mb
                    )
                    
                    stats_list.append(stats)
                
                # Sort by recent activity
                stats_list.sort(key=lambda x: x.recent_activity, reverse=True)
                
                return stats_list
                
            except Exception as e:
                logger.error(f"Failed to get log stats: {e}")
                return []
    
    def search_logs(self, query: str, process_name: Optional[str] = None, 
                   start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                   log_level: Optional[str] = None, max_results: int = 100) -> List[LogEntry]:
        """
        Search log entries by criteria.
        
        Args:
            query: Search query (regex supported)
            process_name: Filter by process name
            start_time: Filter by start time
            end_time: Filter by end time
            log_level: Filter by log level
            max_results: Maximum number of results
            
        Returns:
            List of matching LogEntry objects
        """
        try:
            # Compile search pattern
            try:
                pattern = re.compile(query, re.IGNORECASE)
            except re.error:
                # If regex fails, treat as literal string
                pattern = re.compile(re.escape(query), re.IGNORECASE)
            
            # Get processes to search
            if process_name:
                process_names = [process_name]
            else:
                process_names = self.get_process_names()
            
            matching_entries = []
            
            for proc_name in process_names:
                # Get recent logs for the process
                entries = self.get_process_logs(proc_name, lines=1000)
                
                for entry in entries:
                    # Apply filters
                    if start_time and entry.timestamp < start_time:
                        continue
                    if end_time and entry.timestamp > end_time:
                        continue
                    if log_level and entry.level != log_level:
                        continue
                    
                    # Search in message
                    if pattern.search(entry.message) or pattern.search(entry.raw_line):
                        matching_entries.append(entry)
                        
                        if len(matching_entries) >= max_results:
                            break
                
                if len(matching_entries) >= max_results:
                    break
            
            # Sort by timestamp (newest first)
            matching_entries.sort(key=lambda x: x.timestamp, reverse=True)
            
            return matching_entries[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to search logs: {e}")
            return []
    
    def clear_logs(self, process_name: str) -> bool:
        """
        Clear log files for a process.
        
        Args:
            process_name: Name of the process
            
        Returns:
            True if logs cleared successfully
        """
        with self._lock:
            try:
                # Get log files for the process
                log_files = [lf for lf in self.get_log_files() if lf.process_name == process_name]
                
                cleared_files = []
                for log_file in log_files:
                    log_path = Path(log_file.path)
                    if log_path.exists():
                        # Truncate file instead of deleting to avoid PM2 issues
                        with open(log_path, 'w') as f:
                            f.truncate(0)
                        cleared_files.append(log_file.path)
                
                # Clear live buffer
                if process_name in self._log_buffers:
                    self._log_buffers[process_name].clear()
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.MONITORING,
                    change_type=ChangeType.DELETE,
                    description=f"Cleared logs for process {process_name}",
                    details={
                        'process_name': process_name,
                        'files_cleared': cleared_files,
                        'file_count': len(cleared_files)
                    }
                )
                
                logger.info(f"Cleared {len(cleared_files)} log files for {process_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to clear logs for {process_name}: {e}")
                return False
    
    def export_logs(self, process_name: str, output_file: str, 
                   start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> bool:
        """
        Export logs to a file.
        
        Args:
            process_name: Name of the process
            output_file: Output file path
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            True if export successful
        """
        try:
            # Get log entries
            entries = self.get_process_logs(process_name, lines=10000)
            
            # Apply time filters
            if start_time or end_time:
                filtered_entries = []
                for entry in entries:
                    if start_time and entry.timestamp < start_time:
                        continue
                    if end_time and entry.timestamp > end_time:
                        continue
                    filtered_entries.append(entry)
                entries = filtered_entries
            
            # Write to file
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"# PM2 Log Export for {process_name}\n")
                f.write(f"# Exported at: {datetime.now().isoformat()}\n")
                f.write(f"# Entries: {len(entries)}\n")
                f.write("\n")
                
                # Write entries (oldest first for export)
                for entry in reversed(entries):
                    f.write(f"[{entry.timestamp.isoformat()}] [{entry.level.upper()}] [{entry.log_type}] {entry.message}\n")
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.MONITORING,
                change_type=ChangeType.CREATE,
                description=f"Exported logs for process {process_name}",
                details={
                    'process_name': process_name,
                    'output_file': output_file,
                    'entries_exported': len(entries),
                    'start_time': start_time.isoformat() if start_time else None,
                    'end_time': end_time.isoformat() if end_time else None
                }
            )
            
            logger.info(f"Exported {len(entries)} log entries to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            return False
    
    def _parse_log_filename(self, filename: str) -> Tuple[str, str]:
        """Parse log filename to extract process name and log type."""
        # Common PM2 log filename patterns
        # app-name-0.log, app-name-error-0.log, app-name-out-0.log
        
        if filename.endswith('.log'):
            base_name = filename[:-4]  # Remove .log extension
            
            # Check for error logs
            if '-error-' in base_name:
                process_name = base_name.split('-error-')[0]
                return process_name, 'stderr'
            
            # Check for out logs
            if '-out-' in base_name:
                process_name = base_name.split('-out-')[0] 
                return process_name, 'stdout'
            
            # Default log (usually stdout)
            if base_name.endswith(('-0', '-1', '-2', '-3', '-4')):
                process_name = base_name[:-2]  # Remove instance number
            else:
                process_name = base_name
                
            return process_name, 'stdout'
        
        # Handle .out and .err files
        if filename.endswith('.out'):
            process_name = filename[:-4]
            return process_name, 'stdout'
        
        if filename.endswith('.err'):
            process_name = filename[:-4]
            return process_name, 'stderr'
        
        # Default case
        return filename, 'stdout'
    
    def _monitor_process_logs(self, process_name: str):
        """Monitor logs for a process in a separate thread."""
        try:
            # Use PM2 logs command for real-time monitoring
            cmd = ['pm2', 'logs', process_name, '--raw', '--lines', '0']
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            logger.info(f"Started PM2 logs monitoring for {process_name}")
            
            while self._monitoring_active.get(process_name, False):
                try:
                    # Read line with timeout
                    line = process.stdout.readline()
                    
                    if line:
                        # Parse log line
                        entry = self.pattern_matcher.parse_log_line(
                            line, process_name, 'stdout'
                        )
                        
                        # Add to buffer
                        with self._lock:
                            self._log_buffers[process_name].append(entry)
                    
                    elif process.poll() is not None:
                        # Process ended
                        break
                    
                    # Small delay to prevent excessive CPU usage
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error reading log line for {process_name}: {e}")
                    time.sleep(1)
            
            # Clean up process
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
            
            logger.info(f"Stopped PM2 logs monitoring for {process_name}")
            
        except Exception as e:
            logger.error(f"Failed to monitor logs for {process_name}: {e}")
        finally:
            # Ensure cleanup
            with self._lock:
                if process_name in self._monitoring_active:
                    del self._monitoring_active[process_name]


# Singleton instance
_pm2_log_manager: Optional[PM2LogManager] = None
_manager_lock = RLock()


def get_pm2_log_manager(pm2_home: Optional[str] = None) -> PM2LogManager:
    """
    Get singleton PM2 log manager instance.
    
    Args:
        pm2_home: PM2 home directory (only used on first call)
        
    Returns:
        PM2LogManager instance
    """
    global _pm2_log_manager
    
    with _manager_lock:
        if _pm2_log_manager is None:
            _pm2_log_manager = PM2LogManager(pm2_home)
        
        return _pm2_log_manager


def reset_pm2_log_manager():
    """Reset the singleton PM2 log manager (mainly for testing)."""
    global _pm2_log_manager
    
    with _manager_lock:
        _pm2_log_manager = None