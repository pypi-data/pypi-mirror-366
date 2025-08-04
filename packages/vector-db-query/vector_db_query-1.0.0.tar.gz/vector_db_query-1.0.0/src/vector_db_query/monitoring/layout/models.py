"""
Data models for customizable dashboard layout management.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json


class LayoutType(Enum):
    """Types of dashboard layouts."""
    STANDARD = "standard"          # Default layout
    COMPACT = "compact"           # Minimized layout
    DETAILED = "detailed"         # Full detailed layout
    CUSTOM = "custom"             # User-defined layout
    MOBILE = "mobile"             # Mobile-optimized layout


class WidgetType(Enum):
    """Types of dashboard widgets."""
    SYSTEM_OVERVIEW = "system_overview"
    PROCESS_CONTROL = "process_control"
    QUEUE_STATUS = "queue_status"
    METRICS_CHART = "metrics_chart"
    EVENT_STREAM = "event_stream"
    NOTIFICATION_PANEL = "notification_panel"
    CONNECTION_STATUS = "connection_status"
    PERFORMANCE_GRAPH = "performance_graph"
    LOG_VIEWER = "log_viewer"
    CUSTOM_HTML = "custom_html"


class WidgetSize(Enum):
    """Widget size options."""
    SMALL = "small"       # 1x1
    MEDIUM = "medium"     # 2x1
    LARGE = "large"      # 2x2
    WIDE = "wide"        # 3x1
    FULL = "full"        # Full width


@dataclass
class DashboardWidget:
    """Individual dashboard widget configuration."""
    widget_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    widget_type: WidgetType = WidgetType.SYSTEM_OVERVIEW
    title: str = ""
    
    # Position and size
    row: int = 0
    column: int = 0
    width: int = 1
    height: int = 1
    size: WidgetSize = WidgetSize.MEDIUM
    
    # Display settings
    visible: bool = True
    collapsible: bool = True
    collapsed: bool = False
    refreshable: bool = True
    auto_refresh: bool = True
    refresh_interval_seconds: int = 30
    
    # Widget-specific configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Style settings
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    text_color: Optional[str] = None
    custom_css: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'widget_id': self.widget_id,
            'widget_type': self.widget_type.value,
            'title': self.title,
            'position': {
                'row': self.row,
                'column': self.column,
                'width': self.width,
                'height': self.height,
                'size': self.size.value
            },
            'display': {
                'visible': self.visible,
                'collapsible': self.collapsible,
                'collapsed': self.collapsed,
                'refreshable': self.refreshable,
                'auto_refresh': self.auto_refresh,
                'refresh_interval': self.refresh_interval_seconds
            },
            'config': self.config,
            'style': {
                'background_color': self.background_color,
                'border_color': self.border_color,
                'text_color': self.text_color,
                'custom_css': self.custom_css
            },
            'metadata': {
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
                'created_by': self.created_by
            }
        }


@dataclass
class DashboardTab:
    """Dashboard tab configuration."""
    tab_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    icon: str = "📊"
    
    # Tab properties
    visible: bool = True
    order: int = 0
    closable: bool = False
    
    # Widgets in this tab
    widgets: List[DashboardWidget] = field(default_factory=list)
    
    # Layout settings
    grid_columns: int = 12
    grid_rows: int = 8
    gap_size: int = 10
    
    # Tab-specific configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_widget(self, widget: DashboardWidget) -> str:
        """Add a widget to the tab."""
        widget.updated_at = datetime.now()
        self.widgets.append(widget)
        self.updated_at = datetime.now()
        return widget.widget_id
    
    def remove_widget(self, widget_id: str) -> bool:
        """Remove a widget from the tab."""
        for i, widget in enumerate(self.widgets):
            if widget.widget_id == widget_id:
                self.widgets.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
    
    def get_widget(self, widget_id: str) -> Optional[DashboardWidget]:
        """Get a widget by ID."""
        for widget in self.widgets:
            if widget.widget_id == widget_id:
                return widget
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'tab_id': self.tab_id,
            'name': self.name,
            'icon': self.icon,
            'properties': {
                'visible': self.visible,
                'order': self.order,
                'closable': self.closable
            },
            'layout': {
                'grid_columns': self.grid_columns,
                'grid_rows': self.grid_rows,
                'gap_size': self.gap_size
            },
            'widgets': [w.to_dict() for w in self.widgets],
            'config': self.config,
            'metadata': {
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat()
            }
        }


@dataclass
class DashboardLayout:
    """Complete dashboard layout configuration."""
    layout_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Default Layout"
    layout_type: LayoutType = LayoutType.STANDARD
    
    # Layout properties
    is_active: bool = False
    is_default: bool = False
    shared: bool = False
    
    # Tabs in this layout
    tabs: List[DashboardTab] = field(default_factory=list)
    
    # Global layout settings
    theme: str = "light"  # light, dark, auto
    sidebar_collapsed: bool = False
    show_breadcrumbs: bool = True
    show_header: bool = True
    show_footer: bool = True
    
    # Responsive settings
    mobile_layout: Optional[str] = None
    tablet_layout: Optional[str] = None
    
    # User preferences
    auto_save: bool = True
    save_interval_seconds: int = 300
    
    # Access control
    owner: str = "system"
    allowed_users: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    
    def add_tab(self, tab: DashboardTab) -> str:
        """Add a tab to the layout."""
        tab.order = len(self.tabs)
        tab.updated_at = datetime.now()
        self.tabs.append(tab)
        self.updated_at = datetime.now()
        return tab.tab_id
    
    def remove_tab(self, tab_id: str) -> bool:
        """Remove a tab from the layout."""
        for i, tab in enumerate(self.tabs):
            if tab.tab_id == tab_id:
                if not tab.closable:
                    return False
                self.tabs.pop(i)
                # Reorder remaining tabs
                for j, remaining_tab in enumerate(self.tabs[i:], i):
                    remaining_tab.order = j
                self.updated_at = datetime.now()
                return True
        return False
    
    def reorder_tabs(self, tab_orders: Dict[str, int]) -> bool:
        """Reorder tabs based on provided order mapping."""
        try:
            for tab in self.tabs:
                if tab.tab_id in tab_orders:
                    tab.order = tab_orders[tab.tab_id]
            
            # Sort tabs by order
            self.tabs.sort(key=lambda t: t.order)
            self.updated_at = datetime.now()
            return True
        except Exception:
            return False
    
    def get_tab(self, tab_id: str) -> Optional[DashboardTab]:
        """Get a tab by ID."""
        for tab in self.tabs:
            if tab.tab_id == tab_id:
                return tab
        return None
    
    def get_visible_tabs(self) -> List[DashboardTab]:
        """Get all visible tabs, sorted by order."""
        visible_tabs = [tab for tab in self.tabs if tab.visible]
        return sorted(visible_tabs, key=lambda t: t.order)
    
    def clone(self, new_name: str, new_owner: str = "system") -> 'DashboardLayout':
        """Create a copy of this layout."""
        cloned = DashboardLayout(
            name=new_name,
            layout_type=LayoutType.CUSTOM,
            owner=new_owner,
            theme=self.theme,
            sidebar_collapsed=self.sidebar_collapsed,
            show_breadcrumbs=self.show_breadcrumbs,
            show_header=self.show_header,
            show_footer=self.show_footer
        )
        
        # Clone tabs and widgets
        for tab in self.tabs:
            cloned_tab = DashboardTab(
                name=tab.name,
                icon=tab.icon,
                visible=tab.visible,
                order=tab.order,
                closable=tab.closable,
                grid_columns=tab.grid_columns,
                grid_rows=tab.grid_rows,
                gap_size=tab.gap_size,
                config=tab.config.copy()
            )
            
            # Clone widgets
            for widget in tab.widgets:
                cloned_widget = DashboardWidget(
                    widget_type=widget.widget_type,
                    title=widget.title,
                    row=widget.row,
                    column=widget.column,
                    width=widget.width,
                    height=widget.height,
                    size=widget.size,
                    visible=widget.visible,
                    collapsible=widget.collapsible,
                    collapsed=widget.collapsed,
                    refreshable=widget.refreshable,
                    auto_refresh=widget.auto_refresh,
                    refresh_interval_seconds=widget.refresh_interval_seconds,
                    config=widget.config.copy(),
                    background_color=widget.background_color,
                    border_color=widget.border_color,
                    text_color=widget.text_color,
                    custom_css=widget.custom_css,
                    created_by=new_owner
                )
                cloned_tab.add_widget(cloned_widget)
            
            cloned.add_tab(cloned_tab)
        
        return cloned
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'layout_id': self.layout_id,
            'name': self.name,
            'layout_type': self.layout_type.value,
            'properties': {
                'is_active': self.is_active,
                'is_default': self.is_default,
                'shared': self.shared
            },
            'global_settings': {
                'theme': self.theme,
                'sidebar_collapsed': self.sidebar_collapsed,
                'show_breadcrumbs': self.show_breadcrumbs,
                'show_header': self.show_header,
                'show_footer': self.show_footer
            },
            'responsive': {
                'mobile_layout': self.mobile_layout,
                'tablet_layout': self.tablet_layout
            },
            'preferences': {
                'auto_save': self.auto_save,
                'save_interval_seconds': self.save_interval_seconds
            },
            'tabs': [tab.to_dict() for tab in self.tabs],
            'access': {
                'owner': self.owner,
                'allowed_users': self.allowed_users
            },
            'metadata': {
                'created_at': self.created_at.isoformat(),
                'updated_at': self.updated_at.isoformat(),
                'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
                'usage_count': self.usage_count
            }
        }


@dataclass
class LayoutTemplate:
    """Pre-defined layout template."""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: str = "general"  # general, monitoring, analytics, admin
    
    # Template properties
    layout_type: LayoutType = LayoutType.STANDARD
    preview_image: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Template configuration
    template_config: Dict[str, Any] = field(default_factory=dict)
    
    # Usage tracking
    usage_count: int = 0
    rating: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def create_layout(self, name: str, owner: str = "system") -> DashboardLayout:
        """Create a dashboard layout from this template."""
        layout = DashboardLayout(
            name=name,
            layout_type=self.layout_type,
            owner=owner
        )
        
        # Apply template configuration
        if 'global_settings' in self.template_config:
            settings = self.template_config['global_settings']
            layout.theme = settings.get('theme', 'light')
            layout.sidebar_collapsed = settings.get('sidebar_collapsed', False)
            layout.show_breadcrumbs = settings.get('show_breadcrumbs', True)
            layout.show_header = settings.get('show_header', True)
            layout.show_footer = settings.get('show_footer', True)
        
        # Create tabs from template
        if 'tabs' in self.template_config:
            for tab_config in self.template_config['tabs']:
                tab = DashboardTab(
                    name=tab_config.get('name', 'Tab'),
                    icon=tab_config.get('icon', '📊'),
                    visible=tab_config.get('visible', True),
                    grid_columns=tab_config.get('grid_columns', 12),
                    grid_rows=tab_config.get('grid_rows', 8),
                    gap_size=tab_config.get('gap_size', 10)
                )
                
                # Add widgets from template
                if 'widgets' in tab_config:
                    for widget_config in tab_config['widgets']:
                        widget = DashboardWidget(
                            widget_type=WidgetType(widget_config.get('widget_type', 'system_overview')),
                            title=widget_config.get('title', 'Widget'),
                            row=widget_config.get('row', 0),
                            column=widget_config.get('column', 0),
                            width=widget_config.get('width', 1),
                            height=widget_config.get('height', 1),
                            size=WidgetSize(widget_config.get('size', 'medium')),
                            config=widget_config.get('config', {}),
                            created_by=owner
                        )
                        tab.add_widget(widget)
                
                layout.add_tab(tab)
        
        # Update usage
        self.usage_count += 1
        
        return layout
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'properties': {
                'layout_type': self.layout_type.value,
                'preview_image': self.preview_image,
                'tags': self.tags
            },
            'template_config': self.template_config,
            'usage': {
                'usage_count': self.usage_count,
                'rating': self.rating
            },
            'metadata': {
                'created_at': self.created_at.isoformat(),
                'created_by': self.created_by
            }
        }


@dataclass
class LayoutChange:
    """Record of layout changes for undo/redo functionality."""
    change_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    layout_id: str = ""
    change_type: str = ""  # add_tab, remove_tab, move_widget, etc.
    
    # Change details
    description: str = ""
    old_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    user: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'change_id': self.change_id,
            'layout_id': self.layout_id,
            'change_type': self.change_type,
            'description': self.description,
            'old_state': self.old_state,
            'new_state': self.new_state,
            'timestamp': self.timestamp.isoformat(),
            'user': self.user
        }