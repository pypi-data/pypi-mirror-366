"""
Security module for monitoring dashboard.

This module provides:
- API key management and authentication
- Role-based access control
- Security audit logging
- Token validation and expiration
- Rate limiting and security policies
"""

from .api_key_manager import APIKeyManager, get_api_key_manager
from .api_key_models import APIKey, APIKeyPermission, APIKeyScope, APIKeyStatus
from .security_audit import SecurityAuditor, get_security_auditor
from .api_key_ui import APIKeyManagementUI

__all__ = [
    # Core API key management
    'APIKeyManager', 'get_api_key_manager',
    
    # Models and enums
    'APIKey', 'APIKeyPermission', 'APIKeyScope', 'APIKeyStatus',
    
    # Security auditing
    'SecurityAuditor', 'get_security_auditor',
    
    # User interface
    'APIKeyManagementUI'
]

__version__ = '1.0.0'