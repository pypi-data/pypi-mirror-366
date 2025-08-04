"""
Connection monitoring UI component.

This module provides the UI for monitoring all system connections
including their health, metrics, and configuration.
"""

import streamlit as st
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json

from ..connections import (
    get_connection_monitor, ConnectionMonitor,
    Connection, ConnectionType, ConnectionStatus, ConnectionHealth,
    ConnectionEvent, ConnectionCheck
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class ConnectionMonitorUI:
    """UI component for connection monitoring."""
    
    def __init__(self):
        """Initialize connection monitor UI."""
        self.monitor = get_connection_monitor()
        self.change_tracker = get_change_tracker()
        
        # Initialize session state
        if 'connection_filter' not in st.session_state:
            st.session_state.connection_filter = {
                'type': None,
                'status': None,
                'health': None,
                'group': None
            }
        
        if 'selected_connection' not in st.session_state:
            st.session_state.selected_connection = None
    
    def render(self):
        """Render the connection monitor UI."""
        st.markdown("## 🔌 Connection Monitor")
        
        # Start monitor if not running
        if not self.monitor._is_running:
            asyncio.run(self.monitor.start())
        
        # Create tabs
        tabs = st.tabs([
            "📊 Overview",
            "🔍 Connection Details",
            "📈 Metrics & Analytics",
            "🚨 Alerts & Events",
            "⚙️ Configuration"
        ])
        
        with tabs[0]:
            self._render_overview()
        
        with tabs[1]:
            self._render_connection_details()
        
        with tabs[2]:
            self._render_metrics()
        
        with tabs[3]:
            self._render_alerts_events()
        
        with tabs[4]:
            self._render_configuration()
    
    def _render_overview(self):
        """Render connections overview."""
        st.markdown("### Connections Overview")
        
        # Get statistics
        stats = self.monitor.get_statistics()
        health_summary = stats['health_summary']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Connections",
                stats['connections']['total'],
                delta=f"{stats['connections']['active']} active"
            )
        
        with col2:
            success_rate = stats['checks']['success_rate']
            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%",
                delta=f"{stats['checks']['total']} checks"
            )
        
        with col3:
            healthy_count = health_summary.get('healthy', 0)
            total = stats['connections']['total']
            health_percent = (healthy_count / max(total, 1)) * 100
            st.metric(
                "Health Score",
                f"{health_percent:.0f}%",
                delta=f"{healthy_count} healthy"
            )
        
        with col4:
            critical_count = health_summary.get('critical', 0)
            st.metric(
                "Critical Issues",
                critical_count,
                delta="Immediate attention" if critical_count > 0 else "All good",
                delta_color="inverse"
            )
        
        # Health distribution chart
        st.markdown("#### Health Distribution")
        
        health_data = pd.DataFrame([
            {'Health': k.title(), 'Count': v} 
            for k, v in health_summary.items() if v > 0
        ])
        
        if not health_data.empty:
            fig = px.pie(
                health_data,
                values='Count',
                names='Health',
                color_discrete_map={
                    'Healthy': '#10B981',
                    'Degraded': '#F59E0B',
                    'Unhealthy': '#EF4444',
                    'Critical': '#991B1B',
                    'Unknown': '#6B7280'
                }
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No connections configured")
        
        # Connection list with filters
        st.markdown("#### Connections")
        
        # Filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            conn_types = [None] + [t.value for t in ConnectionType]
            selected_type = st.selectbox(
                "Filter by Type",
                conn_types,
                format_func=lambda x: "All Types" if x is None else x.replace('_', ' ').title()
            )
            st.session_state.connection_filter['type'] = selected_type
        
        with col2:
            statuses = [None] + [s.value for s in ConnectionStatus]
            selected_status = st.selectbox(
                "Filter by Status",
                statuses,
                format_func=lambda x: "All Statuses" if x is None else x.title()
            )
            st.session_state.connection_filter['status'] = selected_status
        
        with col3:
            healths = [None] + [h.value for h in ConnectionHealth]
            selected_health = st.selectbox(
                "Filter by Health",
                healths,
                format_func=lambda x: "All Health Levels" if x is None else x.title()
            )
            st.session_state.connection_filter['health'] = selected_health
        
        with col4:
            # Get all groups
            all_groups = set()
            for group_set in self.monitor._connection_groups.values():
                all_groups.update(group_set)
            
            groups = [None] + sorted(list(all_groups))
            selected_group = st.selectbox(
                "Filter by Group",
                groups,
                format_func=lambda x: "All Groups" if x is None else x
            )
            st.session_state.connection_filter['group'] = selected_group
        
        # Get filtered connections
        connections = self._get_filtered_connections()
        
        if connections:
            # Create connection data for display
            conn_data = []
            for conn in connections:
                status_icon = self._get_status_icon(conn.status)
                health_icon = self._get_health_icon(conn.health)
                
                conn_data.append({
                    'Name': conn.name,
                    'Type': conn.type.value.replace('_', ' ').title(),
                    'Status': f"{status_icon} {conn.status.value.title()}",
                    'Health': f"{health_icon} {conn.health.value.title()}",
                    'Uptime': f"{conn.get_uptime_percentage():.1f}%",
                    'Last Check': conn.last_check_time.strftime('%H:%M:%S') if conn.last_check_time else 'Never',
                    'ID': conn.id
                })
            
            # Display as dataframe
            df = pd.DataFrame(conn_data)
            
            # Make it selectable
            selected = st.dataframe(
                df.drop(columns=['ID']),
                use_container_width=True,
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun"
            )
            
            # Handle selection
            if selected and selected.selection.rows:
                row_idx = selected.selection.rows[0]
                st.session_state.selected_connection = df.iloc[row_idx]['ID']
        else:
            st.info("No connections match the selected filters")
    
    def _render_connection_details(self):
        """Render detailed view of selected connection."""
        st.markdown("### Connection Details")
        
        # Connection selector
        connections = self.monitor.get_all_connections()
        if not connections:
            st.info("No connections configured")
            return
        
        # Create connection options
        conn_options = {conn.id: f"{conn.name} ({conn.type.value})" for conn in connections}
        
        selected_id = st.selectbox(
            "Select Connection",
            list(conn_options.keys()),
            format_func=lambda x: conn_options[x],
            index=list(conn_options.keys()).index(st.session_state.selected_connection) 
                  if st.session_state.selected_connection in conn_options else 0
        )
        
        connection = self.monitor.get_connection(selected_id)
        if not connection:
            return
        
        # Connection info
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Connection Information")
            
            # Basic info
            info_data = {
                'Name': connection.name,
                'Type': connection.type.value.replace('_', ' ').title(),
                'Status': f"{self._get_status_icon(connection.status)} {connection.status.value.title()}",
                'Health': f"{self._get_health_icon(connection.health)} {connection.health.value.title()}",
                'Host': connection.host or 'N/A',
                'Port': connection.port or 'N/A',
                'URL': connection.url or 'N/A',
                'Protocol': connection.protocol or 'N/A'
            }
            
            for key, value in info_data.items():
                st.markdown(f"**{key}:** {value}")
        
        with col2:
            st.markdown("#### Quick Actions")
            
            if st.button("🔄 Check Now", use_container_width=True):
                with st.spinner("Checking connection..."):
                    check = asyncio.run(self.monitor.check_connection(selected_id))
                    if check:
                        if check.success:
                            st.success(f"Connection successful ({check.duration_ms:.0f}ms)")
                        else:
                            st.error(f"Connection failed: {check.error}")
                    st.rerun()
            
            if st.button("📊 View Metrics", use_container_width=True):
                st.session_state.show_metrics = True
            
            if st.button("📋 View Events", use_container_width=True):
                st.session_state.show_events = True
            
            if connection.alert_on_failure:
                if st.button("🔕 Disable Alerts", use_container_width=True):
                    connection.alert_on_failure = False
                    st.success("Alerts disabled")
                    st.rerun()
            else:
                if st.button("🔔 Enable Alerts", use_container_width=True):
                    connection.alert_on_failure = True
                    st.success("Alerts enabled")
                    st.rerun()
        
        # Metrics summary
        st.markdown("#### Performance Metrics")
        
        metrics = connection.metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Latency", f"{metrics.latency_ms:.0f}ms")
        
        with col2:
            st.metric("Avg Response", f"{metrics.avg_response_time_ms:.0f}ms")
        
        with col3:
            st.metric("Error Rate", f"{metrics.error_rate * 100:.1f}%")
        
        with col4:
            uptime_hours = metrics.uptime_seconds / 3600 if metrics.uptime_seconds else 0
            st.metric("Uptime", f"{uptime_hours:.1f}h")
        
        # Check history
        st.markdown("#### Recent Checks")
        
        check_history = self.monitor.get_check_history(selected_id, limit=20)
        if check_history:
            # Create chart data
            chart_data = []
            for check in check_history:
                chart_data.append({
                    'Time': check.timestamp,
                    'Duration': check.duration_ms if check.success else None,
                    'Success': check.success
                })
            
            df = pd.DataFrame(chart_data)
            
            # Response time chart
            fig = go.Figure()
            
            # Successful checks
            success_df = df[df['Success'] == True]
            if not success_df.empty:
                fig.add_trace(go.Scatter(
                    x=success_df['Time'],
                    y=success_df['Duration'],
                    mode='lines+markers',
                    name='Response Time',
                    line=dict(color='#10B981')
                ))
            
            # Failed checks
            failed_df = df[df['Success'] == False]
            if not failed_df.empty:
                for _, row in failed_df.iterrows():
                    fig.add_vline(
                        x=row['Time'],
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Failed"
                    )
            
            fig.update_layout(
                title="Check History",
                xaxis_title="Time",
                yaxis_title="Response Time (ms)",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No check history available")
        
        # Configuration details
        with st.expander("Configuration Details"):
            st.json({
                'check_interval': f"{connection.check_interval_seconds}s",
                'timeout': f"{connection.timeout_seconds}s",
                'retry_count': connection.retry_count,
                'retry_delay': f"{connection.retry_delay_seconds}s",
                'alert_threshold': connection.alert_threshold,
                'tags': connection.tags,
                'config': connection.config
            })
    
    def _render_metrics(self):
        """Render metrics and analytics."""
        st.markdown("### Metrics & Analytics")
        
        # Time range selector
        col1, col2 = st.columns([3, 1])
        
        with col1:
            time_range = st.select_slider(
                "Time Range",
                options=["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days"],
                value="Last 24 Hours"
            )
        
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Overall statistics
        stats = self.monitor.get_statistics()
        
        st.markdown("#### System Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Checks", f"{stats['checks']['total']:,}")
        
        with col2:
            st.metric("Success Rate", f"{stats['checks']['success_rate']:.1f}%")
        
        with col3:
            st.metric("Total Events", f"{stats['events']['total']:,}")
        
        with col4:
            uptime_hours = stats['runtime']['uptime_seconds'] / 3600 if stats['runtime']['uptime_seconds'] else 0
            st.metric("Monitor Uptime", f"{uptime_hours:.1f}h")
        
        # Connection type breakdown
        st.markdown("#### Connections by Type")
        
        connections = self.monitor.get_all_connections()
        type_counts = {}
        for conn in connections:
            conn_type = conn.type.value
            type_counts[conn_type] = type_counts.get(conn_type, 0) + 1
        
        if type_counts:
            fig = px.bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                labels={'x': 'Connection Type', 'y': 'Count'},
                title="Connection Distribution"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Health trends
        st.markdown("#### Health Trends")
        
        # Get recent events for health changes
        events = self.monitor.get_recent_events(limit=100)
        health_events = [e for e in events if e.event_type == 'health_change']
        
        if health_events:
            # Create timeline
            timeline_data = []
            for event in health_events:
                timeline_data.append({
                    'Time': event.timestamp,
                    'Connection': event.connection_name,
                    'Old Health': event.old_health.value if event.old_health else 'unknown',
                    'New Health': event.new_health.value if event.new_health else 'unknown'
                })
            
            df = pd.DataFrame(timeline_data)
            
            fig = px.scatter(
                df,
                x='Time',
                y='Connection',
                color='New Health',
                color_discrete_map={
                    'healthy': '#10B981',
                    'degraded': '#F59E0B',
                    'unhealthy': '#EF4444',
                    'critical': '#991B1B',
                    'unknown': '#6B7280'
                },
                title="Health Change Timeline"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No health change events recorded")
        
        # Performance metrics by connection
        st.markdown("#### Performance by Connection")
        
        perf_data = []
        for conn in connections:
            if conn.metrics.avg_response_time_ms > 0:
                perf_data.append({
                    'Connection': conn.name,
                    'Avg Response (ms)': conn.metrics.avg_response_time_ms,
                    'P95 Response (ms)': conn.metrics.p95_response_time_ms,
                    'Error Rate (%)': conn.metrics.error_rate * 100,
                    'Uptime (%)': conn.get_uptime_percentage()
                })
        
        if perf_data:
            df = pd.DataFrame(perf_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No performance data available")
    
    def _render_alerts_events(self):
        """Render alerts and events."""
        st.markdown("### Alerts & Events")
        
        # Alert summary
        connections = self.monitor.get_all_connections()
        alert_count = sum(1 for c in connections if c.alerted)
        critical_count = sum(1 for c in connections if c.health == ConnectionHealth.CRITICAL)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Alerts", alert_count, delta_color="inverse")
        
        with col2:
            st.metric("Critical Connections", critical_count, delta_color="inverse")
        
        with col3:
            recent_events = self.monitor.get_recent_events(limit=10)
            st.metric("Recent Events", len(recent_events))
        
        # Event filters
        st.markdown("#### Event History")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            event_type_filter = st.selectbox(
                "Event Type",
                ["All", "status_change", "health_change", "alert"],
                index=0
            )
        
        with col2:
            connection_filter = st.selectbox(
                "Connection",
                ["All"] + [c.name for c in connections],
                index=0
            )
        
        with col3:
            limit = st.number_input("Limit", min_value=10, max_value=500, value=50)
        
        # Get filtered events
        events = self.monitor.get_recent_events(limit=limit)
        
        # Apply filters
        if event_type_filter != "All":
            events = [e for e in events if e.event_type == event_type_filter]
        
        if connection_filter != "All":
            events = [e for e in events if e.connection_name == connection_filter]
        
        # Display events
        if events:
            for event in events:
                with st.expander(
                    f"{self._get_event_icon(event)} {event.connection_name} - "
                    f"{event.event_type.replace('_', ' ').title()} - "
                    f"{event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                ):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("**Event Details:**")
                        st.markdown(f"- Type: {event.event_type}")
                        st.markdown(f"- Connection: {event.connection_name}")
                        st.markdown(f"- Time: {event.timestamp}")
                        
                        if event.message:
                            st.markdown(f"- Message: {event.message}")
                        
                        if event.error:
                            st.markdown(f"- Error: {event.error}")
                    
                    with col2:
                        if event.old_status or event.new_status:
                            st.markdown("**Status Change:**")
                            st.markdown(f"- From: {event.old_status.value if event.old_status else 'N/A'}")
                            st.markdown(f"- To: {event.new_status.value if event.new_status else 'N/A'}")
                        
                        if event.old_health or event.new_health:
                            st.markdown("**Health Change:**")
                            st.markdown(f"- From: {event.old_health.value if event.old_health else 'N/A'}")
                            st.markdown(f"- To: {event.new_health.value if event.new_health else 'N/A'}")
                    
                    if event.details:
                        st.markdown("**Additional Details:**")
                        st.json(event.details)
        else:
            st.info("No events found matching the filters")
        
        # Alerted connections
        alerted_connections = [c for c in connections if c.alerted]
        if alerted_connections:
            st.markdown("#### ⚠️ Connections with Active Alerts")
            
            for conn in alerted_connections:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{conn.name}** - {conn.consecutive_failures} consecutive failures")
                        if conn.metrics.last_error:
                            st.caption(f"Last error: {conn.metrics.last_error}")
                    
                    with col2:
                        if st.button("Acknowledge", key=f"ack_{conn.id}"):
                            conn.alerted = False
                            st.success("Alert acknowledged")
                            st.rerun()
                    
                    with col3:
                        if st.button("Check Now", key=f"check_{conn.id}"):
                            with st.spinner("Checking..."):
                                asyncio.run(self.monitor.check_connection(conn.id))
                            st.rerun()
    
    def _render_configuration(self):
        """Render configuration management."""
        st.markdown("### Connection Configuration")
        
        # Add new connection
        st.markdown("#### Add New Connection")
        
        with st.form("add_connection"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Connection Name", placeholder="e.g., Main Database")
                conn_type = st.selectbox(
                    "Connection Type",
                    [t.value for t in ConnectionType],
                    format_func=lambda x: x.replace('_', ' ').title()
                )
                
                host = st.text_input("Host", placeholder="localhost")
                port = st.number_input("Port", min_value=1, max_value=65535, value=None)
            
            with col2:
                url = st.text_input("URL (optional)", placeholder="http://example.com")
                protocol = st.text_input("Protocol (optional)", placeholder="http")
                
                check_interval = st.number_input(
                    "Check Interval (seconds)",
                    min_value=10,
                    max_value=3600,
                    value=30
                )
                timeout = st.number_input(
                    "Timeout (seconds)",
                    min_value=1,
                    max_value=60,
                    value=10
                )
            
            # Tags
            tags = st.text_input(
                "Tags (comma-separated)",
                placeholder="production, critical"
            )
            
            # Alert settings
            col1, col2 = st.columns(2)
            
            with col1:
                alert_on_failure = st.checkbox("Alert on Failure", value=True)
            
            with col2:
                alert_threshold = st.number_input(
                    "Alert Threshold",
                    min_value=1,
                    max_value=10,
                    value=3,
                    help="Alert after N consecutive failures"
                )
            
            if st.form_submit_button("Add Connection", type="primary"):
                # Create connection
                from ..connections.models import Connection, ConnectionType as CT
                
                connection = Connection(
                    name=name,
                    type=CT(conn_type),
                    host=host if host else None,
                    port=port if port else None,
                    url=url if url else None,
                    protocol=protocol if protocol else None,
                    tags=[t.strip() for t in tags.split(',')] if tags else [],
                    check_interval_seconds=check_interval,
                    timeout_seconds=timeout,
                    alert_on_failure=alert_on_failure,
                    alert_threshold=alert_threshold
                )
                
                # Add connection
                self.monitor.add_connection(connection)
                
                # Save configuration
                asyncio.run(self.monitor.save_configuration())
                
                st.success(f"Added connection: {name}")
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.CREATE,
                    description=f"Added connection via UI: {name}",
                    details={'connection_type': conn_type}
                )
                
                st.rerun()
        
        # Existing connections
        st.markdown("#### Manage Connections")
        
        connections = self.monitor.get_all_connections()
        if connections:
            for conn in connections:
                with st.expander(f"{conn.name} ({conn.type.value})"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Status:** {conn.status.value}")
                        st.markdown(f"**Health:** {conn.health.value}")
                        st.markdown(f"**Check Interval:** {conn.check_interval_seconds}s")
                        st.markdown(f"**Uptime:** {conn.get_uptime_percentage():.1f}%")
                    
                    with col2:
                        if st.button("Edit", key=f"edit_{conn.id}"):
                            st.session_state[f"editing_{conn.id}"] = True
                            st.rerun()
                    
                    with col3:
                        if st.button("Remove", key=f"remove_{conn.id}"):
                            if self.monitor.remove_connection(conn.id):
                                asyncio.run(self.monitor.save_configuration())
                                st.success(f"Removed connection: {conn.name}")
                                
                                # Track change
                                self.change_tracker.track_change(
                                    category=ChangeCategory.CONFIGURATION,
                                    change_type=ChangeType.DELETE,
                                    description=f"Removed connection via UI: {conn.name}",
                                    details={'connection_id': conn.id}
                                )
                                
                                st.rerun()
                    
                    # Edit form
                    if st.session_state.get(f"editing_{conn.id}", False):
                        with st.form(f"edit_form_{conn.id}"):
                            st.markdown("**Edit Connection**")
                            
                            new_interval = st.number_input(
                                "Check Interval (seconds)",
                                min_value=10,
                                max_value=3600,
                                value=conn.check_interval_seconds
                            )
                            
                            new_timeout = st.number_input(
                                "Timeout (seconds)",
                                min_value=1,
                                max_value=60,
                                value=conn.timeout_seconds
                            )
                            
                            new_alert = st.checkbox(
                                "Alert on Failure",
                                value=conn.alert_on_failure
                            )
                            
                            new_threshold = st.number_input(
                                "Alert Threshold",
                                min_value=1,
                                max_value=10,
                                value=conn.alert_threshold
                            )
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.form_submit_button("Save"):
                                    conn.check_interval_seconds = new_interval
                                    conn.timeout_seconds = new_timeout
                                    conn.alert_on_failure = new_alert
                                    conn.alert_threshold = new_threshold
                                    
                                    asyncio.run(self.monitor.save_configuration())
                                    st.success("Configuration updated")
                                    st.session_state[f"editing_{conn.id}"] = False
                                    st.rerun()
                            
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state[f"editing_{conn.id}"] = False
                                    st.rerun()
        else:
            st.info("No connections configured")
        
        # Import/Export
        st.markdown("#### Import/Export Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export Configuration", use_container_width=True):
                # Get current configuration
                config = {
                    'connections': []
                }
                
                for conn in connections:
                    config['connections'].append({
                        'name': conn.name,
                        'type': conn.type.value,
                        'host': conn.host,
                        'port': conn.port,
                        'url': conn.url,
                        'protocol': conn.protocol,
                        'tags': conn.tags,
                        'check_interval_seconds': conn.check_interval_seconds,
                        'timeout_seconds': conn.timeout_seconds,
                        'alert_on_failure': conn.alert_on_failure,
                        'alert_threshold': conn.alert_threshold,
                        'config': conn.config
                    })
                
                st.download_button(
                    label="Download Configuration",
                    data=json.dumps(config, indent=2),
                    file_name=f"connections_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            uploaded_file = st.file_uploader(
                "Import Configuration",
                type=['json'],
                help="Upload a connections configuration file"
            )
            
            if uploaded_file:
                try:
                    config = json.loads(uploaded_file.read())
                    
                    # Import connections
                    imported = 0
                    for conn_config in config.get('connections', []):
                        try:
                            connection = self.monitor._create_connection_from_config(conn_config)
                            self.monitor.add_connection(connection)
                            imported += 1
                        except Exception as e:
                            st.error(f"Failed to import connection: {e}")
                    
                    if imported > 0:
                        asyncio.run(self.monitor.save_configuration())
                        st.success(f"Imported {imported} connections")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Failed to import configuration: {e}")
    
    def _get_filtered_connections(self) -> List[Connection]:
        """Get connections based on current filters."""
        connections = self.monitor.get_all_connections()
        
        # Apply type filter
        if st.session_state.connection_filter['type']:
            connections = [c for c in connections 
                          if c.type.value == st.session_state.connection_filter['type']]
        
        # Apply status filter
        if st.session_state.connection_filter['status']:
            connections = [c for c in connections 
                          if c.status.value == st.session_state.connection_filter['status']]
        
        # Apply health filter
        if st.session_state.connection_filter['health']:
            connections = [c for c in connections 
                          if c.health.value == st.session_state.connection_filter['health']]
        
        # Apply group filter
        if st.session_state.connection_filter['group']:
            group_connections = self.monitor.get_connections_by_group(
                st.session_state.connection_filter['group']
            )
            group_ids = {c.id for c in group_connections}
            connections = [c for c in connections if c.id in group_ids]
        
        return connections
    
    def _get_status_icon(self, status: ConnectionStatus) -> str:
        """Get icon for connection status."""
        icons = {
            ConnectionStatus.CONNECTED: "🟢",
            ConnectionStatus.DISCONNECTED: "🔴",
            ConnectionStatus.CONNECTING: "🟡",
            ConnectionStatus.RECONNECTING: "🟠",
            ConnectionStatus.ERROR: "❌",
            ConnectionStatus.TIMEOUT: "⏱️",
            ConnectionStatus.UNAUTHORIZED: "🔒",
            ConnectionStatus.MAINTENANCE: "🔧"
        }
        return icons.get(status, "❓")
    
    def _get_health_icon(self, health: ConnectionHealth) -> str:
        """Get icon for connection health."""
        icons = {
            ConnectionHealth.HEALTHY: "✅",
            ConnectionHealth.DEGRADED: "⚠️",
            ConnectionHealth.UNHEALTHY: "🚨",
            ConnectionHealth.CRITICAL: "💀",
            ConnectionHealth.UNKNOWN: "❓"
        }
        return icons.get(health, "❓")
    
    def _get_event_icon(self, event: ConnectionEvent) -> str:
        """Get icon for event type."""
        if event.event_type == "status_change":
            if event.new_status == ConnectionStatus.CONNECTED:
                return "✅"
            else:
                return "❌"
        elif event.event_type == "health_change":
            return self._get_health_icon(event.new_health) if event.new_health else "❓"
        elif event.event_type == "alert":
            return "🚨"
        else:
            return "ℹ️"


# Singleton instance
_connection_monitor_ui = None


def get_connection_monitor_ui() -> ConnectionMonitorUI:
    """Get singleton connection monitor UI instance."""
    global _connection_monitor_ui
    
    if _connection_monitor_ui is None:
        _connection_monitor_ui = ConnectionMonitorUI()
    
    return _connection_monitor_ui