"""
Comprehensive audit logging user interface for Streamlit.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

from .audit_logger import get_audit_logger
from .audit_analyzer import get_audit_analyzer
from .audit_models import (
    AuditEvent, AuditEventType, AuditEventCategory, AuditEventSeverity,
    AuditEventContext, create_audit_event_from_template
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class AuditLoggingUI:
    """Streamlit UI for audit logging system."""
    
    def __init__(self):
        """Initialize audit logging UI."""
        self.audit_logger = get_audit_logger()
        self.audit_analyzer = get_audit_analyzer()
        self.change_tracker = get_change_tracker()
    
    def render(self):
        """Render the complete audit logging interface."""
        st.title("🔍 Audit Logging System")
        st.markdown("Comprehensive system activity tracking and analysis")
        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Overview", "🔍 Event Search", "📈 Analytics", "🚨 Anomalies", 
            "📋 Compliance", "⚙️ Configuration", "🧪 Test Events"
        ])
        
        with tab1:
            self._render_overview_tab()
        
        with tab2:
            self._render_event_search_tab()
        
        with tab3:
            self._render_analytics_tab()
        
        with tab4:
            self._render_anomalies_tab()
        
        with tab5:
            self._render_compliance_tab()
        
        with tab6:
            self._render_configuration_tab()
        
        with tab7:
            self._render_test_events_tab()
    
    def _render_overview_tab(self):
        """Render overview dashboard."""
        st.subheader("📊 Audit Overview")
        
        # Get statistics
        stats = self.audit_logger.get_statistics(days=30)
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Events (30d)",
                f"{stats.get('total_events', 0):,}",
                delta=None
            )
        
        with col2:
            critical_events = stats.get('critical_events', 0)
            st.metric(
                "Critical Events",
                critical_events,
                delta=f"🔴 {critical_events}" if critical_events > 0 else None
            )
        
        with col3:
            high_events = stats.get('high_events', 0)
            st.metric(
                "High Severity",
                high_events,
                delta=f"🟠 {high_events}" if high_events > 0 else None
            )
        
        with col4:
            # Get recent anomalies
            anomalies = self.audit_analyzer.detect_anomalies(hours=24)
            st.metric(
                "Anomalies (24h)",
                len(anomalies),
                delta=f"⚠️ {len(anomalies)}" if anomalies else None
            )
        
        st.divider()
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            # Events by category
            st.subheader("Events by Category")
            category_data = stats.get('events_by_category', {})
            if category_data:
                fig = px.pie(
                    values=list(category_data.values()),
                    names=list(category_data.keys()),
                    title="Distribution of Events by Category"
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No event data available")
        
        with col2:
            # Events by severity
            st.subheader("Events by Severity")
            severity_data = stats.get('events_by_severity', {})
            if severity_data:
                # Color map for severities
                color_map = {
                    'info': '#17becf',
                    'low': '#2ca02c',
                    'medium': '#ff7f0e',
                    'high': '#d62728',
                    'critical': '#8c0303'
                }
                colors = [color_map.get(sev, '#17becf') for sev in severity_data.keys()]
                
                fig = px.bar(
                    x=list(severity_data.keys()),
                    y=list(severity_data.values()),
                    title="Events by Severity Level",
                    color=list(severity_data.keys()),
                    color_discrete_map=color_map
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No severity data available")
        
        st.divider()
        
        # Recent high-severity events
        st.subheader("Recent High-Severity Events")
        high_severity_events = stats.get('high_severity_events', [])
        
        if high_severity_events:
            df = pd.DataFrame(high_severity_events)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp', ascending=False)
            
            st.dataframe(
                df[['timestamp', 'title', 'severity', 'username', 'ip_address']].head(10),
                use_container_width=True
            )
        else:
            st.info("No recent high-severity events")
        
        # Top users and IPs
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Users (30d)")
            top_users = stats.get('top_users', {})
            if top_users:
                df_users = pd.DataFrame(list(top_users.items()), columns=['User', 'Events'])
                st.dataframe(df_users, use_container_width=True)
            else:
                st.info("No user data available")
        
        with col2:
            st.subheader("Top IP Addresses (30d)")
            top_ips = stats.get('top_ip_addresses', {})
            if top_ips:
                df_ips = pd.DataFrame(list(top_ips.items()), columns=['IP Address', 'Events'])
                st.dataframe(df_ips, use_container_width=True)
            else:
                st.info("No IP address data available")
    
    def _render_event_search_tab(self):
        """Render event search interface."""
        st.subheader("🔍 Event Search & Filtering")
        
        # Search filters
        with st.expander("Search Filters", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Date range
                st.subheader("Date Range")
                date_range = st.selectbox(
                    "Quick Select",
                    ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Range"]
                )
                
                if date_range == "Custom Range":
                    start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=7))
                    end_date = st.date_input("End Date", datetime.now().date())
                    start_datetime = datetime.combine(start_date, datetime.min.time())
                    end_datetime = datetime.combine(end_date, datetime.max.time())
                else:
                    end_datetime = datetime.now()
                    if date_range == "Last Hour":
                        start_datetime = end_datetime - timedelta(hours=1)
                    elif date_range == "Last 24 Hours":
                        start_datetime = end_datetime - timedelta(days=1)
                    elif date_range == "Last 7 Days":
                        start_datetime = end_datetime - timedelta(days=7)
                    else:  # Last 30 Days
                        start_datetime = end_datetime - timedelta(days=30)
                
                # Event types
                st.subheader("Event Types")
                event_types = st.multiselect(
                    "Select Event Types",
                    [e.value for e in AuditEventType],
                    default=[]
                )
                
                # Categories
                categories = st.multiselect(
                    "Categories",
                    [c.value for c in AuditEventCategory],
                    default=[]
                )
            
            with col2:
                # Severities
                st.subheader("Severity Levels")
                severities = st.multiselect(
                    "Select Severities",
                    [s.value for s in AuditEventSeverity],
                    default=[]
                )
                
                # User filters
                st.subheader("User & IP Filters")
                user_id = st.text_input("User ID", "")
                ip_address = st.text_input("IP Address", "")
                
                # Text search
                st.subheader("Text Search")
                text_search = st.text_input("Search in title, description, message", "")
                
                # Limit
                limit = st.number_input("Max Results", min_value=10, max_value=10000, value=100)
        
        # Search button
        if st.button("🔍 Search Events", type="primary"):
            # Convert filter inputs
            event_type_enums = [AuditEventType(et) for et in event_types] if event_types else None
            category_enums = [AuditEventCategory(c) for c in categories] if categories else None
            severity_enums = [AuditEventSeverity(s) for s in severities] if severities else None
            
            # Search events
            events = self.audit_logger.search_events(
                start_date=start_datetime,
                end_date=end_datetime,
                event_types=event_type_enums,
                categories=category_enums,
                severities=severity_enums,
                user_id=user_id if user_id else None,
                ip_address=ip_address if ip_address else None,
                text_search=text_search if text_search else None,
                limit=limit
            )
            
            st.success(f"Found {len(events)} events")
            
            if events:
                # Create DataFrame for display
                event_data = []
                for event in events:
                    event_data.append({
                        'Timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'Event Type': event.event_type.value,
                        'Category': event.category.value,
                        'Severity': event.severity.value,
                        'Title': event.title,
                        'User': event.context.username or event.context.user_id or 'N/A',
                        'IP Address': event.context.ip_address or 'N/A',
                        'Resource': event.resource or 'N/A',
                        'Status': 'Success' if event.is_successful() else 'Failed',
                        'Event ID': event.event_id
                    })
                
                df = pd.DataFrame(event_data)
                
                # Display results
                st.dataframe(df, use_container_width=True)
                
                # Export options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📄 Export CSV"):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name=f"audit_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                with col2:
                    if st.button("📋 Export JSON"):
                        json_data = self.audit_logger.export_events(
                            start_date=start_datetime,
                            end_date=end_datetime,
                            format='json',
                            event_types=event_type_enums,
                            categories=category_enums,
                            severities=severity_enums,
                            user_id=user_id if user_id else None,
                            ip_address=ip_address if ip_address else None,
                            text_search=text_search if text_search else None
                        )
                        st.download_button(
                            label="Download JSON",
                            data=json_data,
                            file_name=f"audit_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                
                with col3:
                    # Event details modal
                    selected_event_id = st.selectbox(
                        "View Event Details",
                        ["Select an event..."] + [event.event_id for event in events[:20]]
                    )
                    
                    if selected_event_id != "Select an event...":
                        event = self.audit_logger.get_event_by_id(selected_event_id)
                        if event:
                            with st.expander(f"Event Details: {event.title}", expanded=True):
                                self._render_event_details(event)
            
            else:
                st.info("No events found matching the search criteria")
    
    def _render_event_details(self, event: AuditEvent):
        """Render detailed event information."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Basic Information")
            st.text(f"Event ID: {event.event_id}")
            st.text(f"Type: {event.event_type.value}")
            st.text(f"Category: {event.category.value}")
            st.text(f"Severity: {event.severity.value}")
            st.text(f"Timestamp: {event.timestamp}")
            st.text(f"Duration: {event.get_duration_seconds()}s" if event.duration_ms else "Duration: N/A")
            
            st.subheader("Event Details")
            st.text(f"Title: {event.title}")
            if event.description:
                st.text(f"Description: {event.description}")
            if event.message:
                st.text(f"Message: {event.message}")
        
        with col2:
            st.subheader("Context Information")
            if event.context.user_id:
                st.text(f"User ID: {event.context.user_id}")
            if event.context.username:
                st.text(f"Username: {event.context.username}")
            if event.context.ip_address:
                st.text(f"IP Address: {event.context.ip_address}")
            if event.context.session_id:
                st.text(f"Session ID: {event.context.session_id}")
            
            st.subheader("Operation Details")
            if event.operation:
                st.text(f"Operation: {event.operation}")
            if event.resource:
                st.text(f"Resource: {event.resource}")
            if event.method:
                st.text(f"Method: {event.method}")
            if event.status_code:
                st.text(f"Status Code: {event.status_code}")
        
        # Additional details
        if event.tags:
            st.subheader("Tags")
            st.write(", ".join(event.tags))
        
        if event.metadata:
            st.subheader("Metadata")
            st.json(event.metadata)
        
        if event.changes:
            st.subheader("Changes")
            st.json(event.changes)
    
    def _render_analytics_tab(self):
        """Render analytics dashboard."""
        st.subheader("📈 Audit Analytics")
        
        # Get analytics summary
        summary = self.audit_analyzer.get_analytics_summary()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events (30d)", f"{summary.get('total_events_30d', 0):,}")
        
        with col2:
            st.metric("High Severity", summary.get('high_severity_events', 0))
        
        with col3:
            st.metric("Critical Events", summary.get('critical_events', 0))
        
        with col4:
            compliance_score = summary.get('latest_compliance_score', 0.0)
            st.metric("Compliance Score", f"{compliance_score:.1%}")
        
        st.divider()
        
        # Trends analysis
        st.subheader("📊 Trends Analysis")
        trends = summary.get('trends', [])
        
        if trends:
            trends_df = pd.DataFrame(trends)
            
            # Filter trends with direction
            directional_trends = trends_df[trends_df['trend_direction'] != 'stable']
            
            if not directional_trends.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Increasing Trends")
                    increasing = directional_trends[directional_trends['trend_direction'] == 'increasing']
                    if not increasing.empty:
                        for _, trend in increasing.iterrows():
                            st.write(f"📈 {trend['category']}.{trend['metric']}: {trend['confidence']:.1%} confidence")
                    else:
                        st.info("No increasing trends detected")
                
                with col2:
                    st.subheader("Decreasing Trends")
                    decreasing = directional_trends[directional_trends['trend_direction'] == 'decreasing']
                    if not decreasing.empty:
                        for _, trend in decreasing.iterrows():
                            st.write(f"📉 {trend['category']}.{trend['metric']}: {trend['confidence']:.1%} confidence")
                    else:
                        st.info("No decreasing trends detected")
            else:
                st.info("All trends appear stable")
        else:
            st.info("No trend data available")
        
        st.divider()
        
        # Patterns analysis
        st.subheader("🔍 Detected Patterns")
        patterns = summary.get('patterns', [])
        
        if patterns:
            for pattern in patterns:
                severity_color = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢',
                    'info': '🔵'
                }.get(pattern['severity'], '⚪')
                
                with st.expander(f"{severity_color} {pattern['description']} (Risk: {pattern['risk_score']:.1%})"):
                    st.write(f"**Pattern Type:** {pattern['pattern_type']}")
                    st.write(f"**Frequency:** {pattern['frequency']} occurrences")
                    st.write(f"**Severity:** {pattern['severity']}")
                    st.write(f"**Risk Score:** {pattern['risk_score']:.1%}")
        else:
            st.info("No significant patterns detected")
    
    def _render_anomalies_tab(self):
        """Render anomalies detection dashboard."""
        st.subheader("🚨 Anomaly Detection")
        
        # Time range selector
        col1, col2 = st.columns([1, 3])
        
        with col1:
            hours = st.selectbox("Detection Period", [1, 6, 12, 24, 48, 72], index=3)
        
        with col2:
            if st.button("🔍 Detect Anomalies", type="primary"):
                anomalies = self.audit_analyzer.detect_anomalies(hours=hours)
                
                if anomalies:
                    st.success(f"Detected {len(anomalies)} anomalies in the last {hours} hours")
                    
                    for anomaly in anomalies:
                        severity_color = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡',
                            'low': '🟢',
                            'info': '🔵'
                        }.get(anomaly.severity.value, '⚪')
                        
                        with st.expander(f"{severity_color} {anomaly.description} (Confidence: {anomaly.confidence:.0%})"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Type:** {anomaly.anomaly_type}")
                                st.write(f"**Severity:** {anomaly.severity.value}")
                                st.write(f"**Detected:** {anomaly.detected_at}")
                                st.write(f"**Confidence:** {anomaly.confidence:.1%}")
                            
                            with col2:
                                if anomaly.threshold_exceeded:
                                    st.write(f"**Threshold Exceeded:** {anomaly.threshold_exceeded}")
                                if anomaly.metrics:
                                    st.write("**Metrics:**")
                                    for key, value in anomaly.metrics.items():
                                        st.write(f"  - {key}: {value}")
                            
                            if anomaly.event_ids:
                                st.write(f"**Related Events:** {len(anomaly.event_ids)} events")
                                if st.button(f"View Events", key=f"view_{anomaly.anomaly_type}"):
                                    # This would trigger event search for these IDs
                                    st.info("Event viewing functionality would be integrated here")
                else:
                    st.success(f"No anomalies detected in the last {hours} hours - system operating normally")
        
        st.divider()
        
        # Anomaly configuration
        st.subheader("⚙️ Anomaly Detection Settings")
        
        with st.expander("Configure Thresholds"):
            analyzer = self.audit_analyzer
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.number_input(
                    "High Frequency User (events/hour)",
                    value=analyzer.anomaly_thresholds['high_frequency_user'],
                    key="threshold_high_freq_user"
                )
                
                st.number_input(
                    "Failed Login Attempts (per hour)",
                    value=analyzer.anomaly_thresholds['failed_login_attempts'],
                    key="threshold_failed_logins"
                )
            
            with col2:
                st.number_input(
                    "Data Access Spike (events/hour)",
                    value=analyzer.anomaly_thresholds['data_access_spike'],
                    key="threshold_data_access"
                )
                
                st.number_input(
                    "Unusual IP Activity (events/hour)",
                    value=analyzer.anomaly_thresholds['unusual_ip_activity'],
                    key="threshold_ip_activity"
                )
            
            if st.button("💾 Update Thresholds"):
                # Update thresholds
                analyzer.anomaly_thresholds.update({
                    'high_frequency_user': st.session_state.get('threshold_high_freq_user', 100),
                    'failed_login_attempts': st.session_state.get('threshold_failed_logins', 5),
                    'data_access_spike': st.session_state.get('threshold_data_access', 50),
                    'unusual_ip_activity': st.session_state.get('threshold_ip_activity', 20)
                })
                st.success("Thresholds updated successfully!")
    
    def _render_compliance_tab(self):
        """Render compliance reporting dashboard."""
        st.subheader("📋 Compliance Reports")
        
        # Generate new report
        with st.expander("Generate New Report", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=30))
            
            with col2:
                end_date = st.date_input("End Date", datetime.now().date())
            
            with col3:
                if st.button("📊 Generate Report", type="primary"):
                    start_datetime = datetime.combine(start_date, datetime.min.time())
                    end_datetime = datetime.combine(end_date, datetime.max.time())
                    
                    with st.spinner("Generating compliance report..."):
                        report = self.audit_analyzer.generate_compliance_report(start_datetime, end_datetime)
                    
                    st.success("Compliance report generated successfully!")
                    
                    # Display report
                    self._render_compliance_report(report)
        
        st.divider()
        
        # Recent reports
        st.subheader("📈 Recent Reports")
        reports = self.audit_analyzer.get_compliance_reports(limit=5)
        
        if reports:
            for report in reports:
                with st.expander(f"Report {report.report_id[:8]} - {report.generated_at.strftime('%Y-%m-%d %H:%M')} (Score: {report.compliance_score:.1%})"):
                    self._render_compliance_report(report)
        else:
            st.info("No compliance reports available. Generate your first report above.")
    
    def _render_compliance_report(self, report):
        """Render a compliance report."""
        # Header metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", f"{report.total_events:,}")
        
        with col2:
            st.metric("Security Events", report.security_events)
        
        with col3:
            st.metric("Failed Operations", report.failed_operations)
        
        with col4:
            score_color = "normal"
            if report.compliance_score < 0.7:
                score_color = "inverse"
            elif report.compliance_score < 0.9:
                score_color = "off"
            
            st.metric("Compliance Score", f"{report.compliance_score:.1%}")
        
        # Period info
        st.text(f"Report Period: {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if report.events_by_category:
                fig = px.pie(
                    values=list(report.events_by_category.values()),
                    names=list(report.events_by_category.keys()),
                    title="Events by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if report.events_by_severity:
                color_map = {
                    'info': '#17becf',
                    'low': '#2ca02c',
                    'medium': '#ff7f0e',
                    'high': '#d62728',
                    'critical': '#8c0303'
                }
                fig = px.bar(
                    x=list(report.events_by_severity.keys()),
                    y=list(report.events_by_severity.values()),
                    title="Events by Severity",
                    color=list(report.events_by_severity.keys()),
                    color_discrete_map=color_map
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        if report.recommendations:
            st.subheader("📋 Recommendations")
            for i, rec in enumerate(report.recommendations, 1):
                st.write(f"{i}. {rec}")
        else:
            st.success("✅ No specific recommendations - system appears compliant")
    
    def _render_configuration_tab(self):
        """Render audit configuration interface."""
        st.subheader("⚙️ Audit Configuration")
        
        # Retention policies
        with st.expander("📅 Retention Policies", expanded=True):
            st.write("Configure how long different types of audit events are retained:")
            
            retention_policies = self.audit_logger.retention_policies.copy()
            
            for category, days in retention_policies.items():
                retention_policies[category] = st.number_input(
                    f"{category.value} Events (days)",
                    min_value=1,
                    max_value=3650,
                    value=days,
                    key=f"retention_{category.value}"
                )
            
            if st.button("💾 Update Retention Policies"):
                self.audit_logger.retention_policies.update(retention_policies)
                st.success("Retention policies updated!")
        
        st.divider()
        
        # Event listeners
        with st.expander("📡 Event Listeners"):
            st.write("Manage audit event listeners and integrations:")
            
            listener_count = len(self.audit_logger._event_listeners)
            st.text(f"Active Listeners: {listener_count}")
            
            if st.button("🧹 Clear Event Listeners"):
                self.audit_logger._event_listeners.clear()
                st.success("Event listeners cleared!")
        
        st.divider()
        
        # Database management
        with st.expander("🗄️ Database Management"):
            st.write("Manage audit database and storage:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🧹 Cleanup Old Events", type="secondary"):
                    deleted_count = self.audit_logger.cleanup_old_events()
                    st.success(f"Cleaned up {deleted_count} old events")
            
            with col2:
                if st.button("📊 Database Statistics"):
                    # Get database size and statistics
                    import os
                    db_size = os.path.getsize(self.audit_logger.db_path)
                    st.text(f"Database Size: {db_size / 1024 / 1024:.2f} MB")
                    st.text(f"Database Path: {self.audit_logger.db_path}")
        
        st.divider()
        
        # Integration settings
        with st.expander("🔗 Integration Settings"):
            st.write("Configure integrations with other systems:")
            
            # Change tracker integration
            st.checkbox("Enable Change Tracker Integration", value=True, disabled=True)
            st.text("Automatically track high-severity audit events in change history")
            
            # Export settings
            st.subheader("Export Settings")
            export_formats = st.multiselect(
                "Enabled Export Formats",
                ["JSON", "CSV", "PDF", "Excel", "HTML"],
                default=["JSON", "CSV"]
            )
            
            if st.button("💾 Update Integration Settings"):
                st.success("Integration settings updated!")
    
    def _render_test_events_tab(self):
        """Render test events interface."""
        st.subheader("🧪 Test Audit Events")
        st.write("Generate test events to verify audit logging functionality")
        
        # Quick test events
        with st.expander("⚡ Quick Test Events", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✅ Test Success Event"):
                    event = AuditEvent(
                        event_type=AuditEventType.USER_ACTION,
                        category=AuditEventCategory.USER,
                        severity=AuditEventSeverity.INFO,
                        title="Test Success Event",
                        description="Generated for testing purposes",
                        operation="test"
                    )
                    event.context.user_id = "test_user"
                    event.context.ip_address = "127.0.0.1"
                    self.audit_logger.log_event(event)
                    st.success("Success event logged!")
            
            with col2:
                if st.button("❌ Test Error Event"):
                    event = AuditEvent(
                        event_type=AuditEventType.SYSTEM_CONFIG_CHANGE,
                        category=AuditEventCategory.SYSTEM,
                        severity=AuditEventSeverity.HIGH,
                        title="Test Error Event",
                        description="Generated error for testing",
                        operation="test_error"
                    )
                    event.set_error("TEST_ERROR", "This is a test error message", 500)
                    self.audit_logger.log_event(event)
                    st.success("Error event logged!")
            
            with col3:
                if st.button("🔒 Test Security Event"):
                    event = AuditEvent(
                        event_type=AuditEventType.SECURITY_LOGIN_FAIL,
                        category=AuditEventCategory.SECURITY,
                        severity=AuditEventSeverity.MEDIUM,
                        title="Test Security Event",
                        description="Failed login attempt (test)",
                        operation="login"
                    )
                    event.context.username = "test_user"
                    event.context.ip_address = "192.168.1.100"
                    self.audit_logger.log_event(event)
                    st.success("Security event logged!")
            
            with col4:
                if st.button("📊 Test Data Event"):
                    event = AuditEvent(
                        event_type=AuditEventType.DATA_EXPORT,
                        category=AuditEventCategory.DATA,
                        severity=AuditEventSeverity.MEDIUM,
                        title="Test Data Export",
                        description="Data export test event",
                        operation="export",
                        resource="test_dataset"
                    )
                    event.context.user_id = "data_analyst"
                    self.audit_logger.log_event(event)
                    st.success("Data event logged!")
        
        st.divider()
        
        # Custom event creator
        with st.expander("🛠️ Custom Event Creator"):
            col1, col2 = st.columns(2)
            
            with col1:
                event_type = st.selectbox("Event Type", [e.value for e in AuditEventType])
                category = st.selectbox("Category", [c.value for c in AuditEventCategory])
                severity = st.selectbox("Severity", [s.value for s in AuditEventSeverity])
                title = st.text_input("Title", "Custom Test Event")
                description = st.text_area("Description", "Custom event for testing")
            
            with col2:
                operation = st.text_input("Operation", "custom_test")
                resource = st.text_input("Resource", "")
                user_id = st.text_input("User ID", "test_user")
                ip_address = st.text_input("IP Address", "127.0.0.1")
                
                # Tags
                tags_input = st.text_input("Tags (comma-separated)", "test,custom")
                tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
            
            if st.button("📝 Create Custom Event", type="primary"):
                event = AuditEvent(
                    event_type=AuditEventType(event_type),
                    category=AuditEventCategory(category),
                    severity=AuditEventSeverity(severity),
                    title=title,
                    description=description,
                    operation=operation,
                    resource=resource if resource else None,
                    tags=tags
                )
                
                event.context.user_id = user_id
                event.context.ip_address = ip_address
                
                self.audit_logger.log_event(event)
                st.success(f"Custom event '{title}' logged successfully!")
        
        st.divider()
        
        # Template events
        with st.expander("📋 Template Events"):
            st.write("Generate events from predefined templates:")
            
            templates = [
                "user_login", "user_login_fail", "api_key_create", 
                "data_export", "config_change", "permission_change"
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                template_name = st.selectbox("Select Template", templates)
            
            with col2:
                template_user_id = st.text_input("Template User ID", "template_user")
            
            if st.button("🚀 Generate from Template"):
                try:
                    self.audit_logger.log_from_template(
                        template_name,
                        user_id=template_user_id,
                        ip_address="127.0.0.1"
                    )
                    st.success(f"Event generated from template '{template_name}'!")
                except ValueError as e:
                    st.error(f"Template error: {e}")
        
        st.divider()
        
        # Bulk event generation
        with st.expander("📈 Bulk Event Generation"):
            st.warning("⚠️ Use carefully - this will generate multiple events")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                bulk_count = st.number_input("Number of Events", min_value=1, max_value=100, value=10)
            
            with col2:
                bulk_type = st.selectbox("Bulk Event Type", [e.value for e in AuditEventType])
            
            with col3:
                bulk_interval = st.number_input("Interval (seconds)", min_value=0.1, max_value=60.0, value=1.0)
            
            if st.button("⚡ Generate Bulk Events"):
                import time
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i in range(bulk_count):
                    event = AuditEvent(
                        event_type=AuditEventType(bulk_type),
                        category=AuditEventCategory.USER,
                        severity=AuditEventSeverity.INFO,
                        title=f"Bulk Test Event {i+1}",
                        description=f"Bulk generated event {i+1} of {bulk_count}",
                        operation="bulk_test"
                    )
                    event.context.user_id = f"bulk_user_{i+1}"
                    event.context.ip_address = "127.0.0.1"
                    
                    self.audit_logger.log_event(event)
                    
                    progress = (i + 1) / bulk_count
                    progress_bar.progress(progress)
                    status_text.text(f"Generated {i+1}/{bulk_count} events...")
                    
                    if i < bulk_count - 1:  # Don't sleep after the last event
                        time.sleep(bulk_interval)
                
                st.success(f"Successfully generated {bulk_count} bulk events!")