"""
Base widget class and configuration for the dashboard widget system.
"""

import streamlit as st
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ..layout.models import WidgetType, WidgetSize, DashboardWidget


@dataclass
class WidgetConfig:
    """Configuration for a dashboard widget."""
    widget_id: str
    widget_type: WidgetType
    title: str
    size: WidgetSize
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Display settings
    visible: bool = True
    collapsible: bool = True
    collapsed: bool = False
    refreshable: bool = True
    auto_refresh: bool = True
    refresh_interval_seconds: int = 30
    
    # Style settings
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    text_color: Optional[str] = None
    custom_css: Optional[str] = None
    
    @classmethod
    def from_dashboard_widget(cls, widget: DashboardWidget) -> 'WidgetConfig':
        """Create WidgetConfig from DashboardWidget."""
        return cls(
            widget_id=widget.widget_id,
            widget_type=widget.widget_type,
            title=widget.title,
            size=widget.size,
            config=widget.config,
            visible=widget.visible,
            collapsible=widget.collapsible,
            collapsed=widget.collapsed,
            refreshable=widget.refreshable,
            auto_refresh=widget.auto_refresh,
            refresh_interval_seconds=widget.refresh_interval_seconds,
            background_color=widget.background_color,
            border_color=widget.border_color,
            text_color=widget.text_color,
            custom_css=widget.custom_css
        )


class BaseWidget(ABC):
    """
    Base class for all dashboard widgets.
    
    Each widget must implement the render method and provide
    widget metadata through class attributes.
    """
    
    # Widget metadata (override in subclasses)
    widget_type: WidgetType = WidgetType.SYSTEM_OVERVIEW
    widget_name: str = "Base Widget"
    widget_description: str = "Base widget class"
    widget_icon: str = "📊"
    widget_category: str = "General"
    default_size: WidgetSize = WidgetSize.MEDIUM
    
    # Configuration schema (override in subclasses)
    config_schema: Dict[str, Any] = {}
    
    def __init__(self, config: WidgetConfig):
        """Initialize widget with configuration."""
        self.config = config
        self.last_updated = datetime.now()
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate widget configuration against schema."""
        # Basic validation - subclasses can override for specific validation
        if not self.config.widget_id:
            raise ValueError("Widget ID is required")
        
        if not self.config.title:
            self.config.title = self.widget_name
    
    def _apply_styles(self) -> None:
        """Apply custom styles to the widget container."""
        if self.config.custom_css:
            st.markdown(f"<style>{self.config.custom_css}</style>", unsafe_allow_html=True)
    
    def _render_header(self) -> None:
        """Render widget header with title and controls."""
        col1, col2 = st.columns([4, 1])
        
        with col1:
            if self.config.collapsible:
                # Use expander for collapsible widgets
                with st.expander(f"{self.widget_icon} {self.config.title}", expanded=not self.config.collapsed):
                    self._render_content()
            else:
                st.markdown(f"### {self.widget_icon} {self.config.title}")
                self._render_content()
        
        with col2:
            if self.config.refreshable:
                if st.button("🔄", key=f"refresh_{self.config.widget_id}", help="Refresh widget"):
                    self.refresh()
                    st.rerun()
    
    def _render_container(self) -> None:
        """Render widget with proper container styling."""
        # Apply custom styles
        self._apply_styles()
        
        # Create container with styling based on size and colors
        container_style = self._get_container_style()
        
        if container_style:
            with st.container():
                st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)
                self._render_header()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            with st.container():
                self._render_header()
    
    def _get_container_style(self) -> str:
        """Get CSS style for the widget container."""
        styles = []
        
        if self.config.background_color:
            styles.append(f"background-color: {self.config.background_color}")
        
        if self.config.border_color:
            styles.append(f"border: 1px solid {self.config.border_color}")
            styles.append("border-radius: 8px")
            styles.append("padding: 10px")
        
        if self.config.text_color:
            styles.append(f"color: {self.config.text_color}")
        
        return "; ".join(styles)
    
    @abstractmethod
    def _render_content(self) -> None:
        """Render the main widget content. Must be implemented by subclasses."""
        pass
    
    def render(self) -> None:
        """Main render method - calls the container renderer."""
        if not self.config.visible:
            return
        
        try:
            self._render_container()
            self.last_updated = datetime.now()
        except Exception as e:
            st.error(f"Error rendering widget '{self.config.title}': {str(e)}")
    
    def refresh(self) -> None:
        """Refresh widget data. Override in subclasses if needed."""
        self.last_updated = datetime.now()
    
    def get_config_ui(self) -> Dict[str, Any]:
        """
        Return configuration UI elements for this widget.
        Override in subclasses for widget-specific configuration.
        """
        config_values = {}
        
        # Basic configuration
        config_values['title'] = st.text_input(
            "Widget Title",
            value=self.config.title,
            key=f"config_title_{self.config.widget_id}"
        )
        
        config_values['size'] = st.selectbox(
            "Widget Size",
            options=[size.value for size in WidgetSize],
            index=[size.value for size in WidgetSize].index(self.config.size.value),
            format_func=lambda x: x.title(),
            key=f"config_size_{self.config.widget_id}"
        )
        
        # Display settings
        with st.expander("Display Settings"):
            config_values['collapsible'] = st.checkbox(
                "Collapsible",
                value=self.config.collapsible,
                key=f"config_collapsible_{self.config.widget_id}"
            )
            
            config_values['refreshable'] = st.checkbox(
                "Refreshable",
                value=self.config.refreshable,
                key=f"config_refreshable_{self.config.widget_id}"
            )
            
            if config_values['refreshable']:
                config_values['refresh_interval'] = st.slider(
                    "Refresh Interval (seconds)",
                    min_value=5,
                    max_value=300,
                    value=self.config.refresh_interval_seconds,
                    key=f"config_refresh_interval_{self.config.widget_id}"
                )
        
        # Style settings
        with st.expander("Style Settings"):
            config_values['background_color'] = st.color_picker(
                "Background Color",
                value=self.config.background_color or "#FFFFFF",
                key=f"config_bg_color_{self.config.widget_id}"
            )
            
            config_values['border_color'] = st.color_picker(
                "Border Color",
                value=self.config.border_color or "#CCCCCC",
                key=f"config_border_color_{self.config.widget_id}"
            )
            
            config_values['text_color'] = st.color_picker(
                "Text Color",
                value=self.config.text_color or "#000000",
                key=f"config_text_color_{self.config.widget_id}"
            )
        
        return config_values
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update widget configuration with new values."""
        if 'title' in new_config:
            self.config.title = new_config['title']
        
        if 'size' in new_config:
            self.config.size = WidgetSize(new_config['size'])
        
        if 'collapsible' in new_config:
            self.config.collapsible = new_config['collapsible']
        
        if 'refreshable' in new_config:
            self.config.refreshable = new_config['refreshable']
        
        if 'refresh_interval' in new_config:
            self.config.refresh_interval_seconds = new_config['refresh_interval']
        
        if 'background_color' in new_config:
            self.config.background_color = new_config['background_color']
        
        if 'border_color' in new_config:
            self.config.border_color = new_config['border_color']
        
        if 'text_color' in new_config:
            self.config.text_color = new_config['text_color']
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert widget to dictionary representation."""
        return {
            'widget_type': self.widget_type.value,
            'widget_name': self.widget_name,
            'widget_description': self.widget_description,
            'widget_icon': self.widget_icon,
            'widget_category': self.widget_category,
            'config': self.config.__dict__,
            'last_updated': self.last_updated.isoformat()
        }
    
    @classmethod
    def get_widget_info(cls) -> Dict[str, Any]:
        """Get widget metadata information."""
        return {
            'widget_type': cls.widget_type.value,
            'widget_name': cls.widget_name,
            'widget_description': cls.widget_description,
            'widget_icon': cls.widget_icon,
            'widget_category': cls.widget_category,
            'default_size': cls.default_size.value,
            'config_schema': cls.config_schema
        }