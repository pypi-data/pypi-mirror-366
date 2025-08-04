"""
MCP Server metrics collector.
"""

import asyncio
import psutil
import logging
import subprocess
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Deque, Union
from collections import defaultdict, deque
from threading import RLock
from pathlib import Path

from .models import (
    MCPMetrics, MCPRequest, MCPResponse, MCPSession,
    MCPError, MCPResourceUsage, MCPMethodStats,
    MCPRequestType, MCPResponseStatus
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class MCPMetricsCollector:
    """
    Collects and aggregates metrics for MCP Server monitoring.
    """
    
    def __init__(self, log_path: Optional[str] = None, socket_path: Optional[str] = None):
        """
        Initialize MCP metrics collector.
        
        Args:
            log_path: Path to MCP server logs
            socket_path: Path to MCP socket
        """
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # Configuration
        self.log_path = log_path or "/var/log/mcp-server.log"
        self.socket_path = socket_path or "/tmp/mcp.sock"
        
        # Collection state
        self._is_collecting = False
        self._collection_task: Optional[asyncio.Task] = None
        self._log_monitor_task: Optional[asyncio.Task] = None
        
        # Metrics storage
        self._current_metrics = MCPMetrics()
        self._sessions: Dict[str, MCPSession] = {}
        self._method_stats: Dict[str, MCPMethodStats] = defaultdict(MCPMethodStats)
        
        # Request tracking
        self._pending_requests: Dict[str, MCPRequest] = {}
        self._request_history: Deque[MCPRequest] = deque(maxlen=1000)
        self._response_history: Deque[MCPResponse] = deque(maxlen=1000)
        self._error_history: Deque[MCPError] = deque(maxlen=100)
        
        # Time series data (for trends)
        self._metrics_history: Deque[MCPMetrics] = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self._resource_history: Deque[MCPResourceUsage] = deque(maxlen=720)  # 12 hours at 1-minute intervals
        
        # Process tracking
        self._mcp_process: Optional[psutil.Process] = None
        self._start_time: Optional[datetime] = None
        
        # Statistics
        self._stats = {
            'collection_cycles': 0,
            'log_lines_processed': 0,
            'errors_encountered': 0
        }
        
        logger.info("MCPMetricsCollector initialized")
    
    async def start(self):
        """Start metrics collection."""
        with self._lock:
            if self._is_collecting:
                logger.warning("Metrics collection is already running")
                return
            
            self._is_collecting = True
            self._start_time = datetime.now()
        
        # Find MCP process
        self._find_mcp_process()
        
        # Start collection tasks
        self._collection_task = asyncio.create_task(self._collect_metrics_loop())
        
        # Start log monitoring if log file exists
        if Path(self.log_path).exists():
            self._log_monitor_task = asyncio.create_task(self._monitor_logs())
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.SYSTEM,
            change_type=ChangeType.UPDATE,
            description="MCP metrics collection started",
            details={'log_path': self.log_path, 'socket_path': self.socket_path}
        )
        
        logger.info("MCP metrics collection started")
    
    async def stop(self):
        """Stop metrics collection."""
        with self._lock:
            if not self._is_collecting:
                return
            
            self._is_collecting = False
        
        # Cancel tasks
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        
        if self._log_monitor_task:
            self._log_monitor_task.cancel()
            try:
                await self._log_monitor_task
            except asyncio.CancelledError:
                pass
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.SYSTEM,
            change_type=ChangeType.UPDATE,
            description="MCP metrics collection stopped",
            details={'runtime_seconds': self._get_uptime_seconds()}
        )
        
        logger.info("MCP metrics collection stopped")
    
    def _find_mcp_process(self):
        """Find MCP server process."""
        try:
            # Look for MCP server process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'mcp-server' in cmdline:
                        self._mcp_process = psutil.Process(proc.info['pid'])
                        logger.info(f"Found MCP server process: PID {proc.info['pid']}")
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.warning("MCP server process not found")
            
        except Exception as e:
            logger.error(f"Error finding MCP process: {e}")
    
    async def _collect_metrics_loop(self):
        """Main metrics collection loop."""
        while self._is_collecting:
            try:
                # Collect metrics
                await self._collect_current_metrics()
                
                # Update statistics
                with self._lock:
                    self._stats['collection_cycles'] += 1
                
                # Store historical data
                self._metrics_history.append(self._current_metrics)
                self._resource_history.append(self._current_metrics.resource_usage)
                
                # Wait for next collection cycle
                await asyncio.sleep(60)  # Collect every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                self._stats['errors_encountered'] += 1
                await asyncio.sleep(60)
    
    async def _collect_current_metrics(self):
        """Collect current metrics snapshot."""
        metrics = MCPMetrics()
        
        # Server info
        metrics.server_version = await self._get_server_version()
        metrics.uptime_seconds = self._get_uptime_seconds()
        
        # Resource usage
        metrics.resource_usage = await self._collect_resource_usage()
        
        # Session metrics
        active_sessions = [s for s in self._sessions.values() if s.is_active]
        metrics.active_sessions = len(active_sessions)
        metrics.total_sessions = len(self._sessions)
        
        # Calculate performance metrics
        await self._calculate_performance_metrics(metrics)
        
        # Method statistics
        metrics.method_stats = dict(self._method_stats)
        
        # Recent activity
        metrics.recent_requests = list(self._request_history)[-10:]
        metrics.recent_errors = list(self._error_history)[-10:]
        
        # Database metrics (if available)
        await self._collect_database_metrics(metrics)
        
        # Cache metrics (if available)
        await self._collect_cache_metrics(metrics)
        
        # Update current metrics
        with self._lock:
            self._current_metrics = metrics
    
    async def _collect_resource_usage(self) -> MCPResourceUsage:
        """Collect resource usage metrics."""
        usage = MCPResourceUsage()
        
        try:
            if self._mcp_process and self._mcp_process.is_running():
                # CPU metrics
                usage.cpu_percent = self._mcp_process.cpu_percent(interval=0.1)
                usage.cpu_threads = self._mcp_process.num_threads()
                
                # Memory metrics
                mem_info = self._mcp_process.memory_info()
                usage.memory_used_mb = mem_info.rss / (1024 * 1024)
                usage.memory_percent = self._mcp_process.memory_percent()
                
                # Get system memory for total
                sys_mem = psutil.virtual_memory()
                usage.memory_total_mb = sys_mem.total / (1024 * 1024)
                
                # Network connections
                try:
                    connections = self._mcp_process.connections()
                    usage.active_connections = len([c for c in connections if c.status == 'ESTABLISHED'])
                    usage.total_connections = len(connections)
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
                
            else:
                # System-wide metrics as fallback
                usage.cpu_percent = psutil.cpu_percent(interval=0.1)
                usage.cpu_cores = psutil.cpu_count(logical=False)
                usage.cpu_threads = psutil.cpu_count(logical=True)
                
                mem = psutil.virtual_memory()
                usage.memory_used_mb = mem.used / (1024 * 1024)
                usage.memory_total_mb = mem.total / (1024 * 1024)
                usage.memory_percent = mem.percent
            
            # Network I/O (system-wide)
            net_io = psutil.net_io_counters()
            if hasattr(self, '_last_net_io'):
                time_delta = 1.0  # Approximate
                bytes_sent_delta = net_io.bytes_sent - self._last_net_io.bytes_sent
                bytes_recv_delta = net_io.bytes_recv - self._last_net_io.bytes_recv
                
                usage.network_out_mbps = (bytes_sent_delta * 8) / (1024 * 1024 * time_delta)
                usage.network_in_mbps = (bytes_recv_delta * 8) / (1024 * 1024 * time_delta)
            
            self._last_net_io = net_io
            
        except Exception as e:
            logger.error(f"Error collecting resource usage: {e}")
        
        return usage
    
    async def _get_server_version(self) -> Optional[str]:
        """Get MCP server version."""
        try:
            # Try to get version from process or API
            # This is a placeholder - implement based on actual MCP server
            return "1.0.0"
        except:
            return None
    
    def _get_uptime_seconds(self) -> float:
        """Get collector uptime in seconds."""
        if self._start_time:
            return (datetime.now() - self._start_time).total_seconds()
        return 0.0
    
    async def _calculate_performance_metrics(self, metrics: MCPMetrics):
        """Calculate performance metrics."""
        # Get recent time window (last 5 minutes)
        time_window = datetime.now() - timedelta(minutes=5)
        
        recent_requests = [r for r in self._request_history if r.timestamp > time_window]
        recent_responses = [r for r in self._response_history if r.timestamp > time_window]
        
        if recent_requests:
            # Requests per second
            time_span = (datetime.now() - recent_requests[0].timestamp).total_seconds()
            if time_span > 0:
                metrics.requests_per_second = len(recent_requests) / time_span
        
        if recent_responses:
            # Average response time
            response_times = [r.response_time_ms for r in recent_responses if r.response_time_ms > 0]
            if response_times:
                metrics.avg_response_time_ms = sum(response_times) / len(response_times)
            
            # Error rate
            error_count = sum(1 for r in recent_responses if r.status != MCPResponseStatus.SUCCESS)
            metrics.error_rate = error_count / len(recent_responses)
        
        # Totals
        metrics.total_requests = len(self._request_history)
        metrics.total_errors = len(self._error_history)
        
        # Data processed
        total_bytes = sum(r.request_size_bytes for r in self._request_history)
        total_bytes += sum(r.response_size_bytes for r in self._response_history)
        metrics.total_data_processed_gb = total_bytes / (1024 * 1024 * 1024)
    
    async def _collect_database_metrics(self, metrics: MCPMetrics):
        """Collect database-related metrics."""
        # This would integrate with actual MCP database connection pool
        # Placeholder implementation
        pass
    
    async def _collect_cache_metrics(self, metrics: MCPMetrics):
        """Collect cache-related metrics."""
        # This would integrate with actual MCP cache system
        # Placeholder implementation
        pass
    
    async def _monitor_logs(self):
        """Monitor MCP server logs for events."""
        try:
            # Use tail to follow log file
            process = await asyncio.create_subprocess_exec(
                'tail', '-F', self.log_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            while self._is_collecting:
                line = await process.stdout.readline()
                if not line:
                    break
                
                try:
                    await self._process_log_line(line.decode('utf-8').strip())
                    self._stats['log_lines_processed'] += 1
                except Exception as e:
                    logger.error(f"Error processing log line: {e}")
                    self._stats['errors_encountered'] += 1
            
        except Exception as e:
            logger.error(f"Error monitoring logs: {e}")
    
    async def _process_log_line(self, line: str):
        """Process a single log line."""
        if not line:
            return
        
        # Parse log line based on MCP server log format
        # This is a simplified example - adapt to actual log format
        
        # Example: Request log
        if '"method":' in line and '"request_id":' in line:
            try:
                # Extract JSON from log line
                json_start = line.find('{')
                if json_start >= 0:
                    data = json.loads(line[json_start:])
                    await self._handle_request_log(data)
            except json.JSONDecodeError:
                pass
        
        # Example: Response log
        elif '"response_time":' in line and '"status":' in line:
            try:
                json_start = line.find('{')
                if json_start >= 0:
                    data = json.loads(line[json_start:])
                    await self._handle_response_log(data)
            except json.JSONDecodeError:
                pass
        
        # Example: Error log
        elif 'ERROR' in line or 'Exception' in line:
            await self._handle_error_log(line)
    
    async def _handle_request_log(self, data: Dict[str, Any]):
        """Handle request log entry."""
        request = MCPRequest(
            id=data.get('request_id', str(uuid.uuid4())),
            method=data.get('method', ''),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            params=data.get('params', {}),
            client_id=data.get('client_id'),
            session_id=data.get('session_id'),
            request_size_bytes=data.get('size', 0)
        )
        
        # Determine request type
        method = request.method.lower()
        if 'query' in method or 'search' in method:
            request.request_type = MCPRequestType.QUERY
        elif 'insert' in method or 'create' in method:
            request.request_type = MCPRequestType.INSERT
        elif 'update' in method:
            request.request_type = MCPRequestType.UPDATE
        elif 'delete' in method:
            request.request_type = MCPRequestType.DELETE
        
        # Track request
        with self._lock:
            self._pending_requests[request.id] = request
            self._request_history.append(request)
        
        # Update session
        if request.session_id:
            await self._update_session(request)
    
    async def _handle_response_log(self, data: Dict[str, Any]):
        """Handle response log entry."""
        request_id = data.get('request_id')
        if not request_id:
            return
        
        # Create response
        status = MCPResponseStatus.SUCCESS if data.get('success', True) else MCPResponseStatus.ERROR
        
        response = MCPResponse(
            request_id=request_id,
            status=status,
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            response_time_ms=data.get('response_time', 0),
            response_size_bytes=data.get('size', 0),
            error=data.get('error'),
            error_code=data.get('error_code'),
            db_query_time_ms=data.get('db_time'),
            cache_hit=data.get('cache_hit', False)
        )
        
        # Track response
        with self._lock:
            self._response_history.append(response)
            
            # Match with request
            request = self._pending_requests.pop(request_id, None)
            if request:
                # Update method stats
                self._update_method_stats(request, response)
    
    async def _handle_error_log(self, line: str):
        """Handle error log entry."""
        error = MCPError(
            timestamp=datetime.now(),
            error_message=line,
            severity='error' if 'ERROR' in line else 'warning'
        )
        
        # Try to extract more details
        if 'request_id' in line:
            # Extract request ID if present
            import re
            match = re.search(r'request_id["\s:]+([a-f0-9-]+)', line)
            if match:
                error.request_id = match.group(1)
        
        with self._lock:
            self._error_history.append(error)
    
    async def _update_session(self, request: MCPRequest):
        """Update session metrics."""
        if not request.session_id:
            return
        
        with self._lock:
            session = self._sessions.get(request.session_id)
            if not session:
                session = MCPSession(
                    id=request.session_id,
                    client_id=request.client_id or 'unknown'
                )
                self._sessions[request.session_id] = session
            
            session.last_activity = datetime.now()
            session.total_requests += 1
    
    def _update_method_stats(self, request: MCPRequest, response: MCPResponse):
        """Update method statistics."""
        stats = self._method_stats[request.method]
        if not stats.method_name:
            stats.method_name = request.method
        
        stats.total_calls += 1
        
        if response.status == MCPResponseStatus.SUCCESS:
            stats.successful_calls += 1
        else:
            stats.failed_calls += 1
            stats.recent_errors.append(response.error or 'Unknown error')
            stats.last_error_time = response.timestamp
            
            # Keep only last 10 errors
            if len(stats.recent_errors) > 10:
                stats.recent_errors = stats.recent_errors[-10:]
        
        # Update timing metrics
        if response.response_time_ms > 0:
            # Simple running average
            if stats.avg_response_time == 0:
                stats.avg_response_time = response.response_time_ms
            else:
                stats.avg_response_time = (stats.avg_response_time * 0.9 + 
                                         response.response_time_ms * 0.1)
            
            stats.min_response_time = min(stats.min_response_time, response.response_time_ms)
            stats.max_response_time = max(stats.max_response_time, response.response_time_ms)
        
        # Update data metrics
        stats.avg_request_size_bytes = (
            (stats.avg_request_size_bytes * (stats.total_calls - 1) + request.request_size_bytes) 
            / stats.total_calls
        )
        stats.avg_response_size_bytes = (
            (stats.avg_response_size_bytes * (stats.total_calls - 1) + response.response_size_bytes) 
            / stats.total_calls
        )
        
        total_bytes = request.request_size_bytes + response.response_size_bytes
        stats.total_data_processed_mb += total_bytes / (1024 * 1024)
        
        # Calculate rates
        if stats.total_calls > 0:
            stats.error_rate = stats.failed_calls / stats.total_calls
    
    def get_current_metrics(self) -> MCPMetrics:
        """Get current metrics snapshot."""
        with self._lock:
            return self._current_metrics
    
    def get_method_stats(self, method: Optional[str] = None) -> Union[MCPMethodStats, Dict[str, MCPMethodStats]]:
        """Get method statistics."""
        with self._lock:
            if method:
                return self._method_stats.get(method, MCPMethodStats(method_name=method))
            return dict(self._method_stats)
    
    def get_active_sessions(self) -> List[MCPSession]:
        """Get list of active sessions."""
        with self._lock:
            return [s for s in self._sessions.values() if s.is_active]
    
    def get_recent_errors(self, limit: int = 50) -> List[MCPError]:
        """Get recent errors."""
        with self._lock:
            return list(self._error_history)[-limit:]
    
    def get_metrics_history(self, hours: int = 24) -> List[MCPMetrics]:
        """Get metrics history."""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self._lock:
            return [m for m in self._metrics_history if m.timestamp > cutoff]
    
    def get_resource_history(self, hours: int = 12) -> List[MCPResourceUsage]:
        """Get resource usage history."""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self._lock:
            return [r for r in self._resource_history if r.timestamp > cutoff]
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test MCP server connection."""
        result = {
            'connected': False,
            'process_found': False,
            'socket_exists': False,
            'log_readable': False,
            'details': {}
        }
        
        # Check process
        self._find_mcp_process()
        if self._mcp_process:
            result['process_found'] = True
            result['details']['pid'] = self._mcp_process.pid
            result['details']['status'] = self._mcp_process.status()
        
        # Check socket
        if Path(self.socket_path).exists():
            result['socket_exists'] = True
        
        # Check log file
        if Path(self.log_path).exists() and Path(self.log_path).is_file():
            result['log_readable'] = True
            result['details']['log_size'] = Path(self.log_path).stat().st_size
        
        result['connected'] = result['process_found'] or result['socket_exists']
        
        return result


# Singleton instance
_mcp_collector: Optional[MCPMetricsCollector] = None
_collector_lock = RLock()


def get_mcp_collector() -> MCPMetricsCollector:
    """Get singleton MCP metrics collector instance."""
    global _mcp_collector
    
    with _collector_lock:
        if _mcp_collector is None:
            _mcp_collector = MCPMetricsCollector()
        
        return _mcp_collector


def reset_mcp_collector():
    """Reset the singleton MCP collector (mainly for testing)."""
    global _mcp_collector
    
    with _collector_lock:
        if _mcp_collector and _mcp_collector._is_collecting:
            asyncio.create_task(_mcp_collector.stop())
        
        _mcp_collector = None