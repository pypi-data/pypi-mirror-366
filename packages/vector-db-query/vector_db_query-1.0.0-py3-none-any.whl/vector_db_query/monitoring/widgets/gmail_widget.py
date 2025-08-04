"""Gmail monitoring widget for dashboard."""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio
import json

from ...data_sources.models import SourceType, SyncStatus
from ...data_sources.database.manager import DataSourceDatabaseManager
from ...data_sources.gmail.gmail_source import GmailDataSource
from ...data_sources.auth.storage import TokenStorage
from ...utils.logger import get_logger

logger = get_logger(__name__)


class GmailMonitoringWidget:
    """Widget for monitoring Gmail sync operations."""
    
    def __init__(self):
        """Initialize Gmail monitoring widget."""
        self.db_manager = DataSourceDatabaseManager()
        self.token_storage = TokenStorage()
        self.gmail_source = None
        
    async def _get_gmail_status(self) -> Dict[str, Any]:
        """Get current Gmail sync status.
        
        Returns:
            Status information
        """
        try:
            # Get sync state from database
            sync_state = await self.db_manager.get_sync_state(SourceType.GMAIL)
            
            # Get authentication status
            token = await self.token_storage.get(SourceType.GMAIL)
            is_authenticated = token is not None and token.access_token is not None
            
            # Get sync history
            recent_syncs = await self.db_manager.get_sync_history(
                SourceType.GMAIL,
                limit=10
            )
            
            # Calculate statistics
            total_processed = sum(s.items_processed for s in recent_syncs)
            total_failed = sum(s.items_failed for s in recent_syncs)
            
            # Get last successful sync
            last_success = None
            for sync in recent_syncs:
                if sync.status == SyncStatus.COMPLETED:
                    last_success = sync.completed_at
                    break
            
            # Check if sync is currently running
            is_syncing = False
            current_sync = None
            if recent_syncs and recent_syncs[0].status == SyncStatus.IN_PROGRESS:
                is_syncing = True
                current_sync = recent_syncs[0]
            
            return {
                'is_authenticated': is_authenticated,
                'is_syncing': is_syncing,
                'last_sync': sync_state.last_sync_timestamp if sync_state else None,
                'last_success': last_success,
                'total_processed': total_processed,
                'total_failed': total_failed,
                'recent_syncs': recent_syncs[:5],  # Last 5 syncs
                'current_sync': current_sync,
                'config': sync_state.configuration if sync_state else {}
            }
            
        except Exception as e:
            logger.error(f"Failed to get Gmail status: {e}")
            return {
                'error': str(e),
                'is_authenticated': False,
                'is_syncing': False
            }
    
    async def _start_sync(self, since_days: int = 1) -> bool:
        """Start Gmail sync operation.
        
        Args:
            since_days: Days of history to sync
            
        Returns:
            True if sync started successfully
        """
        try:
            # Initialize Gmail source if needed
            if not self.gmail_source:
                self.gmail_source = GmailDataSource()
            
            # Check authentication
            if not await self.gmail_source.authenticate():
                st.error("Gmail authentication required. Run: vdq auth setup --source gmail")
                return False
            
            # Start sync in background
            since_date = datetime.utcnow() - timedelta(days=since_days)
            
            # Create sync task
            async def sync_task():
                try:
                    result = await self.gmail_source.sync(since=since_date)
                    logger.info(f"Gmail sync completed: {result.items_processed} processed, {result.items_failed} failed")
                except Exception as e:
                    logger.error(f"Gmail sync failed: {e}")
            
            # Run in background
            asyncio.create_task(sync_task())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Gmail sync: {e}")
            st.error(f"Failed to start sync: {e}")
            return False
    
    def render(self):
        """Render the Gmail monitoring widget."""
        st.subheader("📧 Gmail Integration")
        
        # Get status asynchronously
        status = asyncio.run(self._get_gmail_status())
        
        if 'error' in status:
            st.error(f"Failed to load Gmail status: {status['error']}")
            return
        
        # Authentication status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if status['is_authenticated']:
                st.success("✅ Authenticated")
            else:
                st.error("❌ Not Authenticated")
                st.caption("Run: vdq auth setup --source gmail")
        
        with col2:
            if status['is_syncing']:
                st.info("🔄 Syncing...")
                if status['current_sync']:
                    st.caption(f"Started: {status['current_sync'].started_at.strftime('%H:%M:%S')}")
            else:
                st.info("⏸️ Idle")
        
        with col3:
            if status['last_sync']:
                time_ago = datetime.utcnow() - status['last_sync']
                if time_ago.total_seconds() < 3600:
                    mins = int(time_ago.total_seconds() / 60)
                    st.info(f"Last sync: {mins}m ago")
                else:
                    hours = int(time_ago.total_seconds() / 3600)
                    st.info(f"Last sync: {hours}h ago")
            else:
                st.info("Never synced")
        
        # Statistics
        st.markdown("### 📊 Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Processed", status['total_processed'])
        
        with col2:
            st.metric("Failed", status['total_failed'])
        
        with col3:
            success_rate = 0
            if status['total_processed'] > 0:
                success_rate = ((status['total_processed'] - status['total_failed']) / status['total_processed']) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col4:
            # Get configured labels
            config = status.get('config', {})
            labels = config.get('label_filters', ['INBOX'])
            st.metric("Monitored Labels", len(labels))
        
        # Sync controls
        st.markdown("### 🎮 Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Sync Now", disabled=status['is_syncing'] or not status['is_authenticated']):
                if asyncio.run(self._start_sync(since_days=1)):
                    st.success("Sync started!")
                    st.rerun()
        
        with col2:
            if st.button("📅 Sync Last 7 Days", disabled=status['is_syncing'] or not status['is_authenticated']):
                if asyncio.run(self._start_sync(since_days=7)):
                    st.success("Sync started for last 7 days!")
                    st.rerun()
        
        with col3:
            if st.button("🔄 Refresh Status"):
                st.rerun()
        
        # Recent sync history
        if status['recent_syncs']:
            st.markdown("### 📜 Recent Syncs")
            
            # Create table data
            table_data = []
            for sync in status['recent_syncs']:
                # Status icon
                if sync.status == SyncStatus.COMPLETED:
                    status_icon = "✅"
                elif sync.status == SyncStatus.FAILED:
                    status_icon = "❌"
                elif sync.status == SyncStatus.IN_PROGRESS:
                    status_icon = "🔄"
                else:
                    status_icon = "⚠️"
                
                # Duration
                duration = "-"
                if sync.completed_at and sync.started_at:
                    duration_sec = (sync.completed_at - sync.started_at).total_seconds()
                    if duration_sec < 60:
                        duration = f"{int(duration_sec)}s"
                    else:
                        duration = f"{int(duration_sec/60)}m {int(duration_sec%60)}s"
                
                table_data.append({
                    "Status": status_icon,
                    "Started": sync.started_at.strftime("%Y-%m-%d %H:%M"),
                    "Duration": duration,
                    "Processed": sync.items_processed,
                    "Failed": sync.items_failed
                })
            
            # Display as dataframe
            st.dataframe(table_data, use_container_width=True, hide_index=True)
        
        # Configuration summary
        with st.expander("⚙️ Current Configuration"):
            config = status.get('config', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Email Settings:**")
                st.write(f"- Account: {config.get('email_address', 'Default account')}")
                st.write(f"- Labels: {', '.join(config.get('label_filters', ['INBOX']))}")
                st.write(f"- Excluded: {', '.join(config.get('exclude_labels', ['SPAM', 'TRASH']))}")
            
            with col2:
                st.markdown("**Processing Settings:**")
                st.write(f"- Fetch attachments: {'Yes' if config.get('fetch_attachments', True) else 'No'}")
                st.write(f"- Max attachment size: {config.get('max_attachment_size_mb', 10)} MB")
                st.write(f"- Initial history: {config.get('initial_history_days', 30)} days")
        
        # Help section
        with st.expander("❓ Help"):
            st.markdown("""
            **Gmail Integration Help**
            
            1. **Setup Authentication**: Run `vdq auth setup --source gmail` to authenticate
            2. **Configure Settings**: Use `vdq config set --source gmail` to configure
            3. **Manual Sync**: Click "Sync Now" or run `vdq sync --source gmail`
            4. **Check Logs**: View detailed logs in the terminal or log files
            
            **Common Issues:**
            - Authentication expired: Re-run the auth setup command
            - No emails syncing: Check label filters in configuration
            - Sync failures: Check internet connection and Gmail API limits
            """)


def render_gmail_widget():
    """Helper function to render Gmail widget."""
    widget = GmailMonitoringWidget()
    widget.render()
