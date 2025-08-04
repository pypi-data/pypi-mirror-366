"""
API Key models and data structures for security management.
"""

import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from enum import Enum
import secrets
import hashlib
import json


class APIKeyStatus(Enum):
    """API key status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class APIKeyScope(Enum):
    """API key scope enumeration defining access levels."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    SYSTEM = "system"
    EXPORT = "export"
    MONITORING = "monitoring"
    METRICS = "metrics"
    CONFIGURATION = "configuration"


class APIKeyPermission(Enum):
    """Specific permissions for API keys."""
    # System monitoring
    VIEW_SYSTEM_METRICS = "view_system_metrics"
    VIEW_PROCESS_INFO = "view_process_info"
    VIEW_QUEUE_STATUS = "view_queue_status"
    
    # Process control
    START_SERVICES = "start_services"
    STOP_SERVICES = "stop_services"
    RESTART_SERVICES = "restart_services"
    PAUSE_QUEUE = "pause_queue"
    RESUME_QUEUE = "resume_queue"
    
    # Configuration
    VIEW_CONFIG = "view_config"
    MODIFY_CONFIG = "modify_config"
    VIEW_LAYOUTS = "view_layouts"
    MODIFY_LAYOUTS = "modify_layouts"
    
    # Export and reporting
    EXPORT_DATA = "export_data"
    VIEW_REPORTS = "view_reports"
    GENERATE_REPORTS = "generate_reports"
    
    # Connection management
    VIEW_CONNECTIONS = "view_connections"
    MODIFY_CONNECTIONS = "modify_connections"
    TEST_CONNECTIONS = "test_connections"
    
    # User and security
    VIEW_USERS = "view_users"
    MANAGE_USERS = "manage_users"
    VIEW_API_KEYS = "view_api_keys"
    MANAGE_API_KEYS = "manage_api_keys"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    
    # Advanced features
    SYSTEM_ADMIN = "system_admin"
    DEBUG_ACCESS = "debug_access"


@dataclass
class APIKeyUsageStats:
    """Statistics for API key usage."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    last_used_at: Optional[datetime] = None
    requests_by_endpoint: Dict[str, int] = field(default_factory=dict)
    requests_by_hour: Dict[str, int] = field(default_factory=dict)  # ISO hour strings
    bandwidth_used: int = 0  # bytes
    
    def add_request(self, endpoint: str, success: bool, bytes_transferred: int = 0):
        """Add a request to the usage statistics."""
        self.total_requests += 1
        self.last_used_at = datetime.now()
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Track by endpoint
        self.requests_by_endpoint[endpoint] = self.requests_by_endpoint.get(endpoint, 0) + 1
        
        # Track by hour
        hour_key = datetime.now().strftime('%Y-%m-%d-%H')
        self.requests_by_hour[hour_key] = self.requests_by_hour.get(hour_key, 0) + 1
        
        # Track bandwidth
        self.bandwidth_used += bytes_transferred
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_requests_last_24h(self) -> int:
        """Get number of requests in the last 24 hours."""
        now = datetime.now()
        last_24h = []
        
        for i in range(24):
            hour = (now - timedelta(hours=i)).strftime('%Y-%m-%d-%H')
            last_24h.append(hour)
        
        return sum(self.requests_by_hour.get(hour, 0) for hour in last_24h)


@dataclass
class APIKeyRateLimit:
    """Rate limiting configuration for API keys."""
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    concurrent_requests: int = 10
    bandwidth_limit_mb: int = 100  # MB per hour
    
    def is_within_limits(self, usage_stats: APIKeyUsageStats) -> tuple[bool, str]:
        """Check if usage is within rate limits."""
        now = datetime.now()
        
        # Check requests per minute (last minute)
        current_minute = now.strftime('%Y-%m-%d-%H-%M')
        minute_requests = sum(
            usage_stats.requests_by_hour.get(
                (now - timedelta(minutes=i)).strftime('%Y-%m-%d-%H'), 0
            ) for i in range(1)
        ) // 60  # Rough approximation
        
        if minute_requests > self.requests_per_minute:
            return False, f"Rate limit exceeded: {minute_requests}/{self.requests_per_minute} requests per minute"
        
        # Check requests per hour
        hour_requests = usage_stats.get_requests_last_24h() // 24  # Average per hour
        if hour_requests > self.requests_per_hour:
            return False, f"Rate limit exceeded: {hour_requests}/{self.requests_per_hour} requests per hour"
        
        # Check bandwidth
        bandwidth_mb = usage_stats.bandwidth_used / (1024 * 1024)
        if bandwidth_mb > self.bandwidth_limit_mb:
            return False, f"Bandwidth limit exceeded: {bandwidth_mb:.1f}/{self.bandwidth_limit_mb} MB"
        
        return True, "Within limits"


@dataclass
class APIKey:
    """API Key model for authentication and authorization."""
    
    # Identity
    key_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Authentication
    key_hash: str = ""  # Hashed version of the actual key
    key_prefix: str = ""  # First 8 characters for display
    
    # Authorization
    scopes: Set[APIKeyScope] = field(default_factory=set)
    permissions: Set[APIKeyPermission] = field(default_factory=set)
    allowed_ips: List[str] = field(default_factory=list)  # IP whitelist
    allowed_origins: List[str] = field(default_factory=list)  # CORS origins
    
    # Status and lifecycle
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[str] = None
    revoked_reason: Optional[str] = None
    
    # Owner and metadata
    created_by: str = "system"
    owner_email: Optional[str] = None
    owner_name: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Rate limiting and usage
    rate_limit: APIKeyRateLimit = field(default_factory=APIKeyRateLimit)
    usage_stats: APIKeyUsageStats = field(default_factory=APIKeyUsageStats)
    
    # Security settings
    require_https: bool = True
    enable_audit_logging: bool = True
    max_concurrent_sessions: int = 5
    
    @classmethod
    def generate_key(cls) -> str:
        """Generate a secure API key."""
        # Format: ak_<environment>_<32_chars>
        # where environment could be 'prod', 'dev', 'test'
        environment = "prod"  # Could be configurable
        random_part = secrets.token_urlsafe(24)  # 32 chars base64url
        return f"ak_{environment}_{random_part}"
    
    @classmethod
    def hash_key(cls, api_key: str) -> str:
        """Create a secure hash of the API key."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def set_key(self, api_key: str) -> None:
        """Set the API key and compute hash and prefix."""
        self.key_hash = self.hash_key(api_key)
        self.key_prefix = api_key[:8] + "..."
    
    def verify_key(self, api_key: str) -> bool:
        """Verify if the provided key matches this API key."""
        return self.key_hash == self.hash_key(api_key)
    
    def is_active(self) -> bool:
        """Check if the API key is currently active."""
        if self.status != APIKeyStatus.ACTIVE:
            return False
        
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        
        return True
    
    def is_expired(self) -> bool:
        """Check if the API key has expired."""
        return self.expires_at and datetime.now() > self.expires_at
    
    def has_permission(self, permission: APIKeyPermission) -> bool:
        """Check if the key has a specific permission."""
        return permission in self.permissions
    
    def has_scope(self, scope: APIKeyScope) -> bool:
        """Check if the key has a specific scope."""
        return scope in self.scopes
    
    def can_access_ip(self, ip_address: str) -> bool:
        """Check if the key can be used from the given IP address."""
        if not self.allowed_ips:
            return True  # No IP restrictions
        return ip_address in self.allowed_ips
    
    def can_access_origin(self, origin: str) -> bool:
        """Check if the key can be used from the given origin."""
        if not self.allowed_origins:
            return True  # No origin restrictions
        return origin in self.allowed_origins
    
    def revoke(self, revoked_by: str, reason: str = "Manual revocation") -> None:
        """Revoke the API key."""
        self.status = APIKeyStatus.REVOKED
        self.revoked_at = datetime.now()
        self.revoked_by = revoked_by
        self.revoked_reason = reason
    
    def suspend(self, reason: str = "Suspended by admin") -> None:
        """Suspend the API key."""
        self.status = APIKeyStatus.SUSPENDED
        self.revoked_reason = reason
    
    def activate(self) -> None:
        """Activate the API key."""
        if self.status in [APIKeyStatus.INACTIVE, APIKeyStatus.SUSPENDED]:
            self.status = APIKeyStatus.ACTIVE
            self.revoked_reason = None
    
    def extend_expiry(self, days: int = 90) -> None:
        """Extend the expiry date of the API key."""
        if self.expires_at:
            self.expires_at = max(self.expires_at, datetime.now()) + timedelta(days=days)
        else:
            self.expires_at = datetime.now() + timedelta(days=days)
    
    def add_permission(self, permission: APIKeyPermission) -> None:
        """Add a permission to the API key."""
        self.permissions.add(permission)
    
    def remove_permission(self, permission: APIKeyPermission) -> None:
        """Remove a permission from the API key."""
        self.permissions.discard(permission)
    
    def add_scope(self, scope: APIKeyScope) -> None:
        """Add a scope to the API key."""
        self.scopes.add(scope)
    
    def remove_scope(self, scope: APIKeyScope) -> None:
        """Remove a scope from the API key."""
        self.scopes.discard(scope)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'key_id': self.key_id,
            'name': self.name,
            'description': self.description,
            'key_prefix': self.key_prefix,
            'scopes': [s.value for s in self.scopes],
            'permissions': [p.value for p in self.permissions],
            'allowed_ips': self.allowed_ips,
            'allowed_origins': self.allowed_origins,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None,
            'revoked_by': self.revoked_by,
            'revoked_reason': self.revoked_reason,
            'created_by': self.created_by,
            'owner_email': self.owner_email,
            'owner_name': self.owner_name,
            'tags': self.tags,
            'rate_limit': {
                'requests_per_minute': self.rate_limit.requests_per_minute,
                'requests_per_hour': self.rate_limit.requests_per_hour,
                'requests_per_day': self.rate_limit.requests_per_day,
                'concurrent_requests': self.rate_limit.concurrent_requests,
                'bandwidth_limit_mb': self.rate_limit.bandwidth_limit_mb
            },
            'usage_stats': {
                'total_requests': self.usage_stats.total_requests,
                'successful_requests': self.usage_stats.successful_requests,
                'failed_requests': self.usage_stats.failed_requests,
                'rate_limited_requests': self.usage_stats.rate_limited_requests,
                'last_used_at': self.usage_stats.last_used_at.isoformat() if self.usage_stats.last_used_at else None,
                'requests_by_endpoint': self.usage_stats.requests_by_endpoint,
                'bandwidth_used': self.usage_stats.bandwidth_used,
                'success_rate': self.usage_stats.get_success_rate(),
                'requests_last_24h': self.usage_stats.get_requests_last_24h()
            },
            'require_https': self.require_https,
            'enable_audit_logging': self.enable_audit_logging,
            'max_concurrent_sessions': self.max_concurrent_sessions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIKey':
        """Create APIKey from dictionary."""
        # Create basic instance
        api_key = cls(
            key_id=data.get('key_id', str(uuid.uuid4())),
            name=data.get('name', ''),
            description=data.get('description', ''),
            key_hash=data.get('key_hash', ''),
            key_prefix=data.get('key_prefix', ''),
            status=APIKeyStatus(data.get('status', 'active')),
            created_by=data.get('created_by', 'system'),
            owner_email=data.get('owner_email'),
            owner_name=data.get('owner_name'),
            tags=data.get('tags', {}),
            allowed_ips=data.get('allowed_ips', []),
            allowed_origins=data.get('allowed_origins', []),
            require_https=data.get('require_https', True),
            enable_audit_logging=data.get('enable_audit_logging', True),
            max_concurrent_sessions=data.get('max_concurrent_sessions', 5)
        )
        
        # Parse datetime fields
        if 'created_at' in data:
            api_key.created_at = datetime.fromisoformat(data['created_at'])
        if 'expires_at' in data and data['expires_at']:
            api_key.expires_at = datetime.fromisoformat(data['expires_at'])
        if 'last_used_at' in data and data['last_used_at']:
            api_key.last_used_at = datetime.fromisoformat(data['last_used_at'])
        if 'revoked_at' in data and data['revoked_at']:
            api_key.revoked_at = datetime.fromisoformat(data['revoked_at'])
        
        # Parse revocation fields
        api_key.revoked_by = data.get('revoked_by')
        api_key.revoked_reason = data.get('revoked_reason')
        
        # Parse scopes and permissions
        api_key.scopes = {APIKeyScope(s) for s in data.get('scopes', [])}
        api_key.permissions = {APIKeyPermission(p) for p in data.get('permissions', [])}
        
        # Parse rate limit
        if 'rate_limit' in data:
            rl_data = data['rate_limit']
            api_key.rate_limit = APIKeyRateLimit(
                requests_per_minute=rl_data.get('requests_per_minute', 100),
                requests_per_hour=rl_data.get('requests_per_hour', 1000),
                requests_per_day=rl_data.get('requests_per_day', 10000),
                concurrent_requests=rl_data.get('concurrent_requests', 10),
                bandwidth_limit_mb=rl_data.get('bandwidth_limit_mb', 100)
            )
        
        # Parse usage stats
        if 'usage_stats' in data:
            us_data = data['usage_stats']
            api_key.usage_stats = APIKeyUsageStats(
                total_requests=us_data.get('total_requests', 0),
                successful_requests=us_data.get('successful_requests', 0),
                failed_requests=us_data.get('failed_requests', 0),
                rate_limited_requests=us_data.get('rate_limited_requests', 0),
                requests_by_endpoint=us_data.get('requests_by_endpoint', {}),
                requests_by_hour=us_data.get('requests_by_hour', {}),
                bandwidth_used=us_data.get('bandwidth_used', 0)
            )
            
            if us_data.get('last_used_at'):
                api_key.usage_stats.last_used_at = datetime.fromisoformat(us_data['last_used_at'])
        
        return api_key


# Predefined permission sets for common roles
PERMISSION_SETS = {
    'read_only': {
        APIKeyPermission.VIEW_SYSTEM_METRICS,
        APIKeyPermission.VIEW_PROCESS_INFO,
        APIKeyPermission.VIEW_QUEUE_STATUS,
        APIKeyPermission.VIEW_CONFIG,
        APIKeyPermission.VIEW_LAYOUTS,
        APIKeyPermission.VIEW_REPORTS,
        APIKeyPermission.VIEW_CONNECTIONS
    },
    
    'operator': {
        APIKeyPermission.VIEW_SYSTEM_METRICS,
        APIKeyPermission.VIEW_PROCESS_INFO,
        APIKeyPermission.VIEW_QUEUE_STATUS,
        APIKeyPermission.START_SERVICES,
        APIKeyPermission.STOP_SERVICES,
        APIKeyPermission.RESTART_SERVICES,
        APIKeyPermission.PAUSE_QUEUE,
        APIKeyPermission.RESUME_QUEUE,
        APIKeyPermission.VIEW_CONFIG,
        APIKeyPermission.VIEW_LAYOUTS,
        APIKeyPermission.TEST_CONNECTIONS
    },
    
    'developer': {
        APIKeyPermission.VIEW_SYSTEM_METRICS,
        APIKeyPermission.VIEW_PROCESS_INFO,
        APIKeyPermission.VIEW_QUEUE_STATUS,
        APIKeyPermission.VIEW_CONFIG,
        APIKeyPermission.MODIFY_CONFIG,
        APIKeyPermission.VIEW_LAYOUTS,
        APIKeyPermission.MODIFY_LAYOUTS,
        APIKeyPermission.EXPORT_DATA,
        APIKeyPermission.VIEW_REPORTS,
        APIKeyPermission.GENERATE_REPORTS,
        APIKeyPermission.VIEW_CONNECTIONS,
        APIKeyPermission.MODIFY_CONNECTIONS,
        APIKeyPermission.TEST_CONNECTIONS
    },
    
    'admin': {
        APIKeyPermission.VIEW_SYSTEM_METRICS,
        APIKeyPermission.VIEW_PROCESS_INFO,
        APIKeyPermission.VIEW_QUEUE_STATUS,
        APIKeyPermission.START_SERVICES,
        APIKeyPermission.STOP_SERVICES,
        APIKeyPermission.RESTART_SERVICES,
        APIKeyPermission.PAUSE_QUEUE,
        APIKeyPermission.RESUME_QUEUE,
        APIKeyPermission.VIEW_CONFIG,
        APIKeyPermission.MODIFY_CONFIG,
        APIKeyPermission.VIEW_LAYOUTS,
        APIKeyPermission.MODIFY_LAYOUTS,
        APIKeyPermission.EXPORT_DATA,
        APIKeyPermission.VIEW_REPORTS,
        APIKeyPermission.GENERATE_REPORTS,
        APIKeyPermission.VIEW_CONNECTIONS,
        APIKeyPermission.MODIFY_CONNECTIONS,
        APIKeyPermission.TEST_CONNECTIONS,
        APIKeyPermission.VIEW_USERS,
        APIKeyPermission.MANAGE_USERS,
        APIKeyPermission.VIEW_API_KEYS,
        APIKeyPermission.MANAGE_API_KEYS,
        APIKeyPermission.VIEW_AUDIT_LOGS,
        APIKeyPermission.SYSTEM_ADMIN
    }
}