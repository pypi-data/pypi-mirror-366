"""Orchestrator for managing multiple data sources."""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path

from .base import AbstractDataSource, DataSourceConfig, SyncResult
from .models import SourceType, SyncState, ProcessedDocument
from .deduplication import ContentDeduplicator
from .filters import SelectiveProcessor
from .exceptions import DataSourceError, ConfigurationError
from ..utils.logger import get_logger
from ..utils.config import get_config

logger = get_logger(__name__)


class DataSourceOrchestrator:
    """Manages and coordinates multiple data sources."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize orchestrator with configuration."""
        self.sources: Dict[SourceType, AbstractDataSource] = {}
        self.sync_states: Dict[SourceType, SyncState] = {}
        self.config = get_config() if isinstance(get_config(), dict) else {}
        self._running = False
        self._sync_tasks: Dict[SourceType, asyncio.Task] = {}
        
        # Initialize deduplication system
        cache_dir = Path(".cache/deduplication")
        self.deduplicator = ContentDeduplicator(cache_dir)
        
        # Initialize selective processing
        filter_config = self.config.get('data_sources', {}).get('selective_processing', {})
        self.selective_processor = SelectiveProcessor(filter_config)
        
        # Load data source specific config
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, config_path: Path):
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                
            # Merge with existing config
            if 'data_sources' in config_data:
                self.config.data_sources = config_data['data_sources']
                
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise ConfigurationError(f"Invalid configuration file: {e}")
    
    def register_source(self, source_type: SourceType, source: AbstractDataSource):
        """Register a data source with the orchestrator.
        
        Args:
            source_type: Type of the source
            source: Data source instance
        """
        self.sources[source_type] = source
        
        # Initialize sync state if not exists
        if source_type not in self.sync_states:
            self.sync_states[source_type] = SyncState(source_type=source_type)
        
        logger.info(f"Registered data source: {source_type.value}")
    
    async def initialize_sources(self):
        """Initialize all registered sources."""
        # Import source implementations here to avoid circular imports
        from .gmail import GmailDataSource, GmailConfig
        from .fireflies import FirefliesDataSource, FirefliesConfig
        from .googledrive import GoogleDriveDataSource, GoogleDriveConfig
        
        # Gmail configuration
        if self.config.get('data_sources', {}).get('gmail', {}).get('enabled', False):
            gmail_config_data = self.config.get('data_sources', {}).get('gmail', {})
            gmail_config = GmailConfig.from_dict(gmail_config_data)
            gmail_source = GmailDataSource(gmail_config)
            self.register_source(SourceType.GMAIL, gmail_source)
        
        # Fireflies configuration
        if self.config.get('data_sources', {}).get('fireflies', {}).get('enabled', False):
            fireflies_config_data = self.config.get('data_sources', {}).get('fireflies', {})
            fireflies_config = FirefliesConfig(**fireflies_config_data)
            fireflies_source = FirefliesDataSource(fireflies_config)
            self.register_source(SourceType.FIREFLIES, fireflies_source)
        
        # Google Drive configuration
        if self.config.get('data_sources', {}).get('google_drive', {}).get('enabled', False):
            drive_config_data = self.config.get('data_sources', {}).get('google_drive', {})
            drive_config = GoogleDriveConfig.from_config(drive_config_data)
            drive_source = GoogleDriveDataSource(drive_config)
            self.register_source(SourceType.GOOGLE_DRIVE, drive_source)
        
        logger.info(f"Initialized {len(self.sources)} data sources")
    
    async def sync_source(self, source_type: SourceType) -> SyncResult:
        """Sync a specific data source.
        
        Args:
            source_type: Type of source to sync
            
        Returns:
            SyncResult from the sync operation
        """
        if source_type not in self.sources:
            raise DataSourceError(f"Source {source_type.value} not registered")
        
        source = self.sources[source_type]
        sync_state = self.sync_states[source_type]
        
        # Check if source is active
        if not sync_state.is_active:
            logger.warning(f"Source {source_type.value} is inactive, skipping sync")
            return SyncResult(source_type=source_type.value)
        
        try:
            # Perform sync
            result = await source.sync(since=sync_state.last_sync_timestamp)
            
            # Apply selective processing filters
            result = await self._apply_selective_processing(result, source_type)
            
            # Process documents with deduplication if enabled
            if self.config.get('data_sources', {}).get('deduplication', {}).get('enabled', True):
                result = await self._process_with_deduplication(result, source_type)
            
            # Update sync state on success
            if result.items_processed > 0 or len(result.errors) == 0:
                sync_state.last_sync_timestamp = datetime.utcnow()
                sync_state.clear_errors()
            
            return result
            
        except Exception as e:
            # Record error in sync state
            sync_state.record_error(str(e))
            
            # Disable source after too many errors
            if sync_state.error_count >= 5:
                sync_state.is_active = False
                logger.error(f"Disabling {source_type.value} after {sync_state.error_count} errors")
            
            raise
    
    async def sync_all(self) -> Dict[SourceType, SyncResult]:
        """Sync all registered data sources.
        
        Returns:
            Dict mapping source types to their sync results
        """
        results = {}
        
        # Run syncs in parallel if configured
        if self.config.data_sources.get('processing', {}).get('parallel_sources', True):
            tasks = []
            for source_type in self.sources:
                task = asyncio.create_task(self.sync_source(source_type))
                tasks.append((source_type, task))
            
            for source_type, task in tasks:
                try:
                    results[source_type] = await task
                except Exception as e:
                    logger.error(f"Sync failed for {source_type.value}: {e}")
                    results[source_type] = SyncResult(
                        source_type=source_type.value,
                        errors=[str(e)]
                    )
        else:
            # Run syncs sequentially
            for source_type in self.sources:
                try:
                    results[source_type] = await self.sync_source(source_type)
                except Exception as e:
                    logger.error(f"Sync failed for {source_type.value}: {e}")
                    results[source_type] = SyncResult(
                        source_type=source_type.value,
                        errors=[str(e)]
                    )
        
        return results
    
    async def start_scheduled_sync(self):
        """Start scheduled sync tasks for all sources."""
        self._running = True
        
        for source_type, source in self.sources.items():
            # Start a sync task for each source
            task = asyncio.create_task(
                self._sync_loop(source_type, source.config.sync_interval)
            )
            self._sync_tasks[source_type] = task
        
        logger.info("Started scheduled sync for all sources")
    
    async def _sync_loop(self, source_type: SourceType, interval: int):
        """Run sync loop for a specific source."""
        while self._running:
            try:
                # Perform sync
                result = await self.sync_source(source_type)
                logger.info(
                    f"{source_type.value} sync completed: "
                    f"{result.items_processed} processed, "
                    f"{result.items_failed} failed"
                )
                
                # Wait for next sync
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in sync loop for {source_type.value}: {e}")
                # Wait before retrying
                await asyncio.sleep(60)  # 1 minute retry delay
    
    async def stop_scheduled_sync(self):
        """Stop all scheduled sync tasks."""
        self._running = False
        
        # Cancel all sync tasks
        for task in self._sync_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._sync_tasks.values(), return_exceptions=True)
        
        self._sync_tasks.clear()
        logger.info("Stopped scheduled sync for all sources")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for all data sources.
        
        Returns:
            Dict containing metrics for each source
        """
        metrics = {}
        
        for source_type, source in self.sources.items():
            try:
                source_metrics = await source.get_metrics()
                sync_state = self.sync_states[source_type]
                
                metrics[source_type.value] = {
                    'metrics': source_metrics,
                    'sync_state': {
                        'last_sync': sync_state.last_sync_timestamp.isoformat() 
                                    if sync_state.last_sync_timestamp else None,
                        'is_active': sync_state.is_active,
                        'error_count': sync_state.error_count,
                        'last_error': sync_state.last_error
                    }
                }
            except Exception as e:
                logger.error(f"Failed to get metrics for {source_type.value}: {e}")
                metrics[source_type.value] = {
                    'error': str(e)
                }
        
        return metrics
    
    async def cleanup(self):
        """Cleanup all data sources."""
        # Stop scheduled syncs
        await self.stop_scheduled_sync()
        
        # Cleanup each source
        for source in self.sources.values():
            try:
                await source.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up source: {e}")
    
    async def _apply_selective_processing(self,
                                         result: SyncResult,
                                         source_type: SourceType) -> SyncResult:
        """Apply selective processing filters to sync result.
        
        Args:
            result: Original sync result
            source_type: Type of source
            
        Returns:
            Updated sync result with filters applied
        """
        if not result.processed_documents:
            return result
        
        # Check if selective processing is enabled
        if not self.config.get('data_sources', {}).get('selective_processing', {}).get('enabled', True):
            return result
        
        # Filter documents
        filtered_docs = []
        excluded_count = 0
        
        for doc in result.processed_documents:
            # Convert document to item format for filter evaluation
            item = {
                'id': doc.source_id,
                'headers': {'subject': doc.title} if source_type == SourceType.GMAIL else {},
                'title': doc.title,
                'name': doc.title,
                'date': doc.processed_at.isoformat() if doc.processed_at else None,
                'modifiedTime': doc.processed_at.isoformat() if doc.processed_at else None,
                'body_text': doc.content,
                'content': doc.content,
                'metadata': doc.metadata,
                'attachments': doc.metadata.get('attachments', []) if doc.metadata else [],
                'size': len(doc.content.encode('utf-8')) if doc.content else 0,
                'duration': doc.metadata.get('duration') if doc.metadata else None
            }
            
            # Add source-specific fields
            if source_type == SourceType.GMAIL and doc.metadata:
                item['metadata']['sender_email'] = doc.metadata.get('sender_email', '')
            
            # Check if item should be processed
            if self.selective_processor.should_process(item, source_type.value):
                filtered_docs.append(doc)
            else:
                excluded_count += 1
                logger.debug(f"Excluded {source_type.value} item: {doc.source_id}")
        
        # Update result
        result.processed_documents = filtered_docs
        result.items_processed = len(filtered_docs)
        
        # Add filtering stats to metadata
        if not hasattr(result, 'metadata'):
            result.metadata = {}
        
        result.metadata['selective_processing'] = {
            'total_items': len(result.processed_documents) + excluded_count,
            'excluded_count': excluded_count,
            'included_count': len(filtered_docs),
            'exclusion_rate': excluded_count / (len(result.processed_documents) + excluded_count) if (len(result.processed_documents) + excluded_count) > 0 else 0
        }
        
        if excluded_count > 0:
            logger.info(
                f"Selective processing for {source_type.value}: "
                f"{excluded_count} items excluded, "
                f"{len(filtered_docs)} items kept"
            )
        
        return result
    
    async def _process_with_deduplication(self, 
                                        result: SyncResult, 
                                        source_type: SourceType) -> SyncResult:
        """Process sync result with deduplication.
        
        Args:
            result: Original sync result
            source_type: Type of source
            
        Returns:
            Updated sync result with deduplication applied
        """
        if not result.processed_documents:
            return result
        
        # Get deduplication settings
        dedup_config = self.config.get('data_sources', {}).get('deduplication', {})
        threshold = dedup_config.get('similarity_threshold', 0.95)
        cross_source = dedup_config.get('cross_source_check', True)
        
        # Process each document
        deduplicated_docs = []
        duplicate_count = 0
        
        for doc in result.processed_documents:
            # Check for duplicates
            dedup_result = self.deduplicator.check_duplicate(
                doc,
                source_type=None if cross_source else source_type.value,
                threshold=threshold
            )
            
            if dedup_result.is_duplicate:
                duplicate_count += 1
                logger.info(
                    f"Duplicate found: {doc.title} "
                    f"(similarity: {dedup_result.similarity:.2f}, "
                    f"duplicate of: {dedup_result.duplicate_of})"
                )
                
                # Optionally skip duplicates based on config
                if dedup_config.get('skip_duplicates', True):
                    continue
                
                # Add deduplication info to metadata
                doc.metadata['deduplication'] = {
                    'is_duplicate': True,
                    'duplicate_of': dedup_result.duplicate_of,
                    'duplicate_source': dedup_result.duplicate_source,
                    'similarity': dedup_result.similarity,
                    'match_type': dedup_result.match_type
                }
            else:
                # Register non-duplicate document
                self.deduplicator.register_document(doc)
            
            deduplicated_docs.append(doc)
        
        # Update result
        result.processed_documents = deduplicated_docs
        result.items_processed = len(deduplicated_docs)
        
        # Add deduplication stats to metadata
        if not hasattr(result, 'metadata'):
            result.metadata = {}
        
        result.metadata['deduplication'] = {
            'total_checked': len(result.processed_documents),
            'duplicates_found': duplicate_count,
            'documents_kept': len(deduplicated_docs),
            'threshold': threshold,
            'cross_source_check': cross_source
        }
        
        if duplicate_count > 0:
            logger.info(
                f"Deduplication complete for {source_type.value}: "
                f"{duplicate_count} duplicates found, "
                f"{len(deduplicated_docs)} documents kept"
            )
        
        return result
    
    def get_deduplication_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics.
        
        Returns:
            Deduplication statistics
        """
        return self.deduplicator.get_statistics()
    
    def cleanup_old_duplicates(self, days: int = 90) -> int:
        """Clean up old entries from deduplication cache.
        
        Args:
            days: Remove entries older than this many days
            
        Returns:
            Number of entries removed
        """
        return self.deduplicator.cleanup_old_entries(days)