"""
Security auditing system for API key usage and security events.
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from threading import RLock
from dataclasses import dataclass, field
from enum import Enum

from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class SecurityEventType(Enum):
    """Types of security events to audit."""
    API_KEY_CREATED = "api_key_created"
    API_KEY_USED = "api_key_used"
    API_KEY_REVOKED = "api_key_revoked"
    API_KEY_EXPIRED = "api_key_expired"
    AUTHENTICATION_SUCCESS = "auth_success"
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_FAILURE = "auth_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    IP_BLOCKED = "ip_blocked"
    PERMISSION_ESCALATION = "permission_escalation"
    CONFIGURATION_CHANGE = "config_change"
    SYSTEM_ACCESS = "system_access"


class SecurityEventSeverity(Enum):
    """Severity levels for security events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event for auditing."""
    event_id: str = ""
    event_type: SecurityEventType = SecurityEventType.API_KEY_USED
    severity: SecurityEventSeverity = SecurityEventSeverity.LOW
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Event context
    api_key_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    
    # Event details
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Response info
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    
    # Risk assessment
    risk_score: int = 0  # 0-100
    anomaly_indicators: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'api_key_id': self.api_key_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'endpoint': self.endpoint,
            'method': self.method,
            'message': self.message,
            'details': self.details,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'risk_score': self.risk_score,
            'anomaly_indicators': self.anomaly_indicators
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityEvent':
        """Create from dictionary."""
        event = cls(
            event_id=data.get('event_id', ''),
            event_type=SecurityEventType(data.get('event_type', 'api_key_used')),
            severity=SecurityEventSeverity(data.get('severity', 'low')),
            api_key_id=data.get('api_key_id'),
            user_id=data.get('user_id'),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            endpoint=data.get('endpoint'),
            method=data.get('method'),
            message=data.get('message', ''),
            details=data.get('details', {}),
            status_code=data.get('status_code'),
            response_time_ms=data.get('response_time_ms'),
            risk_score=data.get('risk_score', 0),
            anomaly_indicators=data.get('anomaly_indicators', [])
        )
        
        if 'timestamp' in data:
            event.timestamp = datetime.fromisoformat(data['timestamp'])
        
        return event


class SecurityAuditor:
    """
    Security auditing system for tracking and analyzing security events.
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize security auditor."""
        self._lock = RLock()
        self.data_dir = data_dir or os.path.join(os.getcwd(), ".data", "monitoring")
        self.db_path = os.path.join(self.data_dir, "security_audit.db")
        self.change_tracker = get_change_tracker()
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Risk scoring configuration
        self.risk_thresholds = {
            'failed_auth_attempts': 5,  # per hour
            'rate_limit_violations': 10,  # per hour
            'unusual_endpoints': 3,  # new endpoints per key
            'geographic_anomaly': True,  # requests from different countries
            'time_anomaly': True,  # requests at unusual hours
        }
    
    def _init_database(self) -> None:
        """Initialize SQLite database for security audit logs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Security events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    api_key_id TEXT,
                    user_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    endpoint TEXT,
                    method TEXT,
                    message TEXT NOT NULL,
                    status_code INTEGER,
                    response_time_ms INTEGER,
                    risk_score INTEGER DEFAULT 0,
                    data_json TEXT NOT NULL
                )
            ''')
            
            # IP address tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_tracking (
                    ip_address TEXT PRIMARY KEY,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    request_count INTEGER DEFAULT 0,
                    failed_auth_count INTEGER DEFAULT 0,
                    is_blocked BOOLEAN DEFAULT FALSE,
                    country_code TEXT,
                    city TEXT,
                    is_suspicious BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON security_events (event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_severity ON security_events (severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_api_key ON security_events (api_key_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_ip ON security_events (ip_address)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_tracking_last_seen ON ip_tracking (last_seen)')
            
            conn.commit()
    
    def log_security_event(self, event: SecurityEvent) -> None:
        """Log a security event."""
        with self._lock:
            # Generate event ID if not provided
            if not event.event_id:
                event.event_id = f"{event.event_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(event.to_dict())) % 10000:04d}"
            
            # Calculate risk score if not set
            if event.risk_score == 0:
                event.risk_score = self._calculate_risk_score(event)
            
            # Determine severity based on risk score if not set
            if event.severity == SecurityEventSeverity.LOW and event.risk_score > 0:
                if event.risk_score >= 80:
                    event.severity = SecurityEventSeverity.CRITICAL
                elif event.risk_score >= 60:
                    event.severity = SecurityEventSeverity.HIGH
                elif event.risk_score >= 30:
                    event.severity = SecurityEventSeverity.MEDIUM
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO security_events (
                        event_id, event_type, severity, timestamp,
                        api_key_id, user_id, ip_address, user_agent,
                        endpoint, method, message, status_code,
                        response_time_ms, risk_score, data_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.event_id,
                    event.event_type.value,
                    event.severity.value,
                    event.timestamp.isoformat(),
                    event.api_key_id,
                    event.user_id,
                    event.ip_address,
                    event.user_agent,
                    event.endpoint,
                    event.method,
                    event.message,
                    event.status_code,
                    event.response_time_ms,
                    event.risk_score,
                    json.dumps(event.to_dict())
                ))
                
                conn.commit()
            
            # Update IP tracking
            if event.ip_address:
                self._update_ip_tracking(event)
            
            # Track in change tracker for high-severity events
            if event.severity in [SecurityEventSeverity.HIGH, SecurityEventSeverity.CRITICAL]:
                self.change_tracker.track_change(
                    change_type=ChangeType.CREATE,
                    category=ChangeCategory.SECURITY,
                    entity_id=event.event_id,
                    description=f"Security event: {event.message}",
                    metadata={
                        'event_type': event.event_type.value,
                        'severity': event.severity.value,
                        'risk_score': event.risk_score,
                        'ip_address': event.ip_address
                    }
                )
    
    def _update_ip_tracking(self, event: SecurityEvent) -> None:
        """Update IP address tracking."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if IP exists
            cursor.execute('SELECT * FROM ip_tracking WHERE ip_address = ?', (event.ip_address,))
            row = cursor.fetchone()
            
            if row:
                # Update existing record
                failed_count = row[4]
                if event.event_type == SecurityEventType.AUTHENTICATION_FAILURE:
                    failed_count += 1
                
                cursor.execute('''
                    UPDATE ip_tracking 
                    SET last_seen = ?, request_count = request_count + 1,
                        failed_auth_count = ?, is_suspicious = ?
                    WHERE ip_address = ?
                ''', (
                    event.timestamp.isoformat(),
                    failed_count,
                    failed_count >= self.risk_thresholds['failed_auth_attempts'],
                    event.ip_address
                ))
            else:
                # Insert new record
                failed_count = 1 if event.event_type == SecurityEventType.AUTHENTICATION_FAILURE else 0
                
                cursor.execute('''
                    INSERT INTO ip_tracking (
                        ip_address, first_seen, last_seen, request_count,
                        failed_auth_count, is_suspicious
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    event.ip_address,
                    event.timestamp.isoformat(),
                    event.timestamp.isoformat(),
                    1,
                    failed_count,
                    failed_count >= self.risk_thresholds['failed_auth_attempts']
                ))
            
            conn.commit()
    
    def _calculate_risk_score(self, event: SecurityEvent) -> int:
        """Calculate risk score for an event."""
        risk_score = 0
        
        # Base risk by event type
        base_risks = {
            SecurityEventType.AUTHENTICATION_FAILURE: 20,
            SecurityEventType.AUTHORIZATION_FAILURE: 15,
            SecurityEventType.RATE_LIMIT_EXCEEDED: 25,
            SecurityEventType.SUSPICIOUS_ACTIVITY: 40,
            SecurityEventType.PERMISSION_ESCALATION: 60,
            SecurityEventType.IP_BLOCKED: 80,
            SecurityEventType.API_KEY_USED: 5,
            SecurityEventType.SYSTEM_ACCESS: 30
        }
        
        risk_score += base_risks.get(event.event_type, 10)
        
        # Risk factors
        if event.ip_address:
            # Check IP history
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT failed_auth_count, is_suspicious 
                    FROM ip_tracking 
                    WHERE ip_address = ?
                ''', (event.ip_address,))
                
                row = cursor.fetchone()
                if row:
                    failed_count, is_suspicious = row
                    if failed_count > 3:
                        risk_score += min(failed_count * 5, 30)
                    if is_suspicious:
                        risk_score += 20
        
        # Time-based risk (unusual hours)
        hour = event.timestamp.hour
        if hour < 6 or hour > 22:  # Outside business hours
            risk_score += 10
            event.anomaly_indicators.append("unusual_time")
        
        # Status code risk
        if event.status_code:
            if event.status_code >= 500:
                risk_score += 15
            elif event.status_code >= 400:
                risk_score += 10
        
        # Response time anomaly
        if event.response_time_ms and event.response_time_ms > 5000:  # > 5 seconds
            risk_score += 10
            event.anomaly_indicators.append("slow_response")
        
        return min(risk_score, 100)  # Cap at 100
    
    def get_security_events(self,
                           start_date: datetime = None,
                           end_date: datetime = None,
                           event_type: SecurityEventType = None,
                           severity: SecurityEventSeverity = None,
                           api_key_id: str = None,
                           ip_address: str = None,
                           limit: int = 100) -> List[SecurityEvent]:
        """Get security events with filters."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = 'SELECT data_json FROM security_events WHERE 1=1'
            params = []
            
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date.isoformat())
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date.isoformat())
            
            if event_type:
                query += ' AND event_type = ?'
                params.append(event_type.value)
            
            if severity:
                query += ' AND severity = ?'
                params.append(severity.value)
            
            if api_key_id:
                query += ' AND api_key_id = ?'
                params.append(api_key_id)
            
            if ip_address:
                query += ' AND ip_address = ?'
                params.append(ip_address)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [SecurityEvent.from_dict(json.loads(row[0])) for row in rows]
    
    def get_security_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get security summary for the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Event counts by type
            cursor.execute('''
                SELECT event_type, COUNT(*) 
                FROM security_events 
                WHERE timestamp >= ?
                GROUP BY event_type
            ''', (cutoff_date.isoformat(),))
            
            event_counts = dict(cursor.fetchall())
            
            # Event counts by severity
            cursor.execute('''
                SELECT severity, COUNT(*) 
                FROM security_events 
                WHERE timestamp >= ?
                GROUP BY severity
            ''', (cutoff_date.isoformat(),))
            
            severity_counts = dict(cursor.fetchall())
            
            # Top risky events
            cursor.execute('''
                SELECT message, risk_score, timestamp, ip_address
                FROM security_events 
                WHERE timestamp >= ? AND risk_score > 50
                ORDER BY risk_score DESC
                LIMIT 10
            ''', (cutoff_date.isoformat(),))
            
            risky_events = [
                {
                    'message': row[0],
                    'risk_score': row[1],
                    'timestamp': row[2],
                    'ip_address': row[3]
                }
                for row in cursor.fetchall()
            ]
            
            # Suspicious IPs
            cursor.execute('''
                SELECT ip_address, failed_auth_count, request_count, last_seen
                FROM ip_tracking 
                WHERE is_suspicious = TRUE
                ORDER BY failed_auth_count DESC
                LIMIT 10
            ''')
            
            suspicious_ips = [
                {
                    'ip_address': row[0],
                    'failed_attempts': row[1],
                    'total_requests': row[2],
                    'last_seen': row[3]
                }
                for row in cursor.fetchall()
            ]
            
            # Most active IPs
            cursor.execute('''
                SELECT ip_address, request_count, failed_auth_count, last_seen
                FROM ip_tracking 
                WHERE last_seen >= ?
                ORDER BY request_count DESC
                LIMIT 10
            ''', (cutoff_date.isoformat(),))
            
            active_ips = [
                {
                    'ip_address': row[0],
                    'requests': row[1],
                    'failed_attempts': row[2],
                    'last_seen': row[3]
                }
                for row in cursor.fetchall()
            ]
            
            return {
                'period_days': days,
                'total_events': sum(event_counts.values()),
                'events_by_type': event_counts,
                'events_by_severity': severity_counts,
                'critical_events': severity_counts.get('critical', 0),
                'high_risk_events': len(risky_events),
                'risky_events': risky_events,
                'suspicious_ips': suspicious_ips,
                'most_active_ips': active_ips,
                'blocked_ips': len([ip for ip in suspicious_ips if ip['failed_attempts'] >= 10])
            }
    
    def get_api_key_audit_trail(self, api_key_id: str, days: int = 30) -> List[SecurityEvent]:
        """Get audit trail for a specific API key."""
        start_date = datetime.now() - timedelta(days=days)
        return self.get_security_events(
            start_date=start_date,
            api_key_id=api_key_id,
            limit=1000
        )
    
    def detect_anomalies(self, days: int = 7) -> List[Dict[str, Any]]:
        """Detect security anomalies in the last N days."""
        anomalies = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Detect unusual activity patterns
            
            # 1. Sudden spike in failed authentications
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as failures
                FROM security_events 
                WHERE timestamp >= ? AND event_type = ?
                GROUP BY DATE(timestamp)
                ORDER BY failures DESC
                LIMIT 5
            ''', (cutoff_date.isoformat(), SecurityEventType.AUTHENTICATION_FAILURE.value))
            
            daily_failures = cursor.fetchall()
            if daily_failures and daily_failures[0][1] > 20:  # More than 20 failures in a day
                anomalies.append({
                    'type': 'authentication_spike',
                    'severity': 'high',
                    'description': f'Unusual spike in failed authentications: {daily_failures[0][1]} on {daily_failures[0][0]}',
                    'data': daily_failures
                })
            
            # 2. New IP addresses with high activity
            cursor.execute('''
                SELECT ip_address, request_count, first_seen
                FROM ip_tracking 
                WHERE first_seen >= ? AND request_count > 50
                ORDER BY request_count DESC
            ''', (cutoff_date.isoformat(),))
            
            new_active_ips = cursor.fetchall()
            if new_active_ips:
                anomalies.append({
                    'type': 'new_active_ips',
                    'severity': 'medium',
                    'description': f'New IP addresses with high activity: {len(new_active_ips)} IPs',
                    'data': new_active_ips
                })
            
            # 3. Unusual time patterns
            cursor.execute('''
                SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                FROM security_events 
                WHERE timestamp >= ?
                GROUP BY strftime('%H', timestamp)
                HAVING count > 100
                AND (hour < '06' OR hour > '22')
            ''', (cutoff_date.isoformat(),))
            
            unusual_hours = cursor.fetchall()
            if unusual_hours:
                anomalies.append({
                    'type': 'unusual_time_activity',
                    'severity': 'medium',
                    'description': f'High activity during unusual hours',
                    'data': unusual_hours
                })
        
        return anomalies
    
    def cleanup_old_events(self, days: int = 90) -> int:
        """Clean up old security events."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Count events to be deleted
            cursor.execute('''
                SELECT COUNT(*) FROM security_events 
                WHERE timestamp < ? AND severity NOT IN (?, ?)
            ''', (cutoff_date.isoformat(), 
                  SecurityEventSeverity.HIGH.value, 
                  SecurityEventSeverity.CRITICAL.value))
            
            count = cursor.fetchone()[0]
            
            # Delete old low/medium severity events (keep high/critical)
            cursor.execute('''
                DELETE FROM security_events 
                WHERE timestamp < ? AND severity NOT IN (?, ?)
            ''', (cutoff_date.isoformat(),
                  SecurityEventSeverity.HIGH.value,
                  SecurityEventSeverity.CRITICAL.value))
            
            conn.commit()
            
            return count
    
    def block_ip_address(self, ip_address: str, reason: str = "Manual block") -> None:
        """Block an IP address."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE ip_tracking 
                SET is_blocked = TRUE, is_suspicious = TRUE
                WHERE ip_address = ?
            ''', (ip_address,))
            
            if cursor.rowcount == 0:
                # Insert if doesn't exist
                cursor.execute('''
                    INSERT INTO ip_tracking (
                        ip_address, first_seen, last_seen, request_count,
                        failed_auth_count, is_blocked, is_suspicious
                    ) VALUES (?, ?, ?, 0, 0, TRUE, TRUE)
                ''', (ip_address, datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
        
        # Log the blocking event
        event = SecurityEvent(
            event_type=SecurityEventType.IP_BLOCKED,
            severity=SecurityEventSeverity.HIGH,
            ip_address=ip_address,
            message=f"IP address {ip_address} blocked: {reason}",
            details={'reason': reason},
            risk_score=80
        )
        
        self.log_security_event(event)
    
    def unblock_ip_address(self, ip_address: str) -> None:
        """Unblock an IP address."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE ip_tracking 
                SET is_blocked = FALSE
                WHERE ip_address = ?
            ''', (ip_address,))
            
            conn.commit()
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if an IP address is blocked."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT is_blocked FROM ip_tracking 
                WHERE ip_address = ?
            ''', (ip_address,))
            
            row = cursor.fetchone()
            return row and row[0]


# Global auditor instance
_security_auditor = None
_auditor_lock = RLock()


def get_security_auditor() -> SecurityAuditor:
    """
    Get the global security auditor instance (singleton).
    
    Returns:
        Global security auditor instance
    """
    global _security_auditor
    with _auditor_lock:
        if _security_auditor is None:
            _security_auditor = SecurityAuditor()
        return _security_auditor


def reset_security_auditor() -> None:
    """Reset the global security auditor (mainly for testing)."""
    global _security_auditor
    with _auditor_lock:
        _security_auditor = None