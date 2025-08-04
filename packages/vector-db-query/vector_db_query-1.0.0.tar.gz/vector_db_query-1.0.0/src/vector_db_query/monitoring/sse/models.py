"""
Data models for SSE infrastructure.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class SSEEventType(Enum):
    """Types of SSE events."""
    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    HEARTBEAT = "heartbeat"
    
    # Scheduler events
    SCHEDULE_ADDED = "schedule_added"
    SCHEDULE_UPDATED = "schedule_updated"
    SCHEDULE_REMOVED = "schedule_removed"
    SCHEDULE_TRIGGERED = "schedule_triggered"
    
    # Task events
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"
    
    # Service events
    SERVICE_STARTED = "service_started"
    SERVICE_STOPPED = "service_stopped"
    SERVICE_RESTARTED = "service_restarted"
    SERVICE_ERROR = "service_error"
    
    # File events
    FILE_PROCESSED = "file_processed"
    FILE_ERROR = "file_error"
    BATCH_COMPLETED = "batch_completed"
    
    # Monitoring events
    METRIC_UPDATE = "metric_update"
    HEALTH_CHECK = "health_check"
    ALERT_TRIGGERED = "alert_triggered"
    
    # UI events
    DASHBOARD_REFRESH = "dashboard_refresh"
    USER_ACTION = "user_action"
    
    # Custom events
    CUSTOM = "custom"


class ConnectionStatus(Enum):
    """SSE connection status."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class SSEEvent:
    """Represents a Server-Sent Event."""
    event_type: Union[SSEEventType, str] = SSEEventType.CUSTOM
    data: Dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    retry: Optional[int] = None  # Retry timeout in milliseconds
    
    def to_sse_format(self) -> str:
        """Convert event to SSE format string."""
        lines = []
        
        # Event type
        if isinstance(self.event_type, SSEEventType):
            lines.append(f"event: {self.event_type.value}")
        else:
            lines.append(f"event: {self.event_type}")
        
        # Event ID
        lines.append(f"id: {self.event_id}")
        
        # Retry timeout
        if self.retry:
            lines.append(f"retry: {self.retry}")
        
        # Data (JSON encoded)
        event_data = {
            'timestamp': self.timestamp.isoformat(),
            **self.data
        }
        data_json = json.dumps(event_data, default=str)
        
        # Handle multi-line data
        for line in data_json.split('\n'):
            lines.append(f"data: {line}")
        
        # Add empty line to end the event
        lines.append("")
        
        return '\n'.join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_type': self.event_type.value if isinstance(self.event_type, SSEEventType) else self.event_type,
            'data': self.data,
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'retry': self.retry
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SSEEvent':
        """Create from dictionary."""
        # Convert timestamp
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Convert event type
        if 'event_type' in data:
            try:
                data['event_type'] = SSEEventType(data['event_type'])
            except ValueError:
                # Keep as string for custom events
                pass
        
        return cls(**data)


@dataclass
class SSEConnection:
    """Represents an SSE client connection."""
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_ip: str = "unknown"
    user_agent: str = "unknown"
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    status: ConnectionStatus = ConnectionStatus.CONNECTING
    
    # Connection metadata
    client_info: Dict[str, Any] = field(default_factory=dict)
    subscribed_events: List[str] = field(default_factory=list)
    
    # Statistics
    events_sent: int = 0
    bytes_sent: int = 0
    errors_count: int = 0
    
    @property
    def duration(self) -> float:
        """Get connection duration in seconds."""
        return (datetime.now() - self.connected_at).total_seconds()
    
    @property
    def is_active(self) -> bool:
        """Check if connection is active."""
        return self.status == ConnectionStatus.CONNECTED
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'connection_id': self.connection_id,
            'client_ip': self.client_ip,
            'user_agent': self.user_agent,
            'connected_at': self.connected_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'status': self.status.value,
            'client_info': self.client_info,
            'subscribed_events': self.subscribed_events,
            'events_sent': self.events_sent,
            'bytes_sent': self.bytes_sent,
            'errors_count': self.errors_count,
            'duration_seconds': self.duration
        }


@dataclass
class SSEStats:
    """Statistics for SSE infrastructure."""
    active_connections: int = 0
    total_connections: int = 0
    total_events_sent: int = 0
    total_bytes_sent: int = 0
    total_errors: int = 0
    
    # Event type statistics
    events_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Performance metrics
    average_events_per_second: float = 0.0
    peak_connections: int = 0
    uptime_seconds: float = 0.0
    
    # Connection statistics
    average_connection_duration: float = 0.0
    connection_errors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'active_connections': self.active_connections,
            'total_connections': self.total_connections,
            'total_events_sent': self.total_events_sent,
            'total_bytes_sent': self.total_bytes_sent,
            'total_errors': self.total_errors,
            'events_by_type': self.events_by_type,
            'performance': {
                'average_events_per_second': self.average_events_per_second,
                'peak_connections': self.peak_connections,
                'uptime_seconds': self.uptime_seconds
            },
            'connections': {
                'average_duration': self.average_connection_duration,
                'connection_errors': self.connection_errors
            }
        }


@dataclass
class HeartbeatEvent:
    """Heartbeat event data."""
    timestamp: datetime = field(default_factory=datetime.now)
    server_time: str = field(default_factory=lambda: datetime.now().isoformat())
    uptime_seconds: float = 0.0
    active_tasks: int = 0
    active_schedules: int = 0
    system_load: Optional[float] = None
    memory_usage: Optional[float] = None
    
    def to_sse_event(self) -> SSEEvent:
        """Convert to SSE event."""
        return SSEEvent(
            event_type=SSEEventType.HEARTBEAT,
            data=self.__dict__
        )


@dataclass
class MetricUpdate:
    """Metric update event data."""
    metric_name: str
    value: Union[int, float, str]
    timestamp: datetime = field(default_factory=datetime.now)
    unit: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_sse_event(self) -> SSEEvent:
        """Convert to SSE event."""
        return SSEEvent(
            event_type=SSEEventType.METRIC_UPDATE,
            data={
                'metric_name': self.metric_name,
                'value': self.value,
                'timestamp': self.timestamp.isoformat(),
                'unit': self.unit,
                'tags': self.tags
            }
        )


@dataclass
class AlertEvent:
    """Alert event data."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str = "info"  # info, warning, error, critical
    title: str = ""
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "system"
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_sse_event(self) -> SSEEvent:
        """Convert to SSE event."""
        return SSEEvent(
            event_type=SSEEventType.ALERT_TRIGGERED,
            data={
                'alert_id': self.alert_id,
                'alert_type': self.alert_type,
                'title': self.title,
                'message': self.message,
                'timestamp': self.timestamp.isoformat(),
                'source': self.source,
                'data': self.data
            }
        )


class EventFilter:
    """Filter for SSE events."""
    
    def __init__(
        self,
        event_types: Optional[List[Union[SSEEventType, str]]] = None,
        sources: Optional[List[str]] = None,
        min_priority: Optional[str] = None
    ):
        """
        Initialize event filter.
        
        Args:
            event_types: List of event types to include
            sources: List of event sources to include
            min_priority: Minimum priority level
        """
        self.event_types = set(event_types) if event_types else None
        self.sources = set(sources) if sources else None
        self.min_priority = min_priority
    
    def should_include(self, event: SSEEvent) -> bool:
        """Check if event should be included."""
        # Check event type
        if self.event_types:
            event_type = event.event_type
            if isinstance(event_type, SSEEventType):
                event_type = event_type.value
            
            if event_type not in self.event_types:
                return False
        
        # Check source
        if self.sources:
            event_source = event.data.get('source', 'unknown')
            if event_source not in self.sources:
                return False
        
        # Check priority (if specified)
        if self.min_priority:
            event_priority = event.data.get('priority', 'info')
            priority_levels = ['debug', 'info', 'warning', 'error', 'critical']
            
            try:
                min_level = priority_levels.index(self.min_priority)
                event_level = priority_levels.index(event_priority)
                
                if event_level < min_level:
                    return False
            except ValueError:
                # Invalid priority, include by default
                pass
        
        return True