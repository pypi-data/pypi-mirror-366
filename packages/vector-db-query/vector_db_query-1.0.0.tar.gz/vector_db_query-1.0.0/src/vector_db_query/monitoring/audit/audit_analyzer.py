"""
Advanced audit data analysis and reporting capabilities.
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from threading import RLock
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import statistics

from .audit_models import AuditEvent, AuditEventType, AuditEventCategory, AuditEventSeverity
from .audit_logger import get_audit_logger


@dataclass
class AuditTrend:
    """Trend analysis for audit events."""
    category: str
    metric: str
    period: str
    values: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    trend_direction: str = ""  # "increasing", "decreasing", "stable"
    trend_confidence: float = 0.0
    average: float = 0.0
    median: float = 0.0
    std_dev: float = 0.0
    
    def calculate_statistics(self) -> None:
        """Calculate statistical measures for the trend."""
        if not self.values:
            return
        
        self.average = statistics.mean(self.values)
        self.median = statistics.median(self.values)
        
        if len(self.values) > 1:
            self.std_dev = statistics.stdev(self.values)
            
            # Simple trend detection
            if len(self.values) >= 3:
                recent_avg = statistics.mean(self.values[-3:])
                older_avg = statistics.mean(self.values[:3])
                
                if recent_avg > older_avg * 1.1:
                    self.trend_direction = "increasing"
                    self.trend_confidence = min(1.0, (recent_avg - older_avg) / older_avg)
                elif recent_avg < older_avg * 0.9:
                    self.trend_direction = "decreasing"
                    self.trend_confidence = min(1.0, (older_avg - recent_avg) / older_avg)
                else:
                    self.trend_direction = "stable"
                    self.trend_confidence = 1.0 - (abs(recent_avg - older_avg) / older_avg)


@dataclass
class AuditPattern:
    """Detected pattern in audit events."""
    pattern_type: str
    description: str
    frequency: int
    severity: AuditEventSeverity
    first_seen: datetime
    last_seen: datetime
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    
    def calculate_risk_score(self) -> None:
        """Calculate risk score based on pattern characteristics."""
        base_score = {
            AuditEventSeverity.INFO: 0.1,
            AuditEventSeverity.LOW: 0.2,
            AuditEventSeverity.MEDIUM: 0.5,
            AuditEventSeverity.HIGH: 0.8,
            AuditEventSeverity.CRITICAL: 1.0
        }.get(self.severity, 0.5)
        
        # Adjust based on frequency
        frequency_multiplier = min(2.0, 1.0 + (self.frequency / 100.0))
        
        # Adjust based on recency
        days_since_last = (datetime.now() - self.last_seen).days
        recency_multiplier = max(0.5, 1.0 - (days_since_last / 30.0))
        
        self.risk_score = min(1.0, base_score * frequency_multiplier * recency_multiplier)


@dataclass
class AuditAnomaly:
    """Detected anomaly in audit data."""
    anomaly_type: str
    description: str
    severity: AuditEventSeverity
    detected_at: datetime
    event_ids: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    threshold_exceeded: Optional[str] = None
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'anomaly_type': self.anomaly_type,
            'description': self.description,
            'severity': self.severity.value,
            'detected_at': self.detected_at.isoformat(),
            'event_ids': self.event_ids,
            'metrics': self.metrics,
            'threshold_exceeded': self.threshold_exceeded,
            'confidence': self.confidence
        }


@dataclass
class ComplianceReport:
    """Compliance analysis report."""
    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    total_events: int
    events_by_category: Dict[str, int] = field(default_factory=dict)
    events_by_severity: Dict[str, int] = field(default_factory=dict)
    security_events: int = 0
    data_access_events: int = 0
    failed_operations: int = 0
    anomalies_detected: int = 0
    compliance_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    
    def calculate_compliance_score(self) -> None:
        """Calculate overall compliance score."""
        if self.total_events == 0:
            self.compliance_score = 1.0
            return
        
        # Base score starts at 1.0
        score = 1.0
        
        # Deduct for security issues
        security_ratio = self.security_events / self.total_events
        score -= security_ratio * 0.3
        
        # Deduct for failed operations
        failure_ratio = self.failed_operations / self.total_events
        score -= failure_ratio * 0.2
        
        # Deduct for anomalies
        anomaly_ratio = self.anomalies_detected / max(1, self.total_events / 100)
        score -= min(0.3, anomaly_ratio * 0.1)
        
        self.compliance_score = max(0.0, score)


class AuditAnalyzer:
    """
    Advanced audit data analysis and reporting.
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize audit analyzer."""
        self._lock = RLock()
        self.data_dir = data_dir or os.path.join(os.getcwd(), ".data", "monitoring")
        self.db_path = os.path.join(self.data_dir, "audit_analytics.db")
        self.audit_logger = get_audit_logger()
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize analytics database
        self._init_database()
        
        # Analysis thresholds
        self.anomaly_thresholds = {
            'high_frequency_user': 100,  # events per hour
            'failed_login_attempts': 5,   # per hour
            'data_access_spike': 50,      # events per hour
            'error_rate_spike': 0.1,      # 10% error rate
            'unusual_ip_activity': 20     # events from single IP per hour
        }
    
    def _init_database(self) -> None:
        """Initialize analytics database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Trends table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    period TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    frequency INTEGER NOT NULL,
                    severity TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    examples TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Anomalies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anomaly_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    event_ids TEXT,
                    metrics TEXT,
                    threshold_exceeded TEXT,
                    confidence REAL NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Compliance reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compliance_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id TEXT UNIQUE NOT NULL,
                    generated_at TEXT NOT NULL,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    total_events INTEGER NOT NULL,
                    compliance_score REAL NOT NULL,
                    report_data TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_category ON audit_trends (category, metric)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_timestamp ON audit_trends (timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_type ON audit_patterns (pattern_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_type ON audit_anomalies (anomaly_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_detected ON audit_anomalies (detected_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_generated ON compliance_reports (generated_at)')
            
            conn.commit()
    
    def analyze_trends(self, days: int = 30) -> List[AuditTrend]:
        """Analyze trends in audit data."""
        with self._lock:
            trends = []
            
            # Get audit statistics from logger
            stats = self.audit_logger.get_statistics(days=days)
            
            # Analyze category trends
            for category, count in stats.get('events_by_category', {}).items():
                trend = AuditTrend(
                    category=category,
                    metric="event_count",
                    period=f"{days}d",
                    values=[float(count)],
                    timestamps=[datetime.now()]
                )
                trend.calculate_statistics()
                trends.append(trend)
            
            # Analyze severity trends
            for severity, count in stats.get('events_by_severity', {}).items():
                trend = AuditTrend(
                    category="severity",
                    metric=severity,
                    period=f"{days}d",
                    values=[float(count)],
                    timestamps=[datetime.now()]
                )
                trend.calculate_statistics()
                trends.append(trend)
            
            return trends
    
    def detect_patterns(self, days: int = 7) -> List[AuditPattern]:
        """Detect patterns in audit events."""
        with self._lock:
            patterns = []
            
            # Get recent events
            start_date = datetime.now() - timedelta(days=days)
            events = self.audit_logger.search_events(
                start_date=start_date,
                limit=5000
            )
            
            if not events:
                return patterns
            
            # Pattern 1: Repeated failed logins
            failed_logins = defaultdict(list)
            for event in events:
                if event.event_type == AuditEventType.SECURITY_LOGIN_FAIL:
                    key = f"{event.context.username}_{event.context.ip_address}"
                    failed_logins[key].append(event)
            
            for key, login_events in failed_logins.items():
                if len(login_events) >= 3:
                    pattern = AuditPattern(
                        pattern_type="repeated_failed_logins",
                        description=f"Multiple failed login attempts from {key}",
                        frequency=len(login_events),
                        severity=AuditEventSeverity.HIGH,
                        first_seen=min(e.timestamp for e in login_events),
                        last_seen=max(e.timestamp for e in login_events),
                        examples=[e.event_id for e in login_events[:3]]
                    )
                    pattern.calculate_risk_score()
                    patterns.append(pattern)
            
            # Pattern 2: High-frequency API usage
            api_usage = defaultdict(list)
            for event in events:
                if event.event_type == AuditEventType.API_REQUEST:
                    key = f"{event.context.user_id}_{event.resource}"
                    api_usage[key].append(event)
            
            for key, api_events in api_usage.items():
                if len(api_events) >= 50:  # High frequency threshold
                    pattern = AuditPattern(
                        pattern_type="high_frequency_api_usage",
                        description=f"High-frequency API usage: {key}",
                        frequency=len(api_events),
                        severity=AuditEventSeverity.MEDIUM,
                        first_seen=min(e.timestamp for e in api_events),
                        last_seen=max(e.timestamp for e in api_events),
                        examples=[e.event_id for e in api_events[:3]]
                    )
                    pattern.calculate_risk_score()
                    patterns.append(pattern)
            
            # Pattern 3: Data export activities
            data_exports = [e for e in events if e.event_type == AuditEventType.DATA_EXPORT]
            if data_exports:
                pattern = AuditPattern(
                    pattern_type="data_export_activity",
                    description=f"Data export activities detected",
                    frequency=len(data_exports),
                    severity=AuditEventSeverity.MEDIUM,
                    first_seen=min(e.timestamp for e in data_exports),
                    last_seen=max(e.timestamp for e in data_exports),
                    examples=[e.event_id for e in data_exports[:3]]
                )
                pattern.calculate_risk_score()
                patterns.append(pattern)
            
            return patterns
    
    def detect_anomalies(self, hours: int = 24) -> List[AuditAnomaly]:
        """Detect anomalies in recent audit data."""
        with self._lock:
            anomalies = []
            
            # Get recent events
            start_time = datetime.now() - timedelta(hours=hours)
            events = self.audit_logger.search_events(
                start_date=start_time,
                limit=10000
            )
            
            if not events:
                return anomalies
            
            # Anomaly 1: High frequency from single user
            user_events = defaultdict(list)
            for event in events:
                if event.context.user_id:
                    user_events[event.context.user_id].append(event)
            
            for user_id, user_event_list in user_events.items():
                if len(user_event_list) > self.anomaly_thresholds['high_frequency_user']:
                    anomaly = AuditAnomaly(
                        anomaly_type="high_frequency_user",
                        description=f"User {user_id} generated {len(user_event_list)} events in {hours} hours",
                        severity=AuditEventSeverity.MEDIUM,
                        detected_at=datetime.now(),
                        event_ids=[e.event_id for e in user_event_list[:10]],
                        metrics={'event_count': len(user_event_list), 'threshold': self.anomaly_thresholds['high_frequency_user']},
                        threshold_exceeded='high_frequency_user',
                        confidence=min(1.0, len(user_event_list) / self.anomaly_thresholds['high_frequency_user'])
                    )
                    anomalies.append(anomaly)
            
            # Anomaly 2: Failed login spike
            failed_logins = [e for e in events if e.event_type == AuditEventType.SECURITY_LOGIN_FAIL]
            if len(failed_logins) > self.anomaly_thresholds['failed_login_attempts']:
                anomaly = AuditAnomaly(
                    anomaly_type="failed_login_spike",
                    description=f"{len(failed_logins)} failed login attempts in {hours} hours",
                    severity=AuditEventSeverity.HIGH,
                    detected_at=datetime.now(),
                    event_ids=[e.event_id for e in failed_logins[:10]],
                    metrics={'failed_logins': len(failed_logins), 'threshold': self.anomaly_thresholds['failed_login_attempts']},
                    threshold_exceeded='failed_login_attempts',
                    confidence=min(1.0, len(failed_logins) / self.anomaly_thresholds['failed_login_attempts'])
                )
                anomalies.append(anomaly)
            
            # Anomaly 3: Unusual IP activity
            ip_events = defaultdict(list)
            for event in events:
                if event.context.ip_address:
                    ip_events[event.context.ip_address].append(event)
            
            for ip_address, ip_event_list in ip_events.items():
                if len(ip_event_list) > self.anomaly_thresholds['unusual_ip_activity']:
                    anomaly = AuditAnomaly(
                        anomaly_type="unusual_ip_activity",
                        description=f"Unusual activity from IP {ip_address}: {len(ip_event_list)} events",
                        severity=AuditEventSeverity.MEDIUM,
                        detected_at=datetime.now(),
                        event_ids=[e.event_id for e in ip_event_list[:10]],
                        metrics={'event_count': len(ip_event_list), 'threshold': self.anomaly_thresholds['unusual_ip_activity']},
                        threshold_exceeded='unusual_ip_activity',
                        confidence=min(1.0, len(ip_event_list) / self.anomaly_thresholds['unusual_ip_activity'])
                    )
                    anomalies.append(anomaly)
            
            return anomalies
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> ComplianceReport:
        """Generate compliance analysis report."""
        with self._lock:
            import uuid
            
            report = ComplianceReport(
                report_id=str(uuid.uuid4()),
                generated_at=datetime.now(),
                period_start=start_date,
                period_end=end_date,
                total_events=0
            )
            
            # Get events for the period
            events = self.audit_logger.search_events(
                start_date=start_date,
                end_date=end_date,
                limit=50000
            )
            
            report.total_events = len(events)
            
            if events:
                # Count by category
                report.events_by_category = dict(Counter(e.category.value for e in events))
                
                # Count by severity
                report.events_by_severity = dict(Counter(e.severity.value for e in events))
                
                # Security events
                report.security_events = len([e for e in events if e.category == AuditEventCategory.SECURITY])
                
                # Data access events
                report.data_access_events = len([e for e in events if e.category == AuditEventCategory.DATA])
                
                # Failed operations
                report.failed_operations = len([e for e in events if not e.is_successful()])
                
                # Detect anomalies
                anomalies = self.detect_anomalies(hours=24)
                report.anomalies_detected = len(anomalies)
            
            # Calculate compliance score
            report.calculate_compliance_score()
            
            # Generate recommendations
            if report.compliance_score < 0.8:
                report.recommendations.append("Review security events and implement additional access controls")
            if report.failed_operations > report.total_events * 0.05:
                report.recommendations.append("Investigate high failure rate and improve system reliability")
            if report.anomalies_detected > 0:
                report.recommendations.append("Review detected anomalies and update security policies")
            
            # Save report
            self._save_compliance_report(report)
            
            return report
    
    def _save_compliance_report(self, report: ComplianceReport) -> None:
        """Save compliance report to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO compliance_reports (
                    report_id, generated_at, period_start, period_end,
                    total_events, compliance_score, report_data, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.report_id,
                report.generated_at.isoformat(),
                report.period_start.isoformat(),
                report.period_end.isoformat(),
                report.total_events,
                report.compliance_score,
                json.dumps({
                    'events_by_category': report.events_by_category,
                    'events_by_severity': report.events_by_severity,
                    'security_events': report.security_events,
                    'data_access_events': report.data_access_events,
                    'failed_operations': report.failed_operations,
                    'anomalies_detected': report.anomalies_detected,
                    'recommendations': report.recommendations
                }),
                datetime.now().isoformat()
            ))
            
            conn.commit()
    
    def get_compliance_reports(self, limit: int = 10) -> List[ComplianceReport]:
        """Get recent compliance reports."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT report_id, generated_at, period_start, period_end,
                       total_events, compliance_score, report_data
                FROM compliance_reports
                ORDER BY generated_at DESC
                LIMIT ?
            ''', (limit,))
            
            reports = []
            for row in cursor.fetchall():
                report_data = json.loads(row[6])
                
                report = ComplianceReport(
                    report_id=row[0],
                    generated_at=datetime.fromisoformat(row[1]),
                    period_start=datetime.fromisoformat(row[2]),
                    period_end=datetime.fromisoformat(row[3]),
                    total_events=row[4],
                    compliance_score=row[5],
                    events_by_category=report_data.get('events_by_category', {}),
                    events_by_severity=report_data.get('events_by_severity', {}),
                    security_events=report_data.get('security_events', 0),
                    data_access_events=report_data.get('data_access_events', 0),
                    failed_operations=report_data.get('failed_operations', 0),
                    anomalies_detected=report_data.get('anomalies_detected', 0),
                    recommendations=report_data.get('recommendations', [])
                )
                
                reports.append(report)
            
            return reports
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        with self._lock:
            # Get recent statistics
            stats = self.audit_logger.get_statistics(days=30)
            
            # Get trends
            trends = self.analyze_trends(days=30)
            
            # Get patterns
            patterns = self.detect_patterns(days=7)
            
            # Get anomalies
            anomalies = self.detect_anomalies(hours=24)
            
            # Get recent compliance reports
            reports = self.get_compliance_reports(limit=1)
            
            return {
                'statistics': stats,
                'trends': [
                    {
                        'category': t.category,
                        'metric': t.metric,
                        'trend_direction': t.trend_direction,
                        'confidence': t.trend_confidence,
                        'average': t.average
                    }
                    for t in trends
                ],
                'patterns': [
                    {
                        'pattern_type': p.pattern_type,
                        'description': p.description,
                        'frequency': p.frequency,
                        'risk_score': p.risk_score,
                        'severity': p.severity.value
                    }
                    for p in patterns
                ],
                'anomalies': [a.to_dict() for a in anomalies],
                'latest_compliance_score': reports[0].compliance_score if reports else 0.0,
                'total_events_30d': stats.get('total_events', 0),
                'high_severity_events': stats.get('high_events', 0),
                'critical_events': stats.get('critical_events', 0)
            }


# Global analyzer instance
_audit_analyzer = None
_analyzer_lock = RLock()


def get_audit_analyzer() -> AuditAnalyzer:
    """
    Get the global audit analyzer instance (singleton).
    
    Returns:
        Global audit analyzer instance
    """
    global _audit_analyzer
    with _analyzer_lock:
        if _audit_analyzer is None:
            _audit_analyzer = AuditAnalyzer()
        return _audit_analyzer


def reset_audit_analyzer() -> None:
    """Reset the global audit analyzer (mainly for testing)."""
    global _audit_analyzer
    with _analyzer_lock:
        _audit_analyzer = None