"""
Comprehensive audit logger for tracking all system activities.
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from threading import RLock
from pathlib import Path
import socket
import threading
from contextlib import contextmanager

from .audit_models import (
    AuditEvent, AuditEventType, AuditEventCategory, AuditEventSeverity,
    AuditEventContext, create_audit_event_from_template
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class AuditLogger:
    """
    Comprehensive audit logger for tracking all system activities.
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize audit logger."""
        self._lock = RLock()
        self.data_dir = data_dir or os.path.join(os.getcwd(), ".data", "monitoring")
        self.db_path = os.path.join(self.data_dir, "audit_log.db")
        self.change_tracker = get_change_tracker()
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Event listeners
        self._event_listeners: List[Callable[[AuditEvent], None]] = []
        
        # Retention policies
        self.default_retention_days = 365
        self.retention_policies = {
            AuditEventCategory.SECURITY: 2555,  # 7 years
            AuditEventCategory.COMPLIANCE: 2555,  # 7 years
            AuditEventCategory.DATA: 1095,  # 3 years
            AuditEventCategory.API: 365,   # 1 year
            AuditEventCategory.USER: 365,  # 1 year
            AuditEventCategory.SYSTEM: 180,  # 6 months
        }
        
        # Context tracking
        self._context_stack = threading.local()
        
        # System information
        self.hostname = socket.gethostname()
        self.process_id = os.getpid()
    
    def _init_database(self) -> None:
        """Initialize SQLite database for audit logs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Audit events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    duration_ms INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    message TEXT,
                    target_type TEXT,
                    target_id TEXT,
                    target_name TEXT,
                    operation TEXT,
                    resource TEXT,
                    method TEXT,
                    status_code INTEGER,
                    error_code TEXT,
                    error_message TEXT,
                    user_id TEXT,
                    username TEXT,
                    ip_address TEXT,
                    session_id TEXT,
                    request_id TEXT,
                    correlation_id TEXT,
                    hostname TEXT,
                    process_id INTEGER,
                    thread_id TEXT,
                    tags TEXT,
                    retention_days INTEGER,
                    compliance_flags TEXT,
                    sensitive_data BOOLEAN DEFAULT FALSE,
                    data_json TEXT NOT NULL
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_events (event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_category ON audit_events (category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_severity ON audit_events (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_events (user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_ip_address ON audit_events (ip_address)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_target ON audit_events (target_type, target_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_operation ON audit_events (operation)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_events (resource)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_correlation ON audit_events (correlation_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_events (session_id)')
            
            # Audit statistics table for performance
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    count INTEGER NOT NULL DEFAULT 1,
                    last_updated TEXT NOT NULL,
                    UNIQUE(date, category, event_type, severity)
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_stats_date ON audit_statistics (date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_stats_category ON audit_statistics (category)')
            
            conn.commit()
    
    def log_event(self, event: AuditEvent) -> None:
        """Log an audit event."""
        with self._lock:
            # Set system information
            event.hostname = self.hostname
            event.process_id = self.process_id
            event.thread_id = str(threading.get_ident())
            
            # Apply retention policy
            if event.retention_days is None:
                event.retention_days = self.retention_policies.get(
                    event.category, 
                    self.default_retention_days
                )
            
            # Set current context if available
            self._apply_current_context(event)
            
            # Save to database
            self._save_event(event)
            
            # Update statistics
            self._update_statistics(event)
            
            # Notify listeners
            for listener in self._event_listeners:
                try:
                    listener(event)
                except Exception as e:
                    # Don't let listener errors break audit logging
                    print(f"Audit listener error: {e}")
            
            # Log high-severity events to change tracker
            if event.severity in [AuditEventSeverity.HIGH, AuditEventSeverity.CRITICAL]:
                self.change_tracker.track_change(
                    change_type=ChangeType.CREATE,
                    category=ChangeCategory.AUDIT,
                    entity_id=event.event_id,
                    description=f"Audit: {event.title}",
                    metadata={
                        'event_type': event.event_type.value,
                        'severity': event.severity.value,
                        'user_id': event.context.user_id,
                        'ip_address': event.context.ip_address
                    }
                )
    
    def _save_event(self, event: AuditEvent) -> None:
        """Save event to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_events (
                    event_id, event_type, category, severity, timestamp,
                    duration_ms, title, description, message,
                    target_type, target_id, target_name, operation, resource, method,
                    status_code, error_code, error_message,
                    user_id, username, ip_address, session_id, request_id, correlation_id,
                    hostname, process_id, thread_id,
                    tags, retention_days, compliance_flags, sensitive_data,
                    data_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id,
                event.event_type.value,
                event.category.value,
                event.severity.value,
                event.timestamp.isoformat(),
                event.duration_ms,
                event.title,
                event.description,
                event.message,
                event.target_type,
                event.target_id,
                event.target_name,
                event.operation,
                event.resource,
                event.method,
                event.status_code,
                event.error_code,
                event.error_message,
                event.context.user_id,
                event.context.username,
                event.context.ip_address,
                event.context.session_id,
                event.context.request_id,
                event.context.correlation_id,
                event.hostname,
                event.process_id,
                event.thread_id,
                json.dumps(event.tags),
                event.retention_days,
                json.dumps(event.compliance_flags),
                event.sensitive_data,
                json.dumps(event.to_dict())
            ))
            
            conn.commit()
    
    def _update_statistics(self, event: AuditEvent) -> None:
        """Update audit statistics."""
        date_str = event.timestamp.date().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_statistics (
                    date, category, event_type, severity, count, last_updated
                ) VALUES (?, ?, ?, ?, 1, ?)
                ON CONFLICT(date, category, event_type, severity) 
                DO UPDATE SET 
                    count = count + 1,
                    last_updated = ?
            ''', (
                date_str,
                event.category.value,
                event.event_type.value,
                event.severity.value,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def _apply_current_context(self, event: AuditEvent) -> None:
        """Apply current context from context stack."""
        if hasattr(self._context_stack, 'contexts') and self._context_stack.contexts:
            current_context = self._context_stack.contexts[-1]
            
            # Merge contexts (event context takes precedence)
            for attr_name in ['session_id', 'request_id', 'correlation_id', 'user_id', 
                             'username', 'user_email', 'ip_address', 'user_agent']:
                if getattr(event.context, attr_name) is None:
                    setattr(event.context, attr_name, getattr(current_context, attr_name, None))
    
    @contextmanager
    def audit_context(self, context: AuditEventContext):
        """Context manager for setting audit context."""
        if not hasattr(self._context_stack, 'contexts'):
            self._context_stack.contexts = []
        
        self._context_stack.contexts.append(context)
        try:
            yield
        finally:
            self._context_stack.contexts.pop()
    
    def log_user_action(self, action: str, user_id: str = None, **kwargs) -> None:
        """Log a user action."""
        event = AuditEvent(
            event_type=AuditEventType.USER_ACTION,
            category=AuditEventCategory.USER,
            severity=AuditEventSeverity.INFO,
            title=f"User Action: {action}",
            operation=action,
            **kwargs
        )
        
        if user_id:
            event.context.user_id = user_id
        
        self.log_event(event)
    
    def log_api_request(self, method: str, resource: str, status_code: int, 
                       user_id: str = None, duration_ms: int = None, **kwargs) -> None:
        """Log an API request."""
        severity = AuditEventSeverity.INFO
        if status_code >= 400:
            severity = AuditEventSeverity.MEDIUM if status_code < 500 else AuditEventSeverity.HIGH
        
        event = AuditEvent(
            event_type=AuditEventType.API_REQUEST,
            category=AuditEventCategory.API,
            severity=severity,
            title=f"API Request: {method} {resource}",
            method=method,
            resource=resource,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
        
        if user_id:
            event.context.user_id = user_id
        
        self.log_event(event)
    
    def log_data_access(self, operation: str, target_type: str, target_id: str = None, 
                       user_id: str = None, **kwargs) -> None:
        """Log data access."""
        severity_map = {
            'read': AuditEventSeverity.LOW,
            'create': AuditEventSeverity.MEDIUM,
            'update': AuditEventSeverity.MEDIUM,
            'delete': AuditEventSeverity.HIGH,
            'export': AuditEventSeverity.HIGH
        }
        
        event = AuditEvent(
            event_type=getattr(AuditEventType, f"DATA_{operation.upper()}", AuditEventType.DATA_READ),
            category=AuditEventCategory.DATA,
            severity=severity_map.get(operation.lower(), AuditEventSeverity.MEDIUM),
            title=f"Data {operation.title()}: {target_type}",
            operation=operation,
            target_type=target_type,
            target_id=target_id,
            **kwargs
        )
        
        if user_id:
            event.context.user_id = user_id
        
        self.log_event(event)
    
    def log_security_event(self, event_type: AuditEventType, message: str, 
                          severity: AuditEventSeverity = AuditEventSeverity.MEDIUM,
                          **kwargs) -> None:
        """Log a security event."""
        event = AuditEvent(
            event_type=event_type,
            category=AuditEventCategory.SECURITY,
            severity=severity,
            title=f"Security Event: {event_type.value.replace('_', ' ').title()}",
            message=message,
            **kwargs
        )
        
        self.log_event(event)
    
    def log_system_event(self, event_type: AuditEventType, message: str,
                        severity: AuditEventSeverity = AuditEventSeverity.INFO,
                        **kwargs) -> None:
        """Log a system event."""
        event = AuditEvent(
            event_type=event_type,
            category=AuditEventCategory.SYSTEM,
            severity=severity,
            title=f"System Event: {event_type.value.replace('_', ' ').title()}",
            message=message,
            **kwargs
        )
        
        self.log_event(event)
    
    def log_from_template(self, template_name: str, **kwargs) -> None:
        """Log an event using a predefined template."""
        event = create_audit_event_from_template(template_name, **kwargs)
        self.log_event(event)
    
    def search_events(self,
                     start_date: datetime = None,
                     end_date: datetime = None,
                     event_types: List[AuditEventType] = None,
                     categories: List[AuditEventCategory] = None,
                     severities: List[AuditEventSeverity] = None,
                     user_id: str = None,
                     ip_address: str = None,
                     target_type: str = None,
                     target_id: str = None,
                     operation: str = None,
                     resource: str = None,
                     session_id: str = None,
                     correlation_id: str = None,
                     text_search: str = None,
                     tags: List[str] = None,
                     limit: int = 1000,
                     offset: int = 0) -> List[AuditEvent]:
        """Search audit events with flexible filters."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = 'SELECT data_json FROM audit_events WHERE 1=1'
            params = []
            
            # Time range
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date.isoformat())
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date.isoformat())
            
            # Event filters
            if event_types:
                placeholders = ','.join(['?' for _ in event_types])
                query += f' AND event_type IN ({placeholders})'
                params.extend([et.value for et in event_types])
            
            if categories:
                placeholders = ','.join(['?' for _ in categories])
                query += f' AND category IN ({placeholders})'
                params.extend([c.value for c in categories])
            
            if severities:
                placeholders = ','.join(['?' for _ in severities])
                query += f' AND severity IN ({placeholders})'
                params.extend([s.value for s in severities])
            
            # User and IP filters
            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)
            
            if ip_address:
                query += ' AND ip_address = ?'
                params.append(ip_address)
            
            # Target filters
            if target_type:
                query += ' AND target_type = ?'
                params.append(target_type)
            
            if target_id:
                query += ' AND target_id = ?'
                params.append(target_id)
            
            # Operation filters
            if operation:
                query += ' AND operation = ?'
                params.append(operation)
            
            if resource:
                query += ' AND resource LIKE ?'
                params.append(f'%{resource}%')
            
            # Session and correlation
            if session_id:
                query += ' AND session_id = ?'
                params.append(session_id)
            
            if correlation_id:
                query += ' AND correlation_id = ?'
                params.append(correlation_id)
            
            # Text search
            if text_search:
                query += ' AND (title LIKE ? OR description LIKE ? OR message LIKE ?)'
                search_pattern = f'%{text_search}%'
                params.extend([search_pattern, search_pattern, search_pattern])
            
            # Tags search
            if tags:
                for tag in tags:
                    query += ' AND tags LIKE ?'
                    params.append(f'%"{tag}"%')
            
            # Order and limit
            query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [AuditEvent.from_dict(json.loads(row[0])) for row in rows]
    
    def get_event_by_id(self, event_id: str) -> Optional[AuditEvent]:
        """Get a specific audit event by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT data_json FROM audit_events WHERE event_id = ?', (event_id,))
            row = cursor.fetchone()
            
            if row:
                return AuditEvent.from_dict(json.loads(row[0]))
            
            return None
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get audit statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Overall counts
            cursor.execute('''
                SELECT COUNT(*) FROM audit_events 
                WHERE timestamp >= ?
            ''', (cutoff_date.isoformat(),))
            total_events = cursor.fetchone()[0]
            
            # Events by category
            cursor.execute('''
                SELECT category, COUNT(*) FROM audit_events 
                WHERE timestamp >= ?
                GROUP BY category
                ORDER BY COUNT(*) DESC
            ''', (cutoff_date.isoformat(),))
            by_category = dict(cursor.fetchall())
            
            # Events by severity
            cursor.execute('''
                SELECT severity, COUNT(*) FROM audit_events 
                WHERE timestamp >= ?
                GROUP BY severity
                ORDER BY 
                    CASE severity 
                        WHEN 'critical' THEN 5
                        WHEN 'high' THEN 4
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 2
                        WHEN 'info' THEN 1
                    END DESC
            ''', (cutoff_date.isoformat(),))
            by_severity = dict(cursor.fetchall())
            
            # Top users
            cursor.execute('''
                SELECT username, COUNT(*) FROM audit_events 
                WHERE timestamp >= ? AND username IS NOT NULL
                GROUP BY username
                ORDER BY COUNT(*) DESC
                LIMIT 10
            ''', (cutoff_date.isoformat(),))
            top_users = dict(cursor.fetchall())
            
            # Top IPs
            cursor.execute('''
                SELECT ip_address, COUNT(*) FROM audit_events 
                WHERE timestamp >= ? AND ip_address IS NOT NULL
                GROUP BY ip_address
                ORDER BY COUNT(*) DESC
                LIMIT 10
            ''', (cutoff_date.isoformat(),))
            top_ips = dict(cursor.fetchall())
            
            # Recent high-severity events
            cursor.execute('''
                SELECT event_id, title, severity, timestamp, username, ip_address
                FROM audit_events 
                WHERE timestamp >= ? AND severity IN ('high', 'critical')
                ORDER BY timestamp DESC
                LIMIT 20
            ''', (cutoff_date.isoformat(),))
            
            high_severity_events = [
                {
                    'event_id': row[0],
                    'title': row[1],
                    'severity': row[2],
                    'timestamp': row[3],
                    'username': row[4],
                    'ip_address': row[5]
                }
                for row in cursor.fetchall()
            ]
            
            return {
                'period_days': days,
                'total_events': total_events,
                'events_by_category': by_category,
                'events_by_severity': by_severity,
                'top_users': top_users,
                'top_ip_addresses': top_ips,
                'high_severity_events': high_severity_events,
                'critical_events': by_severity.get('critical', 0),
                'high_events': by_severity.get('high', 0)
            }
    
    def add_event_listener(self, listener: Callable[[AuditEvent], None]) -> None:
        """Add an event listener."""
        with self._lock:
            self._event_listeners.append(listener)
    
    def remove_event_listener(self, listener: Callable[[AuditEvent], None]) -> None:
        """Remove an event listener."""
        with self._lock:
            if listener in self._event_listeners:
                self._event_listeners.remove(listener)
    
    def cleanup_old_events(self) -> int:
        """Clean up old events based on retention policies."""
        with self._lock:
            total_deleted = 0
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get unique retention periods
                cursor.execute('SELECT DISTINCT retention_days FROM audit_events WHERE retention_days IS NOT NULL')
                retention_periods = [row[0] for row in cursor.fetchall()]
                
                for retention_days in retention_periods:
                    cutoff_date = datetime.now() - timedelta(days=retention_days)
                    
                    cursor.execute('''
                        DELETE FROM audit_events 
                        WHERE retention_days = ? AND timestamp < ?
                    ''', (retention_days, cutoff_date.isoformat()))
                    
                    total_deleted += cursor.rowcount
                
                # Also clean up statistics
                old_stats_cutoff = datetime.now() - timedelta(days=max(retention_periods) if retention_periods else 365)
                cursor.execute('''
                    DELETE FROM audit_statistics 
                    WHERE date < ?
                ''', (old_stats_cutoff.date().isoformat(),))
                
                conn.commit()
            
            return total_deleted
    
    def export_events(self, 
                     start_date: datetime,
                     end_date: datetime,
                     format: str = 'json',
                     **search_kwargs) -> str:
        """Export audit events to various formats."""
        events = self.search_events(
            start_date=start_date,
            end_date=end_date,
            limit=10000,  # Large limit for export
            **search_kwargs
        )
        
        if format.lower() == 'json':
            return json.dumps([event.to_dict() for event in events], indent=2, default=str)
        elif format.lower() == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            if events:
                fieldnames = ['timestamp', 'event_type', 'category', 'severity', 'title', 
                             'username', 'ip_address', 'operation', 'resource', 'status_code']
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for event in events:
                    writer.writerow({
                        'timestamp': event.timestamp.isoformat(),
                        'event_type': event.event_type.value,
                        'category': event.category.value,
                        'severity': event.severity.value,
                        'title': event.title,
                        'username': event.context.username or '',
                        'ip_address': event.context.ip_address or '',
                        'operation': event.operation or '',
                        'resource': event.resource or '',
                        'status_code': event.status_code or ''
                    })
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global logger instance
_audit_logger = None
_logger_lock = RLock()


def get_audit_logger() -> AuditLogger:
    """
    Get the global audit logger instance (singleton).
    
    Returns:
        Global audit logger instance
    """
    global _audit_logger
    with _logger_lock:
        if _audit_logger is None:
            _audit_logger = AuditLogger()
        return _audit_logger


def reset_audit_logger() -> None:
    """Reset the global audit logger (mainly for testing)."""
    global _audit_logger
    with _logger_lock:
        _audit_logger = None