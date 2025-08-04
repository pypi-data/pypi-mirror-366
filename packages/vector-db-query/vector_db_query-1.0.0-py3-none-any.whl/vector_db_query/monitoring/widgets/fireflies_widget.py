"""Fireflies.ai monitoring widget for the dashboard."""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio

from ...data_sources.fireflies import FirefliesDataSource, FirefliesConfig
from ...utils.logger import get_logger

logger = get_logger(__name__)


class FirefliesMonitoringWidget:
    """Widget for monitoring Fireflies.ai integration in the dashboard."""
    
    def __init__(self):
        """Initialize the Fireflies monitoring widget."""
        self.source: Optional[FirefliesDataSource] = None
        self._initialize_source()
    
    def _initialize_source(self):
        """Initialize Fireflies data source."""
        try:
            # Try to load config
            config = FirefliesConfig()  # TODO: Load from saved config
            if config.api_key:
                self.source = FirefliesDataSource(config)
        except Exception as e:
            logger.error(f"Failed to initialize Fireflies source: {e}")
    
    async def _get_fireflies_status(self) -> Dict[str, Any]:
        """Get current status of Fireflies integration."""
        if not self.source:
            return {
                "configured": False,
                "error": "Fireflies not configured"
            }
        
        try:
            status = await self.source.get_status()
            return {
                "configured": True,
                **status
            }
        except Exception as e:
            logger.error(f"Failed to get Fireflies status: {e}")
            return {
                "configured": True,
                "error": str(e)
            }
    
    async def _get_recent_transcripts(self, days: int = 7) -> list:
        """Get recent transcripts."""
        if not self.source:
            return []
        
        try:
            # Authenticate if needed
            if not self.source._authenticated:
                await self.source.authenticate()
            
            # List recent transcripts
            since = datetime.utcnow() - timedelta(days=days)
            transcripts = await self.source.client.list_transcripts(
                since=since,
                limit=10
            )
            return transcripts
        except Exception as e:
            logger.error(f"Failed to get recent transcripts: {e}")
            return []
    
    async def _start_sync(self, since_days: int = 7) -> bool:
        """Start a sync operation."""
        if not self.source:
            return False
        
        try:
            since = datetime.utcnow() - timedelta(days=since_days)
            result = await self.source.sync(since=since)
            return result.success
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return False
    
    def render(self):
        """Render the Fireflies monitoring widget."""
        st.markdown("### 🎙️ Fireflies.ai Integration")
        
        # Get status
        status = asyncio.run(self._get_fireflies_status())
        
        if not status.get("configured"):
            st.warning("Fireflies.ai not configured. Run `vdq fireflies configure` to set up.")
            return
        
        # Display status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if status.get("api_connected"):
                st.metric(
                    "API Status",
                    "Connected",
                    delta="Active",
                    delta_color="normal"
                )
            else:
                st.metric(
                    "API Status",
                    "Disconnected",
                    delta="Inactive",
                    delta_color="inverse"
                )
        
        with col2:
            webhook_status = "Enabled" if status.get("webhook_enabled") else "Disabled"
            st.metric(
                "Webhook",
                webhook_status,
                delta=f"{status.get('webhook_events', 0)} events"
            )
        
        with col3:
            st.metric(
                "Transcripts",
                status.get("items_processed", 0),
                delta="Total processed"
            )
        
        with col4:
            if "api_quota" in status:
                quota = status["api_quota"]
                used_pct = (quota["used"] / quota["limit"] * 100) if quota["limit"] != "Unlimited" else 0
                st.metric(
                    "API Usage",
                    f"{quota['used']} min",
                    delta=f"{used_pct:.0f}% used" if quota["limit"] != "Unlimited" else "Unlimited"
                )
            else:
                st.metric("API Usage", "Unknown")
        
        # Show errors if any
        if "error" in status:
            st.error(f"Error: {status['error']}")
        
        # Sync controls
        st.markdown("#### Sync Controls")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            days = st.slider(
                "Sync transcripts from last N days",
                min_value=1,
                max_value=30,
                value=7,
                key="fireflies_sync_days"
            )
        
        with col2:
            if st.button("Start Sync", key="fireflies_sync_btn", type="primary"):
                with st.spinner("Syncing transcripts..."):
                    success = asyncio.run(self._start_sync(days))
                    if success:
                        st.success("Sync completed!")
                        st.rerun()
                    else:
                        st.error("Sync failed. Check logs for details.")
        
        # Recent transcripts
        with st.expander("Recent Transcripts", expanded=False):
            transcripts = asyncio.run(self._get_recent_transcripts())
            
            if transcripts:
                for transcript in transcripts[:5]:
                    date = datetime.fromisoformat(
                        transcript['date'].replace('Z', '+00:00')
                    ).strftime("%Y-%m-%d %H:%M")
                    duration = transcript.get('duration', 0) // 60
                    participants = len(transcript.get('participants', []))
                    
                    st.markdown(f"""
                    **{transcript.get('title', 'Untitled')}**  
                    📅 {date} | ⏱️ {duration} min | 👥 {participants} participants  
                    Platform: {transcript.get('organizer_platform', 'Unknown')}
                    """)
                    st.divider()
            else:
                st.info("No recent transcripts found")
        
        # Configuration info
        with st.expander("Configuration", expanded=False):
            st.markdown("**Filters:**")
            st.write(f"- Minimum duration: {status.get('min_duration_filter', 0)}s")
            
            if status.get('platform_filters'):
                st.write(f"- Platforms: {', '.join(status['platform_filters'])}")
            else:
                st.write("- Platforms: All")
            
            st.markdown("\n**Webhook Endpoint:**")
            st.code("POST https://your-domain.com/api/webhooks/fireflies")
            
            st.markdown("\n**CLI Commands:**")
            st.code("""
# Configure API
vdq fireflies configure

# List recent transcripts
vdq fireflies list --days 7

# Sync transcripts
vdq fireflies sync --days 30

# Check status
vdq fireflies status
            """, language="bash")