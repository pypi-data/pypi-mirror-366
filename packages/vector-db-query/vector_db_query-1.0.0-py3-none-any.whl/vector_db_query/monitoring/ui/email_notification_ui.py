"""
Email notification UI components for the monitoring dashboard.

This module provides Streamlit UI components for managing email notifications,
SMTP configuration, templates, and recipient groups.
"""

import streamlit as st
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

from ..notifications.email_service import (
    EmailService, get_email_service, SMTPConfig, EmailTemplate, EmailRecipientGroup,
    EmailSettings, EmailAuthType, EmailPriority, send_email_notification
)
from ..notifications.models import NotificationSeverity
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class EmailNotificationUI:
    """
    UI components for email notification management.
    
    Provides interface for SMTP configuration, template management,
    recipient groups, and email notification testing.
    """
    
    def __init__(self):
        """Initialize email notification UI."""
        self.email_service = get_email_service()
        self.change_tracker = get_change_tracker()
        
        # Initialize session state for email notifications
        if 'email_notifications_enabled' not in st.session_state:
            st.session_state.email_notifications_enabled = True
        
        if 'last_email_test' not in st.session_state:
            st.session_state.last_email_test = None
    
    def render_email_notification_tab(self):
        """
        Render the main email notification management tab.
        """
        st.header("📧 Email Notification Management")
        
        # Email notification tabs
        email_tabs = st.tabs(["SMTP Configuration", "Templates", "Recipients", "Settings", "Test & Monitor"])
        
        with email_tabs[0]:
            self._render_smtp_configuration()
        
        with email_tabs[1]:
            self._render_template_management()
        
        with email_tabs[2]:
            self._render_recipient_management()
        
        with email_tabs[3]:
            self._render_email_settings()
        
        with email_tabs[4]:
            self._render_test_monitor()
    
    def _render_smtp_configuration(self):
        """Render SMTP configuration interface."""
        st.subheader("🔧 SMTP Server Configuration")
        
        # Get current configuration
        current_config = self.email_service.get_smtp_config()
        
        # SMTP Configuration Form
        with st.form("smtp_configuration_form"):
            st.write("### Server Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                smtp_host = st.text_input(
                    "SMTP Host *",
                    value=current_config.smtp_host if current_config else "",
                    help="SMTP server hostname (e.g., smtp.gmail.com)"
                )
                
                smtp_port = st.number_input(
                    "SMTP Port *",
                    min_value=1,
                    max_value=65535,
                    value=current_config.smtp_port if current_config else 587,
                    help="SMTP server port (587 for TLS, 465 for SSL, 25 for plain)"
                )
                
                auth_type = st.selectbox(
                    "Authentication Type",
                    options=[auth.value for auth in EmailAuthType],
                    index=list(EmailAuthType).index(current_config.auth_type) if current_config else 1,
                    format_func=lambda x: x.replace('_', ' ').title()
                )
            
            with col2:
                use_tls = st.checkbox(
                    "Use TLS",
                    value=current_config.use_tls if current_config else True,
                    help="Enable TLS encryption (recommended for port 587)"
                )
                
                use_ssl = st.checkbox(
                    "Use SSL",
                    value=current_config.use_ssl if current_config else False,
                    help="Enable SSL encryption (for port 465)"
                )
                
                timeout = st.number_input(
                    "Connection Timeout (seconds)",
                    min_value=5,
                    max_value=300,
                    value=current_config.timeout if current_config else 30
                )
            
            st.write("### Authentication")
            
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input(
                    "Username",
                    value=current_config.username if current_config else "",
                    help="SMTP username (usually your email address)"
                )
            
            with col2:
                password = st.text_input(
                    "Password",
                    type="password",
                    value=current_config.password if current_config else "",
                    help="SMTP password or app-specific password"
                )
            
            # Configuration presets
            st.write("### Quick Setup Presets")
            preset_col1, preset_col2, preset_col3 = st.columns(3)
            
            with preset_col1:
                if st.form_submit_button("📧 Gmail Setup"):
                    st.session_state.smtp_preset = {
                        'smtp_host': 'smtp.gmail.com',
                        'smtp_port': 587,
                        'use_tls': True,
                        'use_ssl': False,
                        'auth_type': 'plain'
                    }
            
            with preset_col2:
                if st.form_submit_button("📧 Outlook Setup"):
                    st.session_state.smtp_preset = {
                        'smtp_host': 'smtp-mail.outlook.com',
                        'smtp_port': 587,
                        'use_tls': True,
                        'use_ssl': False,
                        'auth_type': 'plain'
                    }
            
            with preset_col3:
                if st.form_submit_button("📧 Custom SMTP"):
                    st.session_state.smtp_preset = None
            
            # Apply preset if selected
            if hasattr(st.session_state, 'smtp_preset') and st.session_state.smtp_preset:
                preset = st.session_state.smtp_preset
                smtp_host = preset['smtp_host']
                smtp_port = preset['smtp_port']
                use_tls = preset['use_tls']
                use_ssl = preset['use_ssl']
                auth_type = preset['auth_type']
                st.session_state.smtp_preset = None  # Clear preset
                st.rerun()
            
            # Submit button
            submitted = st.form_submit_button("💾 Save SMTP Configuration", type="primary")
            
            if submitted:
                if not smtp_host:
                    st.error("SMTP Host is required")
                elif auth_type != 'none' and not username:
                    st.error("Username is required for authentication")
                elif auth_type != 'none' and not password:
                    st.error("Password is required for authentication")
                else:
                    # Create SMTP configuration
                    smtp_config = SMTPConfig(
                        smtp_host=smtp_host,
                        smtp_port=smtp_port,
                        use_tls=use_tls,
                        use_ssl=use_ssl,
                        auth_type=EmailAuthType(auth_type),
                        username=username if auth_type != 'none' else None,
                        password=password if auth_type != 'none' else None,
                        timeout=timeout
                    )
                    
                    if self.email_service.configure_smtp(smtp_config):
                        st.success("✅ SMTP configuration saved successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save SMTP configuration")
        
        # Current configuration display
        if current_config:
            st.write("### Current Configuration")
            config_data = {
                'Host': current_config.smtp_host,
                'Port': current_config.smtp_port,
                'TLS': '✅' if current_config.use_tls else '❌',
                'SSL': '✅' if current_config.use_ssl else '❌',
                'Auth': current_config.auth_type.value.title(),
                'Username': current_config.username or 'Not set'
            }
            
            for key, value in config_data.items():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.write(f"**{key}:**")
                with col2:
                    st.write(value)
        
        # Configuration tips
        with st.expander("📋 Configuration Tips"):
            st.markdown("""
            ### Common SMTP Settings:
            
            **Gmail:**
            - Host: smtp.gmail.com
            - Port: 587 (TLS) or 465 (SSL)
            - Use app-specific password (not regular password)
            
            **Outlook/Hotmail:**
            - Host: smtp-mail.outlook.com
            - Port: 587 (TLS)
            - Use regular account password
            
            **Yahoo:**
            - Host: smtp.mail.yahoo.com
            - Port: 587 (TLS) or 465 (SSL)
            - Use app-specific password
            
            ### Security Notes:
            - Always use TLS or SSL for secure connections
            - Use app-specific passwords when available
            - Test configuration before relying on it
            """)
    
    def _render_template_management(self):
        """Render email template management interface."""
        st.subheader("📝 Email Template Management")
        
        # Get current templates
        templates = self.email_service.get_templates()
        
        # Template management tabs
        template_subtabs = st.tabs(["Templates List", "Edit Template", "Create Template"])
        
        with template_subtabs[0]:
            self._render_templates_list(templates)
        
        with template_subtabs[1]:
            self._render_template_editor(templates)
        
        with template_subtabs[2]:
            self._render_template_creator()
    
    def _render_templates_list(self, templates: Dict[str, EmailTemplate]):
        """Render templates list."""
        st.write("### Email Templates")
        
        if templates:
            # Templates table
            template_data = []
            for template in templates.values():
                template_data.append({
                    'ID': template.id,
                    'Name': template.name,
                    'Subject': template.subject_template[:50] + '...' if len(template.subject_template) > 50 else template.subject_template,
                    'Severity Filter': ', '.join(template.severity_filter) if template.severity_filter else 'All',
                    'Category Filter': ', '.join(template.category_filter) if template.category_filter else 'All',
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
            
            # Template actions
            if template_data:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🗑️ Delete Selected", type="secondary"):
                        if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                            selected_idx = selected_indices.selection['rows'][0]
                            selected_template_id = template_data[selected_idx]['ID']
                            
                            if st.session_state.get('confirm_delete_template') == selected_template_id:
                                if self.email_service.remove_template(selected_template_id):
                                    st.success(f"Template '{template_data[selected_idx]['Name']}' deleted successfully!")
                                    st.session_state.confirm_delete_template = None
                                    st.rerun()
                                else:
                                    st.error("Failed to delete template")
                            else:
                                st.session_state.confirm_delete_template = selected_template_id
                                st.warning(f"Click again to confirm deletion of '{template_data[selected_idx]['Name']}'")
                
                # Template preview
                if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                    selected_idx = selected_indices.selection['rows'][0]
                    selected_template_id = template_data[selected_idx]['ID']
                    selected_template = templates[selected_template_id]
                    
                    st.write("### Template Preview")
                    
                    with st.expander(f"📧 {selected_template.name}", expanded=True):
                        st.write("**Subject Template:**")
                        st.code(selected_template.subject_template)
                        
                        st.write("**Body Template:**")
                        st.code(selected_template.body_template)
                        
                        if selected_template.html_template:
                            st.write("**HTML Template:**")
                            st.code(selected_template.html_template)
                        
                        st.write("**Filters:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("Severity:", ', '.join(selected_template.severity_filter) if selected_template.severity_filter else 'All')
                        with col2:
                            st.write("Category:", ', '.join(selected_template.category_filter) if selected_template.category_filter else 'All')
        else:
            st.info("No email templates found. Create your first template using the 'Create Template' tab.")
    
    def _render_template_editor(self, templates: Dict[str, EmailTemplate]):
        """Render template editor."""
        st.write("### Edit Email Template")
        
        if not templates:
            st.info("No templates available to edit. Create a template first.")
            return
        
        # Template selection
        template_options = {tid: f"{template.name} ({tid})" for tid, template in templates.items()}
        selected_template_id = st.selectbox(
            "Select Template to Edit",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x]
        )
        
        if selected_template_id:
            template = templates[selected_template_id]
            
            # Template editing form
            with st.form(f"edit_template_{selected_template_id}"):
                name = st.text_input("Template Name", value=template.name)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    severity_filter = st.multiselect(
                        "Severity Filter (empty = all)",
                        options=['info', 'warning', 'error', 'critical'],
                        default=template.severity_filter or []
                    )
                
                with col2:
                    category_filter = st.multiselect(
                        "Category Filter (empty = all)",
                        options=['general', 'system', 'process_control', 'queue_management', 'log_management'],
                        default=template.category_filter or []
                    )
                
                is_active = st.checkbox("Template Active", value=template.is_active)
                
                st.write("**Subject Template:**")
                subject_template = st.text_area(
                    "Subject (use {{variable}} for substitution)",
                    value=template.subject_template,
                    height=50,
                    help="Available variables: title, severity, source, timestamp"
                )
                
                st.write("**Body Template:**")
                body_template = st.text_area(
                    "Body (use {{variable}} for substitution)",
                    value=template.body_template,
                    height=200,
                    help="Available variables: title, message, severity, source, timestamp, data"
                )
                
                st.write("**HTML Template (Optional):**")
                html_template = st.text_area(
                    "HTML Body (use {{variable}} for substitution)",
                    value=template.html_template or "",
                    height=150,
                    help="Optional HTML version of the email body"
                )
                
                submitted = st.form_submit_button("💾 Update Template", type="primary")
                
                if submitted:
                    if not name.strip():
                        st.error("Template name is required")
                    elif not subject_template.strip():
                        st.error("Subject template is required")
                    elif not body_template.strip():
                        st.error("Body template is required")
                    else:
                        # Update template
                        updated_template = EmailTemplate(
                            id=template.id,
                            name=name.strip(),
                            subject_template=subject_template.strip(),
                            body_template=body_template.strip(),
                            html_template=html_template.strip() if html_template.strip() else None,
                            severity_filter=severity_filter if severity_filter else None,
                            category_filter=category_filter if category_filter else None,
                            is_active=is_active,
                            created_at=template.created_at
                        )
                        
                        if self.email_service.add_template(updated_template):  # add_template handles updates too
                            st.success("✅ Template updated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update template")
    
    def _render_template_creator(self):
        """Render template creator."""
        st.write("### Create New Email Template")
        
        with st.form("create_template_form"):
            name = st.text_input("Template Name *")
            
            col1, col2 = st.columns(2)
            
            with col1:
                severity_filter = st.multiselect(
                    "Severity Filter (empty = all)",
                    options=['info', 'warning', 'error', 'critical'],
                    help="Template will only be used for selected severities"
                )
            
            with col2:
                category_filter = st.multiselect(
                    "Category Filter (empty = all)",
                    options=['general', 'system', 'process_control', 'queue_management', 'log_management'],
                    help="Template will only be used for selected categories"
                )
            
            is_active = st.checkbox("Template Active", value=True)
            
            st.write("**Subject Template:**")
            subject_template = st.text_area(
                "Subject (use {{variable}} for substitution)",
                value="[{{severity|upper}}] {{title}}",
                height=50,
                help="Available variables: title, severity, source, timestamp"
            )
            
            st.write("**Body Template:**")
            body_template = st.text_area(
                "Body (use {{variable}} for substitution)",
                value="""{{message}}

Source: {{source}}
Time: {{timestamp}}
Severity: {{severity}}

{% if data %}
Additional Information:
{% for key, value in data.items() %}
- {{key}}: {{value}}
{% endfor %}
{% endif %}

---
Ansera Monitoring System""",
                height=200,
                help="Available variables: title, message, severity, source, timestamp, data"
            )
            
            st.write("**HTML Template (Optional):**")
            html_template = st.text_area(
                "HTML Body (use {{variable}} for substitution)",
                height=150,
                help="Optional HTML version of the email body"
            )
            
            submitted = st.form_submit_button("✨ Create Template", type="primary")
            
            if submitted:
                if not name.strip():
                    st.error("Template name is required")
                elif not subject_template.strip():
                    st.error("Subject template is required")
                elif not body_template.strip():
                    st.error("Body template is required")
                else:
                    # Create template
                    template = EmailTemplate(
                        id=str(uuid.uuid4()),
                        name=name.strip(),
                        subject_template=subject_template.strip(),
                        body_template=body_template.strip(),
                        html_template=html_template.strip() if html_template.strip() else None,
                        severity_filter=severity_filter if severity_filter else None,
                        category_filter=category_filter if category_filter else None,
                        is_active=is_active
                    )
                    
                    if self.email_service.add_template(template):
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
            - `{{severity}}` - Notification severity (info, warning, error, critical)
            - `{{source}}` - Notification source
            - `{{timestamp}}` - Notification timestamp
            - `{{data}}` - Additional data dictionary
            
            ### Template Filters:
            
            - `{{severity|upper}}` - Convert severity to uppercase
            - `{{title|title}}` - Convert title to title case
            - `{{timestamp|strftime('%Y-%m-%d %H:%M')}}` - Format timestamp
            
            ### Conditional Blocks:
            
            ```
            {% if data %}
            Additional Information:
            {% for key, value in data.items() %}
            - {{key}}: {{value}}
            {% endfor %}
            {% endif %}
            ```
            
            ### Example Subject Templates:
            
            - `[{{severity|upper}}] {{title}}`
            - `🚨 {{title}} - {{source}}`
            - `Ansera Alert: {{title}}`
            """)
    
    def _render_recipient_management(self):
        """Render recipient group management interface."""
        st.subheader("👥 Recipient Group Management")
        
        # Get current recipient groups
        recipient_groups = self.email_service.get_recipient_groups()
        
        # Recipient management tabs
        recipient_subtabs = st.tabs(["Groups List", "Edit Group", "Create Group"])
        
        with recipient_subtabs[0]:
            self._render_recipient_groups_list(recipient_groups)
        
        with recipient_subtabs[1]:
            self._render_recipient_group_editor(recipient_groups)
        
        with recipient_subtabs[2]:
            self._render_recipient_group_creator()
    
    def _render_recipient_groups_list(self, groups: Dict[str, EmailRecipientGroup]):
        """Render recipient groups list."""
        st.write("### Email Recipient Groups")
        
        if groups:
            # Groups table
            group_data = []
            for group in groups.values():
                group_data.append({
                    'ID': group.id,
                    'Name': group.name,
                    'Recipients': len(group.email_addresses),
                    'Email Addresses': ', '.join(group.email_addresses[:3]) + ('...' if len(group.email_addresses) > 3 else ''),
                    'Severity Filter': ', '.join(group.severity_filter) if group.severity_filter else 'All',
                    'Category Filter': ', '.join(group.category_filter) if group.category_filter else 'All',
                    'Active': '✅' if group.is_active else '❌',
                    'Created': group.created_at.strftime('%Y-%m-%d')
                })
            
            # Display groups with selection
            selected_indices = st.dataframe(
                group_data,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Group actions
            if group_data:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🗑️ Delete Selected", type="secondary"):
                        if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                            selected_idx = selected_indices.selection['rows'][0]
                            selected_group_id = group_data[selected_idx]['ID']
                            
                            if st.session_state.get('confirm_delete_group') == selected_group_id:
                                if self.email_service.remove_recipient_group(selected_group_id):
                                    st.success(f"Group '{group_data[selected_idx]['Name']}' deleted successfully!")
                                    st.session_state.confirm_delete_group = None
                                    st.rerun()
                                else:
                                    st.error("Failed to delete group")
                            else:
                                st.session_state.confirm_delete_group = selected_group_id
                                st.warning(f"Click again to confirm deletion of '{group_data[selected_idx]['Name']}'")
                
                # Group details
                if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                    selected_idx = selected_indices.selection['rows'][0]
                    selected_group_id = group_data[selected_idx]['ID']
                    selected_group = groups[selected_group_id]
                    
                    st.write("### Group Details")
                    
                    with st.expander(f"👥 {selected_group.name}", expanded=True):
                        st.write("**Email Addresses:**")
                        for email in selected_group.email_addresses:
                            st.write(f"• {email}")
                        
                        st.write("**Filters:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("Severity:", ', '.join(selected_group.severity_filter) if selected_group.severity_filter else 'All')
                        with col2:
                            st.write("Category:", ', '.join(selected_group.category_filter) if selected_group.category_filter else 'All')
        else:
            st.info("No recipient groups found. Create your first group using the 'Create Group' tab.")
    
    def _render_recipient_group_editor(self, groups: Dict[str, EmailRecipientGroup]):
        """Render recipient group editor."""
        st.write("### Edit Recipient Group")
        
        if not groups:
            st.info("No groups available to edit. Create a group first.")
            return
        
        # Group selection
        group_options = {gid: f"{group.name} ({len(group.email_addresses)} recipients)" for gid, group in groups.items()}
        selected_group_id = st.selectbox(
            "Select Group to Edit",
            options=list(group_options.keys()),
            format_func=lambda x: group_options[x]
        )
        
        if selected_group_id:
            group = groups[selected_group_id]
            
            # Group editing form
            with st.form(f"edit_group_{selected_group_id}"):
                name = st.text_input("Group Name", value=group.name)
                
                # Email addresses (one per line)
                email_addresses_text = st.text_area(
                    "Email Addresses (one per line)",
                    value='\n'.join(group.email_addresses),
                    height=150,
                    help="Enter one email address per line"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    severity_filter = st.multiselect(
                        "Severity Filter (empty = all)",
                        options=['info', 'warning', 'error', 'critical'],
                        default=group.severity_filter or []
                    )
                
                with col2:
                    category_filter = st.multiselect(
                        "Category Filter (empty = all)",
                        options=['general', 'system', 'process_control', 'queue_management', 'log_management'],
                        default=group.category_filter or []
                    )
                
                is_active = st.checkbox("Group Active", value=group.is_active)
                
                submitted = st.form_submit_button("💾 Update Group", type="primary")
                
                if submitted:
                    # Parse email addresses
                    email_addresses = [email.strip() for email in email_addresses_text.split('\n') if email.strip()]
                    
                    # Validate email addresses
                    invalid_emails = [email for email in email_addresses if '@' not in email]
                    
                    if not name.strip():
                        st.error("Group name is required")
                    elif not email_addresses:
                        st.error("At least one email address is required")
                    elif invalid_emails:
                        st.error(f"Invalid email addresses: {', '.join(invalid_emails)}")
                    else:
                        # Update group
                        updated_group = EmailRecipientGroup(
                            id=group.id,
                            name=name.strip(),
                            email_addresses=email_addresses,
                            severity_filter=severity_filter if severity_filter else None,
                            category_filter=category_filter if category_filter else None,
                            is_active=is_active,
                            created_at=group.created_at
                        )
                        
                        if self.email_service.add_recipient_group(updated_group):  # add_recipient_group handles updates too
                            st.success("✅ Group updated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update group")
    
    def _render_recipient_group_creator(self):
        """Render recipient group creator."""
        st.write("### Create New Recipient Group")
        
        with st.form("create_group_form"):
            name = st.text_input("Group Name *")
            
            # Email addresses (one per line)
            email_addresses_text = st.text_area(
                "Email Addresses (one per line) *",
                height=150,
                help="Enter one email address per line"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                severity_filter = st.multiselect(
                    "Severity Filter (empty = all)",
                    options=['info', 'warning', 'error', 'critical'],
                    help="Group will only receive selected severities"
                )
            
            with col2:
                category_filter = st.multiselect(
                    "Category Filter (empty = all)",
                    options=['general', 'system', 'process_control', 'queue_management', 'log_management'],
                    help="Group will only receive selected categories"
                )
            
            is_active = st.checkbox("Group Active", value=True)
            
            submitted = st.form_submit_button("✨ Create Group", type="primary")
            
            if submitted:
                # Parse email addresses
                email_addresses = [email.strip() for email in email_addresses_text.split('\n') if email.strip()]
                
                # Validate email addresses
                invalid_emails = [email for email in email_addresses if '@' not in email]
                
                if not name.strip():
                    st.error("Group name is required")
                elif not email_addresses:
                    st.error("At least one email address is required")
                elif invalid_emails:
                    st.error(f"Invalid email addresses: {', '.join(invalid_emails)}")
                else:
                    # Create group
                    group = EmailRecipientGroup(
                        id=str(uuid.uuid4()),
                        name=name.strip(),
                        email_addresses=email_addresses,
                        severity_filter=severity_filter if severity_filter else None,
                        category_filter=category_filter if category_filter else None,
                        is_active=is_active
                    )
                    
                    if self.email_service.add_recipient_group(group):
                        st.success(f"✅ Group '{name}' created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create group")
    
    def _render_email_settings(self):
        """Render email settings interface."""
        st.subheader("⚙️ Email Service Settings")
        
        # Get current settings
        current_settings = self.email_service.get_settings()
        templates = self.email_service.get_templates()
        groups = self.email_service.get_recipient_groups()
        
        # Settings form
        with st.form("email_settings_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**General Settings:**")
                
                enabled = st.checkbox(
                    "Enable Email Notifications",
                    value=current_settings.enabled,
                    help="Master switch for all email notifications"
                )
                
                from_email = st.text_input(
                    "From Email Address *",
                    value=current_settings.from_email,
                    help="Email address to send notifications from"
                )
                
                from_name = st.text_input(
                    "From Name",
                    value=current_settings.from_name,
                    help="Display name for outgoing emails"
                )
                
                rate_limit_per_hour = st.number_input(
                    "Rate Limit (emails per hour)",
                    min_value=1,
                    max_value=1000,
                    value=current_settings.rate_limit_per_hour,
                    help="Maximum emails to send per hour"
                )
            
            with col2:
                st.write("**Default Settings:**")
                
                # Default template
                template_options = {'': 'None'} | {tid: template.name for tid, template in templates.items()}
                default_template_id = st.selectbox(
                    "Default Template",
                    options=list(template_options.keys()),
                    index=list(template_options.keys()).index(current_settings.default_template_id or ''),
                    format_func=lambda x: template_options[x],
                    help="Default template to use for notifications"
                )
                
                # Default recipient group
                group_options = {'': 'None'} | {gid: group.name for gid, group in groups.items()}
                default_recipient_group_id = st.selectbox(
                    "Default Recipient Group",
                    options=list(group_options.keys()),
                    index=list(group_options.keys()).index(current_settings.default_recipient_group_id or ''),
                    format_func=lambda x: group_options[x],
                    help="Default recipient group for notifications"
                )
                
                batch_size = st.number_input(
                    "Batch Size",
                    min_value=1,
                    max_value=100,
                    value=current_settings.batch_size,
                    help="Number of emails to send in one batch"
                )
                
                st.write("**Retry Settings:**")
                
                retry_count = st.number_input(
                    "Retry Count",
                    min_value=0,
                    max_value=10,
                    value=current_settings.retry_count,
                    help="Number of times to retry failed emails"
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
                if not from_email.strip():
                    st.error("From email address is required")
                elif '@' not in from_email:
                    st.error("Invalid from email address")
                else:
                    # Create settings
                    settings = EmailSettings(
                        enabled=enabled,
                        from_email=from_email.strip(),
                        from_name=from_name.strip(),
                        default_template_id=default_template_id if default_template_id else None,
                        default_recipient_group_id=default_recipient_group_id if default_recipient_group_id else None,
                        rate_limit_per_hour=rate_limit_per_hour,
                        batch_size=batch_size,
                        retry_count=retry_count,
                        retry_delay_seconds=retry_delay_seconds
                    )
                    
                    if self.email_service.update_settings(settings):
                        st.success("✅ Settings saved successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save settings")
        
        # Global email toggle
        st.write("### Dashboard Integration")
        
        email_dashboard_enabled = st.checkbox(
            "Send Email Notifications for Dashboard Events",
            value=st.session_state.get('email_dashboard_enabled', False),
            help="Automatically send email notifications for dashboard events (service failures, etc.)"
        )
        
        st.session_state.email_dashboard_enabled = email_dashboard_enabled
        
        if not email_dashboard_enabled:
            st.info("Email notifications for dashboard events are disabled.")
    
    def _render_test_monitor(self):
        """Render email testing and monitoring interface."""
        st.subheader("🧪 Test & Monitor Email Service")
        
        # Service status
        st.write("### Service Status")
        
        stats = self.email_service.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_icon = "✅" if stats['smtp_configured'] else "❌"
            st.metric("SMTP Configured", f"{status_icon} {'Yes' if stats['smtp_configured'] else 'No'}")
        
        with col2:
            status_icon = "✅" if stats['service_enabled'] else "❌"
            st.metric("Service Enabled", f"{status_icon} {'Yes' if stats['service_enabled'] else 'No'}")
        
        with col3:
            st.metric("Templates", stats['templates_count'])
        
        with col4:
            st.metric("Recipient Groups", stats['recipient_groups_count'])
        
        # Rate limiting status
        st.write("### Rate Limiting")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Emails This Hour", stats['emails_sent_this_hour'])
        
        with col2:
            st.metric("Hourly Limit", stats['rate_limit_per_hour'])
        
        with col3:
            remaining = stats['rate_limit_remaining']
            delta_color = "normal" if remaining > 10 else "inverse"
            st.metric("Remaining", remaining, delta=f"{remaining} left", delta_color=delta_color)
        
        # SMTP Connection Test
        st.write("### SMTP Connection Test")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🔧 Test SMTP Connection", type="primary"):
                with st.spinner("Testing SMTP connection..."):
                    # Run async test
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(self.email_service.test_smtp_connection())
                        loop.close()
                        
                        st.session_state.last_smtp_test = result
                        st.rerun()
                    except Exception as e:
                        st.session_state.last_smtp_test = {
                            'success': False,
                            'error': str(e)
                        }
                        st.rerun()
        
        # Display test results
        if hasattr(st.session_state, 'last_smtp_test') and st.session_state.last_smtp_test:
            result = st.session_state.last_smtp_test
            
            if result['success']:
                st.success("✅ SMTP connection test successful!")
                if 'processing_time_ms' in result:
                    st.info(f"Response time: {result['processing_time_ms']}ms")
            else:
                st.error(f"❌ SMTP connection test failed: {result.get('error', 'Unknown error')}")
        
        # Email Test
        st.write("### Send Test Email")
        
        templates = self.email_service.get_templates()
        groups = self.email_service.get_recipient_groups()
        
        with st.form("test_email_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                test_title = st.text_input("Test Email Title", value="Email Service Test")
                test_message = st.text_area(
                    "Test Email Message",
                    value="This is a test email from the Ansera monitoring dashboard email service.",
                    height=100
                )
                test_severity = st.selectbox(
                    "Test Severity",
                    options=['info', 'warning', 'error', 'critical'],
                    index=0
                )
            
            with col2:
                # Template selection
                template_options = {'': 'Default'} | {tid: template.name for tid, template in templates.items()}
                test_template_id = st.selectbox(
                    "Template",
                    options=list(template_options.keys()),
                    format_func=lambda x: template_options[x]
                )
                
                # Recipient options
                recipient_type = st.radio(
                    "Recipients",
                    options=["Group", "Custom"],
                    index=0
                )
                
                if recipient_type == "Group":
                    if groups:
                        group_options = {gid: group.name for gid, group in groups.items()}
                        test_group_id = st.selectbox(
                            "Recipient Group",
                            options=list(group_options.keys()),
                            format_func=lambda x: group_options[x]
                        )
                        test_recipients = None
                    else:
                        st.warning("No recipient groups available")
                        test_group_id = None
                        test_recipients = None
                else:
                    test_recipients_text = st.text_area(
                        "Email Addresses (one per line)",
                        height=100
                    )
                    test_recipients = [email.strip() for email in test_recipients_text.split('\n') if email.strip()]
                    test_group_id = None
            
            submitted = st.form_submit_button("📧 Send Test Email", type="primary")
            
            if submitted:
                if recipient_type == "Group" and not test_group_id:
                    st.error("Please select a recipient group")
                elif recipient_type == "Custom" and not test_recipients:
                    st.error("Please enter at least one email address")
                elif recipient_type == "Custom" and any('@' not in email for email in test_recipients):
                    st.error("Please enter valid email addresses")
                else:
                    with st.spinner("Sending test email..."):
                        try:
                            # Run async send
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            success = loop.run_until_complete(
                                self.email_service.send_notification(
                                    title=test_title,
                                    message=test_message,
                                    severity=NotificationSeverity(test_severity),
                                    category="test",
                                    source="email_ui_test",
                                    template_id=test_template_id if test_template_id else None,
                                    recipient_group_id=test_group_id,
                                    custom_recipients=test_recipients,
                                    data={"test_timestamp": datetime.now().isoformat()}
                                )
                            )
                            
                            loop.close()
                            
                            if success:
                                st.success("✅ Test email sent successfully!")
                                st.session_state.last_email_test = {
                                    'success': True,
                                    'timestamp': datetime.now().isoformat()
                                }
                            else:
                                st.error("❌ Failed to send test email")
                                st.session_state.last_email_test = {
                                    'success': False,
                                    'timestamp': datetime.now().isoformat()
                                }
                        
                        except Exception as e:
                            st.error(f"❌ Error sending test email: {str(e)}")
                            st.session_state.last_email_test = {
                                'success': False,
                                'error': str(e),
                                'timestamp': datetime.now().isoformat()
                            }
        
        # Quick test buttons
        st.write("### Quick Tests")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📧 Test Info"):
                if self._send_quick_test("info"):
                    st.success("Info test sent!")
        
        with col2:
            if st.button("⚠️ Test Warning"):
                if self._send_quick_test("warning"):
                    st.success("Warning test sent!")
        
        with col3:
            if st.button("❌ Test Error"):
                if self._send_quick_test("error"):
                    st.success("Error test sent!")
        
        with col4:
            if st.button("🚨 Test Critical"):
                if self._send_quick_test("critical"):
                    st.success("Critical test sent!")
    
    def _send_quick_test(self, severity: str) -> bool:
        """Send a quick test email."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(
                self.email_service.send_notification(
                    title=f"Quick {severity.title()} Test",
                    message=f"This is a quick {severity} test from the email service.",
                    severity=NotificationSeverity(severity),
                    category="quick_test",
                    source="email_ui_quick_test",
                    data={"test_type": "quick", "severity": severity}
                )
            )
            
            loop.close()
            return success
        
        except Exception as e:
            st.error(f"Quick test failed: {str(e)}")
            return False


# Global UI instance
_email_ui: Optional[EmailNotificationUI] = None


def get_email_notification_ui() -> EmailNotificationUI:
    """Get singleton email notification UI instance."""
    global _email_ui
    
    if _email_ui is None:
        _email_ui = EmailNotificationUI()
    
    return _email_ui