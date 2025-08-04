"""Collection management for Qdrant vector database."""

from typing import Dict, List, Optional

from qdrant_client.models import (
    VectorParams,
    CollectionStatus,
    CreateCollection,
    UpdateCollection,
    HnswConfigDiff,
    OptimizersConfigDiff
)

from vector_db_query.vector_db.client import QdrantClient
from vector_db_query.vector_db.models import CollectionInfo, CollectionConfig
from vector_db_query.vector_db.exceptions import (
    CollectionError,
    CollectionNotFoundError,
    CollectionExistsError
)
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class CollectionManager:
    """Manages collections in Qdrant vector database."""
    
    def __init__(self, client: QdrantClient):
        """Initialize collection manager.
        
        Args:
            client: Qdrant client instance
        """
        self.client = client
        
    def create_collection(
        self,
        name: str,
        vector_size: int,
        distance: str = "Cosine",
        on_disk_payload: bool = True,
        hnsw_config: Optional[Dict] = None
    ) -> bool:
        """Create a new collection.
        
        Args:
            name: Collection name
            vector_size: Size of vectors to store
            distance: Distance metric (Cosine, Euclidean, Dot)
            on_disk_payload: Whether to store payload on disk
            hnsw_config: HNSW index configuration
            
        Returns:
            True if collection created successfully
            
        Raises:
            CollectionExistsError: If collection already exists
            CollectionError: If creation fails
        """
        try:
            # Check if collection exists
            if self.collection_exists(name):
                raise CollectionExistsError(name)
                
            logger.info(
                f"Creating collection '{name}' with vector_size={vector_size}, "
                f"distance={distance}"
            )
            
            # Set default HNSW config if not provided
            if hnsw_config is None:
                hnsw_config = {
                    "m": 16,
                    "ef_construct": 128,
                    "full_scan_threshold": 10000
                }
                
            # Create collection
            self.client.native_client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=QdrantClient.distance_from_string(distance)
                ),
                on_disk_payload=on_disk_payload,
                hnsw_config=hnsw_config
            )
            
            logger.info(f"Collection '{name}' created successfully")
            return True
            
        except CollectionExistsError:
            raise
        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e}")
            raise CollectionError(f"Failed to create collection: {e}")
            
    def create_from_config(self, config: CollectionConfig) -> bool:
        """Create collection from configuration object.
        
        Args:
            config: Collection configuration
            
        Returns:
            True if collection created successfully
        """
        return self.create_collection(
            name=config.name,
            vector_size=config.vector_size,
            distance=config.distance,
            on_disk_payload=config.on_disk_payload,
            hnsw_config=config.hnsw_config
        )
        
    def delete_collection(self, name: str) -> bool:
        """Delete a collection.
        
        Args:
            name: Collection name
            
        Returns:
            True if collection deleted successfully
            
        Raises:
            CollectionNotFoundError: If collection doesn't exist
            CollectionError: If deletion fails
        """
        try:
            if not self.collection_exists(name):
                raise CollectionNotFoundError(name)
                
            logger.info(f"Deleting collection '{name}'")
            self.client.native_client.delete_collection(collection_name=name)
            logger.info(f"Collection '{name}' deleted successfully")
            return True
            
        except CollectionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete collection '{name}': {e}")
            raise CollectionError(f"Failed to delete collection: {e}")
            
    def collection_exists(self, name: str) -> bool:
        """Check if a collection exists.
        
        Args:
            name: Collection name
            
        Returns:
            True if collection exists
        """
        try:
            collections = self.client.get_collections()
            return name in collections
        except Exception as e:
            logger.error(f"Failed to check collection existence: {e}")
            return False
            
    def get_collection_info(self, name: str) -> CollectionInfo:
        """Get information about a collection.
        
        Args:
            name: Collection name
            
        Returns:
            CollectionInfo object
            
        Raises:
            CollectionNotFoundError: If collection doesn't exist
            CollectionError: If retrieval fails
        """
        try:
            if not self.collection_exists(name):
                raise CollectionNotFoundError(name)
                
            # Get collection details
            collection = self.client.native_client.get_collection(collection_name=name)
            
            # Extract configuration
            config = {}
            if hasattr(collection.config, 'params'):
                config = collection.config.params.dict() if hasattr(collection.config.params, 'dict') else {}
                
            # Get status
            status = "unknown"
            if hasattr(collection, 'status'):
                status = collection.status.value if hasattr(collection.status, 'value') else str(collection.status)
                
            # Create CollectionInfo
            return CollectionInfo(
                name=name,
                vector_size=collection.config.params.vectors.size,
                vectors_count=collection.points_count,
                distance_metric=str(collection.config.params.vectors.distance),
                status=status,
                config=config
            )
            
        except CollectionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get collection info for '{name}': {e}")
            raise CollectionError(f"Failed to get collection info: {e}")
            
    def recreate_collection(
        self,
        name: str,
        config: Optional[CollectionConfig] = None,
        preserve_data: bool = False
    ) -> bool:
        """Recreate a collection, optionally preserving data.
        
        Args:
            name: Collection name
            config: New configuration (uses existing if not provided)
            preserve_data: Whether to preserve existing data
            
        Returns:
            True if collection recreated successfully
        """
        try:
            # Get existing info if preserving data or config not provided
            existing_info = None
            if preserve_data or config is None:
                try:
                    existing_info = self.get_collection_info(name)
                except CollectionNotFoundError:
                    pass
                    
            # Use existing config if not provided
            if config is None and existing_info:
                config = CollectionConfig(
                    name=name,
                    vector_size=existing_info.vector_size,
                    distance=existing_info.distance_metric
                )
            elif config is None:
                raise CollectionError("No configuration provided and collection doesn't exist")
                
            # TODO: Implement data preservation if needed
            if preserve_data and existing_info and existing_info.vectors_count > 0:
                logger.warning(
                    f"Data preservation not yet implemented. "
                    f"Collection '{name}' has {existing_info.vectors_count} vectors that will be lost."
                )
                
            # Delete if exists
            if self.collection_exists(name):
                self.delete_collection(name)
                
            # Create with new config
            return self.create_from_config(config)
            
        except Exception as e:
            logger.error(f"Failed to recreate collection '{name}': {e}")
            raise CollectionError(f"Failed to recreate collection: {e}")
            
    def list_collections(self) -> List[CollectionInfo]:
        """List all collections with their info.
        
        Returns:
            List of CollectionInfo objects
        """
        collections = []
        
        try:
            collection_names = self.client.get_collections()
            
            for name in collection_names:
                try:
                    info = self.get_collection_info(name)
                    collections.append(info)
                except Exception as e:
                    logger.warning(f"Failed to get info for collection '{name}': {e}")
                    
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            
        return collections
        
    def optimize_collection(self, name: str, wait: bool = True) -> bool:
        """Optimize collection for better performance.
        
        Args:
            name: Collection name
            wait: Whether to wait for optimization to complete
            
        Returns:
            True if optimization started successfully
        """
        try:
            if not self.collection_exists(name):
                raise CollectionNotFoundError(name)
                
            logger.info(f"Optimizing collection '{name}'")
            
            # Update collection with optimized settings
            self.client.native_client.update_collection(
                collection_name=name,
                optimizer_config=OptimizersConfigDiff(
                    indexing_threshold=20000,
                    flush_interval_sec=5,
                    max_optimization_threads=0  # Use all available
                )
            )
            
            # Trigger optimization
            # Note: Qdrant optimizes automatically, but we can force it
            # by updating HNSW settings
            
            logger.info(f"Collection '{name}' optimization initiated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to optimize collection '{name}': {e}")
            raise CollectionError(f"Failed to optimize collection: {e}")