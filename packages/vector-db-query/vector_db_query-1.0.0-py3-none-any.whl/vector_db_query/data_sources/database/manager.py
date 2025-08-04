"""Database manager for data sources."""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
from pathlib import Path

from ..models import SourceType, SyncStatus, SyncResult, SyncState

# Try to import asyncpg, but make it optional
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

# Try to import SQLAlchemy, but make it optional
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

from ...utils.logger import get_logger

logger = get_logger(__name__)


class DataSourceDatabaseManager:
    """Manager for data source database operations."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """Initialize database manager.
        
        Args:
            connection_string: Database connection string
        """
        self.connection_string = connection_string
        self._pool = None
        self._engine = None
        
        # Use file-based storage as fallback
        self.use_file_storage = not (ASYNCPG_AVAILABLE or SQLALCHEMY_AVAILABLE)
        if self.use_file_storage:
            logger.warning("Database libraries not available. Using file-based storage.")
            self.storage_path = Path(".vector-db-query/data_sources/db")
            self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def get_sync_state(self, source_type: SourceType) -> Optional[SyncState]:
        """Get sync state for a source.
        
        Args:
            source_type: Type of data source
            
        Returns:
            Sync state or None
        """
        if self.use_file_storage:
            return self._get_sync_state_file(source_type)
        
        # TODO: Implement database query
        logger.warning("Database sync state not implemented")
        return None
    
    async def save_sync_state(self, sync_state: SyncState):
        """Save sync state.
        
        Args:
            sync_state: Sync state to save
        """
        if self.use_file_storage:
            self._save_sync_state_file(sync_state)
            return
        
        # TODO: Implement database save
        logger.warning("Database sync state save not implemented")
    
    async def get_sync_history(self, 
                              source_type: SourceType,
                              limit: int = 10) -> List[SyncResult]:
        """Get sync history for a source.
        
        Args:
            source_type: Type of data source
            limit: Maximum results to return
            
        Returns:
            List of sync results
        """
        if self.use_file_storage:
            return self._get_sync_history_file(source_type, limit)
        
        # TODO: Implement database query
        logger.warning("Database sync history not implemented")
        return []
    
    async def save_sync_result(self, result: SyncResult):
        """Save sync result.
        
        Args:
            result: Sync result to save
        """
        if self.use_file_storage:
            self._save_sync_result_file(result)
            return
        
        # TODO: Implement database save
        logger.warning("Database sync result save not implemented")
    
    # File-based storage methods
    
    def _get_sync_state_file(self, source_type: SourceType) -> Optional[SyncState]:
        """Get sync state from file."""
        file_path = self.storage_path / f"{source_type.value}_state.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return SyncState(
                source_type=SourceType(data['source_type']),
                last_sync_timestamp=datetime.fromisoformat(data['last_sync_timestamp']) if data.get('last_sync_timestamp') else None,
                configuration=data.get('configuration', {}),
                is_active=data.get('is_active', True),
                error_count=data.get('error_count', 0),
                last_error=data.get('last_error')
            )
        except Exception as e:
            logger.error(f"Failed to load sync state: {e}")
            return None
    
    def _save_sync_state_file(self, sync_state: SyncState):
        """Save sync state to file."""
        file_path = self.storage_path / f"{sync_state.source_type.value}_state.json"
        
        data = {
            'source_type': sync_state.source_type.value,
            'last_sync_timestamp': sync_state.last_sync_timestamp.isoformat() if sync_state.last_sync_timestamp else None,
            'configuration': sync_state.configuration,
            'is_active': sync_state.is_active,
            'error_count': sync_state.error_count,
            'last_error': sync_state.last_error
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sync state: {e}")
    
    def _get_sync_history_file(self, source_type: SourceType, limit: int) -> List[SyncResult]:
        """Get sync history from file."""
        file_path = self.storage_path / f"{source_type.value}_history.json"
        
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r') as f:
                history = json.load(f)
            
            # Convert to SyncResult objects
            results = []
            for item in history[-limit:]:  # Get last N items
                result = SyncResult(
                    source_type=SourceType(item['source_type']),
                    started_at=datetime.fromisoformat(item['started_at']),
                    completed_at=datetime.fromisoformat(item['completed_at']) if item.get('completed_at') else None,
                    status=SyncStatus(item['status']),
                    items_processed=item.get('items_processed', 0),
                    items_failed=item.get('items_failed', 0),
                    errors=item.get('errors', [])
                )
                results.append(result)
            
            return list(reversed(results))  # Most recent first
            
        except Exception as e:
            logger.error(f"Failed to load sync history: {e}")
            return []
    
    def _save_sync_result_file(self, result: SyncResult):
        """Save sync result to file."""
        file_path = self.storage_path / f"{result.source_type.value}_history.json"
        
        # Load existing history
        history = []
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    history = json.load(f)
            except Exception:
                pass
        
        # Add new result
        history.append({
            'source_type': result.source_type.value,
            'started_at': result.started_at.isoformat(),
            'completed_at': result.completed_at.isoformat() if result.completed_at else None,
            'status': result.status.value,
            'items_processed': result.items_processed,
            'items_failed': result.items_failed,
            'errors': result.errors
        })
        
        # Keep only last 100 entries
        history = history[-100:]
        
        try:
            with open(file_path, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sync result: {e}")