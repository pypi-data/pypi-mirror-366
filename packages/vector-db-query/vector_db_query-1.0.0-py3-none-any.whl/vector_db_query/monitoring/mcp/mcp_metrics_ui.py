"""
MCP Server metrics dashboard UI component.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import json

from .collector import get_mcp_collector
from .analyzer import MCPAnalyzer
from .models import MCPMetrics, MCPMethodStats, MCPSession
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class MCPMetricsUI:
    """
    MCP Server metrics dashboard UI.
    """
    
    def __init__(self):
        """Initialize MCP metrics UI."""
        self.collector = get_mcp_collector()
        self.analyzer = MCPAnalyzer(self.collector)
        self.change_tracker = get_change_tracker()
        
        # Initialize session state
        if 'mcp_auto_refresh' not in st.session_state:
            st.session_state.mcp_auto_refresh = True
        if 'mcp_refresh_interval' not in st.session_state:
            st.session_state.mcp_refresh_interval = 30
        if 'mcp_selected_method' not in st.session_state:
            st.session_state.mcp_selected_method = None
        if 'mcp_time_range' not in st.session_state:
            st.session_state.mcp_time_range = 24
    
    def render(self):
        """Render the MCP metrics dashboard."""
        st.header("🖥️ MCP Server Metrics Dashboard")
        
        # Check if collector is running
        if not self.collector._is_collecting:
            st.warning("MCP metrics collection is not running.")
            if st.button("Start Collection", key="start_mcp_collection"):
                asyncio.run(self.collector.start())
                st.rerun()
            return
        
        # Auto-refresh controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.session_state.mcp_auto_refresh = st.checkbox(
                "Auto-refresh",
                value=st.session_state.mcp_auto_refresh,
                key="mcp_auto_refresh_check"
            )
        with col2:
            st.session_state.mcp_refresh_interval = st.number_input(
                "Interval (s)",
                min_value=5,
                max_value=300,
                value=st.session_state.mcp_refresh_interval,
                key="mcp_refresh_interval_input"
            )
        with col3:
            if st.button("🔄 Refresh Now", key="refresh_mcp_metrics"):
                st.rerun()
        
        # Tabs
        tabs = st.tabs([
            "📊 Overview",
            "📈 Performance",
            "🔧 Methods",
            "📡 Sessions",
            "🚨 Alerts",
            "📋 Reports"
        ])
        
        with tabs[0]:
            self._render_overview_tab()
        
        with tabs[1]:
            self._render_performance_tab()
        
        with tabs[2]:
            self._render_methods_tab()
        
        with tabs[3]:
            self._render_sessions_tab()
        
        with tabs[4]:
            self._render_alerts_tab()
        
        with tabs[5]:
            self._render_reports_tab()
        
        # Auto-refresh
        if st.session_state.mcp_auto_refresh:
            st.empty()  # Placeholder for auto-refresh
            asyncio.run(asyncio.sleep(st.session_state.mcp_refresh_interval))
            st.rerun()
    
    def _render_overview_tab(self):
        """Render overview tab."""
        st.subheader("MCP Server Overview")
        
        # Get current metrics
        metrics = self.collector.get_current_metrics()
        
        # Server info
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Server Version",
                metrics.server_version or "Unknown",
                help="MCP server version"
            )
        
        with col2:
            uptime_hours = metrics.uptime_seconds / 3600
            st.metric(
                "Uptime",
                f"{uptime_hours:.1f}h",
                help="Server uptime in hours"
            )
        
        with col3:
            st.metric(
                "Active Sessions",
                metrics.active_sessions,
                delta=metrics.active_sessions - metrics.total_sessions,
                help="Currently active client sessions"
            )
        
        with col4:
            st.metric(
                "Requests in Flight",
                metrics.requests_in_flight,
                help="Requests currently being processed"
            )
        
        # Performance metrics
        st.markdown("### Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Requests/sec",
                f"{metrics.requests_per_second:.2f}",
                help="Current request rate"
            )
        
        with col2:
            st.metric(
                "Avg Response Time",
                f"{metrics.avg_response_time_ms:.0f}ms",
                help="Average response time"
            )
        
        with col3:
            error_rate_pct = metrics.error_rate * 100
            st.metric(
                "Error Rate",
                f"{error_rate_pct:.1f}%",
                delta=f"{error_rate_pct:.1f}%",
                delta_color="inverse",
                help="Percentage of failed requests"
            )
        
        with col4:
            st.metric(
                "Total Requests",
                f"{metrics.total_requests:,}",
                help="Total requests processed"
            )
        
        # Resource usage
        st.markdown("### Resource Usage")
        
        # CPU and Memory gauges
        col1, col2 = st.columns(2)
        
        with col1:
            cpu_fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=metrics.resource_usage.cpu_percent,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "CPU Usage (%)"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ))
            cpu_fig.update_layout(height=250)
            st.plotly_chart(cpu_fig, use_container_width=True)
        
        with col2:
            memory_fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=metrics.resource_usage.memory_percent,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Memory Usage (%)"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 85], 'color': "yellow"},
                        {'range': [85, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 85
                    }
                }
            ))
            memory_fig.update_layout(height=250)
            st.plotly_chart(memory_fig, use_container_width=True)
        
        # Network and connections
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Network In",
                f"{metrics.resource_usage.network_in_mbps:.1f} Mbps",
                help="Incoming network traffic"
            )
        
        with col2:
            st.metric(
                "Network Out",
                f"{metrics.resource_usage.network_out_mbps:.1f} Mbps",
                help="Outgoing network traffic"
            )
        
        with col3:
            st.metric(
                "Active Connections",
                metrics.resource_usage.active_connections,
                help="Active network connections"
            )
        
        with col4:
            st.metric(
                "Thread Pool",
                f"{metrics.resource_usage.thread_pool_active}/{metrics.resource_usage.thread_pool_size}",
                help="Active threads / Total threads"
            )
        
        # Database and cache metrics
        st.markdown("### Database & Cache")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "DB Pool Size",
                metrics.db_connection_pool_size,
                help="Database connection pool size"
            )
        
        with col2:
            st.metric(
                "Active DB Connections",
                metrics.db_active_connections,
                help="Active database connections"
            )
        
        with col3:
            cache_hit_pct = metrics.cache_hit_rate * 100
            st.metric(
                "Cache Hit Rate",
                f"{cache_hit_pct:.1f}%",
                help="Percentage of cache hits"
            )
        
        with col4:
            st.metric(
                "Cache Size",
                f"{metrics.cache_size_mb:.1f} MB",
                help="Current cache size"
            )
    
    def _render_performance_tab(self):
        """Render performance tab."""
        st.subheader("Performance Analysis")
        
        # Time range selector
        col1, col2 = st.columns([1, 3])
        with col1:
            time_range = st.selectbox(
                "Time Range",
                [1, 6, 12, 24, 48, 72],
                index=3,
                format_func=lambda x: f"Last {x} hours",
                key="perf_time_range"
            )
        
        # Get metrics history
        history = self.collector.get_metrics_history(time_range)
        
        if not history:
            st.info("No historical data available")
            return
        
        # Response time chart
        st.markdown("### Response Time Trends")
        
        response_times = []
        timestamps = []
        for metric in history:
            if metric.avg_response_time_ms > 0:
                response_times.append(metric.avg_response_time_ms)
                timestamps.append(metric.timestamp)
        
        if response_times:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=response_times,
                mode='lines+markers',
                name='Avg Response Time',
                line=dict(color='blue', width=2)
            ))
            fig.update_layout(
                title="Average Response Time",
                xaxis_title="Time",
                yaxis_title="Response Time (ms)",
                hovermode='x',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Request rate and error rate
        col1, col2 = st.columns(2)
        
        with col1:
            request_rates = []
            for metric in history:
                request_rates.append(metric.requests_per_second)
            
            if request_rates:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=request_rates,
                    mode='lines',
                    name='Requests/sec',
                    fill='tozeroy',
                    line=dict(color='green')
                ))
                fig.update_layout(
                    title="Request Rate",
                    xaxis_title="Time",
                    yaxis_title="Requests/sec",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            error_rates = []
            for metric in history:
                error_rates.append(metric.error_rate * 100)
            
            if error_rates:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=error_rates,
                    mode='lines',
                    name='Error Rate',
                    fill='tozeroy',
                    line=dict(color='red')
                ))
                fig.update_layout(
                    title="Error Rate",
                    xaxis_title="Time",
                    yaxis_title="Error Rate (%)",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Resource usage over time
        st.markdown("### Resource Usage Trends")
        
        resource_history = self.collector.get_resource_history(time_range)
        
        if resource_history:
            # CPU and Memory chart
            cpu_values = []
            memory_values = []
            resource_timestamps = []
            
            for resource in resource_history:
                cpu_values.append(resource.cpu_percent)
                memory_values.append(resource.memory_percent)
                resource_timestamps.append(resource.timestamp)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=resource_timestamps,
                y=cpu_values,
                mode='lines',
                name='CPU %',
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=resource_timestamps,
                y=memory_values,
                mode='lines',
                name='Memory %',
                line=dict(color='green')
            ))
            fig.update_layout(
                title="CPU and Memory Usage",
                xaxis_title="Time",
                yaxis_title="Usage (%)",
                hovermode='x',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Trends analysis
        st.markdown("### Trend Analysis")
        trends = self.analyzer.analyze_trends(time_range)
        
        if trends:
            trend_data = []
            for trend in trends:
                trend_data.append({
                    'Metric': trend.metric_name.replace('_', ' ').title(),
                    'Direction': trend.direction.value,
                    'Current': f"{trend.current_value:.2f}",
                    'Average': f"{trend.average_value:.2f}",
                    'Change': f"{trend.change_rate:+.1f}%",
                    'Confidence': f"{trend.confidence:.0%}"
                })
            
            df = pd.DataFrame(trend_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No significant trends detected")
    
    def _render_methods_tab(self):
        """Render methods tab."""
        st.subheader("Method Performance Analysis")
        
        # Get method stats
        method_stats = self.collector.get_method_stats()
        
        if not method_stats:
            st.info("No method statistics available")
            return
        
        # Method overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Method performance table
            method_data = []
            for name, stats in method_stats.items():
                method_data.append({
                    'Method': name,
                    'Calls': stats.total_calls,
                    'Success': stats.successful_calls,
                    'Failed': stats.failed_calls,
                    'Avg Time (ms)': f"{stats.avg_response_time:.0f}",
                    'Error Rate': f"{stats.error_rate:.1%}",
                    'Data (MB)': f"{stats.total_data_processed_mb:.1f}"
                })
            
            df = pd.DataFrame(method_data)
            df = df.sort_values('Calls', ascending=False)
            
            st.markdown("### Method Statistics")
            st.dataframe(df, use_container_width=True)
        
        with col2:
            # Method distribution pie chart
            if method_data:
                fig = px.pie(
                    values=[m['Calls'] for m in method_data[:10]],
                    names=[m['Method'] for m in method_data[:10]],
                    title="Top 10 Methods by Call Count"
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        # Method details
        st.markdown("### Method Details")
        
        selected_method = st.selectbox(
            "Select Method",
            list(method_stats.keys()),
            key="method_selector"
        )
        
        if selected_method:
            stats = method_stats[selected_method]
            
            # Method metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Calls", f"{stats.total_calls:,}")
            
            with col2:
                st.metric("Success Rate", f"{(1 - stats.error_rate):.1%}")
            
            with col3:
                st.metric("Avg Response", f"{stats.avg_response_time:.0f}ms")
            
            with col4:
                st.metric("Data Processed", f"{stats.total_data_processed_mb:.1f} MB")
            
            # Response time distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Response Time Range")
                st.info(f"""
                - **Min**: {stats.min_response_time:.0f}ms
                - **Avg**: {stats.avg_response_time:.0f}ms
                - **Max**: {stats.max_response_time:.0f}ms
                - **P50**: {stats.p50_response_time:.0f}ms
                - **P95**: {stats.p95_response_time:.0f}ms
                - **P99**: {stats.p99_response_time:.0f}ms
                """)
            
            with col2:
                st.markdown("#### Data Transfer")
                st.info(f"""
                - **Avg Request**: {stats.avg_request_size_bytes:,.0f} bytes
                - **Avg Response**: {stats.avg_response_size_bytes:,.0f} bytes
                - **Total Data**: {stats.total_data_processed_mb:.2f} MB
                - **Calls/min**: {stats.calls_per_minute:.1f}
                """)
            
            # Recent errors
            if stats.recent_errors:
                st.markdown("#### Recent Errors")
                for i, error in enumerate(stats.recent_errors[-5:], 1):
                    st.error(f"{i}. {error}")
    
    def _render_sessions_tab(self):
        """Render sessions tab."""
        st.subheader("Active Sessions")
        
        # Get active sessions
        active_sessions = self.collector.get_active_sessions()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Sessions", len(active_sessions))
        
        with col2:
            total_requests = sum(s.total_requests for s in active_sessions)
            st.metric("Total Requests", f"{total_requests:,}")
        
        with col3:
            total_data = sum(s.total_data_transferred_mb for s in active_sessions)
            st.metric("Total Data", f"{total_data:.1f} MB")
        
        if active_sessions:
            # Session table
            session_data = []
            for session in active_sessions:
                session_data.append({
                    'Session ID': session.id[:8] + '...',
                    'Client ID': session.client_id,
                    'Started': session.started_at.strftime('%H:%M:%S'),
                    'Duration': f"{session.duration_seconds() / 60:.1f}m",
                    'Requests': session.total_requests,
                    'Success': session.successful_requests,
                    'Failed': session.failed_requests,
                    'Data (MB)': f"{session.total_data_transferred_mb:.1f}",
                    'Last Activity': session.last_activity.strftime('%H:%M:%S')
                })
            
            df = pd.DataFrame(session_data)
            st.dataframe(df, use_container_width=True)
            
            # Session details
            if st.checkbox("Show Session Details"):
                selected_session = st.selectbox(
                    "Select Session",
                    [s.id for s in active_sessions],
                    format_func=lambda x: next(s.client_id for s in active_sessions if s.id == x)
                )
                
                if selected_session:
                    session = next(s for s in active_sessions if s.id == selected_session)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Session Info")
                        st.json({
                            'id': session.id,
                            'client_id': session.client_id,
                            'client_ip': session.client_ip,
                            'user_agent': session.user_agent,
                            'protocol_version': session.protocol_version
                        })
                    
                    with col2:
                        st.markdown("#### Session Metrics")
                        success_rate = session.successful_requests / max(session.total_requests, 1)
                        st.json({
                            'total_requests': session.total_requests,
                            'success_rate': f"{success_rate:.1%}",
                            'avg_request_size': f"{session.total_data_transferred_mb * 1024 / max(session.total_requests, 1):.1f} KB",
                            'requests_per_minute': f"{session.total_requests / max(session.duration_seconds() / 60, 1):.1f}"
                        })
        else:
            st.info("No active sessions")
    
    def _render_alerts_tab(self):
        """Render alerts tab."""
        st.subheader("Anomalies & Alerts")
        
        # Detect anomalies
        anomalies = self.analyzer.detect_anomalies()
        
        if anomalies:
            # Group by severity
            critical = [a for a in anomalies if a.severity == 'critical']
            high = [a for a in anomalies if a.severity == 'high']
            medium = [a for a in anomalies if a.severity == 'medium']
            low = [a for a in anomalies if a.severity == 'low']
            
            # Summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Critical", len(critical), delta_color="inverse")
            with col2:
                st.metric("High", len(high), delta_color="inverse")
            with col3:
                st.metric("Medium", len(medium))
            with col4:
                st.metric("Low", len(low))
            
            # Anomaly list
            for anomaly in anomalies:
                severity_color = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(anomaly.severity, '⚪')
                
                with st.expander(f"{severity_color} {anomaly.anomaly_type.value} - {anomaly.metric_name}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Details**")
                        st.write(f"- Current Value: {anomaly.current_value:.2f}")
                        st.write(f"- Expected Value: {anomaly.expected_value:.2f}")
                        st.write(f"- Deviation: {anomaly.deviation:.1f} σ")
                        st.write(f"- Time: {anomaly.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    with col2:
                        st.markdown("**Description**")
                        st.write(anomaly.description)
                        if anomaly.recommended_action:
                            st.markdown("**Recommended Action**")
                            st.info(anomaly.recommended_action)
        else:
            st.success("No anomalies detected")
        
        # Recent errors
        st.markdown("### Recent Errors")
        
        errors = self.collector.get_recent_errors(20)
        
        if errors:
            error_data = []
            for error in errors:
                error_data.append({
                    'Time': error.timestamp.strftime('%H:%M:%S'),
                    'Type': error.error_type,
                    'Message': error.error_message[:100] + '...' if len(error.error_message) > 100 else error.error_message,
                    'Method': error.method or 'N/A',
                    'Severity': error.severity
                })
            
            df = pd.DataFrame(error_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent errors")
    
    def _render_reports_tab(self):
        """Render reports tab."""
        st.subheader("Performance Reports")
        
        # Report generation
        col1, col2, col3 = st.columns(3)
        
        with col1:
            report_period = st.selectbox(
                "Report Period",
                [6, 12, 24, 48, 72],
                index=2,
                format_func=lambda x: f"Last {x} hours"
            )
        
        with col2:
            if st.button("Generate Report", type="primary"):
                with st.spinner("Generating performance report..."):
                    report = self.analyzer.generate_performance_report(report_period)
                    st.session_state.mcp_report = report
                    
                    # Track report generation
                    self.change_tracker.track_change(
                        category=ChangeCategory.MONITORING,
                        change_type=ChangeType.CREATE,
                        description="Generated MCP performance report",
                        details={
                            'period_hours': report_period,
                            'health_score': report.health_score
                        }
                    )
        
        with col3:
            if 'mcp_report' in st.session_state:
                if st.button("Export Report"):
                    report_json = json.dumps(
                        st.session_state.mcp_report.to_dict(),
                        indent=2,
                        default=str
                    )
                    st.download_button(
                        "Download JSON",
                        report_json,
                        f"mcp_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        "application/json"
                    )
        
        # Display report
        if 'mcp_report' in st.session_state:
            report = st.session_state.mcp_report
            
            # Health score
            health_color = "green" if report.health_score >= 80 else "orange" if report.health_score >= 60 else "red"
            st.markdown(f"### Health Score: <span style='color:{health_color}'>{report.health_score:.0f}/100</span>", unsafe_allow_html=True)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg Response Time", f"{report.avg_response_time_ms:.0f}ms")
            
            with col2:
                st.metric("P95 Response Time", f"{report.p95_response_time_ms:.0f}ms")
            
            with col3:
                st.metric("Error Rate", f"{report.error_rate:.1%}")
            
            with col4:
                st.metric("Total Requests", f"{report.total_requests:,}")
            
            # Resource usage
            st.markdown("### Resource Usage Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg CPU", f"{report.avg_cpu_percent:.1f}%")
            
            with col2:
                st.metric("Peak CPU", f"{report.peak_cpu_percent:.1f}%")
            
            with col3:
                st.metric("Avg Memory", f"{report.avg_memory_mb:.0f} MB")
            
            with col4:
                st.metric("Peak Memory", f"{report.peak_memory_mb:.0f} MB")
            
            # Slowest methods
            if report.slowest_methods:
                st.markdown("### Slowest Methods")
                slow_df = pd.DataFrame(report.slowest_methods)
                st.dataframe(slow_df, use_container_width=True)
            
            # Error-prone methods
            if report.most_error_prone_methods:
                st.markdown("### Most Error-Prone Methods")
                error_df = pd.DataFrame(report.most_error_prone_methods)
                st.dataframe(error_df, use_container_width=True)
            
            # Recommendations
            if report.recommendations:
                st.markdown("### Recommendations")
                for i, rec in enumerate(report.recommendations, 1):
                    st.warning(f"{i}. {rec}")
        
        # Connection test
        st.markdown("### MCP Server Connection Test")
        
        if st.button("Test Connection"):
            with st.spinner("Testing MCP server connection..."):
                result = asyncio.run(self.collector.test_connection())
                
                if result['connected']:
                    st.success("MCP server is connected and operational")
                else:
                    st.error("MCP server connection issues detected")
                
                # Display test results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Connection Status**")
                    st.write(f"- Process Found: {'✅' if result['process_found'] else '❌'}")
                    st.write(f"- Socket Exists: {'✅' if result['socket_exists'] else '❌'}")
                    st.write(f"- Log Readable: {'✅' if result['log_readable'] else '❌'}")
                
                with col2:
                    st.markdown("**Details**")
                    if result['details']:
                        st.json(result['details'])