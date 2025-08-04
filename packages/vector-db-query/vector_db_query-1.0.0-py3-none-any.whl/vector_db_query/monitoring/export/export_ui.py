"""
Export UI component for dashboard export functionality.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
import json

from .export_manager import get_export_manager, ExportType, ExportFormat, ExportJob


class ExportUI:
    """
    Streamlit UI component for export functionality.
    """
    
    def __init__(self):
        """Initialize export UI."""
        self.export_manager = get_export_manager()
    
    def render(self) -> None:
        """Render the complete export UI."""
        st.header("📤 Export Capabilities")
        
        # Create tabs for different export functions
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🚀 Quick Export", "📋 Job Manager", "📊 Export History", 
            "⚙️ Settings", "📈 Statistics"
        ])
        
        with tab1:
            self._render_quick_export_tab()
        
        with tab2:
            self._render_job_manager_tab()
        
        with tab3:
            self._render_history_tab()
        
        with tab4:
            self._render_settings_tab()
        
        with tab5:
            self._render_statistics_tab()
    
    def _render_quick_export_tab(self) -> None:
        """Render quick export interface."""
        st.subheader("Quick Export")
        st.write("Create and execute exports with common configurations.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Export Configuration**")
            
            # Export type selection
            export_type = st.selectbox(
                "Export Type",
                options=[e.value for e in ExportType],
                format_func=lambda x: x.replace('_', ' ').title(),
                help="Choose what type of data to export"
            )
            
            # Export format selection
            export_format = st.selectbox(
                "Export Format",
                options=[f.value for f in ExportFormat],
                format_func=lambda x: x.upper(),
                help="Choose the output format"
            )
            
            # Title and description
            title = st.text_input(
                "Export Title",
                value=f"{export_type.replace('_', ' ').title()} Export",
                help="Give your export a descriptive title"
            )
            
            description = st.text_area(
                "Description (Optional)",
                help="Add a description for this export"
            )
        
        with col2:
            st.write("**Export Options**")
            
            # Include options
            include_charts = st.checkbox("Include Charts", value=True)
            include_metadata = st.checkbox("Include Metadata", value=True)
            
            # Date range (for time-series data)
            use_date_range = st.checkbox("Specify Date Range")
            if use_date_range:
                date_col1, date_col2 = st.columns(2)
                with date_col1:
                    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
                with date_col2:
                    end_date = st.date_input("End Date", value=datetime.now())
                
                date_range = {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            else:
                date_range = None
            
            # Data sources (for specific exports)
            if export_type in ['custom_report', 'performance_report']:
                data_sources = st.multiselect(
                    "Data Sources",
                    options=["system_metrics", "queue_metrics", "process_data", "logs"],
                    default=["system_metrics"],
                    help="Select which data sources to include"
                )
            else:
                data_sources = []
        
        # Quick export templates
        st.write("**Quick Templates**")
        template_col1, template_col2, template_col3, template_col4 = st.columns(4)
        
        with template_col1:
            if st.button("📊 System Report", help="Export current system metrics", use_container_width=True):
                self._create_quick_export("system_metrics", "pdf", "System Status Report")
        
        with template_col2:
            if st.button("⚡ Performance Report", help="Export performance analytics", use_container_width=True):
                self._create_quick_export("performance_report", "html", "Performance Analysis")
        
        with template_col3:
            if st.button("🗃️ Dashboard Backup", help="Export dashboard configuration", use_container_width=True):
                self._create_quick_export("dashboard_config", "json", "Dashboard Configuration Backup")
        
        with template_col4:
            if st.button("💾 Full Backup", help="Export complete system backup", use_container_width=True):
                self._create_quick_export("full_backup", "json", "Complete System Backup")
        
        st.divider()
        
        # Custom export creation
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("**Create Custom Export**")
        with col2:
            if st.button("🚀 Create & Execute", type="primary", use_container_width=True):
                self._create_custom_export(
                    export_type, export_format, title, description,
                    include_charts, include_metadata, date_range, data_sources
                )
    
    def _render_job_manager_tab(self) -> None:
        """Render job manager interface."""
        st.subheader("Export Job Manager")
        st.write("Monitor and manage active export jobs.")
        
        # Refresh button
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        with col2:
            auto_refresh = st.checkbox("Auto-refresh", help="Automatically refresh every 10 seconds")
        
        # Get active jobs
        jobs = self.export_manager.list_jobs(include_history=False)
        
        if not jobs:
            st.info("No active export jobs.")
            return
        
        st.write(f"**Active Jobs ({len(jobs)})**")
        
        # Jobs table
        for job_data in jobs:
            with st.expander(f"📋 {job_data['title']} - {job_data['status'].title()}", expanded=job_data['status'] == 'running'):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Job Details**")
                    st.write(f"**ID:** `{job_data['job_id'][:8]}...`")
                    st.write(f"**Type:** {job_data['export_type'].replace('_', ' ').title()}")
                    st.write(f"**Format:** {job_data['export_format'].upper()}")
                    st.write(f"**Created:** {job_data['created_at'][:19]}")
                
                with col2:
                    st.write("**Status**")
                    status = job_data['status']
                    if status == 'pending':
                        st.warning(f"🟡 {status.title()}")
                    elif status == 'running':
                        st.info(f"🔵 {status.title()}")
                        st.progress(job_data['progress'] / 100.0)
                    elif status == 'completed':
                        st.success(f"🟢 {status.title()}")
                    elif status == 'failed':
                        st.error(f"🔴 {status.title()}")
                        if job_data.get('error_message'):
                            st.error(f"Error: {job_data['error_message']}")
                
                with col3:
                    st.write("**Actions**")
                    action_col1, action_col2 = st.columns(2)
                    
                    with action_col1:
                        if status == 'pending':
                            if st.button(f"▶️ Execute", key=f"exec_{job_data['job_id']}", use_container_width=True):
                                self._execute_job(job_data['job_id'])
                        elif status == 'completed' and job_data.get('output_path'):
                            if st.button(f"📥 Download", key=f"down_{job_data['job_id']}", use_container_width=True):
                                self._download_export(job_data['output_path'], job_data['title'])
                    
                    with action_col2:
                        if status in ['pending', 'running']:
                            if st.button(f"❌ Cancel", key=f"cancel_{job_data['job_id']}", use_container_width=True):
                                self._cancel_job(job_data['job_id'])
        
        # Auto-refresh logic
        if auto_refresh:
            import time
            time.sleep(10)
            st.rerun()
    
    def _render_history_tab(self) -> None:
        """Render export history interface."""
        st.subheader("Export History")
        st.write("View and manage completed exports.")
        
        # Controls
        col1, col2, col3 = st.columns(3)
        with col1:
            limit = st.number_input("Show Last N Jobs", min_value=10, max_value=200, value=50)
        with col2:
            filter_type = st.selectbox("Filter by Type", ["All"] + [e.value for e in ExportType])
        with col3:
            filter_status = st.selectbox("Filter by Status", ["All", "completed", "failed", "cancelled"])
        
        # Get history
        jobs = self.export_manager.list_jobs(include_history=True, limit=limit)
        
        # Apply filters
        if filter_type != "All":
            jobs = [j for j in jobs if j['export_type'] == filter_type]
        if filter_status != "All":
            jobs = [j for j in jobs if j['status'] == filter_status]
        
        if not jobs:
            st.info("No export history found.")
            return
        
        # History table
        df_data = []
        for job in jobs:
            df_data.append({
                'Title': job['title'],
                'Type': job['export_type'].replace('_', ' ').title(),
                'Format': job['export_format'].upper(),
                'Status': job['status'].title(),
                'Created': job['created_at'][:19],
                'Size': self._format_file_size(job.get('file_size', 0)),
                'Job ID': job['job_id'][:8] + '...'
            })
        
        df = pd.DataFrame(df_data)
        
        # Display table with selection
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Actions for selected job
        if event.selection and event.selection.rows:
            selected_idx = event.selection.rows[0]
            selected_job = jobs[selected_idx]
            
            st.write("**Selected Job Actions**")
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
            
            with action_col1:
                if selected_job['status'] == 'completed' and selected_job.get('output_path'):
                    if st.button("📥 Download", use_container_width=True):
                        self._download_export(selected_job['output_path'], selected_job['title'])
            
            with action_col2:
                if st.button("📋 View Details", use_container_width=True):
                    self._show_job_details(selected_job)
            
            with action_col3:
                if st.button("🔄 Recreate", use_container_width=True):
                    self._recreate_job(selected_job)
            
            with action_col4:
                if st.button("🗑️ Delete", use_container_width=True):
                    self._delete_job(selected_job['job_id'])
        
        # Bulk actions
        st.write("**Bulk Actions**")
        bulk_col1, bulk_col2, bulk_col3 = st.columns(3)
        
        with bulk_col1:
            if st.button("🗑️ Clear Failed Jobs", use_container_width=True):
                self._clear_failed_jobs()
        
        with bulk_col2:
            if st.button("📤 Export History", use_container_width=True):
                self._export_history(jobs)
        
        with bulk_col3:
            if st.button("🧹 Cleanup Old Jobs", use_container_width=True):
                self._cleanup_old_jobs()
    
    def _render_settings_tab(self) -> None:
        """Render export settings interface."""
        st.subheader("Export Settings")
        st.write("Configure default export settings and preferences.")
        
        # Default settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Default Export Settings**")
            
            default_format = st.selectbox(
                "Default Export Format",
                options=[f.value for f in ExportFormat],
                format_func=lambda x: x.upper(),
                help="Default format for new exports"
            )
            
            default_include_charts = st.checkbox("Include Charts by Default", value=True)
            default_include_metadata = st.checkbox("Include Metadata by Default", value=True)
            
            default_output_dir = st.text_input(
                "Default Output Directory",
                value=os.path.join(os.getcwd(), "exports"),
                help="Default directory for export outputs"
            )
        
        with col2:
            st.write("**Export Limits & Cleanup**")
            
            max_history_jobs = st.number_input(
                "Maximum History Jobs",
                min_value=50,
                max_value=1000,
                value=200,
                help="Maximum number of jobs to keep in history"
            )
            
            auto_cleanup_days = st.number_input(
                "Auto-cleanup After (Days)",
                min_value=1,
                max_value=365,
                value=30,
                help="Automatically delete jobs older than this many days"
            )
            
            max_concurrent_jobs = st.number_input(
                "Max Concurrent Jobs",
                min_value=1,
                max_value=10,
                value=3,
                help="Maximum number of jobs that can run simultaneously"
            )
        
        # File format specific settings
        st.write("**Format-Specific Settings**")
        
        format_tab1, format_tab2, format_tab3 = st.tabs(["PDF Settings", "Excel Settings", "HTML Settings"])
        
        with format_tab1:
            pdf_page_size = st.selectbox("PDF Page Size", ["A4", "Letter", "Legal"])
            pdf_orientation = st.selectbox("PDF Orientation", ["Portrait", "Landscape"])
            pdf_include_toc = st.checkbox("Include Table of Contents", value=True)
        
        with format_tab2:
            excel_include_formatting = st.checkbox("Include Excel Formatting", value=True)
            excel_freeze_headers = st.checkbox("Freeze Header Rows", value=True)
            excel_auto_filter = st.checkbox("Enable Auto Filter", value=True)
        
        with format_tab3:
            html_include_css = st.checkbox("Include Inline CSS", value=True)
            html_interactive = st.checkbox("Include Interactive Features", value=True)
            html_responsive = st.checkbox("Responsive Design", value=True)
        
        # Save settings
        if st.button("💾 Save Settings", type="primary"):
            settings = {
                'default_format': default_format,
                'default_include_charts': default_include_charts,
                'default_include_metadata': default_include_metadata,
                'default_output_dir': default_output_dir,
                'max_history_jobs': max_history_jobs,
                'auto_cleanup_days': auto_cleanup_days,
                'max_concurrent_jobs': max_concurrent_jobs,
                'pdf_settings': {
                    'page_size': pdf_page_size,
                    'orientation': pdf_orientation,
                    'include_toc': pdf_include_toc
                },
                'excel_settings': {
                    'include_formatting': excel_include_formatting,
                    'freeze_headers': excel_freeze_headers,
                    'auto_filter': excel_auto_filter
                },
                'html_settings': {
                    'include_css': html_include_css,
                    'interactive': html_interactive,
                    'responsive': html_responsive
                }
            }
            self._save_settings(settings)
            st.success("Settings saved successfully!")
    
    def _render_statistics_tab(self) -> None:
        """Render export statistics interface."""
        st.subheader("Export Statistics")
        st.write("View analytics and statistics about your exports.")
        
        # Get statistics
        stats = self.export_manager.get_export_statistics()
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Jobs", stats['total_jobs'])
        with col2:
            st.metric("Active Jobs", stats['active_jobs'])
        with col3:
            st.metric("Completed", stats['completed_jobs'])
        with col4:
            st.metric("Failed", stats['failed_jobs'])
        
        # Success rate
        if stats['total_jobs'] > 0:
            success_rate = (stats['completed_jobs'] / stats['total_jobs']) * 100
            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%",
                delta=f"{success_rate - 95:.1f}%" if success_rate < 95 else None
            )
        
        # Total exported size
        if stats['total_exported_size'] > 0:
            size_formatted = self._format_file_size(stats['total_exported_size'])
            st.metric("Total Exported", size_formatted)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Export types chart
            if stats['export_types']:
                st.write("**Export Types Distribution**")
                type_df = pd.DataFrame(
                    list(stats['export_types'].items()),
                    columns=['Type', 'Count']
                )
                type_df['Type'] = type_df['Type'].str.replace('_', ' ').str.title()
                st.bar_chart(type_df.set_index('Type'))
        
        with col2:
            # Export formats chart
            if stats['export_formats']:
                st.write("**Export Formats Distribution**")
                format_df = pd.DataFrame(
                    list(stats['export_formats'].items()),
                    columns=['Format', 'Count']
                )
                format_df['Format'] = format_df['Format'].str.upper()
                st.bar_chart(format_df.set_index('Format'))
        
        # Recent activity
        if stats['recent_activity']:
            st.write("**Recent Activity**")
            activity_df = pd.DataFrame(stats['recent_activity'])
            activity_df['created_at'] = pd.to_datetime(activity_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(
                activity_df[['title', 'status', 'export_type', 'export_format', 'created_at']],
                use_container_width=True,
                hide_index=True
            )
    
    def _create_quick_export(self, export_type: str, export_format: str, title: str) -> None:
        """Create and execute a quick export."""
        try:
            job_id = self.export_manager.create_export_job(
                ExportType(export_type),
                ExportFormat(export_format),
                title=title,
                created_by="dashboard_user"
            )
            
            # Execute immediately
            success = self.export_manager.execute_export_job(job_id)
            
            if success:
                st.success(f"✅ Export '{title}' created successfully!")
                st.info(f"Job ID: {job_id[:8]}...")
            else:
                st.error(f"❌ Failed to create export '{title}'")
                
        except Exception as e:
            st.error(f"Error creating export: {str(e)}")
    
    def _create_custom_export(self, export_type: str, export_format: str, title: str, 
                             description: str, include_charts: bool, include_metadata: bool,
                             date_range: Optional[Dict], data_sources: List[str]) -> None:
        """Create a custom export with specified options."""
        try:
            job_id = self.export_manager.create_export_job(
                ExportType(export_type),
                ExportFormat(export_format),
                title=title,
                description=description,
                include_charts=include_charts,
                include_metadata=include_metadata,
                date_range=date_range,
                data_sources=data_sources,
                created_by="dashboard_user"
            )
            
            # Execute immediately
            success = self.export_manager.execute_export_job(job_id)
            
            if success:
                st.success(f"✅ Custom export '{title}' created and executed successfully!")
                st.info(f"Job ID: {job_id[:8]}...")
            else:
                st.error(f"❌ Failed to execute custom export '{title}'")
                
        except Exception as e:
            st.error(f"Error creating custom export: {str(e)}")
    
    def _execute_job(self, job_id: str) -> None:
        """Execute a pending job."""
        success = self.export_manager.execute_export_job(job_id)
        if success:
            st.success("Job execution started!")
            st.rerun()
        else:
            st.error("Failed to start job execution")
    
    def _cancel_job(self, job_id: str) -> None:
        """Cancel an active job."""
        success = self.export_manager.cancel_job(job_id)
        if success:
            st.success("Job cancelled successfully!")
            st.rerun()
        else:
            st.error("Failed to cancel job")
    
    def _delete_job(self, job_id: str) -> None:
        """Delete a job from history."""
        success = self.export_manager.delete_job(job_id, delete_output=True)
        if success:
            st.success("Job deleted successfully!")
            st.rerun()
        else:
            st.error("Failed to delete job")
    
    def _download_export(self, output_path: str, title: str) -> None:
        """Handle export download."""
        if os.path.exists(output_path):
            with open(output_path, 'rb') as f:
                st.download_button(
                    label=f"📥 Download {title}",
                    data=f.read(),
                    file_name=os.path.basename(output_path),
                    mime="application/octet-stream"
                )
        else:
            st.error("Export file not found")
    
    def _show_job_details(self, job: Dict[str, Any]) -> None:
        """Show detailed job information."""
        with st.expander(f"Job Details: {job['title']}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.json({
                    'Job ID': job['job_id'],
                    'Title': job['title'],
                    'Description': job['description'],
                    'Type': job['export_type'],
                    'Format': job['export_format'],
                    'Status': job['status']
                })
            
            with col2:
                st.json({
                    'Created At': job['created_at'],
                    'Created By': job['created_by'],
                    'Progress': f"{job['progress']:.1f}%",
                    'File Size': self._format_file_size(job.get('file_size', 0)),
                    'Output Path': job.get('output_path', 'N/A'),
                    'Error': job.get('error_message', 'None')
                })
    
    def _recreate_job(self, job: Dict[str, Any]) -> None:
        """Recreate a job with the same settings."""
        try:
            new_job_id = self.export_manager.create_export_job(
                ExportType(job['export_type']),
                ExportFormat(job['export_format']),
                title=f"{job['title']} (Recreated)",
                description=job['description'],
                include_charts=job['include_charts'],
                include_metadata=job['include_metadata'],
                date_range=job.get('date_range'),
                data_sources=job.get('data_sources', []),
                created_by="dashboard_user"
            )
            
            st.success(f"Job recreated with ID: {new_job_id[:8]}...")
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to recreate job: {str(e)}")
    
    def _clear_failed_jobs(self) -> None:
        """Clear all failed jobs."""
        # This would be implemented in the export manager
        st.info("Failed jobs cleanup functionality would be implemented here.")
    
    def _export_history(self, jobs: List[Dict[str, Any]]) -> None:
        """Export job history to CSV."""
        df = pd.DataFrame(jobs)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download History CSV",
            data=csv,
            file_name=f"export_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    def _cleanup_old_jobs(self) -> None:
        """Cleanup old jobs based on settings."""
        st.info("Old jobs cleanup functionality would be implemented here.")
    
    def _save_settings(self, settings: Dict[str, Any]) -> None:
        """Save export settings."""
        # This would save settings to a configuration file
        settings_path = os.path.join(self.export_manager.data_dir, "export_settings.json")
        try:
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            st.error(f"Failed to save settings: {str(e)}")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        
        return f"{size_bytes:.1f} TB"