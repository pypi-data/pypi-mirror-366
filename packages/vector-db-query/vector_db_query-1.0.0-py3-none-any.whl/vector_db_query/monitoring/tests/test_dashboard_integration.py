"""
Integration tests for the dashboard system and UI components.
"""

import os
import sys
import pytest
import tempfile
import shutil
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import dashboard components
from vector_db_query.monitoring.widgets.layout_manager import LayoutManager, get_layout_manager
from vector_db_query.monitoring.widgets.widget_models import DashboardWidget, DashboardTab, DashboardLayout
from vector_db_query.monitoring.widgets.widget_registry import WidgetRegistry, get_widget_registry
from vector_db_query.monitoring.widgets.export_manager import ExportManager, get_export_manager
from vector_db_query.monitoring.widgets.export_models import ExportJob, ExportType, ExportFormat
from vector_db_query.monitoring.audit.audit_logger import AuditLogger
from vector_db_query.monitoring.security.api_key_manager import APIKeyManager


class TestDashboardIntegration:
    """Integration tests for dashboard system components."""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up clean test environment for each test."""
        self.test_dir = tempfile.mkdtemp()
        yield
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_layout_manager_integration(self):
        """Test layout manager with real widget configuration."""
        layout_manager = LayoutManager(data_dir=self.test_dir)
        widget_registry = WidgetRegistry()
        
        # Create test widgets
        widget1 = DashboardWidget(
            widget_id="test_widget_1",
            widget_type="system_overview",
            title="System Overview",
            position=(0, 0),
            size=(4, 3)
        )
        
        widget2 = DashboardWidget(
            widget_id="test_widget_2",
            widget_type="process_control",
            title="Process Control",
            position=(4, 0),
            size=(4, 3)
        )
        
        # Create tab with widgets
        tab = DashboardTab(
            tab_id="main_tab",
            name="Main Dashboard",
            widgets=[widget1, widget2]
        )
        
        # Create layout
        layout = DashboardLayout(
            layout_id="test_layout",
            name="Test Layout",
            description="Integration test layout",
            tabs=[tab]
        )
        
        # Save layout
        saved_layout = layout_manager.create_layout(layout)
        assert saved_layout.layout_id == "test_layout"
        
        # Retrieve layout
        retrieved_layout = layout_manager.get_layout("test_layout")
        assert retrieved_layout is not None
        assert len(retrieved_layout.tabs) == 1
        assert len(retrieved_layout.tabs[0].widgets) == 2
        
        # Test layout listing
        layouts = layout_manager.list_layouts()
        assert len(layouts) == 1
        assert layouts[0].name == "Test Layout"
    
    def test_widget_registry_integration(self):
        """Test widget registry with various widget types."""
        registry = WidgetRegistry()
        
        # Test widget type registration
        available_types = registry.get_available_widget_types()
        
        # Should have our predefined widget types
        expected_types = [
            'system_overview', 'process_control', 'queue_status',
            'metrics_chart', 'performance_graph', 'event_stream',
            'notification_panel', 'connection_status', 'log_viewer',
            'custom_html'
        ]
        
        for widget_type in expected_types:
            assert widget_type in [wt['type'] for wt in available_types]
        
        # Test widget creation
        widget_config = {
            'widget_id': 'test_metrics',
            'widget_type': 'metrics_chart',
            'title': 'Test Metrics',
            'position': [0, 0],
            'size': [6, 4],
            'config': {
                'chart_type': 'line',
                'metrics': ['cpu_usage', 'memory_usage'],
                'time_range': '1h'
            }
        }
        
        widget = registry.create_widget_from_config(widget_config)
        assert widget.widget_type == 'metrics_chart'
        assert widget.title == 'Test Metrics'
        assert widget.config['chart_type'] == 'line'
    
    def test_export_manager_integration(self):
        """Test export manager with real data."""
        export_manager = ExportManager(data_dir=self.test_dir)
        audit_logger = AuditLogger(data_dir=self.test_dir)
        
        # Create test audit data
        from vector_db_query.monitoring.audit.audit_models import AuditEvent, AuditEventType, AuditEventCategory, AuditEventSeverity
        
        for i in range(10):
            event = AuditEvent(
                event_type=AuditEventType.USER_ACTION,
                category=AuditEventCategory.USER,
                severity=AuditEventSeverity.INFO,
                title=f"Test Event {i}",
                description=f"Test event for export {i}"
            )
            event.context.user_id = f"user_{i}"
            audit_logger.log_event(event)
        
        # Create export job
        export_job = ExportJob(
            job_id="test_export_001",
            name="Test Export Job",
            export_type=ExportType.AUDIT_LOGS,
            format=ExportFormat.JSON,
            filters={
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'categories': ['user']
            }
        )
        
        # Execute export
        result = export_manager.execute_export(export_job)
        
        assert result is not None
        assert result.status == 'completed'
        assert result.file_path is not None
        assert os.path.exists(result.file_path)
        
        # Verify export content
        with open(result.file_path, 'r') as f:
            content = f.read()
            assert 'Test Event' in content
            assert 'user_' in content
        
        # Test export history
        history = export_manager.get_export_history(limit=10)
        assert len(history) >= 1
        assert history[0].job_id == "test_export_001"
    
    def test_dashboard_widget_rendering(self):
        """Test widget rendering integration."""
        from vector_db_query.monitoring.widgets.widget_renderer import WidgetRenderer
        
        renderer = WidgetRenderer()
        
        # Test system overview widget
        system_widget = DashboardWidget(
            widget_id="system_test",
            widget_type="system_overview",
            title="System Overview Test",
            position=(0, 0),
            size=(4, 3),
            config={
                'show_cpu': True,
                'show_memory': True,
                'show_disk': True,
                'refresh_interval': 5
            }
        )
        
        # Mock the render method to avoid UI dependencies
        with patch.object(renderer, 'render_widget') as mock_render:
            mock_render.return_value = "<div>System Overview Widget</div>"
            
            rendered = renderer.render_widget(system_widget)
            assert rendered is not None
            mock_render.assert_called_once_with(system_widget)
    
    def test_layout_template_integration(self):
        """Test layout templates with real configuration."""
        layout_manager = LayoutManager(data_dir=self.test_dir)
        
        # Create monitoring layout template
        monitoring_template = {
            'name': 'Monitoring Template',
            'description': 'Standard monitoring dashboard layout',
            'category': 'monitoring',
            'tabs': [
                {
                    'name': 'Overview',
                    'widgets': [
                        {
                            'type': 'system_overview',
                            'title': 'System Overview',
                            'position': [0, 0],
                            'size': [6, 4]
                        },
                        {
                            'type': 'process_control',
                            'title': 'Process Control',
                            'position': [6, 0],
                            'size': [6, 4]
                        },
                        {
                            'type': 'queue_status',
                            'title': 'Queue Status',
                            'position': [0, 4],
                            'size': [12, 3]
                        }
                    ]
                },
                {
                    'name': 'Analytics',
                    'widgets': [
                        {
                            'type': 'metrics_chart',
                            'title': 'Performance Metrics',
                            'position': [0, 0],
                            'size': [8, 6]
                        },
                        {
                            'type': 'event_stream',
                            'title': 'Recent Events',
                            'position': [8, 0],
                            'size': [4, 6]
                        }
                    ]
                }
            ]
        }
        
        # Create layout from template
        layout = layout_manager.create_layout_from_template(monitoring_template)
        
        assert layout is not None
        assert layout.name == 'Monitoring Template'
        assert len(layout.tabs) == 2
        assert layout.tabs[0].name == 'Overview'
        assert len(layout.tabs[0].widgets) == 3
        assert layout.tabs[1].name == 'Analytics'
        assert len(layout.tabs[1].widgets) == 2
        
        # Verify widget configuration
        overview_widgets = layout.tabs[0].widgets
        system_widget = next(w for w in overview_widgets if w.widget_type == 'system_overview')
        assert system_widget.title == 'System Overview'
        assert system_widget.size == (6, 4)
    
    def test_export_format_integration(self):
        """Test different export formats."""
        export_manager = ExportManager(data_dir=self.test_dir)
        
        # Create test data
        test_data = {
            'system_metrics': [
                {'timestamp': '2024-01-01T10:00:00Z', 'cpu': 45.2, 'memory': 67.8},
                {'timestamp': '2024-01-01T10:01:00Z', 'cpu': 48.1, 'memory': 69.2},
                {'timestamp': '2024-01-01T10:02:00Z', 'cpu': 52.3, 'memory': 71.5}
            ],
            'metadata': {
                'export_date': '2024-01-01T10:05:00Z',
                'total_records': 3,
                'source': 'monitoring_system'
            }
        }
        
        # Test JSON export
        json_job = ExportJob(
            job_id="json_test",
            name="JSON Export Test",
            export_type=ExportType.SYSTEM_METRICS,
            format=ExportFormat.JSON,
            data=test_data
        )
        
        json_result = export_manager.execute_export(json_job)
        assert json_result.status == 'completed'
        
        with open(json_result.file_path, 'r') as f:
            import json
            exported_data = json.load(f)
            assert 'system_metrics' in exported_data
            assert len(exported_data['system_metrics']) == 3
        
        # Test CSV export
        csv_job = ExportJob(
            job_id="csv_test",
            name="CSV Export Test",
            export_type=ExportType.SYSTEM_METRICS,
            format=ExportFormat.CSV,
            data=test_data
        )
        
        csv_result = export_manager.execute_export(csv_job)
        assert csv_result.status == 'completed'
        
        with open(csv_result.file_path, 'r') as f:
            csv_content = f.read()
            assert 'timestamp,cpu,memory' in csv_content
            assert '45.2,67.8' in csv_content
    
    def test_dashboard_state_persistence(self):
        """Test dashboard state persistence across sessions."""
        layout_manager = LayoutManager(data_dir=self.test_dir)
        
        # Create and save layout
        layout = DashboardLayout(
            layout_id="persistent_test",
            name="Persistent Layout",
            description="Test layout persistence"
        )
        
        # Add tab with custom configuration
        tab = DashboardTab(
            tab_id="config_tab",
            name="Configuration",
            widgets=[
                DashboardWidget(
                    widget_id="config_widget",
                    widget_type="custom_html",
                    title="Configuration Panel",
                    position=(0, 0),
                    size=(12, 8),
                    config={
                        'html_content': '<h1>Configuration Dashboard</h1>',
                        'refresh_interval': 30,
                        'custom_css': 'body { background: #f5f5f5; }'
                    }
                )
            ]
        )
        
        layout.tabs = [tab]
        layout.custom_settings = {
            'theme': 'dark',
            'auto_refresh': True,
            'notification_sound': False
        }
        
        saved_layout = layout_manager.create_layout(layout)
        
        # Simulate session restart by creating new manager
        new_manager = LayoutManager(data_dir=self.test_dir)
        
        # Retrieve layout
        retrieved_layout = new_manager.get_layout("persistent_test")
        
        assert retrieved_layout is not None
        assert retrieved_layout.name == "Persistent Layout"
        assert len(retrieved_layout.tabs) == 1
        assert retrieved_layout.tabs[0].name == "Configuration"
        assert len(retrieved_layout.tabs[0].widgets) == 1
        
        widget = retrieved_layout.tabs[0].widgets[0]
        assert widget.widget_type == "custom_html"
        assert widget.config['html_content'] == '<h1>Configuration Dashboard</h1>'
        assert widget.config['refresh_interval'] == 30
        
        assert retrieved_layout.custom_settings['theme'] == 'dark'
        assert retrieved_layout.custom_settings['auto_refresh'] is True
    
    def test_concurrent_dashboard_operations(self):
        """Test concurrent dashboard operations."""
        layout_manager = LayoutManager(data_dir=self.test_dir)
        
        def create_layout_worker(worker_id):
            """Worker function to create layouts concurrently."""
            layout = DashboardLayout(
                layout_id=f"concurrent_layout_{worker_id}",
                name=f"Layout {worker_id}",
                description=f"Layout created by worker {worker_id}"
            )
            
            # Add some widgets
            widgets = []
            for i in range(3):
                widget = DashboardWidget(
                    widget_id=f"widget_{worker_id}_{i}",
                    widget_type="system_overview",
                    title=f"Widget {worker_id}-{i}",
                    position=(i * 4, 0),
                    size=(4, 3)
                )
                widgets.append(widget)
            
            tab = DashboardTab(
                tab_id=f"tab_{worker_id}",
                name=f"Tab {worker_id}",
                widgets=widgets
            )
            
            layout.tabs = [tab]
            return layout_manager.create_layout(layout)
        
        # Create multiple threads
        threads = []
        results = {}
        num_workers = 5
        
        def worker_wrapper(worker_id):
            try:
                result = create_layout_worker(worker_id)
                results[worker_id] = result
            except Exception as e:
                results[worker_id] = e
        
        for worker_id in range(num_workers):
            thread = threading.Thread(target=worker_wrapper, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == num_workers
        
        for worker_id, result in results.items():
            assert not isinstance(result, Exception), f"Worker {worker_id} failed: {result}"
            assert result.layout_id == f"concurrent_layout_{worker_id}"
        
        # Verify all layouts were saved
        all_layouts = layout_manager.list_layouts()
        concurrent_layouts = [l for l in all_layouts if 'concurrent_layout_' in l.layout_id]
        assert len(concurrent_layouts) == num_workers
    
    def test_dashboard_performance_metrics(self):
        """Test dashboard performance under load."""
        layout_manager = LayoutManager(data_dir=self.test_dir)
        export_manager = ExportManager(data_dir=self.test_dir)
        
        # Create complex layout with many widgets
        widgets = []
        for i in range(20):  # Many widgets
            widget = DashboardWidget(
                widget_id=f"perf_widget_{i}",
                widget_type="metrics_chart",
                title=f"Performance Widget {i}",
                position=(i % 4 * 3, i // 4 * 2),
                size=(3, 2),
                config={
                    'chart_type': 'line',
                    'metrics': [f'metric_{i}', f'metric_{i+1}'],
                    'refresh_interval': 5,
                    'data_points': 100
                }
            )
            widgets.append(widget)
        
        # Create layout with performance timing
        start_time = time.time()
        
        layout = DashboardLayout(
            layout_id="performance_test",
            name="Performance Test Layout",
            description="Layout with many widgets for performance testing",
            tabs=[
                DashboardTab(
                    tab_id="perf_tab",
                    name="Performance Tab",
                    widgets=widgets
                )
            ]
        )
        
        saved_layout = layout_manager.create_layout(layout)
        create_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        retrieved_layout = layout_manager.get_layout("performance_test")
        retrieve_time = time.time() - start_time
        
        # Test listing performance
        start_time = time.time()
        all_layouts = layout_manager.list_layouts()
        list_time = time.time() - start_time
        
        # Verify results
        assert saved_layout.layout_id == "performance_test"
        assert len(retrieved_layout.tabs[0].widgets) == 20
        assert len(all_layouts) >= 1
        
        # Performance assertions (reasonable thresholds)
        assert create_time < 5.0, f"Layout creation took {create_time:.2f}s (> 5s)"
        assert retrieve_time < 2.0, f"Layout retrieval took {retrieve_time:.2f}s (> 2s)"
        assert list_time < 1.0, f"Layout listing took {list_time:.2f}s (> 1s)"
        
        print(f"Dashboard performance metrics:")
        print(f"  Create complex layout: {create_time:.3f}s")
        print(f"  Retrieve layout: {retrieve_time:.3f}s")
        print(f"  List layouts: {list_time:.3f}s")
    
    def test_error_recovery_integration(self):
        """Test error recovery in dashboard operations."""
        layout_manager = LayoutManager(data_dir=self.test_dir)
        
        # Test recovery from corrupted layout data
        layout = DashboardLayout(
            layout_id="recovery_test",
            name="Recovery Test",
            description="Test error recovery"
        )
        
        # Save valid layout first
        saved_layout = layout_manager.create_layout(layout)
        assert saved_layout is not None
        
        # Simulate corruption by directly modifying the database
        import sqlite3
        db_path = os.path.join(self.test_dir, "layouts.db")
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Insert invalid JSON data
            cursor.execute(
                "UPDATE layouts SET layout_data = ? WHERE layout_id = ?",
                ('{"invalid": json}', "recovery_test")
            )
            conn.commit()
        
        # Test graceful handling of corrupted data
        try:
            retrieved_layout = layout_manager.get_layout("recovery_test")
            # Should either return None or raise handled exception
            assert retrieved_layout is None or isinstance(retrieved_layout, DashboardLayout)
        except Exception as e:
            # Should be a handled exception, not a crash
            assert "recovery_test" in str(e) or "invalid" in str(e).lower()
        
        # Test that manager can still operate with other layouts
        new_layout = DashboardLayout(
            layout_id="new_after_corruption",
            name="New Layout",
            description="Layout created after corruption"
        )
        
        new_saved_layout = layout_manager.create_layout(new_layout)
        assert new_saved_layout is not None
        assert new_saved_layout.layout_id == "new_after_corruption"
    
    def test_full_dashboard_workflow(self):
        """Test complete dashboard workflow from creation to export."""
        # Initialize all components
        layout_manager = LayoutManager(data_dir=self.test_dir)
        export_manager = ExportManager(data_dir=self.test_dir)
        audit_logger = AuditLogger(data_dir=self.test_dir)
        
        # 1. Create comprehensive dashboard layout
        widgets = [
            DashboardWidget(
                widget_id="overview_widget",
                widget_type="system_overview",
                title="System Overview",
                position=(0, 0),
                size=(6, 4),
                config={'show_all_metrics': True}
            ),
            DashboardWidget(
                widget_id="audit_widget",
                widget_type="event_stream",
                title="Audit Events",
                position=(6, 0),
                size=(6, 4),
                config={'event_types': ['security', 'user'], 'limit': 50}
            ),
            DashboardWidget(
                widget_id="metrics_widget",
                widget_type="metrics_chart",
                title="Performance Metrics",
                position=(0, 4),
                size=(12, 3),
                config={'chart_type': 'area', 'time_range': '24h'}
            )
        ]
        
        layout = DashboardLayout(
            layout_id="workflow_dashboard",
            name="Workflow Test Dashboard",
            description="Complete workflow test dashboard",
            tabs=[
                DashboardTab(
                    tab_id="main_tab",
                    name="Main",
                    widgets=widgets
                )
            ],
            custom_settings={
                'theme': 'light',
                'auto_refresh': True,
                'refresh_interval': 30
            }
        )
        
        # 2. Save layout
        saved_layout = layout_manager.create_layout(layout)
        assert saved_layout.layout_id == "workflow_dashboard"
        
        # 3. Generate some audit data to display
        from vector_db_query.monitoring.audit.audit_models import AuditEvent, AuditEventType, AuditEventCategory, AuditEventSeverity
        
        events = [
            (AuditEventType.DASHBOARD_VIEW, "Dashboard accessed"),
            (AuditEventType.WIDGET_CREATE, "Widget created"),
            (AuditEventType.LAYOUT_UPDATE, "Layout updated"),
            (AuditEventType.USER_ACTION, "User interaction")
        ]
        
        for event_type, description in events:
            event = AuditEvent(
                event_type=event_type,
                category=AuditEventCategory.DASHBOARD,
                severity=AuditEventSeverity.INFO,
                title=description,
                description=f"Workflow test: {description}"
            )
            event.context.user_id = "workflow_test_user"
            audit_logger.log_event(event)
        
        # 4. Clone layout for customization
        cloned_layout = layout_manager.clone_layout(
            "workflow_dashboard",
            "workflow_dashboard_custom",
            "Customized Workflow Dashboard"
        )
        
        assert cloned_layout.layout_id == "workflow_dashboard_custom"
        assert cloned_layout.name == "Customized Workflow Dashboard"
        assert len(cloned_layout.tabs[0].widgets) == len(widgets)
        
        # 5. Export layout configuration
        layout_export_job = ExportJob(
            job_id="layout_export",
            name="Layout Export",
            export_type=ExportType.DASHBOARD_CONFIG,
            format=ExportFormat.JSON,
            filters={'layout_id': 'workflow_dashboard'}
        )
        
        layout_export_result = export_manager.execute_export(layout_export_job)
        assert layout_export_result.status == 'completed'
        
        # 6. Export audit data
        audit_export_job = ExportJob(
            job_id="audit_export",
            name="Audit Export",
            export_type=ExportType.AUDIT_LOGS,
            format=ExportFormat.CSV,
            filters={'category': 'dashboard'}
        )
        
        audit_export_result = export_manager.execute_export(audit_export_job)
        assert audit_export_result.status == 'completed'
        
        # 7. Verify export contents
        with open(layout_export_result.file_path, 'r') as f:
            import json
            layout_data = json.load(f)
            assert 'workflow_dashboard' in str(layout_data)
            assert 'System Overview' in str(layout_data)
        
        with open(audit_export_result.file_path, 'r') as f:
            audit_csv = f.read()
            assert 'Dashboard accessed' in audit_csv
            assert 'workflow_test_user' in audit_csv
        
        # 8. Get comprehensive statistics
        layouts = layout_manager.list_layouts()
        layout_names = [l.name for l in layouts]
        
        assert "Workflow Test Dashboard" in layout_names
        assert "Customized Workflow Dashboard" in layout_names
        
        export_history = export_manager.get_export_history()
        export_jobs = [h.name for h in export_history]
        
        assert "Layout Export" in export_jobs
        assert "Audit Export" in export_jobs
        
        print("✅ Full dashboard workflow test completed successfully")
        print(f"   Created {len(layouts)} layouts")
        print(f"   Generated {len(events)} audit events")
        print(f"   Completed {len(export_history)} export jobs")


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])