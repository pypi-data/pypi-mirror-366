"""
Comprehensive integration tests for the monitoring system.
"""

import os
import sys
import pytest
import tempfile
import shutil
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import monitoring components
from vector_db_query.monitoring.audit.audit_logger import AuditLogger, get_audit_logger, reset_audit_logger
from vector_db_query.monitoring.audit.audit_analyzer import AuditAnalyzer, get_audit_analyzer, reset_audit_analyzer
from vector_db_query.monitoring.audit.audit_models import (
    AuditEvent, AuditEventType, AuditEventCategory, AuditEventSeverity, AuditEventContext
)
from vector_db_query.monitoring.security.api_key_manager import APIKeyManager, get_api_key_manager
from vector_db_query.monitoring.security.api_key_models import APIKey, APIKeyScope, APIKeyPermission
from vector_db_query.monitoring.security.security_audit import SecurityAuditor, get_security_auditor
from vector_db_query.monitoring.history.change_tracker import ChangeTracker, get_change_tracker, reset_change_tracker


class TestIntegration:
    """Integration tests for monitoring system components."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up clean test environment for each test."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        
        # Reset all singletons to ensure clean state
        reset_audit_logger()
        reset_audit_analyzer()
        reset_change_tracker()
        
        yield
        
        # Cleanup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_audit_logger_basic_functionality(self):
        """Test basic audit logger functionality."""
        logger = AuditLogger(data_dir=self.test_dir)
        
        # Test event logging
        event = AuditEvent(
            event_type=AuditEventType.USER_LOGIN,
            category=AuditEventCategory.SECURITY,
            severity=AuditEventSeverity.INFO,
            title="Test Login",
            description="Test user login event"
        )
        event.context.user_id = "test_user"
        event.context.ip_address = "127.0.0.1"
        
        logger.log_event(event)
        
        # Verify event was logged
        events = logger.search_events(limit=10)
        assert len(events) == 1
        assert events[0].title == "Test Login"
        assert events[0].context.user_id == "test_user"
        
        # Test event retrieval by ID
        retrieved_event = logger.get_event_by_id(event.event_id)
        assert retrieved_event is not None
        assert retrieved_event.event_id == event.event_id
    
    def test_audit_analyzer_integration(self):
        """Test audit analyzer integration with logger."""
        logger = AuditLogger(data_dir=self.test_dir)
        analyzer = AuditAnalyzer(data_dir=self.test_dir)
        
        # Generate test events
        events_data = [
            (AuditEventType.USER_LOGIN, AuditEventCategory.SECURITY, AuditEventSeverity.INFO),
            (AuditEventType.SECURITY_LOGIN_FAIL, AuditEventCategory.SECURITY, AuditEventSeverity.MEDIUM),
            (AuditEventType.DATA_EXPORT, AuditEventCategory.DATA, AuditEventSeverity.HIGH),
            (AuditEventType.API_REQUEST, AuditEventCategory.API, AuditEventSeverity.INFO),
        ]
        
        for i, (event_type, category, severity) in enumerate(events_data):
            event = AuditEvent(
                event_type=event_type,
                category=category,
                severity=severity,
                title=f"Test Event {i+1}",
                description=f"Test event {i+1} for analysis"
            )
            event.context.user_id = f"user_{i+1}"
            event.context.ip_address = "127.0.0.1"
            logger.log_event(event)
        
        # Test analytics
        summary = analyzer.get_analytics_summary()
        assert summary['total_events_30d'] == 4
        assert len(summary['statistics']['events_by_category']) > 0
        
        # Test trend analysis
        trends = analyzer.analyze_trends(days=1)
        assert len(trends) > 0
        
        # Test pattern detection
        patterns = analyzer.detect_patterns(days=1)
        # Should not detect patterns with only 4 events
        assert len(patterns) == 0
    
    def test_security_system_integration(self):
        """Test security system integration with audit logging."""
        # Initialize components
        api_key_manager = APIKeyManager(data_dir=self.test_dir)
        security_auditor = SecurityAuditor(data_dir=self.test_dir)
        audit_logger = AuditLogger(data_dir=self.test_dir)
        
        # Create API key
        api_key, key_string = api_key_manager.create_api_key(
            name="Test API Key",
            scopes={APIKeyScope.READ_ONLY},
            permissions={APIKeyPermission.VIEW_DASHBOARDS},
            expires_days=30
        )
        
        assert api_key is not None
        assert key_string is not None
        
        # Test key authentication
        authenticated_key = api_key_manager.authenticate_key(key_string)
        assert authenticated_key is not None
        assert authenticated_key.key_id == api_key.key_id
        
        # Verify audit events were created
        events = audit_logger.search_events(
            event_types=[AuditEventType.API_KEY_CREATE],
            limit=10
        )
        assert len(events) >= 1
        
        # Test security event logging
        security_auditor.log_security_event(
            event_type=AuditEventType.SECURITY_ACCESS_DENIED,
            message="Test access denied",
            severity=AuditEventSeverity.MEDIUM,
            user_id="test_user",
            ip_address="192.168.1.100"
        )
        
        # Verify security event was logged in audit system
        security_events = audit_logger.search_events(
            categories=[AuditEventCategory.SECURITY],
            limit=10
        )
        assert len(security_events) >= 1
    
    def test_change_tracking_integration(self):
        """Test change tracking integration with audit system."""
        change_tracker = ChangeTracker(data_dir=self.test_dir)
        audit_logger = AuditLogger(data_dir=self.test_dir)
        
        # Test that high-severity audit events are tracked as changes
        high_severity_event = AuditEvent(
            event_type=AuditEventType.SECURITY_BREACH_ATTEMPT,
            category=AuditEventCategory.SECURITY,
            severity=AuditEventSeverity.CRITICAL,
            title="Test Security Breach",
            description="Critical security event for testing"
        )
        high_severity_event.context.user_id = "attacker"
        high_severity_event.context.ip_address = "192.168.1.666"
        
        audit_logger.log_event(high_severity_event)
        
        # Verify change was tracked
        changes = change_tracker.get_recent_changes(limit=10)
        audit_changes = [c for c in changes if c.category.value == 'audit']
        
        # Should have at least one audit-related change
        assert len(audit_changes) >= 1
    
    def test_event_listener_integration(self):
        """Test event listener integration across components."""
        audit_logger = AuditLogger(data_dir=self.test_dir)
        
        # Create a mock listener to test event propagation
        mock_listener = Mock()
        audit_logger.add_event_listener(mock_listener)
        
        # Log an event
        event = AuditEvent(
            event_type=AuditEventType.USER_ACTION,
            category=AuditEventCategory.USER,
            severity=AuditEventSeverity.INFO,
            title="Test Event for Listener",
            description="Testing event listener functionality"
        )
        
        audit_logger.log_event(event)
        
        # Verify listener was called
        mock_listener.assert_called_once()
        called_event = mock_listener.call_args[0][0]
        assert called_event.title == "Test Event for Listener"
        
        # Test listener removal
        audit_logger.remove_event_listener(mock_listener)
        
        # Log another event
        audit_logger.log_event(event)
        
        # Listener should still have been called only once
        assert mock_listener.call_count == 1
    
    def test_compliance_reporting_integration(self):
        """Test compliance reporting with real data."""
        logger = AuditLogger(data_dir=self.test_dir)
        analyzer = AuditAnalyzer(data_dir=self.test_dir)
        
        # Generate diverse test data
        test_scenarios = [
            # Normal operations
            (AuditEventType.USER_LOGIN, AuditEventCategory.SECURITY, AuditEventSeverity.INFO, True),
            (AuditEventType.DATA_READ, AuditEventCategory.DATA, AuditEventSeverity.LOW, True),
            (AuditEventType.API_REQUEST, AuditEventCategory.API, AuditEventSeverity.INFO, True),
            
            # Security incidents
            (AuditEventType.SECURITY_LOGIN_FAIL, AuditEventCategory.SECURITY, AuditEventSeverity.MEDIUM, False),
            (AuditEventType.SECURITY_ACCESS_DENIED, AuditEventCategory.SECURITY, AuditEventSeverity.HIGH, False),
            
            # System errors
            (AuditEventType.SYSTEM_CONFIG_CHANGE, AuditEventCategory.SYSTEM, AuditEventSeverity.HIGH, False),
        ]
        
        for event_type, category, severity, success in test_scenarios:
            event = AuditEvent(
                event_type=event_type,
                category=category,
                severity=severity,
                title=f"Test {event_type.value}",
                description="Test event for compliance reporting"
            )
            
            if not success:
                event.set_error("TEST_ERROR", "Test error message", 400)
            else:
                event.set_success(200)
            
            logger.log_event(event)
        
        # Generate compliance report
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now() + timedelta(hours=1)
        
        report = analyzer.generate_compliance_report(start_date, end_date)
        
        assert report.total_events == len(test_scenarios)
        assert report.security_events > 0
        assert report.failed_operations > 0
        assert 0.0 <= report.compliance_score <= 1.0
        assert len(report.recommendations) >= 0
    
    def test_anomaly_detection_integration(self):
        """Test anomaly detection with realistic scenarios."""
        logger = AuditLogger(data_dir=self.test_dir)
        analyzer = AuditAnalyzer(data_dir=self.test_dir)
        
        # Generate normal activity
        for i in range(10):
            event = AuditEvent(
                event_type=AuditEventType.API_REQUEST,
                category=AuditEventCategory.API,
                severity=AuditEventSeverity.INFO,
                title=f"Normal API Request {i}",
                operation="read"
            )
            event.context.user_id = "normal_user"
            event.context.ip_address = "127.0.0.1"
            logger.log_event(event)
        
        # Generate anomalous activity - high frequency from single user
        for i in range(150):  # Exceeds threshold of 100
            event = AuditEvent(
                event_type=AuditEventType.API_REQUEST,
                category=AuditEventCategory.API,
                severity=AuditEventSeverity.INFO,
                title=f"High Frequency Request {i}",
                operation="read"
            )
            event.context.user_id = "suspicious_user"
            event.context.ip_address = "192.168.1.100"
            logger.log_event(event)
        
        # Generate failed login attempts
        for i in range(10):  # Exceeds threshold of 5
            event = AuditEvent(
                event_type=AuditEventType.SECURITY_LOGIN_FAIL,
                category=AuditEventCategory.SECURITY,
                severity=AuditEventSeverity.MEDIUM,
                title=f"Failed Login {i}",
                operation="login"
            )
            event.context.username = "attacker"
            event.context.ip_address = "10.0.0.1"
            logger.log_event(event)
        
        # Detect anomalies
        anomalies = analyzer.detect_anomalies(hours=1)
        
        # Should detect high frequency user and failed login spike
        assert len(anomalies) >= 2
        
        anomaly_types = [a.anomaly_type for a in anomalies]
        assert "high_frequency_user" in anomaly_types
        assert "failed_login_spike" in anomaly_types
    
    def test_export_integration(self):
        """Test export functionality integration."""
        logger = AuditLogger(data_dir=self.test_dir)
        
        # Generate test data
        for i in range(5):
            event = AuditEvent(
                event_type=AuditEventType.DATA_EXPORT,
                category=AuditEventCategory.DATA,
                severity=AuditEventSeverity.MEDIUM,
                title=f"Export Event {i}",
                description="Test export event"
            )
            event.context.user_id = f"user_{i}"
            logger.log_event(event)
        
        # Test JSON export
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now() + timedelta(hours=1)
        
        json_export = logger.export_events(
            start_date=start_date,
            end_date=end_date,
            format='json'
        )
        
        assert json_export is not None
        assert "Export Event" in json_export
        
        # Test CSV export
        csv_export = logger.export_events(
            start_date=start_date,
            end_date=end_date,
            format='csv'
        )
        
        assert csv_export is not None
        assert "timestamp" in csv_export  # CSV header
        assert "Export Event" in csv_export
    
    def test_retention_policy_integration(self):
        """Test retention policy enforcement."""
        logger = AuditLogger(data_dir=self.test_dir)
        
        # Create an event with short retention
        event = AuditEvent(
            event_type=AuditEventType.USER_ACTION,
            category=AuditEventCategory.USER,
            severity=AuditEventSeverity.INFO,
            title="Short Retention Event",
            retention_days=1  # Very short for testing
        )
        
        # Manually set old timestamp
        event.timestamp = datetime.now() - timedelta(days=2)
        logger.log_event(event)
        
        # Create a current event
        current_event = AuditEvent(
            event_type=AuditEventType.USER_ACTION,
            category=AuditEventCategory.USER,
            severity=AuditEventSeverity.INFO,
            title="Current Event"
        )
        logger.log_event(current_event)
        
        # Verify both events exist
        all_events = logger.search_events(limit=10)
        assert len(all_events) == 2
        
        # Run cleanup
        deleted_count = logger.cleanup_old_events()
        assert deleted_count >= 1
        
        # Verify old event was removed
        remaining_events = logger.search_events(limit=10)
        remaining_titles = [e.title for e in remaining_events]
        assert "Current Event" in remaining_titles
    
    def test_performance_under_load(self):
        """Test system performance under moderate load."""
        logger = AuditLogger(data_dir=self.test_dir)
        analyzer = AuditAnalyzer(data_dir=self.test_dir)
        
        # Generate load
        start_time = time.time()
        event_count = 100
        
        for i in range(event_count):
            event = AuditEvent(
                event_type=AuditEventType.API_REQUEST,
                category=AuditEventCategory.API,
                severity=AuditEventSeverity.INFO,
                title=f"Load Test Event {i}",
                description="Performance testing event"
            )
            event.context.user_id = f"load_user_{i % 10}"
            event.context.ip_address = f"192.168.1.{i % 255}"
            logger.log_event(event)
        
        logging_time = time.time() - start_time
        
        # Test search performance
        search_start = time.time()
        events = logger.search_events(limit=50)
        search_time = time.time() - search_start
        
        # Test analysis performance
        analysis_start = time.time()
        summary = analyzer.get_analytics_summary()
        analysis_time = time.time() - analysis_start
        
        # Verify results
        assert len(events) == 50  # Limited by search limit
        assert summary['total_events_30d'] == event_count
        
        # Performance assertions (reasonable thresholds)
        assert logging_time < 10.0  # Should log 100 events in < 10 seconds
        assert search_time < 2.0    # Should search in < 2 seconds
        assert analysis_time < 5.0  # Should analyze in < 5 seconds
        
        print(f"Performance metrics:")
        print(f"  Logging {event_count} events: {logging_time:.2f}s")
        print(f"  Searching events: {search_time:.2f}s")
        print(f"  Analysis: {analysis_time:.2f}s")
    
    def test_concurrent_access(self):
        """Test concurrent access to monitoring components."""
        logger = AuditLogger(data_dir=self.test_dir)
        
        def worker_function(worker_id):
            """Worker function for concurrent testing."""
            for i in range(10):
                event = AuditEvent(
                    event_type=AuditEventType.USER_ACTION,
                    category=AuditEventCategory.USER,
                    severity=AuditEventSeverity.INFO,
                    title=f"Concurrent Event W{worker_id}-{i}",
                    description=f"Event from worker {worker_id}"
                )
                event.context.user_id = f"worker_{worker_id}"
                logger.log_event(event)
        
        # Create multiple threads
        threads = []
        num_workers = 5
        
        for worker_id in range(num_workers):
            thread = threading.Thread(target=worker_function, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all events were logged
        events = logger.search_events(limit=100)
        assert len(events) == num_workers * 10
        
        # Verify events from all workers
        worker_events = {}
        for event in events:
            user_id = event.context.user_id
            if user_id not in worker_events:
                worker_events[user_id] = 0
            worker_events[user_id] += 1
        
        assert len(worker_events) == num_workers
        for count in worker_events.values():
            assert count == 10
    
    def test_error_handling_integration(self):
        """Test error handling across components."""
        # Test with invalid data directory
        with pytest.raises(Exception):
            # This should handle the error gracefully
            logger = AuditLogger(data_dir="/invalid/path/that/does/not/exist")
        
        # Test with valid logger but problematic events
        logger = AuditLogger(data_dir=self.test_dir)
        
        # Log event with problematic data
        event = AuditEvent(
            event_type=AuditEventType.USER_ACTION,
            category=AuditEventCategory.USER,
            severity=AuditEventSeverity.INFO,
            title="Test Error Handling",
            description="Event with edge case data"
        )
        
        # Add problematic metadata
        event.metadata = {
            'large_data': 'x' * 10000,  # Large string
            'none_value': None,
            'nested_dict': {'deep': {'very': {'deep': 'value'}}}
        }
        
        # Should handle gracefully
        logger.log_event(event)
        
        # Verify event was still logged
        events = logger.search_events(limit=1)
        assert len(events) == 1
        assert events[0].title == "Test Error Handling"
    
    def test_full_system_workflow(self):
        """Test complete workflow from event creation to analysis."""
        # Initialize all components
        logger = AuditLogger(data_dir=self.test_dir)
        analyzer = AuditAnalyzer(data_dir=self.test_dir)
        api_key_manager = APIKeyManager(data_dir=self.test_dir)
        
        # Simulate a complete user workflow
        
        # 1. User creates API key
        api_key, key_string = api_key_manager.create_api_key(
            name="Integration Test Key",
            scopes={APIKeyScope.READ_WRITE},
            permissions={APIKeyPermission.MANAGE_DASHBOARDS}
        )
        
        # 2. User performs various operations
        operations = [
            (AuditEventType.USER_LOGIN, "User login"),
            (AuditEventType.DASHBOARD_VIEW, "Dashboard access"),
            (AuditEventType.DATA_READ, "Data query"),
            (AuditEventType.DATA_EXPORT, "Data export"),
            (AuditEventType.USER_LOGOUT, "User logout")
        ]
        
        for event_type, description in operations:
            event = AuditEvent(
                event_type=event_type,
                category=AuditEventCategory.USER,
                severity=AuditEventSeverity.INFO,
                title=description,
                description=f"Integration test: {description}"
            )
            event.context.user_id = "integration_test_user"
            event.context.ip_address = "127.0.0.1"
            event.context.session_id = "test_session_123"
            logger.log_event(event)
        
        # 3. Analyze the complete workflow
        events = logger.search_events(
            user_id="integration_test_user",
            limit=20
        )
        
        # Should have events from API key creation + user operations
        assert len(events) >= len(operations)
        
        # 4. Generate analytics
        summary = analyzer.get_analytics_summary()
        assert summary['total_events_30d'] >= len(operations)
        
        # 5. Test compliance report
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now() + timedelta(hours=1)
        
        report = analyzer.generate_compliance_report(start_date, end_date)
        assert report.total_events >= len(operations)
        assert report.compliance_score > 0.0
        
        # 6. Test event export
        export_data = logger.export_events(
            start_date=start_date,
            end_date=end_date,
            format='json'
        )
        
        assert "integration_test_user" in export_data
        assert "Dashboard access" in export_data
        
        print("✅ Full system workflow test completed successfully")


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])