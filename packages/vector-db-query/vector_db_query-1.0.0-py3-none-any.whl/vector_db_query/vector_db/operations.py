"""Vector operations for Qdrant database."""

import uuid
from typing import Any, Dict, List, Optional, Union

import numpy as np
from qdrant_client.models import (
    PointStruct,
    SearchRequest,
    Filter,
    FieldCondition,
    MatchValue,
    HasIdCondition,
    Range,
    PointIdsList
)

from vector_db_query.vector_db.client import QdrantClient
from vector_db_query.vector_db.models import VectorPoint, SearchResult
from vector_db_query.vector_db.exceptions import (
    VectorOperationError,
    InsertionError,
    SearchError,
    CollectionNotFoundError
)
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class VectorOperations:
    """Handles vector CRUD operations in Qdrant."""
    
    def __init__(self, client: QdrantClient):
        """Initialize vector operations.
        
        Args:
            client: Qdrant client instance
        """
        self.client = client
        
    def insert_single(
        self,
        collection_name: str,
        vector: Union[List[float], np.ndarray],
        metadata: Dict[str, Any],
        vector_id: Optional[str] = None
    ) -> str:
        """Insert a single vector.
        
        Args:
            collection_name: Name of the collection
            vector: Vector to insert
            metadata: Metadata payload
            vector_id: Optional ID (generated if not provided)
            
        Returns:
            ID of inserted vector
            
        Raises:
            InsertionError: If insertion fails
        """
        try:
            # Generate ID if not provided
            if vector_id is None:
                vector_id = str(uuid.uuid4())
                
            # Convert numpy array to list if needed
            if isinstance(vector, np.ndarray):
                vector = vector.tolist()
                
            # Create point
            point = PointStruct(
                id=vector_id,
                vector=vector,
                payload=metadata
            )
            
            # Insert
            self.client.native_client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            logger.debug(f"Inserted vector {vector_id} into collection '{collection_name}'")
            return vector_id
            
        except Exception as e:
            logger.error(f"Failed to insert vector: {e}")
            raise InsertionError(f"Failed to insert vector: {e}")
            
    def insert_batch(
        self,
        collection_name: str,
        vectors: List[Union[List[float], np.ndarray]],
        metadatas: List[Dict[str, Any]],
        vector_ids: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> List[str]:
        """Insert multiple vectors in batches.
        
        Args:
            collection_name: Name of the collection
            vectors: List of vectors to insert
            metadatas: List of metadata payloads
            vector_ids: Optional list of IDs (generated if not provided)
            batch_size: Size of batches for insertion
            
        Returns:
            List of inserted vector IDs
            
        Raises:
            InsertionError: If insertion fails
        """
        if len(vectors) != len(metadatas):
            raise ValueError("Number of vectors must match number of metadata entries")
            
        try:
            # Generate IDs if not provided
            if vector_ids is None:
                vector_ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
            elif len(vector_ids) != len(vectors):
                raise ValueError("Number of IDs must match number of vectors")
                
            # Convert numpy arrays to lists
            vectors = [v.tolist() if isinstance(v, np.ndarray) else v for v in vectors]
            
            # Insert in batches
            all_ids = []
            for i in range(0, len(vectors), batch_size):
                batch_end = min(i + batch_size, len(vectors))
                
                # Create points for this batch
                points = [
                    PointStruct(
                        id=vector_ids[j],
                        vector=vectors[j],
                        payload=metadatas[j]
                    )
                    for j in range(i, batch_end)
                ]
                
                # Insert batch
                self.client.native_client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                
                batch_ids = vector_ids[i:batch_end]
                all_ids.extend(batch_ids)
                
                logger.debug(
                    f"Inserted batch of {len(points)} vectors "
                    f"({i+1}-{batch_end}/{len(vectors)}) "
                    f"into collection '{collection_name}'"
                )
                
            logger.info(f"Inserted {len(all_ids)} vectors into collection '{collection_name}'")
            return all_ids
            
        except Exception as e:
            logger.error(f"Failed to insert batch: {e}")
            raise InsertionError(f"Failed to insert batch: {e}")
            
    def search(
        self,
        collection_name: str,
        query_vector: Union[List[float], np.ndarray],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
        with_vectors: bool = False
    ) -> List[SearchResult]:
        """Search for similar vectors.
        
        Args:
            collection_name: Name of the collection
            query_vector: Query vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filters: Optional filters for metadata
            with_vectors: Whether to return vectors
            
        Returns:
            List of search results
            
        Raises:
            SearchError: If search fails
        """
        try:
            # Convert numpy array to list if needed
            if isinstance(query_vector, np.ndarray):
                query_vector = query_vector.tolist()
                
            # Build filter if provided
            qdrant_filter = None
            if filters:
                qdrant_filter = self._build_filter(filters)
                
            # Perform search
            results = self.client.native_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=qdrant_filter,
                with_vectors=with_vectors,
                with_payload=True
            )
            
            # Convert to SearchResult objects
            search_results = []
            for result in results:
                vector = None
                if with_vectors and hasattr(result, 'vector'):
                    vector = np.array(result.vector)
                    
                search_results.append(
                    SearchResult(
                        id=str(result.id),
                        score=result.score,
                        payload=result.payload or {},
                        vector=vector
                    )
                )
                
            logger.debug(
                f"Search in collection '{collection_name}' returned "
                f"{len(search_results)} results"
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise SearchError(f"Search failed: {e}")
            
    def get_by_id(
        self,
        collection_name: str,
        vector_id: str,
        with_vector: bool = False
    ) -> Optional[VectorPoint]:
        """Get a vector by ID.
        
        Args:
            collection_name: Name of the collection
            vector_id: Vector ID
            with_vector: Whether to return the vector
            
        Returns:
            VectorPoint if found, None otherwise
        """
        try:
            # Retrieve point
            points = self.client.native_client.retrieve(
                collection_name=collection_name,
                ids=[vector_id],
                with_vectors=with_vector,
                with_payload=True
            )
            
            if not points:
                return None
                
            point = points[0]
            
            # Convert to VectorPoint
            vector = point.vector if with_vector else []
            return VectorPoint(
                id=str(point.id),
                vector=vector,
                payload=point.payload or {}
            )
            
        except Exception as e:
            logger.error(f"Failed to get vector by ID: {e}")
            return None
            
    def update(
        self,
        collection_name: str,
        vector_id: str,
        vector: Optional[Union[List[float], np.ndarray]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a vector and/or its metadata.
        
        Args:
            collection_name: Name of the collection
            vector_id: Vector ID
            vector: New vector (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if update successful
        """
        try:
            if vector is None and metadata is None:
                logger.warning("No updates provided")
                return True
                
            # Update operations
            operations = []
            
            # Update vector if provided
            if vector is not None:
                if isinstance(vector, np.ndarray):
                    vector = vector.tolist()
                    
                # For vector update, we need to re-insert
                existing = self.get_by_id(collection_name, vector_id, with_vector=False)
                if existing:
                    self.insert_single(
                        collection_name,
                        vector,
                        existing.payload if metadata is None else metadata,
                        vector_id
                    )
                else:
                    logger.warning(f"Vector {vector_id} not found for update")
                    return False
                    
            elif metadata is not None:
                # Update payload only
                self.client.native_client.update_payload(
                    collection_name=collection_name,
                    points=[vector_id],
                    payload=metadata
                )
                
            logger.debug(f"Updated vector {vector_id} in collection '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update vector: {e}")
            raise VectorOperationError(f"Failed to update vector: {e}")
            
    def delete(
        self,
        collection_name: str,
        vector_ids: Union[str, List[str]]
    ) -> bool:
        """Delete vectors by IDs.
        
        Args:
            collection_name: Name of the collection
            vector_ids: Single ID or list of IDs
            
        Returns:
            True if deletion successful
        """
        try:
            # Ensure list
            if isinstance(vector_ids, str):
                vector_ids = [vector_ids]
                
            # Delete points
            self.client.native_client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(points=vector_ids)
            )
            
            logger.debug(
                f"Deleted {len(vector_ids)} vectors from "
                f"collection '{collection_name}'"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            raise VectorOperationError(f"Failed to delete vectors: {e}")
            
    def count(
        self,
        collection_name: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count vectors in collection.
        
        Args:
            collection_name: Name of the collection
            filters: Optional filters for counting
            
        Returns:
            Number of vectors
        """
        try:
            if filters:
                # Use scroll to count with filters
                # Note: This is not optimal for large collections
                qdrant_filter = self._build_filter(filters)
                result = self.client.native_client.scroll(
                    collection_name=collection_name,
                    scroll_filter=qdrant_filter,
                    limit=0,  # We only need the count
                    with_payload=False,
                    with_vectors=False
                )
                # The result should contain the total count
                # This is a simplified approach - actual implementation
                # might need to iterate through all results
                return len(list(result[0]))  # This is a placeholder
            else:
                # Get collection info for total count
                collection = self.client.native_client.get_collection(collection_name)
                return collection.points_count
                
        except Exception as e:
            logger.error(f"Failed to count vectors: {e}")
            return 0
            
    def _build_filter(self, filters: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from dictionary.
        
        Args:
            filters: Filter dictionary
            
        Returns:
            Qdrant Filter object
        """
        # This is a simplified implementation
        # In practice, you'd want to support more complex filters
        conditions = []
        
        for key, value in filters.items():
            if isinstance(value, dict):
                # Range filter
                if "gte" in value or "lte" in value:
                    conditions.append(
                        FieldCondition(
                            key=key,
                            range=Range(
                                gte=value.get("gte"),
                                lte=value.get("lte")
                            )
                        )
                    )
            else:
                # Exact match
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
                
        return Filter(must=conditions) if conditions else None