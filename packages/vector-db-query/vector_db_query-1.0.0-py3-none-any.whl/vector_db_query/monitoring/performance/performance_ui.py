"""
Query performance tracking UI component.
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

from .tracker import get_performance_tracker
from .models import (
    QueryMetrics, QueryPattern, PerformanceSnapshot,
    PerformanceTrend, OptimizationRecommendation,
    QueryType, QueryStatus, PerformanceGrade
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class QueryPerformanceUI:
    """
    Query performance tracking and analysis UI.
    """
    
    def __init__(self):
        """Initialize query performance UI."""
        self.tracker = get_performance_tracker()
        self.change_tracker = get_change_tracker()
        
        # Initialize session state
        if 'perf_selected_query' not in st.session_state:
            st.session_state.perf_selected_query = None
        if 'perf_time_range' not in st.session_state:
            st.session_state.perf_time_range = 24
        if 'perf_auto_refresh' not in st.session_state:
            st.session_state.perf_auto_refresh = True
    
    def render(self):
        """Render the query performance UI."""
        st.header("⚡ Query Performance Tracking")
        
        # Start tracker if not running
        if not hasattr(self.tracker, '_snapshot_task') or self.tracker._snapshot_task is None:
            asyncio.run(self.tracker.start())
        
        # Auto-refresh controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.session_state.perf_auto_refresh = st.checkbox(
                "Auto-refresh",
                value=st.session_state.perf_auto_refresh,
                key="perf_auto_refresh_check"
            )
        with col2:
            refresh_interval = st.number_input(
                "Interval (s)",
                min_value=5,
                max_value=60,
                value=10,
                key="perf_refresh_interval"
            )
        with col3:
            if st.button("🔄 Refresh Now", key="refresh_performance"):
                st.rerun()
        
        # Tabs
        tabs = st.tabs([
            "📊 Overview",
            "🔍 Active Queries",
            "📈 Trends",
            "🎯 Patterns",
            "💡 Recommendations",
            "📋 Query History",
            "🔧 Configuration"
        ])
        
        with tabs[0]:
            self._render_overview_tab()
        
        with tabs[1]:
            self._render_active_queries_tab()
        
        with tabs[2]:
            self._render_trends_tab()
        
        with tabs[3]:
            self._render_patterns_tab()
        
        with tabs[4]:
            self._render_recommendations_tab()
        
        with tabs[5]:
            self._render_history_tab()
        
        with tabs[6]:
            self._render_configuration_tab()
        
        # Auto-refresh
        if st.session_state.perf_auto_refresh:
            st.empty()
            asyncio.run(asyncio.sleep(refresh_interval))
            st.rerun()
    
    def _render_overview_tab(self):
        """Render overview tab."""
        st.subheader("Performance Overview")
        
        # Get latest snapshot
        snapshot = self.tracker.get_latest_snapshot()
        
        if not snapshot:
            st.info("No performance data available yet. Queries will be tracked as they execute.")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Queries",
                f"{snapshot.total_queries:,}",
                help="Queries in the last minute"
            )
        
        with col2:
            st.metric(
                "Queries/sec",
                f"{snapshot.queries_per_second:.2f}",
                help="Current query rate"
            )
        
        with col3:
            st.metric(
                "Avg Response Time",
                f"{snapshot.avg_response_time_ms:.0f}ms",
                delta=f"{snapshot.avg_response_time_ms - snapshot.median_response_time_ms:.0f}ms",
                help="Average query response time"
            )
        
        with col4:
            error_pct = snapshot.error_rate * 100
            st.metric(
                "Error Rate",
                f"{error_pct:.1f}%",
                delta=f"{error_pct:.1f}%",
                delta_color="inverse",
                help="Percentage of failed queries"
            )
        
        # Performance distribution
        st.markdown("### Performance Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            # Grade distribution pie chart
            if snapshot.grade_distribution:
                grade_data = [
                    {"Grade": grade.value.title(), "Count": count}
                    for grade, count in snapshot.grade_distribution.items()
                ]
                
                fig = px.pie(
                    grade_data,
                    values="Count",
                    names="Grade",
                    title="Query Performance Grades",
                    color_discrete_map={
                        "Excellent": "#00cc44",
                        "Good": "#66cc00",
                        "Acceptable": "#ffcc00",
                        "Slow": "#ff6600",
                        "Critical": "#cc0000"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Query type distribution
            if snapshot.type_distribution:
                type_data = [
                    {"Type": qtype.value.replace("_", " ").title(), "Count": count}
                    for qtype, count in snapshot.type_distribution.items()
                ]
                
                fig = px.bar(
                    type_data,
                    x="Type",
                    y="Count",
                    title="Query Type Distribution",
                    color="Count",
                    color_continuous_scale="Blues"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Response time percentiles
        st.markdown("### Response Time Percentiles")
        
        percentile_data = {
            "Percentile": ["Average", "Median (P50)", "P95", "P99"],
            "Response Time (ms)": [
                snapshot.avg_response_time_ms,
                snapshot.median_response_time_ms,
                snapshot.p95_response_time_ms,
                snapshot.p99_response_time_ms
            ]
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=percentile_data["Percentile"],
                y=percentile_data["Response Time (ms)"],
                marker_color=['lightblue', 'blue', 'orange', 'red']
            )
        ])
        fig.update_layout(
            title="Response Time Distribution",
            xaxis_title="Percentile",
            yaxis_title="Response Time (ms)",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Resource utilization
        st.markdown("### Resource Utilization")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Avg CPU",
                f"{snapshot.avg_cpu_percent:.1f}%",
                help="Average CPU usage"
            )
        
        with col2:
            st.metric(
                "Peak CPU",
                f"{snapshot.peak_cpu_percent:.1f}%",
                help="Peak CPU usage"
            )
        
        with col3:
            st.metric(
                "Avg Memory",
                f"{snapshot.avg_memory_mb:.0f} MB",
                help="Average memory usage"
            )
        
        with col4:
            st.metric(
                "Cache Hit Rate",
                f"{snapshot.cache_hit_rate * 100:.1f}%",
                help="Percentage of cache hits"
            )
        
        # Top issues
        if snapshot.slowest_queries:
            st.markdown("### Current Issues")
            st.warning(f"🐌 {len(snapshot.slowest_queries)} slow queries detected")
            
            with st.expander("View Slow Queries"):
                for query_id in snapshot.slowest_queries:
                    st.write(f"- Query ID: {query_id}")
    
    def _render_active_queries_tab(self):
        """Render active queries tab."""
        st.subheader("Active Queries")
        
        active_queries = self.tracker.get_active_queries()
        
        if not active_queries:
            st.info("No queries currently executing")
            return
        
        st.markdown(f"### {len(active_queries)} Active Queries")
        
        # Create table data
        data = []
        for query in active_queries:
            elapsed = (datetime.now() - query.started_at).total_seconds()
            
            data.append({
                "Query ID": query.query_id[:8] + "...",
                "Type": query.query_type.value,
                "Status": query.status.value,
                "Elapsed (s)": f"{elapsed:.1f}",
                "CPU %": f"{query.cpu_usage_percent:.1f}",
                "Memory MB": f"{query.memory_used_mb:.0f}"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Query details
        if st.checkbox("Show Query Details"):
            selected_id = st.selectbox(
                "Select Query",
                [q.query_id for q in active_queries],
                format_func=lambda x: x[:8] + "..."
            )
            
            if selected_id:
                query = next(q for q in active_queries if q.query_id == selected_id)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Query Information")
                    st.write(f"**ID**: {query.query_id}")
                    st.write(f"**Type**: {query.query_type.value}")
                    st.write(f"**Status**: {query.status.value}")
                    st.write(f"**Started**: {query.started_at.strftime('%H:%M:%S')}")
                
                with col2:
                    st.markdown("#### Performance Metrics")
                    elapsed = (datetime.now() - query.started_at).total_seconds() * 1000
                    st.write(f"**Elapsed Time**: {elapsed:.0f}ms")
                    st.write(f"**CPU Usage**: {query.cpu_usage_percent:.1f}%")
                    st.write(f"**Memory**: {query.memory_used_mb:.1f} MB")
                    st.write(f"**IO Operations**: {query.io_operations}")
    
    def _render_trends_tab(self):
        """Render trends tab."""
        st.subheader("Performance Trends")
        
        # Time range selector
        time_range = st.selectbox(
            "Time Range",
            [1, 6, 12, 24, 48],
            index=3,
            format_func=lambda x: f"Last {x} hours",
            key="trend_time_range"
        )
        
        trends = self.tracker.get_performance_trends()
        
        if not trends:
            st.info("No trend data available yet")
            return
        
        # Response time trend
        st.markdown("### Response Time Trend")
        
        response_trend = trends.get('response_time')
        if response_trend and response_trend.values:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=response_trend.timestamps,
                y=response_trend.values,
                mode='lines+markers',
                name='Response Time',
                line=dict(color='blue', width=2)
            ))
            
            # Add trend line
            if len(response_trend.values) > 2:
                z = np.polyfit(range(len(response_trend.values)), response_trend.values, 1)
                p = np.poly1d(z)
                fig.add_trace(go.Scatter(
                    x=response_trend.timestamps,
                    y=p(range(len(response_trend.values))),
                    mode='lines',
                    name='Trend',
                    line=dict(color='red', dash='dash')
                ))
            
            fig.update_layout(
                title="Average Response Time",
                xaxis_title="Time",
                yaxis_title="Response Time (ms)",
                hovermode='x',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Query rate and error rate
        col1, col2 = st.columns(2)
        
        with col1:
            query_rate_trend = trends.get('query_rate')
            if query_rate_trend and query_rate_trend.values:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=query_rate_trend.timestamps,
                    y=query_rate_trend.values,
                    mode='lines',
                    fill='tozeroy',
                    name='Query Rate',
                    line=dict(color='green')
                ))
                fig.update_layout(
                    title="Query Rate",
                    xaxis_title="Time",
                    yaxis_title="Queries/sec",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            error_trend = trends.get('error_rate')
            if error_trend and error_trend.values:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=error_trend.timestamps,
                    y=[v * 100 for v in error_trend.values],
                    mode='lines',
                    fill='tozeroy',
                    name='Error Rate',
                    line=dict(color='red')
                ))
                fig.update_layout(
                    title="Error Rate",
                    xaxis_title="Time",
                    yaxis_title="Error Rate (%)",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Resource trends
        st.markdown("### Resource Usage Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cpu_trend = trends.get('cpu_usage')
            if cpu_trend and cpu_trend.values:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=cpu_trend.timestamps,
                    y=cpu_trend.values,
                    mode='lines',
                    name='CPU Usage',
                    line=dict(color='purple')
                ))
                fig.update_layout(
                    title="CPU Usage",
                    xaxis_title="Time",
                    yaxis_title="CPU %",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            memory_trend = trends.get('memory_usage')
            if memory_trend and memory_trend.values:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=memory_trend.timestamps,
                    y=memory_trend.values,
                    mode='lines',
                    name='Memory Usage',
                    line=dict(color='orange')
                ))
                fig.update_layout(
                    title="Memory Usage",
                    xaxis_title="Time",
                    yaxis_title="Memory (MB)",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_patterns_tab(self):
        """Render query patterns tab."""
        st.subheader("Query Patterns")
        
        patterns = self.tracker.get_query_patterns()
        
        if not patterns:
            st.info("No query patterns detected yet. Patterns are identified as queries execute.")
            return
        
        st.markdown(f"### {len(patterns)} Patterns Detected")
        
        # Pattern overview table
        pattern_data = []
        for pattern in patterns:
            pattern_data.append({
                "Pattern": pattern.pattern_type,
                "Frequency": pattern.frequency,
                "Avg Time (ms)": f"{pattern.avg_duration_ms:.0f}",
                "Min Time (ms)": f"{pattern.min_duration_ms:.0f}",
                "Max Time (ms)": f"{pattern.max_duration_ms:.0f}",
                "Avg CPU %": f"{pattern.avg_cpu_percent:.1f}",
                "Optimization Score": f"{pattern.optimization_score:.0f}"
            })
        
        df = pd.DataFrame(pattern_data)
        df = df.sort_values("Frequency", ascending=False)
        st.dataframe(df, use_container_width=True)
        
        # Pattern details
        st.markdown("### Pattern Analysis")
        
        selected_pattern = st.selectbox(
            "Select Pattern",
            [p.pattern_type for p in patterns],
            key="pattern_selector"
        )
        
        if selected_pattern:
            pattern = next(p for p in patterns if p.pattern_type == selected_pattern)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### Pattern Info")
                st.write(f"**Type**: {pattern.pattern_type}")
                st.write(f"**Description**: {pattern.description}")
                st.write(f"**First Seen**: {pattern.first_seen.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Last Seen**: {pattern.last_seen.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                st.markdown("#### Performance Profile")
                st.write(f"**Frequency**: {pattern.frequency} executions")
                st.write(f"**Avg Duration**: {pattern.avg_duration_ms:.0f}ms")
                st.write(f"**P95 Duration**: {pattern.p95_duration_ms:.0f}ms")
                st.write(f"**Optimization Score**: {pattern.optimization_score:.0f}/100")
            
            with col3:
                st.markdown("#### Resource Usage")
                st.write(f"**Avg CPU**: {pattern.avg_cpu_percent:.1f}%")
                st.write(f"**Avg Memory**: {pattern.avg_memory_mb:.0f} MB")
            
            # Optimization suggestions
            if pattern.suggested_optimizations:
                st.markdown("#### Optimization Suggestions")
                for suggestion in pattern.suggested_optimizations:
                    st.info(f"💡 {suggestion}")
    
    def _render_recommendations_tab(self):
        """Render optimization recommendations tab."""
        st.subheader("Optimization Recommendations")
        
        recommendations = self.tracker.get_recommendations()
        
        if not recommendations:
            st.success("No optimization recommendations at this time. System is performing well!")
            return
        
        st.markdown(f"### {len(recommendations)} Recommendations")
        
        # Priority filter
        priority_filter = st.multiselect(
            "Filter by Impact",
            ["critical", "high", "medium", "low"],
            default=["critical", "high"]
        )
        
        filtered_recs = [r for r in recommendations if r.impact in priority_filter]
        
        # Recommendation cards
        for rec in filtered_recs:
            priority_color = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(rec.impact, "⚪")
            
            effort_emoji = {
                "low": "⚡",
                "medium": "⏱️",
                "high": "🏗️"
            }.get(rec.effort, "❓")
            
            with st.expander(
                f"{priority_color} {rec.title} {effort_emoji}",
                expanded=(rec.impact == "critical")
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description**: {rec.description}")
                    
                    st.markdown("**Expected Improvements**")
                    st.write(f"- Time Reduction: {rec.expected_time_reduction_percent:.0f}%")
                    st.write(f"- Resource Reduction: {rec.expected_resource_reduction_percent:.0f}%")
                    st.write(f"- Affected Queries: {rec.affected_queries_per_hour:.0f}/hour")
                    
                    if rec.implementation_steps:
                        st.markdown("**Implementation Steps**")
                        for i, step in enumerate(rec.implementation_steps, 1):
                            st.write(f"{i}. {step}")
                
                with col2:
                    st.markdown("**Metadata**")
                    st.write(f"**Impact**: {rec.impact}")
                    st.write(f"**Effort**: {rec.effort}")
                    st.write(f"**Priority Score**: {rec.calculate_priority_score():.1f}")
                    st.write(f"**Type**: {rec.implementation_type}")
                    st.write(f"**Status**: {rec.status}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"📋 Copy SQL", key=f"copy_{rec.recommendation_id}"):
                        if rec.sql_commands:
                            sql_text = "\n".join(rec.sql_commands)
                            st.code(sql_text, language="sql")
                
                with col2:
                    if st.button(f"✅ Mark Implemented", key=f"impl_{rec.recommendation_id}"):
                        rec.status = "completed"
                        rec.implemented_at = datetime.now()
                        st.success("Marked as implemented")
                        st.rerun()
                
                with col3:
                    if st.button(f"❌ Dismiss", key=f"dismiss_{rec.recommendation_id}"):
                        rec.status = "rejected"
                        st.info("Recommendation dismissed")
                        st.rerun()
    
    def _render_history_tab(self):
        """Render query history tab."""
        st.subheader("Query History")
        
        # Controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            limit = st.number_input(
                "Number of Queries",
                min_value=10,
                max_value=1000,
                value=100,
                step=10
            )
        
        with col2:
            query_type_filter = st.multiselect(
                "Filter by Type",
                [qt.value for qt in QueryType],
                default=[]
            )
        
        with col3:
            grade_filter = st.multiselect(
                "Filter by Grade",
                [g.value for g in PerformanceGrade],
                default=[]
            )
        
        # Get recent queries
        recent_queries = self.tracker.get_recent_queries(limit)
        
        if not recent_queries:
            st.info("No query history available")
            return
        
        # Apply filters
        if query_type_filter:
            recent_queries = [
                q for q in recent_queries 
                if q.query_type.value in query_type_filter
            ]
        
        if grade_filter:
            recent_queries = [
                q for q in recent_queries
                if q.calculate_grade().value in grade_filter
            ]
        
        # Create history table
        history_data = []
        for query in recent_queries:
            history_data.append({
                "Time": query.started_at.strftime("%H:%M:%S"),
                "Query ID": query.query_id[:8] + "...",
                "Type": query.query_type.value,
                "Status": query.status.value,
                "Duration (ms)": f"{query.total_time_ms:.0f}",
                "Grade": query.calculate_grade().value,
                "Results": query.results_returned,
                "Cache Hit": "✓" if query.cache_hit else "✗",
                "CPU %": f"{query.cpu_usage_percent:.1f}",
                "Memory MB": f"{query.memory_used_mb:.0f}"
            })
        
        df = pd.DataFrame(history_data)
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Grade": st.column_config.TextColumn(
                    "Grade",
                    help="Performance grade"
                ),
                "Cache Hit": st.column_config.TextColumn(
                    "Cache",
                    help="Cache hit status"
                )
            }
        )
        
        # Export functionality
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                f"query_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
    
    def _render_configuration_tab(self):
        """Render configuration tab."""
        st.subheader("Performance Tracking Configuration")
        
        # Tracking settings
        st.markdown("### Tracking Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            retention_hours = st.number_input(
                "Data Retention (hours)",
                min_value=1,
                max_value=168,
                value=self.tracker.retention_hours,
                help="How long to keep performance data"
            )
            
            if retention_hours != self.tracker.retention_hours:
                self.tracker.retention_hours = retention_hours
                st.success("Retention period updated")
        
        with col2:
            st.markdown("#### Statistics")
            stats = self.tracker.get_statistics()
            st.write(f"**Queries Tracked**: {stats['queries_tracked']:,}")
            st.write(f"**Patterns Detected**: {stats['patterns_detected']}")
            st.write(f"**Recommendations**: {stats['recommendations_generated']}")
            st.write(f"**Anomalies Detected**: {stats['anomalies_detected']}")
        
        # Performance thresholds
        st.markdown("### Performance Thresholds")
        
        st.info("Define thresholds for performance grades")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.number_input(
                "Excellent (< ms)",
                min_value=1,
                max_value=100,
                value=10,
                help="Queries faster than this are excellent"
            )
            
            st.number_input(
                "Good (< ms)",
                min_value=10,
                max_value=500,
                value=50,
                help="Queries faster than this are good"
            )
        
        with col2:
            st.number_input(
                "Acceptable (< ms)",
                min_value=50,
                max_value=1000,
                value=200,
                help="Queries faster than this are acceptable"
            )
            
            st.number_input(
                "Slow (< ms)",
                min_value=200,
                max_value=5000,
                value=1000,
                help="Queries faster than this are slow"
            )
        
        with col3:
            st.info("Queries slower than the 'Slow' threshold are considered critical")
        
        # Test query tracking
        st.markdown("### Test Query Tracking")
        
        st.info("Generate test queries to verify tracking functionality")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_query_type = st.selectbox(
                "Query Type",
                [qt.value for qt in QueryType],
                key="test_query_type"
            )
            
            test_duration = st.slider(
                "Simulated Duration (ms)",
                min_value=1,
                max_value=5000,
                value=100,
                key="test_duration"
            )
        
        with col2:
            if st.button("🧪 Generate Test Query", type="primary"):
                # Start tracking
                query_id = self.tracker.start_query(
                    QueryType(test_query_type),
                    query_text="Test query for performance tracking"
                )
                
                # Simulate some metrics
                self.tracker.update_query_metrics(
                    query_id,
                    total_time_ms=test_duration,
                    cpu_usage_percent=np.random.uniform(5, 50),
                    memory_used_mb=np.random.uniform(10, 100),
                    results_returned=np.random.randint(1, 100),
                    cache_hit=np.random.choice([True, False])
                )
                
                # Complete query
                self.tracker.complete_query(query_id, QueryStatus.COMPLETED)
                
                st.success(f"Test query {query_id[:8]}... completed in {test_duration}ms")
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.MONITORING,
                    change_type=ChangeType.CREATE,
                    description="Generated test query for performance tracking",
                    details={
                        'query_type': test_query_type,
                        'duration_ms': test_duration
                    }
                )