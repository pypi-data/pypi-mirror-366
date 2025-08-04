"""
Change history UI components for the monitoring dashboard.

This module provides Streamlit UI components for viewing and analyzing
change history, audit trails, and system snapshots.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from ..history.change_tracker import (
    ChangeTracker, ChangeEvent, ChangeType, ChangeCategory,
    ChangeSnapshot, get_change_tracker
)


class ChangeHistoryUI:
    """
    UI components for change history management.
    
    Provides interface for viewing changes, creating snapshots,
    and analyzing system evolution.
    """
    
    def __init__(self, change_tracker: Optional[ChangeTracker] = None):
        """
        Initialize change history UI.
        
        Args:
            change_tracker: Change tracker instance (uses singleton if not provided)
        """
        self.change_tracker = change_tracker or get_change_tracker()
        
    def render_change_history_tab(self):
        """Render the main change history tab."""
        st.header("📜 Change History & Audit Trail")
        
        # Tab selection
        history_tabs = st.tabs([
            "Recent Changes",
            "Search History", 
            "Analytics",
            "Snapshots",
            "Audit Export"
        ])
        
        with history_tabs[0]:
            self._render_recent_changes()
        
        with history_tabs[1]:
            self._render_search_history()
        
        with history_tabs[2]:
            self._render_analytics()
        
        with history_tabs[3]:
            self._render_snapshots()
        
        with history_tabs[4]:
            self._render_audit_export()
    
    def _render_recent_changes(self):
        """Render recent changes view."""
        st.subheader("Recent Changes")
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            limit = st.selectbox(
                "Show last",
                [10, 25, 50, 100, 200],
                index=1,
                key="recent_limit"
            )
        
        with col2:
            category_filter = st.selectbox(
                "Category",
                ["All"] + [c.value for c in ChangeCategory],
                key="recent_category"
            )
        
        with col3:
            refresh_btn = st.button("🔄 Refresh", use_container_width=True)
        
        # Get recent changes
        if category_filter != "All":
            changes = self.change_tracker.get_changes(
                category=ChangeCategory(category_filter),
                limit=limit
            )
        else:
            changes = self.change_tracker.get_recent_changes(limit=limit)
        
        if not changes:
            st.info("No changes recorded yet.")
            return
        
        # Display changes
        for change in changes:
            self._render_change_card(change)
    
    def _render_change_card(self, change: ChangeEvent):
        """Render a single change event card."""
        # Determine icon based on change type
        icon_map = {
            ChangeType.CREATED: "🆕",
            ChangeType.UPDATED: "✏️",
            ChangeType.DELETED: "🗑️",
            ChangeType.ENABLED: "✅",
            ChangeType.DISABLED: "❌",
            ChangeType.EXECUTED: "▶️",
            ChangeType.FAILED: "⚠️",
            ChangeType.CONFIGURED: "⚙️",
            ChangeType.MIGRATED: "📦",
            ChangeType.RESTORED: "♻️"
        }
        
        icon = icon_map.get(change.change_type, "📝")
        
        with st.expander(
            f"{icon} {change.entity_name} - {change.change_type.value.capitalize()}",
            expanded=False
        ):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Description:** {change.description}")
                st.write(f"**Entity:** {change.entity_type} ({change.entity_id})")
                st.write(f"**Category:** {change.category.value}")
                
                if change.user:
                    st.write(f"**User:** {change.user}")
                
                if change.tags:
                    st.write(f"**Tags:** {', '.join(change.tags)}")
            
            with col2:
                st.write(f"**Time:** {change.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                time_ago = self._format_time_ago(change.timestamp)
                st.caption(f"{time_ago} ago")
            
            # Show details if present
            if change.details:
                with st.expander("Details"):
                    st.json(change.details)
            
            # Show value changes if present
            if change.old_value is not None or change.new_value is not None:
                with st.expander("Value Changes"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Old Value:**")
                        if isinstance(change.old_value, (dict, list)):
                            st.json(change.old_value)
                        else:
                            st.code(str(change.old_value))
                    
                    with col2:
                        st.write("**New Value:**")
                        if isinstance(change.new_value, (dict, list)):
                            st.json(change.new_value)
                        else:
                            st.code(str(change.new_value))
            
            # Related changes
            if change.related_changes:
                with st.expander(f"Related Changes ({len(change.related_changes)})"):
                    for related_id in change.related_changes:
                        st.write(f"- {related_id}")
    
    def _render_search_history(self):
        """Render search interface for change history."""
        st.subheader("Search Change History")
        
        # Search form
        with st.form("search_history_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                entity_type = st.text_input(
                    "Entity Type",
                    placeholder="schedule, config, service..."
                )
                
                entity_id = st.text_input(
                    "Entity ID",
                    placeholder="Optional specific ID"
                )
                
                user = st.text_input(
                    "User",
                    placeholder="Filter by user"
                )
            
            with col2:
                category = st.selectbox(
                    "Category",
                    ["Any"] + [c.value for c in ChangeCategory]
                )
                
                change_type = st.selectbox(
                    "Change Type",
                    ["Any"] + [t.value for t in ChangeType]
                )
                
                tags_input = st.text_input(
                    "Tags (comma-separated)",
                    placeholder="tag1, tag2"
                )
            
            # Time range
            st.write("### Time Range")
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=7)
                )
                start_time = st.time_input("Start Time", value=datetime.min.time())
            
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now()
                )
                end_time = st.time_input("End Time", value=datetime.max.time())
            
            # Search button
            submitted = st.form_submit_button("🔍 Search", use_container_width=True)
            
            if submitted:
                # Build search parameters
                search_params = {}
                
                if entity_type:
                    search_params['entity_type'] = entity_type
                
                if entity_id:
                    search_params['entity_id'] = entity_id
                
                if user:
                    search_params['user'] = user
                
                if category != "Any":
                    search_params['category'] = ChangeCategory(category)
                
                if change_type != "Any":
                    search_params['change_type'] = ChangeType(change_type)
                
                if tags_input:
                    search_params['tags'] = [t.strip() for t in tags_input.split(',')]
                
                # Combine date and time
                search_params['start_time'] = datetime.combine(start_date, start_time)
                search_params['end_time'] = datetime.combine(end_date, end_time)
                
                # Perform search
                results = self.change_tracker.get_changes(**search_params, limit=200)
                
                # Display results
                st.write(f"### Search Results ({len(results)} changes)")
                
                if results:
                    for change in results:
                        self._render_change_card(change)
                else:
                    st.info("No changes found matching the search criteria.")
    
    def _render_analytics(self):
        """Render change analytics dashboard."""
        st.subheader("Change Analytics")
        
        # Time range selector
        col1, col2 = st.columns([2, 1])
        
        with col1:
            time_range = st.selectbox(
                "Time Range",
                ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
            )
        
        with col2:
            if st.button("📊 Generate Report", use_container_width=True):
                st.session_state['generate_analytics'] = True
        
        # Calculate time range
        now = datetime.now()
        if time_range == "Last 24 Hours":
            start_time = now - timedelta(days=1)
        elif time_range == "Last 7 Days":
            start_time = now - timedelta(days=7)
        elif time_range == "Last 30 Days":
            start_time = now - timedelta(days=30)
        elif time_range == "Last 90 Days":
            start_time = now - timedelta(days=90)
        else:
            start_time = None
        
        # Get statistics
        stats = self.change_tracker.get_change_statistics(
            start_time=start_time,
            end_time=now
        )
        
        # Display overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Changes", stats['total_changes'])
        
        with col2:
            most_common_type = max(
                stats['by_type'].items(), 
                key=lambda x: x[1]
            )[0] if stats['by_type'] else "N/A"
            st.metric("Most Common Type", most_common_type)
        
        with col3:
            most_active_entity = max(
                stats['by_entity'].items(),
                key=lambda x: x[1]
            )[0] if stats['by_entity'] else "N/A"
            st.metric("Most Active Entity", most_active_entity)
        
        with col4:
            unique_users = len(stats['by_user'])
            st.metric("Active Users", unique_users)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Changes by category pie chart
            if stats['by_category']:
                fig_category = px.pie(
                    values=list(stats['by_category'].values()),
                    names=list(stats['by_category'].keys()),
                    title="Changes by Category"
                )
                st.plotly_chart(fig_category, use_container_width=True)
        
        with col2:
            # Changes by type bar chart
            if stats['by_type']:
                fig_type = px.bar(
                    x=list(stats['by_type'].keys()),
                    y=list(stats['by_type'].values()),
                    title="Changes by Type",
                    labels={'x': 'Change Type', 'y': 'Count'}
                )
                st.plotly_chart(fig_type, use_container_width=True)
        
        # Timeline chart
        if stats['by_day']:
            # Convert to DataFrame for easier plotting
            timeline_data = pd.DataFrame(
                list(stats['by_day'].items()),
                columns=['Date', 'Changes']
            )
            timeline_data['Date'] = pd.to_datetime(timeline_data['Date'])
            timeline_data = timeline_data.sort_values('Date')
            
            fig_timeline = px.line(
                timeline_data,
                x='Date',
                y='Changes',
                title="Changes Over Time",
                markers=True
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # User activity table
        if stats['by_user']:
            st.write("### User Activity")
            user_df = pd.DataFrame(
                list(stats['by_user'].items()),
                columns=['User', 'Changes']
            ).sort_values('Changes', ascending=False)
            st.dataframe(user_df, use_container_width=True)
    
    def _render_snapshots(self):
        """Render system snapshots interface."""
        st.subheader("System Snapshots")
        
        # Create snapshot section
        with st.expander("📸 Create New Snapshot", expanded=False):
            with st.form("create_snapshot_form"):
                name = st.text_input(
                    "Snapshot Name",
                    placeholder="Pre-deployment backup"
                )
                
                description = st.text_area(
                    "Description",
                    placeholder="Snapshot taken before major system update"
                )
                
                # Select what to include
                st.write("### Include in Snapshot:")
                
                include_schedules = st.checkbox("Schedules", value=True)
                include_configs = st.checkbox("Configurations", value=True)
                include_services = st.checkbox("Service States", value=True)
                include_settings = st.checkbox("System Settings", value=True)
                
                submitted = st.form_submit_button("Create Snapshot")
                
                if submitted and name:
                    # Gather state data based on selections
                    state_data = {}
                    
                    if include_schedules:
                        # Get all schedules (mock for now)
                        state_data['schedules'] = {
                            'count': 10,
                            'enabled': 8,
                            'disabled': 2
                        }
                    
                    if include_configs:
                        state_data['configurations'] = {
                            'api_keys': 'encrypted',
                            'db_connections': 5
                        }
                    
                    if include_services:
                        state_data['services'] = {
                            'running': ['queue_processor', 'mcp_server'],
                            'stopped': ['backup_service']
                        }
                    
                    if include_settings:
                        state_data['settings'] = {
                            'version': '1.0.0',
                            'environment': 'production'
                        }
                    
                    # Create snapshot
                    try:
                        snapshot_id = self.change_tracker.create_snapshot(
                            name=name,
                            description=description,
                            state_data=state_data,
                            created_by="current_user"  # TODO: Get actual user
                        )
                        st.success(f"Snapshot created successfully: {snapshot_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating snapshot: {str(e)}")
        
        # List existing snapshots
        st.write("### Existing Snapshots")
        
        snapshots = self.change_tracker.get_snapshots(limit=20)
        
        if not snapshots:
            st.info("No snapshots created yet.")
            return
        
        for snapshot in snapshots:
            with st.expander(
                f"📸 {snapshot.name} - {snapshot.timestamp.strftime('%Y-%m-%d %H:%M')}"
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Description:** {snapshot.description}")
                    st.write(f"**Created by:** {snapshot.created_by or 'System'}")
                    st.write(f"**Checksum:** `{snapshot.checksum[:16]}...`")
                    
                    # Verify integrity
                    if snapshot.verify_integrity():
                        st.success("✓ Snapshot integrity verified")
                    else:
                        st.error("✗ Snapshot integrity check failed")
                
                with col2:
                    # Action buttons
                    if st.button("📄 View Details", key=f"view_{snapshot.id}"):
                        st.json(snapshot.state_data)
                    
                    if st.button("🔄 Compare", key=f"compare_{snapshot.id}"):
                        st.session_state['compare_snapshot'] = snapshot.id
                
                # Show state summary
                st.write("### Snapshot Contents:")
                for key, value in snapshot.state_data.items():
                    if isinstance(value, dict):
                        st.write(f"- **{key}:** {len(value)} items")
                    else:
                        st.write(f"- **{key}:** {value}")
        
        # Snapshot comparison
        if 'compare_snapshot' in st.session_state:
            st.write("### Compare Snapshots")
            
            snapshot1_id = st.session_state['compare_snapshot']
            
            # Select second snapshot
            other_snapshots = [s for s in snapshots if s.id != snapshot1_id]
            
            if other_snapshots:
                snapshot2_name = st.selectbox(
                    "Compare with:",
                    [s.name for s in other_snapshots]
                )
                
                snapshot2 = next(s for s in other_snapshots if s.name == snapshot2_name)
                
                if st.button("🔍 Compare Now"):
                    try:
                        comparison = self.change_tracker.compare_snapshots(
                            snapshot1_id,
                            snapshot2.id
                        )
                        
                        # Display comparison results
                        st.write("### Comparison Results")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**From:** {comparison['snapshot1']['name']}")
                            st.caption(comparison['snapshot1']['timestamp'])
                        
                        with col2:
                            st.write(f"**To:** {comparison['snapshot2']['name']}")
                            st.caption(comparison['snapshot2']['timestamp'])
                        
                        # Show differences
                        differences = comparison['differences']
                        
                        if differences:
                            st.write(f"### Found {len(differences)} differences:")
                            
                            for diff in differences:
                                diff_type = diff['type']
                                path = diff['path']
                                
                                if diff_type == 'added':
                                    st.success(f"➕ Added: {path}")
                                    st.json(diff['new_value'])
                                
                                elif diff_type == 'removed':
                                    st.error(f"➖ Removed: {path}")
                                    st.json(diff['old_value'])
                                
                                elif diff_type == 'modified':
                                    st.warning(f"🔄 Modified: {path}")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write("Old:")
                                        st.json(diff['old_value'])
                                    with col2:
                                        st.write("New:")
                                        st.json(diff['new_value'])
                        else:
                            st.info("No differences found between snapshots.")
                    
                    except Exception as e:
                        st.error(f"Error comparing snapshots: {str(e)}")
                
                # Clear comparison
                if st.button("❌ Cancel Comparison"):
                    del st.session_state['compare_snapshot']
                    st.rerun()
    
    def _render_audit_export(self):
        """Render audit trail export interface."""
        st.subheader("Audit Trail Export")
        
        st.info(
            "Export change history for compliance, auditing, or archival purposes. "
            "Exported files can be used for regulatory compliance or system analysis."
        )
        
        # Export configuration
        with st.form("export_audit_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Time range
                export_range = st.selectbox(
                    "Export Range",
                    [
                        "Last 24 Hours",
                        "Last 7 Days", 
                        "Last 30 Days",
                        "Last Quarter",
                        "Custom Range"
                    ]
                )
                
                if export_range == "Custom Range":
                    start_date = st.date_input(
                        "Start Date",
                        value=datetime.now() - timedelta(days=30)
                    )
                    end_date = st.date_input(
                        "End Date",
                        value=datetime.now()
                    )
                else:
                    # Calculate dates based on selection
                    end_date = datetime.now()
                    if export_range == "Last 24 Hours":
                        start_date = end_date - timedelta(days=1)
                    elif export_range == "Last 7 Days":
                        start_date = end_date - timedelta(days=7)
                    elif export_range == "Last 30 Days":
                        start_date = end_date - timedelta(days=30)
                    else:  # Last Quarter
                        start_date = end_date - timedelta(days=90)
            
            with col2:
                # Export options
                include_details = st.checkbox("Include change details", value=True)
                include_values = st.checkbox("Include old/new values", value=True)
                include_related = st.checkbox("Include related changes", value=False)
                
                # Format
                export_format = st.radio(
                    "Export Format",
                    ["JSON (Full detail)", "CSV (Summary)", "HTML (Report)"]
                )
            
            # Additional filters
            st.write("### Filters (Optional)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                category_filter = st.multiselect(
                    "Categories to Include",
                    [c.value for c in ChangeCategory],
                    default=[c.value for c in ChangeCategory]
                )
            
            with col2:
                entity_types = st.text_input(
                    "Entity Types (comma-separated)",
                    placeholder="Leave empty for all"
                )
            
            submitted = st.form_submit_button("📥 Generate Export")
            
            if submitted:
                # Generate filename
                filename = f"audit_trail_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
                
                if export_format.startswith("JSON"):
                    # Export as JSON
                    export_file = f"{filename}.json"
                    
                    with st.spinner("Generating export..."):
                        try:
                            # Create temporary file
                            import tempfile
                            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
                                self.change_tracker.export_changes(
                                    tmp.name,
                                    start_time=datetime.combine(start_date, datetime.min.time()),
                                    end_time=datetime.combine(end_date, datetime.max.time())
                                )
                                
                                # Read the file content
                                with open(tmp.name, 'r') as f:
                                    export_data = f.read()
                            
                            # Provide download button
                            st.download_button(
                                label="📥 Download Audit Trail (JSON)",
                                data=export_data,
                                file_name=export_file,
                                mime="application/json"
                            )
                            
                            st.success(f"Export generated successfully!")
                        
                        except Exception as e:
                            st.error(f"Error generating export: {str(e)}")
                
                elif export_format.startswith("CSV"):
                    # Export as CSV (summary only)
                    st.warning("CSV export includes summary information only")
                    
                    # Get changes and convert to DataFrame
                    changes = self.change_tracker.get_changes(
                        start_time=datetime.combine(start_date, datetime.min.time()),
                        end_time=datetime.combine(end_date, datetime.max.time()),
                        limit=10000
                    )
                    
                    if changes:
                        # Convert to DataFrame
                        df_data = []
                        for change in changes:
                            df_data.append({
                                'Timestamp': change.timestamp,
                                'Category': change.category.value,
                                'Type': change.change_type.value,
                                'Entity Type': change.entity_type,
                                'Entity ID': change.entity_id,
                                'Entity Name': change.entity_name,
                                'Description': change.description,
                                'User': change.user or 'System',
                                'Tags': ', '.join(change.tags)
                            })
                        
                        df = pd.DataFrame(df_data)
                        
                        # Provide download
                        csv_data = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Audit Trail (CSV)",
                            data=csv_data,
                            file_name=f"{filename}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No changes found for the specified period")
                
                else:
                    # HTML Report format
                    st.info("HTML report generation coming soon...")
        
        # Quick stats
        st.write("### Database Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Get total changes count
            total_changes = self.change_tracker.get_change_statistics()['total_changes']
            st.metric("Total Changes", f"{total_changes:,}")
        
        with col2:
            # Database size estimate
            db_path = Path(self.change_tracker.db_path)
            if db_path.exists():
                db_size_mb = db_path.stat().st_size / (1024 * 1024)
                st.metric("Database Size", f"{db_size_mb:.1f} MB")
        
        with col3:
            # Cleanup option
            if st.button("🧹 Cleanup Old Records"):
                if st.session_state.get('confirm_cleanup'):
                    deleted = self.change_tracker.cleanup_old_changes(days_to_keep=90)
                    st.success(f"Cleaned up {deleted} old records")
                    del st.session_state['confirm_cleanup']
                else:
                    st.session_state['confirm_cleanup'] = True
                    st.warning("Click again to confirm cleanup (keeps last 90 days)")
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format a timestamp to a human-readable 'time ago' string."""
        now = datetime.now()
        delta = now - timestamp
        
        if delta.days > 0:
            if delta.days == 1:
                return "1 day"
            else:
                return f"{delta.days} days"
        
        hours = delta.seconds // 3600
        if hours > 0:
            if hours == 1:
                return "1 hour"
            else:
                return f"{hours} hours"
        
        minutes = (delta.seconds % 3600) // 60
        if minutes > 0:
            if minutes == 1:
                return "1 minute"
            else:
                return f"{minutes} minutes"
        
        return "just now"
    
    def track_ui_change(
        self,
        entity_type: str,
        entity_id: str,
        entity_name: str,
        change_type: ChangeType,
        description: str,
        **kwargs
    ):
        """Helper method to track changes from UI actions."""
        return self.change_tracker.track_change(
            category=ChangeCategory.USER,
            change_type=change_type,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            user="current_user",  # TODO: Get actual user from session
            **kwargs
        )
