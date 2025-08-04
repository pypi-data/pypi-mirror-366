"""
Integration tests for the security system components.
"""

import os
import sys
import pytest
import tempfile
import shutil
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import security components
from vector_db_query.monitoring.security.api_key_manager import APIKeyManager, get_api_key_manager
from vector_db_query.monitoring.security.api_key_models import (
    APIKey, APIKeyStatus, APIKeyScope, APIKeyPermission, APIKeyUsageStats, APIKeyRateLimit
)
from vector_db_query.monitoring.security.security_audit import SecurityAuditor, get_security_auditor
from vector_db_query.monitoring.audit.audit_logger import AuditLogger
from vector_db_query.monitoring.audit.audit_models import AuditEventType, AuditEventCategory, AuditEventSeverity


class TestSecurityIntegration:
    """Integration tests for security system components."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up clean test environment for each test."""
        self.test_dir = tempfile.mkdtemp()
        yield
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_api_key_lifecycle_integration(self):
        """Test complete API key lifecycle with audit integration."""
        api_key_manager = APIKeyManager(data_dir=self.test_dir)
        audit_logger = AuditLogger(data_dir=self.test_dir)
        
        # 1. Create API key
        api_key, key_string = api_key_manager.create_api_key(
            name="Integration Test Key",
            description="Test key for integration testing",
            scopes={APIKeyScope.READ_WRITE, APIKeyScope.ADMIN},
            permissions={APIKeyPermission.MANAGE_DASHBOARDS, APIKeyPermission.VIEW_ANALYTICS},
            expires_days=30,
            rate_limit_per_minute=100,
            rate_limit_per_hour=1000,
            rate_limit_per_day=10000,
            allowed_ips=["127.0.0.1", "192.168.1.0/24"]
        )
        
        assert api_key is not None
        assert key_string is not None
        assert len(key_string) == 64  # SHA-256 produces 64 character hex string
        
        # Verify audit event was created
        create_events = audit_logger.search_events(
            event_types=[AuditEventType.API_KEY_CREATE],
            limit=10
        )
        assert len(create_events) >= 1
        create_event = create_events[0]
        assert create_event.target_id == api_key.key_id
        
        # 2. Authenticate API key
        authenticated_key = api_key_manager.authenticate_key(
            key_string,
            ip_address="127.0.0.1",
            origin="http://localhost:3000"
        )
        
        assert authenticated_key is not None
        assert authenticated_key.key_id == api_key.key_id
        assert authenticated_key.status == APIKeyStatus.ACTIVE
        
        # 3. Use API key (simulate usage)
        for i in range(5):
            api_key_manager.record_usage(
                api_key.key_id,
                endpoint=f"/api/v1/test/{i}",
                method="GET",
                status_code=200,
                response_size=1024 + i * 100,
                duration_ms=50 + i * 10
            )
        
        # 4. Check usage statistics
        usage_stats = api_key_manager.get_usage_stats(api_key.key_id)
        assert usage_stats is not None
        assert usage_stats.total_requests == 5
        assert usage_stats.total_bytes > 0
        
        # 5. Test rate limiting
        current_limits = api_key_manager.check_rate_limits(api_key.key_id)
        assert current_limits['per_minute']['remaining'] < 100  # Should have decreased
        
        # 6. Update API key
        updated_key = api_key_manager.update_api_key(
            api_key.key_id,
            name="Updated Integration Test Key",
            description="Updated description"
        )
        
        assert updated_key.name == "Updated Integration Test Key"
        
        # Verify update audit event
        update_events = audit_logger.search_events(
            event_types=[AuditEventType.API_KEY_UPDATE],
            limit=10
        )
        assert len(update_events) >= 1
        
        # 7. Revoke API key
        revoked_key = api_key_manager.revoke_api_key(api_key.key_id, reason="Integration test completed")
        
        assert revoked_key.status == APIKeyStatus.REVOKED
        assert revoked_key.revoked_at is not None
        assert revoked_key.revocation_reason == "Integration test completed"
        
        # 8. Verify revoked key cannot be authenticated
        revoked_auth = api_key_manager.authenticate_key(
            key_string,
            ip_address="127.0.0.1"
        )
        
        assert revoked_auth is None
        
        # Verify revocation audit event
        revoke_events = audit_logger.search_events(
            event_types=[AuditEventType.API_KEY_REVOKE],
            limit=10
        )
        assert len(revoke_events) >= 1
    
    def test_security_audit_integration(self):
        """Test security auditor integration with monitoring system."""
        security_auditor = SecurityAuditor(data_dir=self.test_dir)
        audit_logger = AuditLogger(data_dir=self.test_dir)
        
        # Generate various security events
        security_scenarios = [
            {
                'event_type': AuditEventType.SECURITY_LOGIN_FAIL,
                'message': 'Failed login attempt',
                'severity': AuditEventSeverity.MEDIUM,
                'user_id': 'test_user',
                'ip_address': '192.168.1.100',
                'user_agent': 'TestAgent/1.0'
            },
            {
                'event_type': AuditEventType.SECURITY_ACCESS_DENIED,
                'message': 'Access denied to restricted resource',
                'severity': AuditEventSeverity.HIGH,
                'user_id': 'unauthorized_user',
                'ip_address': '10.0.0.1',
                'resource': '/admin/users'
            },
            {
                'event_type': AuditEventType.SECURITY_BREACH_ATTEMPT,
                'message': 'Potential security breach detected',
                'severity': AuditEventSeverity.CRITICAL,
                'ip_address': '172.16.0.1',
                'attack_type': 'SQL_INJECTION'
            }
        ]
        
        # Log security events
        for scenario in security_scenarios:
            security_auditor.log_security_event(**scenario)
        
        # Verify events were logged in audit system
        security_events = audit_logger.search_events(
            categories=[AuditEventCategory.SECURITY],
            limit=10
        )
        
        assert len(security_events) >= len(security_scenarios)
        
        # Check specific event types
        login_fails = [e for e in security_events if e.event_type == AuditEventType.SECURITY_LOGIN_FAIL]
        assert len(login_fails) >= 1
        assert login_fails[0].context.ip_address == '192.168.1.100'
        
        # Test IP blocking functionality
        suspicious_ip = '10.0.0.1'
        
        # Generate multiple suspicious events from same IP
        for i in range(6):  # Exceed threshold
            security_auditor.log_security_event(
                event_type=AuditEventType.SECURITY_ACCESS_DENIED,
                message=f'Suspicious activity #{i+1}',
                severity=AuditEventSeverity.HIGH,
                ip_address=suspicious_ip
            )
        
        # Check if IP was blocked
        security_stats = security_auditor.get_security_statistics()
        blocked_ips = security_stats.get('blocked_ips', [])
        
        # Verify IP tracking
        ip_events = audit_logger.search_events(
            ip_address=suspicious_ip,
            limit=20
        )
        assert len(ip_events) >= 6
    
    def test_permission_system_integration(self):
        """Test permission system with real operations."""
        api_key_manager = APIKeyManager(data_dir=self.test_dir)
        
        # Create keys with different permission levels
        
        # 1. Read-only key
        readonly_key, readonly_string = api_key_manager.create_api_key(
            name="Read Only Key",
            scopes={APIKeyScope.READ_ONLY},
            permissions={APIKeyPermission.VIEW_DASHBOARDS, APIKeyPermission.VIEW_ANALYTICS}
        )
        
        # 2. Read-write key
        readwrite_key, readwrite_string = api_key_manager.create_api_key(
            name="Read Write Key",
            scopes={APIKeyScope.READ_WRITE},
            permissions={
                APIKeyPermission.VIEW_DASHBOARDS,
                APIKeyPermission.MANAGE_DASHBOARDS,
                APIKeyPermission.VIEW_ANALYTICS
            }
        )
        
        # 3. Admin key
        admin_key, admin_string = api_key_manager.create_api_key(
            name="Admin Key",
            scopes={APIKeyScope.ADMIN},
            permissions={
                APIKeyPermission.VIEW_DASHBOARDS,
                APIKeyPermission.MANAGE_DASHBOARDS,
                APIKeyPermission.VIEW_ANALYTICS,
                APIKeyPermission.MANAGE_USERS,
                APIKeyPermission.SYSTEM_CONFIG
            }
        )
        
        # Test permission checking
        
        # Read-only key tests
        assert readonly_key.has_permission(APIKeyPermission.VIEW_DASHBOARDS)
        assert not readonly_key.has_permission(APIKeyPermission.MANAGE_DASHBOARDS)
        assert not readonly_key.has_permission(APIKeyPermission.MANAGE_USERS)
        
        # Read-write key tests
        assert readwrite_key.has_permission(APIKeyPermission.VIEW_DASHBOARDS)
        assert readwrite_key.has_permission(APIKeyPermission.MANAGE_DASHBOARDS)
        assert not readwrite_key.has_permission(APIKeyPermission.MANAGE_USERS)
        
        # Admin key tests
        assert admin_key.has_permission(APIKeyPermission.VIEW_DASHBOARDS)
        assert admin_key.has_permission(APIKeyPermission.MANAGE_DASHBOARDS)
        assert admin_key.has_permission(APIKeyPermission.MANAGE_USERS)
        assert admin_key.has_permission(APIKeyPermission.SYSTEM_CONFIG)
        
        # Test scope checking
        assert readonly_key.has_scope(APIKeyScope.READ_ONLY)
        assert not readonly_key.has_scope(APIKeyScope.READ_WRITE)
        
        assert readwrite_key.has_scope(APIKeyScope.READ_WRITE)
        assert not readwrite_key.has_scope(APIKeyScope.ADMIN)
        
        assert admin_key.has_scope(APIKeyScope.ADMIN)
    
    def test_rate_limiting_integration(self):
        """Test rate limiting system with real usage patterns."""
        api_key_manager = APIKeyManager(data_dir=self.test_dir)
        
        # Create key with strict rate limits
        api_key, key_string = api_key_manager.create_api_key(
            name="Rate Limited Key",
            rate_limit_per_minute=5,
            rate_limit_per_hour=20,
            rate_limit_per_day=100
        )
        
        # Test normal usage within limits
        for i in range(3):
            api_key_manager.record_usage(
                api_key.key_id,
                endpoint="/api/v1/test",
                method="GET",
                status_code=200
            )
        
        # Check limits - should still have remaining
        limits = api_key_manager.check_rate_limits(api_key.key_id)
        assert limits['per_minute']['remaining'] == 2
        assert limits['per_hour']['remaining'] == 17
        assert limits['per_day']['remaining'] == 97
        
        # Exceed per-minute limit
        for i in range(3):  # Total will be 6, exceeding limit of 5
            api_key_manager.record_usage(
                api_key.key_id,
                endpoint="/api/v1/test",
                method="GET",
                status_code=200
            )
        
        # Check limits - per-minute should be exceeded
        limits = api_key_manager.check_rate_limits(api_key.key_id)
        assert limits['per_minute']['exceeded'] is True
        assert limits['per_minute']['remaining'] == 0
        
        # Hour and day limits should still be OK
        assert limits['per_hour']['exceeded'] is False
        assert limits['per_day']['exceeded'] is False
        
        # Test rate limit reset (simulate time passage)
        # In real implementation, this would happen automatically
        # For testing, we can directly manipulate the rate limit data
        
        usage_stats = api_key_manager.get_usage_stats(api_key.key_id)
        assert usage_stats.total_requests == 6
    
    def test_ip_restriction_integration(self):
        """Test IP restriction functionality."""
        api_key_manager = APIKeyManager(data_dir=self.test_dir)
        security_auditor = SecurityAuditor(data_dir=self.test_dir)
        
        # Create key with IP restrictions
        api_key, key_string = api_key_manager.create_api_key(
            name="IP Restricted Key",
            allowed_ips=["127.0.0.1", "192.168.1.0/24"]
        )
        
        # Test authentication from allowed IP
        allowed_auth = api_key_manager.authenticate_key(
            key_string,
            ip_address="127.0.0.1"
        )
        assert allowed_auth is not None
        
        # Test authentication from allowed subnet
        subnet_auth = api_key_manager.authenticate_key(
            key_string,
            ip_address="192.168.1.100"
        )
        assert subnet_auth is not None
        
        # Test authentication from disallowed IP
        disallowed_auth = api_key_manager.authenticate_key(
            key_string,
            ip_address="10.0.0.1"
        )
        assert disallowed_auth is None
        
        # Verify security event was logged for disallowed IP
        time.sleep(0.1)  # Brief delay to ensure event is logged
        
        security_events = security_auditor.audit_logger.search_events(
            event_types=[AuditEventType.SECURITY_ACCESS_DENIED],
            ip_address="10.0.0.1",
            limit=10
        )
        
        # Should have at least one access denied event
        assert len(security_events) >= 1
    
    def test_security_analytics_integration(self):
        """Test security analytics and reporting."""
        api_key_manager = APIKeyManager(data_dir=self.test_dir)
        security_auditor = SecurityAuditor(data_dir=self.test_dir)
        
        # Create multiple API keys
        keys = []
        for i in range(3):
            api_key, key_string = api_key_manager.create_api_key(
                name=f"Analytics Test Key {i}",
                scopes={APIKeyScope.READ_WRITE}
            )
            keys.append((api_key, key_string))
        
        # Generate usage patterns
        for i, (api_key, key_string) in enumerate(keys):
            # Different usage patterns for each key
            requests_count = (i + 1) * 10
            
            for j in range(requests_count):
                api_key_manager.record_usage(
                    api_key.key_id,
                    endpoint=f"/api/v1/endpoint_{j % 3}",
                    method="GET",
                    status_code=200 if j % 4 != 0 else 400,  # Some failures
                    response_size=1000 + j * 50,
                    duration_ms=100 + j * 5
                )
        
        # Generate security events
        security_events = [
            (AuditEventType.SECURITY_LOGIN_FAIL, AuditEventSeverity.MEDIUM, "192.168.1.100"),
            (AuditEventType.SECURITY_LOGIN_FAIL, AuditEventSeverity.MEDIUM, "192.168.1.100"),
            (AuditEventType.SECURITY_ACCESS_DENIED, AuditEventSeverity.HIGH, "10.0.0.1"),
            (AuditEventType.SECURITY_BREACH_ATTEMPT, AuditEventSeverity.CRITICAL, "172.16.0.1")
        ]
        
        for event_type, severity, ip_address in security_events:
            security_auditor.log_security_event(
                event_type=event_type,
                message=f"Test security event: {event_type.value}",
                severity=severity,
                ip_address=ip_address
            )
        
        # Get comprehensive analytics
        security_stats = security_auditor.get_security_statistics()
        
        # Verify basic statistics
        assert 'total_events' in security_stats
        assert 'events_by_severity' in security_stats
        assert 'events_by_type' in security_stats
        assert 'top_ips' in security_stats
        
        # Verify API key analytics
        all_keys = api_key_manager.list_api_keys()
        assert len(all_keys) == 3
        
        # Check individual key statistics
        for api_key, _ in keys:
            stats = api_key_manager.get_usage_stats(api_key.key_id)
            assert stats.total_requests > 0
            assert stats.total_bytes > 0
            
            # Check that error rate is calculated
            if stats.failed_requests > 0:
                assert stats.error_rate > 0
    
    def test_security_cleanup_integration(self):
        """Test security data cleanup and maintenance."""
        api_key_manager = APIKeyManager(data_dir=self.test_dir)
        security_auditor = SecurityAuditor(data_dir=self.test_dir)
        
        # Create expired API key
        expired_key, expired_string = api_key_manager.create_api_key(
            name="Expired Key",
            expires_days=-1  # Already expired
        )
        
        # Create active key
        active_key, active_string = api_key_manager.create_api_key(
            name="Active Key",
            expires_days=30
        )
        
        # Generate old security events
        old_time = datetime.now() - timedelta(days=400)  # Very old
        
        # Create event with old timestamp (would need direct database manipulation in real scenario)
        security_auditor.log_security_event(
            event_type=AuditEventType.SECURITY_LOGIN_FAIL,
            message="Old security event",
            severity=AuditEventSeverity.LOW
        )
        
        # Test cleanup operations
        
        # 1. Cleanup expired keys
        cleanup_stats = api_key_manager.cleanup_expired_keys()
        assert 'expired_keys' in cleanup_stats
        
        # 2. Cleanup old audit events
        deleted_count = security_auditor.audit_logger.cleanup_old_events()
        assert isinstance(deleted_count, int)
        
        # Verify active key still exists
        active_keys = [k for k in api_key_manager.list_api_keys() if k.status == APIKeyStatus.ACTIVE]
        active_key_ids = [k.key_id for k in active_keys]
        assert active_key.key_id in active_key_ids
    
    def test_concurrent_security_operations(self):
        """Test concurrent security operations."""
        import threading
        
        api_key_manager = APIKeyManager(data_dir=self.test_dir)
        
        # Create API key for concurrent testing
        api_key, key_string = api_key_manager.create_api_key(
            name="Concurrent Test Key",
            rate_limit_per_minute=1000  # High limit for testing
        )
        
        results = {'success': 0, 'failed': 0}
        
        def concurrent_usage_worker(worker_id):
            """Worker function for concurrent API usage."""
            try:
                for i in range(10):
                    # Authenticate key
                    auth_result = api_key_manager.authenticate_key(
                        key_string,
                        ip_address="127.0.0.1"
                    )
                    
                    if auth_result:
                        # Record usage
                        api_key_manager.record_usage(
                            api_key.key_id,
                            endpoint=f"/api/worker/{worker_id}/{i}",
                            method="GET",
                            status_code=200,
                            response_size=1024,
                            duration_ms=50
                        )
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                results['failed'] += 1
        
        # Create multiple threads
        threads = []
        num_workers = 5
        
        for worker_id in range(num_workers):
            thread = threading.Thread(
                target=concurrent_usage_worker,
                args=(worker_id,)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify results
        total_expected = num_workers * 10
        total_actual = results['success'] + results['failed']
        
        assert total_actual == total_expected
        assert results['success'] > 0  # At least some should succeed
        
        # Verify usage statistics
        final_stats = api_key_manager.get_usage_stats(api_key.key_id)
        assert final_stats.total_requests == results['success']
    
    def test_full_security_workflow(self):
        """Test complete security workflow from key creation to analytics."""
        # Initialize all components
        api_key_manager = APIKeyManager(data_dir=self.test_dir)
        security_auditor = SecurityAuditor(data_dir=self.test_dir)
        audit_logger = AuditLogger(data_dir=self.test_dir)
        
        # 1. Create API key with comprehensive configuration
        api_key, key_string = api_key_manager.create_api_key(
            name="Workflow Test Key",
            description="Complete workflow test",
            scopes={APIKeyScope.READ_WRITE, APIKeyScope.ADMIN},
            permissions={
                APIKeyPermission.VIEW_DASHBOARDS,
                APIKeyPermission.MANAGE_DASHBOARDS,
                APIKeyPermission.VIEW_ANALYTICS,
                APIKeyPermission.MANAGE_USERS
            },
            expires_days=30,
            rate_limit_per_minute=100,
            rate_limit_per_hour=1000,
            allowed_ips=["127.0.0.1", "192.168.1.0/24"],
            allowed_origins=["http://localhost:3000", "https://dashboard.example.com"]
        )
        
        # 2. Simulate normal API usage
        normal_operations = [
            ("/api/v1/dashboards", "GET", 200),
            ("/api/v1/dashboards", "POST", 201),
            ("/api/v1/analytics/metrics", "GET", 200),
            ("/api/v1/users", "GET", 200),
            ("/api/v1/dashboards/123", "PUT", 200)
        ]
        
        for endpoint, method, status in normal_operations:
            # Authenticate key
            auth_result = api_key_manager.authenticate_key(
                key_string,
                ip_address="127.0.0.1",
                origin="http://localhost:3000"
            )
            assert auth_result is not None
            
            # Record usage
            api_key_manager.record_usage(
                api_key.key_id,
                endpoint=endpoint,
                method=method,
                status_code=status,
                response_size=2048,
                duration_ms=150
            )
        
        # 3. Simulate security incidents
        security_incidents = [
            # Failed authentications from suspicious IP
            ("10.0.0.1", AuditEventType.SECURITY_ACCESS_DENIED, "Unauthorized IP"),
            ("10.0.0.1", AuditEventType.SECURITY_ACCESS_DENIED, "Repeated unauthorized access"),
            
            # Suspicious activity
            ("172.16.0.1", AuditEventType.SECURITY_BREACH_ATTEMPT, "SQL injection attempt"),
            
            # Failed login attempts
            ("192.168.1.200", AuditEventType.SECURITY_LOGIN_FAIL, "Invalid credentials")
        ]
        
        for ip_address, event_type, message in security_incidents:
            security_auditor.log_security_event(
                event_type=event_type,
                message=message,
                severity=AuditEventSeverity.HIGH,
                ip_address=ip_address
            )
        
        # 4. Analyze security posture
        security_stats = security_auditor.get_security_statistics()
        
        assert security_stats['total_events'] >= len(security_incidents)
        assert 'events_by_severity' in security_stats
        assert 'top_ips' in security_stats
        
        # 5. Analyze API key usage
        usage_stats = api_key_manager.get_usage_stats(api_key.key_id)
        
        assert usage_stats.total_requests == len(normal_operations)
        assert usage_stats.success_rate == 1.0  # All operations were successful
        assert usage_stats.avg_response_time > 0
        assert usage_stats.total_bytes > 0
        
        # 6. Check rate limits
        current_limits = api_key_manager.check_rate_limits(api_key.key_id)
        
        assert current_limits['per_minute']['remaining'] < 100
        assert not current_limits['per_minute']['exceeded']
        
        # 7. Generate comprehensive audit report
        all_events = audit_logger.search_events(limit=100)
        
        # Should have events from API key creation, usage, and security incidents
        event_types = [e.event_type for e in all_events]
        
        assert AuditEventType.API_KEY_CREATE in event_types
        assert AuditEventType.API_KEY_USE in event_types
        assert AuditEventType.SECURITY_ACCESS_DENIED in event_types
        
        # 8. Test export functionality
        export_data = audit_logger.export_events(
            start_date=datetime.now() - timedelta(hours=1),
            end_date=datetime.now() + timedelta(hours=1),
            format='json'
        )
        
        assert "Workflow Test Key" in export_data
        assert "security" in export_data.lower()
        assert "10.0.0.1" in export_data
        
        print("✅ Full security workflow test completed successfully")
        print(f"   API Key: {api_key.name} ({api_key.key_id})")
        print(f"   Normal operations: {len(normal_operations)}")
        print(f"   Security incidents: {len(security_incidents)}")
        print(f"   Total audit events: {len(all_events)}")
        print(f"   Usage success rate: {usage_stats.success_rate:.1%}")


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])