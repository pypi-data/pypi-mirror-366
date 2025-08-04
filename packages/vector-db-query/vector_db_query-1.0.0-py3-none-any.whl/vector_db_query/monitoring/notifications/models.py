"""
Data models for the notification system.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class NotificationSeverity(Enum):
    """Notification severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    PUSH = "push"
    TOAST = "toast"
    WEBHOOK = "webhook"
    SMS = "sms"
    SLACK = "slack"
    TEAMS = "teams"


class NotificationStatus(Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class DeliveryPriority(Enum):
    """Notification delivery priority."""
    LOW = "low"
    NORMAL = "normal" 
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    """Represents a notification to be sent."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    message: str = ""
    severity: NotificationSeverity = NotificationSeverity.INFO
    
    # Targeting
    channels: List[NotificationChannel] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)  # emails, user IDs, etc.
    
    # Content
    data: Dict[str, Any] = field(default_factory=dict)
    template_name: Optional[str] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    
    # Behavior
    priority: DeliveryPriority = DeliveryPriority.NORMAL
    expires_at: Optional[datetime] = None
    retry_count: int = 3
    delay_seconds: int = 0
    
    # Metadata
    source: str = "system"
    event_type: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    # Tracking
    status: NotificationStatus = NotificationStatus.PENDING
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    attempts: int = 0
    
    def is_expired(self) -> bool:
        """Check if notification has expired."""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False
    
    def can_retry(self) -> bool:
        """Check if notification can be retried."""
        return (
            self.status == NotificationStatus.FAILED and
            self.attempts < self.retry_count and
            not self.is_expired()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity.value,
            'channels': [ch.value for ch in self.channels],
            'recipients': self.recipients,
            'data': self.data,
            'template_name': self.template_name,
            'template_data': self.template_data,
            'priority': self.priority.value,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'retry_count': self.retry_count,
            'delay_seconds': self.delay_seconds,
            'source': self.source,
            'event_type': self.event_type,
            'correlation_id': self.correlation_id,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'failed_at': self.failed_at.isoformat() if self.failed_at else None,
            'error_message': self.error_message,
            'attempts': self.attempts
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create from dictionary."""
        # Convert datetime strings
        datetime_fields = ['created_at', 'sent_at', 'delivered_at', 'failed_at', 'expires_at']
        for field_name in datetime_fields:
            if field_name in data and data[field_name]:
                if isinstance(data[field_name], str):
                    data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Convert enums
        if 'severity' in data:
            data['severity'] = NotificationSeverity(data['severity'])
        if 'status' in data:
            data['status'] = NotificationStatus(data['status'])
        if 'priority' in data:
            data['priority'] = DeliveryPriority(data['priority'])
        if 'channels' in data:
            data['channels'] = [NotificationChannel(ch) for ch in data['channels']]
        
        return cls(**data)


@dataclass
class NotificationResult:
    """Result of a notification delivery attempt."""
    notification_id: str
    channel: NotificationChannel
    status: NotificationStatus
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Delivery details
    recipient: Optional[str] = None
    delivered_to: Optional[str] = None  # actual delivery address/ID
    delivery_id: Optional[str] = None  # external service delivery ID
    
    # Error information
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_after: Optional[int] = None  # seconds to wait before retry
    
    # Metrics
    processing_time_ms: Optional[int] = None
    size_bytes: Optional[int] = None
    
    @property
    def success(self) -> bool:
        """Check if delivery was successful."""
        return self.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'notification_id': self.notification_id,
            'channel': self.channel.value,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'recipient': self.recipient,
            'delivered_to': self.delivered_to,
            'delivery_id': self.delivery_id,
            'error_code': self.error_code,
            'error_message': self.error_message,
            'retry_after': self.retry_after,
            'processing_time_ms': self.processing_time_ms,
            'size_bytes': self.size_bytes,
            'success': self.success
        }


@dataclass
class ChannelConfig:
    """Configuration for a notification channel."""
    channel: NotificationChannel
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Rate limiting
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    
    # Retry configuration
    max_retries: int = 3
    retry_delay_seconds: int = 60
    exponential_backoff: bool = True
    
    # Filtering
    min_severity: NotificationSeverity = NotificationSeverity.INFO
    allowed_sources: Optional[List[str]] = None
    blocked_sources: Optional[List[str]] = None
    
    def should_deliver(self, notification: Notification) -> bool:
        """Check if notification should be delivered to this channel."""
        if not self.enabled:
            return False
        
        # Check severity
        severity_levels = [
            NotificationSeverity.DEBUG,
            NotificationSeverity.INFO,
            NotificationSeverity.WARNING,
            NotificationSeverity.ERROR,
            NotificationSeverity.CRITICAL
        ]
        
        min_level = severity_levels.index(self.min_severity)
        notification_level = severity_levels.index(notification.severity)
        
        if notification_level < min_level:
            return False
        
        # Check source filters
        if self.allowed_sources and notification.source not in self.allowed_sources:
            return False
        
        if self.blocked_sources and notification.source in self.blocked_sources:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'channel': self.channel.value,
            'enabled': self.enabled,
            'config': self.config,
            'rate_limit_per_minute': self.rate_limit_per_minute,
            'rate_limit_per_hour': self.rate_limit_per_hour,
            'max_retries': self.max_retries,
            'retry_delay_seconds': self.retry_delay_seconds,
            'exponential_backoff': self.exponential_backoff,
            'min_severity': self.min_severity.value,
            'allowed_sources': self.allowed_sources,
            'blocked_sources': self.blocked_sources
        }


@dataclass
class NotificationTemplate:
    """Base notification template."""
    name: str
    title_template: str
    message_template: str
    channel: Optional[NotificationChannel] = None
    
    # Template metadata
    description: str = ""
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Default values
    default_data: Dict[str, Any] = field(default_factory=dict)
    required_variables: List[str] = field(default_factory=list)
    
    def render_title(self, data: Dict[str, Any]) -> str:
        """Render title template with data."""
        template_data = {**self.default_data, **data}
        return self.title_template.format(**template_data)
    
    def render_message(self, data: Dict[str, Any]) -> str:
        """Render message template with data."""
        template_data = {**self.default_data, **data}
        return self.message_template.format(**template_data)
    
    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate template data and return missing variables."""
        missing = []
        for var in self.required_variables:
            if var not in data and var not in self.default_data:
                missing.append(var)
        return missing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'title_template': self.title_template,
            'message_template': self.message_template,
            'channel': self.channel.value if self.channel else None,
            'description': self.description,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'default_data': self.default_data,
            'required_variables': self.required_variables
        }


@dataclass
class NotificationStats:
    """Statistics for notification system."""
    total_sent: int = 0
    total_delivered: int = 0
    total_failed: int = 0
    
    # By channel
    by_channel: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    # By severity
    by_severity: Dict[str, int] = field(default_factory=dict)
    
    # Timing
    average_delivery_time_ms: float = 0.0
    max_delivery_time_ms: int = 0
    
    # Error tracking
    error_rate: float = 0.0
    common_errors: Dict[str, int] = field(default_factory=dict)
    
    # Time period
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_sent == 0:
            return 0.0
        return (self.total_delivered / self.total_sent) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_sent': self.total_sent,
            'total_delivered': self.total_delivered,
            'total_failed': self.total_failed,
            'by_channel': self.by_channel,
            'by_severity': self.by_severity,
            'average_delivery_time_ms': self.average_delivery_time_ms,
            'max_delivery_time_ms': self.max_delivery_time_ms,
            'error_rate': self.error_rate,
            'common_errors': self.common_errors,
            'success_rate': self.success_rate(),
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None
        }


@dataclass
class RateLimitBucket:
    """Rate limiting bucket for tracking usage."""
    window_start: datetime
    window_duration: timedelta
    max_count: int
    current_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if rate limit window has expired."""
        return datetime.now() > (self.window_start + self.window_duration)
    
    def can_proceed(self) -> bool:
        """Check if request can proceed without exceeding rate limit."""
        if self.is_expired():
            return True
        return self.current_count < self.max_count
    
    def increment(self) -> bool:
        """Increment counter if within rate limit."""
        if self.is_expired():
            # Reset window
            self.window_start = datetime.now()
            self.current_count = 1
            return True
        
        if self.current_count < self.max_count:
            self.current_count += 1
            return True
        
        return False
    
    def reset(self):
        """Reset the rate limit bucket."""
        self.window_start = datetime.now()
        self.current_count = 0
    
    def time_until_reset(self) -> int:
        """Get seconds until rate limit resets."""
        if self.is_expired():
            return 0
        
        reset_time = self.window_start + self.window_duration
        return int((reset_time - datetime.now()).total_seconds())


class NotificationPriority:
    """Helper class for notification priority handling."""
    
    PRIORITY_ORDER = [
        DeliveryPriority.URGENT,
        DeliveryPriority.HIGH,
        DeliveryPriority.NORMAL,
        DeliveryPriority.LOW
    ]
    
    @classmethod
    def compare(cls, p1: DeliveryPriority, p2: DeliveryPriority) -> int:
        """Compare two priorities. Returns -1 if p1 < p2, 0 if equal, 1 if p1 > p2."""
        idx1 = cls.PRIORITY_ORDER.index(p1)
        idx2 = cls.PRIORITY_ORDER.index(p2)
        
        if idx1 < idx2:
            return 1  # p1 has higher priority
        elif idx1 > idx2:
            return -1  # p1 has lower priority
        else:
            return 0  # equal priority
    
    @classmethod
    def is_higher(cls, p1: DeliveryPriority, p2: DeliveryPriority) -> bool:
        """Check if p1 has higher priority than p2."""
        return cls.compare(p1, p2) > 0