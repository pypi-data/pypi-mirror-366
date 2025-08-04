"""
Customizable dashboard layout management module.

This module provides comprehensive tools for creating, customizing,
and managing dashboard layouts with drag-and-drop widgets.
"""

from .models import (
    LayoutType, WidgetType, WidgetSize,
    DashboardWidget, DashboardTab, DashboardLayout,
    LayoutTemplate, LayoutChange
)
from .layout_manager import LayoutManager, get_layout_manager, reset_layout_manager
from .layout_ui import CustomizableDashboardUI

__all__ = [
    # Enums
    'LayoutType', 'WidgetType', 'WidgetSize',
    # Models
    'DashboardWidget', 'DashboardTab', 'DashboardLayout',
    'LayoutTemplate', 'LayoutChange',
    # Services
    'LayoutManager', 'get_layout_manager', 'reset_layout_manager',
    # UI
    'CustomizableDashboardUI'
]

__version__ = '1.0.0'