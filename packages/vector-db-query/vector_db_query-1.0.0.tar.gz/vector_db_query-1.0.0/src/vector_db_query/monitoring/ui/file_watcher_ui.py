"""
File Watcher UI components for real-time event monitoring.

This module provides Streamlit UI components for visualizing
file system events as they occur.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import deque, defaultdict
import json
from pathlib import Path

from ..scheduling.models import EventType, FileEvent
from ..scheduling.file_watcher import FileWatcher


class FileWatcherUI:
    """
    UI components for file system event monitoring.
    
    Provides real-time visualization of file system events.
    """
    
    def __init__(self, file_watcher: FileWatcher, max_events: int = 100):
        """
        Initialize file watcher UI.
        
        Args:
            file_watcher: File watcher instance
            max_events: Maximum number of events to keep in memory
        """
        self.file_watcher = file_watcher
        self.max_events = max_events
        
        # Event storage (in a real implementation, this would be in a database)
        if 'file_events' not in st.session_state:
            st.session_state.file_events = deque(maxlen=max_events)
        
        if 'event_stats' not in st.session_state:
            st.session_state.event_stats = defaultdict(int)
    
    def render_event_monitor(self):
        """Render the file system event monitor."""
        st.header("🔍 File System Event Monitor")
        
        # Control buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🗑️ Clear Events"):
                st.session_state.file_events.clear()
                st.session_state.event_stats.clear()
                st.success("Event history cleared")
        
        with col2:
            auto_scroll = st.checkbox("Auto-scroll", value=True)
        
        with col3:
            show_details = st.checkbox("Show Details", value=False)
        
        with col4:
            filter_event_type = st.selectbox(
                "Filter Events",
                ["All"] + [e.value for e in EventType],
                key="event_filter"
            )
        
        # Event statistics
        st.subheader("📊 Event Statistics")
        
        stats_cols = st.columns(5)
        event_types = [EventType.CREATED, EventType.MODIFIED, EventType.DELETED, EventType.MOVED]
        
        for idx, event_type in enumerate(event_types):
            with stats_cols[idx]:
                count = st.session_state.event_stats.get(event_type.value, 0)
                st.metric(
                    event_type.value.capitalize(),
                    count,
                    delta=f"+{count}" if count > 0 else None
                )
        
        with stats_cols[4]:
            total_events = sum(st.session_state.event_stats.values())
            st.metric("Total Events", total_events)
        
        # Real-time event stream
        st.subheader("📡 Real-Time Event Stream")
        
        # Create a container for events
        event_container = st.container()
        
        with event_container:
            # Filter events
            filtered_events = list(st.session_state.file_events)
            
            if filter_event_type != "All":
                filtered_events = [
                    e for e in filtered_events 
                    if e.get('event_type') == filter_event_type
                ]
            
            if not filtered_events:
                st.info("No events to display. File system events will appear here as they occur.")
            else:
                # Display events in reverse order (newest first)
                for event in reversed(filtered_events):
                    self._render_event_item(event, show_details)
        
        # Auto-refresh to show new events
        if st.button("🔄 Refresh Events"):
            st.rerun()
    
    def _render_event_item(self, event: Dict[str, Any], show_details: bool):
        """Render a single event item."""
        # Event type icon and color
        event_icons = {
            EventType.CREATED.value: ("📄", "#28a745"),
            EventType.MODIFIED.value: ("✏️", "#ffc107"),
            EventType.DELETED.value: ("🗑️", "#dc3545"),
            EventType.MOVED.value: ("📦", "#17a2b8"),
            "error": ("❌", "#dc3545")
        }
        
        icon, color = event_icons.get(
            event.get('event_type', 'error'),
            ("❓", "#6c757d")
        )
        
        # Create columns for event display
        col1, col2, col3 = st.columns([1, 6, 2])
        
        with col1:
            st.markdown(
                f"<span style='font-size: 1.5em;'>{icon}</span>",
                unsafe_allow_html=True
            )
        
        with col2:
            # File path and event type
            file_path = event.get('file_path', 'Unknown')
            event_type = event.get('event_type', 'Unknown')
            
            st.markdown(f"**{Path(file_path).name}**")
            st.caption(f"{event_type.upper()} - {file_path}")
            
            if show_details and event.get('details'):
                with st.expander("Details"):
                    st.json(event['details'])
        
        with col3:
            # Timestamp
            timestamp = event.get('timestamp')
            if timestamp:
                time_ago = self._format_time_ago(timestamp)
                st.caption(time_ago)
        
        # Divider
        st.divider()
    
    def add_event(self, event: FileEvent, schedule_id: str):
        """
        Add a new event to the UI.
        
        This would be called by the file watcher callback.
        """
        event_dict = {
            'event_type': event.event_type.value,
            'file_path': event.file_path,
            'is_directory': event.is_directory,
            'timestamp': event.timestamp,
            'schedule_id': schedule_id,
            'details': {
                'size': event.size,
                'old_path': event.old_path
            }
        }
        
        # Add to event queue
        st.session_state.file_events.append(event_dict)
        
        # Update statistics
        st.session_state.event_stats[event.event_type.value] += 1
    
    def render_watcher_config(self):
        """Render file watcher configuration panel."""
        st.header("⚙️ Watcher Configuration")
        
        # Get current watchers
        watcher_info = self.file_watcher.get_watcher_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Active Watchers", len(watcher_info))
            st.metric("Monitoring Status", 
                     "Running" if self.file_watcher.is_running else "Stopped")
        
        with col2:
            if self.file_watcher.is_running:
                if st.button("⏸️ Stop File Watcher", use_container_width=True):
                    self.file_watcher.stop()
                    st.success("File watcher stopped")
                    st.rerun()
            else:
                if st.button("▶️ Start File Watcher", use_container_width=True):
                    self.file_watcher.start()
                    st.success("File watcher started")
                    st.rerun()
        
        # Watcher details
        if watcher_info:
            st.subheader("Active Watch Paths")
            
            for schedule_id, info in watcher_info.items():
                with st.expander(f"Schedule: {schedule_id}"):
                    st.write(f"**Paths:** {', '.join(info['paths'])}")
                    st.write(f"**Patterns:** {', '.join(info['patterns'])}")
                    st.write(f"**Events:** {', '.join(info['event_types'])}")
                    st.write(f"**Recursive:** {'Yes' if info['recursive'] else 'No'}")
                    
                    if st.button(f"Remove Watcher", key=f"remove_{schedule_id}"):
                        self.file_watcher.remove_schedule(schedule_id)
                        st.success(f"Removed watcher for schedule {schedule_id}")
                        st.rerun()
    
    def render_event_patterns(self):
        """Render event pattern analysis."""
        st.header("📈 Event Patterns")
        
        if not st.session_state.file_events:
            st.info("No events to analyze. Patterns will appear once events are captured.")
            return
        
        # Time-based analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Event Timeline")
            
            # Group events by hour
            hourly_events = defaultdict(int)
            for event in st.session_state.file_events:
                if event.get('timestamp'):
                    hour = event['timestamp'].hour
                    hourly_events[hour] += 1
            
            # Create simple bar chart
            if hourly_events:
                hours = list(range(24))
                counts = [hourly_events.get(h, 0) for h in hours]
                
                chart_data = {
                    'Hour': hours,
                    'Events': counts
                }
                
                st.bar_chart(data=chart_data, x='Hour', y='Events', height=300)
        
        with col2:
            st.subheader("File Type Distribution")
            
            # Group by file extension
            extension_counts = defaultdict(int)
            for event in st.session_state.file_events:
                file_path = event.get('file_path', '')
                if file_path and not event.get('is_directory'):
                    ext = Path(file_path).suffix.lower() or 'no extension'
                    extension_counts[ext] += 1
            
            if extension_counts:
                # Show top 10 extensions
                sorted_exts = sorted(
                    extension_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
                
                for ext, count in sorted_exts:
                    col_ext, col_count = st.columns([3, 1])
                    with col_ext:
                        st.write(f"**{ext}**")
                    with col_count:
                        st.write(f"{count} events")
        
        # Most active directories
        st.subheader("🗂️ Most Active Directories")
        
        dir_counts = defaultdict(int)
        for event in st.session_state.file_events:
            file_path = event.get('file_path', '')
            if file_path:
                parent_dir = str(Path(file_path).parent)
                dir_counts[parent_dir] += 1
        
        if dir_counts:
            sorted_dirs = sorted(
                dir_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            for dir_path, count in sorted_dirs:
                col_dir, col_count = st.columns([4, 1])
                with col_dir:
                    st.write(f"📁 `{dir_path}`")
                with col_count:
                    st.write(f"{count} events")
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as time ago."""
        now = datetime.now()
        delta = now - timestamp
        
        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s ago"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() / 60)}m ago"
        elif delta.total_seconds() < 86400:
            return f"{int(delta.total_seconds() / 3600)}h ago"
        else:
            return timestamp.strftime("%Y-%m-%d %H:%M")
    
    def render_watcher_dashboard(self):
        """Render the complete file watcher dashboard."""
        tabs = st.tabs([
            "🔍 Event Monitor",
            "⚙️ Configuration",
            "📈 Patterns"
        ])
        
        with tabs[0]:
            self.render_event_monitor()
        
        with tabs[1]:
            self.render_watcher_config()
        
        with tabs[2]:
            self.render_event_patterns()