"""
Monitoring and event widgets for dashboard display.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

from .base_widget import BaseWidget, WidgetConfig
from ..layout.models import WidgetType, WidgetSize


class EventStreamWidget(BaseWidget):
    """Widget for displaying real-time event stream."""
    
    widget_type = WidgetType.EVENT_STREAM
    widget_name = "Event Stream"
    widget_description = "Real-time event stream display with filtering"
    widget_icon = "📡"
    widget_category = "Events"
    default_size = WidgetSize.WIDE
    
    config_schema = {
        'event_types': {'type': 'multiselect', 'options': ['system', 'process', 'queue', 'error', 'warning', 'info'], 'default': ['system', 'process', 'queue'], 'description': 'Event types to display'},
        'max_events': {'type': 'number', 'min': 10, 'max': 1000, 'default': 50, 'description': 'Maximum events to display'},
        'auto_scroll': {'type': 'boolean', 'default': True, 'description': 'Auto-scroll to latest events'},
        'show_timestamps': {'type': 'boolean', 'default': True, 'description': 'Show event timestamps'},
        'compact_view': {'type': 'boolean', 'default': False, 'description': 'Use compact display format'}
    }
    
    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self._sample_events = self._generate_sample_events()
    
    def _generate_sample_events(self) -> List[Dict[str, Any]]:
        """Generate sample events for demonstration."""
        events = []
        now = datetime.now()
        
        event_templates = [
            {'type': 'system', 'severity': 'info', 'message': 'System startup completed', 'source': 'system'},
            {'type': 'process', 'severity': 'info', 'message': 'MCP server started successfully', 'source': 'mcp'},
            {'type': 'queue', 'severity': 'info', 'message': 'Document processed: example.pdf', 'source': 'queue'},
            {'type': 'system', 'severity': 'warning', 'message': 'High CPU usage detected: 85%', 'source': 'monitor'},
            {'type': 'error', 'severity': 'error', 'message': 'Failed to connect to Qdrant database', 'source': 'qdrant'},
            {'type': 'process', 'severity': 'warning', 'message': 'PM2 process restart: ansera-worker', 'source': 'pm2'},
            {'type': 'queue', 'severity': 'info', 'message': 'Queue processing rate: 15 docs/min', 'source': 'queue'},
            {'type': 'system', 'severity': 'info', 'message': 'Scheduled backup completed', 'source': 'scheduler'},
            {'type': 'warning', 'severity': 'warning', 'message': 'Memory usage above 80%', 'source': 'monitor'},
            {'type': 'info', 'severity': 'info', 'message': 'Dashboard accessed by user', 'source': 'web'}
        ]
        
        for i in range(30):  # Generate 30 sample events
            template = event_templates[i % len(event_templates)]
            event_time = now - timedelta(minutes=i * 2)
            
            events.append({
                'id': str(uuid.uuid4())[:8],
                'timestamp': event_time,
                'type': template['type'],
                'severity': template['severity'],
                'source': template['source'],
                'message': template['message'],
                'details': f"Event details for {template['message']}..."
            })
        
        return sorted(events, key=lambda x: x['timestamp'], reverse=True)
    
    def _render_content(self) -> None:
        """Render event stream content."""
        try:
            event_types = self.config.config.get('event_types', ['system', 'process', 'queue'])
            max_events = self.config.config.get('max_events', 50)
            auto_scroll = self.config.config.get('auto_scroll', True)
            show_timestamps = self.config.config.get('show_timestamps', True)
            compact_view = self.config.config.get('compact_view', False)
            
            # Filter events by type
            filtered_events = [
                event for event in self._sample_events 
                if event['type'] in event_types
            ][:max_events]
            
            if not filtered_events:
                st.info("No events match the current filter criteria")
                return
            
            # Event controls
            self._render_event_controls()
            
            # Event list
            if compact_view:
                self._render_compact_events(filtered_events, show_timestamps)
            else:
                self._render_detailed_events(filtered_events, show_timestamps)
                
        except Exception as e:
            st.error(f"Failed to render event stream: {e}")
    
    def _render_event_controls(self) -> None:
        """Render event stream controls."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh", key=f"refresh_events_{self.config.widget_id}"):
                self._sample_events = self._generate_sample_events()
                st.rerun()
        
        with col2:
            if st.button("⏸️ Pause", key=f"pause_events_{self.config.widget_id}"):
                st.info("Event stream paused")
        
        with col3:
            if st.button("🗑️ Clear", key=f"clear_events_{self.config.widget_id}"):
                self._sample_events = []
                st.success("Event stream cleared")
    
    def _render_compact_events(self, events: List[Dict[str, Any]], show_timestamps: bool) -> None:
        """Render events in compact format."""
        st.markdown("#### Recent Events")
        
        for event in events:
            severity_emoji = {
                'info': '🔵',
                'warning': '🟡',
                'error': '🔴',
                'critical': '🟣'
            }.get(event['severity'], '⚪')
            
            timestamp_str = event['timestamp'].strftime('%H:%M:%S') if show_timestamps else ''
            
            event_line = f"{severity_emoji} {timestamp_str} **{event['source']}**: {event['message']}"
            st.markdown(event_line)
    
    def _render_detailed_events(self, events: List[Dict[str, Any]], show_timestamps: bool) -> None:
        """Render events in detailed format."""
        st.markdown("#### Event Stream")
        
        for event in events:
            severity_colors = {
                'info': '#E3F2FD',
                'warning': '#FFF3E0',
                'error': '#FFEBEE',
                'critical': '#F3E5F5'
            }
            
            bg_color = severity_colors.get(event['severity'], '#F5F5F5')
            
            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        background-color: {bg_color}; 
                        padding: 10px; 
                        border-radius: 5px; 
                        margin-bottom: 5px;
                        border-left: 4px solid {'#2196F3' if event['severity'] == 'info' else '#FF9800' if event['severity'] == 'warning' else '#F44336' if event['severity'] == 'error' else '#9C27B0'};
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong>{event['source'].upper()}</strong>
                            <small>{event['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if show_timestamps else ''}</small>
                        </div>
                        <div style="margin-top: 5px;">
                            {event['message']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    def get_config_ui(self) -> Dict[str, Any]:
        """Get configuration UI for event stream widget."""
        config_values = super().get_config_ui()
        
        # Widget-specific configuration
        with st.expander("Event Stream Settings"):
            config_values['event_types'] = st.multiselect(
                "Event Types to Display",
                options=['system', 'process', 'queue', 'error', 'warning', 'info'],
                default=self.config.config.get('event_types', ['system', 'process', 'queue']),
                key=f"config_event_types_{self.config.widget_id}"
            )
            
            config_values['max_events'] = st.slider(
                "Maximum Events",
                min_value=10,
                max_value=1000,
                value=self.config.config.get('max_events', 50),
                key=f"config_max_events_{self.config.widget_id}"
            )
            
            config_values['auto_scroll'] = st.checkbox(
                "Auto-scroll to Latest",
                value=self.config.config.get('auto_scroll', True),
                key=f"config_auto_scroll_{self.config.widget_id}"
            )
            
            config_values['show_timestamps'] = st.checkbox(
                "Show Timestamps",
                value=self.config.config.get('show_timestamps', True),
                key=f"config_show_timestamps_{self.config.widget_id}"
            )
            
            config_values['compact_view'] = st.checkbox(
                "Compact View",
                value=self.config.config.get('compact_view', False),
                key=f"config_compact_view_{self.config.widget_id}"
            )
        
        return config_values


class NotificationPanelWidget(BaseWidget):
    """Widget for displaying active notifications and alerts."""
    
    widget_type = WidgetType.NOTIFICATION_PANEL
    widget_name = "Notification Panel"
    widget_description = "Active notifications and alert management"
    widget_icon = "🔔"
    widget_category = "Notifications"
    default_size = WidgetSize.MEDIUM
    
    config_schema = {
        'notification_types': {'type': 'multiselect', 'options': ['toast', 'email', 'push', 'webhook'], 'default': ['toast'], 'description': 'Notification types to display'},
        'show_dismissed': {'type': 'boolean', 'default': False, 'description': 'Show dismissed notifications'},
        'auto_dismiss': {'type': 'boolean', 'default': True, 'description': 'Auto-dismiss old notifications'},
        'group_by_source': {'type': 'boolean', 'default': True, 'description': 'Group notifications by source'}
    }
    
    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self._sample_notifications = self._generate_sample_notifications()
    
    def _generate_sample_notifications(self) -> List[Dict[str, Any]]:
        """Generate sample notifications for demonstration."""
        notifications = []
        now = datetime.now()
        
        notification_templates = [
            {
                'type': 'toast',
                'severity': 'warning',
                'title': 'High CPU Usage',
                'message': 'CPU usage has exceeded 85% for the last 5 minutes',
                'source': 'system_monitor',
                'action_required': True
            },
            {
                'type': 'email',
                'severity': 'error',
                'title': 'Service Failure',
                'message': 'MCP server has stopped responding',
                'source': 'process_monitor',
                'action_required': True
            },
            {
                'type': 'toast',
                'severity': 'info',
                'title': 'Backup Complete',
                'message': 'Daily backup completed successfully',
                'source': 'scheduler',
                'action_required': False
            },
            {
                'type': 'push',
                'severity': 'warning',
                'title': 'Queue Full',
                'message': 'Document processing queue is at 95% capacity',
                'source': 'queue_monitor',
                'action_required': True
            },
            {
                'type': 'toast',
                'severity': 'info',
                'title': 'Update Available',
                'message': 'A new version of the monitoring system is available',
                'source': 'updater',
                'action_required': False
            }
        ]
        
        for i, template in enumerate(notification_templates):
            notification_time = now - timedelta(minutes=i * 15)
            
            notifications.append({
                'id': str(uuid.uuid4())[:8],
                'timestamp': notification_time,
                'type': template['type'],
                'severity': template['severity'],
                'title': template['title'],
                'message': template['message'],
                'source': template['source'],
                'action_required': template['action_required'],
                'dismissed': i > 2,  # First 3 are active
                'read': i > 1  # First 2 are unread
            })
        
        return sorted(notifications, key=lambda x: x['timestamp'], reverse=True)
    
    def _render_content(self) -> None:
        """Render notification panel content."""
        try:
            notification_types = self.config.config.get('notification_types', ['toast'])
            show_dismissed = self.config.config.get('show_dismissed', False)
            auto_dismiss = self.config.config.get('auto_dismiss', True)
            group_by_source = self.config.config.get('group_by_source', True)
            
            # Filter notifications
            filtered_notifications = [
                notif for notif in self._sample_notifications
                if notif['type'] in notification_types and (show_dismissed or not notif['dismissed'])
            ]
            
            if not filtered_notifications:
                st.info("No active notifications")
                return
            
            # Notification summary
            self._render_notification_summary(filtered_notifications)
            
            # Notification list
            if group_by_source:
                self._render_grouped_notifications(filtered_notifications)
            else:
                self._render_notification_list(filtered_notifications)
            
            # Notification controls
            self._render_notification_controls()
            
        except Exception as e:
            st.error(f"Failed to render notification panel: {e}")
    
    def _render_notification_summary(self, notifications: List[Dict[str, Any]]) -> None:
        """Render notification summary metrics."""
        unread_count = sum(1 for n in notifications if not n['read'])
        action_required_count = sum(1 for n in notifications if n['action_required'] and not n['dismissed'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total", len(notifications))
        
        with col2:
            st.metric("Unread", unread_count, delta=f"{unread_count} new")
        
        with col3:
            st.metric("Action Required", action_required_count, delta_color="inverse")
    
    def _render_grouped_notifications(self, notifications: List[Dict[str, Any]]) -> None:
        """Render notifications grouped by source."""
        # Group by source
        grouped = {}
        for notif in notifications:
            source = notif['source']
            if source not in grouped:
                grouped[source] = []
            grouped[source].append(notif)
        
        for source, source_notifications in grouped.items():
            with st.expander(f"📁 {source.replace('_', ' ').title()} ({len(source_notifications)})", expanded=True):
                for notif in source_notifications:
                    self._render_notification_item(notif)
    
    def _render_notification_list(self, notifications: List[Dict[str, Any]]) -> None:
        """Render notifications as a simple list."""
        st.markdown("#### Active Notifications")
        
        for notif in notifications:
            self._render_notification_item(notif)
    
    def _render_notification_item(self, notification: Dict[str, Any]) -> None:
        """Render individual notification item."""
        severity_icons = {
            'info': '🔵',
            'warning': '🟡',
            'error': '🔴',
            'critical': '🟣'
        }
        
        severity_colors = {
            'info': '#E3F2FD',
            'warning': '#FFF3E0',
            'error': '#FFEBEE',
            'critical': '#F3E5F5'
        }
        
        icon = severity_icons.get(notification['severity'], '⚪')
        bg_color = severity_colors.get(notification['severity'], '#F5F5F5')
        
        # Notification styling
        read_style = "opacity: 0.6;" if notification['read'] else ""
        action_badge = "🔥 ACTION REQUIRED" if notification['action_required'] else ""
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(
                f"""
                <div style="
                    background-color: {bg_color}; 
                    padding: 8px; 
                    border-radius: 4px; 
                    margin-bottom: 5px;
                    {read_style}
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>{icon} <strong>{notification['title']}</strong> {action_badge}</span>
                        <small>{notification['timestamp'].strftime('%H:%M')}</small>
                    </div>
                    <div style="margin-top: 3px; font-size: 0.9em;">
                        {notification['message']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            col2a, col2b = st.columns(2)
            
            with col2a:
                if st.button("✓", key=f"read_{notification['id']}", help="Mark as read"):
                    notification['read'] = True
                    st.rerun()
            
            with col2b:
                if st.button("✕", key=f"dismiss_{notification['id']}", help="Dismiss"):
                    notification['dismissed'] = True
                    st.rerun()
    
    def _render_notification_controls(self) -> None:
        """Render notification control buttons."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✓ Mark All Read", key=f"mark_all_read_{self.config.widget_id}"):
                for notif in self._sample_notifications:
                    notif['read'] = True
                st.success("All notifications marked as read")
                st.rerun()
        
        with col2:
            if st.button("✕ Dismiss All", key=f"dismiss_all_{self.config.widget_id}"):
                for notif in self._sample_notifications:
                    notif['dismissed'] = True
                st.success("All notifications dismissed")
                st.rerun()
        
        with col3:
            if st.button("🔄 Refresh", key=f"refresh_notifications_{self.config.widget_id}"):
                self._sample_notifications = self._generate_sample_notifications()
                st.rerun()
    
    def get_config_ui(self) -> Dict[str, Any]:
        """Get configuration UI for notification panel widget."""
        config_values = super().get_config_ui()
        
        # Widget-specific configuration
        with st.expander("Notification Panel Settings"):
            config_values['notification_types'] = st.multiselect(
                "Notification Types",
                options=['toast', 'email', 'push', 'webhook'],
                default=self.config.config.get('notification_types', ['toast']),
                key=f"config_notif_types_{self.config.widget_id}"
            )
            
            config_values['show_dismissed'] = st.checkbox(
                "Show Dismissed Notifications",
                value=self.config.config.get('show_dismissed', False),
                key=f"config_show_dismissed_{self.config.widget_id}"
            )
            
            config_values['auto_dismiss'] = st.checkbox(
                "Auto-dismiss Old Notifications",
                value=self.config.config.get('auto_dismiss', True),
                key=f"config_auto_dismiss_{self.config.widget_id}"
            )
            
            config_values['group_by_source'] = st.checkbox(
                "Group by Source",
                value=self.config.config.get('group_by_source', True),
                key=f"config_group_by_source_{self.config.widget_id}"
            )
        
        return config_values


class ConnectionStatusWidget(BaseWidget):
    """Widget for displaying connection health and status."""
    
    widget_type = WidgetType.CONNECTION_STATUS
    widget_name = "Connection Status"
    widget_description = "Connection health monitoring and status display"
    widget_icon = "🔌"
    widget_category = "Connections"
    default_size = WidgetSize.MEDIUM
    
    config_schema = {
        'connection_types': {'type': 'multiselect', 'options': ['database', 'api', 'service', 'external'], 'default': ['database', 'api', 'service'], 'description': 'Connection types to monitor'},
        'show_details': {'type': 'boolean', 'default': True, 'description': 'Show connection details'},
        'alert_on_failure': {'type': 'boolean', 'default': True, 'description': 'Alert on connection failures'},
        'check_interval': {'type': 'number', 'min': 5, 'max': 300, 'default': 30, 'description': 'Health check interval (seconds)'}
    }
    
    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self._sample_connections = self._generate_sample_connections()
    
    def _generate_sample_connections(self) -> List[Dict[str, Any]]:
        """Generate sample connection data."""
        connections = [
            {
                'name': 'Qdrant Database',
                'type': 'database',
                'status': 'healthy',
                'response_time': 15,
                'last_check': datetime.now() - timedelta(seconds=30),
                'uptime': 99.8,
                'error_message': None
            },
            {
                'name': 'MCP Server',
                'type': 'service',
                'status': 'healthy',
                'response_time': 8,
                'last_check': datetime.now() - timedelta(seconds=25),
                'uptime': 99.9,
                'error_message': None
            },
            {
                'name': 'External API',
                'type': 'api',
                'status': 'warning',
                'response_time': 250,
                'last_check': datetime.now() - timedelta(seconds=45),
                'uptime': 98.5,
                'error_message': 'Slow response time'
            },
            {
                'name': 'Email Service',
                'type': 'service',
                'status': 'critical',
                'response_time': None,
                'last_check': datetime.now() - timedelta(minutes=5),
                'uptime': 95.2,
                'error_message': 'Connection timeout'
            },
            {
                'name': 'File Storage',
                'type': 'external',
                'status': 'healthy',
                'response_time': 45,
                'last_check': datetime.now() - timedelta(seconds=20),
                'uptime': 99.6,
                'error_message': None
            }
        ]
        
        return connections
    
    def _render_content(self) -> None:
        """Render connection status content."""
        try:
            connection_types = self.config.config.get('connection_types', ['database', 'api', 'service'])
            show_details = self.config.config.get('show_details', True)
            alert_on_failure = self.config.config.get('alert_on_failure', True)
            
            # Filter connections by type
            filtered_connections = [
                conn for conn in self._sample_connections
                if conn['type'] in connection_types
            ]
            
            if not filtered_connections:
                st.info("No connections match the filter criteria")
                return
            
            # Connection summary
            self._render_connection_summary(filtered_connections)
            
            # Connection list
            if show_details:
                self._render_detailed_connections(filtered_connections)
            else:
                self._render_compact_connections(filtered_connections)
            
            # Show alerts if enabled
            if alert_on_failure:
                self._render_connection_alerts(filtered_connections)
                
        except Exception as e:
            st.error(f"Failed to render connection status: {e}")
    
    def _render_connection_summary(self, connections: List[Dict[str, Any]]) -> None:
        """Render connection summary metrics."""
        healthy_count = sum(1 for c in connections if c['status'] == 'healthy')
        warning_count = sum(1 for c in connections if c['status'] == 'warning')
        critical_count = sum(1 for c in connections if c['status'] == 'critical')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", len(connections))
        
        with col2:
            st.metric("🟢 Healthy", healthy_count)
        
        with col3:
            st.metric("🟡 Warning", warning_count, delta_color="inverse")
        
        with col4:
            st.metric("🔴 Critical", critical_count, delta_color="inverse")
    
    def _render_detailed_connections(self, connections: List[Dict[str, Any]]) -> None:
        """Render detailed connection information."""
        st.markdown("#### Connection Details")
        
        for conn in connections:
            status_colors = {
                'healthy': '#E8F5E8',
                'warning': '#FFF3CD',
                'critical': '#F8D7DA'
            }
            
            status_icons = {
                'healthy': '🟢',
                'warning': '🟡',
                'critical': '🔴'
            }
            
            bg_color = status_colors.get(conn['status'], '#F5F5F5')
            icon = status_icons.get(conn['status'], '⚪')
            
            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        background-color: {bg_color}; 
                        padding: 12px; 
                        border-radius: 6px; 
                        margin-bottom: 8px;
                        border-left: 4px solid {'#28a745' if conn['status'] == 'healthy' else '#ffc107' if conn['status'] == 'warning' else '#dc3545'};
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div>
                                <strong>{icon} {conn['name']}</strong>
                                <span style="margin-left: 10px; padding: 2px 8px; background-color: rgba(0,0,0,0.1); border-radius: 12px; font-size: 0.8em;">
                                    {conn['type'].upper()}
                                </span>
                            </div>
                            <small>Last check: {conn['last_check'].strftime('%H:%M:%S')}</small>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 0.9em;">
                            <div>
                                <strong>Response Time:</strong><br>
                                {f"{conn['response_time']}ms" if conn['response_time'] else "N/A"}
                            </div>
                            <div>
                                <strong>Uptime:</strong><br>
                                {conn['uptime']:.1f}%
                            </div>
                            <div>
                                <strong>Status:</strong><br>
                                {conn['status'].title()}
                            </div>
                        </div>
                        {f'<div style="margin-top: 8px; color: #dc3545;"><strong>Error:</strong> {conn["error_message"]}</div>' if conn['error_message'] else ''}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    def _render_compact_connections(self, connections: List[Dict[str, Any]]) -> None:
        """Render connections in compact format."""
        st.markdown("#### Connections")
        
        for conn in connections:
            status_icons = {
                'healthy': '🟢',
                'warning': '🟡',
                'critical': '🔴'
            }
            
            icon = status_icons.get(conn['status'], '⚪')
            response_time = f" ({conn['response_time']}ms)" if conn['response_time'] else ""
            
            st.markdown(f"{icon} **{conn['name']}** - {conn['status'].title()}{response_time}")
    
    def _render_connection_alerts(self, connections: List[Dict[str, Any]]) -> None:
        """Render connection alerts for failed connections."""
        failed_connections = [c for c in connections if c['status'] in ['warning', 'critical']]
        
        if failed_connections:
            st.markdown("#### ⚠️ Connection Alerts")
            
            for conn in failed_connections:
                alert_type = "warning" if conn['status'] == 'warning' else "error"
                
                if alert_type == "warning":
                    st.warning(f"**{conn['name']}**: {conn['error_message'] or 'Performance degraded'}")
                else:
                    st.error(f"**{conn['name']}**: {conn['error_message'] or 'Connection failed'}")
    
    def get_config_ui(self) -> Dict[str, Any]:
        """Get configuration UI for connection status widget."""
        config_values = super().get_config_ui()
        
        # Widget-specific configuration
        with st.expander("Connection Status Settings"):
            config_values['connection_types'] = st.multiselect(
                "Connection Types to Monitor",
                options=['database', 'api', 'service', 'external'],
                default=self.config.config.get('connection_types', ['database', 'api', 'service']),
                key=f"config_conn_types_{self.config.widget_id}"
            )
            
            config_values['show_details'] = st.checkbox(
                "Show Connection Details",
                value=self.config.config.get('show_details', True),
                key=f"config_show_details_{self.config.widget_id}"
            )
            
            config_values['alert_on_failure'] = st.checkbox(
                "Alert on Connection Failures",
                value=self.config.config.get('alert_on_failure', True),
                key=f"config_alert_failure_{self.config.widget_id}"
            )
            
            config_values['check_interval'] = st.slider(
                "Health Check Interval (seconds)",
                min_value=5,
                max_value=300,
                value=self.config.config.get('check_interval', 30),
                key=f"config_check_interval_{self.config.widget_id}"
            )
        
        return config_values