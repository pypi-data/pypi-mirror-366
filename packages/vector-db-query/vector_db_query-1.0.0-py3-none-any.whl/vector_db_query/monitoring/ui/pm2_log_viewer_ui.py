"""
PM2 log viewer UI components for the monitoring dashboard.

This module provides Streamlit UI components for viewing PM2 logs,
real-time log monitoring, log analysis, and log management.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from ..services.pm2_log_manager import (
    PM2LogManager, LogEntry, LogFile, LogStats,
    get_pm2_log_manager
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class PM2LogViewerUI:
    """
    UI components for PM2 log viewing and management.
    
    Provides interface for viewing logs, real-time monitoring,
    log analysis, and log file management.
    """
    
    def __init__(self):
        """Initialize PM2 log viewer UI."""
        self.log_manager = get_pm2_log_manager()
        self.change_tracker = get_change_tracker()
    
    def render_pm2_logs_tab(self):
        """Render the main PM2 logs tab."""
        st.header("📄 PM2 Log Viewer")
        
        # Tab selection
        log_tabs = st.tabs([
            "Log Viewer",
            "Live Monitoring", 
            "Log Analysis",
            "Log Management",
            "Search & Filter"
        ])
        
        with log_tabs[0]:
            self._render_log_viewer()
        
        with log_tabs[1]:
            self._render_live_monitoring()
        
        with log_tabs[2]:
            self._render_log_analysis()
        
        with log_tabs[3]:
            self._render_log_management()
        
        with log_tabs[4]:
            self._render_search_filter()
    
    def _render_log_viewer(self):
        """Render static log viewer interface."""
        st.subheader("Process Log Viewer")
        
        # Get available processes
        process_names = self.log_manager.get_process_names()
        
        if not process_names:
            st.info("No PM2 processes with logs found. Start some processes to see their logs here.")
            return
        
        # Process selection
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_process = st.selectbox(
                "Select Process",
                process_names,
                help="Choose a PM2 process to view its logs"
            )
        
        with col2:
            lines_to_show = st.number_input(
                "Lines to Show",
                min_value=10,
                max_value=1000,
                value=100,
                help="Number of recent log lines to display"
            )
        
        with col3:
            include_stderr = st.checkbox(
                "Include Errors",
                value=True,
                help="Include stderr logs along with stdout"
            )
        
        if selected_process:
            # Refresh button
            col1, col2, col3 = st.columns([1, 1, 4])
            
            with col1:
                if st.button("🔄 Refresh Logs"):
                    st.rerun()
            
            with col2:
                auto_refresh = st.checkbox("Auto Refresh", help="Automatically refresh every 5 seconds")
            
            # Get log entries
            log_entries = self.log_manager.get_process_logs(
                selected_process, 
                lines=lines_to_show, 
                include_stderr=include_stderr
            )
            
            if log_entries:
                # Log level filter
                st.write("### Filter by Log Level")
                available_levels = list(set(entry.level for entry in log_entries))
                selected_levels = st.multiselect(
                    "Log Levels",
                    available_levels,
                    default=available_levels,
                    help="Filter logs by level"
                )
                
                # Filter entries
                filtered_entries = [
                    entry for entry in log_entries 
                    if entry.level in selected_levels
                ]
                
                # Display logs
                st.write(f"### Recent Logs ({len(filtered_entries)} entries)")
                
                # Create scrollable log display
                log_container = st.container()
                
                with log_container:
                    for entry in filtered_entries:
                        # Color code by log level
                        level_colors = {
                            'error': '#FF6B6B',
                            'warn': '#FFD93D', 
                            'info': '#6BCF7F',
                            'debug': '#74C0FC'
                        }
                        
                        level_color = level_colors.get(entry.level, '#FFFFFF')
                        
                        # Format timestamp
                        timestamp_str = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Create log entry display
                        st.markdown(
                            f"""
                            <div style="
                                border-left: 4px solid {level_color};
                                padding: 8px 12px;
                                margin: 4px 0;
                                background-color: rgba(128, 128, 128, 0.1);
                                border-radius: 4px;
                            ">
                                <div style="
                                    font-size: 12px;
                                    color: #888;
                                    margin-bottom: 4px;
                                ">
                                    <strong>{timestamp_str}</strong> 
                                    [{entry.level.upper()}] 
                                    [{entry.log_type}]
                                    {f"[PID: {entry.process_id}]" if entry.process_id else ""}
                                </div>
                                <div style="
                                    font-family: 'Courier New', monospace;
                                    font-size: 14px;
                                    white-space: pre-wrap;
                                    word-wrap: break-word;
                                ">
                                    {entry.message}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                # Export option
                st.write("### Export Logs")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    export_filename = st.text_input(
                        "Export Filename",
                        value=f"{selected_process}_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    )
                
                with col2:
                    if st.button("📤 Export Logs"):
                        if self.log_manager.export_logs(selected_process, export_filename):
                            st.success(f"Logs exported to {export_filename}")
                        else:
                            st.error("Failed to export logs")
            else:
                st.info(f"No log entries found for process '{selected_process}'")
            
            # Auto refresh
            if auto_refresh:
                time.sleep(5)
                st.rerun()
    
    def _render_live_monitoring(self):
        """Render live log monitoring interface."""
        st.subheader("Live Log Monitoring")
        
        # Get available processes
        process_names = self.log_manager.get_process_names()
        
        if not process_names:
            st.info("No PM2 processes found for live monitoring.")
            return
        
        # Process selection for monitoring
        selected_process = st.selectbox(
            "Select Process for Live Monitoring",
            process_names,
            key="live_monitor_process"
        )
        
        if selected_process:
            # Monitoring controls
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("▶️ Start Monitoring"):
                    if self.log_manager.start_live_monitoring(selected_process):
                        st.success(f"Started live monitoring for {selected_process}")
                        st.session_state[f'monitoring_{selected_process}'] = True
                    else:
                        st.error("Failed to start live monitoring")
            
            with col2:
                if st.button("⏹️ Stop Monitoring"):
                    if self.log_manager.stop_live_monitoring(selected_process):
                        st.success(f"Stopped live monitoring for {selected_process}")
                        st.session_state[f'monitoring_{selected_process}'] = False
                    else:
                        st.error("Failed to stop live monitoring")
            
            with col3:
                auto_scroll = st.checkbox("Auto Scroll", value=True)
            
            # Monitoring status
            is_monitoring = st.session_state.get(f'monitoring_{selected_process}', False)
            status_color = "🟢" if is_monitoring else "🔴"
            st.write(f"**Status:** {status_color} {'Active' if is_monitoring else 'Inactive'}")
            
            # Live log display
            st.write("### Live Logs")
            
            # Create placeholder for live logs
            log_placeholder = st.empty()
            
            # Get live logs
            live_entries = self.log_manager.get_live_logs(selected_process, max_lines=50)
            
            if live_entries:
                with log_placeholder.container():
                    # Display live logs in reverse order (newest first)
                    for entry in reversed(live_entries):
                        timestamp_str = entry.timestamp.strftime('%H:%M:%S')
                        
                        # Color code by level
                        if entry.level == 'error':
                            st.error(f"[{timestamp_str}] {entry.message}")
                        elif entry.level == 'warn':
                            st.warning(f"[{timestamp_str}] {entry.message}")
                        else:
                            st.info(f"[{timestamp_str}] {entry.message}")
            else:
                log_placeholder.info("No live log entries yet. Start monitoring to see real-time logs.")
            
            # Auto refresh for live monitoring
            if is_monitoring:
                time.sleep(2)
                st.rerun()
    
    def _render_log_analysis(self):
        """Render log analysis interface."""
        st.subheader("Log Analysis & Statistics")
        
        # Get log statistics
        log_stats = self.log_manager.get_log_stats()
        
        if not log_stats:
            st.info("No log data available for analysis.")
            return
        
        # Overall statistics
        st.write("### Overall Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_processes = len(log_stats)
        total_size_mb = sum(stat.size_mb for stat in log_stats)
        total_errors = sum(stat.error_count for stat in log_stats)
        total_warnings = sum(stat.warning_count for stat in log_stats)
        
        with col1:
            st.metric("Processes", total_processes)
        
        with col2:
            st.metric("Total Log Size", f"{total_size_mb:.2f} MB")
        
        with col3:
            st.metric("Total Errors", total_errors, delta="Issues" if total_errors > 0 else None)
        
        with col4:
            st.metric("Total Warnings", total_warnings, delta="Warnings" if total_warnings > 0 else None)
        
        # Process-wise statistics table
        st.write("### Process Statistics")
        
        stats_data = []
        for stat in log_stats:
            stats_data.append({
                'Process': stat.process_name,
                'Log Files': len(stat.log_files),
                'Size (MB)': f"{stat.size_mb:.2f}",
                'Recent Lines': stat.total_lines,
                'Errors': stat.error_count,
                'Warnings': stat.warning_count,
                'Last Activity': stat.recent_activity.strftime('%Y-%m-%d %H:%M:%S'),
                'Health': '🟢' if stat.error_count == 0 else '🔴' if stat.error_count > 10 else '🟡'
            })
        
        df = pd.DataFrame(stats_data)
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                'Process': st.column_config.TextColumn('Process', width='medium'),
                'Health': st.column_config.TextColumn('Health', width='small'),
                'Errors': st.column_config.NumberColumn('Errors', width='small'),
                'Warnings': st.column_config.NumberColumn('Warnings', width='small')
            }
        )
        
        # Visualizations
        st.write("### Log Analysis Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Error distribution pie chart
            if total_errors > 0 or total_warnings > 0:
                error_data = {
                    'Level': ['Errors', 'Warnings', 'Info'],
                    'Count': [total_errors, total_warnings, max(1, sum(stat.total_lines for stat in log_stats) - total_errors - total_warnings)]
                }
                
                fig = px.pie(
                    error_data,
                    values='Count',
                    names='Level',
                    title='Log Level Distribution',
                    color_discrete_map={
                        'Errors': '#FF6B6B',
                        'Warnings': '#FFD93D',
                        'Info': '#6BCF7F'
                    }
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No errors or warnings to display")
        
        with col2:
            # Log size by process
            if len(log_stats) > 1:
                size_data = {
                    'Process': [stat.process_name for stat in log_stats],
                    'Size (MB)': [stat.size_mb for stat in log_stats]
                }
                
                fig = px.bar(
                    size_data,
                    x='Process',
                    y='Size (MB)',
                    title='Log Size by Process',
                    color='Size (MB)',
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Need multiple processes for size comparison")
        
        # Process detail analysis
        st.write("### Detailed Process Analysis")
        
        selected_process_analysis = st.selectbox(
            "Select Process for Detailed Analysis",
            [stat.process_name for stat in log_stats],
            key="analysis_process"
        )
        
        if selected_process_analysis:
            selected_stat = next(stat for stat in log_stats if stat.process_name == selected_process_analysis)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Process Details:**")
                st.write(f"**Name:** {selected_stat.process_name}")
                st.write(f"**Log Files:** {len(selected_stat.log_files)}")
                st.write(f"**Total Size:** {selected_stat.size_mb:.2f} MB")
                st.write(f"**Recent Activity:** {selected_stat.recent_activity.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Health assessment
                if selected_stat.error_count == 0:
                    st.success("🟢 Healthy - No errors detected")
                elif selected_stat.error_count <= 5:
                    st.warning(f"🟡 Minor Issues - {selected_stat.error_count} errors")
                else:
                    st.error(f"🔴 Issues Detected - {selected_stat.error_count} errors")
            
            with col2:
                st.write("**Log Files:**")
                for log_file in selected_stat.log_files:
                    file_size_kb = log_file.size / 1024
                    st.write(f"• **{log_file.log_type}**: {file_size_kb:.1f} KB")
                    st.caption(f"  Modified: {log_file.modified.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _render_log_management(self):
        """Render log management interface."""
        st.subheader("Log File Management")
        
        # Get log files
        log_files = self.log_manager.get_log_files()
        
        if not log_files:
            st.info("No log files found.")
            return
        
        # File management overview
        st.write("### Log Files Overview")
        
        total_size = sum(lf.size for lf in log_files)
        total_size_mb = total_size / (1024 * 1024)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", len(log_files))
        
        with col2:
            st.metric("Total Size", f"{total_size_mb:.2f} MB")
        
        with col3:
            recent_files = sum(1 for lf in log_files if lf.modified > datetime.now() - timedelta(hours=24))
            st.metric("Active Today", recent_files)
        
        # File list
        st.write("### Log Files")
        
        file_data = []
        for log_file in log_files:
            file_size_mb = log_file.size / (1024 * 1024)
            file_data.append({
                'Process': log_file.process_name,
                'Type': log_file.log_type,
                'Size (MB)': f"{file_size_mb:.3f}",
                'Modified': log_file.modified.strftime('%Y-%m-%d %H:%M:%S'),
                'Path': log_file.path,
                'Age (hours)': int((datetime.now() - log_file.modified).total_seconds() / 3600)
            })
        
        df = pd.DataFrame(file_data)
        st.dataframe(
            df[['Process', 'Type', 'Size (MB)', 'Modified', 'Age (hours)']],
            use_container_width=True,
            column_config={
                'Type': st.column_config.TextColumn('Type', width='small'),
                'Size (MB)': st.column_config.TextColumn('Size (MB)', width='small'),
                'Age (hours)': st.column_config.NumberColumn('Age (h)', width='small')
            }
        )
        
        # Management actions
        st.write("### Management Actions")
        
        # Process selection for management
        process_names = list(set(lf.process_name for lf in log_files))
        selected_process_mgmt = st.selectbox(
            "Select Process for Management",
            process_names,
            key="mgmt_process"
        )
        
        if selected_process_mgmt:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🗑️ Clear Logs"):
                    if st.session_state.get('confirm_clear_logs'):
                        if self.log_manager.clear_logs(selected_process_mgmt):
                            st.success(f"Cleared logs for {selected_process_mgmt}")
                            del st.session_state['confirm_clear_logs']
                            st.rerun()
                        else:
                            st.error("Failed to clear logs")
                    else:
                        st.session_state['confirm_clear_logs'] = True
                        st.warning("Click again to confirm log clearing")
            
            with col2:
                if st.button("📊 View Stats"):
                    stats = self.log_manager.get_log_stats(selected_process_mgmt)
                    if stats:
                        stat = stats[0]
                        st.json({
                            'process_name': stat.process_name,
                            'total_lines': stat.total_lines,
                            'error_count': stat.error_count,
                            'warning_count': stat.warning_count,
                            'size_mb': stat.size_mb,
                            'log_files': len(stat.log_files)
                        })
            
            with col3:
                if st.button("📁 Show Files"):
                    process_files = [lf for lf in log_files if lf.process_name == selected_process_mgmt]
                    for lf in process_files:
                        st.write(f"**{lf.log_type}**: `{lf.path}`")
        
        # Bulk operations
        st.write("### Bulk Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Clean Old Logs:**")
            days_old = st.number_input("Clear logs older than (days)", min_value=1, value=7)
            
            if st.button("🧹 Clean Old Logs"):
                cutoff_date = datetime.now() - timedelta(days=days_old)
                old_files = [lf for lf in log_files if lf.modified < cutoff_date]
                
                if old_files:
                    st.write(f"Found {len(old_files)} files older than {days_old} days:")
                    for lf in old_files[:5]:  # Show first 5
                        st.write(f"• {lf.process_name} ({lf.log_type})")
                    if len(old_files) > 5:
                        st.write(f"... and {len(old_files) - 5} more files")
                    
                    st.info("Note: Individual process log clearing is recommended over bulk operations")
                else:
                    st.success("No old log files found")
        
        with col2:
            st.write("**Log Archive:**")
            st.info("Log archiving functionality coming soon!")
            st.caption("This will allow compressing and archiving old log files to save space.")
    
    def _render_search_filter(self):
        """Render log search and filter interface."""
        st.subheader("Search & Filter Logs")
        
        # Search form
        with st.form("log_search_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                search_query = st.text_input(
                    "Search Query",
                    help="Enter text to search for (supports regex)"
                )
                
                process_filter = st.selectbox(
                    "Process Filter",
                    ['All Processes'] + self.log_manager.get_process_names(),
                    help="Filter by specific process"
                )
                
                log_level_filter = st.selectbox(
                    "Log Level Filter",
                    ['All Levels', 'error', 'warn', 'info', 'debug'],
                    help="Filter by log level"
                )
            
            with col2:
                # Time range filters
                time_range = st.selectbox(
                    "Time Range",
                    ['Last Hour', 'Last 6 Hours', 'Last Day', 'Last Week', 'Custom'],
                    help="Filter by time range"
                )
                
                if time_range == 'Custom':
                    start_time = st.datetime_input("Start Time")
                    end_time = st.datetime_input("End Time")
                else:
                    # Calculate time range
                    now = datetime.now()
                    time_deltas = {
                        'Last Hour': timedelta(hours=1),
                        'Last 6 Hours': timedelta(hours=6),
                        'Last Day': timedelta(days=1),
                        'Last Week': timedelta(weeks=1)
                    }
                    start_time = now - time_deltas[time_range]
                    end_time = now
                
                max_results = st.number_input(
                    "Max Results",
                    min_value=10,
                    max_value=1000,
                    value=100,
                    help="Maximum number of results to return"
                )
            
            submitted = st.form_submit_button("🔍 Search Logs")
        
        # Perform search
        if submitted and search_query:
            with st.spinner("Searching logs..."):
                # Prepare filters
                process_name = None if process_filter == 'All Processes' else process_filter
                log_level = None if log_level_filter == 'All Levels' else log_level_filter
                
                # Search logs
                results = self.log_manager.search_logs(
                    query=search_query,
                    process_name=process_name,
                    start_time=start_time,
                    end_time=end_time,
                    log_level=log_level,
                    max_results=max_results
                )
                
                # Display results
                if results:
                    st.success(f"Found {len(results)} matching log entries")
                    
                    # Results summary
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        process_counts = {}
                        for result in results:
                            process_counts[result.process_name] = process_counts.get(result.process_name, 0) + 1
                        
                        st.write("**By Process:**")
                        for proc, count in sorted(process_counts.items()):
                            st.write(f"• {proc}: {count}")
                    
                    with col2:
                        level_counts = {}
                        for result in results:
                            level_counts[result.level] = level_counts.get(result.level, 0) + 1
                        
                        st.write("**By Level:**")
                        for level, count in sorted(level_counts.items()):
                            st.write(f"• {level}: {count}")
                    
                    with col3:
                        time_span = max(result.timestamp for result in results) - min(result.timestamp for result in results)
                        st.write("**Time Span:**")
                        st.write(f"• Duration: {time_span}")
                        st.write(f"• From: {min(result.timestamp for result in results).strftime('%H:%M:%S')}")
                        st.write(f"• To: {max(result.timestamp for result in results).strftime('%H:%M:%S')}")
                    
                    # Display results
                    st.write("### Search Results")
                    
                    # Export search results
                    if st.button("📤 Export Search Results"):
                        export_path = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        
                        with open(export_path, 'w') as f:
                            f.write(f"Search Results for: {search_query}\n")
                            f.write(f"Time Range: {start_time} to {end_time}\n")
                            f.write(f"Process: {process_name or 'All'}\n")
                            f.write(f"Log Level: {log_level or 'All'}\n")
                            f.write(f"Results: {len(results)}\n")
                            f.write("=" * 50 + "\n\n")
                            
                            for result in results:
                                f.write(f"[{result.timestamp.isoformat()}] [{result.process_name}] [{result.level.upper()}] {result.message}\n")
                        
                        st.success(f"Search results exported to {export_path}")
                    
                    # Display entries
                    for i, result in enumerate(results):
                        with st.expander(f"{result.timestamp.strftime('%H:%M:%S')} - {result.process_name} - {result.level.upper()}", expanded=i < 5):
                            st.code(result.message, language=None)
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.caption(f"**Process:** {result.process_name}")
                            with col2:
                                st.caption(f"**Type:** {result.log_type}")
                            with col3:
                                st.caption(f"**Time:** {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    st.warning("No matching log entries found")
        
        elif submitted and not search_query:
            st.error("Please enter a search query")
        
        # Recent searches (placeholder)
        st.write("### Quick Searches")
        
        quick_searches = [
            "ERROR",
            "Failed",
            "Exception",
            "Warning",
            "Started",
            "Stopped"
        ]
        
        search_cols = st.columns(len(quick_searches))
        
        for i, quick_search in enumerate(quick_searches):
            with search_cols[i]:
                if st.button(f"🔍 {quick_search}", key=f"quick_{quick_search}"):
                    st.session_state['search_query'] = quick_search
                    st.rerun()