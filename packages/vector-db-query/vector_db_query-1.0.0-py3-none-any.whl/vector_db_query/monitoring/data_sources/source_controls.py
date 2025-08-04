"""Control operations for data sources."""

from typing import Dict, Optional
import asyncio

from ...data_sources.models import SourceType, SyncState
from ...data_sources.orchestrator import DataSourceOrchestrator
from ...data_sources.base import SyncResult
from ...data_sources.database import get_db_manager
from ...utils.logger import get_logger

logger = get_logger(__name__)


class DataSourceControls:
    """Provides control operations for data sources."""
    
    def __init__(self, orchestrator: Optional[DataSourceOrchestrator] = None):
        """Initialize controls.
        
        Args:
            orchestrator: Data source orchestrator instance
        """
        self.orchestrator = orchestrator
        self.db_manager = get_db_manager()
        
        # Initialize orchestrator if not provided
        if not self.orchestrator:
            self.orchestrator = DataSourceOrchestrator()
            # Initialize sources asynchronously when first used
            self._initialized = False
        else:
            self._initialized = True
    
    async def _ensure_initialized(self):
        """Ensure orchestrator is initialized."""
        if not self._initialized:
            await self.orchestrator.initialize_sources()
            self._initialized = True
    
    async def sync_all(self) -> Dict[SourceType, SyncResult]:
        """Trigger sync for all active sources.
        
        Returns:
            Dict mapping source types to sync results
        """
        await self._ensure_initialized()
        
        logger.info("Starting sync for all sources")
        try:
            results = await self.orchestrator.sync_all()
            
            # Log summary
            total_processed = sum(r.items_processed for r in results.values())
            total_failed = sum(r.items_failed for r in results.values())
            logger.info(
                f"Sync all completed: {total_processed} processed, "
                f"{total_failed} failed across {len(results)} sources"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Sync all failed: {e}")
            raise
    
    async def sync_source(self, source_type: SourceType) -> SyncResult:
        """Trigger sync for a specific source.
        
        Args:
            source_type: Source to sync
            
        Returns:
            SyncResult from the operation
        """
        await self._ensure_initialized()
        
        logger.info(f"Starting sync for {source_type.value}")
        try:
            result = await self.orchestrator.sync_source(source_type)
            
            logger.info(
                f"Sync completed for {source_type.value}: "
                f"{result.items_processed} processed, {result.items_failed} failed"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Sync failed for {source_type.value}: {e}")
            raise
    
    async def pause_source(self, source_type: SourceType) -> bool:
        """Pause a data source.
        
        Args:
            source_type: Source to pause
            
        Returns:
            True if successful
        """
        logger.info(f"Pausing source: {source_type.value}")
        
        async with self.db_manager.get_async_session() as session:
            # Update sync state
            result = await session.execute(
                """
                UPDATE sync_state 
                SET is_active = false, updated_at = CURRENT_TIMESTAMP
                WHERE source_type = :source_type
                """,
                {"source_type": source_type.value}
            )
            
            if result.rowcount == 0:
                # Create sync state if doesn't exist
                await session.execute(
                    """
                    INSERT INTO sync_state (source_type, is_active)
                    VALUES (:source_type, false)
                    """,
                    {"source_type": source_type.value}
                )
            
            await session.commit()
            
        # Update orchestrator state
        if source_type in self.orchestrator.sync_states:
            self.orchestrator.sync_states[source_type].is_active = False
        
        logger.info(f"Source paused: {source_type.value}")
        return True
    
    async def resume_source(self, source_type: SourceType) -> bool:
        """Resume a paused data source.
        
        Args:
            source_type: Source to resume
            
        Returns:
            True if successful
        """
        logger.info(f"Resuming source: {source_type.value}")
        
        async with self.db_manager.get_async_session() as session:
            # Update sync state
            result = await session.execute(
                """
                UPDATE sync_state 
                SET is_active = true, updated_at = CURRENT_TIMESTAMP
                WHERE source_type = :source_type
                """,
                {"source_type": source_type.value}
            )
            
            if result.rowcount == 0:
                # Create sync state if doesn't exist
                await session.execute(
                    """
                    INSERT INTO sync_state (source_type, is_active)
                    VALUES (:source_type, true)
                    """,
                    {"source_type": source_type.value}
                )
            
            await session.commit()
            
        # Update orchestrator state
        if source_type in self.orchestrator.sync_states:
            self.orchestrator.sync_states[source_type].is_active = True
        
        logger.info(f"Source resumed: {source_type.value}")
        return True
    
    async def clear_errors(self, source_type: SourceType) -> bool:
        """Clear error state for a source.
        
        Args:
            source_type: Source to clear errors for
            
        Returns:
            True if successful
        """
        logger.info(f"Clearing errors for: {source_type.value}")
        
        async with self.db_manager.get_async_session() as session:
            # Clear error state
            await session.execute(
                """
                UPDATE sync_state 
                SET error_count = 0, 
                    last_error = NULL, 
                    last_error_timestamp = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE source_type = :source_type
                """,
                {"source_type": source_type.value}
            )
            
            await session.commit()
            
        # Update orchestrator state
        if source_type in self.orchestrator.sync_states:
            self.orchestrator.sync_states[source_type].clear_errors()
        
        logger.info(f"Errors cleared for: {source_type.value}")
        return True
    
    async def start_scheduled_sync(self):
        """Start scheduled sync for all sources."""
        await self._ensure_initialized()
        
        logger.info("Starting scheduled sync")
        await self.orchestrator.start_scheduled_sync()
    
    async def stop_scheduled_sync(self):
        """Stop scheduled sync for all sources."""
        logger.info("Stopping scheduled sync")
        await self.orchestrator.stop_scheduled_sync()
    
    async def get_source_config(self, source_type: SourceType) -> Optional[Dict]:
        """Get configuration for a source.
        
        Args:
            source_type: Source to get config for
            
        Returns:
            Configuration dict or None
        """
        async with self.db_manager.get_async_session() as session:
            result = await session.execute(
                """
                SELECT configuration
                FROM sync_state
                WHERE source_type = :source_type
                """,
                {"source_type": source_type.value}
            )
            
            row = result.first()
            return row.configuration if row else None
    
    async def update_source_config(self, source_type: SourceType, config: Dict) -> bool:
        """Update configuration for a source.
        
        Args:
            source_type: Source to update
            config: New configuration
            
        Returns:
            True if successful
        """
        logger.info(f"Updating config for: {source_type.value}")
        
        async with self.db_manager.get_async_session() as session:
            # Update configuration
            result = await session.execute(
                """
                UPDATE sync_state 
                SET configuration = :config,
                    updated_at = CURRENT_TIMESTAMP
                WHERE source_type = :source_type
                """,
                {"source_type": source_type.value, "config": config}
            )
            
            if result.rowcount == 0:
                # Create sync state if doesn't exist
                await session.execute(
                    """
                    INSERT INTO sync_state (source_type, configuration)
                    VALUES (:source_type, :config)
                    """,
                    {"source_type": source_type.value, "config": config}
                )
            
            await session.commit()
            
        # Update orchestrator state
        if source_type in self.orchestrator.sync_states:
            self.orchestrator.sync_states[source_type].configuration = config
        
        # Update source configuration if initialized
        if source_type in self.orchestrator.sources:
            source = self.orchestrator.sources[source_type]
            source.config.config = config
        
        logger.info(f"Config updated for: {source_type.value}")
        return True
    
    async def test_source_connection(self, source_type: SourceType) -> bool:
        """Test connection to a data source.
        
        Args:
            source_type: Source to test
            
        Returns:
            True if connection successful
        """
        await self._ensure_initialized()
        
        if source_type not in self.orchestrator.sources:
            logger.warning(f"Source not registered: {source_type.value}")
            return False
        
        source = self.orchestrator.sources[source_type]
        
        try:
            # Test authentication
            if not source.is_authenticated:
                authenticated = await source.authenticate()
                if not authenticated:
                    return False
            
            # Test connection
            return await source.test_connection()
            
        except Exception as e:
            logger.error(f"Connection test failed for {source_type.value}: {e}")
            return False