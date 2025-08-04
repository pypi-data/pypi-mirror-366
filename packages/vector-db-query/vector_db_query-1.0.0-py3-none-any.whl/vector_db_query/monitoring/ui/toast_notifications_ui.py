"""
Toast notifications UI components for the monitoring dashboard.

This module provides Streamlit UI components for displaying and managing
toast notifications within the dashboard interface.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

from ..notifications.toast_manager import (
    ToastManager, ToastNotification, ToastType, ToastPosition, ToastSettings,
    get_toast_manager, toast_success, toast_info, toast_warning, toast_error
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class ToastNotificationUI:
    """
    UI components for toast notifications.
    
    Provides interface for displaying notifications, managing settings,
    and handling user interactions within Streamlit.
    """
    
    def __init__(self):
        """Initialize toast notification UI."""
        self.toast_manager = get_toast_manager()
        self.change_tracker = get_change_tracker()
        
        # Initialize session state for toast notifications
        if 'toast_notifications' not in st.session_state:
            st.session_state.toast_notifications = True
        
        if 'last_toast_check' not in st.session_state:
            st.session_state.last_toast_check = datetime.now()
    
    def render_toast_container(self, container_key: str = "main_toast_container"):
        """
        Render the main toast notification container.
        
        Args:
            container_key: Unique key for the container
        """
        # Check if notifications are enabled
        if not st.session_state.get('toast_notifications', True):
            return
        
        # Get active notifications
        notifications = self.toast_manager.get_active_notifications()
        
        if not notifications:
            return
        
        # Get current settings
        settings = self.toast_manager.get_settings()
        
        # Create container for notifications
        toast_container = st.container()
        
        with toast_container:
            # Apply positioning styles
            position_style = self._get_position_style(settings.position)
            
            # Create notification display area
            st.markdown(
                f"""
                <div id="{container_key}" style="{position_style}">
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display notifications
            for i, notification in enumerate(notifications[:settings.max_notifications]):
                self._render_toast_notification(notification, f"{container_key}_{i}")
    
    def _render_toast_notification(self, notification: ToastNotification, key: str):
        """Render a single toast notification."""
        # Get styling based on notification type
        type_config = self._get_type_config(notification.toast_type)
        
        # Create notification container
        with st.container():
            # Calculate time info
            time_ago = self._format_time_ago(notification.created_at)
            expires_in = ""
            
            if notification.expires_at and not notification.is_persistent:
                expires_in = self._format_time_remaining(notification.expires_at)
            
            # Create the notification HTML
            notification_html = f"""
            <div class="toast-notification {notification.toast_type.value}" 
                 style="
                     background: {type_config['bg_color']};
                     border-left: 4px solid {type_config['border_color']};
                     color: {type_config['text_color']};
                     padding: 12px 16px;
                     margin: 8px 0;
                     border-radius: 6px;
                     box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                     position: relative;
                     animation: slideIn 0.3s ease-out;
                 ">
                
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">
                            {type_config['icon']} {notification.title}
                        </div>
                        <div style="font-size: 13px; line-height: 1.4; margin-bottom: 6px;">
                            {notification.message}
                        </div>
                        <div style="font-size: 11px; opacity: 0.7;">
                            {time_ago}{' • ' + expires_in if expires_in else ''}
                            {' • ' + notification.source if notification.source != 'system' else ''}
                        </div>
                    </div>
                    
                    <div style="margin-left: 12px;">
                        <!-- Action and dismiss buttons will be handled by Streamlit components -->
                    </div>
                </div>
            </div>
            
            <style>
            @keyframes slideIn {{
                from {{
                    transform: translateX(100%);
                    opacity: 0;
                }}
                to {{
                    transform: translateX(0);
                    opacity: 1;
                }}
            }}
            
            .toast-notification {{
                transition: all 0.3s ease;
            }}
            
            .toast-notification:hover {{
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
            </style>
            """
            
            st.markdown(notification_html, unsafe_allow_html=True)
            
            # Action and dismiss buttons
            col1, col2 = st.columns([3, 1])
            
            with col2:
                button_col1, button_col2 = st.columns(2)
                
                # Action button
                if notification.action_text and notification.action_callback:
                    with button_col1:
                        if st.button(
                            notification.action_text,
                            key=f"action_{key}",
                            help="Execute action",
                            type="secondary"
                        ):
                            if self.toast_manager.execute_action(notification.id):
                                st.rerun()
                
                # Dismiss button
                if notification.is_dismissible:
                    with button_col2:
                        dismiss_text = "×" if notification.action_text else "Dismiss"
                        if st.button(
                            dismiss_text,
                            key=f"dismiss_{key}",
                            help="Dismiss notification",
                            type="secondary"
                        ):
                            if self.toast_manager.dismiss_notification(notification.id):
                                st.rerun()
    
    def render_notification_panel(self):
        """Render the notification management panel."""
        st.subheader("🔔 Notification Center")
        
        # Notification tabs
        notification_tabs = st.tabs(["Active", "Settings", "History", "Test"])
        
        with notification_tabs[0]:
            self._render_active_notifications()
        
        with notification_tabs[1]:
            self._render_notification_settings()
        
        with notification_tabs[2]:
            self._render_notification_history()
        
        with notification_tabs[3]:
            self._render_notification_test()
    
    def _render_active_notifications(self):
        """Render active notifications management."""
        st.write("### Active Notifications")
        
        # Get statistics
        stats = self.toast_manager.get_statistics()
        
        # Statistics display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active", stats['active_notifications'])
        
        with col2:
            st.metric("Dismissed", stats['dismissed_notifications'])
        
        with col3:
            persistent_count = stats.get('persistent_count', 0)
            st.metric("Persistent", persistent_count)
        
        with col4:
            error_count = stats['by_type'].get('error', 0)
            st.metric("Errors", error_count, delta="Issues" if error_count > 0 else None)
        
        # Active notifications list
        notifications = self.toast_manager.get_active_notifications()
        
        if notifications:
            # Bulk actions
            st.write("### Bulk Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🗑️ Dismiss All"):
                    dismissed_count = self.toast_manager.dismiss_all()
                    st.success(f"Dismissed {dismissed_count} notifications")
                    st.rerun()
            
            with col2:
                categories = list(set(n.category for n in notifications))
                if len(categories) > 1:
                    selected_category = st.selectbox("Category", categories)
                    if st.button(f"Dismiss {selected_category}"):
                        dismissed_count = self.toast_manager.dismiss_all(selected_category)
                        st.success(f"Dismissed {dismissed_count} notifications in {selected_category}")
                        st.rerun()
            
            with col3:
                if st.button("🧹 Clear Old"):
                    cleared_count = self.toast_manager.clear_dismissed(7)
                    st.success(f"Cleared {cleared_count} old dismissed notifications")
            
            # Notifications table
            st.write("### Notification Details")
            
            notification_data = []
            for notification in notifications:
                time_ago = self._format_time_ago(notification.created_at)
                expires_in = ""
                
                if notification.expires_at and not notification.is_persistent:
                    expires_in = self._format_time_remaining(notification.expires_at)
                
                notification_data.append({
                    'ID': notification.id[:8] + "...",
                    'Title': notification.title,
                    'Type': notification.toast_type.value.title(),
                    'Category': notification.category,
                    'Source': notification.source,
                    'Created': time_ago,
                    'Expires': expires_in if expires_in else "Never" if notification.is_persistent else "Auto",
                    'Persistent': '✅' if notification.is_persistent else '❌',
                    'Dismissible': '✅' if notification.is_dismissible else '❌'
                })
            
            # Display with action buttons
            for i, (notification, data) in enumerate(zip(notifications, notification_data)):
                with st.expander(f"{data['Type']} - {data['Title']}", expanded=i < 3):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Message:** {notification.message}")
                        st.write(f"**Created:** {data['Created']}")
                        st.write(f"**Category:** {data['Category']}")
                        st.write(f"**Source:** {data['Source']}")
                        
                        if notification.metadata:
                            st.write("**Metadata:**")
                            st.json(notification.metadata)
                    
                    with col2:
                        # Action button
                        if notification.action_text and notification.action_callback:
                            if st.button(
                                notification.action_text,
                                key=f"panel_action_{notification.id}",
                                type="primary"
                            ):
                                if self.toast_manager.execute_action(notification.id):
                                    st.success("Action executed")
                                    st.rerun()
                        
                        # Dismiss button
                        if notification.is_dismissible:
                            if st.button(
                                "Dismiss",
                                key=f"panel_dismiss_{notification.id}",
                                type="secondary"
                            ):
                                if self.toast_manager.dismiss_notification(notification.id):
                                    st.success("Notification dismissed")
                                    st.rerun()
        else:
            st.info("No active notifications")
    
    def _render_notification_settings(self):
        """Render notification settings."""
        st.write("### Notification Settings")
        
        # Get current settings
        current_settings = self.toast_manager.get_settings()
        
        # Settings form
        with st.form("toast_settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Display Settings:**")
                
                position = st.selectbox(
                    "Position",
                    [pos.value for pos in ToastPosition],
                    index=list(ToastPosition).index(current_settings.position),
                    format_func=lambda x: x.replace('-', ' ').title()
                )
                
                default_duration = st.number_input(
                    "Default Duration (seconds)",
                    min_value=1,
                    max_value=60,
                    value=current_settings.default_duration
                )
                
                max_notifications = st.number_input(
                    "Max Notifications",
                    min_value=1,
                    max_value=50,
                    value=current_settings.max_notifications
                )
                
                show_timestamps = st.checkbox(
                    "Show Timestamps",
                    value=current_settings.show_timestamps
                )
            
            with col2:
                st.write("**Behavior Settings:**")
                
                auto_dismiss = st.checkbox(
                    "Auto Dismiss",
                    value=current_settings.auto_dismiss,
                    help="Automatically dismiss expired notifications"
                )
                
                group_similar = st.checkbox(
                    "Group Similar",
                    value=current_settings.group_similar,
                    help="Group similar notifications together"
                )
                
                enable_animations = st.checkbox(
                    "Enable Animations",
                    value=current_settings.enable_animations
                )
                
                enable_sound = st.checkbox(
                    "Enable Sound",
                    value=current_settings.enable_sound,
                    help="Play sound for new notifications (if supported)"
                )
            
            submitted = st.form_submit_button("💾 Save Settings")
            
            if submitted:
                # Create new settings
                new_settings = ToastSettings(
                    position=ToastPosition(position),
                    default_duration=default_duration,
                    max_notifications=max_notifications,
                    auto_dismiss=auto_dismiss,
                    show_timestamps=show_timestamps,
                    enable_sound=enable_sound,
                    enable_animations=enable_animations,
                    group_similar=group_similar
                )
                
                if self.toast_manager.update_settings(new_settings):
                    st.success("Settings updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update settings")
        
        # Global notification toggle
        st.write("### Global Controls")
        
        notifications_enabled = st.checkbox(
            "Enable Toast Notifications",
            value=st.session_state.get('toast_notifications', True),
            help="Globally enable/disable toast notifications in the dashboard"
        )
        
        st.session_state.toast_notifications = notifications_enabled
        
        if not notifications_enabled:
            st.info("Toast notifications are disabled. Enable them to see notifications in the dashboard.")
    
    def _render_notification_history(self):
        """Render notification history."""
        st.write("### Notification History")
        
        # Get statistics with breakdown
        stats = self.toast_manager.get_statistics()
        
        # Display statistics
        if stats['by_type']:
            st.write("#### By Type")
            type_data = [{'Type': k.title(), 'Count': v} for k, v in stats['by_type'].items()]
            st.table(type_data)
        
        if stats['by_category']:
            st.write("#### By Category") 
            category_data = [{'Category': k.title(), 'Count': v} for k, v in stats['by_category'].items()]
            st.table(category_data)
        
        if stats['by_source']:
            st.write("#### By Source")
            source_data = [{'Source': k.title(), 'Count': v} for k, v in stats['by_source'].items()]
            st.table(source_data)
        
        # Export option
        if st.button("📤 Export History"):
            st.info("Export functionality coming soon!")
    
    def _render_notification_test(self):
        """Render notification testing interface."""
        st.write("### Test Notifications")
        
        # Test notification form
        with st.form("test_notification_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                test_title = st.text_input("Title", value="Test Notification")
                test_message = st.text_area("Message", value="This is a test notification message.")
                test_type = st.selectbox("Type", [t.value for t in ToastType])
            
            with col2:
                test_duration = st.number_input("Duration (seconds)", min_value=1, max_value=60, value=5)
                test_persistent = st.checkbox("Persistent")
                test_category = st.text_input("Category", value="test")
                test_source = st.text_input("Source", value="test_ui")
            
            # Action settings
            with_action = st.checkbox("Include Action Button")
            if with_action:
                action_text = st.text_input("Action Text", value="Click Me")
            else:
                action_text = None
            
            submitted = st.form_submit_button("📤 Send Test Notification")
            
            if submitted and test_title and test_message:
                # Register test action callback if needed
                if with_action:
                    def test_action_callback(notification):
                        toast_success("Action Executed", f"Test action for: {notification.title}")
                    
                    self.toast_manager.register_action_callback("test_action", test_action_callback)
                
                # Create test notification
                notification_id = self.toast_manager.create_notification(
                    title=test_title,
                    message=test_message,
                    toast_type=ToastType(test_type),
                    duration=None if test_persistent else test_duration,
                    is_persistent=test_persistent,
                    action_text=action_text,
                    action_callback="test_action" if with_action else None,
                    source=test_source,
                    category=test_category
                )
                
                if notification_id:
                    st.success(f"Test notification created! ID: {notification_id[:8]}...")
                    st.rerun()
                else:
                    st.error("Failed to create test notification")
        
        # Quick test buttons
        st.write("### Quick Tests")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Success"):
                toast_success("Success!", "Operation completed successfully", source="quick_test")
                st.rerun()
        
        with col2:
            if st.button("ℹ️ Info"):
                toast_info("Information", "This is an informational message", source="quick_test")
                st.rerun()
        
        with col3:
            if st.button("⚠️ Warning"):
                toast_warning("Warning", "Please check this warning message", source="quick_test")
                st.rerun()
        
        with col4:
            if st.button("❌ Error"):
                toast_error("Error", "Something went wrong!", source="quick_test")
                st.rerun()
    
    def _get_type_config(self, toast_type: ToastType) -> Dict[str, str]:
        """Get styling configuration for notification type."""
        configs = {
            ToastType.SUCCESS: {
                'bg_color': '#F0F9F4',
                'border_color': '#10B981',
                'text_color': '#065F46',
                'icon': '✅'
            },
            ToastType.INFO: {
                'bg_color': '#F0F9FF',
                'border_color': '#3B82F6',
                'text_color': '#1E3A8A',
                'icon': 'ℹ️'
            },
            ToastType.WARNING: {
                'bg_color': '#FFFBEB',
                'border_color': '#F59E0B',
                'text_color': '#92400E',
                'icon': '⚠️'
            },
            ToastType.ERROR: {
                'bg_color': '#FEF2F2',
                'border_color': '#EF4444',
                'text_color': '#991B1B',
                'icon': '❌'
            }
        }
        
        return configs.get(toast_type, configs[ToastType.INFO])
    
    def _get_position_style(self, position: ToastPosition) -> str:
        """Get CSS style for notification position."""
        base_style = """
            position: fixed;
            z-index: 1000;
            pointer-events: none;
            max-width: 400px;
            width: auto;
        """
        
        position_styles = {
            ToastPosition.TOP_RIGHT: "top: 20px; right: 20px;",
            ToastPosition.TOP_LEFT: "top: 20px; left: 20px;",
            ToastPosition.BOTTOM_RIGHT: "bottom: 20px; right: 20px;",
            ToastPosition.BOTTOM_LEFT: "bottom: 20px; left: 20px;",
            ToastPosition.CENTER: "top: 50%; left: 50%; transform: translate(-50%, -50%);"
        }
        
        return base_style + position_styles.get(position, position_styles[ToastPosition.TOP_RIGHT])
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format time as 'X ago' string."""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.total_seconds() < 60:
            return "Just now"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60) 
            return f"{minutes}m ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            days = int(diff.total_seconds() / 86400)
            return f"{days}d ago"
    
    def _format_time_remaining(self, expires_at: datetime) -> str:
        """Format remaining time until expiration."""
        now = datetime.now()
        diff = expires_at - now
        
        if diff.total_seconds() <= 0:
            return "Expired"
        elif diff.total_seconds() < 60:
            seconds = int(diff.total_seconds())
            return f"{seconds}s left"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m left"
        else:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h left"


# Global UI instance
_toast_ui: Optional[ToastNotificationUI] = None


def get_toast_ui() -> ToastNotificationUI:
    """Get singleton toast notification UI instance."""
    global _toast_ui
    
    if _toast_ui is None:
        _toast_ui = ToastNotificationUI()
    
    return _toast_ui