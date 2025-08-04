"""Gmail data source implementation."""

import asyncio
from typing import Dict, Any, Optional, AsyncIterator, List, Set
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib

from ..base import AbstractDataSource, DataSourceConfig, SyncResult
from ..models import SourceType, SyncStatus
from ..auth.storage import TokenStorage
from .gmail_auth import GmailOAuth2Provider
from .imap_client import GmailIMAPClient
from .config import GmailConfig
from .processors import EmailProcessingPipeline
from ...utils.logger import get_logger

logger = get_logger(__name__)


class GmailDataSource(AbstractDataSource):
    """Gmail data source for email integration."""
    
    def __init__(self, config: Optional[GmailConfig] = None):
        """Initialize Gmail data source.
        
        Args:
            config: Gmail configuration (uses default if not provided)
        """
        super().__init__(config or GmailConfig())
        self.config: GmailConfig = self.config  # Type hint
        
        self.auth_provider = GmailOAuth2Provider(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            redirect_uri=self.config.redirect_uri
        )
        
        self.token_storage = TokenStorage()
        self.imap_client = None
        self._processed_ids: Set[str] = set()
        self._load_processed_ids()
        
        # Initialize email processing pipeline
        pipeline_config = {
            'processors': ['content', 'meeting', 'attachment'],
            'continue_on_error': True,
            'content_config': {
                'extract_urls': self.config.extract_meeting_links,
                'extract_emails': True,
                'remove_signatures': True
            },
            'meeting_config': {
                'extract_zoom': True,
                'extract_teams': True,
                'extract_meet': True,
                'extract_calendar': self.config.extract_calendar_events
            },
            'attachment_config': {
                'max_file_size_mb': self.config.max_attachment_size_mb,
                'extract_text': True
            }
        }
        self.processing_pipeline = EmailProcessingPipeline(pipeline_config)
    
    def _load_processed_ids(self):
        """Load previously processed message IDs."""
        cache_file = Path(self.config.knowledge_base_path) / ".gmail_cache" / "processed_ids.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self._processed_ids = set(json.load(f))
                logger.info(f"Loaded {len(self._processed_ids)} processed message IDs")
            except Exception as e:
                logger.warning(f"Failed to load processed IDs: {e}")
    
    def _save_processed_ids(self):
        """Save processed message IDs."""
        cache_file = Path(self.config.knowledge_base_path) / ".gmail_cache" / "processed_ids.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(list(self._processed_ids), f)
        except Exception as e:
            logger.error(f"Failed to save processed IDs: {e}")
    
    async def authenticate(self) -> bool:
        """Authenticate with Gmail.
        
        Returns:
            True if authentication successful
        """
        try:
            # Check if we have a stored token
            token = await self.token_storage.get(SourceType.GMAIL)
            
            if token:
                # Validate token
                if await self.auth_provider.validate_token(token):
                    self.auth_token = token
                    self.is_authenticated = True
                    logger.info("Authenticated with stored token")
                    return True
                
                # Try to refresh if expired
                if token.refresh_token:
                    try:
                        new_token = await self.auth_provider.refresh(token)
                        await self.token_storage.store(SourceType.GMAIL, new_token)
                        self.auth_token = new_token
                        self.is_authenticated = True
                        logger.info("Refreshed expired token")
                        return True
                    except Exception as e:
                        logger.warning(f"Failed to refresh token: {e}")
            
            # No valid token - need manual authentication
            logger.warning("No valid Gmail authentication token found")
            logger.info("Please run: vdq auth setup --source gmail")
            return False
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test Gmail connection.
        
        Returns:
            True if connection successful
        """
        if not self.is_authenticated:
            if not await self.authenticate():
                return False
        
        try:
            # Create IMAP client
            email_address = self.config.email_address or self.auth_token.metadata.get('email')
            if not email_address:
                logger.error("No email address available")
                return False
            
            imap = GmailIMAPClient(email_address, self.auth_token.access_token)
            
            # Test connection
            if imap.connect():
                # List folders as connection test
                folders = imap.list_folders()
                logger.info(f"Connection successful. Found {len(folders)} folders")
                imap.disconnect()
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def fetch_items(self, 
                         since: Optional[datetime] = None, 
                         limit: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]:
        """Fetch emails from Gmail.
        
        Args:
            since: Fetch emails since this date
            limit: Maximum number of emails to fetch
            
        Yields:
            Email data dictionaries
        """
        if not self.is_authenticated:
            if not await self.authenticate():
                return
        
        # Determine email address
        email_address = self.config.email_address or self.auth_token.metadata.get('email')
        if not email_address:
            logger.error("No email address available")
            return
        
        # Create IMAP client
        self.imap_client = GmailIMAPClient(email_address, self.auth_token.access_token)
        
        try:
            # Connect to Gmail
            if not self.imap_client.connect():
                logger.error("Failed to connect to Gmail IMAP")
                return
            
            # Process each configured label
            for label in self.config.label_filters:
                # Skip excluded labels
                if label in self.config.exclude_labels:
                    continue
                
                logger.info(f"Processing label: {label}")
                
                # Select the folder
                success, count = self.imap_client.select_folder(label)
                if not success:
                    logger.warning(f"Failed to select folder: {label}")
                    continue
                
                # Determine search date
                search_since = since
                if not search_since:
                    # Use initial history days for first sync
                    search_since = datetime.utcnow() - timedelta(days=self.config.initial_history_days)
                
                # Search for messages
                message_ids = self.imap_client.search_messages(
                    criteria="ALL",
                    since_date=search_since,
                    limit=limit
                )
                
                logger.info(f"Found {len(message_ids)} messages in {label}")
                
                # Fetch each message
                processed_count = 0
                for msg_id in message_ids:
                    # Skip if already processed
                    if msg_id in self._processed_ids:
                        continue
                    
                    # Fetch message
                    message_data = self.imap_client.fetch_message(msg_id)
                    if not message_data:
                        continue
                    
                    # Apply filters
                    if not self._should_process_message(message_data):
                        continue
                    
                    # Add source info
                    message_data['source'] = {
                        'type': 'gmail',
                        'label': label,
                        'account': email_address
                    }
                    
                    yield message_data
                    
                    processed_count += 1
                    if limit and processed_count >= limit:
                        break
                
                # Check limit
                if limit and processed_count >= limit:
                    break
                    
        finally:
            # Disconnect
            if self.imap_client:
                self.imap_client.disconnect()
                self.imap_client = None
    
    def _should_process_message(self, message_data: Dict[str, Any]) -> bool:
        """Check if message should be processed based on filters.
        
        Args:
            message_data: Message data
            
        Returns:
            True if message should be processed
        """
        metadata = message_data.get('metadata', {})
        sender_email = metadata.get('sender_email', '')
        
        # Check whitelist
        if self.config.sender_whitelist:
            # If whitelist exists, sender must be in it
            if not any(allowed in sender_email for allowed in self.config.sender_whitelist):
                return False
        
        # Check blacklist
        if self.config.sender_blacklist:
            # If sender is in blacklist, skip
            if any(blocked in sender_email for blocked in self.config.sender_blacklist):
                return False
        
        return True
    
    async def process_item(self, item: Dict[str, Any]) -> Optional[Path]:
        """Process an email item and save to knowledge base.
        
        Args:
            item: Email data
            
        Returns:
            Path to saved file or None
        """
        try:
            # Run through processing pipeline
            processed_item = await self.processing_pipeline.process_email(item)
            
            # Generate unique filename
            message_id = processed_item['headers']['message_id']
            # Create safe filename from message ID
            safe_id = hashlib.md5(message_id.encode()).hexdigest()[:12]
            
            # Extract date for organization
            date = processed_item['date']
            year_month = date.strftime("%Y-%m")
            
            # Create file path
            filename = f"{date.strftime('%Y%m%d_%H%M%S')}_{safe_id}.json"
            file_path = Path(self.config.knowledge_base_path) / "gmail" / year_month / filename
            
            # Create directory
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for storage
            storage_data = {
                'source_type': 'gmail',
                'fetched_at': datetime.utcnow().isoformat(),
                'message': {
                    'id': processed_item['id'],
                    'headers': processed_item['headers'],
                    'date': processed_item['date'].isoformat(),
                    'body_text': processed_item['body_text'],
                    'body_html': processed_item['body_html'],
                    'attachments': processed_item['attachments'],
                    'metadata': processed_item['metadata']
                },
                'source_info': processed_item.get('source', {}),
                'processing_results': {
                    'content': processed_item.get('content', {}),
                    'meeting_info': processed_item.get('meeting_info', {}),
                    'processed_attachments': processed_item.get('processed_attachments', []),
                    'summary': processed_item.get('summary', {}),
                    'processing_metadata': processed_item.get('processing', {})
                }
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, indent=2, ensure_ascii=False)
            
            # Mark as processed
            self._processed_ids.add(item['id'])
            
            # Download attachments if configured
            if self.config.fetch_attachments and item['attachments']:
                await self._download_attachments(item, file_path.parent)
            
            # Mark as read in Gmail
            if self.imap_client and self.imap_client._connected:
                self.imap_client.mark_as_read(item['id'])
            
            logger.info(f"Processed email: {item['headers']['subject'][:50]}...")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to process email: {e}")
            return None
    
    async def _download_attachments(self, item: Dict[str, Any], save_dir: Path):
        """Download attachments for an email.
        
        Args:
            item: Email data
            save_dir: Directory to save attachments
        """
        if not self.imap_client or not self.imap_client._connected:
            logger.warning("IMAP client not connected, skipping attachments")
            return
        
        attachments_dir = save_dir / "attachments"
        attachments_dir.mkdir(exist_ok=True)
        
        for attachment in item['attachments']:
            filename = attachment['filename']
            size_mb = attachment['size'] / (1024 * 1024)
            
            # Check size limit
            if size_mb > self.config.max_attachment_size_mb:
                logger.warning(f"Skipping large attachment: {filename} ({size_mb:.1f} MB)")
                continue
            
            # Download attachment
            save_path = attachments_dir / filename
            
            # Run download in thread to avoid blocking
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self.imap_client.download_attachment,
                item['id'],
                filename,
                save_path
            )
            
            if success:
                logger.info(f"Downloaded attachment: {filename}")
            else:
                logger.warning(f"Failed to download attachment: {filename}")
    
    async def sync(self, 
                  since: Optional[datetime] = None, 
                  limit: Optional[int] = None) -> SyncResult:
        """Sync emails from Gmail.
        
        Args:
            since: Sync emails since this date
            limit: Maximum number of emails to sync
            
        Returns:
            SyncResult with sync statistics
        """
        result = SyncResult(
            source_type=SourceType.GMAIL,
            started_at=datetime.utcnow()
        )
        
        try:
            # Authenticate if needed
            if not self.is_authenticated:
                if not await self.authenticate():
                    result.status = SyncStatus.FAILED
                    result.errors.append("Authentication failed")
                    result.completed_at = datetime.utcnow()
                    return result
            
            # Fetch and process items
            async for item in self.fetch_items(since, limit):
                try:
                    # Process the item
                    saved_path = await self.process_item(item)
                    
                    if saved_path:
                        result.items_processed += 1
                        result.items_created.append(str(saved_path))
                    else:
                        result.items_failed += 1
                        
                except Exception as e:
                    logger.error(f"Failed to process item: {e}")
                    result.items_failed += 1
                    result.errors.append(str(e))
            
            # Save processed IDs
            self._save_processed_ids()
            
            # Set sync status
            if result.items_failed == 0:
                result.status = SyncStatus.COMPLETED
            else:
                result.status = SyncStatus.PARTIAL
                
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            result.status = SyncStatus.FAILED
            result.errors.append(str(e))
        
        result.completed_at = datetime.utcnow()
        return result
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for Gmail source.
        
        Returns:
            JSON schema for configuration
        """
        return {
            "type": "object",
            "properties": {
                "email_address": {
                    "type": "string",
                    "format": "email",
                    "description": "Gmail address (optional, uses authenticated account)"
                },
                "label_filters": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["INBOX"],
                    "description": "Gmail labels to sync"
                },
                "exclude_labels": {
                    "type": "array", 
                    "items": {"type": "string"},
                    "default": ["SPAM", "TRASH"],
                    "description": "Labels to exclude"
                },
                "sender_whitelist": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Only process emails from these senders"
                },
                "sender_blacklist": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Skip emails from these senders"
                },
                "fetch_attachments": {
                    "type": "boolean",
                    "default": True,
                    "description": "Download email attachments"
                },
                "max_attachment_size_mb": {
                    "type": "integer",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Maximum attachment size in MB"
                },
                "initial_history_days": {
                    "type": "integer",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 365,
                    "description": "Days of history to fetch on first sync"
                }
            }
        }