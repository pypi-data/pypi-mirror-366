"""
Main SSE manager that coordinates all SSE components.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path

from .models import SSEEvent, SSEConnection, ConnectionStatus, EventFilter, SSEEventType
from .stream import EventStream, create_event_stream
from .broadcaster import EventBroadcaster

logger = logging.getLogger(__name__)


class SSEManager:
    """
    Main SSE manager that coordinates streaming, broadcasting, and connection management.
    
    This is the primary interface for the SSE infrastructure.
    """
    
    def __init__(
        self,
        buffer_size: int = 1000,
        heartbeat_interval: int = 30,
        max_connections: int = 100,
        stats_interval: int = 60
    ):
        """
        Initialize SSE manager.
        
        Args:
            buffer_size: Event buffer size for new connections
            heartbeat_interval: Heartbeat interval in seconds
            max_connections: Maximum concurrent connections
            stats_interval: Statistics update interval
        """
        self.buffer_size = buffer_size
        self.heartbeat_interval = heartbeat_interval
        self.max_connections = max_connections
        self.stats_interval = stats_interval
        
        # Core components
        self.broadcaster = EventBroadcaster(
            buffer_size=buffer_size,
            stats_interval=stats_interval
        )
        
        # Connection tracking
        self._connections: Dict[str, SSEConnection] = {}
        self._connection_lock = asyncio.Lock()
        
        # Event hooks
        self._pre_broadcast_hooks: List[Callable[[SSEEvent], SSEEvent]] = []
        self._post_broadcast_hooks: List[Callable[[SSEEvent, int], None]] = []
        
        # Configuration
        self._default_event_filter: Optional[EventFilter] = None
        
        logger.info(f"SSEManager initialized (max_connections={max_connections})")
    
    async def start(self):
        """Start the SSE manager."""
        await self.broadcaster.start()
        logger.info("SSEManager started")
    
    async def stop(self):
        """Stop the SSE manager."""
        await self.broadcaster.stop()
        
        # Clear connections
        async with self._connection_lock:
            self._connections.clear()
        
        logger.info("SSEManager stopped")
    
    async def create_connection(
        self,
        client_ip: str = "unknown",
        user_agent: str = "unknown",
        client_info: Optional[Dict[str, Any]] = None,
        event_filter: Optional[EventFilter] = None
    ) -> str:
        """
        Create a new SSE connection.
        
        Args:
            client_ip: Client IP address
            user_agent: Client user agent
            client_info: Additional client information
            event_filter: Event filter for this connection
            
        Returns:
            Connection ID
        """
        # Check connection limit
        async with self._connection_lock:
            if len(self._connections) >= self.max_connections:
                raise Exception(f"Maximum connections ({self.max_connections}) reached")
            
            # Create connection
            connection = SSEConnection(
                client_ip=client_ip,
                user_agent=user_agent,
                client_info=client_info or {}
            )
            
            self._connections[connection.connection_id] = connection
        
        logger.info(f"Created SSE connection {connection.connection_id} from {client_ip}")
        return connection.connection_id
    
    async def get_event_stream(
        self,
        connection_id: str,
        event_filter: Optional[EventFilter] = None
    ):
        """
        Get an event stream for a connection.
        
        Args:
            connection_id: Connection ID
            event_filter: Optional event filter
            
        Returns:
            Async generator for SSE events
        """
        async with self._connection_lock:
            if connection_id not in self._connections:
                raise ValueError(f"Connection not found: {connection_id}")
            
            connection = self._connections[connection_id]
        
        # Use provided filter or default
        filter_to_use = event_filter or self._default_event_filter
        
        # Create and manage event stream
        async with create_event_stream(
            connection=connection,
            event_filter=filter_to_use,
            heartbeat_interval=self.heartbeat_interval
        ) as stream:
            
            # Add stream to broadcaster
            await self.broadcaster.add_stream(stream)
            
            try:
                # Yield events from stream
                async for event_data in stream.get_stream():
                    yield event_data
            
            finally:
                # Remove stream from broadcaster
                await self.broadcaster.remove_stream(connection_id)
    
    async def broadcast_event(
        self,
        event: Union[SSEEvent, Dict[str, Any]],
        event_type: Optional[Union[SSEEventType, str]] = None
    ) -> int:
        """
        Broadcast an event to all connections.
        
        Args:
            event: Event to broadcast (SSEEvent or dict)
            event_type: Event type (if event is dict)
            
        Returns:
            Number of connections that received the event
        """
        # Convert dict to SSEEvent if needed
        if isinstance(event, dict):
            if event_type is None:
                event_type = event.get('event_type', SSEEventType.CUSTOM)
            
            sse_event = SSEEvent(
                event_type=event_type,
                data=event
            )
        else:
            sse_event = event
        
        # Apply pre-broadcast hooks
        for hook in self._pre_broadcast_hooks:
            try:
                sse_event = hook(sse_event)
            except Exception as e:
                logger.error(f"Error in pre-broadcast hook: {str(e)}")
        
        # Broadcast event
        sent_count = await self.broadcaster.broadcast_event(sse_event)
        
        # Apply post-broadcast hooks
        for hook in self._post_broadcast_hooks:
            try:
                hook(sse_event, sent_count)
            except Exception as e:
                logger.error(f"Error in post-broadcast hook: {str(e)}")
        
        return sent_count
    
    async def send_to_connection(
        self,
        connection_id: str,
        event: Union[SSEEvent, Dict[str, Any]],
        event_type: Optional[Union[SSEEventType, str]] = None
    ) -> bool:
        """
        Send an event to a specific connection.
        
        Args:
            connection_id: Target connection ID
            event: Event to send
            event_type: Event type (if event is dict)
            
        Returns:
            True if sent successfully
        """
        # Convert dict to SSEEvent if needed
        if isinstance(event, dict):
            if event_type is None:
                event_type = event.get('event_type', SSEEventType.CUSTOM)
            
            sse_event = SSEEvent(
                event_type=event_type,
                data=event
            )
        else:
            sse_event = event
        
        return await self.broadcaster.send_to_connection(connection_id, sse_event)
    
    async def disconnect_connection(self, connection_id: str) -> bool:
        """
        Disconnect a specific connection.
        
        Args:
            connection_id: Connection ID to disconnect
            
        Returns:
            True if disconnected successfully
        """
        async with self._connection_lock:
            if connection_id in self._connections:
                connection = self._connections[connection_id]
                connection.status = ConnectionStatus.DISCONNECTED
                del self._connections[connection_id]
        
        # Remove from broadcaster
        removed = await self.broadcaster.remove_stream(connection_id)
        
        if removed:
            logger.info(f"Disconnected connection {connection_id}")
        
        return removed
    
    async def send_alert(
        self,
        alert_type: str,
        title: str,
        message: str,
        source: str = "system",
        data: Optional[Dict[str, Any]] = None,
        connection_id: Optional[str] = None
    ):
        """
        Send an alert to all connections or a specific connection.
        
        Args:
            alert_type: Alert type (info, warning, error, critical)
            title: Alert title
            message: Alert message
            source: Alert source
            data: Additional data
            connection_id: Specific connection (None for broadcast)
        """
        if connection_id:
            await self.send_to_connection(
                connection_id,
                {
                    'alert_type': alert_type,
                    'title': title,
                    'message': message,
                    'source': source,
                    'data': data or {},
                    'timestamp': datetime.now().isoformat()
                },
                SSEEventType.ALERT_TRIGGERED
            )
        else:
            await self.broadcaster.send_alert(alert_type, title, message, source, data)
    
    async def send_metric_update(
        self,
        metric_name: str,
        value: Any,
        unit: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        connection_id: Optional[str] = None
    ):
        """
        Send a metric update to all connections or a specific connection.
        
        Args:
            metric_name: Metric name
            value: Metric value
            unit: Unit of measurement
            tags: Additional tags
            connection_id: Specific connection (None for broadcast)
        """
        if connection_id:
            await self.send_to_connection(
                connection_id,
                {
                    'metric_name': metric_name,
                    'value': value,
                    'unit': unit,
                    'tags': tags or {},
                    'timestamp': datetime.now().isoformat()
                },
                SSEEventType.METRIC_UPDATE
            )
        else:
            await self.broadcaster.send_metric_update(metric_name, value, unit, tags)
    
    def set_default_event_filter(self, event_filter: Optional[EventFilter]):
        """Set default event filter for new connections."""
        self._default_event_filter = event_filter
        logger.info("Updated default event filter")
    
    def add_pre_broadcast_hook(self, hook: Callable[[SSEEvent], SSEEvent]):
        """Add a pre-broadcast hook that can modify events before broadcasting."""
        self._pre_broadcast_hooks.append(hook)
    
    def add_post_broadcast_hook(self, hook: Callable[[SSEEvent, int], None]):
        """Add a post-broadcast hook that is called after broadcasting."""
        self._post_broadcast_hooks.append(hook)
    
    def remove_pre_broadcast_hook(self, hook: Callable[[SSEEvent], SSEEvent]):
        """Remove a pre-broadcast hook."""
        if hook in self._pre_broadcast_hooks:
            self._pre_broadcast_hooks.remove(hook)
    
    def remove_post_broadcast_hook(self, hook: Callable[[SSEEvent, int], None]):
        """Remove a post-broadcast hook."""
        if hook in self._post_broadcast_hooks:
            self._post_broadcast_hooks.remove(hook)
    
    def add_event_listener(self, listener: Callable[[SSEEvent], None]):
        """Add an event listener to the broadcaster."""
        self.broadcaster.add_event_listener(listener)
    
    def remove_event_listener(self, listener: Callable[[SSEEvent], None]):
        """Remove an event listener from the broadcaster."""
        self.broadcaster.remove_event_listener(listener)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive SSE statistics."""
        broadcaster_stats = self.broadcaster.get_stats()
        connection_stats = await self.broadcaster.get_connection_stats()
        
        async with self._connection_lock:
            total_registered = len(self._connections)
        
        return {
            'manager': {
                'max_connections': self.max_connections,
                'registered_connections': total_registered,
                'heartbeat_interval': self.heartbeat_interval,
                'buffer_size': self.buffer_size
            },
            'broadcaster': broadcaster_stats.to_dict(),
            'connections': connection_stats,
            'performance': {
                'events_per_second': broadcaster_stats.average_events_per_second,
                'peak_connections': broadcaster_stats.peak_connections,
                'uptime_seconds': broadcaster_stats.uptime_seconds
            }
        }
    
    async def get_connection_list(self) -> List[Dict[str, Any]]:
        """Get list of all connections with their details."""
        async with self._connection_lock:
            return [conn.to_dict() for conn in self._connections.values()]
    
    async def get_recent_events(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent events from the buffer."""
        events = self.broadcaster.get_event_buffer(count)
        return [event.to_dict() for event in events]
    
    async def get_event_history_stats(self, hours: int = 1) -> Dict[str, Any]:
        """Get event statistics for the last N hours."""
        return self.broadcaster.get_event_history_stats(hours)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the SSE system."""
        stats = await self.get_stats()
        
        health_status = "healthy"
        issues = []
        
        # Check connection count
        active_connections = stats['broadcaster']['active_connections']
        if active_connections >= self.max_connections * 0.9:
            health_status = "warning"
            issues.append("High connection count")
        
        # Check error rate
        total_errors = stats['broadcaster']['total_errors']
        if total_errors > 0:
            error_rate = total_errors / max(stats['broadcaster']['total_events_sent'], 1)
            if error_rate > 0.05:  # 5% error rate
                health_status = "degraded"
                issues.append(f"High error rate: {error_rate:.1%}")
        
        return {
            'status': health_status,
            'timestamp': datetime.now().isoformat(),
            'active_connections': active_connections,
            'max_connections': self.max_connections,
            'total_events_sent': stats['broadcaster']['total_events_sent'],
            'total_errors': total_errors,
            'uptime_seconds': stats['broadcaster']['uptime_seconds'],
            'issues': issues
        }
    
    @property
    def is_running(self) -> bool:
        """Check if SSE manager is running."""
        return self.broadcaster.is_running
    
    @property
    def active_connections(self) -> int:
        """Get number of active connections."""
        return self.broadcaster.active_connections