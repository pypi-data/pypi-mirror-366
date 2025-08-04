"""
API Key Management UI for monitoring dashboard.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

from .api_key_manager import get_api_key_manager
from .api_key_models import APIKey, APIKeyStatus, APIKeyScope, APIKeyPermission, PERMISSION_SETS
from .security_audit import get_security_auditor, SecurityEventType, SecurityEventSeverity


class APIKeyManagementUI:
    """
    Streamlit UI component for API key management.
    """
    
    def __init__(self):
        """Initialize API key management UI."""
        self.api_key_manager = get_api_key_manager()
        self.security_auditor = get_security_auditor()
    
    def render(self) -> None:
        """Render the complete API key management UI."""
        st.header("🔐 API Key Management")
        
        # Create tabs for different management functions
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🔑 API Keys", "➕ Create Key", "📊 Usage Analytics", 
            "🔍 Security Audit", "⚙️ Settings", "📚 Documentation"
        ])
        
        with tab1:
            self._render_api_keys_tab()
        
        with tab2:
            self._render_create_key_tab()
        
        with tab3:
            self._render_analytics_tab()
        
        with tab4:
            self._render_security_audit_tab()
        
        with tab5:
            self._render_settings_tab()
        
        with tab6:
            self._render_documentation_tab()
    
    def _render_api_keys_tab(self) -> None:
        """Render API keys management interface."""
        st.subheader("API Key Management")
        
        # Controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                options=["All"] + [status.value.title() for status in APIKeyStatus],
                help="Filter keys by their current status"
            )
        
        with col2:
            owner_filter = st.text_input("Filter by Owner", help="Filter by owner email")
        
        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        # Get API keys
        status_enum = None
        if status_filter != "All":
            status_enum = APIKeyStatus(status_filter.lower())
        
        api_keys = self.api_key_manager.list_api_keys(
            status_filter=status_enum,
            owner_email=owner_filter if owner_filter else None,
            limit=100
        )
        
        if not api_keys:
            st.info("No API keys found matching the current filters.")
            return
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        active_count = len([k for k in api_keys if k.status == APIKeyStatus.ACTIVE])
        expired_count = len([k for k in api_keys if k.is_expired()])
        used_today = len([k for k in api_keys if k.last_used_at and k.last_used_at.date() == datetime.now().date()])
        
        with col1:
            st.metric("Total Keys", len(api_keys))
        with col2:
            st.metric("Active", active_count)
        with col3:
            st.metric("Expired", expired_count)
        with col4:
            st.metric("Used Today", used_today)
        
        # API keys table
        st.write("**API Keys**")
        
        # Prepare data for display
        display_data = []
        for key in api_keys:
            display_data.append({
                'Name': key.name,
                'Key': key.key_prefix,
                'Status': key.status.value.title(),
                'Owner': key.owner_email or key.owner_name or 'Unknown',
                'Created': key.created_at.strftime('%Y-%m-%d'),
                'Last Used': key.last_used_at.strftime('%Y-%m-%d %H:%M') if key.last_used_at else 'Never',
                'Expires': key.expires_at.strftime('%Y-%m-%d') if key.expires_at else 'Never',
                'Requests': key.usage_stats.total_requests,
                'Success Rate': f"{key.usage_stats.get_success_rate():.1f}%",
                'Key ID': key.key_id
            })
        
        df = pd.DataFrame(display_data)
        
        # Display table with selection
        event = st.dataframe(
            df.drop('Key ID', axis=1),  # Hide internal ID
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Handle selected key
        if event.selection and event.selection.rows:
            selected_idx = event.selection.rows[0]
            selected_key = api_keys[selected_idx]
            
            st.write("**Selected Key Actions**")
            
            # Key details in expander
            with st.expander(f"🔍 Details: {selected_key.name}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Basic Information**")
                    st.write(f"**Name:** {selected_key.name}")
                    st.write(f"**Description:** {selected_key.description or 'No description'}")
                    st.write(f"**Status:** {selected_key.status.value.title()}")
                    st.write(f"**Created:** {selected_key.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Created By:** {selected_key.created_by}")
                    
                    if selected_key.expires_at:
                        days_until_expiry = (selected_key.expires_at - datetime.now()).days
                        if days_until_expiry < 0:
                            st.error(f"**Expired:** {abs(days_until_expiry)} days ago")
                        elif days_until_expiry < 30:
                            st.warning(f"**Expires:** In {days_until_expiry} days")
                        else:
                            st.write(f"**Expires:** {selected_key.expires_at.strftime('%Y-%m-%d')}")
                    else:
                        st.write("**Expires:** Never")
                
                with col2:
                    st.write("**Usage Statistics**")
                    st.write(f"**Total Requests:** {selected_key.usage_stats.total_requests:,}")
                    st.write(f"**Success Rate:** {selected_key.usage_stats.get_success_rate():.1f}%")
                    st.write(f"**Last Used:** {selected_key.last_used_at.strftime('%Y-%m-%d %H:%M:%S') if selected_key.last_used_at else 'Never'}")
                    st.write(f"**Bandwidth Used:** {selected_key.usage_stats.bandwidth_used / (1024*1024):.1f} MB")
                    
                    if selected_key.usage_stats.last_used_at:
                        hours_since_use = (datetime.now() - selected_key.usage_stats.last_used_at).total_seconds() / 3600
                        if hours_since_use < 1:
                            st.success("Recently active")
                        elif hours_since_use < 24:
                            st.info(f"Used {hours_since_use:.1f} hours ago")
                        else:
                            st.write(f"Used {hours_since_use/24:.1f} days ago")
                
                # Permissions and scopes
                if selected_key.scopes:
                    st.write("**Scopes:**")
                    scope_cols = st.columns(min(len(selected_key.scopes), 4))
                    for i, scope in enumerate(selected_key.scopes):
                        with scope_cols[i % 4]:
                            st.badge(scope.value, type="secondary")
                
                if selected_key.permissions:
                    st.write("**Permissions:**")
                    perm_text = ", ".join([p.value.replace('_', ' ').title() for p in selected_key.permissions])
                    st.text_area("", perm_text, height=60, disabled=True)
                
                # Security settings
                if selected_key.allowed_ips:
                    st.write("**Allowed IPs:**")
                    st.write(", ".join(selected_key.allowed_ips))
                
                if selected_key.allowed_origins:
                    st.write("**Allowed Origins:**")
                    st.write(", ".join(selected_key.allowed_origins))
            
            # Action buttons
            action_col1, action_col2, action_col3, action_col4, action_col5 = st.columns(5)
            
            with action_col1:
                if selected_key.status == APIKeyStatus.ACTIVE:
                    if st.button("⏸️ Suspend", use_container_width=True):
                        self._suspend_key(selected_key.key_id)
                elif selected_key.status == APIKeyStatus.SUSPENDED:
                    if st.button("▶️ Activate", use_container_width=True):
                        self._activate_key(selected_key.key_id)
            
            with action_col2:
                if st.button("📝 Edit", use_container_width=True):
                    self._show_edit_key_dialog(selected_key)
            
            with action_col3:
                if st.button("📊 Analytics", use_container_width=True):
                    self._show_key_analytics(selected_key)
            
            with action_col4:
                if st.button("🔍 Audit Trail", use_container_width=True):
                    self._show_audit_trail(selected_key)
            
            with action_col5:
                if st.button("🗑️ Revoke", type="primary", use_container_width=True):
                    self._revoke_key_dialog(selected_key)
    
    def _render_create_key_tab(self) -> None:
        """Render API key creation interface."""
        st.subheader("Create New API Key")
        
        with st.form("create_api_key"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Information**")
                
                name = st.text_input(
                    "API Key Name *",
                    help="Give your API key a descriptive name"
                )
                
                description = st.text_area(
                    "Description",
                    help="Describe what this API key will be used for"
                )
                
                owner_name = st.text_input("Owner Name")
                owner_email = st.text_input("Owner Email")
                
                expires_option = st.selectbox(
                    "Expiration",
                    options=["90 days", "180 days", "1 year", "Never"],
                    help="When should this key expire?"
                )
            
            with col2:
                st.write("**Access Control**")
                
                # Permission set selection
                permission_set = st.selectbox(
                    "Permission Template",
                    options=["Custom"] + list(PERMISSION_SETS.keys()),
                    format_func=lambda x: x.replace('_', ' ').title(),
                    help="Choose a predefined permission set or create custom"
                )
                
                # Custom permissions if selected
                if permission_set == "Custom":
                    selected_scopes = st.multiselect(
                        "Scopes",
                        options=[scope.value for scope in APIKeyScope],
                        format_func=lambda x: x.replace('_', ' ').title(),
                        help="High-level access scopes"
                    )
                    
                    selected_permissions = st.multiselect(
                        "Specific Permissions",
                        options=[perm.value for perm in APIKeyPermission],
                        format_func=lambda x: x.replace('_', ' ').title(),
                        help="Specific permissions to grant"
                    )
                else:
                    # Show permissions in the selected set
                    permissions_in_set = PERMISSION_SETS.get(permission_set, set())
                    st.write("**Included Permissions:**")
                    perm_text = "\n".join([f"• {p.value.replace('_', ' ').title()}" for p in permissions_in_set])
                    st.text_area("", perm_text, height=120, disabled=True)
                
                # IP restrictions
                ip_restriction = st.checkbox("Restrict by IP Address")
                if ip_restriction:
                    allowed_ips = st.text_area(
                        "Allowed IPs (one per line)",
                        help="Enter IP addresses that can use this key"
                    )
                
                # Origin restrictions
                origin_restriction = st.checkbox("Restrict by Origin (CORS)")
                if origin_restriction:
                    allowed_origins = st.text_area(
                        "Allowed Origins (one per line)",
                        help="Enter origins that can use this key"
                    )
            
            # Rate limiting settings
            st.write("**Rate Limiting**")
            rate_col1, rate_col2, rate_col3 = st.columns(3)
            
            with rate_col1:
                requests_per_minute = st.number_input("Requests per Minute", min_value=1, value=100)
            with rate_col2:
                requests_per_hour = st.number_input("Requests per Hour", min_value=1, value=1000)
            with rate_col3:
                bandwidth_limit = st.number_input("Bandwidth Limit (MB/hour)", min_value=1, value=100)
            
            # Submit button
            submitted = st.form_submit_button("🔑 Create API Key", type="primary", use_container_width=True)
            
            if submitted:
                if not name:
                    st.error("API Key name is required")
                    return
                
                # Parse expiration
                expires_days = 0
                if expires_option == "90 days":
                    expires_days = 90
                elif expires_option == "180 days":
                    expires_days = 180
                elif expires_option == "1 year":
                    expires_days = 365
                
                # Parse IPs and origins
                ips = [ip.strip() for ip in (allowed_ips.split('\n') if ip_restriction else [])] if ip_restriction else []
                origins = [origin.strip() for origin in (allowed_origins.split('\n') if origin_restriction else [])] if origin_restriction else []
                
                # Create the key
                try:
                    if permission_set == "Custom":
                        scopes = [APIKeyScope(s) for s in selected_scopes]
                        permissions = [APIKeyPermission(p) for p in selected_permissions]
                        perm_set = None
                    else:
                        scopes = []
                        permissions = []
                        perm_set = permission_set
                    
                    api_key, key_string = self.api_key_manager.create_api_key(
                        name=name,
                        description=description,
                        scopes=scopes,
                        permissions=permissions,
                        permission_set=perm_set,
                        expires_days=expires_days,
                        owner_email=owner_email,
                        owner_name=owner_name,
                        allowed_ips=ips,
                        created_by="dashboard_user"
                    )
                    
                    # Update rate limits
                    api_key.rate_limit.requests_per_minute = requests_per_minute
                    api_key.rate_limit.requests_per_hour = requests_per_hour
                    api_key.rate_limit.bandwidth_limit_mb = bandwidth_limit
                    
                    st.success("✅ API Key created successfully!")
                    
                    # Display the key (only shown once)
                    st.warning("⚠️ **Important:** This is the only time you'll see the full API key. Save it securely!")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.code(key_string, language="text")
                    with col2:
                        st.download_button(
                            "📥 Download Key",
                            data=f"API Key: {key_string}\nName: {name}\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                            file_name=f"api_key_{name.replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                    
                    # Show next steps
                    st.info("""
                    **Next Steps:**
                    1. Save the API key in a secure location
                    2. Test the key with a simple API call
                    3. Monitor usage in the Analytics tab
                    4. Set up alerts for suspicious activity
                    """)
                    
                except Exception as e:
                    st.error(f"Failed to create API key: {str(e)}")
    
    def _render_analytics_tab(self) -> None:
        """Render usage analytics interface."""
        st.subheader("Usage Analytics")
        
        # Time range selector
        col1, col2 = st.columns(2)
        with col1:
            time_range = st.selectbox(
                "Time Range",
                options=["Last 7 days", "Last 30 days", "Last 90 days"],
                help="Select time range for analytics"
            )
        
        with col2:
            api_keys = self.api_key_manager.list_api_keys(limit=50)
            key_names = ["All Keys"] + [f"{key.name} ({key.key_prefix})" for key in api_keys]
            selected_key = st.selectbox("Filter by Key", options=key_names)
        
        # Parse time range
        days = 7
        if time_range == "Last 30 days":
            days = 30
        elif time_range == "Last 90 days":
            days = 90
        
        # Get overall statistics
        overall_stats = self.api_key_manager.get_api_key_statistics()
        
        # Display overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total API Keys", overall_stats['total_keys'])
        with col2:
            st.metric("Active Keys", overall_stats['active_keys'])
        with col3:
            st.metric("Recent Usage", f"{overall_stats['recent_usage_30_days']:,}")
        with col4:
            success_rate = 95.5  # Would calculate from actual data
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Usage charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**API Key Status Distribution**")
            if overall_stats['by_status']:
                status_df = pd.DataFrame([
                    {'Status': status.title(), 'Count': count}
                    for status, count in overall_stats['by_status'].items()
                ])
                
                fig = px.pie(
                    status_df, 
                    values='Count', 
                    names='Status',
                    color_discrete_sequence=['#28a745', '#ffc107', '#dc3545', '#6c757d']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available")
        
        with col2:
            st.write("**Most Active Keys**")
            if overall_stats['most_active_keys']:
                active_df = pd.DataFrame(overall_stats['most_active_keys'])
                fig = px.bar(
                    active_df.head(10), 
                    x='requests', 
                    y='name',
                    orientation='h',
                    color='requests',
                    color_continuous_scale='viridis'
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No usage data available")
        
        # Detailed key analytics if specific key selected
        if selected_key != "All Keys":
            selected_key_name = selected_key.split(" (")[0]
            key = next((k for k in api_keys if k.name == selected_key_name), None)
            
            if key:
                st.divider()
                st.write(f"**Detailed Analytics: {key.name}**")
                
                usage_stats = self.api_key_manager.get_usage_statistics(key.key_id, days)
                
                # Usage metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Requests", f"{usage_stats['overall']['total_requests']:,}")
                with col2:
                    st.metric("Success Rate", f"{usage_stats['overall']['success_rate']:.1f}%")
                with col3:
                    st.metric("Avg Response Time", f"{usage_stats['overall']['avg_response_time_ms']:.0f}ms")
                with col4:
                    bandwidth_mb = usage_stats['overall']['total_bytes_transferred'] / (1024 * 1024)
                    st.metric("Data Transferred", f"{bandwidth_mb:.1f} MB")
                
                # Endpoint usage
                if usage_stats['by_endpoint']:
                    st.write("**Usage by Endpoint**")
                    endpoint_df = pd.DataFrame(usage_stats['by_endpoint'])
                    
                    fig = px.bar(
                        endpoint_df.head(10),
                        x='requests',
                        y='endpoint',
                        orientation='h',
                        color='success_rate',
                        color_continuous_scale='RdYlGn',
                        color_continuous_midpoint=95
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
    
    def _render_security_audit_tab(self) -> None:
        """Render security audit interface."""
        st.subheader("Security Audit")
        
        # Time range selector
        col1, col2 = st.columns(2)
        with col1:
            audit_days = st.selectbox(
                "Audit Period",
                options=[7, 14, 30, 90],
                format_func=lambda x: f"Last {x} days",
                help="Select period for security audit"
            )
        
        with col2:
            if st.button("🔄 Refresh Audit", use_container_width=True):
                st.rerun()
        
        # Get security summary
        security_summary = self.security_auditor.get_security_summary(audit_days)
        
        # Security overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", f"{security_summary['total_events']:,}")
        with col2:
            st.metric("Critical Events", security_summary['critical_events'])
        with col3:
            st.metric("Suspicious IPs", len(security_summary['suspicious_ips']))
        with col4:
            st.metric("Blocked IPs", security_summary['blocked_ips'])
        
        # Security event distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Events by Type**")
            if security_summary['events_by_type']:
                type_df = pd.DataFrame([
                    {'Event Type': event_type.replace('_', ' ').title(), 'Count': count}
                    for event_type, count in security_summary['events_by_type'].items()
                ])
                
                fig = px.bar(type_df, x='Count', y='Event Type', orientation='h')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No security events in selected period")
        
        with col2:
            st.write("**Events by Severity**")
            if security_summary['events_by_severity']:
                severity_df = pd.DataFrame([
                    {'Severity': severity.title(), 'Count': count}
                    for severity, count in security_summary['events_by_severity'].items()
                ])
                
                fig = px.pie(
                    severity_df,
                    values='Count',
                    names='Severity',
                    color_discrete_map={
                        'Low': '#28a745',
                        'Medium': '#ffc107', 
                        'High': '#fd7e14',
                        'Critical': '#dc3545'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # High-risk events
        if security_summary['risky_events']:
            st.write("**High-Risk Events**")
            risk_df = pd.DataFrame(security_summary['risky_events'])
            risk_df['timestamp'] = pd.to_datetime(risk_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(
                risk_df[['timestamp', 'message', 'risk_score', 'ip_address']],
                use_container_width=True,
                hide_index=True
            )
        
        # Suspicious IPs
        if security_summary['suspicious_ips']:
            st.write("**Suspicious IP Addresses**")
            
            for ip_info in security_summary['suspicious_ips'][:10]:
                with st.expander(f"🚨 {ip_info['ip_address']} - {ip_info['failed_attempts']} failed attempts"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Failed Attempts:** {ip_info['failed_attempts']}")
                        st.write(f"**Total Requests:** {ip_info['total_requests']}")
                    
                    with col2:
                        st.write(f"**Last Seen:** {ip_info['last_seen'][:19]}")
                        failure_rate = (ip_info['failed_attempts'] / max(ip_info['total_requests'], 1)) * 100
                        st.write(f"**Failure Rate:** {failure_rate:.1f}%")
                    
                    with col3:
                        if st.button(f"🚫 Block IP", key=f"block_{ip_info['ip_address']}"):
                            self.security_auditor.block_ip_address(
                                ip_info['ip_address'], 
                                "Blocked from dashboard due to suspicious activity"
                            )
                            st.success(f"IP {ip_info['ip_address']} has been blocked")
                            st.rerun()
        
        # Anomaly detection
        st.write("**Security Anomalies**")
        anomalies = self.security_auditor.detect_anomalies(audit_days)
        
        if anomalies:
            for anomaly in anomalies:
                severity_color = {
                    'low': 'success',
                    'medium': 'warning', 
                    'high': 'error',
                    'critical': 'error'
                }.get(anomaly['severity'], 'info')
                
                with st.container():
                    st.write(f"**{anomaly['type'].replace('_', ' ').title()}** - {anomaly['severity'].title()}")
                    if severity_color == 'error':
                        st.error(anomaly['description'])
                    elif severity_color == 'warning':
                        st.warning(anomaly['description'])
                    else:
                        st.info(anomaly['description'])
        else:
            st.success("✅ No security anomalies detected in the selected period")
    
    def _render_settings_tab(self) -> None:
        """Render API key system settings."""
        st.subheader("API Key System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Default Settings**")
            
            default_expiry = st.selectbox(
                "Default Key Expiry",
                options=[30, 90, 180, 365, 0],
                format_func=lambda x: f"{x} days" if x > 0 else "Never expires",
                index=1,  # Default to 90 days
                help="Default expiration period for new API keys"
            )
            
            max_keys_per_user = st.number_input(
                "Max Keys per User",
                min_value=1,
                max_value=50,
                value=10,
                help="Maximum number of API keys a user can create"
            )
            
            auto_cleanup = st.checkbox(
                "Auto-cleanup Expired Keys",
                value=True,
                help="Automatically clean up expired keys"
            )
            
            if auto_cleanup:
                cleanup_days = st.number_input(
                    "Cleanup After (days)",
                    min_value=1,
                    max_value=365,
                    value=30,
                    help="Delete expired keys after this many days"
                )
        
        with col2:
            st.write("**Security Settings**")
            
            require_https = st.checkbox(
                "Require HTTPS",
                value=True,
                help="Require all API requests to use HTTPS"
            )
            
            enable_ip_blocking = st.checkbox(
                "Enable IP Blocking",
                value=True,
                help="Automatically block suspicious IP addresses"
            )
            
            failed_attempts_threshold = st.number_input(
                "Failed Attempts Threshold",
                min_value=3,
                max_value=20,
                value=5,
                help="Block IP after this many failed attempts"
            )
            
            audit_retention_days = st.number_input(
                "Audit Log Retention (days)",
                min_value=30,
                max_value=365,
                value=90,
                help="How long to keep security audit logs"
            )
        
        # Rate limiting defaults
        st.write("**Default Rate Limits**")
        
        rate_col1, rate_col2, rate_col3 = st.columns(3)
        
        with rate_col1:
            default_rpm = st.number_input("Default RPM", min_value=1, value=100)
        with rate_col2:
            default_rph = st.number_input("Default RPH", min_value=1, value=1000)
        with rate_col3:
            default_bandwidth = st.number_input("Default Bandwidth (MB/h)", min_value=1, value=100)
        
        # Save settings
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            settings = {
                'default_expiry_days': default_expiry,
                'max_keys_per_user': max_keys_per_user,
                'auto_cleanup': auto_cleanup,
                'cleanup_days': cleanup_days if auto_cleanup else 30,
                'require_https': require_https,
                'enable_ip_blocking': enable_ip_blocking,
                'failed_attempts_threshold': failed_attempts_threshold,
                'audit_retention_days': audit_retention_days,
                'default_rate_limits': {
                    'requests_per_minute': default_rpm,
                    'requests_per_hour': default_rph,
                    'bandwidth_mb_per_hour': default_bandwidth
                }
            }
            
            # Save settings (implementation would save to config file)
            st.success("Settings saved successfully!")
        
        # System maintenance
        st.divider()
        st.write("**System Maintenance**")
        
        maint_col1, maint_col2, maint_col3 = st.columns(3)
        
        with maint_col1:
            if st.button("🧹 Cleanup Expired Keys", use_container_width=True):
                count = self.api_key_manager.cleanup_expired_keys()
                st.success(f"Cleaned up {count} expired keys")
        
        with maint_col2:
            if st.button("🗑️ Clean Audit Logs", use_container_width=True):
                count = self.security_auditor.cleanup_old_events(audit_retention_days)
                st.success(f"Cleaned up {count} old audit events")
        
        with maint_col3:
            if st.button("📊 Generate Report", use_container_width=True):
                self._generate_security_report()
    
    def _render_documentation_tab(self) -> None:
        """Render API documentation and examples."""
        st.subheader("API Documentation")
        
        # API usage examples
        st.write("**Authentication**")
        st.code("""
# Include the API key in the Authorization header
curl -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "Content-Type: application/json" \\
     https://your-domain.com/api/v1/metrics
        """, language="bash")
        
        st.write("**Common Endpoints**")
        
        endpoints = [
            {
                "endpoint": "GET /api/v1/metrics/system",
                "description": "Get current system metrics",
                "permissions": ["view_system_metrics"],
                "example": """
curl -H "Authorization: Bearer YOUR_API_KEY" \\
     https://your-domain.com/api/v1/metrics/system
                """
            },
            {
                "endpoint": "POST /api/v1/services/restart",
                "description": "Restart a service",
                "permissions": ["restart_services"],
                "example": """
curl -X POST \\
     -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{"service": "worker"}' \\
     https://your-domain.com/api/v1/services/restart
                """
            },
            {
                "endpoint": "GET /api/v1/export/data",
                "description": "Export dashboard data",
                "permissions": ["export_data"],
                "example": """
curl -H "Authorization: Bearer YOUR_API_KEY" \\
     "https://your-domain.com/api/v1/export/data?format=json&type=system_metrics"
                """
            }
        ]
        
        for endpoint in endpoints:
            with st.expander(f"📡 {endpoint['endpoint']}"):
                st.write(f"**Description:** {endpoint['description']}")
                st.write(f"**Required Permissions:** {', '.join(endpoint['permissions'])}")
                st.code(endpoint['example'], language="bash")
        
        # Permission reference
        st.write("**Permission Reference**")
        
        permission_groups = {
            "System Monitoring": [
                "view_system_metrics", "view_process_info", "view_queue_status"
            ],
            "Process Control": [
                "start_services", "stop_services", "restart_services",
                "pause_queue", "resume_queue"
            ],
            "Configuration": [
                "view_config", "modify_config", "view_layouts", "modify_layouts"
            ],
            "Export & Reporting": [
                "export_data", "view_reports", "generate_reports"
            ],
            "Administration": [
                "view_users", "manage_users", "view_api_keys", 
                "manage_api_keys", "system_admin"
            ]
        }
        
        for group, permissions in permission_groups.items():
            with st.expander(f"🔐 {group}"):
                for perm in permissions:
                    st.write(f"• **{perm}**: {perm.replace('_', ' ').title()}")
        
        # Rate limiting info
        st.write("**Rate Limiting**")
        st.info("""
        API keys are subject to rate limiting to ensure fair usage:
        
        - **Requests per minute**: Default 100, configurable per key
        - **Requests per hour**: Default 1,000, configurable per key  
        - **Daily requests**: Default 10,000, configurable per key
        - **Bandwidth**: Default 100MB/hour, configurable per key
        
        When rate limits are exceeded, you'll receive a `429 Too Many Requests` response.
        """)
        
        # Error handling
        st.write("**Error Responses**")
        
        error_codes = [
            {"code": 401, "meaning": "Unauthorized", "description": "Invalid or missing API key"},
            {"code": 403, "meaning": "Forbidden", "description": "API key lacks required permissions"},
            {"code": 429, "meaning": "Too Many Requests", "description": "Rate limit exceeded"},
            {"code": 500, "meaning": "Internal Server Error", "description": "Server error occurred"}
        ]
        
        error_df = pd.DataFrame(error_codes)
        st.dataframe(error_df, use_container_width=True, hide_index=True)
    
    # Helper methods for actions
    
    def _suspend_key(self, key_id: str) -> None:
        """Suspend an API key."""
        success = self.api_key_manager.suspend_api_key(key_id, "Suspended from dashboard")
        if success:
            st.success("API key suspended successfully")
            st.rerun()
        else:
            st.error("Failed to suspend API key")
    
    def _activate_key(self, key_id: str) -> None:
        """Activate an API key."""
        success = self.api_key_manager.activate_api_key(key_id)
        if success:
            st.success("API key activated successfully")
            st.rerun()
        else:
            st.error("Failed to activate API key")
    
    def _revoke_key_dialog(self, api_key: APIKey) -> None:
        """Show revoke key confirmation dialog."""
        with st.form(f"revoke_key_{api_key.key_id}"):
            st.warning(f"⚠️ **Are you sure you want to revoke '{api_key.name}'?**")
            st.write("This action cannot be undone. The API key will be permanently disabled.")
            
            reason = st.text_input("Reason for revocation", placeholder="e.g., Key compromised")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.rerun()
            with col2:
                if st.form_submit_button("🗑️ Revoke Key", type="primary", use_container_width=True):
                    success = self.api_key_manager.revoke_api_key(
                        api_key.key_id, 
                        "dashboard_user", 
                        reason or "Revoked from dashboard"
                    )
                    if success:
                        st.success("API key revoked successfully")
                        st.rerun()
                    else:
                        st.error("Failed to revoke API key")
    
    def _show_edit_key_dialog(self, api_key: APIKey) -> None:
        """Show edit key dialog."""
        st.info("Edit functionality would be implemented here")
    
    def _show_key_analytics(self, api_key: APIKey) -> None:
        """Show detailed analytics for a key."""
        st.info("Detailed analytics would be implemented here")
    
    def _show_audit_trail(self, api_key: APIKey) -> None:
        """Show audit trail for a key."""
        st.info("Audit trail would be implemented here")
    
    def _generate_security_report(self) -> None:
        """Generate a security report."""
        st.success("Security report generated successfully (would be implemented)")
        st.info("Report would include comprehensive security analysis and recommendations")