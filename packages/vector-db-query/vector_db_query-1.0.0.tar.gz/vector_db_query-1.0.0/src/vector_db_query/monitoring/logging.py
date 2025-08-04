"""
Ansera Monitoring System Logging Integration

This module integrates with the dev-agent logging system to provide
comprehensive logging for all monitoring activities.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import traceback
from functools import wraps

# Configure base logger
logger = logging.getLogger(__name__)


class MonitoringLogger:
    """
    Comprehensive logging system for Ansera monitoring.
    
    Integrates with dev-agent logging infrastructure and provides
    structured logging for all monitoring activities.
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize monitoring logger."""
        self.base_dir = base_dir or Path.cwd()
        self.logs_dir = self.base_dir / ".dev-workflow" / "logs"
        self.monitoring_logs_dir = self.logs_dir / "monitoring"
        
        # Initialize directory structure
        self._init_directories()
        
        # Initialize master log
        self.master_log = self.logs_dir / "monitoring-master.log"
        if not self.master_log.exists():
            self._init_master_log()
    
    def _init_directories(self):
        """Initialize logging directory structure."""
        directories = [
            self.logs_dir / "monitoring" / "changes",
            self.logs_dir / "monitoring" / "activities",
            self.logs_dir / "monitoring" / "metrics",
            self.logs_dir / "monitoring" / "queue",
            self.logs_dir / "monitoring" / "processes",
            self.logs_dir / "monitoring" / "errors",
            self.logs_dir / "monitoring" / "snapshots",
            self.logs_dir / "monitoring" / "reports"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _init_master_log(self):
        """Initialize master monitoring log."""
        with open(self.master_log, 'w') as f:
            f.write("# Ansera Monitoring System Master Log\n")
            f.write(f"Initialized: {datetime.now().isoformat()}\n")
            f.write("=" * 50 + "\n\n")
    
    def log_pre_change(self, component: str, change_type: str, 
                      description: str) -> str:
        """
        Log state before making changes.
        
        Args:
            component: Component making the change
            change_type: Type of change
            description: Description of planned change
            
        Returns:
            Log file path for reference
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = self.monitoring_logs_dir / "changes" / f"pre-{timestamp}-{component}.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "change_type": change_type,
            "description": description,
            "state": self._capture_current_state()
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Log to master
        self._append_master_log(f"PRE-CHANGE: {component} - {change_type} - {description}")
        
        return str(log_file)
    
    def log_post_change(self, pre_log_file: str, component: str,
                       change_type: str, result: str, details: Optional[Dict] = None):
        """
        Log state after changes.
        
        Args:
            pre_log_file: Path to pre-change log
            component: Component that made the change
            change_type: Type of change
            result: Result status (SUCCESS/FAILURE/PARTIAL)
            details: Additional details about the change
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        post_log_file = pre_log_file.replace("pre-", "post-")
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "change_type": change_type,
            "result": result,
            "pre_log_file": pre_log_file,
            "details": details or {},
            "state": self._capture_current_state()
        }
        
        with open(post_log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        # Log to master
        self._append_master_log(f"POST-CHANGE: {component} - {change_type} - {result}")
        
        # Create change summary
        self._create_change_summary(pre_log_file, post_log_file, component, change_type, result)
    
    def log_activity(self, component: str, activity_type: str, details: str):
        """
        Log monitoring activity.
        
        Args:
            component: Component performing activity
            activity_type: Type of activity
            details: Activity details
        """
        date_str = datetime.now().strftime("%Y%m%d")
        activity_log = self.monitoring_logs_dir / "activities" / f"{date_str}.log"
        
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{component}] [{activity_type}] {details}\n"
        
        with open(activity_log, 'a') as f:
            f.write(log_entry)
        
        # Component-specific log
        comp_log = self.monitoring_logs_dir / "activities" / component / f"{date_str}.log"
        comp_log.parent.mkdir(exist_ok=True)
        
        with open(comp_log, 'a') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{activity_type}] {details}\n")
    
    def log_metrics(self, metrics_data: Dict[str, Any]):
        """
        Log system metrics.
        
        Args:
            metrics_data: Dictionary containing metrics
        """
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y%m%d")
        metrics_log = self.monitoring_logs_dir / "metrics" / f"{date_str}.jsonl"
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "metrics": metrics_data
        }
        
        with open(metrics_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_queue_event(self, event_type: str, job_id: str, details: Dict[str, Any]):
        """
        Log queue processing events.
        
        Args:
            event_type: Type of queue event
            job_id: Job identifier
            details: Event details
        """
        date_str = datetime.now().strftime("%Y%m%d")
        queue_log = self.monitoring_logs_dir / "queue" / f"{date_str}.jsonl"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "job_id": job_id,
            "details": details
        }
        
        with open(queue_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_process_event(self, process_name: str, event_type: str, 
                         pid: Optional[int] = None, details: Optional[Dict] = None):
        """
        Log process management events.
        
        Args:
            process_name: Name of the process
            event_type: Type of event (start/stop/restart/error)
            pid: Process ID if applicable
            details: Additional details
        """
        date_str = datetime.now().strftime("%Y%m%d")
        process_log = self.monitoring_logs_dir / "processes" / f"{date_str}.jsonl"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "process_name": process_name,
            "event_type": event_type,
            "pid": pid,
            "details": details or {}
        }
        
        with open(process_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_error(self, component: str, error_type: str, 
                 error_message: str, stack_trace: Optional[str] = None):
        """
        Log errors with full context.
        
        Args:
            component: Component where error occurred
            error_type: Type of error
            error_message: Error message
            stack_trace: Optional stack trace
        """
        timestamp = datetime.now()
        error_id = f"{timestamp.strftime('%Y%m%d-%H%M%S')}-{component}"
        error_file = self.monitoring_logs_dir / "errors" / f"{error_id}.json"
        
        error_data = {
            "timestamp": timestamp.isoformat(),
            "component": component,
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace or traceback.format_exc(),
            "context": self._capture_error_context()
        }
        
        with open(error_file, 'w') as f:
            json.dump(error_data, f, indent=2)
        
        # Log to master
        self._append_master_log(f"ERROR: {component} - {error_type} - {error_message}")
        
        # Also log to daily error log
        self._append_daily_error_log(component, error_type, error_message)
    
    def create_snapshot(self, snapshot_name: str, trigger: str, description: str):
        """
        Create a snapshot of current monitoring state.
        
        Args:
            snapshot_name: Name for the snapshot
            trigger: What triggered the snapshot
            description: Description of the snapshot
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        snapshot_dir = self.monitoring_logs_dir / "snapshots" / f"{timestamp}-{snapshot_name}"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Capture current state
        state_data = self._capture_full_state()
        
        # Save state
        with open(snapshot_dir / "state.json", 'w') as f:
            json.dump(state_data, f, indent=2)
        
        # Save metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "name": snapshot_name,
            "trigger": trigger,
            "description": description
        }
        
        with open(snapshot_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Log to master
        self._append_master_log(f"SNAPSHOT: {snapshot_name} - {trigger}")
        
        return str(snapshot_dir)
    
    def generate_daily_report(self, date: Optional[str] = None) -> str:
        """
        Generate daily monitoring report.
        
        Args:
            date: Date in YYYYMMDD format (default: today)
            
        Returns:
            Path to generated report
        """
        date = date or datetime.now().strftime("%Y%m%d")
        report_file = self.monitoring_logs_dir / "reports" / f"daily-{date}.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# Ansera Monitoring Daily Report - {date}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            # Activity summary
            f.write("## Activity Summary\n")
            activities = self._get_daily_activities(date)
            for component, count in activities.items():
                f.write(f"- {component}: {count} activities\n")
            f.write("\n")
            
            # Metrics summary
            f.write("## Metrics Summary\n")
            metrics = self._get_daily_metrics_summary(date)
            f.write(f"- Average CPU: {metrics.get('avg_cpu', 'N/A')}%\n")
            f.write(f"- Average Memory: {metrics.get('avg_memory', 'N/A')}%\n")
            f.write(f"- Queue Processed: {metrics.get('queue_processed', 0)}\n")
            f.write("\n")
            
            # Process events
            f.write("## Process Events\n")
            process_events = self._get_daily_process_events(date)
            for event in process_events:
                f.write(f"- {event}\n")
            f.write("\n")
            
            # Errors
            f.write("## Errors\n")
            errors = self._get_daily_errors(date)
            if errors:
                for error in errors:
                    f.write(f"- {error}\n")
            else:
                f.write("No errors reported.\n")
        
        return str(report_file)
    
    def _capture_current_state(self) -> Dict[str, Any]:
        """Capture current monitoring state."""
        return {
            "timestamp": datetime.now().isoformat(),
            "queue_dir_exists": (self.base_dir / ".vector_db_query" / "queue").exists(),
            "logs_dir_size": self._get_directory_size(self.logs_dir),
            "monitoring_active": True
        }
    
    def _capture_full_state(self) -> Dict[str, Any]:
        """Capture full monitoring state for snapshots."""
        state = self._capture_current_state()
        
        # Add detailed information
        state.update({
            "queue_files": self._list_queue_files(),
            "recent_metrics": self._get_recent_metrics(),
            "active_processes": self._get_active_processes()
        })
        
        return state
    
    def _capture_error_context(self) -> Dict[str, Any]:
        """Capture context when error occurs."""
        return {
            "working_directory": str(Path.cwd()),
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "python_version": os.sys.version,
                "platform": os.sys.platform
            }
        }
    
    def _append_master_log(self, entry: str):
        """Append entry to master log."""
        with open(self.master_log, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] {entry}\n")
    
    def _append_daily_error_log(self, component: str, error_type: str, message: str):
        """Append to daily error log."""
        date_str = datetime.now().strftime("%Y%m%d")
        error_log = self.monitoring_logs_dir / "errors" / f"{date_str}.log"
        
        with open(error_log, 'a') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [{component}] [{error_type}] {message}\n")
    
    def _create_change_summary(self, pre_log: str, post_log: str, 
                             component: str, change_type: str, result: str):
        """Create change summary."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        summary_file = self.monitoring_logs_dir / "changes" / f"summary-{timestamp}.json"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "change_type": change_type,
            "result": result,
            "pre_log_file": pre_log,
            "post_log_file": post_log
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes."""
        total = 0
        try:
            for path in directory.rglob('*'):
                if path.is_file():
                    total += path.stat().st_size
        except:
            pass
        return total
    
    def _list_queue_files(self) -> List[str]:
        """List queue files."""
        queue_dir = self.base_dir / ".vector_db_query" / "queue"
        if queue_dir.exists():
            return [f.name for f in queue_dir.glob("*.json")]
        return []
    
    def _get_recent_metrics(self) -> List[Dict]:
        """Get recent metrics entries."""
        # Implementation would read recent metrics
        return []
    
    def _get_active_processes(self) -> List[Dict]:
        """Get list of active processes."""
        # Implementation would check running processes
        return []
    
    def _get_daily_activities(self, date: str) -> Dict[str, int]:
        """Get activity counts by component for a date."""
        activities = {}
        activity_file = self.monitoring_logs_dir / "activities" / f"{date}.log"
        
        if activity_file.exists():
            with open(activity_file, 'r') as f:
                for line in f:
                    if '[' in line:
                        parts = line.split(']')
                        if len(parts) >= 2:
                            component = parts[1].strip('[').strip()
                            activities[component] = activities.get(component, 0) + 1
        
        return activities
    
    def _get_daily_metrics_summary(self, date: str) -> Dict[str, float]:
        """Get metrics summary for a date."""
        summary = {
            'avg_cpu': 0,
            'avg_memory': 0,
            'queue_processed': 0
        }
        
        metrics_file = self.monitoring_logs_dir / "metrics" / f"{date}.jsonl"
        if metrics_file.exists():
            cpu_values = []
            memory_values = []
            
            with open(metrics_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        metrics = data.get('metrics', {})
                        if 'cpu' in metrics:
                            cpu_values.append(metrics['cpu'])
                        if 'memory' in metrics:
                            memory_values.append(metrics['memory'].get('percent', 0))
                    except:
                        continue
            
            if cpu_values:
                summary['avg_cpu'] = sum(cpu_values) / len(cpu_values)
            if memory_values:
                summary['avg_memory'] = sum(memory_values) / len(memory_values)
        
        return summary
    
    def _get_daily_process_events(self, date: str) -> List[str]:
        """Get process events for a date."""
        events = []
        process_file = self.monitoring_logs_dir / "processes" / f"{date}.jsonl"
        
        if process_file.exists():
            with open(process_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        event = f"{data['event_type']} - {data['process_name']}"
                        if data.get('pid'):
                            event += f" (PID: {data['pid']})"
                        events.append(event)
                    except:
                        continue
        
        return events
    
    def _get_daily_errors(self, date: str) -> List[str]:
        """Get errors for a date."""
        errors = []
        error_log = self.monitoring_logs_dir / "errors" / f"{date}.log"
        
        if error_log.exists():
            with open(error_log, 'r') as f:
                errors = [line.strip() for line in f if line.strip()]
        
        return errors


# Decorator for automatic logging
def log_monitoring_activity(activity_type: str):
    """
    Decorator to automatically log monitoring activities.
    
    Args:
        activity_type: Type of activity being performed
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get logger instance
            if hasattr(self, '_logger'):
                logger_instance = self._logger
            else:
                logger_instance = MonitoringLogger()
            
            # Log activity start
            logger_instance.log_activity(
                self.__class__.__name__,
                activity_type,
                f"Starting {func.__name__}"
            )
            
            try:
                # Execute function
                result = func(self, *args, **kwargs)
                
                # Log success
                logger_instance.log_activity(
                    self.__class__.__name__,
                    activity_type,
                    f"Completed {func.__name__} successfully"
                )
                
                return result
                
            except Exception as e:
                # Log error
                logger_instance.log_error(
                    self.__class__.__name__,
                    activity_type,
                    str(e)
                )
                raise
        
        return wrapper
    return decorator


# Singleton instance
_monitoring_logger = None

def get_monitoring_logger() -> MonitoringLogger:
    """Get singleton monitoring logger instance."""
    global _monitoring_logger
    if _monitoring_logger is None:
        _monitoring_logger = MonitoringLogger()
    return _monitoring_logger