"""
Audit logging module for comprehensive system activity tracking.

This module provides:
- Comprehensive audit trail logging
- Activity monitoring and analysis
- Compliance reporting
- Change tracking integration
- Real-time audit event streaming
- Advanced filtering and search
"""

from .audit_logger import AuditLogger, get_audit_logger
from .audit_models import AuditEvent, AuditEventType, AuditEventCategory, AuditEventSeverity
from .audit_analyzer import AuditAnalyzer, get_audit_analyzer
from .audit_ui import AuditLoggingUI

__all__ = [
    # Core audit logging
    'AuditLogger', 'get_audit_logger',
    
    # Models and enums
    'AuditEvent', 'AuditEventType', 'AuditEventCategory', 'AuditEventSeverity',
    
    # Analysis and reporting
    'AuditAnalyzer', 'get_audit_analyzer',
    
    # User interface
    'AuditLoggingUI'
]

__version__ = '1.0.0'