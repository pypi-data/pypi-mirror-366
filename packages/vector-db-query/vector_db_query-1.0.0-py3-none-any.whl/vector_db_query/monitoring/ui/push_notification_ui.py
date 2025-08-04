"""
Push notification UI components for the monitoring dashboard.

This module provides Streamlit UI components for managing push notifications,
Firebase configuration, device tokens, topics, and templates.
"""

import streamlit as st
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

from ..notifications.push_service import (
    PushService, get_push_service, DeviceToken, PushTopic, PushTemplate,
    PushSettings, DevicePlatform, PushPriority, send_push_notification
)
from ..notifications.models import NotificationSeverity
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class PushNotificationUI:
    """
    UI components for push notification management.
    
    Provides interface for Firebase configuration, device token management,
    topic subscriptions, templates, and push notification testing.
    """
    
    def __init__(self):
        """Initialize push notification UI."""
        self.push_service = get_push_service()
        self.change_tracker = get_change_tracker()
        
        # Initialize session state for push notifications
        if 'push_notifications_enabled' not in st.session_state:
            st.session_state.push_notifications_enabled = True
        
        if 'last_push_test' not in st.session_state:
            st.session_state.last_push_test = None
    
    def render_push_notification_tab(self):
        """
        Render the main push notification management tab.
        """
        st.header("📱 Push Notification Management")
        
        # Push notification tabs
        push_tabs = st.tabs(["Firebase Config", "Device Tokens", "Topics", "Templates", "Settings", "Test & Monitor"])
        
        with push_tabs[0]:
            self._render_firebase_configuration()
        
        with push_tabs[1]:
            self._render_device_token_management()
        
        with push_tabs[2]:
            self._render_topic_management()
        
        with push_tabs[3]:
            self._render_template_management()
        
        with push_tabs[4]:
            self._render_push_settings()
        
        with push_tabs[5]:
            self._render_test_monitor()
    
    def _render_firebase_configuration(self):
        """Render Firebase configuration interface."""
        st.subheader("🔥 Firebase Configuration")
        
        # Get current configuration
        current_config = self.push_service.get_firebase_config()
        
        # Firebase Configuration Form
        with st.form("firebase_configuration_form"):
            st.write("### Firebase Project Settings")
            
            project_id = st.text_input(
                "Firebase Project ID *",
                value=current_config.get('project_id', '') if current_config else "",
                help="Your Firebase project ID"
            )
            
            credentials_path = st.text_input(
                "Service Account Credentials Path *",
                value=current_config.get('credentials_path', '') if current_config else "",
                help="Absolute path to Firebase service account JSON file"
            )
            
            # Configuration instructions
            with st.expander("📋 Firebase Setup Instructions"):
                st.markdown("""
                ### Setting up Firebase for Push Notifications:
                
                1. **Create Firebase Project:**
                   - Go to [Firebase Console](https://console.firebase.google.com/)
                   - Create a new project or select existing one
                   - Enable Firebase Cloud Messaging (FCM)
                
                2. **Generate Service Account Key:**
                   - Go to Project Settings → Service Accounts
                   - Click "Generate new private key"
                   - Download the JSON file
                   - Store it securely on your server
                
                3. **Configure Mobile Apps:**
                   - Add Android/iOS apps to your Firebase project
                   - Download configuration files (google-services.json / GoogleService-Info.plist)
                   - Integrate FCM SDK in your mobile apps
                
                4. **Security Notes:**
                   - Keep service account credentials secure
                   - Use environment variables for paths
                   - Restrict API key permissions
                """)
            
            submitted = st.form_submit_button("💾 Save Firebase Configuration", type="primary")
            
            if submitted:
                if not project_id.strip():
                    st.error("Firebase Project ID is required")
                elif not credentials_path.strip():
                    st.error("Service Account Credentials Path is required")
                else:
                    if self.push_service.configure_firebase(credentials_path.strip(), project_id.strip()):
                        st.success("✅ Firebase configuration saved successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save Firebase configuration. Check credentials file exists and is valid.")
        
        # Current configuration display
        if current_config:
            st.write("### Current Configuration")
            config_data = {
                'Project ID': current_config['project_id'],
                'Credentials Path': current_config['credentials_path'],
                'Status': '✅ Configured'
            }
            
            for key, value in config_data.items():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.write(f"**{key}:**")
                with col2:
                    st.write(value)
        else:
            st.info("🔧 Firebase not configured. Configure Firebase to enable push notifications.")
    
    def _render_device_token_management(self):
        """Render device token management interface."""
        st.subheader("📱 Device Token Management")
        
        # Get device tokens
        device_tokens = self.push_service.get_device_tokens()
        
        # Device token management tabs
        token_subtabs = st.tabs(["Active Tokens", "Register Token", "Token Analytics"])
        
        with token_subtabs[0]:
            self._render_device_tokens_list(device_tokens)
        
        with token_subtabs[1]:
            self._render_device_token_registration()
        
        with token_subtabs[2]:
            self._render_token_analytics(device_tokens)
    
    def _render_device_tokens_list(self, tokens: Dict[str, DeviceToken]):
        """Render device tokens list."""
        st.write("### Active Device Tokens")
        
        if tokens:
            # Tokens table
            token_data = []
            for token in tokens.values():
                token_data.append({
                    'ID': token.id[:8] + '...',
                    'User ID': token.user_id,
                    'Platform': token.platform.value.title(),
                    'Device Name': token.device_name or 'Unknown',
                    'Model': token.device_model or 'Unknown',
                    'App Version': token.app_version or 'Unknown',
                    'Last Seen': token.last_seen.strftime('%Y-%m-%d %H:%M'),
                    'Active': '✅' if token.is_active else '❌'
                })
            
            # Display tokens with selection
            selected_indices = st.dataframe(
                token_data,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Token actions
            if token_data:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("🗑️ Deactivate Selected", type="secondary"):
                        if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                            selected_idx = selected_indices.selection['rows'][0]
                            # Find the full token ID
                            selected_token_id = None
                            for token_id, token in tokens.items():
                                if token_id.startswith(token_data[selected_idx]['ID'][:8]):
                                    selected_token_id = token_id
                                    break
                            
                            if selected_token_id and st.session_state.get('confirm_deactivate_token') == selected_token_id:
                                if self.push_service.unregister_device_token(selected_token_id):
                                    st.success("Token deactivated successfully!")
                                    st.session_state.confirm_deactivate_token = None
                                    st.rerun()
                                else:
                                    st.error("Failed to deactivate token")
                            elif selected_token_id:
                                st.session_state.confirm_deactivate_token = selected_token_id
                                st.warning("Click again to confirm deactivation")
                
                with col2:
                    if st.button("🧹 Cleanup Inactive", type="secondary"):
                        cleanup_count = self.push_service.cleanup_inactive_tokens()
                        if cleanup_count > 0:
                            st.success(f"Cleaned up {cleanup_count} inactive tokens")
                            st.rerun()
                        else:
                            st.info("No inactive tokens to clean up")
                
                # Token details
                if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                    selected_idx = selected_indices.selection['rows'][0]
                    # Find the full token
                    selected_token = None
                    for token in tokens.values():
                        if token.id.startswith(token_data[selected_idx]['ID'][:8]):
                            selected_token = token
                            break
                    
                    if selected_token:
                        st.write("### Token Details")
                        
                        with st.expander(f"📱 {selected_token.device_name or 'Unknown Device'}", expanded=True):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Device Information:**")
                                st.write(f"User ID: {selected_token.user_id}")
                                st.write(f"Platform: {selected_token.platform.value.title()}")
                                st.write(f"Device Name: {selected_token.device_name or 'Unknown'}")
                                st.write(f"Model: {selected_token.device_model or 'Unknown'}")
                                st.write(f"App Version: {selected_token.app_version or 'Unknown'}")
                            
                            with col2:
                                st.write("**Status Information:**")
                                st.write(f"Active: {'✅' if selected_token.is_active else '❌'}")
                                st.write(f"Registered: {selected_token.created_at.strftime('%Y-%m-%d %H:%M')}")
                                st.write(f"Last Seen: {selected_token.last_seen.strftime('%Y-%m-%d %H:%M')}")
                                
                                # Get user's topic subscriptions
                                subscriptions = self.push_service.get_user_subscriptions(selected_token.user_id)
                                st.write(f"Topic Subscriptions: {len(subscriptions)}")
                            
                            if subscriptions:
                                st.write("**Subscribed Topics:**")
                                topics = self.push_service.get_topics()
                                for topic_id in subscriptions:
                                    topic = topics.get(topic_id)
                                    if topic:
                                        st.write(f"• {topic.name}")
                            
                            if selected_token.metadata:
                                st.write("**Metadata:**")
                                st.json(selected_token.metadata)
        else:
            st.info("No device tokens registered. Users need to register their devices through the mobile app.")
    
    def _render_device_token_registration(self):
        """Render device token registration form."""
        st.write("### Register Device Token")
        st.info("💡 In production, device tokens are typically registered automatically by mobile apps. This manual registration is for testing.")
        
        with st.form("register_token_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                device_token = st.text_area(
                    "Device Token *",
                    height=100,
                    help="FCM device token from mobile app"
                )
                
                platform = st.selectbox(
                    "Platform *",
                    options=[p.value for p in DevicePlatform],
                    format_func=lambda x: x.title()
                )
                
                user_id = st.text_input(
                    "User ID *",
                    help="Unique user identifier"
                )
            
            with col2:
                device_name = st.text_input(
                    "Device Name",
                    help="Human-readable device name"
                )
                
                device_model = st.text_input(
                    "Device Model",
                    help="Device model information"
                )
                
                app_version = st.text_input(
                    "App Version",
                    help="Mobile app version"
                )
            
            submitted = st.form_submit_button("📱 Register Device Token", type="primary")
            
            if submitted:
                if not device_token.strip():
                    st.error("Device token is required")
                elif not user_id.strip():
                    st.error("User ID is required")
                else:
                    token_id = self.push_service.register_device_token(
                        token=device_token.strip(),
                        platform=DevicePlatform(platform),
                        user_id=user_id.strip(),
                        device_name=device_name.strip() if device_name.strip() else None,
                        device_model=device_model.strip() if device_model.strip() else None,
                        app_version=app_version.strip() if app_version.strip() else None
                    )
                    
                    if token_id:
                        st.success(f"✅ Device token registered successfully! ID: {token_id[:8]}...")
                        st.rerun()
                    else:
                        st.error("❌ Failed to register device token")
    
    def _render_token_analytics(self, tokens: Dict[str, DeviceToken]):
        """Render token analytics."""
        st.write("### Token Analytics")
        
        if tokens:
            # Platform breakdown
            platform_counts = {}
            user_counts = {}
            active_count = 0
            
            for token in tokens.values():
                if token.is_active:
                    active_count += 1
                    platform = token.platform.value
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
                    user_counts[token.user_id] = user_counts.get(token.user_id, 0) + 1
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Tokens", len(tokens))
            
            with col2:
                st.metric("Active Tokens", active_count)
            
            with col3:
                st.metric("Unique Users", len(user_counts))
            
            with col4:
                avg_tokens = sum(user_counts.values()) / len(user_counts) if user_counts else 0
                st.metric("Avg Tokens/User", f"{avg_tokens:.1f}")
            
            # Platform breakdown
            if platform_counts:
                st.write("### Platform Distribution")
                platform_data = [{'Platform': k.title(), 'Count': v, 'Percentage': f"{(v/active_count)*100:.1f}%"} 
                               for k, v in platform_counts.items()]
                st.table(platform_data)
            
            # Recent registrations
            st.write("### Recent Registrations")
            recent_tokens = sorted(tokens.values(), key=lambda x: x.created_at, reverse=True)[:10]
            
            recent_data = []
            for token in recent_tokens:
                recent_data.append({
                    'User ID': token.user_id,
                    'Platform': token.platform.value.title(),
                    'Device': token.device_name or 'Unknown',
                    'Registered': token.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Active': '✅' if token.is_active else '❌'
                })
            
            st.dataframe(recent_data, use_container_width=True, hide_index=True)
        else:
            st.info("No tokens available for analytics")
    
    def _render_topic_management(self):
        """Render topic management interface."""
        st.subheader("📢 Topic Management")
        
        # Get topics
        topics = self.push_service.get_topics()
        
        # Topic management tabs
        topic_subtabs = st.tabs(["Topics List", "Create Topic", "Subscriptions"])
        
        with topic_subtabs[0]:
            self._render_topics_list(topics)
        
        with topic_subtabs[1]:
            self._render_topic_creator()
        
        with topic_subtabs[2]:
            self._render_subscription_management(topics)
    
    def _render_topics_list(self, topics: Dict[str, PushTopic]):
        """Render topics list."""
        st.write("### Push Notification Topics")
        
        if topics:
            # Topics table
            topic_data = []
            for topic in topics.values():
                topic_data.append({
                    'ID': topic.id,
                    'Name': topic.name,
                    'Description': topic.description[:50] + '...' if len(topic.description) > 50 else topic.description,
                    'Subscribers': topic.subscriber_count,
                    'Severity Filter': ', '.join(topic.severity_filter) if topic.severity_filter else 'All',
                    'Category Filter': ', '.join(topic.category_filter) if topic.category_filter else 'All',
                    'Active': '✅' if topic.is_active else '❌',
                    'Created': topic.created_at.strftime('%Y-%m-%d')
                })
            
            # Display topics with selection
            selected_indices = st.dataframe(
                topic_data,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Topic details
            if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                selected_idx = selected_indices.selection['rows'][0]
                selected_topic_id = topic_data[selected_idx]['ID']
                selected_topic = topics[selected_topic_id]
                
                st.write("### Topic Details")
                
                with st.expander(f"📢 {selected_topic.name}", expanded=True):
                    st.write(f"**Description:** {selected_topic.description}")
                    st.write(f"**Subscribers:** {selected_topic.subscriber_count}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Severity Filter:**", ', '.join(selected_topic.severity_filter) if selected_topic.severity_filter else 'All')
                    with col2:
                        st.write("**Category Filter:**", ', '.join(selected_topic.category_filter) if selected_topic.category_filter else 'All')
                    
                    # Show subscribers
                    subscribers = self.push_service.get_topic_subscribers(selected_topic_id)
                    if subscribers:
                        st.write("**Subscriber Details:**")
                        tokens = self.push_service.get_device_tokens()
                        subscriber_data = []
                        
                        for token_id in subscribers:
                            token = tokens.get(token_id)
                            if token:
                                subscriber_data.append({
                                    'User ID': token.user_id,
                                    'Platform': token.platform.value.title(),
                                    'Device': token.device_name or 'Unknown',
                                    'Last Seen': token.last_seen.strftime('%Y-%m-%d %H:%M')
                                })
                        
                        if subscriber_data:
                            st.dataframe(subscriber_data, use_container_width=True, hide_index=True)
        else:
            st.info("No topics found. Create your first topic to start organizing push notifications.")
    
    def _render_topic_creator(self):
        """Render topic creator."""
        st.write("### Create New Topic")
        
        with st.form("create_topic_form"):
            name = st.text_input("Topic Name *")
            description = st.text_area("Description *", height=100)
            
            col1, col2 = st.columns(2)
            
            with col1:
                severity_filter = st.multiselect(
                    "Severity Filter (empty = all)",
                    options=['info', 'warning', 'error', 'critical'],
                    help="Topic will only receive selected severities"
                )
            
            with col2:
                category_filter = st.multiselect(
                    "Category Filter (empty = all)",
                    options=['general', 'system', 'process_control', 'queue_management', 'log_management', 'maintenance', 'summary'],
                    help="Topic will only receive selected categories"
                )
            
            is_active = st.checkbox("Topic Active", value=True)
            
            submitted = st.form_submit_button("✨ Create Topic", type="primary")
            
            if submitted:
                if not name.strip():
                    st.error("Topic name is required")
                elif not description.strip():
                    st.error("Topic description is required")
                else:
                    # Create topic
                    topic = PushTopic(
                        id=str(uuid.uuid4()),
                        name=name.strip(),
                        description=description.strip(),
                        severity_filter=severity_filter if severity_filter else None,
                        category_filter=category_filter if category_filter else None,
                        is_active=is_active
                    )
                    
                    if self.push_service.add_topic(topic):
                        st.success(f"✅ Topic '{name}' created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create topic")
    
    def _render_subscription_management(self, topics: Dict[str, PushTopic]):
        """Render subscription management."""
        st.write("### Subscription Management")
        
        if topics:
            # Get device tokens for user selection
            tokens = self.push_service.get_device_tokens()
            if tokens:
                # User selection
                users = list(set(token.user_id for token in tokens.values()))
                selected_user = st.selectbox("Select User", users)
                
                if selected_user:
                    user_tokens = [token for token in tokens.values() if token.user_id == selected_user]
                    user_subscriptions = self.push_service.get_user_subscriptions(selected_user)
                    
                    st.write(f"### Managing subscriptions for: {selected_user}")
                    st.write(f"Device tokens: {len(user_tokens)}")
                    
                    # Subscription form
                    with st.form(f"subscriptions_{selected_user}"):
                        st.write("**Topic Subscriptions:**")
                        
                        subscription_changes = {}
                        for topic_id, topic in topics.items():
                            if topic.is_active:
                                current_subscribed = topic_id in user_subscriptions
                                new_subscription = st.checkbox(
                                    f"{topic.name} - {topic.description}",
                                    value=current_subscribed,
                                    key=f"sub_{topic_id}_{selected_user}"
                                )
                                
                                if new_subscription != current_subscribed:
                                    subscription_changes[topic_id] = new_subscription
                        
                        submitted = st.form_submit_button("💾 Update Subscriptions", type="primary")
                        
                        if submitted and subscription_changes:
                            success_count = 0
                            
                            for token in user_tokens:
                                for topic_id, should_subscribe in subscription_changes.items():
                                    if should_subscribe:
                                        if self.push_service.subscribe_to_topic(token.id, topic_id):
                                            success_count += 1
                                    else:
                                        if self.push_service.unsubscribe_from_topic(token.id, topic_id):
                                            success_count += 1
                            
                            if success_count > 0:
                                st.success(f"✅ Updated subscriptions for {len(user_tokens)} device(s)")
                                st.rerun()
                            else:
                                st.error("❌ Failed to update subscriptions")
            else:
                st.info("No device tokens available. Users need to register devices first.")
        else:
            st.info("No topics available. Create topics first.")
    
    def _render_template_management(self):
        """Render template management interface."""
        st.subheader("📝 Push Template Management")
        
        # Get templates
        templates = self.push_service.get_templates()
        
        # Template management tabs
        template_subtabs = st.tabs(["Templates List", "Create Template"])
        
        with template_subtabs[0]:
            self._render_templates_list(templates)
        
        with template_subtabs[1]:
            self._render_template_creator()
    
    def _render_templates_list(self, templates: Dict[str, PushTemplate]):
        """Render templates list."""
        st.write("### Push Notification Templates")
        
        if templates:
            # Templates table
            template_data = []
            for template in templates.values():
                template_data.append({
                    'ID': template.id,
                    'Name': template.name,
                    'Title': template.title_template[:30] + '...' if len(template.title_template) > 30 else template.title_template,
                    'Body': template.body_template[:40] + '...' if len(template.body_template) > 40 else template.body_template,
                    'Sound': template.sound or 'Default',
                    'Severity Filter': ', '.join(template.severity_filter) if template.severity_filter else 'All',
                    'Active': '✅' if template.is_active else '❌',
                    'Created': template.created_at.strftime('%Y-%m-%d')
                })
            
            # Display templates with selection
            selected_indices = st.dataframe(
                template_data,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Template preview
            if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                selected_idx = selected_indices.selection['rows'][0]
                selected_template_id = template_data[selected_idx]['ID']
                selected_template = templates[selected_template_id]
                
                st.write("### Template Preview")
                
                with st.expander(f"📝 {selected_template.name}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Title Template:**")
                        st.code(selected_template.title_template)
                        
                        st.write("**Body Template:**")
                        st.code(selected_template.body_template)
                    
                    with col2:
                        st.write("**Settings:**")
                        st.write(f"Sound: {selected_template.sound or 'Default'}")
                        st.write(f"Badge Increment: {'✅' if selected_template.badge_increment else '❌'}")
                        
                        if selected_template.android_channel_id:
                            st.write(f"Android Channel: {selected_template.android_channel_id}")
                        
                        if selected_template.ios_category:
                            st.write(f"iOS Category: {selected_template.ios_category}")
                        
                        if selected_template.action_buttons:
                            st.write("**Action Buttons:**")
                            for button in selected_template.action_buttons:
                                st.write(f"• {button.get('title', 'Unnamed')} ({button.get('id', 'no-id')})")
                    
                    st.write("**Filters:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("Severity:", ', '.join(selected_template.severity_filter) if selected_template.severity_filter else 'All')
                    with col2:
                        st.write("Category:", ', '.join(selected_template.category_filter) if selected_template.category_filter else 'All')
        else:
            st.info("No push templates found. Default templates are created automatically.")
    
    def _render_template_creator(self):
        """Render template creator."""
        st.write("### Create New Push Template")
        
        with st.form("create_push_template_form"):
            name = st.text_input("Template Name *")
            
            col1, col2 = st.columns(2)
            
            with col1:
                title_template = st.text_input(
                    "Title Template *",
                    value="{{title}}",
                    help="Use {{variable}} for substitution"
                )
                
                body_template = st.text_area(
                    "Body Template *",
                    value="{{message}}",
                    height=100,
                    help="Use {{variable}} for substitution"
                )
                
                sound = st.text_input(
                    "Sound",
                    value="default",
                    help="Sound file name or 'default'"
                )
            
            with col2:
                badge_increment = st.checkbox("Badge Increment", value=True)
                
                android_channel_id = st.text_input(
                    "Android Channel ID",
                    help="Android notification channel ID"
                )
                
                ios_category = st.text_input(
                    "iOS Category",
                    help="iOS notification category"
                )
                
                severity_filter = st.multiselect(
                    "Severity Filter (empty = all)",
                    options=['info', 'warning', 'error', 'critical']
                )
                
                category_filter = st.multiselect(
                    "Category Filter (empty = all)",
                    options=['general', 'system', 'process_control', 'queue_management', 'log_management']
                )
            
            # Action buttons
            st.write("**Action Buttons (Optional):**")
            
            action_buttons = []
            num_buttons = st.number_input("Number of Action Buttons", min_value=0, max_value=3, value=0)
            
            for i in range(int(num_buttons)):
                col1, col2 = st.columns(2)
                with col1:
                    button_id = st.text_input(f"Button {i+1} ID", key=f"btn_id_{i}")
                with col2:
                    button_title = st.text_input(f"Button {i+1} Title", key=f"btn_title_{i}")
                
                if button_id and button_title:
                    action_buttons.append({"id": button_id, "title": button_title})
            
            is_active = st.checkbox("Template Active", value=True)
            
            submitted = st.form_submit_button("✨ Create Template", type="primary")
            
            if submitted:
                if not name.strip():
                    st.error("Template name is required")
                elif not title_template.strip():
                    st.error("Title template is required")
                elif not body_template.strip():
                    st.error("Body template is required")
                else:
                    # Create template
                    template = PushTemplate(
                        id=str(uuid.uuid4()),
                        name=name.strip(),
                        title_template=title_template.strip(),
                        body_template=body_template.strip(),
                        sound=sound.strip() if sound.strip() else None,
                        badge_increment=badge_increment,
                        android_channel_id=android_channel_id.strip() if android_channel_id.strip() else None,
                        ios_category=ios_category.strip() if ios_category.strip() else None,
                        action_buttons=action_buttons if action_buttons else None,
                        severity_filter=severity_filter if severity_filter else None,
                        category_filter=category_filter if category_filter else None,
                        is_active=is_active
                    )
                    
                    if self.push_service.add_template(template):
                        st.success(f"✅ Template '{name}' created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create template")
        
        # Template variables help
        with st.expander("📋 Template Variables Help"):
            st.markdown("""
            ### Available Variables:
            
            - `{{title}}` - Notification title
            - `{{message}}` - Notification message
            - `{{severity}}` - Notification severity
            - `{{source}}` - Notification source
            - `{{timestamp}}` - Notification timestamp
            - `{{data.key}}` - Access data dictionary values
            
            ### Example Templates:
            
            **Title Templates:**
            - `{{title}}`
            - `🚨 {{title}}`
            - `[{{severity|upper}}] {{title}}`
            
            **Body Templates:**
            - `{{message}}`
            - `{{message}} from {{source}}`
            - `Alert: {{message}} ({{severity}})`
            """)
    
    def _render_push_settings(self):
        """Render push settings interface."""
        st.subheader("⚙️ Push Notification Settings")
        
        # Get current settings
        current_settings = self.push_service.get_settings()
        
        # Settings form
        with st.form("push_settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**General Settings:**")
                
                enabled = st.checkbox(
                    "Enable Push Notifications",
                    value=current_settings.enabled,
                    help="Master switch for all push notifications"
                )
                
                rate_limit_per_hour = st.number_input(
                    "Rate Limit (notifications per hour)",
                    min_value=1,
                    max_value=10000,
                    value=current_settings.rate_limit_per_hour,
                    help="Maximum notifications to send per hour"
                )
                
                batch_size = st.number_input(
                    "Batch Size",
                    min_value=1,
                    max_value=1000,
                    value=current_settings.batch_size,
                    help="Number of notifications to send in one batch"
                )
                
                dry_run = st.checkbox(
                    "Dry Run Mode",
                    value=current_settings.dry_run,
                    help="Test mode - notifications won't actually be sent"
                )
            
            with col2:
                st.write("**Default Settings:**")
                
                # Default template
                templates = self.push_service.get_templates()
                template_options = {'': 'None'} | {tid: template.name for tid, template in templates.items()}
                default_template_id = st.selectbox(
                    "Default Template",
                    options=list(template_options.keys()),
                    index=list(template_options.keys()).index(current_settings.default_template_id or ''),
                    format_func=lambda x: template_options[x],
                    help="Default template to use for notifications"
                )
                
                default_priority = st.selectbox(
                    "Default Priority",
                    options=[p.value for p in PushPriority],
                    index=list(PushPriority).index(current_settings.default_priority),
                    format_func=lambda x: x.title()
                )
                
                st.write("**Maintenance Settings:**")
                
                token_cleanup_days = st.number_input(
                    "Token Cleanup (days)",
                    min_value=1,
                    max_value=365,
                    value=current_settings.token_cleanup_days,
                    help="Days after which inactive tokens are cleaned up"
                )
                
                retry_count = st.number_input(
                    "Retry Count",
                    min_value=0,
                    max_value=10,
                    value=current_settings.retry_count,
                    help="Number of times to retry failed notifications"
                )
                
                retry_delay_seconds = st.number_input(
                    "Retry Delay (seconds)",
                    min_value=1,
                    max_value=300,
                    value=current_settings.retry_delay_seconds,
                    help="Delay between retry attempts"
                )
            
            submitted = st.form_submit_button("💾 Save Settings", type="primary")
            
            if submitted:
                # Create settings
                settings = PushSettings(
                    enabled=enabled,
                    firebase_project_id=current_settings.firebase_project_id,  # Keep existing
                    default_template_id=default_template_id if default_template_id else None,
                    default_priority=PushPriority(default_priority),
                    rate_limit_per_hour=rate_limit_per_hour,
                    batch_size=batch_size,
                    token_cleanup_days=token_cleanup_days,
                    retry_count=retry_count,
                    retry_delay_seconds=retry_delay_seconds,
                    dry_run=dry_run
                )
                
                if self.push_service.update_settings(settings):
                    st.success("✅ Settings saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save settings")
        
        # Global push toggle
        st.write("### Dashboard Integration")
        
        push_dashboard_enabled = st.checkbox(
            "Send Push Notifications for Dashboard Events",
            value=st.session_state.get('push_dashboard_enabled', False),
            help="Automatically send push notifications for critical dashboard events"
        )
        
        st.session_state.push_dashboard_enabled = push_dashboard_enabled
        
        if not push_dashboard_enabled:
            st.info("Push notifications for dashboard events are disabled.")
    
    def _render_test_monitor(self):
        """Render push testing and monitoring interface."""
        st.subheader("🧪 Test & Monitor Push Service")
        
        # Service status
        st.write("### Service Status")
        
        stats = self.push_service.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_icon = "✅" if stats['firebase_configured'] else "❌"
            st.metric("Firebase Configured", f"{status_icon} {'Yes' if stats['firebase_configured'] else 'No'}")
        
        with col2:
            status_icon = "✅" if stats['service_enabled'] else "❌"
            st.metric("Service Enabled", f"{status_icon} {'Yes' if stats['service_enabled'] else 'No'}")
        
        with col3:
            st.metric("Active Tokens", stats['active_device_tokens'])
        
        with col4:
            st.metric("Unique Users", stats['unique_users'])
        
        # Rate limiting status
        st.write("### Rate Limiting")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Notifications This Hour", stats['notifications_sent_this_hour'])
        
        with col2:
            st.metric("Hourly Limit", stats['rate_limit_per_hour'])
        
        with col3:
            remaining = stats['rate_limit_remaining']
            delta_color = "normal" if remaining > 50 else "inverse"
            st.metric("Remaining", remaining, delta=f"{remaining} left", delta_color=delta_color)
        
        # Platform breakdown
        if stats['platform_breakdown']:
            st.write("### Platform Distribution")
            platform_data = [{'Platform': k.title(), 'Count': v} for k, v in stats['platform_breakdown'].items()]
            st.table(platform_data)
        
        # Push notification test
        st.write("### Send Test Notification")
        
        tokens = self.push_service.get_device_tokens()
        topics = self.push_service.get_topics()
        
        if tokens or topics:
            with st.form("test_push_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    test_title = st.text_input("Notification Title", value="Test Push Notification")
                    test_message = st.text_area(
                        "Notification Message",
                        value="This is a test push notification from the Ansera monitoring dashboard.",
                        height=100
                    )
                    test_severity = st.selectbox(
                        "Severity",
                        options=['info', 'warning', 'error', 'critical'],
                        index=0
                    )
                
                with col2:
                    # Recipient options
                    recipient_type = st.radio(
                        "Send To",
                        options=["Topic", "Specific User", "All Users"],
                        index=0
                    )
                    
                    if recipient_type == "Topic" and topics:
                        topic_options = {tid: topic.name for tid, topic in topics.items()}
                        test_topic_id = st.selectbox(
                            "Select Topic",
                            options=list(topic_options.keys()),
                            format_func=lambda x: topic_options[x]
                        )
                    elif recipient_type == "Specific User" and tokens:
                        users = list(set(token.user_id for token in tokens.values()))
                        test_user_id = st.selectbox("Select User", users)
                    
                    test_priority = st.selectbox(
                        "Priority",
                        options=[p.value for p in PushPriority],
                        index=1,
                        format_func=lambda x: x.title()
                    )
                
                submitted = st.form_submit_button("📱 Send Test Notification", type="primary")
                
                if submitted:
                    try:
                        with st.spinner("Sending test notification..."):
                            # Run async send
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            kwargs = {
                                'title': test_title,
                                'message': test_message,
                                'severity': NotificationSeverity(test_severity),
                                'category': 'test',
                                'source': 'push_ui_test',
                                'priority': PushPriority(test_priority),
                                'data': {'test_timestamp': datetime.now().isoformat()}
                            }
                            
                            if recipient_type == "Topic":
                                kwargs['topic_id'] = test_topic_id
                            elif recipient_type == "Specific User":
                                kwargs['user_ids'] = [test_user_id]
                            # For "All Users", no additional parameters needed
                            
                            success = loop.run_until_complete(
                                self.push_service.send_notification(**kwargs)
                            )
                            
                            loop.close()
                            
                            if success:
                                st.success("✅ Test notification sent successfully!")
                                st.session_state.last_push_test = {
                                    'success': True,
                                    'timestamp': datetime.now().isoformat()
                                }
                            else:
                                st.error("❌ Failed to send test notification")
                                st.session_state.last_push_test = {
                                    'success': False,
                                    'timestamp': datetime.now().isoformat()
                                }
                    
                    except Exception as e:
                        st.error(f"❌ Error sending test notification: {str(e)}")
                        st.session_state.last_push_test = {
                            'success': False,
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        }
        else:
            st.info("No device tokens or topics available. Register devices and create topics first.")
        
        # Quick test buttons
        if tokens:
            st.write("### Quick Tests")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📱 Test Info"):
                    if self._send_quick_push_test("info"):
                        st.success("Info test sent!")
            
            with col2:
                if st.button("⚠️ Test Warning"):
                    if self._send_quick_push_test("warning"):
                        st.success("Warning test sent!")
            
            with col3:
                if st.button("❌ Test Error"):
                    if self._send_quick_push_test("error"):
                        st.success("Error test sent!")
            
            with col4:
                if st.button("🚨 Test Critical"):
                    if self._send_quick_push_test("critical"):
                        st.success("Critical test sent!")
    
    def _send_quick_push_test(self, severity: str) -> bool:
        """Send a quick test push notification."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(
                self.push_service.send_notification(
                    title=f"Quick {severity.title()} Test",
                    message=f"This is a quick {severity} test from the push service.",
                    severity=NotificationSeverity(severity),
                    category="quick_test",
                    source="push_ui_quick_test",
                    data={"test_type": "quick", "severity": severity}
                )
            )
            
            loop.close()
            return success
        
        except Exception as e:
            st.error(f"Quick test failed: {str(e)}")
            return False


# Global UI instance
_push_ui: Optional[PushNotificationUI] = None


def get_push_notification_ui() -> PushNotificationUI:
    """Get singleton push notification UI instance."""
    global _push_ui
    
    if _push_ui is None:
        _push_ui = PushNotificationUI()
    
    return _push_ui