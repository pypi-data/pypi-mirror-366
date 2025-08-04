"""
Streaming UI component for real-time event monitoring.

This module provides UI components for configuring and monitoring
SSE event streams in the dashboard.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
import json
import asyncio
from collections import deque

from ..streaming import get_stream_manager, StreamManager
from ..streaming.event_streamer import get_event_streamer
from ..notifications.event_config import EventType
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class StreamingUI:
    """UI component for managing event streaming."""
    
    def __init__(self):
        """Initialize streaming UI."""
        self.stream_manager = get_stream_manager()
        self.event_streamer = get_event_streamer()
        self.change_tracker = get_change_tracker()
        
        # Initialize session state
        if 'streaming_client_id' not in st.session_state:
            st.session_state.streaming_client_id = None
        
        if 'streaming_connected' not in st.session_state:
            st.session_state.streaming_connected = False
        
        if 'streaming_events' not in st.session_state:
            st.session_state.streaming_events = deque(maxlen=100)
        
        if 'event_filter' not in st.session_state:
            st.session_state.event_filter = {
                'event_types': [],
                'sources': [],
                'min_priority': None
            }
    
    def render(self):
        """Render the streaming UI."""
        st.markdown("## 📡 Real-Time Event Streaming")
        
        # Create tabs
        tabs = st.tabs([
            "🔴 Live Stream",
            "⚙️ Stream Configuration", 
            "📊 Stream Statistics",
            "🔍 Event Inspector",
            "📋 Connection Manager"
        ])
        
        with tabs[0]:
            self._render_live_stream()
        
        with tabs[1]:
            self._render_stream_config()
        
        with tabs[2]:
            asyncio.run(self._render_stream_stats())
        
        with tabs[3]:
            self._render_event_inspector()
        
        with tabs[4]:
            asyncio.run(self._render_connection_manager())
    
    def _render_live_stream(self):
        """Render live event stream."""
        st.markdown("### Live Event Stream")
        
        # Connection controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if not st.session_state.streaming_connected:
                if st.button("🟢 Connect to Stream", type="primary", use_container_width=True):
                    asyncio.run(self._connect_to_stream())
            else:
                if st.button("🔴 Disconnect", type="secondary", use_container_width=True):
                    asyncio.run(self._disconnect_from_stream())
        
        with col2:
            st.metric("Status", 
                     "Connected" if st.session_state.streaming_connected else "Disconnected",
                     delta="Live" if st.session_state.streaming_connected else None)
        
        with col3:
            st.metric("Events", len(st.session_state.streaming_events))
        
        # Event stream display
        if st.session_state.streaming_connected:
            st.markdown("---")
            
            # Controls
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("🧹 Clear Events"):
                    st.session_state.streaming_events.clear()
                    st.rerun()
            
            with col2:
                auto_scroll = st.checkbox("Auto-scroll", value=True)
            
            with col3:
                pause_stream = st.checkbox("Pause Stream", value=False)
            
            # Event container
            event_container = st.container(height=500)
            
            with event_container:
                if not st.session_state.streaming_events:
                    st.info("👀 Waiting for events...")
                else:
                    # Display events in reverse order (newest first)
                    for event in reversed(st.session_state.streaming_events):
                        self._render_event_card(event)
            
            # Auto-refresh if connected and not paused
            if st.session_state.streaming_connected and not pause_stream:
                st.empty()  # Placeholder for auto-refresh
        
        else:
            st.info("🔌 Not connected. Click 'Connect to Stream' to start receiving events.")
    
    def _render_event_card(self, event: Dict[str, Any]):
        """Render a single event card."""
        # Determine event styling
        event_type = event.get('event_type', 'unknown')
        severity = event.get('data', {}).get('severity', 'info')
        
        # Color mapping
        severity_colors = {
            'critical': '🔴',
            'error': '🟠',
            'warning': '🟡',
            'info': '🔵',
            'debug': '⚪'
        }
        
        icon = severity_colors.get(severity, '⚪')
        
        # Create expandable card
        with st.expander(
            f"{icon} {event_type} - {event.get('timestamp', 'N/A')}",
            expanded=False
        ):
            # Event details
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Event Type:**")
                st.code(event_type)
                
                if 'source' in event.get('data', {}):
                    st.markdown("**Source:**")
                    st.code(event['data']['source'])
            
            with col2:
                st.markdown("**Severity:**")
                st.code(severity)
                
                if 'category' in event.get('data', {}):
                    st.markdown("**Category:**")
                    st.code(event['data']['category'])
            
            # Event data
            st.markdown("**Event Data:**")
            st.json(event.get('data', {}))
            
            # Timestamp
            st.caption(f"Received: {event.get('timestamp', 'Unknown')}")
    
    def _render_stream_config(self):
        """Render stream configuration."""
        st.markdown("### Stream Configuration")
        
        # Event filter configuration
        st.markdown("#### Event Filters")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Event type filter
            event_types = st.multiselect(
                "Event Types",
                options=[e.value for e in EventType],
                default=st.session_state.event_filter.get('event_types', []),
                help="Select event types to receive (empty = all)"
            )
            
            # Update filter
            st.session_state.event_filter['event_types'] = event_types
        
        with col2:
            # Source filter
            available_sources = ['system', 'scheduler', 'monitoring', 'service', 'user']
            sources = st.multiselect(
                "Event Sources",
                options=available_sources,
                default=st.session_state.event_filter.get('sources', []),
                help="Select event sources to receive (empty = all)"
            )
            
            st.session_state.event_filter['sources'] = sources
        
        # Priority filter
        st.markdown("#### Minimum Priority")
        priority_options = ['None', 'debug', 'info', 'warning', 'error', 'critical']
        min_priority = st.select_slider(
            "Minimum Event Priority",
            options=priority_options,
            value=st.session_state.event_filter.get('min_priority') or 'None'
        )
        
        st.session_state.event_filter['min_priority'] = None if min_priority == 'None' else min_priority
        
        # Connection preferences
        st.markdown("#### Connection Preferences")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            auto_reconnect = st.checkbox(
                "Auto-reconnect",
                value=True,
                help="Automatically reconnect on disconnect"
            )
        
        with col2:
            reconnect_delay = st.number_input(
                "Reconnect Delay (s)",
                min_value=1,
                max_value=60,
                value=5
            )
        
        with col3:
            max_reconnects = st.number_input(
                "Max Reconnect Attempts",
                min_value=1,
                max_value=50,
                value=10
            )
        
        # Apply configuration button
        if st.button("💾 Apply Configuration", type="primary"):
            # If connected, update filter
            if st.session_state.streaming_connected and st.session_state.streaming_client_id:
                asyncio.run(self.stream_manager.update_client_filter(
                    st.session_state.streaming_client_id,
                    st.session_state.event_filter
                ))
                st.success("✅ Configuration applied!")
            else:
                st.info("Configuration will be applied on next connection")
        
        # Display current configuration
        st.markdown("#### Current Configuration")
        st.json(st.session_state.event_filter)
    
    async def _render_stream_stats(self):
        """Render stream statistics."""
        st.markdown("### Stream Statistics")
        
        # Get statistics
        stats = await self.stream_manager.get_stats()
        streamer_stats = await self.event_streamer.get_streaming_stats()
        
        # Manager statistics
        st.markdown("#### Stream Manager")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Clients", stats['manager']['total_clients'])
        
        with col2:
            st.metric("Active Clients", stats['manager']['active_clients'])
        
        with col3:
            st.metric("Events Delivered", f"{stats['manager']['total_events_delivered']:,}")
        
        with col4:
            st.metric("Reconnects", stats['manager']['total_reconnects'])
        
        # Event streamer statistics
        st.markdown("#### Event Streamer")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Events Streamed", f"{streamer_stats['streaming']['events_streamed']:,}")
        
        with col2:
            st.metric("Events Filtered", f"{streamer_stats['streaming']['events_filtered']:,}")
        
        with col3:
            st.metric("Connections Served", streamer_stats['streaming']['connections_served'])
        
        with col4:
            uptime = streamer_stats['streaming']['uptime_seconds']
            if uptime:
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                st.metric("Uptime", f"{hours}h {minutes}m")
            else:
                st.metric("Uptime", "N/A")
        
        # SSE infrastructure statistics
        st.markdown("#### SSE Infrastructure")
        
        sse_stats = streamer_stats['sse']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Connections", sse_stats['active_connections'])
        
        with col2:
            st.metric("Total Events", f"{sse_stats['total_events_sent']:,}")
        
        with col3:
            st.metric("Error Rate", 
                     f"{(sse_stats['total_errors'] / max(sse_stats['total_events_sent'], 1) * 100):.1f}%")
        
        with col4:
            st.metric("Avg Events/sec", f"{sse_stats['average_events_per_second']:.1f}")
        
        # Client groups
        if stats['groups']:
            st.markdown("#### Client Groups")
            
            group_data = []
            for group, count in stats['groups'].items():
                group_data.append({
                    'Group': group,
                    'Client Count': count
                })
            
            st.dataframe(group_data, use_container_width=True)
    
    def _render_event_inspector(self):
        """Render event inspector."""
        st.markdown("### Event Inspector")
        
        # Event search
        search_term = st.text_input(
            "🔍 Search Events",
            placeholder="Search by type, source, or content..."
        )
        
        # Filter stored events
        filtered_events = []
        for event in st.session_state.streaming_events:
            if search_term.lower() in json.dumps(event).lower():
                filtered_events.append(event)
        
        # Display filtered events
        st.markdown(f"**Found {len(filtered_events)} events**")
        
        if filtered_events:
            # Event selector
            event_options = []
            for i, event in enumerate(filtered_events):
                timestamp = event.get('timestamp', 'Unknown')
                event_type = event.get('event_type', 'unknown')
                event_options.append(f"{i}: {event_type} - {timestamp}")
            
            selected_index = st.selectbox(
                "Select Event",
                range(len(event_options)),
                format_func=lambda x: event_options[x]
            )
            
            # Display selected event details
            if selected_index is not None:
                selected_event = filtered_events[selected_index]
                
                st.markdown("#### Event Details")
                
                # Basic info
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**Event ID:**")
                    st.code(selected_event.get('event_id', 'N/A'))
                    
                    st.markdown("**Event Type:**")
                    st.code(selected_event.get('event_type', 'N/A'))
                
                with col2:
                    st.markdown("**Timestamp:**")
                    st.code(selected_event.get('timestamp', 'N/A'))
                    
                    if 'retry' in selected_event:
                        st.markdown("**Retry:**")
                        st.code(f"{selected_event['retry']}ms")
                
                # Full event JSON
                st.markdown("**Full Event Data:**")
                st.json(selected_event)
                
                # Event actions
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("📋 Copy Event", use_container_width=True):
                        st.code(json.dumps(selected_event, indent=2))
                
                with col2:
                    if st.button("🔄 Replay Event", use_container_width=True):
                        # Simulate event replay
                        st.info("Event replay functionality coming soon")
        else:
            st.info("No events match your search criteria")
    
    async def _render_connection_manager(self):
        """Render connection manager."""
        st.markdown("### Connection Manager")
        
        # Get all clients
        stats = await self.stream_manager.get_stats()
        clients = stats.get('clients', [])
        
        if not clients:
            st.info("No clients registered")
        else:
            # Client list
            st.markdown(f"**Total Clients: {len(clients)}**")
            
            # Display clients in a table
            client_data = []
            for client in clients:
                client_data.append({
                    'Name': client['name'],
                    'Status': '🟢 Active' if client['is_active'] else '⚪ Inactive',
                    'Connected': client['connected_at'],
                    'Last Seen': client['last_seen'],
                    'Events': client['events_received'],
                    'Reconnects': client['reconnect_count'],
                    'Buffered': client['buffered_events']
                })
            
            st.dataframe(client_data, use_container_width=True)
            
            # Client actions
            st.markdown("#### Client Actions")
            
            client_names = [client['name'] for client in clients]
            selected_client = st.selectbox("Select Client", client_names)
            
            if selected_client:
                # Find selected client
                selected_client_data = next(
                    (c for c in clients if c['name'] == selected_client), 
                    None
                )
                
                if selected_client_data:
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        if st.button("📤 Send Test Event"):
                            await self.stream_manager.send_to_client(
                                selected_client_data['client_id'],
                                'test_event',
                                {
                                    'message': 'Test event from Connection Manager',
                                    'timestamp': datetime.now().isoformat()
                                }
                            )
                            st.success("Test event sent!")
                    
                    with col2:
                        if st.button("🔌 Disconnect Client"):
                            await self.stream_manager.disconnect_client(
                                selected_client_data['client_id']
                            )
                            st.success("Client disconnected")
                            st.rerun()
                    
                    with col3:
                        if st.button("❌ Remove Client"):
                            await self.stream_manager.unregister_client(
                                selected_client_data['client_id']
                            )
                            st.success("Client removed")
                            st.rerun()
    
    async def _connect_to_stream(self):
        """Connect to event stream."""
        try:
            # Register client if needed
            if not st.session_state.streaming_client_id:
                from ..streaming.stream_manager import register_dashboard_client
                client_id = await register_dashboard_client(
                    name=f"Dashboard-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    event_filter=st.session_state.event_filter
                )
                st.session_state.streaming_client_id = client_id
            
            # Define event handler
            def on_event(event: Dict[str, Any]):
                st.session_state.streaming_events.append(event)
            
            # Connect
            from ..streaming.stream_manager import connect_dashboard_client
            connected = await connect_dashboard_client(
                st.session_state.streaming_client_id,
                on_event=on_event
            )
            
            if connected:
                st.session_state.streaming_connected = True
                st.success("✅ Connected to event stream!")
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.SYSTEM,
                    change_type=ChangeType.UPDATE,
                    description="Dashboard connected to event stream",
                    details={'client_id': st.session_state.streaming_client_id}
                )
            else:
                st.error("Failed to connect to stream")
        
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
    
    async def _disconnect_from_stream(self):
        """Disconnect from event stream."""
        try:
            if st.session_state.streaming_client_id:
                from ..streaming.stream_manager import disconnect_dashboard_client
                await disconnect_dashboard_client(st.session_state.streaming_client_id)
                
                st.session_state.streaming_connected = False
                st.success("✅ Disconnected from stream")
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.SYSTEM,
                    change_type=ChangeType.UPDATE,
                    description="Dashboard disconnected from event stream",
                    details={'client_id': st.session_state.streaming_client_id}
                )
        
        except Exception as e:
            st.error(f"Disconnect error: {str(e)}")