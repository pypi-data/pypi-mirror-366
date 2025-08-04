"""
Dashboard layout management service.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from collections import deque
from threading import RLock
import sqlite3

from .models import (
    LayoutType, WidgetType, WidgetSize,
    DashboardWidget, DashboardTab, DashboardLayout,
    LayoutTemplate, LayoutChange
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class LayoutManager:
    """
    Manages dashboard layouts, templates, and customization.
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize layout manager."""
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # Data directory
        if data_dir is None:
            data_dir = os.path.expanduser("~/.ansera/monitoring/layouts")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Database connection
        self.db_path = os.path.join(self.data_dir, "layouts.db")
        self._init_database()
        
        # In-memory storage
        self._layouts: Dict[str, DashboardLayout] = {}
        self._templates: Dict[str, LayoutTemplate] = {}
        self._change_history: deque = deque(maxlen=1000)
        
        # Callbacks
        self._layout_callbacks: List[Callable[[str, str], None]] = []  # layout_id, action
        
        # Load data
        self._load_layouts()
        self._load_templates()
        self._create_default_templates()
        
        logger.info("LayoutManager initialized")
    
    def _init_database(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS layouts (
                    layout_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    layout_type TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT FALSE,
                    is_default BOOLEAN DEFAULT FALSE,
                    shared BOOLEAN DEFAULT FALSE,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS templates (
                    template_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    layout_type TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    rating REAL DEFAULT 0.0,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT DEFAULT 'system'
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS layout_changes (
                    change_id TEXT PRIMARY KEY,
                    layout_id TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    description TEXT,
                    old_state TEXT,
                    new_state TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user TEXT DEFAULT 'system'
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_layouts_owner ON layouts(owner)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_layouts_active ON layouts(is_active)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_changes_layout ON layout_changes(layout_id)')
    
    def _load_layouts(self):
        """Load layouts from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM layouts')
            
            for row in cursor.fetchall():
                try:
                    data = json.loads(row['data'])
                    layout = self._dict_to_layout(data)
                    layout.layout_id = row['layout_id']
                    self._layouts[layout.layout_id] = layout
                except Exception as e:
                    logger.error(f"Error loading layout {row['layout_id']}: {e}")
    
    def _load_templates(self):
        """Load templates from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM templates')
            
            for row in cursor.fetchall():
                try:
                    data = json.loads(row['data'])
                    template = self._dict_to_template(data)
                    template.template_id = row['template_id']
                    template.usage_count = row['usage_count']
                    template.rating = row['rating']
                    self._templates[template.template_id] = template
                except Exception as e:
                    logger.error(f"Error loading template {row['template_id']}: {e}")
    
    def _create_default_templates(self):
        """Create default layout templates."""
        # Standard monitoring template
        if not any(t.name == "Standard Monitoring" for t in self._templates.values()):
            standard_template = LayoutTemplate(
                name="Standard Monitoring",
                description="Standard monitoring dashboard with all essential tabs",
                category="monitoring",
                layout_type=LayoutType.STANDARD,
                tags=["monitoring", "standard", "complete"],
                template_config={
                    'global_settings': {
                        'theme': 'light',
                        'sidebar_collapsed': False,
                        'show_breadcrumbs': True,
                        'show_header': True,
                        'show_footer': True
                    },
                    'tabs': [
                        {
                            'name': 'System Overview',
                            'icon': '📊',
                            'visible': True,
                            'widgets': [
                                {
                                    'widget_type': 'system_overview',
                                    'title': 'System Metrics',
                                    'row': 0, 'column': 0,
                                    'width': 2, 'height': 1,
                                    'size': 'large'
                                },
                                {
                                    'widget_type': 'process_control',
                                    'title': 'Process Control',
                                    'row': 0, 'column': 2,
                                    'width': 1, 'height': 1,
                                    'size': 'medium'
                                }
                            ]
                        },
                        {
                            'name': 'Performance',
                            'icon': '⚡',
                            'visible': True,
                            'widgets': [
                                {
                                    'widget_type': 'performance_graph',
                                    'title': 'Performance Trends',
                                    'row': 0, 'column': 0,
                                    'width': 3, 'height': 2,
                                    'size': 'full'
                                }
                            ]
                        }
                    ]
                }
            )
            self.save_template(standard_template)
        
        # Compact template
        if not any(t.name == "Compact View" for t in self._templates.values()):
            compact_template = LayoutTemplate(
                name="Compact View",
                description="Minimal dashboard for small screens",
                category="mobile",
                layout_type=LayoutType.COMPACT,
                tags=["compact", "mobile", "minimal"],
                template_config={
                    'global_settings': {
                        'theme': 'light',
                        'sidebar_collapsed': True,
                        'show_breadcrumbs': False,
                        'show_header': True,
                        'show_footer': False
                    },
                    'tabs': [
                        {
                            'name': 'Overview',
                            'icon': '📱',
                            'visible': True,
                            'grid_columns': 6,
                            'widgets': [
                                {
                                    'widget_type': 'system_overview',
                                    'title': 'Status',
                                    'row': 0, 'column': 0,
                                    'width': 1, 'height': 1,
                                    'size': 'small'
                                }
                            ]
                        }
                    ]
                }
            )
            self.save_template(compact_template)
    
    def create_layout(self, name: str, layout_type: LayoutType = LayoutType.CUSTOM,
                     owner: str = "system", template_id: Optional[str] = None) -> str:
        """Create a new dashboard layout."""
        with self._lock:
            if template_id and template_id in self._templates:
                # Create from template
                layout = self._templates[template_id].create_layout(name, owner)
            else:
                # Create empty layout
                layout = DashboardLayout(
                    name=name,
                    layout_type=layout_type,
                    owner=owner
                )
                
                # Add default system overview tab
                overview_tab = DashboardTab(
                    name="System Overview",
                    icon="📊",
                    visible=True,
                    order=0
                )
                
                # Add default system overview widget
                overview_widget = DashboardWidget(
                    widget_type=WidgetType.SYSTEM_OVERVIEW,
                    title="System Metrics",
                    row=0,
                    column=0,
                    width=2,
                    height=1,
                    size=WidgetSize.LARGE,
                    created_by=owner
                )
                overview_tab.add_widget(overview_widget)
                layout.add_tab(overview_tab)
            
            # Save to database
            self._save_layout_to_db(layout)
            
            # Store in memory
            self._layouts[layout.layout_id] = layout
            
            # Record change
            self._record_change(LayoutChange(
                layout_id=layout.layout_id,
                change_type="create_layout",
                description=f"Created layout '{name}'",
                new_state=layout.to_dict(),
                user=owner
            ))
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.MONITORING,
                change_type=ChangeType.CREATE,
                description=f"Created dashboard layout: {name}",
                details={'layout_id': layout.layout_id, 'type': layout_type.value}
            )
            
            # Trigger callbacks
            for callback in self._layout_callbacks:
                try:
                    callback(layout.layout_id, "created")
                except Exception as e:
                    logger.error(f"Error in layout callback: {e}")
            
            return layout.layout_id
    
    def get_layout(self, layout_id: str) -> Optional[DashboardLayout]:
        """Get a layout by ID."""
        with self._lock:
            layout = self._layouts.get(layout_id)
            if layout:
                layout.last_used_at = datetime.now()
                layout.usage_count += 1
                self._save_layout_to_db(layout)
            return layout
    
    def get_layouts_by_owner(self, owner: str) -> List[DashboardLayout]:
        """Get all layouts owned by a user."""
        with self._lock:
            return [
                layout for layout in self._layouts.values()
                if layout.owner == owner or layout.shared
            ]
    
    def get_active_layout(self, owner: str) -> Optional[DashboardLayout]:
        """Get the active layout for a user."""
        with self._lock:
            for layout in self._layouts.values():
                if layout.is_active and (layout.owner == owner or layout.shared):
                    return layout
            return None
    
    def set_active_layout(self, layout_id: str, owner: str) -> bool:
        """Set a layout as active for a user."""
        with self._lock:
            layout = self._layouts.get(layout_id)
            if not layout or (layout.owner != owner and not layout.shared):
                return False
            
            # Deactivate other layouts for this owner
            for other_layout in self._layouts.values():
                if other_layout.owner == owner and other_layout.is_active:
                    other_layout.is_active = False
                    self._save_layout_to_db(other_layout)
            
            # Activate selected layout
            layout.is_active = True
            layout.last_used_at = datetime.now()
            layout.usage_count += 1
            self._save_layout_to_db(layout)
            
            # Record change
            self._record_change(LayoutChange(
                layout_id=layout_id,
                change_type="set_active",
                description=f"Set layout '{layout.name}' as active",
                user=owner
            ))
            
            return True
    
    def update_layout(self, layout_id: str, updates: Dict[str, Any], user: str = "system") -> bool:
        """Update a layout."""
        with self._lock:
            layout = self._layouts.get(layout_id)
            if not layout:
                return False
            
            old_state = layout.to_dict()
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(layout, key):
                    setattr(layout, key, value)
            
            layout.updated_at = datetime.now()
            
            # Save to database
            self._save_layout_to_db(layout)
            
            # Record change
            self._record_change(LayoutChange(
                layout_id=layout_id,
                change_type="update_layout",
                description=f"Updated layout '{layout.name}'",
                old_state=old_state,
                new_state=layout.to_dict(),
                user=user
            ))
            
            # Trigger callbacks
            for callback in self._layout_callbacks:
                try:
                    callback(layout_id, "updated")
                except Exception as e:
                    logger.error(f"Error in layout callback: {e}")
            
            return True
    
    def delete_layout(self, layout_id: str, user: str = "system") -> bool:
        """Delete a layout."""
        with self._lock:
            layout = self._layouts.get(layout_id)
            if not layout or layout.is_default:
                return False
            
            # Remove from memory
            del self._layouts[layout_id]
            
            # Remove from database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM layouts WHERE layout_id = ?', (layout_id,))
                conn.execute('DELETE FROM layout_changes WHERE layout_id = ?', (layout_id,))
            
            # Record change
            self._record_change(LayoutChange(
                layout_id=layout_id,
                change_type="delete_layout",
                description=f"Deleted layout '{layout.name}'",
                old_state=layout.to_dict(),
                user=user
            ))
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.MONITORING,
                change_type=ChangeType.DELETE,
                description=f"Deleted dashboard layout: {layout.name}",
                details={'layout_id': layout_id}
            )
            
            return True
    
    def clone_layout(self, layout_id: str, new_name: str, new_owner: str = "system") -> Optional[str]:
        """Clone an existing layout."""
        with self._lock:
            original = self._layouts.get(layout_id)
            if not original:
                return None
            
            cloned = original.clone(new_name, new_owner)
            
            # Save to database
            self._save_layout_to_db(cloned)
            
            # Store in memory
            self._layouts[cloned.layout_id] = cloned
            
            # Record change
            self._record_change(LayoutChange(
                layout_id=cloned.layout_id,
                change_type="clone_layout",
                description=f"Cloned layout '{original.name}' as '{new_name}'",
                new_state=cloned.to_dict(),
                user=new_owner
            ))
            
            return cloned.layout_id
    
    def add_tab_to_layout(self, layout_id: str, tab: DashboardTab, user: str = "system") -> bool:
        """Add a tab to a layout."""
        with self._lock:
            layout = self._layouts.get(layout_id)
            if not layout:
                return False
            
            old_state = layout.to_dict()
            layout.add_tab(tab)
            
            # Save to database
            self._save_layout_to_db(layout)
            
            # Record change
            self._record_change(LayoutChange(
                layout_id=layout_id,
                change_type="add_tab",
                description=f"Added tab '{tab.name}' to layout",
                old_state=old_state,
                new_state=layout.to_dict(),
                user=user
            ))
            
            return True
    
    def remove_tab_from_layout(self, layout_id: str, tab_id: str, user: str = "system") -> bool:
        """Remove a tab from a layout."""
        with self._lock:
            layout = self._layouts.get(layout_id)
            if not layout:
                return False
            
            old_state = layout.to_dict()
            success = layout.remove_tab(tab_id)
            
            if success:
                # Save to database
                self._save_layout_to_db(layout)
                
                # Record change
                self._record_change(LayoutChange(
                    layout_id=layout_id,
                    change_type="remove_tab",
                    description=f"Removed tab from layout",
                    old_state=old_state,
                    new_state=layout.to_dict(),
                    user=user
                ))
            
            return success
    
    def reorder_tabs(self, layout_id: str, tab_orders: Dict[str, int], user: str = "system") -> bool:
        """Reorder tabs in a layout."""
        with self._lock:
            layout = self._layouts.get(layout_id)
            if not layout:
                return False
            
            old_state = layout.to_dict()
            success = layout.reorder_tabs(tab_orders)
            
            if success:
                # Save to database
                self._save_layout_to_db(layout)
                
                # Record change
                self._record_change(LayoutChange(
                    layout_id=layout_id,
                    change_type="reorder_tabs",
                    description="Reordered tabs in layout",
                    old_state=old_state,
                    new_state=layout.to_dict(),
                    user=user
                ))
            
            return success
    
    def add_widget_to_tab(self, layout_id: str, tab_id: str, widget: DashboardWidget, user: str = "system") -> bool:
        """Add a widget to a tab."""
        with self._lock:
            layout = self._layouts.get(layout_id)
            if not layout:
                return False
            
            tab = layout.get_tab(tab_id)
            if not tab:
                return False
            
            old_state = layout.to_dict()
            tab.add_widget(widget)
            layout.updated_at = datetime.now()
            
            # Save to database
            self._save_layout_to_db(layout)
            
            # Record change
            self._record_change(LayoutChange(
                layout_id=layout_id,
                change_type="add_widget",
                description=f"Added widget '{widget.title}' to tab '{tab.name}'",
                old_state=old_state,
                new_state=layout.to_dict(),
                user=user
            ))
            
            return True
    
    def remove_widget_from_tab(self, layout_id: str, tab_id: str, widget_id: str, user: str = "system") -> bool:
        """Remove a widget from a tab."""
        with self._lock:
            layout = self._layouts.get(layout_id)
            if not layout:
                return False
            
            tab = layout.get_tab(tab_id)
            if not tab:
                return False
            
            old_state = layout.to_dict()
            success = tab.remove_widget(widget_id)
            
            if success:
                layout.updated_at = datetime.now()
                
                # Save to database
                self._save_layout_to_db(layout)
                
                # Record change
                self._record_change(LayoutChange(
                    layout_id=layout_id,
                    change_type="remove_widget",
                    description=f"Removed widget from tab '{tab.name}'",
                    old_state=old_state,
                    new_state=layout.to_dict(),
                    user=user
                ))
            
            return success
    
    def get_templates(self, category: Optional[str] = None) -> List[LayoutTemplate]:
        """Get layout templates."""
        with self._lock:
            templates = list(self._templates.values())
            if category:
                templates = [t for t in templates if t.category == category]
            return sorted(templates, key=lambda t: (t.category, t.name))
    
    def save_template(self, template: LayoutTemplate) -> str:
        """Save a layout template."""
        with self._lock:
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO templates 
                    (template_id, name, description, category, layout_type, usage_count, rating, data, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    template.template_id,
                    template.name,
                    template.description,
                    template.category,
                    template.layout_type.value,
                    template.usage_count,
                    template.rating,
                    json.dumps(template.to_dict()),
                    template.created_by
                ))
            
            # Store in memory
            self._templates[template.template_id] = template
            
            return template.template_id
    
    def get_change_history(self, layout_id: Optional[str] = None, limit: int = 100) -> List[LayoutChange]:
        """Get layout change history."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if layout_id:
                    cursor = conn.execute(
                        'SELECT * FROM layout_changes WHERE layout_id = ? ORDER BY timestamp DESC LIMIT ?',
                        (layout_id, limit)
                    )
                else:
                    cursor = conn.execute(
                        'SELECT * FROM layout_changes ORDER BY timestamp DESC LIMIT ?',
                        (limit,)
                    )
                
                changes = []
                for row in cursor.fetchall():
                    change = LayoutChange(
                        change_id=row['change_id'],
                        layout_id=row['layout_id'],
                        change_type=row['change_type'],
                        description=row['description'],
                        old_state=json.loads(row['old_state']) if row['old_state'] else None,
                        new_state=json.loads(row['new_state']) if row['new_state'] else None,
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        user=row['user']
                    )
                    changes.append(change)
                
                return changes
    
    def export_layout(self, layout_id: str) -> Optional[Dict[str, Any]]:
        """Export a layout to dictionary."""
        with self._lock:
            layout = self._layouts.get(layout_id)
            return layout.to_dict() if layout else None
    
    def import_layout(self, layout_data: Dict[str, Any], new_owner: str = "system") -> Optional[str]:
        """Import a layout from dictionary."""
        try:
            layout = self._dict_to_layout(layout_data)
            layout.owner = new_owner
            layout.is_active = False
            layout.is_default = False
            
            # Save to database
            self._save_layout_to_db(layout)
            
            # Store in memory
            self._layouts[layout.layout_id] = layout
            
            return layout.layout_id
        except Exception as e:
            logger.error(f"Error importing layout: {e}")
            return None
    
    def _save_layout_to_db(self, layout: DashboardLayout):
        """Save a layout to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO layouts 
                (layout_id, name, layout_type, owner, is_active, is_default, shared, data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                layout.layout_id,
                layout.name,
                layout.layout_type.value,
                layout.owner,
                layout.is_active,
                layout.is_default,
                layout.shared,
                json.dumps(layout.to_dict()),
                layout.updated_at.isoformat()
            ))
    
    def _record_change(self, change: LayoutChange):
        """Record a layout change."""
        self._change_history.append(change)
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO layout_changes 
                (change_id, layout_id, change_type, description, old_state, new_state, timestamp, user)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                change.change_id,
                change.layout_id,
                change.change_type,
                change.description,
                json.dumps(change.old_state) if change.old_state else None,
                json.dumps(change.new_state) if change.new_state else None,
                change.timestamp.isoformat(),
                change.user
            ))
    
    def _dict_to_layout(self, data: Dict[str, Any]) -> DashboardLayout:
        """Convert dictionary to DashboardLayout."""
        layout = DashboardLayout(
            layout_id=data.get('layout_id', ''),
            name=data.get('name', ''),
            layout_type=LayoutType(data.get('layout_type', 'standard')),
            is_active=data.get('properties', {}).get('is_active', False),
            is_default=data.get('properties', {}).get('is_default', False),
            shared=data.get('properties', {}).get('shared', False),
            owner=data.get('access', {}).get('owner', 'system'),
            allowed_users=data.get('access', {}).get('allowed_users', [])
        )
        
        # Global settings
        global_settings = data.get('global_settings', {})
        layout.theme = global_settings.get('theme', 'light')
        layout.sidebar_collapsed = global_settings.get('sidebar_collapsed', False)
        layout.show_breadcrumbs = global_settings.get('show_breadcrumbs', True)
        layout.show_header = global_settings.get('show_header', True)
        layout.show_footer = global_settings.get('show_footer', True)
        
        # Preferences
        preferences = data.get('preferences', {})
        layout.auto_save = preferences.get('auto_save', True)
        layout.save_interval_seconds = preferences.get('save_interval_seconds', 300)
        
        # Metadata
        metadata = data.get('metadata', {})
        if 'created_at' in metadata:
            layout.created_at = datetime.fromisoformat(metadata['created_at'])
        if 'updated_at' in metadata:
            layout.updated_at = datetime.fromisoformat(metadata['updated_at'])
        if 'last_used_at' in metadata and metadata['last_used_at']:
            layout.last_used_at = datetime.fromisoformat(metadata['last_used_at'])
        layout.usage_count = metadata.get('usage_count', 0)
        
        # Tabs
        for tab_data in data.get('tabs', []):
            tab = self._dict_to_tab(tab_data)
            layout.tabs.append(tab)
        
        return layout
    
    def _dict_to_tab(self, data: Dict[str, Any]) -> DashboardTab:
        """Convert dictionary to DashboardTab."""
        tab = DashboardTab(
            tab_id=data.get('tab_id', ''),
            name=data.get('name', ''),
            icon=data.get('icon', '📊'),
            visible=data.get('properties', {}).get('visible', True),
            order=data.get('properties', {}).get('order', 0),
            closable=data.get('properties', {}).get('closable', False),
            grid_columns=data.get('layout', {}).get('grid_columns', 12),
            grid_rows=data.get('layout', {}).get('grid_rows', 8),
            gap_size=data.get('layout', {}).get('gap_size', 10),
            config=data.get('config', {})
        )
        
        # Metadata
        metadata = data.get('metadata', {})
        if 'created_at' in metadata:
            tab.created_at = datetime.fromisoformat(metadata['created_at'])
        if 'updated_at' in metadata:
            tab.updated_at = datetime.fromisoformat(metadata['updated_at'])
        
        # Widgets
        for widget_data in data.get('widgets', []):
            widget = self._dict_to_widget(widget_data)
            tab.widgets.append(widget)
        
        return tab
    
    def _dict_to_widget(self, data: Dict[str, Any]) -> DashboardWidget:
        """Convert dictionary to DashboardWidget."""
        widget = DashboardWidget(
            widget_id=data.get('widget_id', ''),
            widget_type=WidgetType(data.get('widget_type', 'system_overview')),
            title=data.get('title', ''),
            row=data.get('position', {}).get('row', 0),
            column=data.get('position', {}).get('column', 0),
            width=data.get('position', {}).get('width', 1),
            height=data.get('position', {}).get('height', 1),
            size=WidgetSize(data.get('position', {}).get('size', 'medium')),
            visible=data.get('display', {}).get('visible', True),
            collapsible=data.get('display', {}).get('collapsible', True),
            collapsed=data.get('display', {}).get('collapsed', False),
            refreshable=data.get('display', {}).get('refreshable', True),
            auto_refresh=data.get('display', {}).get('auto_refresh', True),
            refresh_interval_seconds=data.get('display', {}).get('refresh_interval', 30),
            config=data.get('config', {}),
            background_color=data.get('style', {}).get('background_color'),
            border_color=data.get('style', {}).get('border_color'),
            text_color=data.get('style', {}).get('text_color'),
            custom_css=data.get('style', {}).get('custom_css'),
            created_by=data.get('metadata', {}).get('created_by', 'system')
        )
        
        # Metadata
        metadata = data.get('metadata', {})
        if 'created_at' in metadata:
            widget.created_at = datetime.fromisoformat(metadata['created_at'])
        if 'updated_at' in metadata:
            widget.updated_at = datetime.fromisoformat(metadata['updated_at'])
        
        return widget
    
    def _dict_to_template(self, data: Dict[str, Any]) -> LayoutTemplate:
        """Convert dictionary to LayoutTemplate."""
        template = LayoutTemplate(
            template_id=data.get('template_id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            category=data.get('category', 'general'),
            layout_type=LayoutType(data.get('properties', {}).get('layout_type', 'standard')),
            preview_image=data.get('properties', {}).get('preview_image'),
            tags=data.get('properties', {}).get('tags', []),
            template_config=data.get('template_config', {}),
            usage_count=data.get('usage', {}).get('usage_count', 0),
            rating=data.get('usage', {}).get('rating', 0.0),
            created_by=data.get('metadata', {}).get('created_by', 'system')
        )
        
        # Metadata
        metadata = data.get('metadata', {})
        if 'created_at' in metadata:
            template.created_at = datetime.fromisoformat(metadata['created_at'])
        
        return template
    
    def add_layout_callback(self, callback: Callable[[str, str], None]):
        """Add a callback for layout changes."""
        self._layout_callbacks.append(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get layout manager statistics."""
        with self._lock:
            return {
                'total_layouts': len(self._layouts),
                'active_layouts': len([l for l in self._layouts.values() if l.is_active]),
                'shared_layouts': len([l for l in self._layouts.values() if l.shared]),
                'total_templates': len(self._templates),
                'changes_recorded': len(self._change_history)
            }


# Singleton instance
_layout_manager: Optional[LayoutManager] = None
_manager_lock = RLock()


def get_layout_manager() -> LayoutManager:
    """Get singleton layout manager instance."""
    global _layout_manager
    
    with _manager_lock:
        if _layout_manager is None:
            _layout_manager = LayoutManager()
        
        return _layout_manager


def reset_layout_manager():
    """Reset the singleton layout manager."""
    global _layout_manager
    
    with _manager_lock:
        _layout_manager = None