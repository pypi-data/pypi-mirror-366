"""
Pytest configuration and shared fixtures for monitoring system tests.
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data that persists for the session."""
    temp_dir = tempfile.mkdtemp(prefix="monitoring_tests_")
    yield temp_dir
    # Cleanup after all tests
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def clean_test_dir():
    """Create a clean temporary directory for each test."""
    temp_dir = tempfile.mkdtemp(prefix="test_")
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_audit_events():
    """Generate sample audit events for testing."""
    from vector_db_query.monitoring.audit.audit_models import (
        AuditEvent, AuditEventType, AuditEventCategory, AuditEventSeverity, AuditEventContext
    )
    from datetime import datetime, timedelta
    
    events = []
    base_time = datetime.now() - timedelta(hours=1)
    
    # Generate a variety of test events
    event_scenarios = [
        (AuditEventType.USER_LOGIN, AuditEventCategory.SECURITY, AuditEventSeverity.INFO, "user1", "127.0.0.1"),
        (AuditEventType.DASHBOARD_VIEW, AuditEventCategory.DASHBOARD, AuditEventSeverity.INFO, "user1", "127.0.0.1"),
        (AuditEventType.API_REQUEST, AuditEventCategory.API, AuditEventSeverity.INFO, "user2", "192.168.1.100"),
        (AuditEventType.DATA_EXPORT, AuditEventCategory.DATA, AuditEventSeverity.MEDIUM, "user2", "192.168.1.100"),
        (AuditEventType.SECURITY_LOGIN_FAIL, AuditEventCategory.SECURITY, AuditEventSeverity.MEDIUM, None, "10.0.0.1"),
        (AuditEventType.SYSTEM_CONFIG_CHANGE, AuditEventCategory.SYSTEM, AuditEventSeverity.HIGH, "admin", "127.0.0.1"),
    ]
    
    for i, (event_type, category, severity, user_id, ip_address) in enumerate(event_scenarios):
        event = AuditEvent(
            event_type=event_type,
            category=category,
            severity=severity,
            title=f"Test {event_type.value}",
            description=f"Test event {i+1} for integration testing",
            timestamp=base_time + timedelta(minutes=i*5)
        )
        
        event.context = AuditEventContext(
            user_id=user_id,
            ip_address=ip_address,
            session_id=f"session_{i+1}" if user_id else None
        )
        
        events.append(event)
    
    return events


@pytest.fixture
def sample_api_keys():
    """Generate sample API keys for testing."""
    from vector_db_query.monitoring.security.api_key_models import (
        APIKey, APIKeyScope, APIKeyPermission, APIKeyStatus
    )
    
    keys = []
    
    # Read-only key
    readonly_key = APIKey(
        key_id="readonly_key_001",
        name="Read Only Test Key",
        description="Test key with read-only permissions",
        scopes={APIKeyScope.READ_ONLY},
        permissions={APIKeyPermission.VIEW_DASHBOARDS, APIKeyPermission.VIEW_ANALYTICS},
        status=APIKeyStatus.ACTIVE
    )
    readonly_key.set_key("test_readonly_key_string")
    keys.append(readonly_key)
    
    # Read-write key
    readwrite_key = APIKey(
        key_id="readwrite_key_001",
        name="Read Write Test Key",
        description="Test key with read-write permissions",
        scopes={APIKeyScope.READ_WRITE},
        permissions={
            APIKeyPermission.VIEW_DASHBOARDS,
            APIKeyPermission.MANAGE_DASHBOARDS,
            APIKeyPermission.VIEW_ANALYTICS
        },
        status=APIKeyStatus.ACTIVE,
        rate_limit_per_minute=100,
        rate_limit_per_hour=1000
    )
    readwrite_key.set_key("test_readwrite_key_string")
    keys.append(readwrite_key)
    
    # Admin key
    admin_key = APIKey(
        key_id="admin_key_001",
        name="Admin Test Key",
        description="Test key with admin permissions",
        scopes={APIKeyScope.ADMIN},
        permissions={
            APIKeyPermission.VIEW_DASHBOARDS,
            APIKeyPermission.MANAGE_DASHBOARDS,
            APIKeyPermission.VIEW_ANALYTICS,
            APIKeyPermission.MANAGE_USERS,
            APIKeyPermission.SYSTEM_CONFIG
        },
        status=APIKeyStatus.ACTIVE,
        allowed_ips=["127.0.0.1", "192.168.1.0/24"]
    )
    admin_key.set_key("test_admin_key_string")
    keys.append(admin_key)
    
    return keys


@pytest.fixture
def sample_dashboard_layout():
    """Generate sample dashboard layout for testing."""
    from vector_db_query.monitoring.widgets.widget_models import (
        DashboardLayout, DashboardTab, DashboardWidget
    )
    
    # Create widgets
    widgets = [
        DashboardWidget(
            widget_id="system_overview_1",
            widget_type="system_overview",
            title="System Overview",
            position=(0, 0),
            size=(6, 4),
            config={
                'show_cpu': True,
                'show_memory': True,
                'show_disk': True,
                'refresh_interval': 30
            }
        ),
        DashboardWidget(
            widget_id="metrics_chart_1",
            widget_type="metrics_chart",
            title="Performance Metrics",
            position=(6, 0),
            size=(6, 4),
            config={
                'chart_type': 'line',
                'metrics': ['cpu_usage', 'memory_usage'],
                'time_range': '1hour'
            }
        ),
        DashboardWidget(
            widget_id="event_stream_1",
            widget_type="event_stream",
            title="Recent Events",
            position=(0, 4),
            size=(12, 3),
            config={
                'event_types': ['security', 'system'],
                'limit': 20
            }
        )
    ]
    
    # Create tab
    tab = DashboardTab(
        tab_id="main_tab",
        name="Main Dashboard",
        widgets=widgets
    )
    
    # Create layout
    layout = DashboardLayout(
        layout_id="test_layout_001",
        name="Test Dashboard Layout",
        description="Sample layout for integration testing",
        tabs=[tab],
        custom_settings={
            'theme': 'light',
            'auto_refresh': True,
            'refresh_interval': 60
        }
    )
    
    return layout


@pytest.fixture
def mock_system_metrics():
    """Generate mock system metrics for testing."""
    import random
    from datetime import datetime, timedelta
    
    metrics = []
    base_time = datetime.now() - timedelta(hours=2)
    
    for i in range(120):  # 2 hours of minute-by-minute data
        timestamp = base_time + timedelta(minutes=i)
        
        # Generate realistic-looking metrics with some variation
        cpu_base = 45 + random.gauss(0, 10)
        memory_base = 65 + random.gauss(0, 8)
        disk_base = 75 + random.gauss(0, 5)
        
        metric = {
            'timestamp': timestamp,
            'cpu_usage': max(0, min(100, cpu_base)),
            'memory_usage': max(0, min(100, memory_base)),
            'disk_usage': max(0, min(100, disk_base)),
            'network_in': random.randint(1000, 5000),
            'network_out': random.randint(500, 2000),
            'active_connections': random.randint(10, 50)
        }
        
        metrics.append(metric)
    
    return metrics


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances before each test to ensure clean state."""
    # Import and reset all singleton managers
    try:
        from vector_db_query.monitoring.audit.audit_logger import reset_audit_logger
        from vector_db_query.monitoring.audit.audit_analyzer import reset_audit_analyzer
        from vector_db_query.monitoring.history.change_tracker import reset_change_tracker
        
        reset_audit_logger()
        reset_audit_analyzer()
        reset_change_tracker()
    except ImportError:
        # Some modules might not be available in all test contexts
        pass
    
    yield
    
    # Reset again after test
    try:
        reset_audit_logger()
        reset_audit_analyzer()
        reset_change_tracker()
    except ImportError:
        pass


@pytest.fixture
def integration_test_environment(clean_test_dir, sample_audit_events, sample_api_keys):
    """Set up complete integration test environment."""
    from vector_db_query.monitoring.audit.audit_logger import AuditLogger
    from vector_db_query.monitoring.security.api_key_manager import APIKeyManager
    from vector_db_query.monitoring.widgets.layout_manager import LayoutManager
    
    # Initialize components with test directory
    audit_logger = AuditLogger(data_dir=clean_test_dir)
    api_key_manager = APIKeyManager(data_dir=clean_test_dir)
    layout_manager = LayoutManager(data_dir=clean_test_dir)
    
    # Populate with sample data
    for event in sample_audit_events:
        audit_logger.log_event(event)
    
    # Return environment dictionary
    return {
        'test_dir': clean_test_dir,
        'audit_logger': audit_logger,
        'api_key_manager': api_key_manager,
        'layout_manager': layout_manager,
        'sample_events': sample_audit_events,
        'sample_keys': sample_api_keys
    }


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security-related"
    )
    config.addinivalue_line(
        "markers", "dashboard: mark test as dashboard-related"
    )
    config.addinivalue_line(
        "markers", "audit: mark test as audit-related"
    )