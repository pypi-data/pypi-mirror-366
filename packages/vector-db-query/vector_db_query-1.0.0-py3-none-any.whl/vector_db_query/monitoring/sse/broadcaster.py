"""
Event broadcaster for multi-client SSE distribution.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable, Any
from threading import RLock
from collections import defaultdict, deque

from .models import SSEEvent, SSEEventType, SSEStats, HeartbeatEvent, AlertEvent
from .stream import EventStream, StreamManager

logger = logging.getLogger(__name__)


class EventBroadcaster:
    """
    Broadcasts events to multiple SSE client streams.
    
    Provides efficient event distribution with filtering, buffering, and statistics.
    """
    
    def __init__(
        self,
        buffer_size: int = 1000,
        stats_interval: int = 60,
        cleanup_interval: int = 300
    ):
        """
        Initialize event broadcaster.
        
        Args:
            buffer_size: Maximum events to buffer for new connections
            stats_interval: Statistics update interval in seconds
            cleanup_interval: Cleanup interval for inactive connections
        """
        self.buffer_size = buffer_size
        self.stats_interval = stats_interval
        self.cleanup_interval = cleanup_interval
        
        # Stream management
        self.stream_manager = StreamManager()
        
        # Event buffering for new connections
        self._event_buffer: deque = deque(maxlen=buffer_size)
        self._buffer_lock = RLock()
        
        # Statistics
        self._stats = SSEStats()
        self._start_time = datetime.now()
        self._event_history: deque = deque(maxlen=10000)  # Keep last 10k events for stats
        
        # Background tasks
        self._running = False
        self._stats_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        # Event callbacks
        self._event_listeners: List[Callable[[SSEEvent], None]] = []
        
        logger.info("EventBroadcaster initialized")
    
    async def start(self):
        """Start the event broadcaster."""
        if self._running:
            logger.warning("EventBroadcaster is already running")
            return
        
        self._running = True
        self._start_time = datetime.now()
        
        # Start background tasks
        self._stats_task = asyncio.create_task(self._stats_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Send startup event
        startup_event = SSEEvent(
            event_type=SSEEventType.SYSTEM_STARTUP,
            data={
                'timestamp': datetime.now().isoformat(),
                'broadcaster_id': id(self)
            }
        )
        await self.broadcast_event(startup_event)
        
        logger.info("EventBroadcaster started")
    
    async def stop(self):
        """Stop the event broadcaster."""
        if not self._running:
            logger.warning("EventBroadcaster is not running")
            return
        
        self._running = False
        
        # Send shutdown event
        shutdown_event = SSEEvent(
            event_type=SSEEventType.SYSTEM_SHUTDOWN,
            data={
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': (datetime.now() - self._start_time).total_seconds()
            }
        )
        await self.broadcast_event(shutdown_event)
        
        # Cancel background tasks
        for task in [self._stats_task, self._cleanup_task, self._heartbeat_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Shutdown stream manager
        await self.stream_manager.shutdown()
        
        logger.info("EventBroadcaster stopped")
    
    async def add_stream(self, stream: EventStream, send_buffer: bool = True):
        """
        Add a new event stream.
        
        Args:
            stream: EventStream to add
            send_buffer: Whether to send buffered events to new stream
        """
        await self.stream_manager.add_stream(stream)
        
        # Send buffered events to new stream if requested
        if send_buffer:
            with self._buffer_lock:
                for event in self._event_buffer:
                    await stream.send_event(event)
        
        # Update stats
        self._stats.active_connections = self.stream_manager.active_stream_count
        self._stats.total_connections += 1
        
        if self._stats.active_connections > self._stats.peak_connections:
            self._stats.peak_connections = self._stats.active_connections
        
        logger.info(f"Added stream {stream.connection.connection_id} (total: {self._stats.active_connections})")
    
    async def remove_stream(self, connection_id: str):
        """Remove an event stream."""
        removed = await self.stream_manager.remove_stream(connection_id)
        
        if removed:
            self._stats.active_connections = self.stream_manager.active_stream_count
            logger.info(f"Removed stream {connection_id} (total: {self._stats.active_connections})")
        
        return removed
    
    async def broadcast_event(
        self, 
        event: SSEEvent, 
        exclude_connections: Optional[Set[str]] = None
    ) -> int:
        """
        Broadcast event to all connected streams.
        
        Args:
            event: Event to broadcast
            exclude_connections: Connection IDs to exclude
            
        Returns:
            Number of streams that received the event
        """
        if not self._running:
            return 0
        
        # Add to buffer
        with self._buffer_lock:
            self._event_buffer.append(event)
        
        # Add to history for stats
        self._event_history.append({
            'timestamp': event.timestamp,
            'event_type': event.event_type.value if isinstance(event.event_type, SSEEventType) else event.event_type,
            'data_size': len(str(event.data))
        })
        
        # Broadcast to streams
        sent_count = await self.stream_manager.broadcast_event(event)
        
        # Update statistics
        event_type_str = event.event_type.value if isinstance(event.event_type, SSEEventType) else event.event_type
        self._stats.events_by_type[event_type_str] = self._stats.events_by_type.get(event_type_str, 0) + 1
        self._stats.total_events_sent += sent_count
        
        # Call event listeners
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in event listener: {str(e)}")
        
        return sent_count
    
    async def send_to_connection(self, connection_id: str, event: SSEEvent) -> bool:
        """Send event to a specific connection."""
        return await self.stream_manager.send_to_stream(connection_id, event)
    
    async def send_alert(
        self, 
        alert_type: str, 
        title: str, 
        message: str, 
        source: str = "system",
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Send an alert event to all connections.
        
        Args:
            alert_type: Type of alert (info, warning, error, critical)
            title: Alert title
            message: Alert message
            source: Alert source
            data: Additional alert data
        """
        alert = AlertEvent(
            alert_type=alert_type,
            title=title,
            message=message,
            source=source,
            data=data or {}
        )
        
        await self.broadcast_event(alert.to_sse_event())
    
    async def send_metric_update(
        self, 
        metric_name: str, 
        value: Any, 
        unit: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Send a metric update event.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            tags: Additional tags
        """
        metric_event = SSEEvent(
            event_type=SSEEventType.METRIC_UPDATE,
            data={
                'metric_name': metric_name,
                'value': value,
                'unit': unit,
                'tags': tags or {},
                'timestamp': datetime.now().isoformat()
            }
        )
        
        await self.broadcast_event(metric_event)
    
    def add_event_listener(self, listener: Callable[[SSEEvent], None]):
        """Add an event listener."""
        self._event_listeners.append(listener)
    
    def remove_event_listener(self, listener: Callable[[SSEEvent], None]):
        """Remove an event listener."""
        if listener in self._event_listeners:
            self._event_listeners.remove(listener)
    
    def get_stats(self) -> SSEStats:
        """Get current statistics."""
        self._stats.active_connections = self.stream_manager.active_stream_count
        self._stats.uptime_seconds = (datetime.now() - self._start_time).total_seconds()
        
        # Calculate events per second
        if self._stats.uptime_seconds > 0:
            self._stats.average_events_per_second = self._stats.total_events_sent / self._stats.uptime_seconds
        
        return self._stats
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get detailed connection statistics."""
        return await self.stream_manager.get_stream_stats()
    
    def get_event_buffer(self, count: Optional[int] = None) -> List[SSEEvent]:
        """
        Get recent events from buffer.
        
        Args:
            count: Number of events to return (None for all)
            
        Returns:
            List of recent events
        """
        with self._buffer_lock:
            if count is None:
                return list(self._event_buffer)
            else:
                return list(self._event_buffer)[-count:]
    
    def get_event_history_stats(self, hours: int = 1) -> Dict[str, Any]:
        """
        Get event statistics for the last N hours.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Event statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_events = [
            event for event in self._event_history 
            if event['timestamp'] >= cutoff_time
        ]
        
        # Count by event type
        event_counts = defaultdict(int)
        total_data_size = 0
        
        for event in recent_events:
            event_counts[event['event_type']] += 1
            total_data_size += event['data_size']
        
        return {
            'time_period_hours': hours,
            'total_events': len(recent_events),
            'events_per_hour': len(recent_events) / hours if hours > 0 else 0,
            'total_data_size_bytes': total_data_size,
            'events_by_type': dict(event_counts),
            'average_event_size': total_data_size / len(recent_events) if recent_events else 0
        }
    
    async def _stats_loop(self):
        """Background task for updating statistics."""
        while self._running:
            try:
                await asyncio.sleep(self.stats_interval)
                
                if not self._running:
                    break
                
                # Update stats
                stats = self.get_stats()
                
                # Send stats update event
                stats_event = SSEEvent(
                    event_type=SSEEventType.METRIC_UPDATE,
                    data={
                        'metric_name': 'sse_stats',
                        'value': stats.to_dict(),
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                await self.broadcast_event(stats_event)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in stats loop: {str(e)}")
    
    async def _cleanup_loop(self):
        """Background task for cleaning up inactive connections."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                if not self._running:
                    break
                
                # Cleanup inactive streams
                await self.stream_manager.cleanup_inactive_streams(
                    max_age_seconds=self.cleanup_interval
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")
    
    async def _heartbeat_loop(self):
        """Background task for sending heartbeat events."""
        while self._running:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                if not self._running:
                    break
                
                # Create heartbeat event
                heartbeat = HeartbeatEvent(
                    uptime_seconds=self._stats.uptime_seconds,
                    active_tasks=0,  # This would be filled by the monitoring system
                    active_schedules=0  # This would be filled by the scheduler
                )
                
                await self.broadcast_event(heartbeat.to_sse_event())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {str(e)}")
    
    @property
    def is_running(self) -> bool:
        """Check if broadcaster is running."""
        return self._running
    
    @property
    def active_connections(self) -> int:
        """Get number of active connections."""
        return self.stream_manager.active_stream_count
    
    @property
    def buffer_size_current(self) -> int:
        """Get current buffer size."""
        with self._buffer_lock:
            return len(self._event_buffer)