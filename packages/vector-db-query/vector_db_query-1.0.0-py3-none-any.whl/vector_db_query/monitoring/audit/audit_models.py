"""
Audit event models and data structures for comprehensive activity tracking.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import json


class AuditEventType(Enum):
    """Types of audit events."""
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SYSTEM_RESTART = "system_restart"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACTION = "user_action"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    
    # API operations
    API_REQUEST = "api_request"
    API_KEY_CREATE = "api_key_create"
    API_KEY_UPDATE = "api_key_update"
    API_KEY_REVOKE = "api_key_revoke"
    API_KEY_USE = "api_key_use"
    
    # Data operations
    DATA_CREATE = "data_create"
    DATA_READ = "data_read"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    
    # Service operations
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"
    SERVICE_RESTART = "service_restart"
    SERVICE_CONFIG = "service_config"
    SERVICE_DEPLOY = "service_deploy"
    
    # Security events
    SECURITY_LOGIN_FAIL = "security_login_fail"
    SECURITY_ACCESS_DENIED = "security_access_denied"
    SECURITY_PERMISSION_CHANGE = "security_permission_change"
    SECURITY_POLICY_CHANGE = "security_policy_change"
    SECURITY_BREACH_ATTEMPT = "security_breach_attempt"
    
    # Dashboard events
    DASHBOARD_VIEW = "dashboard_view"
    DASHBOARD_CONFIG = "dashboard_config"
    WIDGET_CREATE = "widget_create"
    WIDGET_UPDATE = "widget_update"
    WIDGET_DELETE = "widget_delete"
    LAYOUT_CREATE = "layout_create"
    LAYOUT_UPDATE = "layout_update"
    LAYOUT_DELETE = "layout_delete"
    
    # Export events
    EXPORT_REQUEST = "export_request"
    EXPORT_COMPLETE = "export_complete"
    EXPORT_FAIL = "export_fail"
    EXPORT_DOWNLOAD = "export_download"
    
    # Monitoring events
    METRIC_COLLECTION = "metric_collection"
    ALERT_TRIGGER = "alert_trigger"
    ALERT_RESOLVE = "alert_resolve"
    NOTIFICATION_SEND = "notification_send"
    
    # Connection events
    CONNECTION_ESTABLISH = "connection_establish"
    CONNECTION_CLOSE = "connection_close"
    CONNECTION_FAIL = "connection_fail"
    CONNECTION_TEST = "connection_test"
    
    # Queue events
    QUEUE_PAUSE = "queue_pause"
    QUEUE_RESUME = "queue_resume"
    QUEUE_CLEAR = "queue_clear"
    JOB_SUBMIT = "job_submit"
    JOB_COMPLETE = "job_complete"
    JOB_FAIL = "job_fail"
    
    # Maintenance events
    BACKUP_START = "backup_start"
    BACKUP_COMPLETE = "backup_complete"
    BACKUP_FAIL = "backup_fail"
    CLEANUP_START = "cleanup_start"
    CLEANUP_COMPLETE = "cleanup_complete"
    
    # Compliance events
    COMPLIANCE_CHECK = "compliance_check"
    AUDIT_EXPORT = "audit_export"
    RETENTION_POLICY = "retention_policy"


class AuditEventCategory(Enum):
    """Categories for grouping audit events."""
    SYSTEM = "system"
    SECURITY = "security"
    USER = "user"
    DATA = "data"
    API = "api"
    DASHBOARD = "dashboard"
    EXPORT = "export"
    MONITORING = "monitoring"
    CONNECTION = "connection"
    QUEUE = "queue"
    MAINTENANCE = "maintenance"
    COMPLIANCE = "compliance"


class AuditEventSeverity(Enum):
    """Severity levels for audit events."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEventContext:
    """Context information for audit events."""
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    transaction_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    trace_id: Optional[str] = None
    
    # User context
    user_id: Optional[str] = None
    username: Optional[str] = None
    user_email: Optional[str] = None
    user_roles: List[str] = field(default_factory=list)
    
    # Request context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    origin: Optional[str] = None
    
    # Application context
    component: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None
    api_version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'session_id': self.session_id,
            'request_id': self.request_id,
            'correlation_id': self.correlation_id,
            'transaction_id': self.transaction_id,
            'parent_event_id': self.parent_event_id,
            'trace_id': self.trace_id,
            'user_id': self.user_id,
            'username': self.username,
            'user_email': self.user_email,
            'user_roles': self.user_roles,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referer': self.referer,
            'origin': self.origin,
            'component': self.component,
            'module': self.module,
            'function': self.function,
            'api_version': self.api_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEventContext':
        """Create from dictionary."""
        return cls(
            session_id=data.get('session_id'),
            request_id=data.get('request_id'),
            correlation_id=data.get('correlation_id'),
            transaction_id=data.get('transaction_id'),
            parent_event_id=data.get('parent_event_id'),
            trace_id=data.get('trace_id'),
            user_id=data.get('user_id'),
            username=data.get('username'),
            user_email=data.get('user_email'),
            user_roles=data.get('user_roles', []),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            referer=data.get('referer'),
            origin=data.get('origin'),
            component=data.get('component'),
            module=data.get('module'),
            function=data.get('function'),
            api_version=data.get('api_version')
        )


@dataclass
class AuditEvent:
    """Comprehensive audit event for activity tracking."""
    
    # Core identification
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: AuditEventType = AuditEventType.USER_ACTION
    category: AuditEventCategory = AuditEventCategory.USER
    severity: AuditEventSeverity = AuditEventSeverity.INFO
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: Optional[int] = None
    
    # Event details
    title: str = ""
    description: str = ""
    message: str = ""
    
    # Context information
    context: AuditEventContext = field(default_factory=AuditEventContext)
    
    # Target information
    target_type: Optional[str] = None  # e.g., "api_key", "user", "layout"
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    
    # Operation details
    operation: Optional[str] = None  # e.g., "create", "update", "delete"
    resource: Optional[str] = None   # e.g., "/api/v1/users", "dashboard.layout"
    method: Optional[str] = None     # e.g., "POST", "GET", "PUT", "DELETE"
    
    # Request/Response info
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    # Change tracking
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    
    # Metadata and tags
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Compliance and retention
    retention_days: Optional[int] = None
    compliance_flags: List[str] = field(default_factory=list)
    sensitive_data: bool = False
    
    # System information
    hostname: Optional[str] = None
    process_id: Optional[int] = None
    thread_id: Optional[str] = None
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the event."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the event."""
        self.metadata[key] = value
    
    def add_compliance_flag(self, flag: str) -> None:
        """Add a compliance flag."""
        if flag not in self.compliance_flags:
            self.compliance_flags.append(flag)
    
    def set_changes(self, old_values: Dict[str, Any], new_values: Dict[str, Any]) -> None:
        """Set change tracking information."""
        self.old_values = old_values
        self.new_values = new_values
        
        # Calculate changes
        changes = {}
        all_keys = set(old_values.keys()) | set(new_values.keys())
        
        for key in all_keys:
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            
            if old_val != new_val:
                changes[key] = {
                    'old': old_val,
                    'new': new_val
                }
        
        self.changes = changes
    
    def set_error(self, error_code: str, error_message: str, status_code: int = None) -> None:
        """Set error information."""
        self.error_code = error_code
        self.error_message = error_message
        self.status_code = status_code or 500
        
        # Increase severity for errors
        if self.severity == AuditEventSeverity.INFO:
            self.severity = AuditEventSeverity.MEDIUM
    
    def set_success(self, status_code: int = 200, response_data: Dict[str, Any] = None) -> None:
        """Set success information."""
        self.status_code = status_code
        self.response_data = response_data
        self.error_code = None
        self.error_message = None
    
    def is_successful(self) -> bool:
        """Check if the event represents a successful operation."""
        if self.status_code is not None:
            return 200 <= self.status_code < 400
        return self.error_code is None
    
    def get_duration_seconds(self) -> Optional[float]:
        """Get duration in seconds."""
        return self.duration_ms / 1000.0 if self.duration_ms is not None else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'category': self.category.value,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'duration_ms': self.duration_ms,
            'title': self.title,
            'description': self.description,
            'message': self.message,
            'context': self.context.to_dict(),
            'target_type': self.target_type,
            'target_id': self.target_id,
            'target_name': self.target_name,
            'operation': self.operation,
            'resource': self.resource,
            'method': self.method,
            'request_data': self.request_data,
            'response_data': self.response_data,
            'status_code': self.status_code,
            'error_code': self.error_code,
            'error_message': self.error_message,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'changes': self.changes,
            'tags': self.tags,
            'metadata': self.metadata,
            'retention_days': self.retention_days,
            'compliance_flags': self.compliance_flags,
            'sensitive_data': self.sensitive_data,
            'hostname': self.hostname,
            'process_id': self.process_id,
            'thread_id': self.thread_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Create AuditEvent from dictionary."""
        event = cls(
            event_id=data.get('event_id', str(uuid.uuid4())),
            event_type=AuditEventType(data.get('event_type', 'user_action')),
            category=AuditEventCategory(data.get('category', 'user')),
            severity=AuditEventSeverity(data.get('severity', 'info')),
            duration_ms=data.get('duration_ms'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            message=data.get('message', ''),
            target_type=data.get('target_type'),
            target_id=data.get('target_id'),
            target_name=data.get('target_name'),
            operation=data.get('operation'),
            resource=data.get('resource'),
            method=data.get('method'),
            request_data=data.get('request_data'),
            response_data=data.get('response_data'),
            status_code=data.get('status_code'),
            error_code=data.get('error_code'),
            error_message=data.get('error_message'),
            old_values=data.get('old_values'),
            new_values=data.get('new_values'),
            changes=data.get('changes'),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            retention_days=data.get('retention_days'),
            compliance_flags=data.get('compliance_flags', []),
            sensitive_data=data.get('sensitive_data', False),
            hostname=data.get('hostname'),
            process_id=data.get('process_id'),
            thread_id=data.get('thread_id')
        )
        
        # Parse timestamp
        if 'timestamp' in data:
            try:
                event.timestamp = datetime.fromisoformat(data['timestamp'])
            except:
                pass
        
        # Parse context
        if 'context' in data:
            event.context = AuditEventContext.from_dict(data['context'])
        
        return event


# Predefined event templates for common operations
EVENT_TEMPLATES = {
    'user_login': {
        'event_type': AuditEventType.USER_LOGIN,
        'category': AuditEventCategory.SECURITY,
        'severity': AuditEventSeverity.INFO,
        'title': 'User Login',
        'description': 'User successfully logged into the system'
    },
    
    'user_login_fail': {
        'event_type': AuditEventType.SECURITY_LOGIN_FAIL,
        'category': AuditEventCategory.SECURITY,
        'severity': AuditEventSeverity.MEDIUM,
        'title': 'Login Failed',
        'description': 'User login attempt failed'
    },
    
    'api_key_create': {
        'event_type': AuditEventType.API_KEY_CREATE,
        'category': AuditEventCategory.SECURITY,
        'severity': AuditEventSeverity.MEDIUM,
        'title': 'API Key Created',
        'description': 'New API key was created'
    },
    
    'data_export': {
        'event_type': AuditEventType.DATA_EXPORT,
        'category': AuditEventCategory.DATA,
        'severity': AuditEventSeverity.MEDIUM,
        'title': 'Data Export',
        'description': 'Data was exported from the system'
    },
    
    'config_change': {
        'event_type': AuditEventType.SYSTEM_CONFIG_CHANGE,
        'category': AuditEventCategory.SYSTEM,
        'severity': AuditEventSeverity.HIGH,
        'title': 'Configuration Changed',
        'description': 'System configuration was modified'
    },
    
    'permission_change': {
        'event_type': AuditEventType.SECURITY_PERMISSION_CHANGE,
        'category': AuditEventCategory.SECURITY,
        'severity': AuditEventSeverity.HIGH,
        'title': 'Permissions Changed',
        'description': 'User or system permissions were modified'
    }
}


def create_audit_event_from_template(template_name: str, **kwargs) -> AuditEvent:
    """Create an audit event from a predefined template."""
    if template_name not in EVENT_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")
    
    template = EVENT_TEMPLATES[template_name].copy()
    template.update(kwargs)
    
    return AuditEvent(
        event_type=template.get('event_type'),
        category=template.get('category'),
        severity=template.get('severity'),
        title=template.get('title'),
        description=template.get('description'),
        message=template.get('message', ''),
        **{k: v for k, v in template.items() if k not in ['event_type', 'category', 'severity', 'title', 'description', 'message']}
    )