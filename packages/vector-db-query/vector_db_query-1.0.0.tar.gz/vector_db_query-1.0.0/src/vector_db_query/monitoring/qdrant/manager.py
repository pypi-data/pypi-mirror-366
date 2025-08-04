"""
Qdrant management service for collection and point operations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance as QdrantDistance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest as QdrantSearchRequest,
    UpdateStatus,
    CollectionStatus as QdrantCollectionStatus,
    OptimizersConfigDiff,
    HnswConfigDiff
)
import numpy as np

from .models import (
    CollectionConfig, CollectionInfo, CollectionStatus,
    PointData, SearchRequest, SearchResult,
    BatchOperation, OptimizationTask, OptimizationStatus,
    QdrantMetrics, Distance, IndexType
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class QdrantManager:
    """
    Manages Qdrant vector database operations including collections,
    points, search, and optimization.
    """
    
    def __init__(self, host: str = "localhost", port: int = 6333, 
                 api_key: Optional[str] = None, https: bool = False):
        """
        Initialize Qdrant manager.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            api_key: Optional API key for authentication
            https: Use HTTPS connection
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.https = https
        
        # Initialize client
        self.client = QdrantClient(
            host=host,
            port=port,
            api_key=api_key,
            https=https
        )
        
        self.change_tracker = get_change_tracker()
        
        # Cache for collection info
        self._collection_cache: Dict[str, CollectionInfo] = {}
        self._cache_ttl = timedelta(minutes=5)
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Active operations
        self._active_operations: Dict[str, BatchOperation] = {}
        self._optimization_tasks: Dict[str, OptimizationTask] = {}
        
        logger.info(f"QdrantManager initialized for {host}:{port}")
    
    async def create_collection(self, config: CollectionConfig) -> CollectionInfo:
        """
        Create a new collection.
        
        Args:
            config: Collection configuration
            
        Returns:
            CollectionInfo object
        """
        try:
            # Convert distance metric
            distance_map = {
                Distance.COSINE: QdrantDistance.COSINE,
                Distance.EUCLID: QdrantDistance.EUCLID,
                Distance.DOT: QdrantDistance.DOT
            }
            
            # Create collection
            self.client.create_collection(
                collection_name=config.name,
                vectors_config=VectorParams(
                    size=config.vector_size,
                    distance=distance_map[config.distance]
                ),
                hnsw_config=config.hnsw_config,
                wal_config=config.wal_config,
                optimizers_config=config.optimizers_config,
                replication_factor=config.replication_factor,
                write_consistency_factor=config.write_consistency_factor
            )
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.DATABASE,
                change_type=ChangeType.CREATE,
                description=f"Created Qdrant collection: {config.name}",
                details=config.to_dict()
            )
            
            # Get collection info
            info = await self.get_collection_info(config.name)
            
            logger.info(f"Created collection: {config.name}")
            return info
            
        except Exception as e:
            logger.error(f"Error creating collection {config.name}: {e}")
            raise
    
    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of collection to delete
            
        Returns:
            Success status
        """
        try:
            # Get info before deletion for tracking
            info = await self.get_collection_info(collection_name)
            
            # Delete collection
            self.client.delete_collection(collection_name)
            
            # Clear cache
            self._collection_cache.pop(collection_name, None)
            self._cache_timestamps.pop(collection_name, None)
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.DATABASE,
                change_type=ChangeType.DELETE,
                description=f"Deleted Qdrant collection: {collection_name}",
                details={
                    'vectors_count': info.vectors_count,
                    'size_bytes': info.size_bytes
                }
            )
            
            logger.info(f"Deleted collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False
    
    async def get_collection_info(self, collection_name: str, 
                                 use_cache: bool = True) -> CollectionInfo:
        """
        Get detailed information about a collection.
        
        Args:
            collection_name: Name of collection
            use_cache: Whether to use cached info
            
        Returns:
            CollectionInfo object
        """
        # Check cache
        if use_cache and collection_name in self._collection_cache:
            cache_time = self._cache_timestamps.get(collection_name)
            if cache_time and datetime.now() - cache_time < self._cache_ttl:
                return self._collection_cache[collection_name]
        
        try:
            # Get collection info from Qdrant
            collection = self.client.get_collection(collection_name)
            
            # Get collection statistics
            stats = self.client.collection_info(collection_name)
            
            # Map status
            status_map = {
                QdrantCollectionStatus.GREEN: CollectionStatus.GREEN,
                QdrantCollectionStatus.YELLOW: CollectionStatus.YELLOW,
                QdrantCollectionStatus.RED: CollectionStatus.RED
            }
            
            # Create config object
            config = CollectionConfig(
                name=collection_name,
                vector_size=collection.config.params.vectors.size,
                distance=Distance.COSINE  # Default, would need mapping
            )
            
            # Create info object
            info = CollectionInfo(
                name=collection_name,
                status=status_map.get(collection.status, CollectionStatus.GREEN),
                vectors_count=stats.vectors_count or 0,
                points_count=stats.points_count or 0,
                segments_count=stats.segments_count or 0,
                config=config,
                indexed_vectors_count=stats.indexed_vectors_count or 0
            )
            
            # Cache the info
            self._collection_cache[collection_name] = info
            self._cache_timestamps[collection_name] = datetime.now()
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting collection info for {collection_name}: {e}")
            raise
    
    async def list_collections(self) -> List[CollectionInfo]:
        """
        List all collections.
        
        Returns:
            List of CollectionInfo objects
        """
        try:
            collections = self.client.get_collections()
            
            infos = []
            for collection in collections.collections:
                try:
                    info = await self.get_collection_info(collection.name)
                    infos.append(info)
                except Exception as e:
                    logger.error(f"Error getting info for collection {collection.name}: {e}")
            
            return infos
            
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    async def insert_points(self, collection_name: str, 
                          points: List[PointData],
                          batch_size: int = 100) -> BatchOperation:
        """
        Insert points into a collection.
        
        Args:
            collection_name: Target collection
            points: Points to insert
            batch_size: Batch size for insertion
            
        Returns:
            BatchOperation tracking the insertion
        """
        operation = BatchOperation(
            operation_type="insert",
            collection_name=collection_name,
            points=points,
            started_at=datetime.now()
        )
        
        self._active_operations[operation.operation_id] = operation
        
        try:
            # Process in batches
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                
                # Convert to Qdrant points
                qdrant_points = [
                    PointStruct(
                        id=point.id,
                        vector=point.vector,
                        payload=point.payload
                    )
                    for point in batch
                ]
                
                # Insert batch
                self.client.upsert(
                    collection_name=collection_name,
                    points=qdrant_points
                )
                
                operation.processed_count += len(batch)
                logger.debug(f"Inserted batch {i//batch_size + 1}, total: {operation.processed_count}")
            
            operation.status = "completed"
            operation.completed_at = datetime.now()
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.DATABASE,
                change_type=ChangeType.CREATE,
                description=f"Inserted {len(points)} points into {collection_name}",
                details={
                    'operation_id': operation.operation_id,
                    'points_count': len(points),
                    'duration_ms': operation.duration_ms()
                }
            )
            
            # Clear cache for this collection
            self._collection_cache.pop(collection_name, None)
            
            logger.info(f"Completed insertion of {len(points)} points into {collection_name}")
            
        except Exception as e:
            operation.status = "failed"
            operation.error_count = len(points) - operation.processed_count
            operation.errors.append(str(e))
            operation.completed_at = datetime.now()
            logger.error(f"Error inserting points: {e}")
        
        return operation
    
    async def search(self, request: SearchRequest) -> List[SearchResult]:
        """
        Search for similar vectors.
        
        Args:
            request: Search request configuration
            
        Returns:
            List of search results
        """
        try:
            # Build search parameters
            search_params = {
                "limit": request.limit,
                "offset": request.offset,
                "with_payload": request.with_payload,
                "with_vectors": request.with_vector
            }
            
            if request.score_threshold:
                search_params["score_threshold"] = request.score_threshold
            
            if request.params:
                search_params["search_params"] = request.params
            
            # Perform search
            results = self.client.search(
                collection_name=request.collection_name,
                query_vector=request.vector,
                query_filter=request.filter,
                **search_params
            )
            
            # Convert to SearchResult objects
            search_results = [
                SearchResult(
                    id=result.id,
                    score=result.score,
                    payload=result.payload if request.with_payload else None,
                    vector=result.vector if request.with_vector else None
                )
                for result in results
            ]
            
            logger.debug(f"Search in {request.collection_name} returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching in {request.collection_name}: {e}")
            raise
    
    async def delete_points(self, collection_name: str,
                          point_ids: Optional[List[Union[str, int]]] = None,
                          filter: Optional[Dict[str, Any]] = None) -> BatchOperation:
        """
        Delete points from a collection.
        
        Args:
            collection_name: Target collection
            point_ids: IDs of points to delete
            filter: Filter for points to delete
            
        Returns:
            BatchOperation tracking the deletion
        """
        operation = BatchOperation(
            operation_type="delete",
            collection_name=collection_name,
            point_ids=point_ids or [],
            filter=filter,
            started_at=datetime.now()
        )
        
        self._active_operations[operation.operation_id] = operation
        
        try:
            if point_ids:
                # Delete by IDs
                self.client.delete(
                    collection_name=collection_name,
                    points_selector=point_ids
                )
                operation.processed_count = len(point_ids)
            elif filter:
                # Delete by filter
                result = self.client.delete(
                    collection_name=collection_name,
                    points_selector=filter
                )
                operation.processed_count = result.status
            
            operation.status = "completed"
            operation.completed_at = datetime.now()
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.DATABASE,
                change_type=ChangeType.DELETE,
                description=f"Deleted points from {collection_name}",
                details={
                    'operation_id': operation.operation_id,
                    'method': 'ids' if point_ids else 'filter',
                    'count': operation.processed_count
                }
            )
            
            # Clear cache
            self._collection_cache.pop(collection_name, None)
            
            logger.info(f"Deleted {operation.processed_count} points from {collection_name}")
            
        except Exception as e:
            operation.status = "failed"
            operation.errors.append(str(e))
            operation.completed_at = datetime.now()
            logger.error(f"Error deleting points: {e}")
        
        return operation
    
    async def optimize_collection(self, collection_name: str,
                                wait: bool = False) -> OptimizationTask:
        """
        Optimize a collection.
        
        Args:
            collection_name: Collection to optimize
            wait: Whether to wait for completion
            
        Returns:
            OptimizationTask tracking the optimization
        """
        task = OptimizationTask(
            collection_name=collection_name,
            optimization_type="indexing",
            status=OptimizationStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        self._optimization_tasks[task.task_id] = task
        
        try:
            # Get initial state
            info_before = await self.get_collection_info(collection_name, use_cache=False)
            task.segments_before = info_before.segments_count
            task.size_before_bytes = info_before.size_bytes
            
            # Trigger optimization
            update_result = self.client.update_collection(
                collection_name=collection_name,
                optimizer_config=OptimizersConfigDiff(
                    indexing_threshold=1  # Force immediate indexing
                )
            )
            
            if wait:
                # Wait for optimization to complete
                await self._wait_for_optimization(collection_name, task)
            else:
                # Schedule background check
                asyncio.create_task(self._wait_for_optimization(collection_name, task))
            
            return task
            
        except Exception as e:
            task.status = OptimizationStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            logger.error(f"Error optimizing collection {collection_name}: {e}")
            return task
    
    async def _wait_for_optimization(self, collection_name: str, 
                                   task: OptimizationTask):
        """Wait for optimization to complete."""
        try:
            max_wait = 300  # 5 minutes
            start_time = datetime.now()
            
            while (datetime.now() - start_time).total_seconds() < max_wait:
                # Check collection status
                info = await self.get_collection_info(collection_name, use_cache=False)
                
                if info.is_optimized:
                    task.status = OptimizationStatus.COMPLETED
                    task.segments_after = info.segments_count
                    task.size_after_bytes = info.size_bytes
                    task.progress = 100.0
                    task.completed_at = datetime.now()
                    
                    # Track change
                    self.change_tracker.track_change(
                        category=ChangeCategory.SYSTEM,
                        change_type=ChangeType.UPDATE,
                        description=f"Optimized collection {collection_name}",
                        details={
                            'task_id': task.task_id,
                            'segments_reduced': task.segments_before - task.segments_after,
                            'space_saved_bytes': task.space_saved_bytes(),
                            'duration_seconds': task.duration_seconds()
                        }
                    )
                    
                    logger.info(f"Optimization completed for {collection_name}")
                    break
                
                # Update progress estimate
                elapsed = (datetime.now() - start_time).total_seconds()
                task.progress = min(95, (elapsed / 60) * 20)  # Rough estimate
                
                await asyncio.sleep(5)
            
            else:
                # Timeout
                task.status = OptimizationStatus.FAILED
                task.error_message = "Optimization timeout"
                task.completed_at = datetime.now()
                
        except Exception as e:
            task.status = OptimizationStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            logger.error(f"Error waiting for optimization: {e}")
    
    async def get_metrics(self) -> QdrantMetrics:
        """
        Get overall Qdrant metrics.
        
        Returns:
            QdrantMetrics object
        """
        metrics = QdrantMetrics()
        
        try:
            # Get all collections
            collections = await self.list_collections()
            
            metrics.total_collections = len(collections)
            
            # Aggregate metrics
            for collection in collections:
                metrics.total_vectors += collection.vectors_count
                metrics.total_points += collection.points_count
                metrics.total_size_bytes += collection.size_bytes
            
            # Get telemetry if available
            try:
                telemetry = self.client.openapi_client.service_api.metrics()
                if telemetry:
                    # Parse telemetry data
                    # This would depend on actual Qdrant telemetry format
                    pass
            except:
                pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting Qdrant metrics: {e}")
            return metrics
    
    def get_active_operations(self) -> List[BatchOperation]:
        """Get list of active operations."""
        return list(self._active_operations.values())
    
    def get_optimization_tasks(self) -> List[OptimizationTask]:
        """Get list of optimization tasks."""
        return list(self._optimization_tasks.values())
    
    async def create_snapshot(self, collection_name: str) -> str:
        """
        Create a snapshot of a collection.
        
        Args:
            collection_name: Collection to snapshot
            
        Returns:
            Snapshot name
        """
        try:
            result = self.client.create_snapshot(collection_name)
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.SYSTEM,
                change_type=ChangeType.CREATE,
                description=f"Created snapshot for collection {collection_name}",
                details={'snapshot_name': result.name}
            )
            
            logger.info(f"Created snapshot for {collection_name}: {result.name}")
            return result.name
            
        except Exception as e:
            logger.error(f"Error creating snapshot for {collection_name}: {e}")
            raise
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check Qdrant server health.
        
        Returns:
            Health status dictionary
        """
        try:
            # Try to get collections as health check
            collections = self.client.get_collections()
            
            return {
                'status': 'healthy',
                'collections_count': len(collections.collections),
                'version': getattr(self.client, 'version', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Singleton instance
_qdrant_manager: Optional[QdrantManager] = None


def get_qdrant_manager(host: str = "localhost", port: int = 6333,
                      api_key: Optional[str] = None, 
                      https: bool = False) -> QdrantManager:
    """Get singleton Qdrant manager instance."""
    global _qdrant_manager
    
    if _qdrant_manager is None:
        _qdrant_manager = QdrantManager(host, port, api_key, https)
    
    return _qdrant_manager


def reset_qdrant_manager():
    """Reset the singleton Qdrant manager."""
    global _qdrant_manager
    _qdrant_manager = None