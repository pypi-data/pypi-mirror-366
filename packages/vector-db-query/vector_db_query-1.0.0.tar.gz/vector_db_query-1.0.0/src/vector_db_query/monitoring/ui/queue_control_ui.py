"""
Queue control UI components for the monitoring dashboard.

This module provides Streamlit UI components for controlling
queue processing including pause/resume and scheduling.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from ..services.queue_controller import (
    QueueController, QueueState, PauseMode, PauseSchedule,
    get_queue_controller, get_all_queue_controllers
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class QueueControlUI:
    """
    UI components for queue control and monitoring.
    
    Provides interface for pausing/resuming queues,
    scheduling maintenance windows, and monitoring metrics.
    """
    
    def __init__(self):
        """
        Initialize queue control UI.
        """
        self.change_tracker = get_change_tracker()
        
    def render_queue_control_tab(self):
        """Render the main queue control tab."""
        st.header("📦 Queue Control Center")
        
        # Tab selection
        queue_tabs = st.tabs([
            "Queue Overview",
            "Pause/Resume",
            "Scheduled Maintenance",
            "Queue Metrics",
            "Bulk Operations"
        ])
        
        with queue_tabs[0]:
            self._render_queue_overview()
        
        with queue_tabs[1]:
            self._render_pause_resume()
        
        with queue_tabs[2]:
            self._render_scheduled_maintenance()
        
        with queue_tabs[3]:
            self._render_queue_metrics()
        
        with queue_tabs[4]:
            self._render_bulk_operations()
    
    def _render_queue_overview(self):
        """Render queue overview with status cards."""
        st.subheader("Queue Status Overview")
        
        # Get all queue controllers
        controllers = get_all_queue_controllers()
        
        if not controllers:
            st.info("No active queues found. Queues will appear here once processing starts.")
            
            # Option to initialize default queue
            if st.button("🚀 Initialize Default Queue"):
                default_controller = get_queue_controller("default")
                default_controller.start()
                st.success("Default queue initialized and started")
                st.rerun()
            
            return
        
        # Display queue cards
        cols = st.columns(min(len(controllers), 3))
        
        for idx, (queue_name, controller) in enumerate(controllers.items()):
            col_idx = idx % 3
            
            with cols[col_idx]:
                self._render_queue_card(queue_name, controller)
    
    def _render_queue_card(self, queue_name: str, controller: QueueController):
        """Render a single queue status card."""
        state_info = controller.get_state()
        state = state_info['state']
        metrics = state_info['metrics']
        
        # State-based styling
        if state == 'running':
            status_color = '🟢'  # Green
            status_text = "Running"
        elif state == 'paused':
            status_color = '🟡'  # Yellow
            status_text = "Paused"
        elif state == 'stopped':
            status_color = '🔴'  # Red
            status_text = "Stopped"
        elif state == 'draining':
            status_color = '🟠'  # Orange
            status_text = "Draining"
        else:
            status_color = '⚪'  # White
            status_text = state.title()
        
        # Card container
        with st.container():
            st.markdown(f"### {status_color} {queue_name.title()} Queue")
            
            # Status info
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Status:** {status_text}")
                st.write(f"**Workers:** {state_info['workers']['active']}/{state_info['workers']['total']}")
                
                if state_info['pause_info']['reason']:
                    st.write(f"**Pause Reason:** {state_info['pause_info']['reason']}")
            
            with col2:
                st.metric(
                    "Processed",
                    f"{metrics['items_processed']:,}",
                    delta=f"+{metrics['items_pending']} pending" if metrics['items_pending'] > 0 else None
                )
                
                if metrics['processing_rate'] > 0:
                    st.metric(
                        "Rate",
                        f"{metrics['processing_rate']:.1f}/sec",
                        delta=f"{metrics['average_processing_time']:.2f}s avg" if metrics['average_processing_time'] > 0 else None
                    )
            
            # Quick actions
            action_cols = st.columns(3)
            
            with action_cols[0]:
                if state == 'running':
                    if st.button(f"⏸️ Pause", key=f"pause_{queue_name}"):
                        if controller.pause(PauseMode.GRACEFUL, "Manual pause from dashboard"):
                            st.success(f"Paused {queue_name} queue")
                            st.rerun()
                elif state in ['paused', 'draining']:
                    if st.button(f"▶️ Resume", key=f"resume_{queue_name}"):
                        if controller.resume("Manual resume from dashboard"):
                            st.success(f"Resumed {queue_name} queue")
                            st.rerun()
                elif state == 'stopped':
                    if st.button(f"🚀 Start", key=f"start_{queue_name}"):
                        if controller.start():
                            st.success(f"Started {queue_name} queue")
                            st.rerun()
            
            with action_cols[1]:
                if st.button(f"📈 Details", key=f"details_{queue_name}"):
                    st.session_state[f'show_details_{queue_name}'] = True
            
            with action_cols[2]:
                if state == 'running':
                    if st.button(f"🚫 Stop", key=f"stop_{queue_name}"):
                        if st.session_state.get(f'confirm_stop_{queue_name}'):
                            if controller.stop(graceful=True):
                                st.success(f"Stopped {queue_name} queue")
                                del st.session_state[f'confirm_stop_{queue_name}']
                                st.rerun()
                        else:
                            st.session_state[f'confirm_stop_{queue_name}'] = True
                            st.warning("Click again to confirm stop")
            
            # Show details if requested
            if st.session_state.get(f'show_details_{queue_name}'):
                with st.expander(f"Queue Details - {queue_name}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Current State:**")
                        st.json({
                            'state': state,
                            'workers': state_info['workers'],
                            'pause_info': state_info['pause_info']
                        })
                    
                    with col2:
                        st.write("**Metrics:**")
                        st.json(metrics)
                    
                    # Scheduled pauses
                    if state_info['scheduled_pauses']:
                        st.write("**Scheduled Pauses:**")
                        for schedule in state_info['scheduled_pauses']:
                            status_icon = "🟢" if schedule['is_active'] else "⚪"
                            st.write(f"{status_icon} **{schedule['name']}** - {schedule['pause_time']}")
                    
                    if st.button("Close Details", key=f"close_details_{queue_name}"):
                        del st.session_state[f'show_details_{queue_name}']
                        st.rerun()
            
            st.divider()
    
    def _render_pause_resume(self):
        """Render pause/resume controls."""
        st.subheader("Manual Pause/Resume Control")
        
        # Queue selector
        controllers = get_all_queue_controllers()
        
        if not controllers:
            st.warning("No active queues found. Initialize queues from the Overview tab.")
            return
        
        selected_queue = st.selectbox(
            "Select Queue",
            list(controllers.keys()),
            format_func=lambda x: x.title()
        )
        
        if selected_queue:
            controller = controllers[selected_queue]
            state_info = controller.get_state()
            current_state = state_info['state']
            
            # Current status
            st.write(f"**Current Status:** {current_state.title()}")
            
            if state_info['pause_info']['paused_at']:
                pause_duration = state_info['pause_info']['pause_duration']
                st.write(f"**Paused for:** {pause_duration:.0f} seconds")
                st.write(f"**Pause Reason:** {state_info['pause_info']['reason']}")
            
            # Control actions
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Pause Controls")
                
                if current_state == 'running':
                    # Pause mode selection
                    pause_mode = st.selectbox(
                        "Pause Mode",
                        [mode.value for mode in PauseMode],
                        format_func=lambda x: {
                            'immediate': 'Immediate - Stop now',
                            'graceful': 'Graceful - Finish current tasks',
                            'drain': 'Drain - Process all queued items',
                            'scheduled': 'Scheduled - Pause at specific time'
                        }.get(x, x.title())
                    )
                    
                    reason = st.text_input(
                        "Pause Reason",
                        placeholder="Maintenance, debugging, etc."
                    )
                    
                    if st.button("⏸️ Pause Queue", type="primary"):
                        mode_enum = PauseMode(pause_mode)
                        
                        if controller.pause(mode_enum, reason or "Manual pause"):
                            st.success(f"Paused {selected_queue} queue with {pause_mode} mode")
                            st.rerun()
                        else:
                            st.error("Failed to pause queue")
                
                else:
                    st.info(f"Queue is currently {current_state}. Cannot pause.")
            
            with col2:
                st.write("### Resume Controls")
                
                if current_state in ['paused', 'draining']:
                    resume_reason = st.text_input(
                        "Resume Reason",
                        placeholder="Maintenance complete, issue resolved, etc."
                    )
                    
                    if st.button("▶️ Resume Queue", type="primary"):
                        if controller.resume(resume_reason or "Manual resume"):
                            st.success(f"Resumed {selected_queue} queue")
                            st.rerun()
                        else:
                            st.error("Failed to resume queue")
                
                else:
                    st.info(f"Queue is currently {current_state}. Cannot resume.")
            
            # Emergency controls
            st.write("### Emergency Controls")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if current_state != 'stopped':
                    if st.button("🚫 Emergency Stop", key="emergency_stop"):
                        if st.session_state.get('confirm_emergency_stop'):
                            if controller.stop(graceful=False):
                                st.success("Emergency stop executed")
                                del st.session_state['confirm_emergency_stop']
                                st.rerun()
                        else:
                            st.session_state['confirm_emergency_stop'] = True
                            st.error("Click again to confirm EMERGENCY STOP (immediate halt)")
            
            with col2:
                if current_state == 'stopped':
                    if st.button("🚀 Restart Queue", key="restart_queue"):
                        if controller.start():
                            st.success(f"Restarted {selected_queue} queue")
                            st.rerun()
    
    def _render_scheduled_maintenance(self):
        """Render scheduled maintenance interface."""
        st.subheader("Scheduled Maintenance Windows")
        
        controllers = get_all_queue_controllers()
        
        if not controllers:
            st.warning("No active queues found.")
            return
        
        # Create new schedule
        with st.expander("➕ Schedule New Maintenance Window", expanded=False):
            with st.form("schedule_maintenance_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_queue = st.selectbox(
                        "Queue",
                        list(controllers.keys()),
                        format_func=lambda x: x.title()
                    )
                    
                    schedule_name = st.text_input(
                        "Schedule Name",
                        placeholder="Weekly maintenance"
                    )
                    
                    reason = st.text_area(
                        "Maintenance Reason",
                        placeholder="System updates, backup, cleanup, etc."
                    )
                
                with col2:
                    # Pause time
                    pause_date = st.date_input(
                        "Pause Date",
                        value=datetime.now().date() + timedelta(days=1)
                    )
                    
                    pause_time = st.time_input(
                        "Pause Time",
                        value=datetime.now().replace(hour=2, minute=0, second=0, microsecond=0).time()
                    )
                    
                    # Resume time (optional)
                    auto_resume = st.checkbox("Auto Resume", value=True)
                    
                    if auto_resume:
                        resume_time = st.time_input(
                            "Resume Time",
                            value=datetime.now().replace(hour=6, minute=0, second=0, microsecond=0).time()
                        )
                    
                    # Pause mode
                    pause_mode = st.selectbox(
                        "Pause Mode",
                        [mode.value for mode in PauseMode if mode != PauseMode.SCHEDULED],
                        index=1  # Default to graceful
                    )
                    
                    recurring = st.checkbox("Recurring Schedule")
                
                submitted = st.form_submit_button("Schedule Maintenance")
                
                if submitted and schedule_name and selected_queue:
                    # Combine date and time
                    pause_datetime = datetime.combine(pause_date, pause_time)
                    resume_datetime = None
                    
                    if auto_resume:
                        resume_datetime = datetime.combine(pause_date, resume_time)
                        
                        # Handle case where resume is next day
                        if resume_datetime <= pause_datetime:
                            resume_datetime += timedelta(days=1)
                    
                    # Create schedule
                    schedule = PauseSchedule(
                        id=f"maint_{int(datetime.now().timestamp())}",
                        name=schedule_name,
                        pause_time=pause_datetime,
                        resume_time=resume_datetime,
                        mode=PauseMode(pause_mode),
                        reason=reason or "Scheduled maintenance",
                        recurring=recurring,
                        created_by="dashboard_user"
                    )
                    
                    # Schedule with controller
                    controller = controllers[selected_queue]
                    if controller.schedule_pause(schedule):
                        st.success(f"Scheduled maintenance for {selected_queue} queue")
                        st.rerun()
                    else:
                        st.error("Failed to schedule maintenance")
        
        # Show existing schedules
        st.write("### Active Maintenance Schedules")
        
        for queue_name, controller in controllers.items():
            state_info = controller.get_state()
            schedules = state_info['scheduled_pauses']
            
            if schedules:
                st.write(f"**{queue_name.title()} Queue:**")
                
                for schedule in schedules:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            status_icon = "🟢" if schedule['is_active'] else "⚪"
                            st.write(f"{status_icon} **{schedule['name']}**")
                            st.caption(schedule['reason'])
                        
                        with col2:
                            pause_time = datetime.fromisoformat(schedule['pause_time'])
                            st.write(f"**Pause:** {pause_time.strftime('%Y-%m-%d %H:%M')}")
                            
                            if schedule['resume_time']:
                                resume_time = datetime.fromisoformat(schedule['resume_time'])
                                st.write(f"**Resume:** {resume_time.strftime('%Y-%m-%d %H:%M')}")
                            else:
                                st.write("**Resume:** Manual")
                        
                        with col3:
                            if st.button("🗿 Cancel", key=f"cancel_{schedule['id']}"):
                                if controller.cancel_scheduled_pause(schedule['id']):
                                    st.success("Cancelled scheduled maintenance")
                                    st.rerun()
                        
                        st.divider()
            else:
                st.write(f"**{queue_name.title()} Queue:** No scheduled maintenance")
    
    def _render_queue_metrics(self):
        """Render queue metrics and analytics."""
        st.subheader("Queue Performance Metrics")
        
        controllers = get_all_queue_controllers()
        
        if not controllers:
            st.warning("No active queues found.")
            return
        
        # Queue selector for detailed metrics
        selected_queue = st.selectbox(
            "Select Queue for Detailed Metrics",
            list(controllers.keys()),
            format_func=lambda x: x.title()
        )
        
        if selected_queue:
            controller = controllers[selected_queue]
            state_info = controller.get_state()
            metrics = state_info['metrics']
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Items Processed",
                    f"{metrics['items_processed']:,}",
                    delta=f"+{metrics['items_pending']} pending" if metrics['items_pending'] > 0 else None
                )
            
            with col2:
                st.metric(
                    "Processing Rate",
                    f"{metrics['processing_rate']:.1f}/sec",
                    delta=f"{metrics['average_processing_time']:.2f}s avg"
                )
            
            with col3:
                st.metric(
                    "Items Failed",
                    f"{metrics['items_failed']:,}",
                    delta=f"{(metrics['items_failed'] / max(metrics['items_processed'], 1) * 100):.1f}% rate"
                )
            
            with col4:
                if metrics['last_activity']:
                    last_activity = datetime.fromisoformat(metrics['last_activity'])
                    time_since = (datetime.now() - last_activity).total_seconds()
                    st.metric(
                        "Last Activity",
                        f"{time_since:.0f}s ago",
                        delta="Active" if time_since < 60 else "Idle"
                    )
                else:
                    st.metric("Last Activity", "Never")
            
            # Historical charts (mock data for demonstration)
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Processing Rate Over Time")
                
                # Generate mock time series data
                import numpy as np
                hours = list(range(24))
                rates = np.random.normal(metrics['processing_rate'], metrics['processing_rate'] * 0.2, 24)
                rates = np.maximum(rates, 0)  # Ensure non-negative
                
                fig = px.line(
                    x=hours,
                    y=rates,
                    title="Items per Second",
                    labels={'x': 'Hour of Day', 'y': 'Processing Rate'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("### Queue Status Distribution")
                
                # Mock status distribution
                status_data = {
                    'Status': ['Processed', 'Pending', 'In Progress', 'Failed'],
                    'Count': [
                        metrics['items_processed'],
                        metrics['items_pending'],
                        metrics['items_in_progress'],
                        metrics['items_failed']
                    ]
                }
                
                fig = px.pie(
                    status_data,
                    values='Count',
                    names='Status',
                    color_discrete_map={
                        'Processed': '#32CD32',
                        'Pending': '#FFA500',
                        'In Progress': '#1E90FF',
                        'Failed': '#FF6347'
                    }
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            # Worker status
            st.write("### Worker Status")
            
            worker_info = state_info['workers']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Active Workers:** {worker_info['active']}/{worker_info['total']}")
                
                # Progress bar for worker utilization
                utilization = worker_info['active'] / max(worker_info['total'], 1)
                st.progress(utilization)
                st.caption(f"Worker Utilization: {utilization*100:.1f}%")
            
            with col2:
                # Worker performance (mock data)
                worker_data = {
                    'Worker': [f"Worker {i+1}" for i in range(worker_info['total'])],
                    'Status': ['Active' if i < worker_info['active'] else 'Idle' for i in range(worker_info['total'])],
                    'Items Processed': np.random.randint(0, 100, worker_info['total'])
                }
                
                df = pd.DataFrame(worker_data)
                st.dataframe(df, use_container_width=True)
    
    def _render_bulk_operations(self):
        """Render bulk operations interface."""
        st.subheader("Bulk Queue Operations")
        
        controllers = get_all_queue_controllers()
        
        if not controllers:
            st.warning("No active queues found.")
            return
        
        # Operation type selector
        operation = st.selectbox(
            "Bulk Operation",
            [
                "Pause All Queues",
                "Resume All Queues",
                "Stop All Queues",
                "Start All Queues",
                "Schedule Global Maintenance"
            ]
        )
        
        # Queue selection
        selected_queues = st.multiselect(
            "Select Queues",
            list(controllers.keys()),
            default=list(controllers.keys()),
            format_func=lambda x: x.title()
        )
        
        if not selected_queues:
            st.warning("Please select at least one queue.")
            return
        
        # Operation-specific parameters
        if operation == "Pause All Queues":
            pause_mode = st.selectbox(
                "Pause Mode",
                [mode.value for mode in PauseMode if mode != PauseMode.SCHEDULED],
                index=1  # Default to graceful
            )
            
            reason = st.text_input(
                "Pause Reason",
                placeholder="Bulk maintenance operation"
            )
            
            if st.button(f"⏸️ Execute Bulk Pause", type="primary"):
                results = []
                
                for queue_name in selected_queues:
                    controller = controllers[queue_name]
                    success = controller.pause(PauseMode(pause_mode), reason or "Bulk pause")
                    results.append((queue_name, success))
                
                # Show results
                successful = [name for name, success in results if success]
                failed = [name for name, success in results if not success]
                
                if successful:
                    st.success(f"Paused queues: {', '.join(successful)}")
                
                if failed:
                    st.error(f"Failed to pause: {', '.join(failed)}")
                
                st.rerun()
        
        elif operation == "Resume All Queues":
            reason = st.text_input(
                "Resume Reason",
                placeholder="Maintenance complete"
            )
            
            if st.button(f"▶️ Execute Bulk Resume", type="primary"):
                results = []
                
                for queue_name in selected_queues:
                    controller = controllers[queue_name]
                    success = controller.resume(reason or "Bulk resume")
                    results.append((queue_name, success))
                
                # Show results
                successful = [name for name, success in results if success]
                failed = [name for name, success in results if not success]
                
                if successful:
                    st.success(f"Resumed queues: {', '.join(successful)}")
                
                if failed:
                    st.error(f"Failed to resume: {', '.join(failed)}")
                
                st.rerun()
        
        elif operation == "Stop All Queues":
            graceful = st.checkbox("Graceful Stop", value=True)
            
            if st.button(f"🚫 Execute Bulk Stop", type="secondary"):
                if st.session_state.get('confirm_bulk_stop'):
                    results = []
                    
                    for queue_name in selected_queues:
                        controller = controllers[queue_name]
                        success = controller.stop(graceful=graceful)
                        results.append((queue_name, success))
                    
                    # Show results
                    successful = [name for name, success in results if success]
                    failed = [name for name, success in results if not success]
                    
                    if successful:
                        st.success(f"Stopped queues: {', '.join(successful)}")
                    
                    if failed:
                        st.error(f"Failed to stop: {', '.join(failed)}")
                    
                    del st.session_state['confirm_bulk_stop']
                    st.rerun()
                else:
                    st.session_state['confirm_bulk_stop'] = True
                    st.warning("Click again to confirm bulk stop operation")
        
        elif operation == "Start All Queues":
            if st.button(f"🚀 Execute Bulk Start", type="primary"):
                results = []
                
                for queue_name in selected_queues:
                    controller = controllers[queue_name]
                    success = controller.start()
                    results.append((queue_name, success))
                
                # Show results
                successful = [name for name, success in results if success]
                failed = [name for name, success in results if not success]
                
                if successful:
                    st.success(f"Started queues: {', '.join(successful)}")
                
                if failed:
                    st.error(f"Failed to start: {', '.join(failed)}")
                
                st.rerun()
        
        elif operation == "Schedule Global Maintenance":
            st.write("### Global Maintenance Schedule")
            
            col1, col2 = st.columns(2)
            
            with col1:
                maintenance_date = st.date_input(
                    "Maintenance Date",
                    value=datetime.now().date() + timedelta(days=1)
                )
                
                start_time = st.time_input(
                    "Start Time",
                    value=datetime.now().replace(hour=2, minute=0, second=0, microsecond=0).time()
                )
                
                duration = st.number_input(
                    "Duration (hours)",
                    min_value=0.5,
                    max_value=24.0,
                    value=2.0,
                    step=0.5
                )
            
            with col2:
                reason = st.text_area(
                    "Maintenance Reason",
                    placeholder="System-wide maintenance, updates, etc."
                )
                
                pause_mode = st.selectbox(
                    "Pause Mode",
                    [mode.value for mode in PauseMode if mode != PauseMode.SCHEDULED],
                    index=1
                )
            
            if st.button(f"🗺 Schedule Global Maintenance", type="primary"):
                # Calculate times
                start_datetime = datetime.combine(maintenance_date, start_time)
                end_datetime = start_datetime + timedelta(hours=duration)
                
                results = []
                
                for queue_name in selected_queues:
                    controller = controllers[queue_name]
                    
                    schedule = PauseSchedule(
                        id=f"global_maint_{queue_name}_{int(start_datetime.timestamp())}",
                        name=f"Global Maintenance - {queue_name}",
                        pause_time=start_datetime,
                        resume_time=end_datetime,
                        mode=PauseMode(pause_mode),
                        reason=reason or "Global maintenance window",
                        created_by="dashboard_admin"
                    )
                    
                    success = controller.schedule_pause(schedule)
                    results.append((queue_name, success))
                
                # Show results
                successful = [name for name, success in results if success]
                failed = [name for name, success in results if not success]
                
                if successful:
                    st.success(f"Scheduled maintenance for: {', '.join(successful)}")
                    st.info(f"Maintenance window: {start_datetime} to {end_datetime}")
                
                if failed:
                    st.error(f"Failed to schedule for: {', '.join(failed)}")
        
        # Current queue status summary
        st.write("### Current Queue Status")
        
        status_data = []
        for queue_name in selected_queues:
            controller = controllers[queue_name]
            state_info = controller.get_state()
            
            status_data.append({
                'Queue': queue_name.title(),
                'State': state_info['state'].title(),
                'Workers': f"{state_info['workers']['active']}/{state_info['workers']['total']}",
                'Processed': f"{state_info['metrics']['items_processed']:,}",
                'Pending': f"{state_info['metrics']['items_pending']:,}",
                'Scheduled Pauses': len(state_info['scheduled_pauses'])
            })
        
        if status_data:
            df = pd.DataFrame(status_data)
            st.dataframe(df, use_container_width=True)
