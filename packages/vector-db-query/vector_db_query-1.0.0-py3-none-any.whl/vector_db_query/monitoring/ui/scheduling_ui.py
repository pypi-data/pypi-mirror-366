"""
Scheduling UI components for the monitoring dashboard.

This module provides Streamlit UI components for managing schedules,
including cron schedules and file system event watchers.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from pathlib import Path

from ..scheduling.models import Schedule, ScheduleType, FileEvent, EventType
from ..scheduling.schedule_manager import ScheduleManager
from ..scheduling.cron_scheduler import CronScheduler
from ..scheduling.file_watcher import FileWatcher
from ..scheduling.multi_folder_watcher import MultiFolderWatcher
from .file_watcher_ui import FileWatcherUI
from .schedule_management_ui import ScheduleManagementUI
from .multi_folder_ui import MultiFolderUI
from .change_history_ui import ChangeHistoryUI
from ..history.change_tracker import ChangeType, ChangeCategory


class SchedulingUI:
    """
    UI components for schedule management.
    
    Provides interface for creating, editing, and monitoring schedules.
    """
    
    def __init__(self, schedule_manager: ScheduleManager):
        """
        Initialize scheduling UI.
        
        Args:
            schedule_manager: Schedule manager instance
        """
        self.schedule_manager = schedule_manager
        
        # Initialize file watcher and its UI
        self.file_watcher = FileWatcher()
        self.file_watcher_ui = FileWatcherUI(self.file_watcher)
        
        # Initialize multi-folder watcher and its UI
        self.multi_folder_watcher = MultiFolderWatcher()
        self.multi_folder_ui = MultiFolderUI(schedule_manager, self.multi_folder_watcher)
        
        # Initialize schedule management UI
        self.management_ui = ScheduleManagementUI(schedule_manager)
        
        # Initialize change history UI
        self.change_history_ui = ChangeHistoryUI()
        
    def render_scheduling_tab(self):
        """Render the main scheduling tab."""
        st.header("📅 Task Scheduling")
        
        # Tab selection
        schedule_tabs = st.tabs([
            "Active Schedules", 
            "Create Schedule", 
            "Schedule History",
            "Event Watchers",
            "Multi-Folder",
            "Management",
            "Change History"
        ])
        
        with schedule_tabs[0]:
            self._render_active_schedules()
        
        with schedule_tabs[1]:
            self._render_create_schedule()
        
        with schedule_tabs[2]:
            self._render_schedule_history()
        
        with schedule_tabs[3]:
            self._render_event_watchers()
        
        with schedule_tabs[4]:
            self.multi_folder_ui.render_multi_folder_config()
        
        with schedule_tabs[5]:
            self.management_ui.render_management_dashboard()
        
        with schedule_tabs[6]:
            self.change_history_ui.render_change_history_tab()
    
    def _render_active_schedules(self):
        """Render active schedules view."""
        st.subheader("Active Schedules")
        
        # Get all schedules
        schedules = self.schedule_manager.get_all_schedules()
        
        if not schedules:
            st.info("No active schedules. Create one to get started!")
            return
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All"] + [t.value for t in ScheduleType],
                key="schedule_filter_type"
            )
        
        with col2:
            filter_enabled = st.selectbox(
                "Filter by Status",
                ["All", "Enabled", "Disabled"],
                key="schedule_filter_status"
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Name", "Next Run", "Last Run", "Created"],
                key="schedule_sort"
            )
        
        # Apply filters
        filtered_schedules = schedules
        
        if filter_type != "All":
            filtered_schedules = [
                s for s in filtered_schedules 
                if s.schedule_type.value == filter_type
            ]
        
        if filter_enabled == "Enabled":
            filtered_schedules = [s for s in filtered_schedules if s.enabled]
        elif filter_enabled == "Disabled":
            filtered_schedules = [s for s in filtered_schedules if not s.enabled]
        
        # Sort schedules
        if sort_by == "Name":
            filtered_schedules.sort(key=lambda s: s.name)
        elif sort_by == "Next Run":
            filtered_schedules.sort(key=lambda s: s.next_run_at or datetime.max)
        elif sort_by == "Last Run":
            filtered_schedules.sort(key=lambda s: s.last_run_at or datetime.min, reverse=True)
        elif sort_by == "Created":
            filtered_schedules.sort(key=lambda s: s.created_at, reverse=True)
        
        # Display schedules
        for schedule in filtered_schedules:
            self._render_schedule_card(schedule)
    
    def _render_schedule_card(self, schedule: Schedule):
        """Render a single schedule card."""
        with st.expander(f"📅 {schedule.name}", expanded=False):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # Basic info
                st.write(f"**Type:** {schedule.schedule_type.value}")
                
                if schedule.schedule_type == ScheduleType.CRON:
                    st.write(f"**Cron Expression:** `{schedule.cron_expression}`")
                elif schedule.schedule_type == ScheduleType.FILE_EVENT:
                    st.write(f"**Watch Path:** `{schedule.watch_paths[0] if schedule.watch_paths else 'None'}`")
                
                st.write(f"**Task:** {schedule.task_name}")
                
                # Status
                status_color = "🟢" if schedule.enabled else "🔴"
                st.write(f"**Status:** {status_color} {'Enabled' if schedule.enabled else 'Disabled'}")
            
            with col2:
                # Timing info
                if schedule.next_run_at:
                    st.metric(
                        "Next Run",
                        schedule.next_run_at.strftime("%H:%M"),
                        f"In {self._format_time_delta(schedule.next_run_at - datetime.now())}"
                    )
                else:
                    st.metric("Next Run", "Not scheduled")
                
                if schedule.last_run_at:
                    st.metric(
                        "Last Run",
                        schedule.last_run_at.strftime("%H:%M"),
                        f"{self._format_time_delta(datetime.now() - schedule.last_run_at)} ago"
                    )
            
            with col3:
                # Statistics
                st.metric("Total Runs", schedule.run_count)
                
                if schedule.run_count > 0:
                    success_rate = (schedule.success_count / schedule.run_count) * 100
                    st.metric("Success Rate", f"{success_rate:.1f}%")
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button(
                    "▶️ Run Now" if schedule.enabled else "Enable",
                    key=f"run_{schedule.id}"
                ):
                    if schedule.enabled:
                        # Trigger immediate execution
                        if st.session_state.get('confirm_run') == schedule.id:
                            self.schedule_manager.trigger_schedule(schedule.id)
                            st.success(f"Triggered schedule: {schedule.name}")
                            del st.session_state['confirm_run']
                        else:
                            st.session_state['confirm_run'] = schedule.id
                            st.warning("Click again to confirm immediate execution")
                    else:
                        # Enable schedule
                        schedule.enabled = True
                        self.schedule_manager.update_schedule(schedule)
                        
                        # Track the change
                        self.change_history_ui.track_ui_change(
                            entity_type="schedule",
                            entity_id=schedule.id,
                            entity_name=schedule.name,
                            change_type=ChangeType.ENABLED,
                            description=f"Schedule '{schedule.name}' was enabled",
                            old_value={"enabled": False},
                            new_value={"enabled": True}
                        )
                        
                        st.success(f"Enabled schedule: {schedule.name}")
                        st.rerun()
            
            with col2:
                if schedule.enabled and st.button("⏸️ Disable", key=f"disable_{schedule.id}"):
                    schedule.enabled = False
                    self.schedule_manager.update_schedule(schedule)
                    
                    # Track the change
                    self.change_history_ui.track_ui_change(
                        entity_type="schedule",
                        entity_id=schedule.id,
                        entity_name=schedule.name,
                        change_type=ChangeType.DISABLED,
                        description=f"Schedule '{schedule.name}' was disabled",
                        old_value={"enabled": True},
                        new_value={"enabled": False}
                    )
                    
                    st.success(f"Disabled schedule: {schedule.name}")
                    st.rerun()
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_{schedule.id}"):
                    st.session_state['editing_schedule'] = schedule.id
                    st.rerun()
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{schedule.id}"):
                    if st.session_state.get('confirm_delete') == schedule.id:
                        # Track the deletion
                        self.change_history_ui.track_ui_change(
                            entity_type="schedule",
                            entity_id=schedule.id,
                            entity_name=schedule.name,
                            change_type=ChangeType.DELETED,
                            description=f"Schedule '{schedule.name}' was deleted",
                            old_value=schedule.to_dict() if hasattr(schedule, 'to_dict') else {"name": schedule.name},
                            new_value=None
                        )
                        
                        self.schedule_manager.delete_schedule(schedule.id)
                        st.success(f"Deleted schedule: {schedule.name}")
                        del st.session_state['confirm_delete']
                        st.rerun()
                    else:
                        st.session_state['confirm_delete'] = schedule.id
                        st.warning("Click again to confirm deletion")
            
            # Show task parameters if any
            if schedule.task_params:
                with st.expander("Task Parameters"):
                    st.json(schedule.task_params)
    
    def _render_create_schedule(self):
        """Render create schedule form."""
        st.subheader("Create New Schedule")
        
        # Check if editing existing schedule
        editing_id = st.session_state.get('editing_schedule')
        editing_schedule = None
        
        if editing_id:
            editing_schedule = self.schedule_manager.get_schedule(editing_id)
            if editing_schedule:
                st.info(f"Editing schedule: {editing_schedule.name}")
                if st.button("Cancel Edit"):
                    del st.session_state['editing_schedule']
                    st.rerun()
        
        # Schedule form
        with st.form("create_schedule_form"):
            # Basic information
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "Schedule Name",
                    value=editing_schedule.name if editing_schedule else "",
                    placeholder="Daily Backup"
                )
                
                description = st.text_area(
                    "Description",
                    value=editing_schedule.description if editing_schedule else "",
                    placeholder="Backup all documents daily at 2 AM"
                )
            
            with col2:
                schedule_type = st.selectbox(
                    "Schedule Type",
                    [t.value for t in ScheduleType],
                    index=[t.value for t in ScheduleType].index(
                        editing_schedule.schedule_type.value
                    ) if editing_schedule else 0
                )
                
                enabled = st.checkbox(
                    "Enable Schedule",
                    value=editing_schedule.enabled if editing_schedule else True
                )
            
            # Type-specific configuration
            if schedule_type == ScheduleType.CRON.value:
                st.subheader("Cron Configuration")
                
                # Cron helper
                use_helper = st.checkbox("Use Cron Helper", value=True)
                
                if use_helper:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        frequency = st.selectbox(
                            "Frequency",
                            ["Every Hour", "Daily", "Weekly", "Monthly", "Custom"]
                        )
                    
                    if frequency == "Every Hour":
                        with col2:
                            minute = st.number_input("At minute", min_value=0, max_value=59, value=0)
                        cron_expression = f"{minute} * * * *"
                    
                    elif frequency == "Daily":
                        with col2:
                            hour = st.number_input("Hour (24h)", min_value=0, max_value=23, value=2)
                        with col3:
                            minute = st.number_input("Minute", min_value=0, max_value=59, value=0)
                        cron_expression = f"{minute} {hour} * * *"
                    
                    elif frequency == "Weekly":
                        with col2:
                            day_of_week = st.selectbox(
                                "Day of Week",
                                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                index=0
                            )
                        with col3:
                            hour = st.number_input("Hour (24h)", min_value=0, max_value=23, value=2)
                        
                        dow_map = {
                            "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
                            "Friday": 5, "Saturday": 6, "Sunday": 0
                        }
                        cron_expression = f"0 {hour} * * {dow_map[day_of_week]}"
                    
                    else:  # Custom
                        cron_expression = st.text_input(
                            "Cron Expression",
                            value=editing_schedule.cron_expression if editing_schedule else "0 2 * * *",
                            help="minute hour day month day_of_week"
                        )
                    
                    st.code(f"Cron: {cron_expression}")
                else:
                    cron_expression = st.text_input(
                        "Cron Expression",
                        value=editing_schedule.cron_expression if editing_schedule else "0 2 * * *",
                        help="minute hour day month day_of_week"
                    )
                
                # Validate cron expression
                if cron_expression:
                    cron_scheduler = CronScheduler()
                    if cron_scheduler.validate_cron_expression(cron_expression):
                        st.success("✓ Valid cron expression")
                    else:
                        st.error("✗ Invalid cron expression")
            
            elif schedule_type == ScheduleType.FILE_EVENT.value:
                st.subheader("File Event Configuration")
                
                watch_path = st.text_input(
                    "Watch Path",
                    value=editing_schedule.watch_paths[0] if editing_schedule and editing_schedule.watch_paths else "",
                    placeholder="/path/to/watch"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    patterns = st.text_input(
                        "File Patterns (comma-separated)",
                        value=",".join(editing_schedule.patterns) if editing_schedule and editing_schedule.patterns else "*.pdf,*.docx",
                        help="File patterns to watch for"
                    )
                
                with col2:
                    recursive = st.checkbox(
                        "Watch Recursively",
                        value=editing_schedule.recursive if editing_schedule else True
                    )
                
                event_types = st.multiselect(
                    "Trigger Events",
                    ["created", "modified", "deleted", "moved"],
                    default=["created", "modified"]
                )
            
            # Task configuration
            st.subheader("Task Configuration")
            
            available_tasks = [
                "full_reindex",
                "incremental_index", 
                "cleanup_vectors",
                "backup_database",
                "export_logs",
                "generate_report"
            ]
            
            task_name = st.selectbox(
                "Task to Execute",
                available_tasks,
                index=available_tasks.index(editing_schedule.task_name) if editing_schedule and editing_schedule.task_name in available_tasks else 0
            )
            
            # Task parameters
            task_params = {}
            
            if task_name == "incremental_index":
                task_params["folder"] = st.text_input(
                    "Folder to Index",
                    value=editing_schedule.task_params.get("folder", "") if editing_schedule else ""
                )
            
            elif task_name == "cleanup_vectors":
                task_params["days_old"] = st.number_input(
                    "Delete vectors older than (days)",
                    min_value=1,
                    value=editing_schedule.task_params.get("days_old", 30) if editing_schedule else 30
                )
            
            elif task_name == "export_logs":
                task_params["include_types"] = st.multiselect(
                    "Log Types to Export",
                    ["system", "queue", "mcp", "all"],
                    default=editing_schedule.task_params.get("include_types", ["all"]) if editing_schedule else ["all"]
                )
            
            # Additional options
            with st.expander("Advanced Options"):
                max_retries = st.number_input(
                    "Max Retries on Failure",
                    min_value=0,
                    max_value=10,
                    value=editing_schedule.max_retries if editing_schedule else 3
                )
                
                retry_delay = st.number_input(
                    "Retry Delay (seconds)",
                    min_value=10,
                    max_value=3600,
                    value=editing_schedule.retry_delay if editing_schedule else 60
                )
                
                timeout = st.number_input(
                    "Task Timeout (seconds)",
                    min_value=60,
                    max_value=7200,
                    value=editing_schedule.timeout if editing_schedule else 1800
                )
            
            # Submit button
            submit_label = "Update Schedule" if editing_schedule else "Create Schedule"
            submitted = st.form_submit_button(submit_label)
            
            if submitted:
                # Validate inputs
                if not name:
                    st.error("Please provide a schedule name")
                    return
                
                # Create schedule object
                if editing_schedule:
                    schedule = editing_schedule
                    schedule.name = name
                    schedule.description = description
                    schedule.enabled = enabled
                    schedule.task_name = task_name
                    schedule.task_params = task_params
                    schedule.max_retries = max_retries
                    schedule.retry_delay = retry_delay
                    schedule.timeout = timeout
                else:
                    schedule = Schedule(
                        name=name,
                        description=description,
                        schedule_type=ScheduleType(schedule_type),
                        enabled=enabled,
                        task_name=task_name,
                        task_params=task_params,
                        max_retries=max_retries,
                        retry_delay=retry_delay,
                        timeout=timeout
                    )
                
                # Set type-specific fields
                if schedule_type == ScheduleType.CRON.value:
                    schedule.cron_expression = cron_expression
                    schedule.trigger = ScheduleTrigger.CRON
                
                elif schedule_type == ScheduleType.FILE_EVENT.value:
                    schedule.watch_paths = [watch_path] if watch_path else []
                    schedule.patterns = [p.strip() for p in patterns.split(',') if p.strip()]
                    schedule.recursive = recursive
                    schedule.trigger = ScheduleTrigger.FILE_CHANGE
                
                # Save schedule
                try:
                    if editing_schedule:
                        # Track update
                        self.change_history_ui.track_ui_change(
                            entity_type="schedule",
                            entity_id=schedule.id,
                            entity_name=schedule.name,
                            change_type=ChangeType.UPDATED,
                            description=f"Schedule '{schedule.name}' was updated",
                            old_value=editing_schedule.to_dict() if hasattr(editing_schedule, 'to_dict') else {"name": editing_schedule.name},
                            new_value=schedule.to_dict() if hasattr(schedule, 'to_dict') else {"name": schedule.name}
                        )
                        
                        self.schedule_manager.update_schedule(schedule)
                        st.success(f"Updated schedule: {name}")
                        del st.session_state['editing_schedule']
                    else:
                        # Create the schedule first to get the ID
                        self.schedule_manager.create_schedule(schedule)
                        
                        # Track creation
                        self.change_history_ui.track_ui_change(
                            entity_type="schedule",
                            entity_id=schedule.id,
                            entity_name=schedule.name,
                            change_type=ChangeType.CREATED,
                            description=f"Schedule '{schedule.name}' was created",
                            new_value=schedule.to_dict() if hasattr(schedule, 'to_dict') else {"name": schedule.name}
                        )
                        
                        st.success(f"Created schedule: {name}")
                    
                    st.rerun()
                
                except Exception as e:
                    st.error(f"Error saving schedule: {str(e)}")
    
    def _render_schedule_history(self):
        """Render schedule execution history."""
        st.subheader("Schedule Execution History")
        
        # Time range filter
        col1, col2, col3 = st.columns(3)
        
        with col1:
            time_range = st.selectbox(
                "Time Range",
                ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"]
            )
        
        with col2:
            schedule_filter = st.selectbox(
                "Schedule",
                ["All"] + [s.name for s in self.schedule_manager.get_all_schedules()]
            )
        
        with col3:
            status_filter = st.selectbox(
                "Status",
                ["All", "Success", "Failed", "Running"]
            )
        
        # Calculate time range
        now = datetime.now()
        if time_range == "Last Hour":
            start_time = now - timedelta(hours=1)
        elif time_range == "Last 24 Hours":
            start_time = now - timedelta(days=1)
        elif time_range == "Last 7 Days":
            start_time = now - timedelta(days=7)
        elif time_range == "Last 30 Days":
            start_time = now - timedelta(days=30)
        else:
            start_time = None
        
        # Get history (mock data for now)
        history = self._get_mock_history(start_time, schedule_filter, status_filter)
        
        if not history:
            st.info("No execution history found for the selected filters")
            return
        
        # Display history
        for entry in history:
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                status_icon = "✅" if entry['status'] == "Success" else "❌" if entry['status'] == "Failed" else "🔄"
                st.write(f"{status_icon} **{entry['schedule_name']}**")
                st.caption(f"Task: {entry['task_name']}")
            
            with col2:
                st.write(f"**Started:** {entry['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                if entry['end_time']:
                    duration = (entry['end_time'] - entry['start_time']).total_seconds()
                    st.caption(f"Duration: {duration:.1f}s")
            
            with col3:
                st.write(f"**Status:** {entry['status']}")
            
            with col4:
                if st.button("View Details", key=f"details_{entry['id']}"):
                    with st.expander("Execution Details", expanded=True):
                        st.json(entry.get('details', {}))
            
            st.divider()
    
    def _render_event_watchers(self):
        """Render file system event watchers."""
        # Use the dedicated file watcher UI
        self.file_watcher_ui.render_watcher_dashboard()
    
    def _format_time_delta(self, delta: timedelta) -> str:
        """Format a timedelta to a human-readable string."""
        total_seconds = int(delta.total_seconds())
        
        if total_seconds < 0:
            return "overdue"
        
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes}m"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            return f"{hours}h"
        else:
            days = total_seconds // 86400
            return f"{days}d"
    
    def _get_mock_history(self, start_time, schedule_filter, status_filter):
        """Get mock execution history data."""
        # This would be replaced with actual history from the database
        history = [
            {
                'id': '1',
                'schedule_name': 'Daily Backup',
                'task_name': 'backup_database',
                'start_time': datetime.now() - timedelta(hours=2),
                'end_time': datetime.now() - timedelta(hours=1, minutes=55),
                'status': 'Success',
                'details': {'backed_up_files': 1523, 'size_mb': 245.7}
            },
            {
                'id': '2',
                'schedule_name': 'Hourly Index Update',
                'task_name': 'incremental_index',
                'start_time': datetime.now() - timedelta(minutes=30),
                'end_time': datetime.now() - timedelta(minutes=28),
                'status': 'Success',
                'details': {'indexed_files': 15, 'new_embeddings': 450}
            },
            {
                'id': '3',
                'schedule_name': 'Weekly Cleanup',
                'task_name': 'cleanup_vectors',
                'start_time': datetime.now() - timedelta(days=1),
                'end_time': datetime.now() - timedelta(days=1) + timedelta(minutes=5),
                'status': 'Failed',
                'details': {'error': 'Database connection timeout'}
            }
        ]
        
        # Apply filters
        if start_time:
            history = [h for h in history if h['start_time'] >= start_time]
        
        if schedule_filter != "All":
            history = [h for h in history if h['schedule_name'] == schedule_filter]
        
        if status_filter != "All":
            history = [h for h in history if h['status'] == status_filter]
        
        return history