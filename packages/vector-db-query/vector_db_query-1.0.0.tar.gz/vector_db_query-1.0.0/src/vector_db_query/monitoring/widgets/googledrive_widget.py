"""Google Drive monitoring widget for Streamlit dashboard."""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio

from ...data_sources.googledrive import (
    GoogleDriveConfig,
    GoogleDriveDataSource
)
from ...utils.logger import get_logger

logger = get_logger(__name__)


def render_googledrive_widget(container=None):
    """Render Google Drive monitoring widget.
    
    Args:
        container: Streamlit container to render in
    """
    target = container if container else st
    
    with target.container():
        # Widget header
        col1, col2 = target.columns([3, 1])
        with col1:
            target.subheader("📄 Google Drive - Gemini Transcripts")
        with col2:
            if target.button("🔄", key="gdrive_refresh", help="Refresh Google Drive stats"):
                st.rerun()
        
        try:
            # Get Google Drive status
            status = asyncio.run(get_googledrive_status())
            
            # Connection status
            if status['connected']:
                target.success(f"✅ Connected as: {status.get('user_email', 'Unknown')}")
            else:
                target.error("❌ Not connected")
                if target.button("Connect to Google Drive", key="gdrive_connect"):
                    target.info("Run: `vdq googledrive configure` in terminal")
                return
            
            # Metrics columns
            col1, col2, col3, col4 = target.columns(4)
            
            with col1:
                target.metric(
                    "Files Processed",
                    status.get('items_processed', 0),
                    help="Total Gemini transcripts processed"
                )
            
            with col2:
                target.metric(
                    "Last Sync",
                    status.get('last_sync_display', 'Never'),
                    help="Time since last sync"
                )
            
            with col3:
                errors = status.get('errors', 0)
                target.metric(
                    "Errors",
                    errors,
                    delta=None if errors == 0 else f"+{errors}",
                    delta_color="inverse",
                    help="Processing errors"
                )
            
            with col4:
                if 'storage_quota' in status:
                    quota = status['storage_quota']
                    target.metric(
                        "Storage Used",
                        f"{quota['percent_used']}%",
                        f"{quota['used_gb']}/{quota['limit_gb']} GB",
                        help="Google Drive storage usage"
                    )
                else:
                    target.metric("Storage", "N/A")
            
            # Configuration details
            with target.expander("Configuration", expanded=False):
                col1, col2 = target.columns(2)
                
                with col1:
                    target.markdown("**Search Patterns:**")
                    for pattern in status.get('search_patterns', []):
                        target.code(pattern, language=None)
                
                with col2:
                    target.markdown("**Settings:**")
                    target.text(f"Output: {status.get('output_dir', 'Not set')}")
                    target.text(f"History: {status.get('history_days', 30)} days")
                    if status.get('folder_ids'):
                        target.text(f"Folders: {len(status['folder_ids'])} filtered")
            
            # Recent transcripts
            if 'recent_files' in status and status['recent_files']:
                with target.expander(f"Recent Transcripts ({len(status['recent_files'])})", expanded=True):
                    for file_info in status['recent_files'][:5]:
                        with target.container():
                            col1, col2, col3 = target.columns([3, 1, 1])
                            with col1:
                                target.text(file_info['name'][:50] + "..." if len(file_info['name']) > 50 else file_info['name'])
                            with col2:
                                target.caption(file_info['modified'])
                            with col3:
                                target.caption(f"Tabs: {file_info.get('tabs', 'N/A')}")
            
            # Quick actions
            col1, col2, col3 = target.columns(3)
            
            with col1:
                if target.button("🔍 Search Transcripts", key="gdrive_search", use_container_width=True):
                    target.info("Run: `vdq googledrive search` in terminal")
            
            with col2:
                if target.button("🔄 Sync Now", key="gdrive_sync", use_container_width=True):
                    target.info("Run: `vdq googledrive sync` in terminal")
            
            with col3:
                if target.button("📊 View Stats", key="gdrive_stats", use_container_width=True):
                    target.info("Run: `vdq googledrive status` in terminal")
            
        except Exception as e:
            logger.error(f"Error rendering Google Drive widget: {e}")
            target.error(f"Error loading Google Drive status: {str(e)}")


async def get_googledrive_status() -> Dict[str, Any]:
    """Get current Google Drive integration status.
    
    Returns:
        Status dictionary
    """
    try:
        # Initialize source
        config = GoogleDriveConfig()
        source = GoogleDriveDataSource(config)
        
        # Get base status
        status = await source.get_status()
        
        # Format last sync time
        if status.get('last_sync_time'):
            last_sync = datetime.fromisoformat(status['last_sync_time'])
            time_diff = datetime.utcnow() - last_sync
            
            if time_diff.days > 0:
                status['last_sync_display'] = f"{time_diff.days}d ago"
            elif time_diff.seconds > 3600:
                status['last_sync_display'] = f"{time_diff.seconds // 3600}h ago"
            elif time_diff.seconds > 60:
                status['last_sync_display'] = f"{time_diff.seconds // 60}m ago"
            else:
                status['last_sync_display'] = "Just now"
        else:
            status['last_sync_display'] = "Never"
        
        # Get recent files if connected
        if status.get('connected'):
            try:
                # Try to get user info
                if source._connected:
                    user_info = await source.client.get_user_info()
                    user = user_info.get('user', {})
                    status['user_email'] = user.get('emailAddress', 'Unknown')
                
                # Get recent transcripts
                recent_files = []
                since = datetime.utcnow() - timedelta(days=7)
                
                # This would need actual implementation to fetch recent files
                # For now, using mock data from status
                status['recent_files'] = recent_files
                
            except Exception as e:
                logger.debug(f"Could not fetch recent files: {e}")
        
        # Add configuration info
        status['history_days'] = config.initial_history_days
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get Google Drive status: {e}")
        return {
            'connected': False,
            'error': str(e)
        }


def get_googledrive_metrics() -> Dict[str, Any]:
    """Get Google Drive metrics for the main dashboard.
    
    Returns:
        Metrics dictionary
    """
    try:
        # Get status synchronously
        status = asyncio.run(get_googledrive_status())
        
        return {
            'name': 'Google Drive',
            'icon': '📄',
            'connected': status.get('connected', False),
            'items_processed': status.get('items_processed', 0),
            'last_sync': status.get('last_sync_display', 'Never'),
            'errors': status.get('errors', 0),
            'status': 'active' if status.get('connected') else 'inactive'
        }
        
    except Exception as e:
        logger.error(f"Failed to get Google Drive metrics: {e}")
        return {
            'name': 'Google Drive',
            'icon': '📄',
            'connected': False,
            'items_processed': 0,
            'last_sync': 'Error',
            'errors': 1,
            'status': 'error'
        }