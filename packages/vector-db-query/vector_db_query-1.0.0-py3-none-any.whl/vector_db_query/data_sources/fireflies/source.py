"""Fireflies.ai data source implementation."""

import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator
from datetime import datetime, timedelta
from pathlib import Path

from ..base import AbstractDataSource, SyncResult
from ..models import ProcessedDocument
from .config import FirefliesConfig
from .client import FirefliesClient, FirefliesTranscript
from .processor import FirefliesTranscriptProcessor
from .webhook import FirefliesWebhookHandler
from ...utils.logger import get_logger

logger = get_logger(__name__)


class FirefliesDataSource(AbstractDataSource):
    """Data source for Fireflies.ai meeting transcripts."""
    
    def __init__(self, config: Optional[FirefliesConfig] = None, output_dir: Optional[Path] = None):
        """Initialize Fireflies data source.
        
        Args:
            config: Fireflies configuration
            output_dir: Directory to save transcripts
        """
        super().__init__()
        self.config = config or FirefliesConfig()
        self.client = FirefliesClient(self.config)
        self.processor = FirefliesTranscriptProcessor(output_dir)
        self.webhook_handler = FirefliesWebhookHandler(self.config)
        self._authenticated = False
    
    async def authenticate(self) -> bool:
        """Authenticate with Fireflies API.
        
        Returns:
            True if authentication successful
        """
        try:
            # Test API connection
            success = await self.client.test_connection()
            if success:
                self._authenticated = True
                logger.info("Successfully authenticated with Fireflies API")
            else:
                logger.error("Failed to authenticate with Fireflies API")
            
            return success
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def fetch_items(self, 
                         since: Optional[datetime] = None,
                         limit: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]:
        """Fetch transcripts from Fireflies.
        
        Args:
            since: Fetch items since this date
            limit: Maximum number of items to fetch
            
        Yields:
            Transcript data dictionaries
        """
        if not self._authenticated:
            if not await self.authenticate():
                raise Exception("Authentication required")
        
        # Default to last sync time or configured history
        if not since and self.last_sync_time:
            since = self.last_sync_time
        
        # Fetch transcripts
        async for transcript in self.client.fetch_transcripts(since=since, limit=limit):
            yield {
                "type": "transcript",
                "data": transcript
            }
    
    async def process_item(self, item: Dict[str, Any]) -> Optional[ProcessedDocument]:
        """Process a Fireflies item.
        
        Args:
            item: Item data from fetch_items
            
        Returns:
            ProcessedDocument if successful, None otherwise
        """
        try:
            item_type = item.get("type")
            
            if item_type == "transcript":
                transcript = item["data"]
                if isinstance(transcript, dict):
                    # Convert dict to FirefliesTranscript if needed
                    transcript = FirefliesTranscript.from_api_response(transcript)
                
                # Process transcript
                doc = self.processor.process_transcript(transcript)
                
                # Update metrics
                self.metrics["items_processed"] += 1
                self.metrics["last_item_time"] = datetime.utcnow()
                
                return doc
            
            else:
                logger.warning(f"Unknown item type: {item_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to process item: {e}")
            self.metrics["errors"] += 1
            return None
    
    async def sync(self,
                  since: Optional[datetime] = None,
                  limit: Optional[int] = None) -> SyncResult:
        """Perform full sync of Fireflies transcripts.
        
        Args:
            since: Sync items since this date
            limit: Maximum number of items to sync
            
        Returns:
            SyncResult with sync statistics
        """
        start_time = datetime.utcnow()
        processed_docs = []
        errors = []
        
        try:
            # Ensure authenticated
            if not self._authenticated:
                if not await self.authenticate():
                    return SyncResult(
                        source_type="fireflies",
                        started_at=start_time,
                        completed_at=datetime.utcnow(),
                        success=False,
                        items_fetched=0,
                        items_processed=0,
                        errors=["Authentication failed"]
                    )
            
            # Fetch and process items
            items_fetched = 0
            async for item in self.fetch_items(since=since, limit=limit):
                items_fetched += 1
                
                try:
                    doc = await self.process_item(item)
                    if doc:
                        processed_docs.append(doc)
                except Exception as e:
                    error_msg = f"Failed to process item: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
            
            # Update last sync time
            self.last_sync_time = datetime.utcnow()
            
            # Create sync result
            result = SyncResult(
                source_type="fireflies",
                started_at=start_time,
                completed_at=datetime.utcnow(),
                success=True,
                items_fetched=items_fetched,
                items_processed=len(processed_docs),
                errors=errors,
                processed_documents=processed_docs
            )
            
            logger.info(f"Fireflies sync completed: {result.items_processed}/{result.items_fetched} items processed")
            return result
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return SyncResult(
                source_type="fireflies",
                started_at=start_time,
                completed_at=datetime.utcnow(),
                success=False,
                items_fetched=0,
                items_processed=0,
                errors=[str(e)]
            )
    
    async def handle_webhook(self, headers: Dict[str, str], body: bytes) -> Dict[str, Any]:
        """Handle incoming webhook from Fireflies.
        
        Args:
            headers: Request headers
            body: Request body
            
        Returns:
            Processing result
        """
        result = await self.webhook_handler.handle_webhook(headers, body)
        
        # If transcript was processed, update metrics
        if result.get("status") == "processed":
            self.metrics["items_processed"] += 1
            self.metrics["webhook_events"] = self.metrics.get("webhook_events", 0) + 1
        
        return result
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of Fireflies integration.
        
        Returns:
            Status dictionary
        """
        status = await super().get_status()
        
        # Add Fireflies-specific status
        status.update({
            "api_connected": self._authenticated,
            "webhook_enabled": self.config.webhook_enabled,
            "webhook_events": self.metrics.get("webhook_events", 0),
            "min_duration_filter": self.config.min_duration_seconds,
            "platform_filters": self.config.platform_filters
        })
        
        # Check API quota if authenticated
        if self._authenticated:
            try:
                user_info = await self.client.get_user_info()
                status["api_quota"] = {
                    "used": user_info.get("minutesConsumed", 0),
                    "limit": user_info.get("minutesLimit", "Unlimited")
                }
            except:
                pass
        
        return status
    
    async def test_connection(self) -> bool:
        """Test connection to Fireflies.
        
        Returns:
            True if connection successful
        """
        return await self.authenticate()
    
    def get_webhook_handler(self) -> FirefliesWebhookHandler:
        """Get webhook handler instance.
        
        Returns:
            Webhook handler for FastAPI integration
        """
        return self.webhook_handler