"""
Widget renderer for displaying dashboard widgets in layouts.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
import uuid

from .widget_registry import get_widget_registry
from .base_widget import WidgetConfig
from ..layout.models import DashboardLayout, DashboardTab, DashboardWidget, WidgetType, WidgetSize
from ..layout.layout_manager import get_layout_manager


class WidgetRenderer:
    """
    Renders dashboard widgets in a layout-aware manner.
    """
    
    def __init__(self):
        """Initialize widget renderer."""
        self.widget_registry = get_widget_registry()
        self.layout_manager = get_layout_manager()
    
    def render_widget(self, dashboard_widget: DashboardWidget) -> None:
        """
        Render a single widget.
        
        Args:
            dashboard_widget: Widget configuration to render
        """
        try:
            # Create widget instance
            widget = self.widget_registry.create_widget_from_dashboard_widget(dashboard_widget)
            
            if widget:
                # Render the widget
                widget.render()
            else:
                st.error(f"Unknown widget type: {dashboard_widget.widget_type.value}")
                
        except Exception as e:
            st.error(f"Error rendering widget '{dashboard_widget.title}': {str(e)}")
    
    def render_tab(self, tab: DashboardTab, layout_id: Optional[str] = None) -> None:
        """
        Render all widgets in a tab.
        
        Args:
            tab: Tab to render
            layout_id: Optional layout ID for context
        """
        if not tab.visible:
            return
        
        visible_widgets = [w for w in tab.widgets if w.visible]
        
        if not visible_widgets:
            st.info(f"No widgets to display in '{tab.name}' tab")
            return
        
        # Group widgets by row for grid layout
        widget_grid = self._organize_widgets_by_grid(visible_widgets, tab.grid_columns)
        
        # Render widgets in grid
        self._render_widget_grid(widget_grid, tab.grid_columns)
    
    def render_layout(self, layout: DashboardLayout) -> None:
        """
        Render a complete dashboard layout.
        
        Args:
            layout: Layout to render
        """
        visible_tabs = layout.get_visible_tabs()
        
        if not visible_tabs:
            st.info("No tabs to display in this layout")
            return
        
        # Create tabs
        tab_names = [f"{tab.icon} {tab.name}" for tab in visible_tabs]
        streamlit_tabs = st.tabs(tab_names)
        
        # Render each tab
        for i, tab in enumerate(visible_tabs):
            with streamlit_tabs[i]:
                self.render_tab(tab, layout.layout_id)
    
    def render_widget_by_id(self, layout_id: str, tab_id: str, widget_id: str) -> None:
        """
        Render a specific widget by its ID.
        
        Args:
            layout_id: Layout ID
            tab_id: Tab ID
            widget_id: Widget ID
        """
        layout = self.layout_manager.get_layout(layout_id)
        if not layout:
            st.error("Layout not found")
            return
        
        tab = layout.get_tab(tab_id)
        if not tab:
            st.error("Tab not found")
            return
        
        widget = tab.get_widget(widget_id)
        if not widget:
            st.error("Widget not found")
            return
        
        self.render_widget(widget)
    
    def _organize_widgets_by_grid(self, widgets: List[DashboardWidget], grid_columns: int) -> Dict[int, List[DashboardWidget]]:
        """
        Organize widgets by their grid positions.
        
        Args:
            widgets: List of widgets to organize
            grid_columns: Number of grid columns
            
        Returns:
            Dictionary with row numbers as keys and widget lists as values
        """
        widget_grid = {}
        
        # Sort widgets by row, then column
        sorted_widgets = sorted(widgets, key=lambda w: (w.row, w.column))
        
        for widget in sorted_widgets:
            row = widget.row
            if row not in widget_grid:
                widget_grid[row] = []
            widget_grid[row].append(widget)
        
        return widget_grid
    
    def _render_widget_grid(self, widget_grid: Dict[int, List[DashboardWidget]], grid_columns: int) -> None:
        """
        Render widgets in a grid layout.
        
        Args:
            widget_grid: Dictionary with row numbers and widget lists
            grid_columns: Number of grid columns
        """
        for row_num in sorted(widget_grid.keys()):
            row_widgets = widget_grid[row_num]
            
            # Calculate column widths based on widget sizes
            column_specs = self._calculate_column_specs(row_widgets, grid_columns)
            
            if column_specs:
                cols = st.columns(column_specs)
                
                for i, widget in enumerate(row_widgets):
                    if i < len(cols):
                        with cols[i]:
                            self.render_widget(widget)
            else:
                # Fallback: render widgets in a single column
                for widget in row_widgets:
                    self.render_widget(widget)
    
    def _calculate_column_specs(self, widgets: List[DashboardWidget], grid_columns: int) -> List[int]:
        """
        Calculate column specifications for widget layout.
        
        Args:
            widgets: List of widgets in the row
            grid_columns: Total number of grid columns
            
        Returns:
            List of column width ratios
        """
        if not widgets:
            return []
        
        # Simple approach: equal width columns based on widget count
        # More sophisticated sizing could be implemented based on widget.width
        column_count = min(len(widgets), grid_columns)
        
        # Adjust for widget sizes
        column_specs = []
        for widget in widgets[:column_count]:
            if widget.size == WidgetSize.SMALL:
                column_specs.append(1)
            elif widget.size == WidgetSize.MEDIUM:
                column_specs.append(2)
            elif widget.size == WidgetSize.LARGE:
                column_specs.append(3)
            elif widget.size == WidgetSize.WIDE:
                column_specs.append(4)
            elif widget.size == WidgetSize.FULL:
                column_specs.append(6)
            else:
                column_specs.append(2)  # Default
        
        return column_specs
    
    def render_widget_library_preview(self) -> None:
        """Render a preview of all available widget types."""
        st.markdown("### Widget Library Preview")
        
        widgets_by_category = self.widget_registry.get_widgets_by_category()
        
        for category, widgets in widgets_by_category.items():
            st.markdown(f"#### {category} Widgets")
            
            cols = st.columns(min(3, len(widgets)))
            
            for i, widget_info in enumerate(widgets):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"**{widget_info['widget_icon']} {widget_info['widget_name']}**")
                        st.caption(widget_info['widget_description'])
                        
                        # Create sample widget
                        sample_config = WidgetConfig(
                            widget_id=str(uuid.uuid4()),
                            widget_type=WidgetType(widget_info['widget_type']),
                            title=f"Sample {widget_info['widget_name']}",
                            size=WidgetSize(widget_info['default_size'])
                        )
                        
                        if st.button(f"Preview", key=f"preview_{widget_info['widget_type']}"):
                            sample_widget = self.widget_registry.create_widget(sample_config)
                            if sample_widget:
                                with st.expander(f"Preview: {widget_info['widget_name']}", expanded=True):
                                    sample_widget.render()
    
    def render_widget_configurator(self, widget_type: WidgetType, widget_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Render widget configuration interface.
        
        Args:
            widget_type: Type of widget to configure
            widget_id: Optional existing widget ID
            
        Returns:
            Configuration values or None if cancelled
        """
        widget_class = self.widget_registry.get_widget_class(widget_type)
        if not widget_class:
            st.error(f"Unknown widget type: {widget_type.value}")
            return None
        
        st.markdown(f"### Configure {widget_class.widget_name}")
        st.caption(widget_class.widget_description)
        
        # Create sample widget for configuration
        sample_config = WidgetConfig(
            widget_id=widget_id or str(uuid.uuid4()),
            widget_type=widget_type,
            title=f"New {widget_class.widget_name}",
            size=widget_class.default_size
        )
        
        sample_widget = widget_class(sample_config)
        
        # Get configuration UI
        config_values = sample_widget.get_config_ui()
        
        # Configuration actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Configuration", type="primary"):
                return config_values
        
        with col2:
            if st.button("👁️ Preview"):
                # Update widget with new configuration
                sample_widget.update_config(config_values)
                with st.expander("Widget Preview", expanded=True):
                    sample_widget.render()
        
        with col3:
            if st.button("❌ Cancel"):
                return None
        
        return None
    
    def get_widget_library_info(self) -> Dict[str, Any]:
        """
        Get information about the widget library.
        
        Returns:
            Dictionary with widget library statistics and information
        """
        return {
            'registry_stats': self.widget_registry.get_registry_stats(),
            'available_widgets': self.widget_registry.get_available_widgets(),
            'widgets_by_category': self.widget_registry.get_widgets_by_category()
        }


# Global renderer instance
_widget_renderer = None


def get_widget_renderer() -> WidgetRenderer:
    """
    Get the global widget renderer instance.
    
    Returns:
        Global widget renderer instance
    """
    global _widget_renderer
    if _widget_renderer is None:
        _widget_renderer = WidgetRenderer()
    return _widget_renderer