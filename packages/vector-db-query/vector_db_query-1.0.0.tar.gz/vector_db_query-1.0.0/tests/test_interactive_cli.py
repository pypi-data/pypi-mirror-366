"""Tests for interactive CLI components."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.vector_db_query.cli.interactive import (
    InteractiveMenu, MenuBuilder, MenuItem,
    FileBrowser, FileInfo,
    QueryBuilder, QueryTemplate,
    ResultViewer, SearchResult,
    PreferencesManager, UserPreferences,
    UsageAnalytics, SmartSuggestions
)


class TestMenuSystem:
    """Test menu system functionality."""
    
    def test_menu_builder(self):
        """Test menu builder."""
        builder = MenuBuilder()
        
        # Create menu
        menu = builder.create_menu("main", "Main Menu")
        assert menu.name == "main"
        assert menu.title == "Main Menu"
        
        # Add items
        builder.add_item(
            "main", "option1", "Option 1",
            handler=lambda: print("Option 1"),
            description="First option"
        )
        
        builder.add_separator("main")
        
        builder.add_item(
            "main", "option2", "Option 2",
            handler=lambda: print("Option 2"),
            submenu_name="submenu"
        )
        
        items = menu.items
        assert len(items) == 3
        assert items[0].name == "option1"
        assert items[1].is_separator
        assert items[2].has_submenu
    
    @patch('questionary.select')
    def test_menu_navigation(self, mock_select):
        """Test menu navigation."""
        mock_select.return_value.ask.return_value = "option1"
        
        builder = MenuBuilder()
        menu = builder.create_menu("test", "Test Menu")
        
        handler_called = False
        def test_handler():
            nonlocal handler_called
            handler_called = True
        
        builder.add_item("test", "option1", "Option 1", handler=test_handler)
        
        result = menu.show()
        assert result == "option1"
        assert handler_called


class TestFileBrowser:
    """Test file browser functionality."""
    
    def test_file_browser_init(self):
        """Test file browser initialization."""
        browser = FileBrowser(
            filters=[".txt", ".md"],
            allow_multiple=True,
            preview_enabled=True
        )
        
        assert browser.filters == [".txt", ".md"]
        assert browser.allow_multiple is True
        assert browser.preview_enabled is True
    
    @patch('questionary.path')
    def test_browse_single_file(self, mock_path, temp_dir):
        """Test browsing single file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")
        
        mock_path.return_value.ask.return_value = str(test_file)
        
        browser = FileBrowser()
        result = browser.browse()
        
        assert len(result) == 1
        assert result[0] == test_file
    
    def test_file_preview(self, temp_dir):
        """Test file preview generation."""
        test_file = temp_dir / "test.txt"
        content = "\n".join([f"Line {i}" for i in range(100)])
        test_file.write_text(content)
        
        browser = FileBrowser(preview_enabled=True, max_preview_lines=10)
        preview = browser._generate_preview(test_file)
        
        assert "Line 0" in preview
        assert "Line 9" in preview
        assert "..." in preview  # Truncation indicator
        assert "Line 99" not in preview


class TestQueryBuilder:
    """Test query builder functionality."""
    
    @patch('questionary.text')
    def test_build_simple_query(self, mock_text):
        """Test building simple query."""
        mock_text.return_value.ask.return_value = "test query"
        
        builder = QueryBuilder()
        query = builder.build_query()
        
        assert query == "test query"
    
    def test_query_templates(self):
        """Test query templates."""
        builder = QueryBuilder()
        
        # Add template
        template = QueryTemplate(
            name="Find by topic",
            template="Find documents about {topic}",
            variables=["topic"]
        )
        builder.add_template(template)
        
        templates = builder.get_templates()
        assert len(templates) == 1
        assert templates[0].name == "Find by topic"
    
    def test_query_history(self):
        """Test query history."""
        builder = QueryBuilder()
        
        # Add queries to history
        builder.add_to_history("query 1")
        builder.add_to_history("query 2")
        builder.add_to_history("query 1")  # Duplicate
        
        history = builder.get_history()
        assert len(history) == 2  # No duplicates
        assert history[0] == "query 1"
        assert history[1] == "query 2"


class TestResultViewer:
    """Test result viewer functionality."""
    
    def test_result_viewer_init(self):
        """Test result viewer initialization."""
        results = [
            SearchResult(
                id="1",
                content="Result 1",
                score=0.95,
                metadata={"source": "file1.txt"}
            ),
            SearchResult(
                id="2",
                content="Result 2",
                score=0.85,
                metadata={"source": "file2.txt"}
            )
        ]
        
        viewer = ResultViewer(
            results=results,
            query="test query",
            page_size=10
        )
        
        assert len(viewer.results) == 2
        assert viewer.query == "test query"
        assert viewer.page_size == 10
    
    @patch('questionary.select')
    def test_display_results(self, mock_select):
        """Test displaying results."""
        results = [
            SearchResult(
                id="1",
                content="Test result content",
                score=0.95,
                metadata={"source": "test.txt"}
            )
        ]
        
        mock_select.return_value.ask.return_value = results[0]
        
        viewer = ResultViewer(results=results, query="test")
        selected = viewer.display()
        
        assert selected == results[0]


class TestPreferences:
    """Test preferences management."""
    
    def test_preferences_manager(self, temp_dir):
        """Test preferences manager."""
        prefs_file = temp_dir / "preferences.json"
        manager = PreferencesManager(prefs_file)
        
        # Get default preferences
        prefs = manager.get_preferences()
        assert isinstance(prefs, UserPreferences)
        assert prefs.theme == "monokai"  # Default
        
        # Update preference
        manager.set_preference("theme", "dracula")
        assert manager.get_preference("theme") == "dracula"
        
        # Save and reload
        manager.save()
        new_manager = PreferencesManager(prefs_file)
        assert new_manager.get_preference("theme") == "dracula"
    
    def test_preference_validation(self, temp_dir):
        """Test preference validation."""
        manager = PreferencesManager(temp_dir / "prefs.json")
        
        # Valid preference
        manager.set_preference("page_size", 50)
        assert manager.get_preference("page_size") == 50
        
        # Invalid preference (should use default)
        manager.set_preference("page_size", -1)
        assert manager.get_preference("page_size") == 20  # Default


class TestAnalytics:
    """Test usage analytics."""
    
    def test_usage_analytics(self, temp_dir):
        """Test usage analytics tracking."""
        analytics_file = temp_dir / "analytics.json"
        analytics = UsageAnalytics(analytics_file)
        
        # Track actions
        analytics.track_action("process_documents", {"count": 5})
        analytics.track_action("query_database", {"query": "test"})
        
        # Track error
        analytics.track_error("Connection failed", {"service": "vector_db"})
        
        # Save session
        analytics.save_session()
        
        # Get insights
        insights = analytics.get_insights()
        assert insights["total_sessions"] == 1
        assert insights["total_actions"] == 2
        assert insights["total_errors"] == 1
    
    def test_smart_suggestions(self):
        """Test smart suggestions."""
        analytics = Mock()
        analytics.get_insights.return_value = {
            "total_sessions": 10,
            "most_common_actions": [
                ("process_documents", 20),
                ("query_database", 15)
            ]
        }
        
        suggestions = SmartSuggestions(analytics)
        
        # Get contextual suggestions
        suggs = suggestions.get_suggestions("after_processing")
        assert len(suggs) > 0
        assert any("query" in s.lower() for s in suggs)
        
        # Get error suggestion
        error_sugg = suggestions.get_error_suggestion("API key not found")
        assert error_sugg is not None
        assert "API key" in error_sugg


class TestPolishFeatures:
    """Test polish and optimization features."""
    
    def test_performance_monitor(self):
        """Test performance monitoring."""
        from src.vector_db_query.cli.interactive.optimization import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        monitor.enabled = True
        
        @monitor.measure("test_operation")
        def slow_operation():
            import time
            time.sleep(0.1)
            return "done"
        
        result = slow_operation()
        assert result == "done"
        
        # Check metrics
        report = monitor.report()
        assert "test_operation" in report
        assert report["test_operation"]["count"] == 1
        assert report["test_operation"]["average"] >= 0.1
    
    def test_cache_manager(self):
        """Test caching functionality."""
        from src.vector_db_query.cli.interactive.optimization import CacheManager
        
        manager = CacheManager()
        
        call_count = 0
        @manager.cached("test_cache")
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = expensive_operation(5)
        assert result1 == 10
        assert call_count == 1
        
        # Cached call
        result2 = expensive_operation(5)
        assert result2 == 10
        assert call_count == 1  # Not called again
        
        # Different argument
        result3 = expensive_operation(3)
        assert result3 == 6
        assert call_count == 2