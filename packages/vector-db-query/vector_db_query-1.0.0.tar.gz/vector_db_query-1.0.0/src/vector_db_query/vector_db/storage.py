"""Storage manager for document embeddings."""

import time
from typing import Dict, List, Optional

from vector_db_query.document_processor.models import ProcessedDocument, Embedding
from vector_db_query.vector_db.client import QdrantClient
from vector_db_query.vector_db.collection import CollectionManager
from vector_db_query.vector_db.operations import VectorOperations
from vector_db_query.vector_db.models import (
    StorageResult,
    StorageStats,
    CollectionConfig,
    VectorPoint
)
from vector_db_query.vector_db.exceptions import StorageError
from vector_db_query.utils.config import get_config
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class StorageManager:
    """Manages storage of document embeddings in vector database."""
    
    def __init__(
        self,
        client: QdrantClient,
        collection_manager: Optional[CollectionManager] = None,
        operations: Optional[VectorOperations] = None
    ):
        """Initialize storage manager.
        
        Args:
            client: Qdrant client instance
            collection_manager: Collection manager (created if not provided)
            operations: Vector operations handler (created if not provided)
        """
        self.client = client
        self.collection_manager = collection_manager or CollectionManager(client)
        self.operations = operations or VectorOperations(client)
        self.config = get_config()
        
    def store_documents(
        self,
        documents: List[ProcessedDocument],
        collection_name: Optional[str] = None,
        create_collection: bool = True
    ) -> StorageResult:
        """Store processed documents with their embeddings.
        
        Args:
            documents: List of processed documents
            collection_name: Name of collection (uses default if not provided)
            create_collection: Whether to create collection if it doesn't exist
            
        Returns:
            StorageResult with statistics
        """
        start_time = time.time()
        
        # Use default collection name if not provided
        if collection_name is None:
            collection_name = self.config.get("vector_db.collection_name", "documents")
            
        stored_count = 0
        failed_count = 0
        errors = []
        
        try:
            # Ensure collection exists
            if create_collection and not self.collection_manager.collection_exists(collection_name):
                logger.info(f"Creating collection '{collection_name}'")
                
                # Get vector size from first document with embeddings
                vector_size = None
                for doc in documents:
                    if doc.embeddings:
                        vector_size = doc.embeddings[0].dimensions
                        break
                        
                if vector_size is None:
                    raise StorageError("No embeddings found in documents")
                    
                # Create collection
                collection_config = CollectionConfig(
                    name=collection_name,
                    vector_size=vector_size,
                    distance=self.config.get("vector_db.distance_metric", "Cosine")
                )
                self.collection_manager.create_from_config(collection_config)
                
            # Process each document
            for doc in documents:
                try:
                    count = self._store_document(doc, collection_name)
                    stored_count += count
                except Exception as e:
                    logger.error(f"Failed to store document {doc.file_path}: {e}")
                    failed_count += len(doc.embeddings) if doc.embeddings else 1
                    errors.append(f"{doc.metadata.filename}: {str(e)}")
                    
            duration = time.time() - start_time
            
            return StorageResult(
                success=failed_count == 0,
                stored_count=stored_count,
                failed_count=failed_count,
                collection_name=collection_name,
                duration=duration,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Storage operation failed: {e}")
            raise StorageError(f"Failed to store documents: {e}")
            
    def store_embeddings(
        self,
        embeddings: List[Embedding],
        metadata_list: List[Dict[str, any]],
        collection_name: Optional[str] = None
    ) -> StorageResult:
        """Store embeddings with metadata.
        
        Args:
            embeddings: List of embeddings
            metadata_list: List of metadata dictionaries
            collection_name: Name of collection
            
        Returns:
            StorageResult with statistics
        """
        if len(embeddings) != len(metadata_list):
            raise ValueError("Number of embeddings must match metadata entries")
            
        start_time = time.time()
        
        # Use default collection name if not provided
        if collection_name is None:
            collection_name = self.config.get("vector_db.collection_name", "documents")
            
        try:
            # Extract vectors and IDs
            vectors = [emb.to_list() for emb in embeddings]
            vector_ids = [emb.chunk_id for emb in embeddings]
            
            # Store in batches
            stored_ids = self.operations.insert_batch(
                collection_name=collection_name,
                vectors=vectors,
                metadatas=metadata_list,
                vector_ids=vector_ids
            )
            
            duration = time.time() - start_time
            
            return StorageResult(
                success=True,
                stored_count=len(stored_ids),
                failed_count=0,
                collection_name=collection_name,
                duration=duration,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to store embeddings: {e}")
            raise StorageError(f"Failed to store embeddings: {e}")
            
    def get_storage_stats(self) -> StorageStats:
        """Get storage statistics across all collections.
        
        Returns:
            StorageStats object
        """
        try:
            # Get all collections
            collections = self.collection_manager.list_collections()
            
            total_vectors = 0
            total_collections = len(collections)
            collections_dict = {}
            
            # Get stats for each collection
            for collection in collections:
                collections_dict[collection.name] = collection.vectors_count
                total_vectors += collection.vectors_count
                
            # Note: Disk and memory usage would require additional API calls
            # or direct access to Qdrant metrics
            return StorageStats(
                total_vectors=total_vectors,
                total_collections=total_collections,
                disk_usage_mb=0.0,  # Placeholder
                memory_usage_mb=0.0,  # Placeholder
                collections=collections_dict
            )
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return StorageStats(
                total_vectors=0,
                total_collections=0,
                disk_usage_mb=0.0,
                memory_usage_mb=0.0,
                collections={}
            )
            
    def optimize_collection(self, collection_name: str) -> bool:
        """Optimize a collection for better performance.
        
        Args:
            collection_name: Name of collection to optimize
            
        Returns:
            True if optimization successful
        """
        try:
            return self.collection_manager.optimize_collection(collection_name)
        except Exception as e:
            logger.error(f"Failed to optimize collection: {e}")
            return False
            
    def _store_document(self, document: ProcessedDocument, collection_name: str) -> int:
        """Store a single document's embeddings.
        
        Args:
            document: Processed document
            collection_name: Target collection
            
        Returns:
            Number of vectors stored
        """
        if not document.embeddings:
            logger.warning(f"No embeddings found for document {document.file_path}")
            return 0
            
        # Prepare metadata for each chunk
        metadata_list = []
        
        for i, (chunk, embedding) in enumerate(zip(document.chunks, document.embeddings)):
            # Create metadata combining chunk and document info
            metadata = {
                # Chunk information
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "chunk_text": chunk.text[:200],  # First 200 chars
                "chunk_size": chunk.size,
                "start_pos": chunk.start_pos,
                "end_pos": chunk.end_pos,
                
                # Document information
                "document_id": str(document.file_path),
                "file_path": str(document.file_path),
                "file_name": document.metadata.filename,
                "file_type": document.metadata.file_type,
                "file_size": document.metadata.file_size,
                
                # Processing information
                "created_at": document.metadata.processing_date.isoformat(),
                "embedding_model": embedding.model,
                "embedding_dimensions": embedding.dimensions,
                
                # Custom metadata from chunk
                **chunk.metadata
            }
            
            # Add custom tags from document if any
            if document.metadata.custom_tags:
                metadata["custom_tags"] = document.metadata.custom_tags
                
            metadata_list.append(metadata)
            
        # Extract embeddings
        embeddings = document.embeddings[:len(metadata_list)]
        
        # Store embeddings
        result = self.store_embeddings(
            embeddings=embeddings,
            metadata_list=metadata_list,
            collection_name=collection_name
        )
        
        return result.stored_count