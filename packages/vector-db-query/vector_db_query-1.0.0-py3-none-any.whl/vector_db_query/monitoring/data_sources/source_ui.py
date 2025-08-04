"""Streamlit UI components for data source monitoring."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any, Optional, List
import pandas as pd

from .source_metrics import DataSourceMetrics
from .source_controls import DataSourceControls
from ...data_sources.models import SourceType
from ...utils.logger import get_logger

logger = get_logger(__name__)


class DataSourceMonitoringUI:
    """UI components for data source monitoring."""
    
    def __init__(self, metrics: DataSourceMetrics, controls: DataSourceControls):
        """Initialize UI components.
        
        Args:
            metrics: Metrics collector instance
            controls: Source controls instance
        """
        self.metrics = metrics
        self.controls = controls
        
        # Initialize session state
        if 'data_source_refresh' not in st.session_state:
            st.session_state.data_source_refresh = True
        if 'selected_source' not in st.session_state:
            st.session_state.selected_source = None
    
    def render(self):
        """Render the data sources monitoring section."""
        st.header("📊 Data Sources")
        
        # Top-level controls
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            # Source selector
            source_options = ["All Sources"] + [s.value.title() for s in SourceType]
            selected = st.selectbox(
                "Select Source",
                source_options,
                key="source_selector"
            )
            
            if selected != "All Sources":
                st.session_state.selected_source = SourceType(selected.lower())
            else:
                st.session_state.selected_source = None
        
        with col2:
            # Refresh control
            auto_refresh = st.checkbox(
                "Auto Refresh",
                value=st.session_state.data_source_refresh,
                key="auto_refresh_data_sources"
            )
            st.session_state.data_source_refresh = auto_refresh
        
        with col3:
            # Manual refresh button
            if st.button("🔄 Refresh Now", key="refresh_data_sources"):
                st.rerun()
        
        with col4:
            # Sync all button
            if st.button("🔄 Sync All", key="sync_all_sources"):
                asyncio.run(self._handle_sync_all())
        
        # Main content area
        if st.session_state.selected_source:
            self._render_single_source(st.session_state.selected_source)
        else:
            self._render_all_sources()
        
        # Auto-refresh logic
        if auto_refresh:
            st.empty()  # Placeholder for auto-refresh
            asyncio.run(self._auto_refresh())
    
    def _render_all_sources(self):
        """Render overview of all data sources."""
        # Get metrics
        metrics = asyncio.run(self.metrics.get_source_metrics())
        
        if not metrics:
            st.warning("No metrics available. Have you configured any data sources?")
            return
        
        # Overall summary cards
        if 'overall' in metrics:
            overall = metrics['overall']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Items",
                    f"{overall.get('total_items', 0):,}",
                    delta=f"{overall.get('pending_items', 0)} pending"
                )
            
            with col2:
                st.metric(
                    "Active Sources",
                    overall.get('active_sources', 0),
                    delta=None
                )
            
            with col3:
                success_rate = overall.get('success_rate', 0)
                st.metric(
                    "Success Rate",
                    f"{success_rate:.1f}%",
                    delta=f"{overall.get('failed_items', 0)} failed"
                )
            
            with col4:
                last_sync = overall.get('last_sync')
                if last_sync:
                    last_sync_dt = datetime.fromisoformat(last_sync)
                    mins_ago = (datetime.utcnow() - last_sync_dt).seconds // 60
                    st.metric("Last Activity", f"{mins_ago}m ago")
                else:
                    st.metric("Last Activity", "Never")
        
        # Per-source status grid
        st.subheader("Source Status")
        
        source_cols = st.columns(3)
        
        for idx, source_type in enumerate(SourceType):
            col_idx = idx % 3
            
            with source_cols[col_idx]:
                source_data = metrics.get(source_type.value, {})
                self._render_source_card(source_type, source_data)
        
        # Activity timeline
        st.subheader("Activity Timeline (24h)")
        self._render_activity_timeline(metrics)
        
        # Recent errors
        errors = asyncio.run(self.metrics.get_error_summary())
        if errors:
            st.subheader("⚠️ Recent Errors")
            self._render_error_summary(errors)
    
    def _render_single_source(self, source_type: SourceType):
        """Render detailed view for a single source."""
        # Special handling for Gmail - use dedicated widget
        if source_type == SourceType.GMAIL:
            from ..widgets.gmail_widget import render_gmail_widget
            render_gmail_widget()
            return
        
        # Special handling for Fireflies - use dedicated widget
        if source_type == SourceType.FIREFLIES:
            from ..widgets.fireflies_widget import FirefliesMonitoringWidget
            widget = FirefliesMonitoringWidget()
            widget.render()
            return
        
        # Special handling for Google Drive - use dedicated widget
        if source_type == SourceType.GOOGLE_DRIVE:
            from ..widgets.googledrive_widget import render_googledrive_widget
            render_googledrive_widget()
            return
        
        # Default rendering for other sources
        # Get metrics for this source
        metrics = asyncio.run(self.metrics.get_source_metrics(source_type))
        source_data = metrics.get(source_type.value, {})
        
        if not source_data:
            st.warning(f"No data available for {source_type.value}")
            return
        
        # Header with controls
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.subheader(f"{source_type.value.title()} Details")
        
        with col2:
            if st.button(f"🔄 Sync {source_type.value.title()}", key=f"sync_{source_type.value}"):
                asyncio.run(self._handle_sync_source(source_type))
        
        with col3:
            sync_state = source_data.get('sync_state', {})
            is_active = sync_state.get('is_active', False) if sync_state else False
            
            if is_active:
                if st.button("⏸️ Pause", key=f"pause_{source_type.value}"):
                    asyncio.run(self.controls.pause_source(source_type))
                    st.rerun()
            else:
                if st.button("▶️ Resume", key=f"resume_{source_type.value}"):
                    asyncio.run(self.controls.resume_source(source_type))
                    st.rerun()
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Items", f"{source_data.get('total_items', 0):,}")
        
        with col2:
            st.metric("Completed", f"{source_data.get('completed', 0):,}")
        
        with col3:
            st.metric("Failed", f"{source_data.get('failed', 0):,}")
        
        with col4:
            st.metric("Pending", f"{source_data.get('pending', 0):,}")
        
        # Activity chart
        st.subheader("Activity (24h)")
        self._render_source_activity_chart(source_data)
        
        # Sync history
        st.subheader("Recent Sync History")
        history = asyncio.run(self.metrics.get_sync_history(source_type, hours=24))
        self._render_sync_history(history)
        
        # Configuration
        if sync_state and sync_state.get('configuration'):
            with st.expander("Configuration"):
                st.json(sync_state['configuration'])
    
    def _render_source_card(self, source_type: SourceType, data: Dict[str, Any]):
        """Render a card for a single source."""
        # Determine status color
        sync_state = data.get('sync_state', {})
        is_active = sync_state.get('is_active', False) if sync_state else False
        has_errors = sync_state.get('error_count', 0) > 0 if sync_state else False
        
        if not is_active:
            status_color = "🔴"  # Red - inactive
        elif has_errors:
            status_color = "🟡"  # Yellow - active with errors
        else:
            status_color = "🟢"  # Green - active and healthy
        
        # Card container
        with st.container():
            st.markdown(f"### {status_color} {source_type.value.title()}")
            
            # Metrics
            total = data.get('total_items', 0)
            success_rate = data.get('success_rate', 0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Items", f"{total:,}")
            with col2:
                st.metric("Success", f"{success_rate:.0f}%")
            
            # Last sync
            last_sync = sync_state.get('last_sync') if sync_state else None
            if last_sync:
                last_sync_dt = datetime.fromisoformat(last_sync)
                mins_ago = (datetime.utcnow() - last_sync_dt).seconds // 60
                st.caption(f"Last sync: {mins_ago}m ago")
            else:
                st.caption("Never synced")
            
            # Error indicator
            if has_errors and sync_state:
                st.error(f"⚠️ {sync_state['error_count']} errors")
    
    def _render_activity_timeline(self, metrics: Dict[str, Any]):
        """Render combined activity timeline."""
        # Collect all activity data
        all_activity = []
        
        for source_type in SourceType:
            source_data = metrics.get(source_type.value, {})
            activity = source_data.get('activity_24h', [])
            
            for point in activity:
                all_activity.append({
                    'hour': datetime.fromisoformat(point['hour']),
                    'count': point['count'],
                    'source': source_type.value
                })
        
        if not all_activity:
            st.info("No activity in the last 24 hours")
            return
        
        # Create DataFrame
        df = pd.DataFrame(all_activity)
        
        # Create stacked bar chart
        fig = px.bar(
            df,
            x='hour',
            y='count',
            color='source',
            title='Items Processed by Hour',
            labels={'count': 'Items', 'hour': 'Time'},
            color_discrete_map={
                'gmail': '#EA4335',
                'fireflies': '#FF6F00',
                'google_drive': '#4285F4'
            }
        )
        
        fig.update_layout(
            xaxis_tickformat='%H:%M',
            showlegend=True,
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_source_activity_chart(self, source_data: Dict[str, Any]):
        """Render activity chart for a single source."""
        activity = source_data.get('activity_24h', [])
        
        if not activity:
            st.info("No activity in the last 24 hours")
            return
        
        # Create DataFrame
        df = pd.DataFrame(activity)
        df['hour'] = pd.to_datetime(df['hour'])
        
        # Create line chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['hour'],
            y=df['count'],
            mode='lines+markers',
            name='Items Processed',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Items',
            xaxis_tickformat='%H:%M',
            showlegend=False,
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_sync_history(self, history: List[Dict[str, Any]]):
        """Render sync history table."""
        if not history:
            st.info("No sync history available")
            return
        
        # Create DataFrame
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Format for display
        df['Time'] = df['timestamp'].dt.strftime('%H:%M:%S')
        df['Status'] = df['status'].str.title()
        df['Items'] = df['items']
        
        # Display table
        st.dataframe(
            df[['Time', 'Status', 'Items']],
            use_container_width=True,
            hide_index=True
        )
    
    def _render_error_summary(self, errors: Dict[str, List[Dict[str, Any]]]):
        """Render error summary."""
        for source_type, error_list in errors.items():
            if error_list:
                with st.expander(f"{source_type.title()} Errors ({len(error_list)})"):
                    for error in error_list[:5]:  # Show max 5 errors
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.caption(error['timestamp'][:19])
                        with col2:
                            st.error(error['error'][:200])  # Truncate long errors
    
    async def _handle_sync_all(self):
        """Handle sync all sources."""
        with st.spinner("Syncing all sources..."):
            try:
                results = await self.controls.sync_all()
                
                # Show results
                for source_type, result in results.items():
                    if result.errors:
                        st.error(f"{source_type}: Failed - {result.errors[0]}")
                    else:
                        st.success(f"{source_type}: Processed {result.items_processed} items")
                        
            except Exception as e:
                st.error(f"Sync failed: {str(e)}")
    
    async def _handle_sync_source(self, source_type: SourceType):
        """Handle sync single source."""
        with st.spinner(f"Syncing {source_type.value}..."):
            try:
                result = await self.controls.sync_source(source_type)
                
                if result.errors:
                    st.error(f"Sync failed: {result.errors[0]}")
                else:
                    st.success(f"Processed {result.items_processed} items")
                    
            except Exception as e:
                st.error(f"Sync failed: {str(e)}")
    
    async def _auto_refresh(self):
        """Auto-refresh logic."""
        # Wait 30 seconds before refresh
        await asyncio.sleep(30)
        if st.session_state.data_source_refresh:
            st.rerun()