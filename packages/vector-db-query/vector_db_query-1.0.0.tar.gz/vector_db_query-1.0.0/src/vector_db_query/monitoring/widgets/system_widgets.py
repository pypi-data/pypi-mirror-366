"""
System monitoring widgets for dashboard display.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .base_widget import BaseWidget, WidgetConfig
from ..layout.models import WidgetType, WidgetSize
from ..metrics import SystemMonitor
from ..process_manager import QueueMonitor
from ..controls import get_controller


class SystemOverviewWidget(BaseWidget):
    """Widget displaying system overview metrics."""
    
    widget_type = WidgetType.SYSTEM_OVERVIEW
    widget_name = "System Overview"
    widget_description = "Shows CPU, memory, disk usage and system health"
    widget_icon = "🖥️"
    widget_category = "System"
    default_size = WidgetSize.MEDIUM
    
    config_schema = {
        'show_cpu': {'type': 'boolean', 'default': True, 'description': 'Show CPU metrics'},
        'show_memory': {'type': 'boolean', 'default': True, 'description': 'Show memory metrics'},
        'show_disk': {'type': 'boolean', 'default': True, 'description': 'Show disk metrics'},
        'show_qdrant': {'type': 'boolean', 'default': True, 'description': 'Show Qdrant status'},
        'metric_style': {'type': 'select', 'options': ['cards', 'chart', 'compact'], 'default': 'cards', 'description': 'Display style'}
    }
    
    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.system_monitor = SystemMonitor()
    
    def _render_content(self) -> None:
        """Render system overview content."""
        try:
            # Get system metrics
            metrics = self.system_monitor.get_quick_stats()
            
            # Get display preferences
            show_cpu = self.config.config.get('show_cpu', True)
            show_memory = self.config.config.get('show_memory', True)
            show_disk = self.config.config.get('show_disk', True)
            show_qdrant = self.config.config.get('show_qdrant', True)
            metric_style = self.config.config.get('metric_style', 'cards')
            
            if metric_style == 'cards':
                self._render_metric_cards(metrics, show_cpu, show_memory, show_disk, show_qdrant)
            elif metric_style == 'chart':
                self._render_metric_chart(metrics, show_cpu, show_memory, show_disk)
            else:  # compact
                self._render_compact_metrics(metrics, show_cpu, show_memory, show_disk, show_qdrant)
                
        except Exception as e:
            st.error(f"Failed to load system metrics: {e}")
    
    def _render_metric_cards(self, metrics: Dict[str, Any], show_cpu: bool, show_memory: bool, show_disk: bool, show_qdrant: bool) -> None:
        """Render metrics as cards."""
        cols = []
        if show_cpu:
            cols.append('cpu')
        if show_memory:
            cols.append('memory')
        if show_disk:
            cols.append('disk')
        if show_qdrant:
            cols.append('qdrant')
        
        if not cols:
            st.info("No metrics selected for display")
            return
        
        columns = st.columns(len(cols))
        
        for i, metric_type in enumerate(cols):
            with columns[i]:
                if metric_type == 'cpu':
                    cpu_percent = metrics['cpu']
                    delta_color = "inverse" if cpu_percent > 80 else "normal"
                    st.metric(
                        label="CPU Usage",
                        value=f"{cpu_percent}%",
                        delta=f"{cpu_percent - 50:+.1f}%",
                        delta_color=delta_color
                    )
                
                elif metric_type == 'memory':
                    memory = metrics['memory']
                    st.metric(
                        label="Memory",
                        value=f"{memory['used_gb']:.1f}GB",
                        delta=f"{memory['percent']:.1f}% used"
                    )
                
                elif metric_type == 'disk':
                    disk = metrics['disk']
                    delta_color = "inverse" if disk['percent'] > 90 else "normal"
                    st.metric(
                        label="Disk Usage",
                        value=f"{disk['percent']:.1f}%",
                        delta=f"{disk['used_gb']:.0f}GB used",
                        delta_color=delta_color
                    )
                
                elif metric_type == 'qdrant':
                    qdrant = metrics['qdrant']
                    status_emoji = "✅" if qdrant['status'] == 'healthy' else "❌"
                    st.metric(
                        label="Qdrant",
                        value=f"{status_emoji} {qdrant['status'].title()}",
                        delta=f"{qdrant['documents']} docs"
                    )
    
    def _render_metric_chart(self, metrics: Dict[str, Any], show_cpu: bool, show_memory: bool, show_disk: bool) -> None:
        """Render metrics as a chart."""
        chart_data = []
        
        if show_cpu:
            chart_data.append({'Metric': 'CPU', 'Usage %': metrics['cpu'], 'Color': '#FF6B6B'})
        
        if show_memory:
            chart_data.append({'Metric': 'Memory', 'Usage %': metrics['memory']['percent'], 'Color': '#4ECDC4'})
        
        if show_disk:
            chart_data.append({'Metric': 'Disk', 'Usage %': metrics['disk']['percent'], 'Color': '#45B7D1'})
        
        if chart_data:
            df = pd.DataFrame(chart_data)
            
            fig = px.bar(
                df,
                x='Metric',
                y='Usage %',
                color='Metric',
                color_discrete_map={row['Metric']: row['Color'] for row in chart_data},
                title="System Resource Usage"
            )
            
            fig.update_layout(
                height=300,
                showlegend=False,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No metrics selected for chart display")
    
    def _render_compact_metrics(self, metrics: Dict[str, Any], show_cpu: bool, show_memory: bool, show_disk: bool, show_qdrant: bool) -> None:
        """Render metrics in compact format."""
        info_lines = []
        
        if show_cpu:
            cpu_status = "🔴" if metrics['cpu'] > 80 else "🟡" if metrics['cpu'] > 60 else "🟢"
            info_lines.append(f"{cpu_status} **CPU**: {metrics['cpu']}%")
        
        if show_memory:
            memory = metrics['memory']
            memory_status = "🔴" if memory['percent'] > 90 else "🟡" if memory['percent'] > 75 else "🟢"
            info_lines.append(f"{memory_status} **Memory**: {memory['used_gb']:.1f}GB ({memory['percent']:.1f}%)")
        
        if show_disk:
            disk = metrics['disk']
            disk_status = "🔴" if disk['percent'] > 90 else "🟡" if disk['percent'] > 75 else "🟢"
            info_lines.append(f"{disk_status} **Disk**: {disk['percent']:.1f}% ({disk['used_gb']:.0f}GB)")
        
        if show_qdrant:
            qdrant = metrics['qdrant']
            qdrant_status = "✅" if qdrant['status'] == 'healthy' else "❌"
            info_lines.append(f"{qdrant_status} **Qdrant**: {qdrant['status']} ({qdrant['documents']} docs)")
        
        if info_lines:
            for line in info_lines:
                st.markdown(line)
        else:
            st.info("No metrics selected for display")
    
    def get_config_ui(self) -> Dict[str, Any]:
        """Get configuration UI for system overview widget."""
        config_values = super().get_config_ui()
        
        # Widget-specific configuration
        with st.expander("System Overview Settings"):
            config_values['show_cpu'] = st.checkbox(
                "Show CPU Metrics",
                value=self.config.config.get('show_cpu', True),
                key=f"config_show_cpu_{self.config.widget_id}"
            )
            
            config_values['show_memory'] = st.checkbox(
                "Show Memory Metrics",
                value=self.config.config.get('show_memory', True),
                key=f"config_show_memory_{self.config.widget_id}"
            )
            
            config_values['show_disk'] = st.checkbox(
                "Show Disk Metrics",
                value=self.config.config.get('show_disk', True),
                key=f"config_show_disk_{self.config.widget_id}"
            )
            
            config_values['show_qdrant'] = st.checkbox(
                "Show Qdrant Status",
                value=self.config.config.get('show_qdrant', True),
                key=f"config_show_qdrant_{self.config.widget_id}"
            )
            
            config_values['metric_style'] = st.selectbox(
                "Display Style",
                options=['cards', 'chart', 'compact'],
                index=['cards', 'chart', 'compact'].index(self.config.config.get('metric_style', 'cards')),
                key=f"config_metric_style_{self.config.widget_id}"
            )
        
        return config_values


class ProcessControlWidget(BaseWidget):
    """Widget for controlling system processes."""
    
    widget_type = WidgetType.PROCESS_CONTROL
    widget_name = "Process Control"
    widget_description = "Start, stop, and restart system services"
    widget_icon = "🎛️"
    widget_category = "Control"
    default_size = WidgetSize.MEDIUM
    
    config_schema = {
        'show_pm2_controls': {'type': 'boolean', 'default': True, 'description': 'Show PM2 controls'},
        'show_service_status': {'type': 'boolean', 'default': True, 'description': 'Show service status'},
        'confirm_actions': {'type': 'boolean', 'default': True, 'description': 'Require confirmation for dangerous actions'}
    }
    
    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.process_controller = get_controller()
    
    def _render_content(self) -> None:
        """Render process control content."""
        try:
            show_pm2_controls = self.config.config.get('show_pm2_controls', True)
            show_service_status = self.config.config.get('show_service_status', True)
            confirm_actions = self.config.config.get('confirm_actions', True)
            
            # Get PM2 status
            pm2_status = self.process_controller.get_pm2_status()
            
            if show_service_status:
                self._render_service_status(pm2_status)
            
            if show_pm2_controls:
                self._render_pm2_controls(pm2_status, confirm_actions)
                
        except Exception as e:
            st.error(f"Failed to load process control: {e}")
    
    def _render_service_status(self, pm2_status: Dict[str, Any]) -> None:
        """Render service status display."""
        if pm2_status.get('pm2_available'):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("PM2 Status", "🟢 Available")
            
            with col2:
                st.metric("Total Services", pm2_status['total_count'])
            
            with col3:
                running_count = sum(1 for p in pm2_status['processes'] if p['status'] == 'online')
                st.metric("Running", running_count)
        else:
            st.warning("🔴 PM2 not available")
    
    def _render_pm2_controls(self, pm2_status: Dict[str, Any], confirm_actions: bool) -> None:
        """Render PM2 control buttons."""
        if not pm2_status.get('pm2_available'):
            st.info("PM2 controls unavailable")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ Start All", key=f"start_all_{self.config.widget_id}", use_container_width=True):
                if not confirm_actions or st.session_state.get(f'confirm_start_{self.config.widget_id}', False):
                    with st.spinner("Starting services..."):
                        result = self.process_controller.start_all_services()
                        if result['status'] == 'success':
                            st.success(result['message'])
                        else:
                            st.error(result['message'])
                    if confirm_actions:
                        st.session_state[f'confirm_start_{self.config.widget_id}'] = False
                elif confirm_actions:
                    st.session_state[f'confirm_start_{self.config.widget_id}'] = True
                    st.warning("Click again to confirm")
        
        with col2:
            if st.button("⏹️ Stop All", key=f"stop_all_{self.config.widget_id}", use_container_width=True):
                if not confirm_actions or st.session_state.get(f'confirm_stop_{self.config.widget_id}', False):
                    with st.spinner("Stopping services..."):
                        result = self.process_controller.stop_all_services()
                        if result['status'] == 'success':
                            st.success(result['message'])
                        else:
                            st.error(result['message'])
                    if confirm_actions:
                        st.session_state[f'confirm_stop_{self.config.widget_id}'] = False
                elif confirm_actions:
                    st.session_state[f'confirm_stop_{self.config.widget_id}'] = True
                    st.error("Click again to confirm")
        
        with col3:
            if st.button("🔄 Restart MCP", key=f"restart_mcp_{self.config.widget_id}", use_container_width=True):
                with st.spinner("Restarting MCP..."):
                    result = self.process_controller.restart_mcp_server()
                    if result['status'] == 'success':
                        st.success(result['message'])
                    else:
                        st.error(result['message'])
    
    def get_config_ui(self) -> Dict[str, Any]:
        """Get configuration UI for process control widget."""
        config_values = super().get_config_ui()
        
        # Widget-specific configuration
        with st.expander("Process Control Settings"):
            config_values['show_pm2_controls'] = st.checkbox(
                "Show PM2 Controls",
                value=self.config.config.get('show_pm2_controls', True),
                key=f"config_show_pm2_{self.config.widget_id}"
            )
            
            config_values['show_service_status'] = st.checkbox(
                "Show Service Status",
                value=self.config.config.get('show_service_status', True),
                key=f"config_show_status_{self.config.widget_id}"
            )
            
            config_values['confirm_actions'] = st.checkbox(
                "Require Action Confirmation",
                value=self.config.config.get('confirm_actions', True),
                key=f"config_confirm_{self.config.widget_id}"
            )
        
        return config_values


class QueueStatusWidget(BaseWidget):
    """Widget displaying queue status and metrics."""
    
    widget_type = WidgetType.QUEUE_STATUS
    widget_name = "Queue Status"
    widget_description = "Shows document processing queue metrics and status"
    widget_icon = "📦"
    widget_category = "Queue"
    default_size = WidgetSize.MEDIUM
    
    config_schema = {
        'show_metrics': {'type': 'boolean', 'default': True, 'description': 'Show queue metrics'},
        'show_chart': {'type': 'boolean', 'default': True, 'description': 'Show queue distribution chart'},
        'show_controls': {'type': 'boolean', 'default': True, 'description': 'Show queue controls'},
        'chart_type': {'type': 'select', 'options': ['pie', 'bar'], 'default': 'pie', 'description': 'Chart type'}
    }
    
    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self.queue_monitor = QueueMonitor()
    
    def _render_content(self) -> None:
        """Render queue status content."""
        try:
            show_metrics = self.config.config.get('show_metrics', True)
            show_chart = self.config.config.get('show_chart', True)
            show_controls = self.config.config.get('show_controls', True)
            chart_type = self.config.config.get('chart_type', 'pie')
            
            # Get queue metrics
            metrics = self.queue_monitor.get_queue_metrics()
            
            if show_metrics:
                self._render_queue_metrics(metrics)
            
            if show_chart:
                self._render_queue_chart(metrics, chart_type)
            
            if show_controls:
                self._render_queue_controls()
                
        except Exception as e:
            st.error(f"Failed to load queue status: {e}")
    
    def _render_queue_metrics(self, metrics: Dict[str, Any]) -> None:
        """Render queue metrics cards."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("⏳ Pending", metrics['pending'])
        
        with col2:
            st.metric("🔄 Processing", metrics['processing'])
        
        with col3:
            st.metric(
                "✅ Completed",
                metrics['completed'],
                delta=f"{metrics['processing_rate']:.1f} docs/min"
            )
        
        with col4:
            st.metric("❌ Failed", metrics['failed'])
        
        # Queue health indicator
        health_colors = {
            'healthy': '🟢',
            'warning': '🟡',
            'critical': '🔴'
        }
        health_color = health_colors.get(metrics['queue_health'], '⚪')
        st.caption(f"Queue Health: {health_color} {metrics['queue_health'].upper()}")
        
        if metrics['average_processing_time'] > 0:
            st.caption(f"Average Processing Time: {metrics['average_processing_time']:.1f}s")
    
    def _render_queue_chart(self, metrics: Dict[str, Any], chart_type: str) -> None:
        """Render queue distribution chart."""
        queue_data = {
            'Status': ['Pending', 'Processing', 'Completed', 'Failed'],
            'Count': [
                metrics['pending'],
                metrics['processing'],
                metrics['completed'],
                metrics['failed']
            ]
        }
        
        df = pd.DataFrame(queue_data)
        
        if chart_type == 'pie':
            fig = px.pie(
                df,
                values='Count',
                names='Status',
                color_discrete_map={
                    'Pending': '#FFA500',
                    'Processing': '#1E90FF',
                    'Completed': '#32CD32',
                    'Failed': '#FF6347'
                }
            )
        else:  # bar
            fig = px.bar(
                df,
                x='Status',
                y='Count',
                color='Status',
                color_discrete_map={
                    'Pending': '#FFA500',
                    'Processing': '#1E90FF',
                    'Completed': '#32CD32',
                    'Failed': '#FF6347'
                }
            )
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=(chart_type == 'pie')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_queue_controls(self) -> None:
        """Render queue control buttons."""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Queue", key=f"clear_queue_{self.config.widget_id}", use_container_width=True):
                if st.session_state.get(f'confirm_clear_{self.config.widget_id}', False):
                    self.queue_monitor.reset_queue()
                    st.success("Queue cleared")
                    st.session_state[f'confirm_clear_{self.config.widget_id}'] = False
                else:
                    st.session_state[f'confirm_clear_{self.config.widget_id}'] = True
                    st.warning("Click again to confirm")
        
        with col2:
            if st.button("📊 View Details", key=f"queue_details_{self.config.widget_id}", use_container_width=True):
                st.info("Queue details would open in a modal/expander")
    
    def get_config_ui(self) -> Dict[str, Any]:
        """Get configuration UI for queue status widget."""
        config_values = super().get_config_ui()
        
        # Widget-specific configuration
        with st.expander("Queue Status Settings"):
            config_values['show_metrics'] = st.checkbox(
                "Show Queue Metrics",
                value=self.config.config.get('show_metrics', True),
                key=f"config_show_metrics_{self.config.widget_id}"
            )
            
            config_values['show_chart'] = st.checkbox(
                "Show Distribution Chart",
                value=self.config.config.get('show_chart', True),
                key=f"config_show_chart_{self.config.widget_id}"
            )
            
            config_values['show_controls'] = st.checkbox(
                "Show Queue Controls",
                value=self.config.config.get('show_controls', True),
                key=f"config_show_controls_{self.config.widget_id}"
            )
            
            if config_values['show_chart']:
                config_values['chart_type'] = st.selectbox(
                    "Chart Type",
                    options=['pie', 'bar'],
                    index=['pie', 'bar'].index(self.config.config.get('chart_type', 'pie')),
                    key=f"config_chart_type_{self.config.widget_id}"
                )
        
        return config_values