"""
Ansera Monitoring Dashboard - Streamlit UI

This module provides a real-time monitoring dashboard for Ansera
background processes, system metrics, and queue status.
"""

import streamlit as st
import time
import asyncio
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any

# Import our monitoring modules
from .metrics import SystemMonitor
from .process_manager import QueueMonitor
from .controls import ProcessController, get_controller
from .scheduling.schedule_manager import ScheduleManager
from .ui.scheduling_ui import SchedulingUI
from .ui.parameter_adjustment_ui import ParameterAdjustmentUI
from .ui.queue_control_ui import QueueControlUI
from .ui.dependency_management_ui import DependencyManagementUI
from .ui.pm2_config_editor_ui import PM2ConfigEditorUI
from .ui.pm2_log_viewer_ui import PM2LogViewerUI
from .ui.toast_notifications_ui import get_toast_ui
from .ui.email_notification_ui import get_email_notification_ui
from .ui.push_notification_ui import get_push_notification_ui
from .ui.event_config_ui import get_event_configuration_ui
from .ui.streaming_ui import StreamingUI
from .ui.connection_monitor_ui import get_connection_monitor_ui
from .mcp.mcp_metrics_ui import MCPMetricsUI
from .qdrant.qdrant_ui import QdrantManagementUI
from .performance.performance_ui import QueryPerformanceUI
from .pool.pool_ui import ConnectionPoolUI
from .layout.layout_ui import CustomizableDashboardUI
from .services.enhanced_controller import get_enhanced_controller
from .notifications.toast_manager import toast_success, toast_info, toast_warning, toast_error
from .notifications.email_service import send_error_email, send_warning_email, send_info_email
from .notifications.push_service import send_push_error, send_push_warning, send_push_info
from .data_sources import DataSourceMonitoringUI, DataSourceMetrics, DataSourceControls
from .datasources_config_ui import render_datasources_config


# Page configuration
st.set_page_config(
    page_title="Ansera System Monitor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize monitors
@st.cache_resource
def init_monitors():
    """Initialize monitoring instances (cached)."""
    system_monitor = SystemMonitor()
    queue_monitor = QueueMonitor()
    process_controller = get_controller()
    schedule_manager = ScheduleManager()
    scheduling_ui = SchedulingUI(schedule_manager)
    enhanced_controller = get_enhanced_controller()
    parameter_ui = ParameterAdjustmentUI()
    queue_control_ui = QueueControlUI()
    dependency_ui = DependencyManagementUI()
    pm2_config_ui = PM2ConfigEditorUI()
    pm2_log_ui = PM2LogViewerUI()
    toast_ui = get_toast_ui()
    email_ui = get_email_notification_ui()
    push_ui = get_push_notification_ui()
    event_config_ui = get_event_configuration_ui()
    streaming_ui = StreamingUI()
    connection_monitor_ui = get_connection_monitor_ui()
    return system_monitor, queue_monitor, process_controller, schedule_manager, scheduling_ui, enhanced_controller, parameter_ui, queue_control_ui, dependency_ui, pm2_config_ui, pm2_log_ui, toast_ui, email_ui, push_ui, event_config_ui, streaming_ui, connection_monitor_ui

system_monitor, queue_monitor, process_controller, schedule_manager, scheduling_ui, enhanced_controller, parameter_ui, queue_control_ui, dependency_ui, pm2_config_ui, pm2_log_ui, toast_ui, email_ui, push_ui, event_config_ui, streaming_ui, connection_monitor_ui = init_monitors()


def main():
    """Main dashboard application."""
    
    # Toast notification container (render at top of page)
    toast_ui.render_toast_container()
    
    # Header
    st.title("🔍 Ansera System Monitor")
    st.caption(f"Real-time monitoring dashboard - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Dashboard Controls")
        
        # Refresh settings
        auto_refresh = st.checkbox("Auto Refresh", value=True)
        refresh_interval = st.slider("Refresh Interval (seconds)", 1, 30, 5)
        
        # Manual refresh button
        if st.button("🔄 Refresh Now"):
            st.rerun()
        
        st.divider()
        
        # Process controls
        st.header("Process Control")
        
        # Check PM2 status
        pm2_status = process_controller.get_pm2_status()
        
        if pm2_status.get('pm2_available'):
            st.info(f"🚀 PM2 is managing {pm2_status['total_count']} Ansera services")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("▶️ Start All", use_container_width=True):
                    with st.spinner("Starting all services..."):
                        result = process_controller.start_all_services()
                        if result['status'] == 'success':
                            st.success(result['message'])
                            toast_success("Services Started", result['message'], source="dashboard", category="process_control")
                        else:
                            st.error(result['message'])
                            toast_error("Start Failed", result['message'], source="dashboard", category="process_control")
                            # Send email notification for critical failure
                            if st.session_state.get('email_dashboard_enabled', False):
                                asyncio.create_task(send_error_email(
                                    "Service Start Failed", 
                                    result['message'], 
                                    source="dashboard", 
                                    category="process_control"
                                ))
                            # Send push notification for critical failure
                            if st.session_state.get('push_dashboard_enabled', False):
                                asyncio.create_task(send_push_error(
                                    "Service Start Failed", 
                                    result['message'], 
                                    source="dashboard", 
                                    category="process_control"
                                ))
            
            with col2:
                if st.button("⏹️ Stop All", use_container_width=True):
                    if st.checkbox("Confirm stop all services"):
                        with st.spinner("Stopping all services..."):
                            result = process_controller.stop_all_services()
                            if result['status'] == 'success':
                                st.success(result['message'])
                                toast_info("Services Stopped", result['message'], source="dashboard", category="process_control")
                            else:
                                st.error(result['message'])
                                toast_error("Stop Failed", result['message'], source="dashboard", category="process_control")
                                # Send email notification for critical failure
                                if st.session_state.get('email_dashboard_enabled', False):
                                    asyncio.create_task(send_error_email(
                                        "Service Stop Failed", 
                                        result['message'], 
                                        source="dashboard", 
                                        category="process_control"
                                    ))
                                # Send push notification for critical failure
                                if st.session_state.get('push_dashboard_enabled', False):
                                    asyncio.create_task(send_push_error(
                                        "Service Stop Failed", 
                                        result['message'], 
                                        source="dashboard", 
                                        category="process_control"
                                    ))
            
            with col3:
                if st.button("🔄 Restart MCP", use_container_width=True):
                    with st.spinner("Restarting MCP Server..."):
                        result = process_controller.restart_mcp_server()
                        if result['status'] == 'success':
                            st.success(result['message'])
                            toast_success("MCP Restarted", result['message'], source="dashboard", category="process_control")
                        else:
                            st.error(result['message'])
                            toast_error("MCP Restart Failed", result['message'], source="dashboard", category="process_control")
                            # Send email notification for critical failure
                            if st.session_state.get('email_dashboard_enabled', False):
                                asyncio.create_task(send_error_email(
                                    "MCP Server Restart Failed", 
                                    result['message'], 
                                    source="dashboard", 
                                    category="process_control"
                                ))
                            # Send push notification for critical failure
                            if st.session_state.get('push_dashboard_enabled', False):
                                asyncio.create_task(send_push_error(
                                    "MCP Server Restart Failed", 
                                    result['message'], 
                                    source="dashboard", 
                                    category="process_control"
                                ))
        else:
            st.warning("PM2 not available - using manual process control")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Restart MCP", use_container_width=True):
                    with st.spinner("Restarting MCP Server..."):
                        result = process_controller.restart_mcp_server()
                        if result['status'] == 'success':
                            st.success(result['message'])
                            toast_success("MCP Restarted", result['message'], source="dashboard", category="process_control")
                        else:
                            st.error(result['message'])
                            toast_error("MCP Restart Failed", result['message'], source="dashboard", category="process_control")
                            # Send email notification for critical failure
                            if st.session_state.get('email_dashboard_enabled', False):
                                asyncio.create_task(send_error_email(
                                    "MCP Server Restart Failed (Manual)", 
                                    result['message'], 
                                    source="dashboard", 
                                    category="process_control"
                                ))
                            # Send push notification for critical failure
                            if st.session_state.get('push_dashboard_enabled', False):
                                asyncio.create_task(send_push_error(
                                    "MCP Server Restart Failed (Manual)", 
                                    result['message'], 
                                    source="dashboard", 
                                    category="process_control"
                                ))
            
            with col2:
                pass  # Placeholder for alignment
        
        # Queue controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Queue", use_container_width=True):
                if st.checkbox("Confirm clear queue"):
                    queue_monitor.reset_queue()
                    st.success("Queue cleared")
                    toast_info("Queue Cleared", "All queue items have been removed", source="dashboard", category="queue_management")
        
        with col2:
            if st.button("📥 Export Logs", use_container_width=True):
                with st.spinner("Exporting logs..."):
                    result = process_controller.export_logs()
                    if result['status'] == 'success':
                        st.success(f"Logs exported: {result['filename']} ({result['size'] / 1024:.1f} KB)")
                        toast_success("Logs Exported", f"Logs exported: {result['filename']} ({result['size'] / 1024:.1f} KB)", source="dashboard", category="log_management")
                        # Could add download button here in future
                    else:
                        st.error(result['message'])
                        toast_error("Export Failed", result['message'], source="dashboard", category="log_management")
        
        st.divider()
        
        # Display settings
        st.header("Display Settings")
        show_detailed_processes = st.checkbox("Show Detailed Processes", value=True)
        show_queue_history = st.checkbox("Show Queue History", value=False)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13, tab14, tab15, tab16 = st.tabs(["📊 System Overview", "📅 Scheduling", "🎛️ Service Control", "📦 Queue Control", "🔗 Dependencies", "📈 Analytics", "🔔 Notifications", "📡 Streaming", "🔌 Connections", "🖥️ MCP Metrics", "🗃️ Qdrant", "⚡ Performance", "🏊 Connection Pools", "🎨 Layout", "📊 Data Sources", "🔧 Configuration"])
    
    with tab1:
        # System Overview Tab
        # System metrics row
        metrics_container = st.container()
        with metrics_container:
            st.header("System Metrics")
        
        # Get current metrics
        system_metrics = system_monitor.get_quick_stats()
        
        # Create metric columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # CPU metric with delta
            cpu_percent = system_metrics['cpu']
            cpu_delta = cpu_percent - 50  # Compare to 50% baseline
            st.metric(
                label="CPU Usage",
                value=f"{cpu_percent}%",
                delta=f"{cpu_delta:+.1f}%",
                delta_color="inverse"
            )
        
        with col2:
            # Memory metric
            memory = system_metrics['memory']
            st.metric(
                label="Memory",
                value=f"{memory['used_gb']:.1f}GB / {memory['total_gb']:.1f}GB",
                delta=f"{memory['percent']:.1f}%",
                delta_color="inverse"
            )
        
        with col3:
            # Disk metric
            disk = system_metrics['disk']
            st.metric(
                label="Disk Usage",
                value=f"{disk['percent']:.1f}%",
                delta=f"{disk['used_gb']:.0f}GB used",
                delta_color="inverse"
            )
        
        with col4:
            # Qdrant status
            qdrant = system_metrics['qdrant']
            status_emoji = "✅" if qdrant['status'] == 'healthy' else "❌"
            st.metric(
                label="Qdrant Status",
                value=f"{status_emoji} {qdrant['status'].title()}",
                delta=f"{qdrant['documents']} documents"
            )
    
    # Process monitoring section
    st.header("Active Processes")
    
    process_container = st.container()
    with process_container:
        # Check if PM2 is available
        pm2_status = process_controller.get_pm2_status()
        
        if pm2_status.get('pm2_available') and pm2_status['processes']:
            # Show PM2-managed processes
            st.subheader("PM2-Managed Services")
            
            pm2_data = []
            for proc in pm2_status['processes']:
                pm2_data.append({
                    "Service": proc['name'],
                    "Status": proc['status'].upper(),
                    "CPU %": f"{proc['cpu']}%",
                    "Memory": f"{proc['memory'] / (1024*1024):.1f} MB",
                    "Uptime": f"{proc['uptime'] / 1000 / 60:.0f} min" if proc['uptime'] else "0 min",
                    "Restarts": proc['restarts']
                })
            
            st.dataframe(
                pm2_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.TextColumn(
                        "Status",
                        help="Process status",
                        width="small"
                    ),
                    "CPU %": st.column_config.TextColumn(
                        "CPU %",
                        width="small"
                    ),
                    "Memory": st.column_config.TextColumn(
                        "Memory",
                        width="small"
                    ),
                    "Uptime": st.column_config.TextColumn(
                        "Uptime",
                        width="small"
                    ),
                    "Restarts": st.column_config.NumberColumn(
                        "Restarts",
                        width="small"
                    )
                }
            )
        
        # Also show system processes
        processes = system_monitor.get_ansera_processes()
        
        if processes:
            if pm2_status.get('pm2_available'):
                st.subheader("Other System Processes")
            
            if show_detailed_processes:
                # Detailed table view
                process_data = []
                for proc in processes:
                    process_data.append({
                        "PID": proc['pid'],
                        "Name": proc['name'],
                        "CPU %": f"{proc['cpu_percent']:.1f}%",
                        "Memory %": f"{proc['memory_percent']:.1f}%",
                        "Status": proc['status'],
                        "Command": proc.get('cmdline', '')[:80] + '...'
                    })
                
                st.dataframe(
                    process_data,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Status": st.column_config.TextColumn(
                            "Status",
                            help="Process status",
                            width="small"
                        ),
                        "CPU %": st.column_config.TextColumn(
                            "CPU %",
                            width="small"
                        ),
                        "Memory %": st.column_config.TextColumn(
                            "Memory %",
                            width="small"
                        )
                    }
                )
            else:
                # Simple view
                st.info(f"🔄 {len(processes)} Ansera processes running")
        elif not pm2_status.get('pm2_available'):
            st.warning("No Ansera processes detected")
    
    # Queue monitoring section
    st.header("Document Processing Queue")
    
    queue_container = st.container()
    with queue_container:
        # Get queue metrics
        queue_metrics = queue_monitor.get_queue_metrics()
        
        # Queue status columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="⏳ Pending",
                value=queue_metrics['pending'],
                delta=None
            )
        
        with col2:
            st.metric(
                label="🔄 Processing",
                value=queue_metrics['processing'],
                delta=None
            )
        
        with col3:
            st.metric(
                label="✅ Completed",
                value=queue_metrics['completed'],
                delta=f"{queue_metrics['processing_rate']:.1f} docs/min"
            )
        
        with col4:
            st.metric(
                label="❌ Failed",
                value=queue_metrics['failed'],
                delta=None
            )
        
        # Queue health indicator
        health_color = {
            'healthy': '🟢',
            'warning': '🟡', 
            'critical': '🔴'
        }
        st.caption(f"Queue Health: {health_color.get(queue_metrics['queue_health'], '�')} {queue_metrics['queue_health'].upper()}")
        
        # Average processing time
        if queue_metrics['average_processing_time'] > 0:
            st.caption(f"Average Processing Time: {queue_metrics['average_processing_time']:.1f} seconds")
    
    # Queue history (optional)
    if show_queue_history:
        st.header("Recent Jobs")
        
        recent_jobs = queue_monitor.get_recent_jobs(limit=10)
        if recent_jobs:
            job_data = []
            for job in recent_jobs:
                job_data.append({
                    "Job ID": job['job_id'],
                    "Document": job['document_path'].split('/')[-1],
                    "Status": job['status'].upper(),
                    "Started": job.get('started_at', 'N/A')
                })
            
            st.dataframe(job_data, use_container_width=True, hide_index=True)
        else:
            st.info("No recent jobs to display")
    
    # Data Sources Summary
    st.header("Data Sources Overview")
    
    try:
        # Get data source metrics
        from .widgets.gmail_widget import get_gmail_metrics
        from .widgets.fireflies_widget import get_fireflies_metrics
        from .widgets.googledrive_widget import get_googledrive_metrics
        
        # Create columns for data sources
        ds_col1, ds_col2, ds_col3 = st.columns(3)
        
        with ds_col1:
            gmail_metrics = get_gmail_metrics()
            status_icon = "✅" if gmail_metrics['connected'] else "❌"
            st.metric(
                f"{status_icon} Gmail",
                f"{gmail_metrics['items_processed']} emails",
                f"Last: {gmail_metrics['last_sync']}"
            )
            if gmail_metrics['errors'] > 0:
                st.caption(f"⚠️ {gmail_metrics['errors']} errors")
        
        with ds_col2:
            fireflies_metrics = get_fireflies_metrics()
            status_icon = "✅" if fireflies_metrics['connected'] else "❌"
            st.metric(
                f"{status_icon} Fireflies",
                f"{fireflies_metrics['items_processed']} transcripts",
                f"Last: {fireflies_metrics['last_sync']}"
            )
            if fireflies_metrics['errors'] > 0:
                st.caption(f"⚠️ {fireflies_metrics['errors']} errors")
        
        with ds_col3:
            gdrive_metrics = get_googledrive_metrics()
            status_icon = "✅" if gdrive_metrics['connected'] else "❌"
            st.metric(
                f"{status_icon} Google Drive",
                f"{gdrive_metrics['items_processed']} files",
                f"Last: {gdrive_metrics['last_sync']}"
            )
            if gdrive_metrics['errors'] > 0:
                st.caption(f"⚠️ {gdrive_metrics['errors']} errors")
        
        # Quick link to full data sources tab
        if st.button("View All Data Sources →", key="view_data_sources"):
            st.info("Navigate to the 'Data Sources' tab for detailed monitoring")
            
    except Exception as e:
        st.info("Data sources not configured")
    
    # Performance charts
    with st.expander("Performance Charts", expanded=True):
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # CPU/Memory trend chart (placeholder)
            st.subheader("System Resources Trend")
            
            # Create sample data for demonstration
            # In real implementation, this would come from historical data
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(10)),
                y=[45, 48, 52, 49, 51, 55, 53, 50, 48, 46],
                mode='lines',
                name='CPU %',
                line=dict(color='rgb(255, 127, 14)')
            ))
            fig.add_trace(go.Scatter(
                x=list(range(10)),
                y=[30, 32, 31, 33, 35, 34, 36, 35, 33, 32],
                mode='lines',
                name='Memory %',
                line=dict(color='rgb(44, 160, 44)')
            ))
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis_title="Time",
                yaxis_title="Usage %"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            # Queue status pie chart
            st.subheader("Queue Distribution")
            
            queue_data = {
                'Status': ['Pending', 'Processing', 'Completed', 'Failed'],
                'Count': [
                    queue_metrics['pending'],
                    queue_metrics['processing'],
                    queue_metrics['completed'],
                    queue_metrics['failed']
                ]
            }
            
            fig = px.pie(
                queue_data,
                values='Count',
                names='Status',
                color_discrete_map={
                    'Pending': '#FFA500',
                    'Processing': '#1E90FF',
                    'Completed': '#32CD32',
                    'Failed': '#FF6347'
                }
            )
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Scheduling Tab
        scheduling_ui.render_scheduling_tab()
    
    with tab3:
        # Service Control Tab
        st.header("🎛️ Service Control Center")
        
        # Sub-tabs for service control
        service_subtabs = st.tabs(["Parameter Control", "PM2 Configuration", "PM2 Logs"])
        
        with service_subtabs[0]:
            parameter_ui.render_parameter_tab()
        
        with service_subtabs[1]:
            pm2_config_ui.render_pm2_config_tab()
        
        with service_subtabs[2]:
            pm2_log_ui.render_pm2_logs_tab()
    
    with tab4:
        # Queue Control Tab
        queue_control_ui.render_queue_control_tab()
    
    with tab5:
        # Dependencies Tab
        dependency_ui.render_dependency_tab()
    
    with tab6:
        # Analytics Tab
        st.header("📈 Analytics & Insights")
        st.info("Analytics features coming soon! This will include:")
        st.markdown("""
        - Processing trends and patterns
        - Resource utilization analysis
        - Performance metrics over time
        - Predictive insights
        - Cost analysis
        """)
    
    with tab7:
        # Notifications Tab
        st.header("🔔 Notification Center")
        
        # Notification sub-tabs
        notification_subtabs = st.tabs(["Toast Notifications", "Email Notifications", "Push Notifications", "Event Configuration"])
        
        with notification_subtabs[0]:
            toast_ui.render_notification_panel()
        
        with notification_subtabs[1]:
            email_ui.render_email_notification_tab()
        
        with notification_subtabs[2]:
            push_ui.render_push_notification_tab()
        
        with notification_subtabs[3]:
            event_config_ui.render_event_configuration_tab()
    
    with tab8:
        # Streaming Tab
        streaming_ui.render()
    
    with tab9:
        # Connection Monitor Tab
        connection_monitor_ui.render()
    
    with tab10:
        # MCP Metrics Tab
        mcp_metrics_ui = MCPMetricsUI()
        mcp_metrics_ui.render()
    
    with tab11:
        # Qdrant Management Tab
        qdrant_ui = QdrantManagementUI()
        qdrant_ui.render()
    
    with tab12:
        # Query Performance Tab
        performance_ui = QueryPerformanceUI()
        performance_ui.render()
    
    with tab13:
        # Connection Pool Tab
        pool_ui = ConnectionPoolUI()
        pool_ui.render()
    
    with tab14:
        # Layout Customization Tab
        layout_ui = CustomizableDashboardUI()
        layout_ui.render()
    
    with tab15:
        # Data Sources Tab
        data_source_ui = DataSourceMonitoringUI(
            metrics=DataSourceMetrics(),
            controls=DataSourceControls()
        )
        data_source_ui.render()
    
    with tab16:
        # Configuration Tab
        render_datasources_config()
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


def run_dashboard():
    """Entry point for the dashboard."""
    main()


if __name__ == "__main__":
    run_dashboard()