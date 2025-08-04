"""
Customizable dashboard layout UI component.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

from .layout_manager import get_layout_manager
from .models import (
    LayoutType, WidgetType, WidgetSize,
    DashboardLayout, DashboardTab, DashboardWidget,
    LayoutTemplate
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory
from ..widgets.widget_renderer import get_widget_renderer
from ..widgets.widget_registry import get_widget_registry


class CustomizableDashboardUI:
    """
    UI for customizing dashboard layouts.
    """
    
    def __init__(self):
        """Initialize customizable dashboard UI."""
        self.layout_manager = get_layout_manager()
        self.change_tracker = get_change_tracker()
        self.widget_renderer = get_widget_renderer()
        self.widget_registry = get_widget_registry()
        
        # Initialize session state
        if 'layout_selected_layout' not in st.session_state:
            st.session_state.layout_selected_layout = None
        if 'layout_edit_mode' not in st.session_state:
            st.session_state.layout_edit_mode = False
        if 'layout_show_preview' not in st.session_state:
            st.session_state.layout_show_preview = True
    
    def render(self):
        """Render the customizable dashboard UI."""
        st.header("🎨 Dashboard Layout Customization")
        
        # Layout selector
        self._render_layout_selector()
        
        # Tabs
        tabs = st.tabs([
            "🏠 My Layouts",
            "🛠️ Layout Editor", 
            "📋 Templates",
            "🎯 Widget Library",
            "📊 Preview",
            "📈 Analytics",
            "⚙️ Settings"
        ])
        
        with tabs[0]:
            self._render_my_layouts_tab()
        
        with tabs[1]:
            self._render_layout_editor_tab()
        
        with tabs[2]:
            self._render_templates_tab()
        
        with tabs[3]:
            self._render_widget_library_tab()
        
        with tabs[4]:
            self._render_preview_tab()
        
        with tabs[5]:
            self._render_analytics_tab()
        
        with tabs[6]:
            self._render_settings_tab()
    
    def _render_layout_selector(self):
        """Render layout selector."""
        st.markdown("### Current Layout")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Get user's layouts
            user_layouts = self.layout_manager.get_layouts_by_owner("system")  # Would use actual user
            
            if user_layouts:
                layout_options = {layout.layout_id: f"{layout.name} ({layout.layout_type.value})" for layout in user_layouts}
                
                # Get currently active layout
                active_layout = self.layout_manager.get_active_layout("system")
                default_index = 0
                
                if active_layout:
                    for i, layout in enumerate(user_layouts):
                        if layout.layout_id == active_layout.layout_id:
                            default_index = i
                            break
                
                selected_layout_id = st.selectbox(
                    "Select Layout",
                    options=list(layout_options.keys()),
                    format_func=lambda x: layout_options[x],
                    index=default_index,
                    key="layout_selector"
                )
                
                st.session_state.layout_selected_layout = selected_layout_id
            else:
                st.info("No layouts found. Create your first layout using the templates below.")
                st.session_state.layout_selected_layout = None
        
        with col2:
            if st.session_state.layout_selected_layout:
                if st.button("🔄 Set Active", key="set_active_layout"):
                    if self.layout_manager.set_active_layout(st.session_state.layout_selected_layout, "system"):
                        st.success("Layout activated!")
                        st.rerun()
                    else:
                        st.error("Failed to activate layout")
        
        with col3:
            st.session_state.layout_edit_mode = st.toggle(
                "Edit Mode", 
                value=st.session_state.layout_edit_mode,
                key="layout_edit_toggle"
            )
    
    def _render_my_layouts_tab(self):
        """Render my layouts tab."""
        st.subheader("My Dashboard Layouts")
        
        # Get user's layouts
        user_layouts = self.layout_manager.get_layouts_by_owner("system")
        
        if not user_layouts:
            st.info("You haven't created any custom layouts yet. Start with a template!")
            return
        
        # Layout cards
        cols = st.columns(3)
        
        for i, layout in enumerate(user_layouts):
            with cols[i % 3]:
                with st.container(border=True):
                    # Layout header
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{layout.name}**")
                        st.caption(f"{layout.layout_type.value.title()} • {len(layout.tabs)} tabs")
                    
                    with col2:
                        if layout.is_active:
                            st.success("Active")
                        elif layout.is_default:
                            st.info("Default")
                    
                    # Layout info
                    st.write(f"📅 Created: {layout.created_at.strftime('%Y-%m-%d')}")
                    st.write(f"📊 Used: {layout.usage_count} times")
                    
                    if layout.last_used_at:
                        st.write(f"🕒 Last used: {layout.last_used_at.strftime('%Y-%m-%d %H:%M')}")
                    
                    # Actions
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📝", key=f"edit_{layout.layout_id}", help="Edit"):
                            st.session_state.layout_selected_layout = layout.layout_id
                            st.session_state.layout_edit_mode = True
                            st.rerun()
                    
                    with col2:
                        if st.button("📋", key=f"clone_{layout.layout_id}", help="Clone"):
                            new_name = f"{layout.name} (Copy)"
                            cloned_id = self.layout_manager.clone_layout(layout.layout_id, new_name, "system")
                            if cloned_id:
                                st.success(f"Cloned as '{new_name}'")
                                st.rerun()
                            else:
                                st.error("Failed to clone layout")
                    
                    with col3:
                        if not layout.is_default and st.button("🗑️", key=f"delete_{layout.layout_id}", help="Delete"):
                            if st.session_state.get(f"confirm_delete_{layout.layout_id}", False):
                                if self.layout_manager.delete_layout(layout.layout_id, "system"):
                                    st.success("Layout deleted")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete layout")
                                st.session_state[f"confirm_delete_{layout.layout_id}"] = False
                            else:
                                st.session_state[f"confirm_delete_{layout.layout_id}"] = True
                                st.warning("Click again to confirm deletion")
        
        # Create new layout
        st.markdown("### Create New Layout")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_layout_name = st.text_input("Layout Name", key="new_layout_name")
        
        with col2:
            layout_type = st.selectbox(
                "Layout Type",
                options=[lt.value for lt in LayoutType],
                format_func=lambda x: x.replace("_", " ").title(),
                key="new_layout_type"
            )
        
        with col3:
            if st.button("➕ Create Empty Layout", type="secondary"):
                if new_layout_name:
                    layout_id = self.layout_manager.create_layout(
                        new_layout_name,
                        LayoutType(layout_type),
                        "system"
                    )
                    st.success(f"Created layout '{new_layout_name}'")
                    st.session_state.layout_selected_layout = layout_id
                    st.rerun()
                else:
                    st.error("Please enter a layout name")
    
    def _render_layout_editor_tab(self):
        """Render layout editor tab."""
        st.subheader("Layout Editor")
        
        if not st.session_state.layout_selected_layout:
            st.info("Select a layout to edit")
            return
        
        layout = self.layout_manager.get_layout(st.session_state.layout_selected_layout)
        if not layout:
            st.error("Selected layout not found")
            return
        
        if not st.session_state.layout_edit_mode:
            st.info("Enable Edit Mode to modify the layout")
            return
        
        st.markdown(f"### Editing: {layout.name}")
        
        # Layout properties
        with st.expander("Layout Properties", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Layout Name", value=layout.name, key="edit_layout_name")
                new_theme = st.selectbox(
                    "Theme",
                    options=["light", "dark", "auto"],
                    index=["light", "dark", "auto"].index(layout.theme),
                    key="edit_layout_theme"
                )
            
            with col2:
                sidebar_collapsed = st.checkbox(
                    "Collapse Sidebar",
                    value=layout.sidebar_collapsed,
                    key="edit_sidebar_collapsed"
                )
                show_breadcrumbs = st.checkbox(
                    "Show Breadcrumbs",
                    value=layout.show_breadcrumbs,
                    key="edit_show_breadcrumbs"
                )
            
            if st.button("💾 Save Layout Properties"):
                updates = {
                    'name': new_name,
                    'theme': new_theme,
                    'sidebar_collapsed': sidebar_collapsed,
                    'show_breadcrumbs': show_breadcrumbs
                }
                
                if self.layout_manager.update_layout(layout.layout_id, updates, "system"):
                    st.success("Layout properties updated!")
                    st.rerun()
                else:
                    st.error("Failed to update layout")
        
        # Tab management
        st.markdown("### Tab Management")
        
        # Display tabs
        if layout.tabs:
            tab_data = []
            for tab in layout.get_visible_tabs():
                tab_data.append({
                    "Order": tab.order,
                    "Name": tab.name,
                    "Icon": tab.icon,
                    "Widgets": len(tab.widgets),
                    "Visible": "✓" if tab.visible else "✗",
                    "Closable": "✓" if tab.closable else "✗"
                })
            
            df = pd.DataFrame(tab_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Tab actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Add new tab
                if st.button("➕ Add Tab"):
                    new_tab = DashboardTab(
                        name="New Tab",
                        icon="📊",
                        visible=True,
                        order=len(layout.tabs)
                    )
                    
                    if self.layout_manager.add_tab_to_layout(layout.layout_id, new_tab, "system"):
                        st.success("Tab added!")
                        st.rerun()
                    else:
                        st.error("Failed to add tab")
            
            with col2:
                # Remove tab
                tab_to_remove = st.selectbox(
                    "Remove Tab",
                    options=[t.tab_id for t in layout.tabs if t.closable],
                    format_func=lambda x: next(t.name for t in layout.tabs if t.tab_id == x),
                    key="tab_to_remove"
                )
                
                if tab_to_remove and st.button("🗑️ Remove Selected Tab"):
                    if self.layout_manager.remove_tab_from_layout(layout.layout_id, tab_to_remove, "system"):
                        st.success("Tab removed!")
                        st.rerun()
                    else:
                        st.error("Failed to remove tab")
            
            with col3:
                # Reorder tabs
                if st.button("🔄 Reorder Tabs"):
                    st.info("Drag and drop functionality would be implemented here")
        else:
            st.info("No tabs in this layout")
        
        # Widget management
        if layout.tabs:
            st.markdown("### Widget Management")
            
            selected_tab_id = st.selectbox(
                "Select Tab to Edit",
                options=[t.tab_id for t in layout.tabs],
                format_func=lambda x: next(t.name for t in layout.tabs if t.tab_id == x),
                key="selected_tab_for_widgets"
            )
            
            selected_tab = layout.get_tab(selected_tab_id)
            if selected_tab:
                st.markdown(f"#### Widgets in '{selected_tab.name}'")
                
                if selected_tab.widgets:
                    widget_data = []
                    for widget in selected_tab.widgets:
                        widget_data.append({
                            "Title": widget.title,
                            "Type": widget.widget_type.value.replace("_", " ").title(),
                            "Position": f"({widget.row}, {widget.column})",
                            "Size": f"{widget.width}x{widget.height}",
                            "Visible": "✓" if widget.visible else "✗"
                        })
                    
                    df = pd.DataFrame(widget_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No widgets in this tab")
                
                # Add widget
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    widget_type = st.selectbox(
                        "Widget Type",
                        options=[wt.value for wt in WidgetType],
                        format_func=lambda x: x.replace("_", " ").title(),
                        key="new_widget_type"
                    )
                
                with col2:
                    widget_title = st.text_input("Widget Title", key="new_widget_title")
                
                with col3:
                    widget_size = st.selectbox(
                        "Widget Size",
                        options=[ws.value for ws in WidgetSize],
                        key="new_widget_size"
                    )
                
                if st.button("➕ Add Widget to Tab"):
                    if widget_title:
                        new_widget = DashboardWidget(
                            widget_type=WidgetType(widget_type),
                            title=widget_title,
                            size=WidgetSize(widget_size),
                            row=0,
                            column=0,
                            width=2 if widget_size == "large" else 1,
                            height=2 if widget_size == "large" else 1,
                            created_by="system"
                        )
                        
                        if self.layout_manager.add_widget_to_tab(
                            layout.layout_id, selected_tab_id, new_widget, "system"
                        ):
                            st.success("Widget added!")
                            st.rerun()
                        else:
                            st.error("Failed to add widget")
                    else:
                        st.error("Please enter a widget title")
    
    def _render_templates_tab(self):
        """Render templates tab."""
        st.subheader("Layout Templates")
        
        # Get templates
        templates = self.layout_manager.get_templates()
        
        if not templates:
            st.info("No templates available")
            return
        
        # Group by category
        categories = {}
        for template in templates:
            if template.category not in categories:
                categories[template.category] = []
            categories[template.category].append(template)
        
        # Render categories
        for category, category_templates in categories.items():
            st.markdown(f"### {category.title()} Templates")
            
            cols = st.columns(3)
            
            for i, template in enumerate(category_templates):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"**{template.name}**")
                        st.caption(template.description)
                        
                        # Template info
                        st.write(f"📊 Type: {template.layout_type.value.title()}")
                        st.write(f"📈 Used: {template.usage_count} times")
                        
                        if template.rating > 0:
                            st.write(f"⭐ Rating: {template.rating:.1f}/5.0")
                        
                        # Tags
                        if template.tags:
                            tag_text = " ".join([f"`{tag}`" for tag in template.tags])
                            st.markdown(f"Tags: {tag_text}")
                        
                        # Actions
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📄 View", key=f"view_template_{template.template_id}"):
                                st.json(template.template_config)
                        
                        with col2:
                            layout_name = st.text_input(
                                "Name",
                                value=f"My {template.name}",
                                key=f"template_name_{template.template_id}"
                            )
                            
                            if st.button("🔧 Use Template", key=f"use_template_{template.template_id}"):
                                if layout_name:
                                    layout_id = self.layout_manager.create_layout(
                                        layout_name,
                                        LayoutType.CUSTOM,
                                        "system",
                                        template.template_id
                                    )
                                    st.success(f"Created layout '{layout_name}' from template!")
                                    st.session_state.layout_selected_layout = layout_id
                                    st.rerun()
                                else:
                                    st.error("Please enter a layout name")
    
    def _render_widget_library_tab(self):
        """Render widget library tab."""
        st.subheader("Widget Library")
        
        # Get widget library information
        library_info = self.widget_renderer.get_widget_library_info()
        registry_stats = library_info['registry_stats']
        widgets_by_category = library_info['widgets_by_category']
        
        # Library statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Widgets", registry_stats['total_widgets'])
        
        with col2:
            st.metric("Categories", len(registry_stats['categories']))
        
        with col3:
            st.metric("Widget Types", len(registry_stats['widget_types']))
        
        # Search functionality
        search_term = st.text_input("🔍 Search Widgets", placeholder="Search by name or description...")
        
        if search_term:
            matching_widgets = self.widget_registry.search_widgets(search_term)
            st.markdown(f"### Search Results ({len(matching_widgets)} matches)")
            
            if matching_widgets:
                cols = st.columns(3)
                for i, widget_info in enumerate(matching_widgets):
                    with cols[i % 3]:
                        self._render_widget_info_card(widget_info)
            else:
                st.info("No widgets match your search criteria")
        else:
            # Render by category
            for category, widgets in widgets_by_category.items():
                with st.expander(f"📁 {category} Widgets ({len(widgets)})", expanded=True):
                    cols = st.columns(3)
                    
                    for i, widget_info in enumerate(widgets):
                        with cols[i % 3]:
                            self._render_widget_info_card(widget_info)
        
        # Widget sizes reference
        with st.expander("📏 Widget Size Reference", expanded=False):
            size_info = {
                WidgetSize.SMALL: {"description": "1x1 grid (compact)", "width": "Small"},
                WidgetSize.MEDIUM: {"description": "2x1 grid (standard)", "width": "Medium"},
                WidgetSize.LARGE: {"description": "2x2 grid (detailed)", "width": "Large"},
                WidgetSize.WIDE: {"description": "3x1 grid (full width)", "width": "Wide"},
                WidgetSize.FULL: {"description": "Full container width", "width": "Full"}
            }
            
            for size, info in size_info.items():
                st.write(f"• **{info['width']}** ({size.value}): {info['description']}")
        
        # Widget preview functionality
        st.markdown("### 🎭 Widget Preview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            widget_type_options = [wt.value for wt in WidgetType]
            selected_widget_type = st.selectbox(
                "Select Widget to Preview",
                options=widget_type_options,
                format_func=lambda x: x.replace('_', ' ').title(),
                key="widget_preview_selector"
            )
        
        with col2:
            if st.button("👁️ Preview Widget", key="preview_widget_btn"):
                st.session_state.show_widget_preview = True
                st.session_state.preview_widget_type = selected_widget_type
        
        # Show widget preview
        if st.session_state.get('show_widget_preview', False):
            widget_type = WidgetType(st.session_state.preview_widget_type)
            
            with st.expander(f"Preview: {widget_type.value.replace('_', ' ').title()}", expanded=True):
                try:
                    # Get widget class and create sample instance
                    widget_class = self.widget_registry.get_widget_class(widget_type)
                    if widget_class:
                        from ..widgets.base_widget import WidgetConfig
                        import uuid
                        
                        # Create sample configuration
                        sample_config = WidgetConfig(
                            widget_id=str(uuid.uuid4()),
                            widget_type=widget_type,
                            title=f"Sample {widget_class.widget_name}",
                            size=widget_class.default_size
                        )
                        
                        # Create and render widget
                        sample_widget = widget_class(sample_config)
                        sample_widget.render()
                    else:
                        st.error(f"Widget type {widget_type.value} not found in registry")
                        
                except Exception as e:
                    st.error(f"Error previewing widget: {str(e)}")
                
                if st.button("❌ Close Preview", key="close_preview_btn"):
                    st.session_state.show_widget_preview = False
                    st.rerun()
    
    def _render_widget_info_card(self, widget_info: Dict[str, Any]) -> None:
        """Render widget information card."""
        with st.container(border=True):
            st.markdown(f"**{widget_info['widget_icon']} {widget_info['widget_name']}**")
            st.caption(widget_info['widget_description'])
            
            # Widget metadata
            st.markdown(f"📂 **Category**: {widget_info['widget_category']}")
            st.markdown(f"📏 **Default Size**: {widget_info['default_size'].replace('_', ' ').title()}")
            
            # Configuration options count
            config_count = len(widget_info.get('config_schema', {}))
            if config_count > 0:
                st.markdown(f"⚙️ **Config Options**: {config_count}")
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔧 Configure", key=f"configure_{widget_info['widget_type']}", help="Configure widget"):
                    st.session_state.configure_widget_type = widget_info['widget_type']
                    st.session_state.show_widget_configurator = True
                    st.rerun()
            
            with col2:
                if st.button("➕ Add", key=f"add_{widget_info['widget_type']}", help="Add to current layout"):
                    self._add_widget_to_current_layout(WidgetType(widget_info['widget_type']))
        
        # Show widget configurator if requested
        if (st.session_state.get('show_widget_configurator', False) and 
            st.session_state.get('configure_widget_type') == widget_info['widget_type']):
            
            with st.expander(f"Configure {widget_info['widget_name']}", expanded=True):
                config_result = self.widget_renderer.render_widget_configurator(
                    WidgetType(widget_info['widget_type'])
                )
                
                if config_result is not None:
                    st.session_state.show_widget_configurator = False
                    st.success("Widget configured successfully!")
                    # Here you could save the configuration or add to layout
                    st.rerun()
    
    def _add_widget_to_current_layout(self, widget_type: WidgetType) -> None:
        """Add a widget to the currently selected layout."""
        if not st.session_state.layout_selected_layout:
            st.warning("Please select a layout first")
            return
        
        layout = self.layout_manager.get_layout(st.session_state.layout_selected_layout)
        if not layout:
            st.error("Selected layout not found")
            return
        
        if not layout.tabs:
            st.warning("Layout has no tabs. Add a tab first.")
            return
        
        # Add to first tab for simplicity
        first_tab = layout.tabs[0]
        
        # Get widget class info
        widget_class = self.widget_registry.get_widget_class(widget_type)
        if not widget_class:
            st.error(f"Widget type {widget_type.value} not found")
            return
        
        # Create new widget
        new_widget = DashboardWidget(
            widget_type=widget_type,
            title=f"New {widget_class.widget_name}",
            size=widget_class.default_size,
            row=0,
            column=len(first_tab.widgets),  # Add to end
            width=2 if widget_class.default_size == WidgetSize.LARGE else 1,
            height=2 if widget_class.default_size == WidgetSize.LARGE else 1,
            created_by="system"
        )
        
        # Add widget to layout
        if self.layout_manager.add_widget_to_tab(
            layout.layout_id, first_tab.tab_id, new_widget, "system"
        ):
            st.success(f"Added '{widget_class.widget_name}' to '{first_tab.name}' tab")
            st.rerun()
        else:
            st.error("Failed to add widget to layout")
    
    def _render_preview_tab(self):
        """Render preview tab."""
        st.subheader("Layout Preview")
        
        if not st.session_state.layout_selected_layout:
            st.info("Select a layout to preview")
            return
        
        layout = self.layout_manager.get_layout(st.session_state.layout_selected_layout)
        if not layout:
            st.error("Selected layout not found")
            return
        
        st.markdown(f"### Preview: {layout.name}")
        
        # Preview controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            preview_mode = st.selectbox(
                "Preview Mode",
                options=["desktop", "tablet", "mobile"],
                key="preview_mode"
            )
        
        with col2:
            show_grid = st.checkbox("Show Grid", value=False, key="show_grid")
        
        with col3:
            show_borders = st.checkbox("Show Widget Borders", value=True, key="show_borders")
        
        # Layout structure
        st.markdown("#### Layout Structure")
        
        st.info(f"""
        **Theme**: {layout.theme}  
        **Sidebar**: {'Collapsed' if layout.sidebar_collapsed else 'Expanded'}  
        **Breadcrumbs**: {'Shown' if layout.show_breadcrumbs else 'Hidden'}  
        **Tabs**: {len(layout.tabs)} tabs  
        """)
        
        # Layout preview options
        col1, col2 = st.columns(2)
        
        with col1:
            preview_mode = st.selectbox(
                "Preview Mode",
                options=["layout_structure", "live_widgets", "grid_visualization"],
                format_func=lambda x: {
                    "layout_structure": "📋 Layout Structure",
                    "live_widgets": "🎭 Live Widget Preview", 
                    "grid_visualization": "🏗️ Grid Visualization"
                }[x],
                key="preview_mode_selector"
            )
        
        with col2:
            if st.button("🔄 Refresh Preview", key="refresh_preview"):
                st.rerun()
        
        # Render preview based on mode
        if preview_mode == "live_widgets":
            # Live widget preview - render actual widgets
            st.markdown("#### 🎭 Live Widget Preview")
            
            if layout.tabs:
                # Create tabs for preview
                tab_names = [f"{tab.icon} {tab.name}" for tab in layout.get_visible_tabs()]
                if tab_names:
                    preview_tabs = st.tabs(tab_names)
                    
                    for i, tab in enumerate(layout.get_visible_tabs()):
                        with preview_tabs[i]:
                            if tab.widgets:
                                st.caption(f"Rendering {len(tab.widgets)} widgets in live preview mode")
                                try:
                                    # Use widget renderer to render the tab
                                    self.widget_renderer.render_tab(tab, layout.layout_id)
                                except Exception as e:
                                    st.error(f"Error rendering tab widgets: {str(e)}")
                            else:
                                st.info("No widgets in this tab")
                else:
                    st.info("No visible tabs in layout")
            else:
                st.info("No tabs in this layout")
        
        elif preview_mode == "grid_visualization":
            # Grid visualization
            st.markdown("#### 🏗️ Grid Layout Visualization")
            
            if layout.tabs:
                for tab in layout.get_visible_tabs():
                    with st.expander(f"{tab.icon} {tab.name} ({len(tab.widgets)} widgets)", expanded=True):
                        if tab.widgets:
                            st.markdown(f"**Grid**: {tab.grid_columns} columns × {tab.grid_rows} rows")
                            
                            # Create grid visualization
                            grid_data = []
                            widget_positions = {}
                            
                            # Map widgets to positions
                            for widget in tab.widgets:
                                pos_key = f"{widget.row}-{widget.column}"
                                widget_positions[pos_key] = widget
                            
                            # Create visual grid
                            for row in range(min(6, tab.grid_rows)):  # Show first 6 rows
                                row_data = {}
                                for col in range(min(8, tab.grid_columns)):  # Show first 8 columns
                                    key = f"{row}-{col}"
                                    if key in widget_positions:
                                        widget = widget_positions[key]
                                        size_indicator = {
                                            WidgetSize.SMALL: "🔹",
                                            WidgetSize.MEDIUM: "🔸", 
                                            WidgetSize.LARGE: "🔶",
                                            WidgetSize.WIDE: "📏",
                                            WidgetSize.FULL: "📐"
                                        }.get(widget.size, "⚪")
                                        
                                        row_data[f"C{col}"] = f"{size_indicator} {widget.title[:15]}..."
                                    else:
                                        row_data[f"C{col}"] = "⬜ Empty"
                                grid_data.append(row_data)
                            
                            if grid_data:
                                df = pd.DataFrame(grid_data, index=[f"R{i}" for i in range(len(grid_data))])
                                st.dataframe(df, use_container_width=True)
                                
                                # Legend
                                st.caption("Legend: 🔹Small 🔸Medium 🔶Large 📏Wide 📐Full ⬜Empty")
                        else:
                            st.info("No widgets in this tab")
            else:
                st.info("No tabs in this layout")
        
        else:  # layout_structure
            # Structure preview (existing functionality)
            st.markdown("#### 📋 Layout Structure")
            
            if layout.tabs:
                for tab in layout.get_visible_tabs():
                    with st.expander(f"{tab.icon} {tab.name} ({len(tab.widgets)} widgets)", expanded=True):
                        if tab.widgets:
                            st.markdown(f"**Grid Configuration**: {tab.grid_columns} columns × {tab.grid_rows} rows")
                            
                            # Widget list with details
                            widget_data = []
                            for widget in tab.widgets:
                                widget_data.append({
                                    "Widget": widget.title,
                                    "Type": widget.widget_type.value.replace('_', ' ').title(),
                                    "Size": widget.size.value.title(),
                                    "Position": f"({widget.row}, {widget.column})",
                                    "Dimensions": f"{widget.width}×{widget.height}",
                                    "Visible": "✓" if widget.visible else "✗",
                                    "Auto-refresh": "✓" if widget.auto_refresh else "✗"
                                })
                            
                            if widget_data:
                                df = pd.DataFrame(widget_data)
                                st.dataframe(df, use_container_width=True, hide_index=True)
                        else:
                            st.info("No widgets in this tab")
            else:
                st.info("No tabs in this layout")
        
        # Export options
        st.markdown("#### Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export JSON"):
                layout_data = self.layout_manager.export_layout(layout.layout_id)
                if layout_data:
                    st.download_button(
                        "Download Layout JSON",
                        data=json.dumps(layout_data, indent=2),
                        file_name=f"layout_{layout.name.lower().replace(' ', '_')}.json",
                        mime="application/json"
                    )
        
        with col2:
            if st.button("📸 Generate Screenshot"):
                st.info("Screenshot functionality would be implemented here")
        
        with col3:
            if st.button("🔗 Share Layout"):
                st.info("Sharing functionality would be implemented here")
    
    def _render_analytics_tab(self):
        """Render analytics tab."""
        st.subheader("Layout Analytics")
        
        # Statistics
        stats = self.layout_manager.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Layouts", stats['total_layouts'])
        
        with col2:
            st.metric("Active Layouts", stats['active_layouts'])
        
        with col3:
            st.metric("Shared Layouts", stats['shared_layouts'])
        
        with col4:
            st.metric("Templates", stats['total_templates'])
        
        # Usage analytics
        st.markdown("### Layout Usage")
        
        user_layouts = self.layout_manager.get_layouts_by_owner("system")
        
        if user_layouts:
            usage_data = []
            for layout in user_layouts:
                usage_data.append({
                    "Layout": layout.name,
                    "Type": layout.layout_type.value,
                    "Usage Count": layout.usage_count,
                    "Last Used": layout.last_used_at.strftime('%Y-%m-%d') if layout.last_used_at else "Never",
                    "Tabs": len(layout.tabs),
                    "Total Widgets": sum(len(tab.widgets) for tab in layout.tabs)
                })
            
            df = pd.DataFrame(usage_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No layouts to analyze")
        
        # Change history
        st.markdown("### Recent Changes")
        
        changes = self.layout_manager.get_change_history(limit=20)
        
        if changes:
            change_data = []
            for change in changes:
                layout_name = "Unknown"
                if change.layout_id in [l.layout_id for l in user_layouts]:
                    layout = next(l for l in user_layouts if l.layout_id == change.layout_id)
                    layout_name = layout.name
                
                change_data.append({
                    "Time": change.timestamp.strftime('%Y-%m-%d %H:%M'),
                    "Layout": layout_name,
                    "Action": change.change_type.replace("_", " ").title(),
                    "Description": change.description,
                    "User": change.user
                })
            
            df = pd.DataFrame(change_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No recent changes")
    
    def _render_settings_tab(self):
        """Render settings tab."""
        st.subheader("Layout Settings")
        
        # Import/Export
        st.markdown("### Import/Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Import Layout")
            
            uploaded_file = st.file_uploader(
                "Upload Layout JSON",
                type=['json'],
                key="layout_import"
            )
            
            if uploaded_file:
                try:
                    layout_data = json.load(uploaded_file)
                    
                    # Show layout info
                    st.info(f"Layout: {layout_data.get('name', 'Unknown')}")
                    st.info(f"Type: {layout_data.get('layout_type', 'Unknown')}")
                    st.info(f"Tabs: {len(layout_data.get('tabs', []))}")
                    
                    if st.button("📥 Import Layout"):
                        layout_id = self.layout_manager.import_layout(layout_data, "system")
                        if layout_id:
                            st.success("Layout imported successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to import layout")
                
                except Exception as e:
                    st.error(f"Error reading layout file: {e}")
        
        with col2:
            st.markdown("#### Export All Layouts")
            
            if st.button("📤 Export All My Layouts"):
                user_layouts = self.layout_manager.get_layouts_by_owner("system")
                
                if user_layouts:
                    export_data = {
                        'layouts': [self.layout_manager.export_layout(l.layout_id) for l in user_layouts],
                        'exported_at': datetime.now().isoformat(),
                        'exported_by': 'system'
                    }
                    
                    st.download_button(
                        "Download All Layouts",
                        data=json.dumps(export_data, indent=2),
                        file_name=f"all_layouts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:
                    st.info("No layouts to export")
        
        # Backup and Restore
        st.markdown("### Backup Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Create Backup"):
                st.info("Backup functionality would be implemented here")
        
        with col2:
            if st.button("🔄 Restore from Backup"):
                st.info("Restore functionality would be implemented here")
        
        # Reset and cleanup
        st.markdown("### Reset Options")
        
        st.warning("⚠️ Dangerous operations below")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset to Default"):
                if st.session_state.get('confirm_reset', False):
                    st.info("Reset functionality would be implemented here")
                    st.session_state.confirm_reset = False
                else:
                    st.session_state.confirm_reset = True
                    st.warning("Click again to confirm reset")
        
        with col2:
            if st.button("🗑️ Delete All Custom Layouts"):
                if st.session_state.get('confirm_delete_all', False):
                    st.info("Bulk delete functionality would be implemented here")
                    st.session_state.confirm_delete_all = False
                else:
                    st.session_state.confirm_delete_all = True
                    st.error("Click again to confirm deletion of ALL custom layouts")