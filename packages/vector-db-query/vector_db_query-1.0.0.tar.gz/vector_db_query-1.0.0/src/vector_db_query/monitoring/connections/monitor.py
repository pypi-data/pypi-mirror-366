"""
Connection monitoring service for tracking and checking system connections.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from threading import RLock
import json
from pathlib import Path
from collections import defaultdict, deque

from .models import (
    Connection, ConnectionType, ConnectionStatus, ConnectionHealth,
    ConnectionMetrics, ConnectionEvent, ConnectionCheck
)
from .checkers import get_checker, ConnectionChecker
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory
from ..notifications import process_system_event, EventType

logger = logging.getLogger(__name__)


class ConnectionMonitor:
    """
    Central service for monitoring all system connections.
    
    Tracks connection health, performs regular checks, and manages alerts.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize connection monitor.
        
        Args:
            config_path: Path to connections configuration file
        """
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # Configuration
        self.config_path = config_path or "config/connections.json"
        
        # Connection storage
        self._connections: Dict[str, Connection] = {}
        self._connection_groups: Dict[str, Set[str]] = defaultdict(set)
        
        # Monitoring state
        self._is_running = False
        self._check_tasks: Dict[str, asyncio.Task] = {}
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Event tracking
        self._event_history: deque = deque(maxlen=1000)
        self._event_listeners: List[Callable[[ConnectionEvent], None]] = []
        
        # Check history (connection_id -> deque of checks)
        self._check_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Statistics
        self._stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'total_events': 0,
            'start_time': None
        }
        
        # Load configuration
        self._load_configuration()
        
        logger.info("ConnectionMonitor initialized")
    
    def _load_configuration(self):
        """Load connections from configuration file."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            logger.info(f"No configuration file found at {self.config_path}")
            return
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Load connections
            for conn_config in config.get('connections', []):
                try:
                    connection = self._create_connection_from_config(conn_config)
                    self.add_connection(connection)
                except Exception as e:
                    logger.error(f"Failed to load connection config: {e}")
            
            logger.info(f"Loaded {len(self._connections)} connections from configuration")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    def _create_connection_from_config(self, config: Dict[str, Any]) -> Connection:
        """Create Connection instance from configuration."""
        # Map string type to enum
        conn_type = ConnectionType(config.get('type', 'custom'))
        
        connection = Connection(
            name=config['name'],
            type=conn_type,
            host=config.get('host'),
            port=config.get('port'),
            url=config.get('url'),
            protocol=config.get('protocol'),
            config=config.get('config', {}),
            tags=config.get('tags', []),
            check_interval_seconds=config.get('check_interval_seconds', 30),
            timeout_seconds=config.get('timeout_seconds', 10),
            retry_count=config.get('retry_count', 3),
            retry_delay_seconds=config.get('retry_delay_seconds', 5),
            alert_on_failure=config.get('alert_on_failure', True),
            alert_threshold=config.get('alert_threshold', 3)
        )
        
        # Add to groups
        for group in config.get('groups', []):
            self._connection_groups[group].add(connection.id)
        
        return connection
    
    def add_connection(self, connection: Connection, groups: Optional[List[str]] = None):
        """
        Add a connection to monitor.
        
        Args:
            connection: Connection to add
            groups: Optional groups to add connection to
        """
        with self._lock:
            self._connections[connection.id] = connection
            
            # Add to groups
            if groups:
                for group in groups:
                    self._connection_groups[group].add(connection.id)
            
            # Start monitoring if service is running
            if self._is_running:
                task = asyncio.create_task(self._monitor_connection(connection))
                self._check_tasks[connection.id] = task
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.CONFIGURATION,
            change_type=ChangeType.CREATE,
            description=f"Added connection: {connection.name}",
            details={'connection_id': connection.id, 'type': connection.type.value}
        )
        
        logger.info(f"Added connection: {connection.name} ({connection.type.value})")
    
    def remove_connection(self, connection_id: str) -> bool:
        """
        Remove a connection from monitoring.
        
        Args:
            connection_id: ID of connection to remove
            
        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if connection_id not in self._connections:
                return False
            
            connection = self._connections.pop(connection_id)
            
            # Remove from groups
            for group_connections in self._connection_groups.values():
                group_connections.discard(connection_id)
            
            # Cancel monitoring task
            if connection_id in self._check_tasks:
                task = self._check_tasks.pop(connection_id)
                task.cancel()
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.CONFIGURATION,
            change_type=ChangeType.DELETE,
            description=f"Removed connection: {connection.name}",
            details={'connection_id': connection_id}
        )
        
        logger.info(f"Removed connection: {connection.name}")
        return True
    
    async def start(self):
        """Start connection monitoring."""
        with self._lock:
            if self._is_running:
                logger.warning("Connection monitor is already running")
                return
            
            self._is_running = True
            self._stats['start_time'] = datetime.now()
        
        # Start monitoring all connections
        for connection in self._connections.values():
            task = asyncio.create_task(self._monitor_connection(connection))
            self._check_tasks[connection.id] = task
        
        # Start monitor task
        self._monitor_task = asyncio.create_task(self._run_monitor())
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.SYSTEM,
            change_type=ChangeType.UPDATE,
            description="Connection monitor started",
            details={'connection_count': len(self._connections)}
        )
        
        logger.info(f"Connection monitor started with {len(self._connections)} connections")
    
    async def stop(self):
        """Stop connection monitoring."""
        with self._lock:
            if not self._is_running:
                return
            
            self._is_running = False
        
        # Cancel all check tasks
        for task in self._check_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self._check_tasks:
            await asyncio.gather(*self._check_tasks.values(), return_exceptions=True)
        
        self._check_tasks.clear()
        
        # Cancel monitor task
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.SYSTEM,
            change_type=ChangeType.UPDATE,
            description="Connection monitor stopped",
            details={'runtime_seconds': self._get_runtime_seconds()}
        )
        
        logger.info("Connection monitor stopped")
    
    async def _monitor_connection(self, connection: Connection):
        """Monitor a single connection."""
        checker = get_checker(connection.type)
        
        while self._is_running:
            try:
                # Perform check
                check = await checker.check(connection)
                
                # Update statistics
                with self._lock:
                    self._stats['total_checks'] += 1
                    if check.success:
                        self._stats['successful_checks'] += 1
                    else:
                        self._stats['failed_checks'] += 1
                
                # Process check result
                await self._process_check_result(connection, check, checker)
                
                # Store check history
                self._check_history[connection.id].append(check)
                
                # Wait for next check
                await asyncio.sleep(connection.check_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error monitoring connection {connection.name}: {e}")
                await asyncio.sleep(connection.check_interval_seconds)
    
    async def _process_check_result(self, connection: Connection, check: ConnectionCheck, 
                                   checker: ConnectionChecker):
        """Process connection check result."""
        old_status = connection.status
        old_health = connection.health
        
        # Update connection based on check result
        if check.success:
            connection.update_status(ConnectionStatus.CONNECTED)
            connection.record_success()
            
            # Update metrics
            if check.response_time_ms:
                self._update_response_time_metrics(connection, check.response_time_ms)
            
            # Determine health
            health = checker.determine_health(connection, check)
            connection.health = health
            
        else:
            connection.update_status(ConnectionStatus.ERROR)
            connection.record_failure(check.error)
            
            # Update error rate
            self._update_error_rate(connection)
            
            # Set health based on failures
            if connection.consecutive_failures >= 5:
                connection.health = ConnectionHealth.CRITICAL
            elif connection.consecutive_failures >= 3:
                connection.health = ConnectionHealth.UNHEALTHY
            else:
                connection.health = ConnectionHealth.DEGRADED
        
        # Check for status/health changes
        if old_status != connection.status or old_health != connection.health:
            await self._handle_connection_change(connection, old_status, old_health, check)
        
        # Check for alerts
        if connection.should_alert():
            await self._trigger_alert(connection, check)
    
    def _update_response_time_metrics(self, connection: Connection, response_time_ms: float):
        """Update response time metrics."""
        metrics = connection.metrics
        
        # Simple moving average for now
        if metrics.avg_response_time_ms == 0:
            metrics.avg_response_time_ms = response_time_ms
        else:
            metrics.avg_response_time_ms = (metrics.avg_response_time_ms * 0.9 + 
                                           response_time_ms * 0.1)
        
        # Update latency
        metrics.latency_ms = response_time_ms
        
        # Simple P95/P99 approximation (would need proper percentile tracking in production)
        metrics.p95_response_time_ms = max(metrics.p95_response_time_ms, response_time_ms * 0.95)
        metrics.p99_response_time_ms = max(metrics.p99_response_time_ms, response_time_ms * 0.99)
    
    def _update_error_rate(self, connection: Connection):
        """Update error rate metric."""
        if connection.total_checks > 0:
            connection.metrics.error_rate = connection.total_failures / connection.total_checks
            connection.metrics.error_count = connection.total_failures
    
    async def _handle_connection_change(self, connection: Connection, 
                                      old_status: ConnectionStatus,
                                      old_health: ConnectionHealth,
                                      check: ConnectionCheck):
        """Handle connection status/health change."""
        # Create event
        event = ConnectionEvent(
            connection_id=connection.id,
            connection_name=connection.name,
            event_type="status_change" if old_status != connection.status else "health_change",
            old_status=old_status,
            new_status=connection.status,
            old_health=old_health,
            new_health=connection.health,
            message=f"Connection {connection.name} changed from {old_status.value} to {connection.status.value}",
            error=check.error,
            details=check.details,
            metrics_snapshot=connection.metrics.to_dict()
        )
        
        # Store event
        self._event_history.append(event)
        self._stats['total_events'] += 1
        
        # Notify listeners
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in event listener: {e}")
        
        # Process system event
        if connection.status == ConnectionStatus.ERROR:
            if connection.type == ConnectionType.QDRANT:
                event_type = EventType.CONNECTION_LOST
            elif connection.type == ConnectionType.MCP_SERVER:
                event_type = EventType.SERVICE_FAILURE
            else:
                event_type = EventType.CONNECTION_LOST
            
            process_system_event(
                event_type,
                connection_name=connection.name,
                connection_type=connection.type.value,
                error=check.error,
                consecutive_failures=connection.consecutive_failures
            )
        elif old_status == ConnectionStatus.ERROR and connection.status == ConnectionStatus.CONNECTED:
            process_system_event(
                EventType.CONNECTION_RESTORED,
                connection_name=connection.name,
                connection_type=connection.type.value,
                downtime_seconds=(datetime.now() - connection.last_failure_time).total_seconds()
            )
    
    async def _trigger_alert(self, connection: Connection, check: ConnectionCheck):
        """Trigger alert for connection failure."""
        connection.alerted = True
        
        # Log alert
        logger.error(f"ALERT: Connection {connection.name} has failed {connection.consecutive_failures} times")
        
        # Process as critical event
        process_system_event(
            EventType.CONNECTION_LOST,
            connection_name=connection.name,
            connection_type=connection.type.value,
            error=check.error,
            consecutive_failures=connection.consecutive_failures,
            severity="critical"
        )
    
    async def _run_monitor(self):
        """Run periodic monitoring tasks."""
        while self._is_running:
            try:
                # Calculate uptime for all connections
                now = datetime.now()
                for connection in self._connections.values():
                    if connection.last_success_time:
                        uptime = (now - connection.created_at).total_seconds()
                        connection.metrics.uptime_seconds = uptime
                
                # Cleanup old events
                if len(self._event_history) > 900:
                    # Keep last 900 events
                    for _ in range(100):
                        self._event_history.popleft()
                
                await asyncio.sleep(60)  # Run every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitor task: {e}")
    
    async def check_connection(self, connection_id: str) -> Optional[ConnectionCheck]:
        """
        Manually check a specific connection.
        
        Args:
            connection_id: ID of connection to check
            
        Returns:
            ConnectionCheck result or None if not found
        """
        with self._lock:
            connection = self._connections.get(connection_id)
            if not connection:
                return None
        
        checker = get_checker(connection.type)
        check = await checker.check(connection)
        
        # Process result
        await self._process_check_result(connection, check, checker)
        
        return check
    
    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """Get connection by ID."""
        with self._lock:
            return self._connections.get(connection_id)
    
    def get_all_connections(self) -> List[Connection]:
        """Get all connections."""
        with self._lock:
            return list(self._connections.values())
    
    def get_connections_by_type(self, conn_type: ConnectionType) -> List[Connection]:
        """Get connections by type."""
        with self._lock:
            return [conn for conn in self._connections.values() 
                   if conn.type == conn_type]
    
    def get_connections_by_group(self, group: str) -> List[Connection]:
        """Get connections in a group."""
        with self._lock:
            conn_ids = self._connection_groups.get(group, set())
            return [self._connections[cid] for cid in conn_ids 
                   if cid in self._connections]
    
    def get_connection_health_summary(self) -> Dict[str, int]:
        """Get summary of connection health."""
        summary = {
            ConnectionHealth.HEALTHY.value: 0,
            ConnectionHealth.DEGRADED.value: 0,
            ConnectionHealth.UNHEALTHY.value: 0,
            ConnectionHealth.CRITICAL.value: 0,
            ConnectionHealth.UNKNOWN.value: 0
        }
        
        with self._lock:
            for connection in self._connections.values():
                summary[connection.health.value] += 1
        
        return summary
    
    def get_recent_events(self, limit: int = 50, 
                         connection_id: Optional[str] = None) -> List[ConnectionEvent]:
        """Get recent connection events."""
        events = list(self._event_history)
        
        if connection_id:
            events = [e for e in events if e.connection_id == connection_id]
        
        # Return most recent first
        return list(reversed(events))[:limit]
    
    def get_check_history(self, connection_id: str, 
                         limit: int = 50) -> List[ConnectionCheck]:
        """Get check history for a connection."""
        checks = list(self._check_history.get(connection_id, []))
        return list(reversed(checks))[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        with self._lock:
            total_connections = len(self._connections)
            active_connections = sum(1 for c in self._connections.values() 
                                   if c.status == ConnectionStatus.CONNECTED)
            
            success_rate = 0.0
            if self._stats['total_checks'] > 0:
                success_rate = (self._stats['successful_checks'] / 
                              self._stats['total_checks']) * 100
            
            return {
                'connections': {
                    'total': total_connections,
                    'active': active_connections,
                    'inactive': total_connections - active_connections
                },
                'health_summary': self.get_connection_health_summary(),
                'checks': {
                    'total': self._stats['total_checks'],
                    'successful': self._stats['successful_checks'],
                    'failed': self._stats['failed_checks'],
                    'success_rate': success_rate
                },
                'events': {
                    'total': self._stats['total_events'],
                    'recent_count': len(self._event_history)
                },
                'runtime': {
                    'is_running': self._is_running,
                    'start_time': self._stats['start_time'].isoformat() if self._stats['start_time'] else None,
                    'uptime_seconds': self._get_runtime_seconds()
                }
            }
    
    def _get_runtime_seconds(self) -> Optional[float]:
        """Get runtime in seconds."""
        if self._stats['start_time']:
            return (datetime.now() - self._stats['start_time']).total_seconds()
        return None
    
    def add_event_listener(self, listener: Callable[[ConnectionEvent], None]):
        """Add event listener."""
        self._event_listeners.append(listener)
    
    def remove_event_listener(self, listener: Callable[[ConnectionEvent], None]):
        """Remove event listener."""
        if listener in self._event_listeners:
            self._event_listeners.remove(listener)
    
    async def save_configuration(self):
        """Save current connections to configuration file."""
        config = {
            'connections': []
        }
        
        with self._lock:
            for connection in self._connections.values():
                # Find groups for this connection
                groups = []
                for group, conn_ids in self._connection_groups.items():
                    if connection.id in conn_ids:
                        groups.append(group)
                
                conn_config = {
                    'name': connection.name,
                    'type': connection.type.value,
                    'host': connection.host,
                    'port': connection.port,
                    'url': connection.url,
                    'protocol': connection.protocol,
                    'config': connection.config,
                    'tags': connection.tags,
                    'groups': groups,
                    'check_interval_seconds': connection.check_interval_seconds,
                    'timeout_seconds': connection.timeout_seconds,
                    'retry_count': connection.retry_count,
                    'retry_delay_seconds': connection.retry_delay_seconds,
                    'alert_on_failure': connection.alert_on_failure,
                    'alert_threshold': connection.alert_threshold
                }
                
                config['connections'].append(conn_config)
        
        # Save to file
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved {len(config['connections'])} connections to configuration")


# Singleton instance
_connection_monitor: Optional[ConnectionMonitor] = None
_monitor_lock = RLock()


def get_connection_monitor() -> ConnectionMonitor:
    """Get singleton connection monitor instance."""
    global _connection_monitor
    
    with _monitor_lock:
        if _connection_monitor is None:
            _connection_monitor = ConnectionMonitor()
        
        return _connection_monitor


def reset_connection_monitor():
    """Reset the singleton connection monitor (mainly for testing)."""
    global _connection_monitor
    
    with _monitor_lock:
        if _connection_monitor and _connection_monitor._is_running:
            asyncio.create_task(_connection_monitor.stop())
        
        _connection_monitor = None