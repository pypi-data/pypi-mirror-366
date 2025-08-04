"""
Widget registry for managing and creating dashboard widgets.
"""

from typing import Dict, Type, List, Any, Optional
from threading import RLock

from .base_widget import BaseWidget, WidgetConfig
from .system_widgets import SystemOverviewWidget, ProcessControlWidget, QueueStatusWidget
from .analytics_widgets import MetricsChartWidget, PerformanceGraphWidget
from .monitoring_widgets import EventStreamWidget, NotificationPanelWidget, ConnectionStatusWidget
from .utility_widgets import LogViewerWidget, CustomHTMLWidget
from ..layout.models import WidgetType, DashboardWidget


class WidgetRegistry:
    """
    Registry for managing dashboard widget types and creating widget instances.
    """
    
    def __init__(self):
        """Initialize widget registry."""
        self._lock = RLock()
        self._widget_classes: Dict[WidgetType, Type[BaseWidget]] = {}
        self._register_default_widgets()
    
    def _register_default_widgets(self) -> None:
        """Register default widget types."""
        # System widgets
        self.register_widget(SystemOverviewWidget)
        self.register_widget(ProcessControlWidget)
        self.register_widget(QueueStatusWidget)
        
        # Analytics widgets
        self.register_widget(MetricsChartWidget)
        self.register_widget(PerformanceGraphWidget)
        
        # Monitoring widgets
        self.register_widget(EventStreamWidget)
        self.register_widget(NotificationPanelWidget)
        self.register_widget(ConnectionStatusWidget)
        
        # Utility widgets
        self.register_widget(LogViewerWidget)  
        self.register_widget(CustomHTMLWidget)
    
    def register_widget(self, widget_class: Type[BaseWidget]) -> None:
        """
        Register a widget class.
        
        Args:
            widget_class: Widget class to register
        """
        with self._lock:
            if not issubclass(widget_class, BaseWidget):
                raise ValueError(f"Widget class {widget_class.__name__} must inherit from BaseWidget")
            
            widget_type = widget_class.widget_type
            self._widget_classes[widget_type] = widget_class
    
    def unregister_widget(self, widget_type: WidgetType) -> bool:
        """
        Unregister a widget type.
        
        Args:
            widget_type: Widget type to unregister
            
        Returns:
            True if widget was unregistered, False if not found
        """
        with self._lock:
            if widget_type in self._widget_classes:
                del self._widget_classes[widget_type]
                return True
            return False
    
    def get_widget_class(self, widget_type: WidgetType) -> Optional[Type[BaseWidget]]:
        """
        Get widget class for a given type.
        
        Args:
            widget_type: Widget type to get class for
            
        Returns:
            Widget class or None if not found
        """
        with self._lock:
            return self._widget_classes.get(widget_type)
    
    def create_widget(self, widget_config: WidgetConfig) -> Optional[BaseWidget]:
        """
        Create a widget instance from configuration.
        
        Args:
            widget_config: Widget configuration
            
        Returns:
            Widget instance or None if widget type not found
        """
        widget_class = self.get_widget_class(widget_config.widget_type)
        if widget_class:
            try:
                return widget_class(widget_config)
            except Exception as e:
                print(f"Error creating widget {widget_config.widget_type}: {e}")
                return None
        return None
    
    def create_widget_from_dashboard_widget(self, dashboard_widget: DashboardWidget) -> Optional[BaseWidget]:
        """
        Create a widget instance from DashboardWidget.
        
        Args:
            dashboard_widget: Dashboard widget configuration
            
        Returns:
            Widget instance or None if widget type not found
        """
        widget_config = WidgetConfig.from_dashboard_widget(dashboard_widget)
        return self.create_widget(widget_config)
    
    def get_available_widgets(self) -> List[Dict[str, Any]]:
        """
        Get list of available widget types and their metadata.
        
        Returns:
            List of widget metadata dictionaries
        """
        with self._lock:
            widgets = []
            for widget_type, widget_class in self._widget_classes.items():
                widgets.append(widget_class.get_widget_info())
            return sorted(widgets, key=lambda x: (x['widget_category'], x['widget_name']))
    
    def get_widgets_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get widgets grouped by category.
        
        Returns:
            Dictionary with categories as keys and widget lists as values
        """
        widgets = self.get_available_widgets()
        categories = {}
        
        for widget in widgets:
            category = widget['widget_category']
            if category not in categories:
                categories[category] = []
            categories[category].append(widget)
        
        return categories
    
    def search_widgets(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for widgets by name or description.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching widget metadata
        """
        search_term = search_term.lower()
        widgets = self.get_available_widgets()
        
        matching_widgets = []
        for widget in widgets:
            if (search_term in widget['widget_name'].lower() or
                search_term in widget['widget_description'].lower() or
                search_term in widget['widget_category'].lower()):
                matching_widgets.append(widget)
        
        return matching_widgets
    
    def get_widget_config_schema(self, widget_type: WidgetType) -> Dict[str, Any]:
        """
        Get configuration schema for a widget type.
        
        Args:
            widget_type: Widget type to get schema for
            
        Returns:
            Configuration schema or empty dict if not found
        """
        widget_class = self.get_widget_class(widget_type)
        if widget_class:
            return widget_class.config_schema
        return {}
    
    def validate_widget_config(self, widget_type: WidgetType, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate widget configuration against schema.
        
        Args:
            widget_type: Widget type to validate for
            config: Configuration to validate
            
        Returns:
            Dictionary with 'valid' boolean and 'errors' list
        """
        schema = self.get_widget_config_schema(widget_type)
        errors = []
        
        if not schema:
            return {'valid': True, 'errors': []}
        
        for key, schema_def in schema.items():
            if key in config:
                value = config[key]
                
                # Type validation
                if 'type' in schema_def:
                    expected_type = schema_def['type']
                    
                    if expected_type == 'boolean' and not isinstance(value, bool):
                        errors.append(f"'{key}' must be a boolean")
                    elif expected_type == 'number' and not isinstance(value, (int, float)):
                        errors.append(f"'{key}' must be a number")
                    elif expected_type == 'select' and value not in schema_def.get('options', []):
                        errors.append(f"'{key}' must be one of {schema_def.get('options', [])}")
                    elif expected_type == 'multiselect':
                        if not isinstance(value, list):
                            errors.append(f"'{key}' must be a list")
                        else:
                            valid_options = schema_def.get('options', [])
                            invalid_values = [v for v in value if v not in valid_options]
                            if invalid_values:
                                errors.append(f"'{key}' contains invalid values: {invalid_values}")
                
                # Range validation for numbers
                if expected_type == 'number' and isinstance(value, (int, float)):
                    if 'min' in schema_def and value < schema_def['min']:
                        errors.append(f"'{key}' must be >= {schema_def['min']}")
                    if 'max' in schema_def and value > schema_def['max']:
                        errors.append(f"'{key}' must be <= {schema_def['max']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with registry statistics
        """
        with self._lock:
            categories = self.get_widgets_by_category()
            
            return {
                'total_widgets': len(self._widget_classes),
                'categories': list(categories.keys()),
                'widgets_by_category': {cat: len(widgets) for cat, widgets in categories.items()},
                'widget_types': [wt.value for wt in self._widget_classes.keys()]
            }


# Global registry instance
_widget_registry = None
_registry_lock = RLock()


def get_widget_registry() -> WidgetRegistry:
    """
    Get the global widget registry instance (singleton).
    
    Returns:
        Global widget registry instance
    """
    global _widget_registry
    with _registry_lock:
        if _widget_registry is None:
            _widget_registry = WidgetRegistry()
        return _widget_registry


def reset_widget_registry() -> None:
    """Reset the global widget registry (mainly for testing)."""
    global _widget_registry
    with _registry_lock:
        _widget_registry = None