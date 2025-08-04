"""Google Drive data source implementation for Gemini transcripts."""

import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator
from datetime import datetime, timedelta
from pathlib import Path

from ..base import AbstractDataSource, SyncResult
from ..models import ProcessedDocument, SourceType
from .config import GoogleDriveConfig
from .client import GoogleDriveClient
from .detector import GeminiTranscriptDetector
from .processor import GeminiProcessingPipeline
from ...utils.logger import get_logger

logger = get_logger(__name__)


class GoogleDriveDataSource(AbstractDataSource):
    """Data source for Google Drive files, specifically Gemini transcripts."""
    
    def __init__(self, config: Optional[GoogleDriveConfig] = None, output_dir: Optional[Path] = None):
        """Initialize Google Drive data source.
        
        Args:
            config: Google Drive configuration
            output_dir: Directory to save transcripts
        """
        super().__init__()
        self.config = config or GoogleDriveConfig()
        self.client = GoogleDriveClient(self.config)
        self.detector = GeminiTranscriptDetector()
        self.output_dir = output_dir or Path(self.config.knowledge_base_folder)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline = GeminiProcessingPipeline(self.output_dir)
        self._connected = False
    
    async def authenticate(self) -> bool:
        """Authenticate with Google Drive API.
        
        Returns:
            True if authentication successful
        """
        try:
            # Connect to Google Drive
            success = await self.client.connect()
            if success:
                self._connected = True
                logger.info("Successfully authenticated with Google Drive")
                
                # Get user info
                user_info = await self.client.get_user_info()
                user = user_info.get('user', {})
                logger.info(f"Connected as: {user.get('emailAddress', 'Unknown')}")
            else:
                logger.error("Failed to authenticate with Google Drive")
            
            return success
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    async def fetch_items(self, 
                         since: Optional[datetime] = None,
                         limit: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]:
        """Fetch Gemini transcripts from Google Drive.
        
        Args:
            since: Fetch items modified after this date
            limit: Maximum number of items to fetch
            
        Yields:
            File data dictionaries
        """
        if not self._connected:
            if not await self.authenticate():
                raise Exception("Authentication required")
        
        # Default to last sync time or configured history
        if not since and self.last_sync_time:
            since = self.last_sync_time
        elif not since:
            since = datetime.utcnow() - timedelta(days=self.config.initial_history_days)
        
        # Fetch transcripts
        async for file_data in self.client.fetch_transcripts(since=since, limit=limit):
            yield {
                "type": "gemini_transcript",
                "data": file_data
            }
    
    async def process_item(self, item: Dict[str, Any]) -> Optional[ProcessedDocument]:
        """Process a Google Drive item.
        
        Args:
            item: Item data from fetch_items
            
        Returns:
            ProcessedDocument if successful, None otherwise
        """
        try:
            item_type = item.get("type")
            
            if item_type == "gemini_transcript":
                file_data = item["data"]
                
                # Process the transcript
                doc = await self._process_gemini_transcript(file_data)
                
                if doc:
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
    
    async def _process_gemini_transcript(self, file_data: Dict[str, Any]) -> Optional[ProcessedDocument]:
        """Process a Gemini transcript file.
        
        Args:
            file_data: File data including content
            
        Returns:
            ProcessedDocument if successful
        """
        try:
            # Use processing pipeline
            result = await self.pipeline.process_transcript(file_data, save_structured=True)
            
            if not result['success']:
                logger.error(f"Pipeline processing failed: {result.get('error', 'Unknown error')}")
                return None
            
            # Extract key information
            file_id = file_data['id']
            file_name = file_data['name']
            modified_time = datetime.fromisoformat(file_data['modifiedTime'].replace('Z', '+00:00'))
            
            # Generate filename for raw content
            safe_name = "".join(c for c in file_name if c.isalnum() or c in " -_").rstrip()
            safe_name = safe_name.replace(" ", "_")[:100]
            filename = f"{modified_time.strftime('%Y%m%d_%H%M')}_{safe_name}_{file_id[:8]}.md"
            file_path = self.output_dir / filename
            
            # Save raw content
            file_path.write_text(file_data.get('content', ''), encoding='utf-8')
            
            # Create processed document with pipeline results
            structured = result.get('structured_content', {})
            doc = ProcessedDocument(
                source_id=f"gdrive_{file_id}",
                source_type="google_drive",
                title=structured.get('meeting_title', file_name),
                content=result['content'],
                metadata=result['metadata'],
                file_path=str(file_path),
                processed_at=datetime.utcnow(),
                embedding_status="pending"
            )
            
            # Add structured data to metadata
            doc.metadata['structured_data'] = {
                'summary': structured.get('summary'),
                'action_items': structured.get('action_items', []),
                'key_topics': structured.get('key_topics', []),
                'tab_count': len(structured.get('tabs', {})),
                'participants': structured.get('participants', [])
            }
            
            logger.info(f"Processed Gemini transcript: {file_name} (tabs: {doc.metadata['structured_data']['tab_count']})")
            return doc
            
        except Exception as e:
            logger.error(f"Failed to process Gemini transcript: {e}")
            return None
    
    def _extract_gemini_metadata(self, content: str, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from Gemini transcript content.
        
        Args:
            content: Transcript content
            file_data: Original file data
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "file_id": file_data['id'],
            "file_name": file_data['name'],
            "modified_time": file_data['modifiedTime'],
            "size_bytes": int(file_data.get('size', 0)),
            "web_view_link": file_data.get('webViewLink'),
            "transcript_type": "gemini",
            "confidence": file_data.get('confidence', 0.0)
        }
        
        # Use detector to validate and extract structured data
        validation = self.detector.validate_transcript(content)
        
        # Add validation results
        metadata['is_valid_gemini'] = validation['is_valid']
        metadata['validation_confidence'] = validation['confidence']
        
        # Add extracted metadata
        if validation['metadata']:
            metadata.update(validation['metadata'])
        
        # Add tab information
        if validation['tabs']:
            metadata['has_tabs'] = True
            metadata['tab_count'] = len(validation['tabs'])
            metadata['tab_names'] = [tab['name'] for tab in validation['tabs']]
        
        # Add any warnings
        if validation['warnings']:
            metadata['warnings'] = validation['warnings']
        
        return metadata
    
    async def sync(self,
                  since: Optional[datetime] = None,
                  limit: Optional[int] = None) -> SyncResult:
        """Perform full sync of Google Drive transcripts.
        
        Args:
            since: Sync items modified after this date
            limit: Maximum number of items to sync
            
        Returns:
            SyncResult with sync statistics
        """
        start_time = datetime.utcnow()
        processed_docs = []
        errors = []
        
        try:
            # Ensure authenticated
            if not self._connected:
                if not await self.authenticate():
                    return SyncResult(
                        source_type="google_drive",
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
                source_type="google_drive",
                started_at=start_time,
                completed_at=datetime.utcnow(),
                success=True,
                items_fetched=items_fetched,
                items_processed=len(processed_docs),
                errors=errors,
                processed_documents=processed_docs
            )
            
            logger.info(f"Google Drive sync completed: {result.items_processed}/{result.items_fetched} items processed")
            return result
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return SyncResult(
                source_type="google_drive",
                started_at=start_time,
                completed_at=datetime.utcnow(),
                success=False,
                items_fetched=0,
                items_processed=0,
                errors=[str(e)]
            )
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of Google Drive integration.
        
        Returns:
            Status dictionary
        """
        status = await super().get_status()
        
        # Add Google Drive-specific status
        status.update({
            "connected": self._connected,
            "search_patterns": self.config.search_patterns,
            "folder_ids": self.config.folder_ids,
            "output_dir": str(self.output_dir)
        })
        
        # Get storage quota if connected
        if self._connected:
            try:
                user_info = await self.client.get_user_info()
                storage = user_info.get('storage', {})
                if storage:
                    used = int(storage.get('usage', 0))
                    limit = int(storage.get('limit', 0))
                    status["storage_quota"] = {
                        "used_gb": round(used / (1024**3), 2),
                        "limit_gb": round(limit / (1024**3), 2),
                        "percent_used": round((used / limit * 100), 1) if limit > 0 else 0
                    }
            except:
                pass
        
        return status
    
    async def test_connection(self) -> bool:
        """Test connection to Google Drive.
        
        Returns:
            True if connection successful
        """
        if self._connected:
            return await self.client.test_connection()
        else:
            return await self.authenticate()