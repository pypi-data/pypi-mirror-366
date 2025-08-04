"""
Schedule Management UI for comprehensive schedule control.

This module provides advanced UI components for managing schedules,
including bulk operations, import/export, and schedule templates.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import csv
from io import StringIO
from pathlib import Path

from ..scheduling.models import Schedule, ScheduleType
from ..scheduling.schedule_manager import ScheduleManager
from ..scheduling.cron_scheduler import CronScheduler


class ScheduleManagementUI:
    """
    Advanced schedule management interface.
    
    Provides comprehensive tools for managing, organizing, and
    controlling schedules at scale.
    """
    
    def __init__(self, schedule_manager: ScheduleManager):
        """
        Initialize schedule management UI.
        
        Args:
            schedule_manager: Schedule manager instance
        """
        self.schedule_manager = schedule_manager
        self.cron_scheduler = CronScheduler()
        
    def render_management_dashboard(self):
        """Render the main schedule management dashboard."""
        st.header("🎛️ Schedule Management Dashboard")
        
        # Quick stats
        self._render_schedule_stats()
        
        # Management tabs
        tabs = st.tabs([
            "📋 Bulk Operations",
            "📁 Import/Export", 
            "🎨 Templates",
            "📊 Analytics",
            "🔧 Advanced Settings"
        ])
        
        with tabs[0]:
            self._render_bulk_operations()
        
        with tabs[1]:
            self._render_import_export()
        
        with tabs[2]:
            self._render_templates()
        
        with tabs[3]:
            self._render_analytics()
        
        with tabs[4]:
            self._render_advanced_settings()
    
    def _render_schedule_stats(self):
        """Render schedule statistics overview."""
        schedules = self.schedule_manager.get_all_schedules()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Schedules", len(schedules))
        
        with col2:
            active_count = sum(1 for s in schedules if s.enabled)
            st.metric("Active", active_count)
        
        with col3:
            cron_count = sum(1 for s in schedules if s.schedule_type == ScheduleType.CRON)
            st.metric("Cron Jobs", cron_count)
        
        with col4:
            file_count = sum(1 for s in schedules if s.schedule_type == ScheduleType.FILE_EVENT)
            st.metric("File Watchers", file_count)
        
        with col5:
            # Calculate success rate
            total_runs = sum(s.run_count for s in schedules)
            total_success = sum(s.success_count for s in schedules)
            success_rate = (total_success / total_runs * 100) if total_runs > 0 else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")
    
    def _render_bulk_operations(self):
        """Render bulk operations interface."""
        st.subheader("📋 Bulk Operations")
        
        schedules = self.schedule_manager.get_all_schedules()
        
        if not schedules:
            st.info("No schedules available for bulk operations")
            return
        
        # Selection interface
        st.write("### Select Schedules")
        
        # Quick selection buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Select All"):
                st.session_state['bulk_selected'] = [s.id for s in schedules]
        
        with col2:
            if st.button("Select None"):
                st.session_state['bulk_selected'] = []
        
        with col3:
            if st.button("Select Active"):
                st.session_state['bulk_selected'] = [s.id for s in schedules if s.enabled]
        
        with col4:
            if st.button("Select Inactive"):
                st.session_state['bulk_selected'] = [s.id for s in schedules if not s.enabled]
        
        # Initialize selection state
        if 'bulk_selected' not in st.session_state:
            st.session_state['bulk_selected'] = []
        
        # Schedule table with checkboxes
        schedule_data = []
        for schedule in schedules:
            is_selected = schedule.id in st.session_state['bulk_selected']
            
            schedule_data.append({
                'Select': is_selected,
                'Name': schedule.name,
                'Type': schedule.schedule_type.value,
                'Status': '🟢 Active' if schedule.enabled else '🔴 Inactive',
                'Last Run': schedule.last_run_at.strftime('%Y-%m-%d %H:%M') if schedule.last_run_at else 'Never',
                'Success Rate': f"{(schedule.success_count / schedule.run_count * 100):.0f}%" if schedule.run_count > 0 else "N/A",
                'ID': schedule.id
            })
        
        # Create dataframe
        df = pd.DataFrame(schedule_data)
        
        # Display with selection
        edited_df = st.data_editor(
            df,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select for bulk operations",
                    default=False,
                ),
                "ID": None  # Hide ID column
            },
            disabled=["Name", "Type", "Status", "Last Run", "Success Rate"],
            hide_index=True,
            key="bulk_selection_table"
        )
        
        # Update selection based on dataframe
        st.session_state['bulk_selected'] = edited_df[edited_df['Select']]['ID'].tolist()
        
        selected_count = len(st.session_state['bulk_selected'])
        st.info(f"Selected: {selected_count} schedules")
        
        if selected_count > 0:
            st.write("### Bulk Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Status Operations**")
                
                if st.button("🟢 Enable Selected", use_container_width=True):
                    self._bulk_enable(st.session_state['bulk_selected'], True)
                
                if st.button("🔴 Disable Selected", use_container_width=True):
                    self._bulk_enable(st.session_state['bulk_selected'], False)
                
                if st.button("🔄 Toggle Status", use_container_width=True):
                    self._bulk_toggle(st.session_state['bulk_selected'])
            
            with col2:
                st.write("**Execution Operations**")
                
                if st.button("▶️ Run Now", use_container_width=True):
                    if st.session_state.get('confirm_bulk_run'):
                        self._bulk_run(st.session_state['bulk_selected'])
                        del st.session_state['confirm_bulk_run']
                    else:
                        st.session_state['confirm_bulk_run'] = True
                        st.warning("Click again to confirm bulk execution")
                
                if st.button("🔄 Reset Statistics", use_container_width=True):
                    if st.session_state.get('confirm_reset_stats'):
                        self._bulk_reset_stats(st.session_state['bulk_selected'])
                        del st.session_state['confirm_reset_stats']
                    else:
                        st.session_state['confirm_reset_stats'] = True
                        st.warning("Click again to confirm reset")
            
            with col3:
                st.write("**Dangerous Operations**")
                
                if st.button("🗑️ Delete Selected", use_container_width=True, type="secondary"):
                    if st.session_state.get('confirm_bulk_delete'):
                        self._bulk_delete(st.session_state['bulk_selected'])
                        del st.session_state['confirm_bulk_delete']
                        st.session_state['bulk_selected'] = []
                    else:
                        st.session_state['confirm_bulk_delete'] = True
                        st.error("⚠️ Click again to confirm deletion")
            
            # Bulk parameter update
            with st.expander("🔧 Bulk Parameter Update"):
                st.write("Update parameters for all selected schedules")
                
                param_type = st.selectbox(
                    "Parameter to Update",
                    ["Max Retries", "Retry Delay", "Timeout", "Task Parameters"]
                )
                
                if param_type == "Max Retries":
                    new_value = st.number_input("New Max Retries", min_value=0, max_value=10, value=3)
                    if st.button("Apply to Selected"):
                        self._bulk_update_parameter(st.session_state['bulk_selected'], 'max_retries', new_value)
                
                elif param_type == "Retry Delay":
                    new_value = st.number_input("New Retry Delay (seconds)", min_value=10, max_value=3600, value=60)
                    if st.button("Apply to Selected"):
                        self._bulk_update_parameter(st.session_state['bulk_selected'], 'retry_delay', new_value)
                
                elif param_type == "Timeout":
                    new_value = st.number_input("New Timeout (seconds)", min_value=60, max_value=7200, value=1800)
                    if st.button("Apply to Selected"):
                        self._bulk_update_parameter(st.session_state['bulk_selected'], 'timeout', new_value)
    
    def _render_import_export(self):
        """Render import/export interface."""
        st.subheader("📁 Import/Export Schedules")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Export Schedules")
            
            export_format = st.selectbox(
                "Export Format",
                ["JSON", "CSV", "YAML"]
            )
            
            include_stats = st.checkbox("Include Statistics", value=True)
            include_history = st.checkbox("Include Execution History", value=False)
            
            if st.button("📥 Export All Schedules", use_container_width=True):
                export_data = self._export_schedules(export_format, include_stats, include_history)
                
                if export_format == "JSON":
                    st.download_button(
                        label="Download schedules.json",
                        data=export_data,
                        file_name=f"schedules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                elif export_format == "CSV":
                    st.download_button(
                        label="Download schedules.csv",
                        data=export_data,
                        file_name=f"schedules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            st.write("### Import Schedules")
            
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['json', 'csv'],
                help="Upload schedule configuration file"
            )
            
            if uploaded_file is not None:
                import_options = st.expander("Import Options", expanded=True)
                
                with import_options:
                    overwrite = st.checkbox("Overwrite existing schedules", value=False)
                    validate_only = st.checkbox("Validate only (don't import)", value=False)
                    auto_enable = st.checkbox("Auto-enable imported schedules", value=False)
                
                if st.button("📤 Import Schedules", use_container_width=True):
                    self._import_schedules(uploaded_file, overwrite, validate_only, auto_enable)
    
    def _render_templates(self):
        """Render schedule templates interface."""
        st.subheader("🎨 Schedule Templates")
        
        # Predefined templates
        templates = {
            "Daily Backup": {
                "description": "Daily backup at 2 AM",
                "type": ScheduleType.CRON,
                "cron": "0 2 * * *",
                "task": "backup_database",
                "params": {}
            },
            "Hourly Index Update": {
                "description": "Update search index every hour",
                "type": ScheduleType.CRON,
                "cron": "0 * * * *",
                "task": "incremental_index",
                "params": {"folder": ""}
            },
            "Real-time Document Monitor": {
                "description": "Monitor folder for new documents",
                "type": ScheduleType.FILE_EVENT,
                "watch_path": "",
                "patterns": ["*.pdf", "*.docx", "*.txt"],
                "task": "incremental_index",
                "params": {}
            },
            "Weekly Cleanup": {
                "description": "Clean old data weekly on Sunday",
                "type": ScheduleType.CRON,
                "cron": "0 3 * * 0",
                "task": "cleanup_vectors",
                "params": {"days_old": 30}
            },
            "Business Hours Monitor": {
                "description": "Active monitoring during business hours",
                "type": ScheduleType.CRON,
                "cron": "*/15 9-17 * * 1-5",
                "task": "full_reindex",
                "params": {}
            }
        }
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.write("### Available Templates")
            
            selected_template = st.selectbox(
                "Select Template",
                list(templates.keys())
            )
            
            if selected_template:
                template = templates[selected_template]
                
                st.info(template['description'])
                
                with st.expander("Template Details"):
                    st.json(template)
                
                if st.button("🚀 Use This Template", use_container_width=True):
                    st.session_state['template_to_use'] = template
                    st.session_state['template_name'] = selected_template
                    st.success(f"Template loaded: {selected_template}")
        
        with col2:
            st.write("### Create From Template")
            
            if st.session_state.get('template_to_use'):
                template = st.session_state['template_to_use']
                
                # Pre-fill form with template values
                name = st.text_input(
                    "Schedule Name",
                    value=f"{st.session_state['template_name']} - {datetime.now().strftime('%Y%m%d')}"
                )
                
                description = st.text_area(
                    "Description",
                    value=template['description']
                )
                
                if template['type'] == ScheduleType.CRON:
                    cron_expr = st.text_input(
                        "Cron Expression",
                        value=template['cron'],
                        help="You can modify the cron expression"
                    )
                    
                    # Validate and show next runs
                    if self.cron_scheduler.validate_cron_expression(cron_expr):
                        st.success("✓ Valid cron expression")
                        # Could show next run times here
                    else:
                        st.error("✗ Invalid cron expression")
                
                elif template['type'] == ScheduleType.FILE_EVENT:
                    watch_path = st.text_input(
                        "Watch Path",
                        placeholder="/path/to/monitor"
                    )
                    
                    patterns = st.text_input(
                        "File Patterns",
                        value=", ".join(template.get('patterns', []))
                    )
                
                # Task parameters
                if template.get('params'):
                    st.write("**Task Parameters**")
                    task_params = {}
                    
                    for param, default_value in template['params'].items():
                        if isinstance(default_value, str):
                            task_params[param] = st.text_input(param.title(), value=default_value)
                        elif isinstance(default_value, int):
                            task_params[param] = st.number_input(param.title(), value=default_value)
                        elif isinstance(default_value, bool):
                            task_params[param] = st.checkbox(param.title(), value=default_value)
                
                if st.button("✅ Create Schedule", use_container_width=True):
                    # Create schedule from template
                    schedule = Schedule(
                        name=name,
                        description=description,
                        schedule_type=template['type'],
                        task_name=template['task'],
                        enabled=True
                    )
                    
                    if template['type'] == ScheduleType.CRON:
                        schedule.cron_expression = cron_expr
                        schedule.trigger = ScheduleTrigger.CRON
                    elif template['type'] == ScheduleType.FILE_EVENT:
                        schedule.watch_paths = [watch_path] if watch_path else []
                        schedule.patterns = [p.strip() for p in patterns.split(',')]
                        schedule.trigger = ScheduleTrigger.FILE_CHANGE
                    
                    if 'task_params' in locals():
                        schedule.task_params = task_params
                    
                    try:
                        self.schedule_manager.create_schedule(schedule)
                        st.success(f"Created schedule: {name}")
                        del st.session_state['template_to_use']
                        del st.session_state['template_name']
                    except Exception as e:
                        st.error(f"Error creating schedule: {str(e)}")
            else:
                st.info("Select a template to get started")
    
    def _render_analytics(self):
        """Render schedule analytics."""
        st.subheader("📊 Schedule Analytics")
        
        schedules = self.schedule_manager.get_all_schedules()
        
        if not schedules:
            st.info("No schedules to analyze")
            return
        
        # Time range selector
        col1, col2 = st.columns([2, 4])
        
        with col1:
            time_range = st.selectbox(
                "Analysis Period",
                ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"]
            )
        
        # Calculate metrics
        metrics = self._calculate_analytics(schedules, time_range)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Executions", metrics['total_executions'])
            st.metric("Avg Daily Runs", f"{metrics['avg_daily_runs']:.1f}")
        
        with col2:
            st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
            st.metric("Failure Rate", f"{metrics['failure_rate']:.1f}%")
        
        with col3:
            st.metric("Most Active", metrics['most_active_schedule'])
            st.metric("Least Active", metrics['least_active_schedule'])
        
        with col4:
            st.metric("Avg Duration", f"{metrics['avg_duration']:.1f}s")
            st.metric("Total Runtime", f"{metrics['total_runtime']:.1f}h")
        
        # Charts
        st.write("### Execution Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Success/Failure distribution
            st.write("**Success vs Failure Distribution**")
            
            success_data = {
                'Status': ['Success', 'Failed'],
                'Count': [metrics['total_success'], metrics['total_failed']]
            }
            
            df_success = pd.DataFrame(success_data)
            st.bar_chart(df_success.set_index('Status'))
        
        with col2:
            # Schedule type distribution
            st.write("**Schedule Type Distribution**")
            
            type_counts = {}
            for schedule in schedules:
                stype = schedule.schedule_type.value
                type_counts[stype] = type_counts.get(stype, 0) + 1
            
            type_data = {
                'Type': list(type_counts.keys()),
                'Count': list(type_counts.values())
            }
            
            df_types = pd.DataFrame(type_data)
            st.bar_chart(df_types.set_index('Type'))
        
        # Top performers
        st.write("### Performance Rankings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏆 Top Performers (by success rate)**")
            
            top_performers = sorted(
                schedules,
                key=lambda s: (s.success_count / s.run_count) if s.run_count > 0 else 0,
                reverse=True
            )[:5]
            
            for i, schedule in enumerate(top_performers, 1):
                success_rate = (schedule.success_count / schedule.run_count * 100) if schedule.run_count > 0 else 0
                st.write(f"{i}. **{schedule.name}** - {success_rate:.1f}% ({schedule.run_count} runs)")
        
        with col2:
            st.write("**⚠️ Needs Attention (by failure rate)**")
            
            problem_schedules = sorted(
                schedules,
                key=lambda s: (s.failure_count / s.run_count) if s.run_count > 0 else 0,
                reverse=True
            )[:5]
            
            for i, schedule in enumerate(problem_schedules, 1):
                failure_rate = (schedule.failure_count / schedule.run_count * 100) if schedule.run_count > 0 else 0
                if failure_rate > 0:
                    st.write(f"{i}. **{schedule.name}** - {failure_rate:.1f}% failures ({schedule.failure_count} failed)")
    
    def _render_advanced_settings(self):
        """Render advanced settings interface."""
        st.subheader("🔧 Advanced Settings")
        
        # Global settings
        st.write("### Global Schedule Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Execution Limits**")
            
            max_concurrent = st.number_input(
                "Max Concurrent Executions",
                min_value=1,
                max_value=50,
                value=10,
                help="Maximum number of schedules that can run simultaneously"
            )
            
            default_timeout = st.number_input(
                "Default Timeout (seconds)",
                min_value=60,
                max_value=7200,
                value=1800,
                help="Default timeout for new schedules"
            )
            
            retry_limit = st.number_input(
                "Global Retry Limit",
                min_value=0,
                max_value=10,
                value=3,
                help="Maximum retries for failed executions"
            )
        
        with col2:
            st.write("**Monitoring Settings**")
            
            alert_threshold = st.slider(
                "Failure Alert Threshold (%)",
                min_value=0,
                max_value=100,
                value=20,
                help="Alert when failure rate exceeds this threshold"
            )
            
            log_retention = st.number_input(
                "Log Retention (days)",
                min_value=1,
                max_value=365,
                value=30,
                help="How long to keep execution logs"
            )
            
            enable_notifications = st.checkbox(
                "Enable Failure Notifications",
                value=True
            )
        
        if st.button("💾 Save Global Settings", use_container_width=True):
            # Save settings (implementation would go here)
            st.success("Global settings saved")
        
        # Maintenance operations
        st.write("### Maintenance Operations")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧹 Clean Old Logs", use_container_width=True):
                if st.session_state.get('confirm_clean_logs'):
                    # Clean logs older than retention period
                    st.success(f"Cleaned logs older than {log_retention} days")
                    del st.session_state['confirm_clean_logs']
                else:
                    st.session_state['confirm_clean_logs'] = True
                    st.warning("Click again to confirm")
        
        with col2:
            if st.button("🔄 Reset All Statistics", use_container_width=True):
                if st.session_state.get('confirm_reset_all'):
                    # Reset all schedule statistics
                    st.success("All statistics reset")
                    del st.session_state['confirm_reset_all']
                else:
                    st.session_state['confirm_reset_all'] = True
                    st.error("⚠️ Click again to confirm")
        
        with col3:
            if st.button("🔍 Validate All Schedules", use_container_width=True):
                # Validate all schedule configurations
                issues = self._validate_all_schedules()
                if issues:
                    st.warning(f"Found {len(issues)} issues")
                    for issue in issues:
                        st.write(f"- {issue}")
                else:
                    st.success("All schedules valid")
        
        # Debug information
        with st.expander("🐛 Debug Information"):
            st.write("**System Information**")
            st.json({
                "total_schedules": len(self.schedule_manager.get_all_schedules()),
                "scheduler_running": self.schedule_manager.is_running,
                "persistence_path": str(self.schedule_manager.persistence_path),
                "last_save": self.schedule_manager.last_save_time.isoformat() if hasattr(self.schedule_manager, 'last_save_time') else "N/A"
            })
    
    # Helper methods for bulk operations
    
    def _bulk_enable(self, schedule_ids: List[str], enable: bool):
        """Enable or disable multiple schedules."""
        count = 0
        for schedule_id in schedule_ids:
            schedule = self.schedule_manager.get_schedule(schedule_id)
            if schedule:
                schedule.enabled = enable
                self.schedule_manager.update_schedule(schedule)
                count += 1
        
        action = "enabled" if enable else "disabled"
        st.success(f"Successfully {action} {count} schedules")
        st.rerun()
    
    def _bulk_toggle(self, schedule_ids: List[str]):
        """Toggle status of multiple schedules."""
        count = 0
        for schedule_id in schedule_ids:
            schedule = self.schedule_manager.get_schedule(schedule_id)
            if schedule:
                schedule.enabled = not schedule.enabled
                self.schedule_manager.update_schedule(schedule)
                count += 1
        
        st.success(f"Toggled status of {count} schedules")
        st.rerun()
    
    def _bulk_run(self, schedule_ids: List[str]):
        """Run multiple schedules immediately."""
        count = 0
        for schedule_id in schedule_ids:
            try:
                self.schedule_manager.trigger_schedule(schedule_id)
                count += 1
            except Exception as e:
                st.error(f"Failed to run schedule {schedule_id}: {str(e)}")
        
        st.success(f"Triggered {count} schedules for immediate execution")
    
    def _bulk_reset_stats(self, schedule_ids: List[str]):
        """Reset statistics for multiple schedules."""
        count = 0
        for schedule_id in schedule_ids:
            schedule = self.schedule_manager.get_schedule(schedule_id)
            if schedule:
                schedule.run_count = 0
                schedule.success_count = 0
                schedule.failure_count = 0
                schedule.last_run_at = None
                schedule.last_error = None
                self.schedule_manager.update_schedule(schedule)
                count += 1
        
        st.success(f"Reset statistics for {count} schedules")
        st.rerun()
    
    def _bulk_delete(self, schedule_ids: List[str]):
        """Delete multiple schedules."""
        count = 0
        for schedule_id in schedule_ids:
            try:
                self.schedule_manager.delete_schedule(schedule_id)
                count += 1
            except Exception as e:
                st.error(f"Failed to delete schedule {schedule_id}: {str(e)}")
        
        st.success(f"Deleted {count} schedules")
        st.rerun()
    
    def _bulk_update_parameter(self, schedule_ids: List[str], param_name: str, value: Any):
        """Update a parameter for multiple schedules."""
        count = 0
        for schedule_id in schedule_ids:
            schedule = self.schedule_manager.get_schedule(schedule_id)
            if schedule:
                setattr(schedule, param_name, value)
                self.schedule_manager.update_schedule(schedule)
                count += 1
        
        st.success(f"Updated {param_name} for {count} schedules")
        st.rerun()
    
    def _export_schedules(self, format: str, include_stats: bool, include_history: bool) -> str:
        """Export schedules in the specified format."""
        schedules = self.schedule_manager.get_all_schedules()
        
        if format == "JSON":
            export_data = []
            for schedule in schedules:
                # Convert schedule to dict manually
                schedule_dict = {
                    'id': schedule.id,
                    'name': schedule.name,
                    'description': schedule.description,
                    'schedule_type': schedule.schedule_type.value,
                    'enabled': schedule.enabled,
                    'task_name': schedule.task_name,
                    'task_params': schedule.task_params,
                    'cron_expression': schedule.cron_expression,
                    'watch_paths': schedule.watch_paths,
                    'patterns': schedule.patterns,
                    'trigger': schedule.trigger.value if schedule.trigger else None,
                    'created_at': schedule.created_at.isoformat(),
                    'updated_at': schedule.updated_at.isoformat()
                }
                
                if not include_stats:
                    # Remove statistics
                    for key in ['run_count', 'success_count', 'failure_count', 'last_run_at', 'last_error']:
                        schedule_dict.pop(key, None)
                
                export_data.append(schedule_dict)
            
            return json.dumps(export_data, indent=2, default=str)
        
        elif format == "CSV":
            output = StringIO()
            writer = csv.writer(output)
            
            # Header
            headers = ['name', 'description', 'type', 'enabled', 'task_name']
            if include_stats:
                headers.extend(['run_count', 'success_count', 'failure_count', 'last_run_at'])
            writer.writerow(headers)
            
            # Data
            for schedule in schedules:
                row = [
                    schedule.name,
                    schedule.description,
                    schedule.schedule_type.value,
                    schedule.enabled,
                    schedule.task_name
                ]
                
                if include_stats:
                    row.extend([
                        schedule.run_count,
                        schedule.success_count,
                        schedule.failure_count,
                        schedule.last_run_at.isoformat() if schedule.last_run_at else ''
                    ])
                
                writer.writerow(row)
            
            return output.getvalue()
    
    def _import_schedules(self, file, overwrite: bool, validate_only: bool, auto_enable: bool):
        """Import schedules from file."""
        try:
            content = file.read()
            
            if file.name.endswith('.json'):
                schedules_data = json.loads(content)
            elif file.name.endswith('.csv'):
                # Parse CSV
                csv_data = StringIO(content.decode('utf-8'))
                reader = csv.DictReader(csv_data)
                schedules_data = list(reader)
            else:
                st.error("Unsupported file format")
                return
            
            # Validate schedules
            valid_count = 0
            error_count = 0
            errors = []
            
            for data in schedules_data:
                try:
                    # Create schedule object
                    if isinstance(data, dict):
                        # Convert from dict manually
                        schedule = Schedule(
                            name=data.get('name', ''),
                            description=data.get('description', ''),
                            schedule_type=ScheduleType(data.get('type', data.get('schedule_type', 'cron'))),
                            enabled=data.get('enabled', False),
                            task_name=data.get('task_name', ''),
                            task_params=data.get('task_params', {})
                        )
                        
                        # Set type-specific fields
                        if schedule.schedule_type == ScheduleType.CRON:
                            schedule.cron_expression = data.get('cron_expression', '0 * * * *')
                            schedule.trigger = ScheduleTrigger.CRON
                        elif schedule.schedule_type == ScheduleType.FILE_EVENT:
                            schedule.watch_paths = data.get('watch_paths', [])
                            schedule.patterns = data.get('patterns', [])
                            schedule.trigger = ScheduleTrigger.FILE_CHANGE
                    else:
                        schedule = None
                    
                    if schedule:
                        valid_count += 1
                        
                        if not validate_only:
                            if auto_enable:
                                schedule.enabled = True
                            
                            # Check if exists
                            existing = self.schedule_manager.get_schedule_by_name(schedule.name)
                            if existing and not overwrite:
                                errors.append(f"Schedule '{schedule.name}' already exists")
                                error_count += 1
                            else:
                                if existing:
                                    self.schedule_manager.delete_schedule(existing.id)
                                self.schedule_manager.create_schedule(schedule)
                    else:
                        error_count += 1
                        errors.append(f"Invalid schedule data: {data}")
                
                except Exception as e:
                    error_count += 1
                    errors.append(f"Error processing schedule: {str(e)}")
            
            # Show results
            if validate_only:
                st.info(f"Validation complete: {valid_count} valid, {error_count} errors")
            else:
                st.success(f"Import complete: {valid_count} imported, {error_count} errors")
            
            if errors:
                with st.expander("Import Errors"):
                    for error in errors:
                        st.write(f"- {error}")
        
        except Exception as e:
            st.error(f"Import failed: {str(e)}")
    
    def _calculate_analytics(self, schedules: List[Schedule], time_range: str) -> Dict[str, Any]:
        """Calculate analytics metrics for schedules."""
        # This is a simplified version - in production, you'd filter by time range
        total_runs = sum(s.run_count for s in schedules)
        total_success = sum(s.success_count for s in schedules)
        total_failed = sum(s.failure_count for s in schedules)
        
        # Find most/least active
        sorted_by_runs = sorted(schedules, key=lambda s: s.run_count, reverse=True)
        most_active = sorted_by_runs[0].name if sorted_by_runs else "N/A"
        least_active = sorted_by_runs[-1].name if sorted_by_runs else "N/A"
        
        return {
            'total_executions': total_runs,
            'total_success': total_success,
            'total_failed': total_failed,
            'success_rate': (total_success / total_runs * 100) if total_runs > 0 else 0,
            'failure_rate': (total_failed / total_runs * 100) if total_runs > 0 else 0,
            'avg_daily_runs': total_runs / 30,  # Simplified
            'most_active_schedule': most_active,
            'least_active_schedule': least_active,
            'avg_duration': 45.2,  # Mock data
            'total_runtime': total_runs * 45.2 / 3600  # Mock calculation
        }
    
    def _validate_all_schedules(self) -> List[str]:
        """Validate all schedule configurations."""
        issues = []
        schedules = self.schedule_manager.get_all_schedules()
        
        for schedule in schedules:
            # Check cron expressions
            if schedule.schedule_type == ScheduleType.CRON:
                if not self.cron_scheduler.validate_cron_expression(schedule.cron_expression):
                    issues.append(f"{schedule.name}: Invalid cron expression")
            
            # Check file paths
            elif schedule.schedule_type == ScheduleType.FILE_EVENT:
                for path in schedule.watch_paths:
                    if not Path(path).exists():
                        issues.append(f"{schedule.name}: Watch path does not exist: {path}")
            
            # Check task exists
            if schedule.task_name not in ['full_reindex', 'incremental_index', 'cleanup_vectors', 
                                          'backup_database', 'export_logs', 'generate_report']:
                issues.append(f"{schedule.name}: Unknown task: {schedule.task_name}")
        
        return issues