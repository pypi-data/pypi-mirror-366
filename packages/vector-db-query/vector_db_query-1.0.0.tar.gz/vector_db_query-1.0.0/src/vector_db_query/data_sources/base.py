"""Base classes for data source integrations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional, AsyncIterator
from pathlib import Path
import asyncio
from enum import Enum

from ..utils.logger import get_logger

logger = get_logger(__name__)


class AuthMethod(Enum):
    """Authentication methods supported by data sources."""
    OAUTH2 = "oauth2"
    OAUTH2_USER = "oauth2_user"
    API_KEY = "api_key"
    WEBHOOK = "webhook"
    IMAP = "imap"


@dataclass
class DataSourceConfig:
    """Configuration for a data source."""
    source_type: str
    enabled: bool = True
    auth_method: AuthMethod = AuthMethod.OAUTH2
    sync_interval: int = 300  # seconds
    max_concurrent_items: int = 10
    retry_attempts: int = 3
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class SyncResult:
    """Result of a sync operation."""
    source_type: str
    started_at: datetime
    completed_at: datetime
    success: bool
    items_fetched: int
    items_processed: int
    errors: List[str] = None
    processed_documents: List[Any] = None  # Will be List[ProcessedDocument]
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.processed_documents is None:
            self.processed_documents = []
    
    @property
    def duration(self) -> float:
        """Get sync duration in seconds."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.items_fetched == 0:
            return 100.0
        return (self.items_processed / self.items_fetched) * 100


class AbstractDataSource(ABC):
    """Abstract base class for all data sources."""
    
    def __init__(self, config: DataSourceConfig):
        """Initialize data source with configuration."""
        self.config = config
        self.is_authenticated = False
        self._sync_lock = asyncio.Lock()
        
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the data source.
        
        Returns:
            bool: True if authentication successful
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test the connection to the data source.
        
        Returns:
            bool: True if connection successful
        """
        pass
    
    @abstractmethod
    async def fetch_items(self, 
                         since: Optional[datetime] = None,
                         limit: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]:
        """Fetch items from the data source.
        
        Args:
            since: Fetch items created/modified after this time
            limit: Maximum number of items to fetch
            
        Yields:
            Dict containing item data
        """
        pass
    
    @abstractmethod
    async def process_item(self, item: Dict[str, Any]) -> Optional[Path]:
        """Process a single item from the data source.
        
        Args:
            item: Item data from fetch_items
            
        Returns:
            Path to processed file, or None if skipped
        """
        pass
    
    async def sync(self, 
                   since: Optional[datetime] = None,
                   limit: Optional[int] = None) -> SyncResult:
        """Perform a full sync operation.
        
        Args:
            since: Sync items after this time
            limit: Maximum items to sync
            
        Returns:
            SyncResult with operation details
        """
        async with self._sync_lock:
            result = SyncResult(source_type=self.config.source_type)
            
            try:
                # Ensure authenticated
                if not self.is_authenticated:
                    if not await self.authenticate():
                        result.errors.append("Authentication failed")
                        return result
                
                # Test connection
                if not await self.test_connection():
                    result.errors.append("Connection test failed")
                    return result
                
                # Fetch and process items
                processed_count = 0
                async for item in self.fetch_items(since=since, limit=limit):
                    try:
                        file_path = await self.process_item(item)
                        if file_path:
                            result.items_processed += 1
                            processed_count += 1
                            
                            # Log progress every 10 items
                            if processed_count % 10 == 0:
                                logger.info(f"{self.config.source_type}: Processed {processed_count} items")
                                
                    except Exception as e:
                        result.items_failed += 1
                        result.errors.append(f"Failed to process item: {str(e)}")
                        logger.error(f"Error processing item: {e}", exc_info=True)
                        
                        # Continue processing other items
                        continue
                
            except Exception as e:
                result.errors.append(f"Sync failed: {str(e)}")
                logger.error(f"Sync failed for {self.config.source_type}: {e}", exc_info=True)
            
            finally:
                result.completed_at = datetime.utcnow()
                
            return result
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for the data source.
        
        Returns:
            Dict containing metrics like last_sync, items_total, etc.
        """
        pass
    
    async def cleanup(self):
        """Cleanup resources used by the data source."""
        pass