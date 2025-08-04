"""Streamlit UI for data sources configuration."""

import streamlit as st
from pathlib import Path
import yaml
import json
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from ..data_sources.orchestrator import DataSourceOrchestrator
from ..data_sources.models import SourceType
from ..utils.config import get_config, update_config
from ..utils.logger import get_logger
from .ui.selective_processing_ui import render_selective_processing

logger = get_logger(__name__)


def render_datasources_config():
    """Render the data sources configuration UI."""
    st.title("🔧 Data Sources Configuration")
    
    # Load current configuration
    config = get_config()
    ds_config = config.get('data_sources', {})
    
    # Create tabs for different sections
    tabs = st.tabs(["Overview", "Gmail", "Fireflies", "Google Drive", "Deduplication", "Selective Processing", "Advanced"])
    
    # Overview Tab
    with tabs[0]:
        render_overview(ds_config)
    
    # Gmail Tab
    with tabs[1]:
        ds_config['gmail'] = render_gmail_config(ds_config.get('gmail', {}))
    
    # Fireflies Tab
    with tabs[2]:
        ds_config['fireflies'] = render_fireflies_config(ds_config.get('fireflies', {}))
    
    # Google Drive Tab
    with tabs[3]:
        ds_config['google_drive'] = render_google_drive_config(ds_config.get('google_drive', {}))
    
    # Deduplication Tab
    with tabs[4]:
        ds_config['deduplication'] = render_deduplication_config(ds_config.get('deduplication', {}))
    
    # Selective Processing Tab
    with tabs[5]:
        render_selective_processing()
    
    # Advanced Tab
    with tabs[6]:
        ds_config['processing'] = render_advanced_config(ds_config.get('processing', {}))
    
    # Save button
    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("💾 Save Configuration", type="primary", use_container_width=True):
            save_configuration(config, ds_config)
    
    with col3:
        if st.button("🧪 Test Connections", use_container_width=True):
            test_connections()


def render_overview(ds_config: Dict[str, Any]):
    """Render overview of all data sources."""
    st.header("Data Sources Overview")
    
    # Status summary
    col1, col2, col3, col4 = st.columns(4)
    
    enabled_count = sum(1 for source in ['gmail', 'fireflies', 'google_drive'] 
                       if ds_config.get(source, {}).get('enabled', False))
    
    with col1:
        st.metric("Enabled Sources", enabled_count)
    
    with col2:
        dedup_enabled = ds_config.get('deduplication', {}).get('enabled', True)
        st.metric("Deduplication", "ON" if dedup_enabled else "OFF")
    
    with col3:
        parallel = ds_config.get('processing', {}).get('parallel_sources', True)
        st.metric("Parallel Processing", "ON" if parallel else "OFF")
    
    with col4:
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    # Data sources status
    st.subheader("Source Status")
    
    # Create status dataframe
    status_data = []
    for source_type in ['gmail', 'fireflies', 'google_drive']:
        source_config = ds_config.get(source_type, {})
        status_data.append({
            'Source': source_type.title(),
            'Enabled': '✅' if source_config.get('enabled', False) else '❌',
            'Configured': '✅' if is_source_configured(source_type, source_config) else '⚠️',
            'Knowledge Base': source_config.get('knowledge_base_folder', 'Not set')
        })
    
    st.dataframe(status_data, use_container_width=True, hide_index=True)
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Enable All Sources"):
            st.info("Navigate to each source tab to enable and configure")
    
    with col2:
        if st.button("Run Full Sync"):
            run_full_sync()
    
    with col3:
        if st.button("View Logs"):
            st.info("Logs feature coming soon")


def render_gmail_config(gmail_config: Dict[str, Any]) -> Dict[str, Any]:
    """Render Gmail configuration."""
    st.header("📧 Gmail Configuration")
    
    # Enable/disable
    gmail_config['enabled'] = st.checkbox(
        "Enable Gmail Integration",
        value=gmail_config.get('enabled', False),
        help="Enable syncing emails from Gmail"
    )
    
    if gmail_config['enabled']:
        # Basic settings
        st.subheader("Basic Settings")
        
        gmail_config['email'] = st.text_input(
            "Gmail Address",
            value=gmail_config.get('email', ''),
            placeholder="your.email@gmail.com",
            help="The Gmail address to sync from"
        )
        
        # OAuth setup
        st.subheader("Authentication")
        
        oauth_file = gmail_config.get('oauth_credentials_file', '')
        uploaded_file = st.file_uploader(
            "Upload OAuth Credentials JSON",
            type=['json'],
            help="Download from Google Cloud Console"
        )
        
        if uploaded_file:
            # Save uploaded file
            creds_path = Path(".credentials") / "gmail_oauth.json"
            creds_path.parent.mkdir(exist_ok=True)
            creds_path.write_bytes(uploaded_file.read())
            gmail_config['oauth_credentials_file'] = str(creds_path)
            st.success("Credentials uploaded successfully!")
        elif oauth_file:
            st.info(f"Using credentials: {oauth_file}")
        
        # Folder selection
        st.subheader("Folder Selection")
        
        default_folders = gmail_config.get('folders', ['INBOX', '[Gmail]/Sent Mail'])
        
        col1, col2 = st.columns(2)
        with col1:
            inbox = st.checkbox("INBOX", value="INBOX" in default_folders)
            sent = st.checkbox("[Gmail]/Sent Mail", value="[Gmail]/Sent Mail" in default_folders)
            drafts = st.checkbox("[Gmail]/Drafts", value="[Gmail]/Drafts" in default_folders)
        
        with col2:
            spam = st.checkbox("[Gmail]/Spam", value="[Gmail]/Spam" in default_folders)
            trash = st.checkbox("[Gmail]/Trash", value="[Gmail]/Trash" in default_folders)
            starred = st.checkbox("[Gmail]/Starred", value="[Gmail]/Starred" in default_folders)
        
        # Build folder list
        folders = []
        if inbox: folders.append("INBOX")
        if sent: folders.append("[Gmail]/Sent Mail")
        if drafts: folders.append("[Gmail]/Drafts")
        if spam: folders.append("[Gmail]/Spam")
        if trash: folders.append("[Gmail]/Trash")
        if starred: folders.append("[Gmail]/Starred")
        
        # Custom folders
        custom = st.text_input(
            "Additional Folders (comma-separated)",
            placeholder="Label1, Label2",
            help="Add any custom labels or folders"
        )
        if custom:
            folders.extend([f.strip() for f in custom.split(',')])
        
        gmail_config['folders'] = folders
        
        # Sync settings
        st.subheader("Sync Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            gmail_config['initial_history_days'] = st.number_input(
                "Initial History Days",
                min_value=1,
                max_value=365,
                value=gmail_config.get('initial_history_days', 30),
                help="How many days of history to sync initially"
            )
        
        with col2:
            gmail_config['max_attachment_size_mb'] = st.number_input(
                "Max Attachment Size (MB)",
                min_value=1,
                max_value=100,
                value=gmail_config.get('max_attachment_size_mb', 25),
                help="Maximum size of attachments to download"
            )
        
        # Knowledge base
        st.subheader("Storage Settings")
        
        gmail_config['knowledge_base_folder'] = st.text_input(
            "Knowledge Base Folder",
            value=gmail_config.get('knowledge_base_folder', 'knowledge_base/emails/gmail'),
            help="Where to store processed emails"
        )
        
        # Advanced filters
        with st.expander("Advanced Filters"):
            st.write("Sender Filters")
            
            whitelist = st.text_area(
                "Sender Whitelist (one per line)",
                value='\n'.join(gmail_config.get('sender_whitelist', [])),
                help="Only sync emails from these senders"
            )
            gmail_config['sender_whitelist'] = [s.strip() for s in whitelist.split('\n') if s.strip()]
            
            blacklist = st.text_area(
                "Sender Blacklist (one per line)",
                value='\n'.join(gmail_config.get('sender_blacklist', [])),
                help="Never sync emails from these senders"
            )
            gmail_config['sender_blacklist'] = [s.strip() for s in blacklist.split('\n') if s.strip()]
            
            # Feature toggles
            st.write("Processing Options")
            gmail_config['extract_meeting_links'] = st.checkbox(
                "Extract Meeting Links",
                value=gmail_config.get('extract_meeting_links', True)
            )
            gmail_config['extract_calendar_events'] = st.checkbox(
                "Extract Calendar Events",
                value=gmail_config.get('extract_calendar_events', True)
            )
            gmail_config['fetch_attachments'] = st.checkbox(
                "Download Attachments",
                value=gmail_config.get('fetch_attachments', True)
            )
            gmail_config['mark_as_read'] = st.checkbox(
                "Mark Synced Emails as Read",
                value=gmail_config.get('mark_as_read', False)
            )
    
    return gmail_config


def render_fireflies_config(fireflies_config: Dict[str, Any]) -> Dict[str, Any]:
    """Render Fireflies configuration."""
    st.header("🎙️ Fireflies Configuration")
    
    # Enable/disable
    fireflies_config['enabled'] = st.checkbox(
        "Enable Fireflies Integration",
        value=fireflies_config.get('enabled', False),
        help="Enable syncing meeting transcripts from Fireflies.ai"
    )
    
    if fireflies_config['enabled']:
        # API settings
        st.subheader("API Configuration")
        
        fireflies_config['api_key'] = st.text_input(
            "API Key",
            value=fireflies_config.get('api_key', ''),
            type="password",
            help="Your Fireflies.ai API key"
        )
        
        # Webhook settings
        st.subheader("Webhook Settings")
        
        fireflies_config['webhook_enabled'] = st.checkbox(
            "Enable Webhook",
            value=fireflies_config.get('webhook_enabled', True),
            help="Receive real-time updates for new transcripts"
        )
        
        if fireflies_config['webhook_enabled']:
            fireflies_config['webhook_secret'] = st.text_input(
                "Webhook Secret",
                value=fireflies_config.get('webhook_secret', ''),
                type="password",
                help="Secret for webhook verification"
            )
            
            st.info("Webhook URL: https://your-domain.com/api/webhooks/fireflies")
        
        # Sync settings
        st.subheader("Sync Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            fireflies_config['initial_history_days'] = st.number_input(
                "Initial History Days",
                min_value=1,
                max_value=365,
                value=fireflies_config.get('initial_history_days', 30)
            )
        
        with col2:
            fireflies_config['sync_interval'] = st.number_input(
                "Sync Interval (minutes)",
                min_value=5,
                max_value=1440,
                value=fireflies_config.get('sync_interval', 60)
            )
        
        # Meeting filters
        st.subheader("Meeting Filters")
        
        col1, col2 = st.columns(2)
        with col1:
            min_duration = st.number_input(
                "Min Duration (minutes)",
                min_value=1,
                max_value=60,
                value=fireflies_config.get('min_duration_seconds', 300) // 60
            )
            fireflies_config['min_duration_seconds'] = min_duration * 60
        
        with col2:
            max_duration = st.number_input(
                "Max Duration (hours)",
                min_value=1,
                max_value=8,
                value=fireflies_config.get('max_duration_seconds', 14400) // 3600
            )
            fireflies_config['max_duration_seconds'] = max_duration * 3600
        
        # Platform filters
        st.write("Platform Filters")
        platforms = ['zoom', 'teams', 'meet', 'webex', 'other']
        selected_platforms = st.multiselect(
            "Include Only These Platforms",
            options=platforms,
            default=fireflies_config.get('platform_filters', []),
            help="Leave empty to include all platforms"
        )
        fireflies_config['platform_filters'] = selected_platforms
        
        # User filters
        with st.expander("User Filters"):
            included = st.text_area(
                "Include Only These Users (email, one per line)",
                value='\n'.join(fireflies_config.get('included_users', []))
            )
            fireflies_config['included_users'] = [u.strip() for u in included.split('\n') if u.strip()]
            
            excluded = st.text_area(
                "Exclude These Users (email, one per line)",
                value='\n'.join(fireflies_config.get('excluded_users', []))
            )
            fireflies_config['excluded_users'] = [u.strip() for u in excluded.split('\n') if u.strip()]
        
        # Storage settings
        st.subheader("Storage Settings")
        
        fireflies_config['output_dir'] = st.text_input(
            "Output Directory",
            value=fireflies_config.get('output_dir', 'knowledge_base/meetings/fireflies')
        )
    
    return fireflies_config


def render_google_drive_config(drive_config: Dict[str, Any]) -> Dict[str, Any]:
    """Render Google Drive configuration."""
    st.header("📁 Google Drive Configuration")
    
    # Enable/disable
    drive_config['enabled'] = st.checkbox(
        "Enable Google Drive Integration",
        value=drive_config.get('enabled', False),
        help="Enable syncing Gemini transcripts from Google Drive"
    )
    
    if drive_config['enabled']:
        # OAuth setup
        st.subheader("Authentication")
        
        oauth_file = drive_config.get('oauth_credentials_file', '')
        uploaded_file = st.file_uploader(
            "Upload OAuth Credentials JSON",
            type=['json'],
            help="Download from Google Cloud Console",
            key="gdrive_oauth"
        )
        
        if uploaded_file:
            # Save uploaded file
            creds_path = Path(".credentials") / "gdrive_oauth.json"
            creds_path.parent.mkdir(exist_ok=True)
            creds_path.write_bytes(uploaded_file.read())
            drive_config['oauth_credentials_file'] = str(creds_path)
            st.success("Credentials uploaded successfully!")
        elif oauth_file:
            st.info(f"Using credentials: {oauth_file}")
        
        # Search settings
        st.subheader("Search Configuration")
        
        # Search patterns
        patterns = st.text_area(
            "Search Patterns (one per line)",
            value='\n'.join(drive_config.get('search_patterns', ['Notes by Gemini'])),
            help="File name patterns to search for"
        )
        drive_config['search_patterns'] = [p.strip() for p in patterns.split('\n') if p.strip()]
        
        # Folder IDs
        folder_ids = st.text_area(
            "Specific Folder IDs (one per line)",
            value='\n'.join(drive_config.get('folder_ids', [])),
            placeholder="Leave empty to search all folders",
            help="Google Drive folder IDs to search in"
        )
        drive_config['folder_ids'] = [f.strip() for f in folder_ids.split('\n') if f.strip()]
        
        # Sync settings
        st.subheader("Sync Settings")
        
        drive_config['initial_history_days'] = st.number_input(
            "Initial History Days",
            min_value=1,
            max_value=365,
            value=drive_config.get('initial_history_days', 30)
        )
        
        # Storage settings
        st.subheader("Storage Settings")
        
        drive_config['knowledge_base_folder'] = st.text_input(
            "Knowledge Base Folder",
            value=drive_config.get('knowledge_base_folder', 'knowledge_base/meetings/gemini')
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            drive_config['include_shared_drives'] = st.checkbox(
                "Include Shared Drives",
                value=drive_config.get('include_shared_drives', True)
            )
            
            drive_config['follow_shortcuts'] = st.checkbox(
                "Follow Shortcuts",
                value=drive_config.get('follow_shortcuts', True)
            )
            
            drive_config['max_results_per_query'] = st.number_input(
                "Max Results Per Query",
                min_value=10,
                max_value=1000,
                value=drive_config.get('max_results_per_query', 100)
            )
    
    return drive_config


def render_deduplication_config(dedup_config: Dict[str, Any]) -> Dict[str, Any]:
    """Render deduplication configuration."""
    st.header("🔍 Deduplication Settings")
    
    # Enable/disable
    dedup_config['enabled'] = st.checkbox(
        "Enable Content Deduplication",
        value=dedup_config.get('enabled', True),
        help="Detect and handle duplicate content across sources"
    )
    
    if dedup_config['enabled']:
        # Threshold setting
        st.subheader("Similarity Detection")
        
        dedup_config['similarity_threshold'] = st.slider(
            "Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=dedup_config.get('similarity_threshold', 0.95),
            step=0.05,
            help="Higher values = more strict duplicate detection"
        )
        
        # Show what the threshold means
        threshold = dedup_config['similarity_threshold']
        if threshold >= 0.95:
            st.info("🎯 Very strict: Only nearly identical documents are duplicates")
        elif threshold >= 0.85:
            st.info("📊 Balanced: Similar documents with minor differences are duplicates")
        elif threshold >= 0.75:
            st.info("🔄 Lenient: Documents with moderate similarity are duplicates")
        else:
            st.warning("⚠️ Very lenient: Many documents may be marked as duplicates")
        
        # Cross-source checking
        st.subheader("Deduplication Scope")
        
        dedup_config['cross_source_check'] = st.checkbox(
            "Check Across All Sources",
            value=dedup_config.get('cross_source_check', True),
            help="Check for duplicates across Gmail, Fireflies, and Google Drive"
        )
        
        if dedup_config['cross_source_check']:
            st.info("Checking for duplicates across all data sources")
        else:
            st.info("Checking for duplicates only within each source")
        
        # Action on duplicates
        st.subheader("Duplicate Handling")
        
        dedup_config['skip_duplicates'] = st.checkbox(
            "Skip Duplicate Documents",
            value=dedup_config.get('skip_duplicates', True),
            help="Don't process documents identified as duplicates"
        )
        
        # Cache settings
        st.subheader("Cache Management")
        
        col1, col2 = st.columns(2)
        with col1:
            dedup_config['cleanup_days'] = st.number_input(
                "Keep Cache For (days)",
                min_value=7,
                max_value=365,
                value=dedup_config.get('cleanup_days', 90),
                help="How long to keep deduplication data"
            )
        
        with col2:
            if st.button("🧹 Clean Cache Now"):
                clean_dedup_cache()
        
        # Statistics
        st.subheader("Deduplication Statistics")
        show_dedup_stats()
    
    return dedup_config


def render_advanced_config(processing_config: Dict[str, Any]) -> Dict[str, Any]:
    """Render advanced processing configuration."""
    st.header("⚙️ Advanced Processing Settings")
    
    # Parallel processing
    st.subheader("Performance Settings")
    
    processing_config['parallel_sources'] = st.checkbox(
        "Process Sources in Parallel",
        value=processing_config.get('parallel_sources', True),
        help="Process multiple sources simultaneously for faster syncing"
    )
    
    if processing_config['parallel_sources']:
        processing_config['max_concurrent_items'] = st.number_input(
            "Max Concurrent Items",
            min_value=1,
            max_value=50,
            value=processing_config.get('max_concurrent_items', 10),
            help="Maximum number of items to process simultaneously"
        )
    
    # Retry settings
    st.subheader("Error Handling")
    
    col1, col2 = st.columns(2)
    with col1:
        processing_config['retry_attempts'] = st.number_input(
            "Retry Attempts",
            min_value=0,
            max_value=10,
            value=processing_config.get('retry_attempts', 3),
            help="Number of times to retry failed operations"
        )
    
    with col2:
        processing_config['retry_delay'] = st.number_input(
            "Retry Delay (seconds)",
            min_value=1,
            max_value=300,
            value=processing_config.get('retry_delay', 60),
            help="Wait time between retry attempts"
        )
    
    # NLP settings
    st.subheader("NLP Processing")
    
    nlp_config = processing_config.get('nlp', {})
    
    nlp_config['extract_entities'] = st.checkbox(
        "Extract Named Entities",
        value=nlp_config.get('extract_entities', True),
        help="Extract people, organizations, locations, etc."
    )
    
    nlp_config['analyze_sentiment'] = st.checkbox(
        "Analyze Sentiment",
        value=nlp_config.get('analyze_sentiment', True),
        help="Determine emotional tone of content"
    )
    
    nlp_config['extract_key_phrases'] = st.checkbox(
        "Extract Key Phrases",
        value=nlp_config.get('extract_key_phrases', True),
        help="Identify important phrases and topics"
    )
    
    processing_config['nlp'] = nlp_config
    
    # Logging
    st.subheader("Logging Settings")
    
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    processing_config['log_level'] = st.select_slider(
        "Log Level",
        options=log_levels,
        value=processing_config.get('log_level', 'INFO')
    )
    
    processing_config['log_to_file'] = st.checkbox(
        "Log to File",
        value=processing_config.get('log_to_file', True)
    )
    
    if processing_config['log_to_file']:
        processing_config['log_directory'] = st.text_input(
            "Log Directory",
            value=processing_config.get('log_directory', '.logs/data_sources')
        )
    
    return processing_config


def is_source_configured(source_type: str, config: Dict[str, Any]) -> bool:
    """Check if a source is properly configured."""
    if source_type == 'gmail':
        return bool(config.get('email') and config.get('oauth_credentials_file'))
    elif source_type == 'fireflies':
        return bool(config.get('api_key'))
    elif source_type == 'google_drive':
        return bool(config.get('oauth_credentials_file'))
    return False


def save_configuration(config: Dict[str, Any], ds_config: Dict[str, Any]):
    """Save configuration to file."""
    try:
        config['data_sources'] = ds_config
        
        # Write to config file
        config_path = Path("config/default.yaml")
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        st.success("✅ Configuration saved successfully!")
        st.info(f"Configuration file: {config_path}")
        
    except Exception as e:
        st.error(f"Failed to save configuration: {e}")
        logger.error(f"Configuration save failed: {e}")


def test_connections():
    """Test data source connections."""
    with st.spinner("Testing connections..."):
        asyncio.run(_test_connections_async())


async def _test_connections_async():
    """Async function to test connections."""
    try:
        orchestrator = DataSourceOrchestrator()
        await orchestrator.initialize_sources()
        
        results = []
        for source_type, source in orchestrator.sources.items():
            try:
                success = await source.test_connection()
                results.append({
                    'Source': source_type.value.title(),
                    'Status': '✅ Connected' if success else '❌ Failed',
                    'Message': 'Connection successful' if success else 'Connection failed'
                })
            except Exception as e:
                results.append({
                    'Source': source_type.value.title(),
                    'Status': '❌ Error',
                    'Message': str(e)
                })
        
        # Display results
        for result in results:
            if '✅' in result['Status']:
                st.success(f"{result['Source']}: {result['Status']}")
            else:
                st.error(f"{result['Source']}: {result['Status']} - {result['Message']}")
                
    except Exception as e:
        st.error(f"Test failed: {e}")


def run_full_sync():
    """Run full sync for all enabled sources."""
    with st.spinner("Running full sync..."):
        asyncio.run(_run_full_sync_async())


async def _run_full_sync_async():
    """Async function to run full sync."""
    try:
        orchestrator = DataSourceOrchestrator()
        await orchestrator.initialize_sources()
        
        results = await orchestrator.sync_all()
        
        # Display results
        for source_type, result in results.items():
            if result.errors:
                st.warning(f"{source_type.value.title()}: {result.items_processed} processed, {len(result.errors)} errors")
            else:
                st.success(f"{source_type.value.title()}: {result.items_processed} items processed")
                
    except Exception as e:
        st.error(f"Sync failed: {e}")


def clean_dedup_cache():
    """Clean deduplication cache."""
    try:
        orchestrator = DataSourceOrchestrator()
        removed = orchestrator.cleanup_old_duplicates(90)  # 90 days
        st.success(f"Removed {removed} old deduplication entries")
    except Exception as e:
        st.error(f"Cleanup failed: {e}")


def show_dedup_stats():
    """Show deduplication statistics."""
    try:
        orchestrator = DataSourceOrchestrator()
        stats = orchestrator.get_deduplication_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Documents", f"{stats.get('total_documents', 0):,}")
        with col2:
            st.metric("Unique Documents", f"{stats.get('unique_documents', 0):,}")
        with col3:
            duplicate_rate = 0
            if stats.get('total_documents', 0) > 0:
                duplicate_rate = (1 - stats.get('unique_documents', 0) / stats['total_documents']) * 100
            st.metric("Duplicate Rate", f"{duplicate_rate:.1f}%")
            
    except Exception as e:
        st.info("No deduplication statistics available yet")


if __name__ == "__main__":
    render_datasources_config()