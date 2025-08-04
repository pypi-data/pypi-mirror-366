"""
Dashboard Widget Library

This module provides reusable dashboard widgets for the monitoring system.
Each widget is designed to be modular and configurable for different use cases.
"""

from .base_widget import BaseWidget, WidgetConfig
from .system_widgets import (
    SystemOverviewWidget,
    ProcessControlWidget,
    QueueStatusWidget
)
from .analytics_widgets import (
    MetricsChartWidget,
    PerformanceGraphWidget
)
from .monitoring_widgets import (
    EventStreamWidget,
    NotificationPanelWidget,
    ConnectionStatusWidget
)
from .utility_widgets import (
    LogViewerWidget,
    CustomHTMLWidget
)
from .widget_registry import WidgetRegistry, get_widget_registry
from .widget_renderer import WidgetRenderer, get_widget_renderer

__all__ = [
    # Base classes
    'BaseWidget', 'WidgetConfig',
    
    # System widgets
    'SystemOverviewWidget', 'ProcessControlWidget', 'QueueStatusWidget',
    
    # Analytics widgets  
    'MetricsChartWidget', 'PerformanceGraphWidget',
    
    # Monitoring widgets
    'EventStreamWidget', 'NotificationPanelWidget', 'ConnectionStatusWidget',
    
    # Utility widgets
    'LogViewerWidget', 'CustomHTMLWidget',
    
    # Registry and Renderer
    'WidgetRegistry', 'get_widget_registry',
    'WidgetRenderer', 'get_widget_renderer'
]

__version__ = '1.0.0'