"""
Event streaming service that integrates event configuration with SSE infrastructure.

This module provides real-time streaming of monitoring events configured through
the event configuration system to connected dashboard clients via SSE.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from threading import RLock
import json

from ..sse.manager import SSEManager
from ..sse.models import SSEEvent, SSEEventType, EventFilter
from ..notifications.event_config import (
    EventConfigurationService, get_event_config_service,
    EventType, EventConfiguration, process_system_event
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class EventStreamer:
    """
    Service that streams monitoring events in real-time via SSE.
    
    Integrates the event configuration system with SSE infrastructure to provide
    real-time event streaming to dashboard clients.
    """
    
    def __init__(self, sse_manager: Optional[SSEManager] = None):
        """
        Initialize event streamer.
        
        Args:
            sse_manager: SSE manager instance (creates default if None)
        """
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # SSE Infrastructure
        self.sse_manager = sse_manager or SSEManager(
            buffer_size=1000,
            heartbeat_interval=30,
            max_connections=50,
            stats_interval=60
        )
        
        # Event Configuration
        self.event_config_service = get_event_config_service()
        
        # Stream state
        self._is_running = False
        self._stream_tasks: List[asyncio.Task] = []
        
        # Event mapping
        self._event_type_mapping = self._create_event_type_mapping()
        
        # Event listeners
        self._event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        
        # Statistics
        self._stats = {
            'events_streamed': 0,
            'events_filtered': 0,
            'connections_served': 0,
            'start_time': None,
            'last_event_time': None
        }
        
        logger.info("EventStreamer initialized")
    
    def _create_event_type_mapping(self) -> Dict[EventType, SSEEventType]:
        """Create mapping between EventType and SSEEventType."""
        return {
            EventType.SYSTEM_STARTUP: SSEEventType.SYSTEM_STARTUP,
            EventType.SYSTEM_SHUTDOWN: SSEEventType.SYSTEM_SHUTDOWN,
            EventType.SERVICE_START: SSEEventType.SERVICE_STARTED,
            EventType.SERVICE_STOP: SSEEventType.SERVICE_STOPPED,
            EventType.SERVICE_RESTART: SSEEventType.SERVICE_RESTARTED,
            EventType.SERVICE_FAILURE: SSEEventType.SERVICE_ERROR,
            EventType.PROCESSING_ERROR: SSEEventType.TASK_FAILED,
            EventType.HIGH_CPU_USAGE: SSEEventType.METRIC_UPDATE,
            EventType.HIGH_MEMORY_USAGE: SSEEventType.METRIC_UPDATE,
            EventType.LOW_DISK_SPACE: SSEEventType.METRIC_UPDATE,
            EventType.QUEUE_FULL: SSEEventType.ALERT_TRIGGERED,
            EventType.QUEUE_EMPTY: SSEEventType.METRIC_UPDATE,
            EventType.QUEUE_STALLED: SSEEventType.ALERT_TRIGGERED,
            EventType.CONNECTION_LOST: SSEEventType.ALERT_TRIGGERED,
            EventType.CONNECTION_RESTORED: SSEEventType.ALERT_TRIGGERED,
            EventType.SCHEDULE_EXECUTED: SSEEventType.SCHEDULE_TRIGGERED,
            EventType.SCHEDULE_FAILED: SSEEventType.TASK_FAILED,
            EventType.BACKUP_COMPLETED: SSEEventType.TASK_COMPLETED,
            EventType.BACKUP_FAILED: SSEEventType.TASK_FAILED,
            EventType.MAINTENANCE_START: SSEEventType.ALERT_TRIGGERED,
            EventType.MAINTENANCE_END: SSEEventType.ALERT_TRIGGERED,
            EventType.CUSTOM_EVENT: SSEEventType.CUSTOM
        }
    
    async def start(self):
        """Start the event streaming service."""
        with self._lock:
            if self._is_running:
                logger.warning("Event streamer is already running")
                return
            
            self._is_running = True
            self._stats['start_time'] = datetime.now()
        
        # Start SSE manager
        await self.sse_manager.start()
        
        # Set up event processing hook
        self.event_config_service._event_stream_hook = self._process_event_for_streaming
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.CONFIGURATION,
            change_type=ChangeType.UPDATE,
            description="Event streaming service started",
            details={'start_time': self._stats['start_time'].isoformat()}
        )
        
        logger.info("Event streaming service started")
    
    async def stop(self):
        """Stop the event streaming service."""
        with self._lock:
            if not self._is_running:
                return
            
            self._is_running = False
        
        # Cancel stream tasks
        for task in self._stream_tasks:
            task.cancel()
        
        if self._stream_tasks:
            await asyncio.gather(*self._stream_tasks, return_exceptions=True)
        
        self._stream_tasks.clear()
        
        # Stop SSE manager
        await self.sse_manager.stop()
        
        # Remove event processing hook
        if hasattr(self.event_config_service, '_event_stream_hook'):
            delattr(self.event_config_service, '_event_stream_hook')
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.CONFIGURATION,
            change_type=ChangeType.UPDATE,
            description="Event streaming service stopped",
            details={'stop_time': datetime.now().isoformat()}
        )
        
        logger.info("Event streaming service stopped")
    
    def _process_event_for_streaming(self, event_type: EventType, context: Dict[str, Any], 
                                   notifications: List[Dict[str, Any]]):
        """
        Process events for streaming (called by event config service).
        
        Args:
            event_type: The event type that occurred
            context: Event context data
            notifications: Generated notifications
        """
        if not self._is_running:
            return
        
        try:
            # Create streaming event
            streaming_event = self._create_streaming_event(event_type, context, notifications)
            
            # Stream event asynchronously
            task = asyncio.create_task(self._stream_event(streaming_event))
            self._stream_tasks.append(task)
            
            # Clean up completed tasks
            self._cleanup_completed_tasks()
            
        except Exception as e:
            logger.error(f"Error processing event for streaming: {e}")
    
    def _create_streaming_event(self, event_type: EventType, context: Dict[str, Any], 
                               notifications: List[Dict[str, Any]]) -> SSEEvent:
        """Create SSE event from monitoring event."""
        # Map to SSE event type
        sse_event_type = self._event_type_mapping.get(event_type, SSEEventType.CUSTOM)
        
        # Prepare event data
        event_data = {
            'monitoring_event_type': event_type.value,
            'context': context,
            'notification_count': len(notifications),
            'notifications': notifications,
            'severity': self._determine_event_severity(event_type, context),
            'source': context.get('source', 'monitoring'),
            'category': context.get('category', 'general'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add specific data based on event type
        if event_type in [EventType.HIGH_CPU_USAGE, EventType.HIGH_MEMORY_USAGE]:
            event_data['metric_name'] = context.get('metric', event_type.value)
            event_data['metric_value'] = context.get('value', context.get('cpu_percent', context.get('memory_percent')))
            event_data['metric_unit'] = '%'
        
        elif event_type == EventType.LOW_DISK_SPACE:
            event_data['metric_name'] = 'disk_usage'
            event_data['metric_value'] = context.get('disk_percent', 0)
            event_data['metric_unit'] = '%'
        
        elif event_type in [EventType.QUEUE_FULL, EventType.QUEUE_EMPTY, EventType.QUEUE_STALLED]:
            event_data['queue_size'] = context.get('queue_size', 0)
            event_data['queue_max_size'] = context.get('max_size', 0)
        
        elif event_type == EventType.SERVICE_FAILURE:
            event_data['service_name'] = context.get('service_name', 'unknown')
            event_data['error_message'] = context.get('error_message', '')
        
        return SSEEvent(
            event_type=sse_event_type,
            data=event_data
        )
    
    def _determine_event_severity(self, event_type: EventType, context: Dict[str, Any]) -> str:
        """Determine event severity based on type and context."""
        critical_events = [
            EventType.SYSTEM_SHUTDOWN,
            EventType.SERVICE_FAILURE,
            EventType.CONNECTION_LOST
        ]
        
        warning_events = [
            EventType.HIGH_CPU_USAGE,
            EventType.HIGH_MEMORY_USAGE,
            EventType.LOW_DISK_SPACE,
            EventType.QUEUE_FULL,
            EventType.QUEUE_STALLED,
            EventType.SCHEDULE_FAILED,
            EventType.BACKUP_FAILED
        ]
        
        if event_type in critical_events:
            return 'critical'
        elif event_type in warning_events:
            return 'warning'
        else:
            return 'info'
    
    async def _stream_event(self, event: SSEEvent):
        """Stream event to all connected clients."""
        try:
            # Apply event listeners
            for listener in self._event_listeners:
                try:
                    listener(event.to_dict())
                except Exception as e:
                    logger.error(f"Error in event listener: {e}")
            
            # Broadcast event
            sent_count = await self.sse_manager.broadcast_event(event)
            
            # Update statistics
            with self._lock:
                self._stats['events_streamed'] += 1
                self._stats['last_event_time'] = datetime.now()
                if sent_count > 0:
                    self._stats['connections_served'] = max(
                        self._stats['connections_served'], 
                        sent_count
                    )
            
            logger.debug(f"Streamed event {event.event_type.value} to {sent_count} connections")
            
        except Exception as e:
            logger.error(f"Error streaming event: {e}")
    
    def _cleanup_completed_tasks(self):
        """Clean up completed stream tasks."""
        self._stream_tasks = [task for task in self._stream_tasks if not task.done()]
    
    async def create_client_stream(self, client_id: str, event_filter: Optional[Dict[str, Any]] = None):
        """
        Create an event stream for a specific client.
        
        Args:
            client_id: Client identifier
            event_filter: Optional event filter parameters
            
        Returns:
            Async generator for client events
        """
        if not self._is_running:
            raise RuntimeError("Event streaming service is not running")
        
        # Create SSE connection
        connection_id = await self.sse_manager.create_connection(
            client_ip="dashboard",
            user_agent=f"dashboard-client-{client_id}",
            client_info={'client_id': client_id}
        )
        
        # Create event filter if specified
        sse_filter = None
        if event_filter:
            event_types = event_filter.get('event_types', [])
            sources = event_filter.get('sources', [])
            min_priority = event_filter.get('min_priority')
            
            sse_filter = EventFilter(
                event_types=event_types,
                sources=sources,
                min_priority=min_priority
            )
        
        try:
            # Get event stream
            async for event_data in self.sse_manager.get_event_stream(connection_id, sse_filter):
                yield event_data
        
        finally:
            # Clean up connection
            await self.sse_manager.disconnect_connection(connection_id)
    
    async def send_dashboard_event(self, event_type: str, data: Dict[str, Any]):
        """
        Send a dashboard-specific event.
        
        Args:
            event_type: Dashboard event type
            data: Event data
        """
        event = SSEEvent(
            event_type=SSEEventType.DASHBOARD_REFRESH,
            data={
                'dashboard_event_type': event_type,
                'timestamp': datetime.now().isoformat(),
                **data
            }
        )
        
        await self.sse_manager.broadcast_event(event)
    
    async def send_system_alert(self, severity: str, title: str, message: str, 
                               source: str = "system", data: Optional[Dict[str, Any]] = None):
        """
        Send a system alert via SSE.
        
        Args:
            severity: Alert severity (info, warning, error, critical)
            title: Alert title
            message: Alert message
            source: Alert source
            data: Additional data
        """
        await self.sse_manager.send_alert(severity, title, message, source, data)
    
    async def send_metric_update(self, metric_name: str, value: Any, 
                                unit: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        """
        Send a metric update via SSE.
        
        Args:
            metric_name: Metric name
            value: Metric value
            unit: Unit of measurement
            tags: Additional tags
        """
        await self.sse_manager.send_metric_update(metric_name, value, unit, tags)
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]):
        """Add an event listener for processed events."""
        self._event_listeners.append(listener)
    
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]):
        """Remove an event listener."""
        if listener in self._event_listeners:
            self._event_listeners.remove(listener)
    
    async def get_streaming_stats(self) -> Dict[str, Any]:
        """Get streaming service statistics."""
        sse_stats = await self.sse_manager.get_stats()
        
        with self._lock:
            uptime = None
            if self._stats['start_time']:
                uptime = (datetime.now() - self._stats['start_time']).total_seconds()
            
            return {
                'streaming': {
                    'is_running': self._is_running,
                    'events_streamed': self._stats['events_streamed'],
                    'events_filtered': self._stats['events_filtered'],
                    'connections_served': self._stats['connections_served'],
                    'uptime_seconds': uptime,
                    'last_event_time': self._stats['last_event_time'].isoformat() if self._stats['last_event_time'] else None
                },
                'sse': sse_stats,
                'event_listeners': len(self._event_listeners)
            }
    
    async def get_active_connections(self) -> List[Dict[str, Any]]:
        """Get list of active SSE connections."""
        return await self.sse_manager.get_connection_list()
    
    async def get_recent_events(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent streamed events."""
        return await self.sse_manager.get_recent_events(count)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of streaming service."""
        sse_health = await self.sse_manager.health_check()
        
        streaming_health = "healthy"
        issues = []
        
        # Check if service is running
        if not self._is_running:
            streaming_health = "stopped"
            issues.append("Streaming service is not running")
        
        # Check event processing rate
        with self._lock:
            if self._stats['start_time']:
                uptime = (datetime.now() - self._stats['start_time']).total_seconds()
                if uptime > 300 and self._stats['events_streamed'] == 0:  # 5 minutes with no events
                    streaming_health = "warning"
                    issues.append("No events processed in last 5 minutes")
        
        return {
            'streaming': {
                'status': streaming_health,
                'issues': issues,
                'is_running': self._is_running
            },
            'sse': sse_health
        }
    
    @property
    def is_running(self) -> bool:
        """Check if streaming service is running."""
        return self._is_running
    
    @property
    def active_connections(self) -> int:
        """Get number of active connections."""
        return self.sse_manager.active_connections


# Singleton instance
_event_streamer: Optional[EventStreamer] = None
_streamer_lock = RLock()


def get_event_streamer() -> EventStreamer:
    """Get singleton event streamer instance."""
    global _event_streamer
    
    with _streamer_lock:
        if _event_streamer is None:
            _event_streamer = EventStreamer()
        
        return _event_streamer


def reset_event_streamer():
    """Reset the singleton event streamer (mainly for testing)."""
    global _event_streamer
    
    with _streamer_lock:
        if _event_streamer and _event_streamer.is_running:
            asyncio.create_task(_event_streamer.stop())
        
        _event_streamer = None


# Integration functions
async def start_event_streaming():
    """Start the event streaming service."""
    streamer = get_event_streamer()
    await streamer.start()


async def stop_event_streaming():
    """Stop the event streaming service."""
    streamer = get_event_streamer()
    await streamer.stop()


async def stream_system_event(event_type: EventType, **context):
    """
    Trigger a system event and stream it.
    
    Args:
        event_type: System event type
        **context: Event context data
    """
    # Process through event configuration system (which will trigger streaming)
    process_system_event(event_type, **context)