"""
Data models for connection monitoring.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid


class ConnectionType(Enum):
    """Types of connections to monitor."""
    QDRANT = "qdrant"
    MCP_SERVER = "mcp_server"
    DATABASE = "database"
    SERVICE = "service"
    HTTP_ENDPOINT = "http_endpoint"
    WEBSOCKET = "websocket"
    REDIS = "redis"
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"
    CUSTOM = "custom"


class ConnectionStatus(Enum):
    """Connection status states."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    TIMEOUT = "timeout"
    UNAUTHORIZED = "unauthorized"
    MAINTENANCE = "maintenance"


class ConnectionHealth(Enum):
    """Connection health levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ConnectionMetrics:
    """Metrics for a connection."""
    latency_ms: float = 0.0
    throughput_mbps: float = 0.0
    error_rate: float = 0.0
    uptime_seconds: float = 0.0
    request_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    
    # Performance metrics
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    
    # Resource metrics
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    connection_pool_size: Optional[int] = None
    active_connections: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'latency_ms': self.latency_ms,
            'throughput_mbps': self.throughput_mbps,
            'error_rate': self.error_rate,
            'uptime_seconds': self.uptime_seconds,
            'request_count': self.request_count,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None,
            'performance': {
                'avg_response_time_ms': self.avg_response_time_ms,
                'p95_response_time_ms': self.p95_response_time_ms,
                'p99_response_time_ms': self.p99_response_time_ms
            },
            'resources': {
                'cpu_usage_percent': self.cpu_usage_percent,
                'memory_usage_mb': self.memory_usage_mb,
                'connection_pool_size': self.connection_pool_size,
                'active_connections': self.active_connections
            }
        }


@dataclass
class Connection:
    """Represents a monitored connection."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: ConnectionType = ConnectionType.CUSTOM
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    health: ConnectionHealth = ConnectionHealth.UNKNOWN
    
    # Connection details
    host: Optional[str] = None
    port: Optional[int] = None
    url: Optional[str] = None
    protocol: Optional[str] = None
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Monitoring settings
    check_interval_seconds: int = 30
    timeout_seconds: int = 10
    retry_count: int = 3
    retry_delay_seconds: int = 5
    
    # Status tracking
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_check_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    
    # Metrics
    metrics: ConnectionMetrics = field(default_factory=ConnectionMetrics)
    
    # Event tracking
    consecutive_failures: int = 0
    total_failures: int = 0
    total_checks: int = 0
    
    # Alerts
    alert_on_failure: bool = True
    alert_threshold: int = 3  # Alert after N consecutive failures
    alerted: bool = False
    
    def update_status(self, status: ConnectionStatus, health: Optional[ConnectionHealth] = None):
        """Update connection status."""
        self.status = status
        if health:
            self.health = health
        self.updated_at = datetime.now()
    
    def record_success(self):
        """Record successful connection check."""
        self.last_success_time = datetime.now()
        self.consecutive_failures = 0
        self.alerted = False
        self.total_checks += 1
    
    def record_failure(self, error: Optional[str] = None):
        """Record failed connection check."""
        self.last_failure_time = datetime.now()
        self.consecutive_failures += 1
        self.total_failures += 1
        self.total_checks += 1
        
        if error:
            self.metrics.last_error = error
            self.metrics.last_error_time = datetime.now()
    
    def should_alert(self) -> bool:
        """Check if an alert should be triggered."""
        return (self.alert_on_failure and 
                self.consecutive_failures >= self.alert_threshold and 
                not self.alerted)
    
    def get_uptime_percentage(self) -> float:
        """Calculate uptime percentage."""
        if self.total_checks == 0:
            return 100.0
        
        success_count = self.total_checks - self.total_failures
        return (success_count / self.total_checks) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'status': self.status.value,
            'health': self.health.value,
            'connection': {
                'host': self.host,
                'port': self.port,
                'url': self.url,
                'protocol': self.protocol
            },
            'config': self.config,
            'tags': self.tags,
            'monitoring': {
                'check_interval_seconds': self.check_interval_seconds,
                'timeout_seconds': self.timeout_seconds,
                'retry_count': self.retry_count,
                'retry_delay_seconds': self.retry_delay_seconds
            },
            'timestamps': {
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
                'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
                'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None,
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None
            },
            'metrics': self.metrics.to_dict(),
            'statistics': {
                'consecutive_failures': self.consecutive_failures,
                'total_failures': self.total_failures,
                'total_checks': self.total_checks,
                'uptime_percentage': self.get_uptime_percentage()
            },
            'alerts': {
                'alert_on_failure': self.alert_on_failure,
                'alert_threshold': self.alert_threshold,
                'alerted': self.alerted
            }
        }


@dataclass
class ConnectionEvent:
    """Represents a connection event."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    connection_id: str = ""
    connection_name: str = ""
    event_type: str = ""  # connected, disconnected, error, health_change, etc.
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Event details
    old_status: Optional[ConnectionStatus] = None
    new_status: Optional[ConnectionStatus] = None
    old_health: Optional[ConnectionHealth] = None
    new_health: Optional[ConnectionHealth] = None
    
    # Additional data
    message: Optional[str] = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics at time of event
    metrics_snapshot: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'connection_id': self.connection_id,
            'connection_name': self.connection_name,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'status_change': {
                'old': self.old_status.value if self.old_status else None,
                'new': self.new_status.value if self.new_status else None
            },
            'health_change': {
                'old': self.old_health.value if self.old_health else None,
                'new': self.new_health.value if self.new_health else None
            },
            'message': self.message,
            'error': self.error,
            'details': self.details,
            'metrics_snapshot': self.metrics_snapshot
        }


@dataclass
class ConnectionCheck:
    """Represents a connection check result."""
    connection_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = False
    
    # Check details
    duration_ms: float = 0.0
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    
    # Error information
    error: Optional[str] = None
    error_type: Optional[str] = None
    
    # Additional data
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'connection_id': self.connection_id,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
            'duration_ms': self.duration_ms,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'error': self.error,
            'error_type': self.error_type,
            'details': self.details
        }