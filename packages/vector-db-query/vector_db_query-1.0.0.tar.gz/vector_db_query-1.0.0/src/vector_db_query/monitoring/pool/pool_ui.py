"""
Connection pool visualization UI component.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import json
import numpy as np

from .pool_manager import get_pool_manager
from .models import (
    PoolType, ConnectionState, PoolHealth,
    ConnectionPool, PoolConnection, PoolMetrics,
    PoolEvent, PoolOptimization
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class ConnectionPoolUI:
    """
    Connection pool visualization and management UI.
    """
    
    def __init__(self):
        """Initialize connection pool UI."""
        self.pool_manager = get_pool_manager()
        self.change_tracker = get_change_tracker()
        
        # Initialize session state
        if 'pool_selected_pool' not in st.session_state:
            st.session_state.pool_selected_pool = None
        if 'pool_time_range' not in st.session_state:
            st.session_state.pool_time_range = 1
        if 'pool_auto_refresh' not in st.session_state:
            st.session_state.pool_auto_refresh = True
    
    def render(self):
        """Render the connection pool UI."""
        st.header("🔌 Connection Pool Visualization")
        
        # Start manager if not running
        if not hasattr(self.pool_manager, '_monitor_task') or self.pool_manager._monitor_task is None:
            asyncio.run(self.pool_manager.start())
        
        # Auto-refresh controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.session_state.pool_auto_refresh = st.checkbox(
                "Auto-refresh",
                value=st.session_state.pool_auto_refresh,
                key="pool_auto_refresh_check"
            )
        with col2:
            refresh_interval = st.number_input(
                "Interval (s)",
                min_value=5,
                max_value=60,
                value=10,
                key="pool_refresh_interval"
            )
        with col3:
            if st.button("🔄 Refresh Now", key="refresh_pools"):
                st.rerun()
        
        # Tabs
        tabs = st.tabs([
            "📊 Overview",
            "🔍 Pool Details",
            "📈 Performance",
            "⚡ Live Connections",
            "📋 Events",
            "💡 Optimizations",
            "🔧 Configuration"
        ])
        
        with tabs[0]:
            self._render_overview_tab()
        
        with tabs[1]:
            self._render_pool_details_tab()
        
        with tabs[2]:
            self._render_performance_tab()
        
        with tabs[3]:
            self._render_connections_tab()
        
        with tabs[4]:
            self._render_events_tab()
        
        with tabs[5]:
            self._render_optimizations_tab()
        
        with tabs[6]:
            self._render_configuration_tab()
        
        # Auto-refresh
        if st.session_state.pool_auto_refresh:
            st.empty()
            asyncio.run(asyncio.sleep(refresh_interval))
            st.rerun()
    
    def _render_overview_tab(self):
        """Render overview tab."""
        st.subheader("Connection Pool Overview")
        
        # Get all pools
        pools = self.pool_manager.get_all_pools()
        
        if not pools:
            st.info("No connection pools registered")
            return
        
        # Summary metrics
        stats = self.pool_manager.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Pools",
                stats['pools_managed'],
                help="Number of managed connection pools"
            )
        
        with col2:
            st.metric(
                "Total Connections",
                stats['total_connections'],
                delta=f"{stats['active_connections']} active",
                help="Total connections across all pools"
            )
        
        with col3:
            st.metric(
                "Total Requests",
                f"{stats['total_requests']:,}",
                help="Total requests handled"
            )
        
        with col4:
            pending_opts = len(self.pool_manager.get_optimizations(status="pending"))
            st.metric(
                "Pending Optimizations",
                pending_opts,
                delta=f"{pending_opts} pending" if pending_opts > 0 else None,
                delta_color="inverse",
                help="Optimization recommendations pending"
            )
        
        # Pool summary table
        st.markdown("### Pool Summary")
        
        pool_data = []
        for pool in pools:
            counts = pool.get_connection_counts()
            
            pool_data.append({
                "Name": pool.name,
                "Type": pool.pool_type.value,
                "Health": pool.health_status.value,
                "Connections": len(pool.connections),
                "Active": counts.get(ConnectionState.ACTIVE, 0),
                "Idle": counts.get(ConnectionState.IDLE, 0),
                "Errors": counts.get(ConnectionState.ERROR, 0),
                "Utilization %": f"{pool.calculate_utilization():.1f}",
                "Requests": pool.total_requests_handled,
                "Error Rate": f"{(pool.total_errors / max(pool.total_requests_handled, 1) * 100):.1f}%"
            })
        
        df = pd.DataFrame(pool_data)
        
        # Color code health status
        def color_health(val):
            colors = {
                "healthy": "background-color: #28a745",
                "warning": "background-color: #ffc107",
                "degraded": "background-color: #fd7e14",
                "critical": "background-color: #dc3545",
                "failed": "background-color: #6c757d"
            }
            return colors.get(val, "")
        
        styled_df = df.style.applymap(color_health, subset=['Health'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Pool health distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Health pie chart
            health_counts = {}
            for pool in pools:
                health = pool.health_status.value
                health_counts[health] = health_counts.get(health, 0) + 1
            
            fig = px.pie(
                values=list(health_counts.values()),
                names=list(health_counts.keys()),
                title="Pool Health Distribution",
                color_discrete_map={
                    "healthy": "#28a745",
                    "warning": "#ffc107",
                    "degraded": "#fd7e14",
                    "critical": "#dc3545",
                    "failed": "#6c757d"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pool type distribution
            type_counts = {}
            for pool in pools:
                ptype = pool.pool_type.value
                type_counts[ptype] = type_counts.get(ptype, 0) + 1
            
            fig = px.bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                title="Pools by Type",
                labels={'x': 'Pool Type', 'y': 'Count'},
                color=list(type_counts.values()),
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Scaling recommendations
        st.markdown("### Scaling Recommendations")
        
        scale_recommendations = []
        for pool in pools:
            recommendation = pool.needs_scaling()
            if recommendation != "maintain":
                scale_recommendations.append({
                    "Pool": pool.name,
                    "Current Size": len(pool.connections),
                    "Utilization": f"{pool.calculate_utilization():.1f}%",
                    "Recommendation": recommendation.replace("_", " ").title()
                })
        
        if scale_recommendations:
            st.dataframe(
                pd.DataFrame(scale_recommendations),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("All pools are properly sized")
    
    def _render_pool_details_tab(self):
        """Render pool details tab."""
        st.subheader("Pool Details")
        
        pools = self.pool_manager.get_all_pools()
        if not pools:
            st.info("No connection pools registered")
            return
        
        # Pool selector
        pool_names = {p.pool_id: p.name for p in pools}
        selected_pool_id = st.selectbox(
            "Select Pool",
            options=list(pool_names.keys()),
            format_func=lambda x: pool_names[x],
            key="pool_selector"
        )
        
        pool = self.pool_manager.get_pool(selected_pool_id)
        if not pool:
            return
        
        # Pool information
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Configuration")
            st.write(f"**Type**: {pool.pool_type.value}")
            st.write(f"**Min Size**: {pool.min_size}")
            st.write(f"**Max Size**: {pool.max_size}")
            st.write(f"**Target Size**: {pool.target_size}")
            st.write(f"**Current Size**: {len(pool.connections)}")
        
        with col2:
            st.markdown("#### Timeouts")
            st.write(f"**Connection Timeout**: {pool.connection_timeout_ms}ms")
            st.write(f"**Request Timeout**: {pool.request_timeout_ms}ms")
            st.write(f"**Max Idle**: {pool.max_idle_seconds}s")
            st.write(f"**Max Lifetime**: {pool.max_lifetime_seconds}s")
        
        with col3:
            st.markdown("#### Statistics")
            st.write(f"**Total Created**: {pool.total_connections_created}")
            st.write(f"**Total Destroyed**: {pool.total_connections_destroyed}")
            st.write(f"**Total Requests**: {pool.total_requests_handled:,}")
            st.write(f"**Total Errors**: {pool.total_errors}")
            st.write(f"**Error Rate**: {(pool.total_errors / max(pool.total_requests_handled, 1) * 100):.2f}%")
        
        # Connection state visualization
        st.markdown("### Connection States")
        
        counts = pool.get_connection_counts()
        
        # Create gauge chart for utilization
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pool.calculate_utilization(),
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Pool Utilization %"},
            delta={'reference': pool.target_size / pool.max_size * 100},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Connection state breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            state_data = []
            for state, count in counts.items():
                if count > 0:
                    state_data.append({
                        "State": state.value.title(),
                        "Count": count
                    })
            
            if state_data:
                fig = px.bar(
                    state_data,
                    x="State",
                    y="Count",
                    title="Connections by State",
                    color="Count",
                    color_continuous_scale="Viridis"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Connection efficiency
            connections = list(pool.connections.values())
            if connections:
                efficiency_data = []
                for conn in connections[:10]:  # Top 10
                    efficiency_data.append({
                        "Connection": conn.connection_id[:8] + "...",
                        "Efficiency": conn.calculate_efficiency(),
                        "Use Count": conn.use_count
                    })
                
                df = pd.DataFrame(efficiency_data)
                fig = px.bar(
                    df,
                    x="Connection",
                    y="Efficiency",
                    title="Connection Efficiency (Top 10)",
                    color="Use Count",
                    color_continuous_scale="Blues"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_performance_tab(self):
        """Render performance tab."""
        st.subheader("Pool Performance")
        
        # Time range selector
        time_range = st.selectbox(
            "Time Range",
            options=[1, 6, 12, 24],
            format_func=lambda x: f"Last {x} hours",
            index=0,
            key="perf_time_range"
        )
        
        pools = self.pool_manager.get_all_pools()
        if not pools:
            st.info("No connection pools registered")
            return
        
        # Pool selector
        pool_names = {p.pool_id: p.name for p in pools}
        selected_pool_id = st.selectbox(
            "Select Pool",
            options=list(pool_names.keys()),
            format_func=lambda x: pool_names[x],
            key="perf_pool_selector"
        )
        
        # Get metrics
        metrics = self.pool_manager.get_pool_metrics(selected_pool_id, hours=time_range)
        
        if not metrics:
            st.info("No performance data available for selected time range")
            return
        
        # Create time series data
        timestamps = [m.timestamp for m in metrics]
        
        # Utilization over time
        st.markdown("### Utilization Trend")
        
        utilization_data = [
            (m.active_connections / max(m.total_connections, 1)) * 100 
            for m in metrics
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=utilization_data,
            mode='lines',
            name='Utilization %',
            line=dict(color='blue', width=2)
        ))
        
        # Add target utilization line
        pool = self.pool_manager.get_pool(selected_pool_id)
        if pool:
            target_util = (pool.target_size / pool.max_size) * 100
            fig.add_hline(
                y=target_util,
                line_dash="dash",
                line_color="green",
                annotation_text="Target"
            )
        
        fig.update_layout(
            title="Pool Utilization Over Time",
            xaxis_title="Time",
            yaxis_title="Utilization %",
            yaxis_range=[0, 100],
            hovermode='x'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Connection counts over time
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=[m.total_connections for m in metrics],
                mode='lines',
                name='Total',
                line=dict(color='gray', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=[m.active_connections for m in metrics],
                mode='lines',
                name='Active',
                fill='tonexty',
                line=dict(color='green', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=[m.idle_connections for m in metrics],
                mode='lines',
                name='Idle',
                line=dict(color='blue', width=2)
            ))
            
            fig.update_layout(
                title="Connection States",
                xaxis_title="Time",
                yaxis_title="Count",
                hovermode='x'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Error rate
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=[m.error_rate * 100 for m in metrics],
                mode='lines',
                name='Error Rate',
                line=dict(color='red', width=2)
            ))
            
            fig.update_layout(
                title="Error Rate %",
                xaxis_title="Time",
                yaxis_title="Error Rate %",
                hovermode='x'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics
        st.markdown("### Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Request time
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=[m.avg_request_time_ms for m in metrics],
                mode='lines',
                name='Avg Request Time',
                line=dict(color='purple', width=2)
            ))
            
            fig.update_layout(
                title="Average Request Time",
                xaxis_title="Time",
                yaxis_title="Time (ms)",
                hovermode='x'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Requests per second
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=[m.requests_per_second for m in metrics],
                mode='lines',
                name='Requests/sec',
                line=dict(color='orange', width=2)
            ))
            
            fig.update_layout(
                title="Request Rate",
                xaxis_title="Time",
                yaxis_title="Requests/sec",
                hovermode='x'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Efficiency score
        st.markdown("### Efficiency Score")
        
        efficiency_scores = [m.calculate_efficiency_score() for m in metrics]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=efficiency_scores,
            mode='lines',
            fill='tozeroy',
            name='Efficiency Score',
            line=dict(color='green', width=2)
        ))
        
        # Add threshold lines
        fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Good")
        fig.add_hline(y=50, line_dash="dash", line_color="yellow", annotation_text="Fair")
        fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Poor")
        
        fig.update_layout(
            title="Pool Efficiency Score (0-100)",
            xaxis_title="Time",
            yaxis_title="Score",
            yaxis_range=[0, 100],
            hovermode='x'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_connections_tab(self):
        """Render live connections tab."""
        st.subheader("Live Connection Monitor")
        
        pools = self.pool_manager.get_all_pools()
        if not pools:
            st.info("No connection pools registered")
            return
        
        # Pool filter
        pool_names = ["All Pools"] + [p.name for p in pools]
        selected_pool_name = st.selectbox(
            "Filter by Pool",
            options=pool_names,
            key="conn_pool_filter"
        )
        
        # State filter
        state_filter = st.multiselect(
            "Filter by State",
            options=[s.value for s in ConnectionState],
            default=["active", "idle"],
            key="conn_state_filter"
        )
        
        # Collect all connections
        all_connections = []
        
        for pool in pools:
            if selected_pool_name != "All Pools" and pool.name != selected_pool_name:
                continue
            
            for conn in pool.connections.values():
                if conn.state.value in state_filter:
                    all_connections.append({
                        "pool": pool,
                        "connection": conn
                    })
        
        if not all_connections:
            st.info("No connections match the selected filters")
            return
        
        st.markdown(f"### {len(all_connections)} Connections")
        
        # Connection table
        conn_data = []
        for item in all_connections:
            pool = item["pool"]
            conn = item["connection"]
            
            # Calculate idle time
            if conn.last_used_at:
                idle_time = (datetime.now() - conn.last_used_at).total_seconds()
                idle_str = f"{idle_time:.0f}s"
            else:
                idle_str = "Never used"
            
            conn_data.append({
                "Pool": pool.name,
                "Connection ID": conn.connection_id[:8] + "...",
                "State": conn.state.value,
                "Use Count": conn.use_count,
                "Idle Time": idle_str,
                "Total Active Time": f"{conn.total_time_active_ms:.0f}ms",
                "Errors": conn.error_count,
                "Health Score": f"{conn.health_score:.0f}",
                "Efficiency": f"{conn.calculate_efficiency():.0f}%",
                "Remote": conn.remote_address or "N/A"
            })
        
        df = pd.DataFrame(conn_data)
        
        # Color code states
        def color_state(val):
            colors = {
                "idle": "background-color: #28a745",
                "active": "background-color: #17a2b8",
                "reserved": "background-color: #ffc107",
                "stale": "background-color: #fd7e14",
                "error": "background-color: #dc3545",
                "closing": "background-color: #6c757d",
                "closed": "background-color: #343a40"
            }
            return colors.get(val, "")
        
        styled_df = df.style.applymap(color_state, subset=['State'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Connection details
        if st.checkbox("Show Connection Details"):
            selected_conn_id = st.selectbox(
                "Select Connection",
                options=[c["connection"].connection_id for c in all_connections],
                format_func=lambda x: x[:8] + "...",
                key="conn_detail_selector"
            )
            
            # Find selected connection
            selected_item = next(
                (item for item in all_connections 
                 if item["connection"].connection_id == selected_conn_id),
                None
            )
            
            if selected_item:
                conn = selected_item["connection"]
                pool = selected_item["pool"]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Connection Information")
                    st.json({
                        "connection_id": conn.connection_id,
                        "pool_name": pool.name,
                        "state": conn.state.value,
                        "created_at": conn.created_at.isoformat(),
                        "last_used_at": conn.last_used_at.isoformat() if conn.last_used_at else None,
                        "protocol": conn.protocol,
                        "remote_address": conn.remote_address
                    })
                
                with col2:
                    st.markdown("#### Connection Metrics")
                    st.json({
                        "use_count": conn.use_count,
                        "total_active_time_ms": conn.total_time_active_ms,
                        "avg_request_time_ms": conn.total_time_active_ms / max(conn.use_count, 1),
                        "error_count": conn.error_count,
                        "last_error": conn.last_error,
                        "health_score": conn.health_score,
                        "efficiency": conn.calculate_efficiency(),
                        "is_stale": conn.is_stale(pool.max_idle_seconds)
                    })
                
                # Actions
                st.markdown("#### Actions")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔄 Reset Connection", key=f"reset_{conn.connection_id}"):
                        self.pool_manager.destroy_connection(conn.connection_id)
                        st.success("Connection reset")
                        st.rerun()
                
                with col2:
                    if st.button("🏥 Health Check", key=f"health_{conn.connection_id}"):
                        st.info("Health check initiated")
                
                with col3:
                    if st.button("📊 View History", key=f"history_{conn.connection_id}"):
                        st.info("Connection history not available in this version")
    
    def _render_events_tab(self):
        """Render events tab."""
        st.subheader("Pool Events")
        
        # Time range
        time_range = st.selectbox(
            "Time Range",
            options=[1, 6, 24, 48],
            format_func=lambda x: f"Last {x} hours",
            index=2,
            key="event_time_range"
        )
        
        # Get events
        events = self.pool_manager.get_pool_events(hours=time_range)
        
        if not events:
            st.info("No events in selected time range")
            return
        
        # Event type filter
        event_types = list(set(e.event_type for e in events))
        selected_types = st.multiselect(
            "Filter by Event Type",
            options=event_types,
            default=event_types,
            key="event_type_filter"
        )
        
        # Severity filter
        severities = list(set(e.severity for e in events))
        selected_severities = st.multiselect(
            "Filter by Severity",
            options=severities,
            default=severities,
            key="event_severity_filter"
        )
        
        # Apply filters
        filtered_events = [
            e for e in events
            if e.event_type in selected_types and e.severity in selected_severities
        ]
        
        st.markdown(f"### {len(filtered_events)} Events")
        
        # Event timeline
        if filtered_events:
            # Group events by hour
            event_counts = {}
            for event in filtered_events:
                hour = event.timestamp.replace(minute=0, second=0, microsecond=0)
                event_counts[hour] = event_counts.get(hour, 0) + 1
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(event_counts.keys()),
                y=list(event_counts.values()),
                mode='lines+markers',
                name='Events',
                line=dict(color='blue', width=2)
            ))
            
            fig.update_layout(
                title="Event Timeline",
                xaxis_title="Time",
                yaxis_title="Event Count",
                hovermode='x'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Event table
        event_data = []
        for event in filtered_events[:100]:  # Limit to 100 most recent
            event_data.append({
                "Time": event.timestamp.strftime("%H:%M:%S"),
                "Type": event.event_type,
                "Pool": self.pool_manager.get_pool(event.pool_id).name if self.pool_manager.get_pool(event.pool_id) else "Unknown",
                "Severity": event.severity,
                "Description": event.description,
                "Affected": event.affected_connections
            })
        
        df = pd.DataFrame(event_data)
        
        # Color code severity
        def color_severity(val):
            colors = {
                "info": "background-color: #17a2b8",
                "warning": "background-color: #ffc107",
                "error": "background-color: #dc3545",
                "critical": "background-color: #721c24"
            }
            return colors.get(val, "")
        
        styled_df = df.style.applymap(color_severity, subset=['Severity'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Event details
        if st.checkbox("Show Event Details"):
            selected_idx = st.number_input(
                "Event Index",
                min_value=0,
                max_value=len(filtered_events)-1,
                value=0,
                key="event_detail_idx"
            )
            
            if 0 <= selected_idx < len(filtered_events):
                event = filtered_events[selected_idx]
                
                st.json({
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat(),
                    "pool_id": event.pool_id,
                    "connection_id": event.connection_id,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "description": event.description,
                    "affected_connections": event.affected_connections,
                    "metadata": event.metadata
                })
    
    def _render_optimizations_tab(self):
        """Render optimizations tab."""
        st.subheader("Pool Optimizations")
        
        # Get all optimizations
        all_opts = self.pool_manager.get_optimizations()
        
        if not all_opts:
            st.success("No optimization recommendations at this time")
            return
        
        # Status filter
        status_filter = st.selectbox(
            "Filter by Status",
            options=["all", "pending", "implemented", "rejected"],
            index=0,
            key="opt_status_filter"
        )
        
        if status_filter != "all":
            filtered_opts = [o for o in all_opts if o.status == status_filter]
        else:
            filtered_opts = all_opts
        
        st.markdown(f"### {len(filtered_opts)} Recommendations")
        
        # Recommendation cards
        for opt in filtered_opts:
            pool = self.pool_manager.get_pool(opt.pool_id)
            pool_name = pool.name if pool else "Unknown Pool"
            
            # Priority emoji
            priority_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(opt.priority, "⚪")
            
            # Category icon
            category_icon = {
                "sizing": "📏",
                "performance": "⚡",
                "reliability": "🛡️",
                "cost": "💰"
            }.get(opt.category, "📋")
            
            with st.expander(
                f"{priority_emoji} {category_icon} {opt.title} - {pool_name}",
                expanded=(opt.status == "pending" and opt.priority in ["critical", "high"])
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description**: {opt.description}")
                    
                    # Suggested changes
                    if any([opt.suggested_min_size, opt.suggested_max_size, 
                           opt.suggested_target_size, opt.suggested_timeout_ms]):
                        st.markdown("**Suggested Changes**:")
                        if opt.suggested_min_size:
                            st.write(f"- Min Size: {pool.min_size} → {opt.suggested_min_size}")
                        if opt.suggested_max_size:
                            st.write(f"- Max Size: {pool.max_size} → {opt.suggested_max_size}")
                        if opt.suggested_target_size:
                            st.write(f"- Target Size: {pool.target_size} → {opt.suggested_target_size}")
                        if opt.suggested_timeout_ms:
                            st.write(f"- Timeout: {pool.connection_timeout_ms}ms → {opt.suggested_timeout_ms}ms")
                    
                    # Expected impact
                    st.markdown("**Expected Impact**:")
                    if opt.expected_improvement_percent > 0:
                        st.write(f"- Performance improvement: {opt.expected_improvement_percent:.0f}%")
                    if opt.expected_cost_change_percent != 0:
                        cost_change = opt.expected_cost_change_percent
                        if cost_change > 0:
                            st.write(f"- Cost increase: {cost_change:.0f}%")
                        else:
                            st.write(f"- Cost savings: {abs(cost_change):.0f}%")
                
                with col2:
                    st.markdown("**Metadata**")
                    st.write(f"**Category**: {opt.category}")
                    st.write(f"**Priority**: {opt.priority}")
                    st.write(f"**Effort**: {opt.implementation_effort}")
                    st.write(f"**Status**: {opt.status}")
                    st.write(f"**Created**: {opt.created_at.strftime('%Y-%m-%d %H:%M')}")
                    if opt.implemented_at:
                        st.write(f"**Implemented**: {opt.implemented_at.strftime('%Y-%m-%d %H:%M')}")
                
                # Actions for pending recommendations
                if opt.status == "pending":
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(
                            "✅ Apply",
                            key=f"apply_{opt.recommendation_id}",
                            type="primary"
                        ):
                            if self.pool_manager.apply_optimization(opt.recommendation_id):
                                st.success("Optimization applied successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to apply optimization")
                    
                    with col2:
                        if st.button(
                            "❌ Reject",
                            key=f"reject_{opt.recommendation_id}"
                        ):
                            opt.status = "rejected"
                            st.info("Recommendation rejected")
                            st.rerun()
                    
                    with col3:
                        if st.button(
                            "📋 Export",
                            key=f"export_{opt.recommendation_id}"
                        ):
                            st.json(opt.to_dict())
        
        # Summary statistics
        st.markdown("### Optimization Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            pending = len([o for o in all_opts if o.status == "pending"])
            st.metric("Pending", pending)
        
        with col2:
            implemented = len([o for o in all_opts if o.status == "implemented"])
            st.metric("Implemented", implemented)
        
        with col3:
            rejected = len([o for o in all_opts if o.status == "rejected"])
            st.metric("Rejected", rejected)
        
        with col4:
            critical = len([o for o in all_opts if o.priority == "critical" and o.status == "pending"])
            st.metric("Critical Pending", critical, delta=critical if critical > 0 else None, delta_color="inverse")
    
    def _render_configuration_tab(self):
        """Render configuration tab."""
        st.subheader("Pool Configuration")
        
        pools = self.pool_manager.get_all_pools()
        if not pools:
            st.info("No connection pools registered")
            return
        
        # Pool selector
        pool_names = {p.pool_id: p.name for p in pools}
        selected_pool_id = st.selectbox(
            "Select Pool to Configure",
            options=list(pool_names.keys()),
            format_func=lambda x: pool_names[x],
            key="config_pool_selector"
        )
        
        pool = self.pool_manager.get_pool(selected_pool_id)
        if not pool:
            return
        
        st.markdown(f"### Configuring: {pool.name}")
        
        # Configuration sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Pool Sizing")
            
            new_min_size = st.number_input(
                "Minimum Size",
                min_value=1,
                max_value=100,
                value=pool.min_size,
                key="config_min_size"
            )
            
            new_max_size = st.number_input(
                "Maximum Size",
                min_value=new_min_size,
                max_value=1000,
                value=pool.max_size,
                key="config_max_size"
            )
            
            new_target_size = st.number_input(
                "Target Size",
                min_value=new_min_size,
                max_value=new_max_size,
                value=pool.target_size,
                key="config_target_size"
            )
            
            st.markdown("#### Connection Limits")
            
            new_max_requests = st.number_input(
                "Max Requests per Connection",
                min_value=100,
                max_value=10000,
                value=pool.max_requests_per_connection,
                step=100,
                key="config_max_requests"
            )
            
            new_max_concurrent = st.number_input(
                "Max Concurrent Requests",
                min_value=10,
                max_value=1000,
                value=pool.max_concurrent_requests,
                step=10,
                key="config_max_concurrent"
            )
        
        with col2:
            st.markdown("#### Timeouts")
            
            new_conn_timeout = st.number_input(
                "Connection Timeout (ms)",
                min_value=100,
                max_value=30000,
                value=pool.connection_timeout_ms,
                step=100,
                key="config_conn_timeout"
            )
            
            new_req_timeout = st.number_input(
                "Request Timeout (ms)",
                min_value=1000,
                max_value=300000,
                value=pool.request_timeout_ms,
                step=1000,
                key="config_req_timeout"
            )
            
            new_max_idle = st.number_input(
                "Max Idle Time (seconds)",
                min_value=30,
                max_value=3600,
                value=pool.max_idle_seconds,
                step=30,
                key="config_max_idle"
            )
            
            new_max_lifetime = st.number_input(
                "Max Connection Lifetime (seconds)",
                min_value=300,
                max_value=86400,
                value=pool.max_lifetime_seconds,
                step=300,
                key="config_max_lifetime"
            )
            
            st.markdown("#### Health Checks")
            
            new_health_interval = st.number_input(
                "Health Check Interval (seconds)",
                min_value=10,
                max_value=300,
                value=pool.health_check_interval_seconds,
                step=10,
                key="config_health_interval"
            )
        
        # Apply changes
        if st.button("💾 Apply Configuration", type="primary"):
            # Update pool configuration
            pool.min_size = new_min_size
            pool.max_size = new_max_size
            pool.target_size = new_target_size
            pool.max_requests_per_connection = new_max_requests
            pool.max_concurrent_requests = new_max_concurrent
            pool.connection_timeout_ms = new_conn_timeout
            pool.request_timeout_ms = new_req_timeout
            pool.max_idle_seconds = new_max_idle
            pool.max_lifetime_seconds = new_max_lifetime
            pool.health_check_interval_seconds = new_health_interval
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.MONITORING,
                change_type=ChangeType.UPDATE,
                description=f"Updated configuration for pool: {pool.name}",
                details={
                    'pool_id': pool.pool_id,
                    'changes': {
                        'min_size': new_min_size,
                        'max_size': new_max_size,
                        'target_size': new_target_size,
                        'timeouts': {
                            'connection': new_conn_timeout,
                            'request': new_req_timeout
                        }
                    }
                }
            )
            
            st.success("Configuration updated successfully!")
            st.rerun()
        
        # Export/Import configuration
        st.markdown("### Configuration Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export Configuration"):
                config = {
                    'pool_name': pool.name,
                    'pool_type': pool.pool_type.value,
                    'sizing': {
                        'min_size': pool.min_size,
                        'max_size': pool.max_size,
                        'target_size': pool.target_size
                    },
                    'timeouts': {
                        'connection_ms': pool.connection_timeout_ms,
                        'request_ms': pool.request_timeout_ms,
                        'max_idle_seconds': pool.max_idle_seconds,
                        'max_lifetime_seconds': pool.max_lifetime_seconds
                    },
                    'limits': {
                        'max_requests_per_connection': pool.max_requests_per_connection,
                        'max_concurrent_requests': pool.max_concurrent_requests
                    },
                    'health': {
                        'check_interval_seconds': pool.health_check_interval_seconds,
                        'unhealthy_threshold': pool.unhealthy_threshold,
                        'healthy_threshold': pool.healthy_threshold
                    }
                }
                
                st.download_button(
                    "Download JSON",
                    data=json.dumps(config, indent=2),
                    file_name=f"pool_config_{pool.name.lower().replace(' ', '_')}.json",
                    mime="application/json"
                )
        
        with col2:
            uploaded_file = st.file_uploader(
                "Import Configuration",
                type=['json'],
                key="config_import"
            )
            
            if uploaded_file:
                try:
                    config = json.load(uploaded_file)
                    st.success("Configuration loaded! Apply changes above.")
                    # Could auto-populate fields here
                except Exception as e:
                    st.error(f"Error loading configuration: {e}")
        
        # Statistics
        st.markdown("### Pool Statistics")
        
        stats = self.pool_manager.get_statistics()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Pools", stats['pools_managed'])
            st.metric("Total Connections", stats['total_connections'])
        
        with col2:
            st.metric("Active Connections", stats['active_connections'])
            st.metric("Total Requests", f"{stats['total_requests']:,}")
        
        with col3:
            st.metric("Optimizations", stats['optimizations_generated'])
            st.metric("Events Logged", stats['events_logged'])