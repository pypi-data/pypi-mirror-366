"""High-level vector database service."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from vector_db_query.document_processor import DocumentProcessor, ProcessedDocument
from vector_db_query.document_processor.embedder import GeminiEmbedder
from vector_db_query.vector_db.docker_manager import QdrantDockerManager
from vector_db_query.vector_db.client import QdrantClient
from vector_db_query.vector_db.collection import CollectionManager
from vector_db_query.vector_db.operations import VectorOperations
from vector_db_query.vector_db.storage import StorageManager
from vector_db_query.vector_db.models import (
    SearchResult,
    StorageResult,
    HealthStatus,
    CollectionConfig
)
from vector_db_query.vector_db.exceptions import VectorDBError, ConnectionError
from vector_db_query.utils.config import get_config
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class VectorDBService:
    """High-level service for vector database operations."""
    
    def __init__(self, auto_start: bool = True):
        """Initialize vector database service.
        
        Args:
            auto_start: Whether to automatically start Qdrant
        """
        self.config = get_config()
        
        # Initialize components
        self.docker_manager = QdrantDockerManager()
        self.client = QdrantClient()
        self.collections = CollectionManager(self.client)
        self.operations = VectorOperations(self.client)
        self.storage = StorageManager(self.client, self.collections, self.operations)
        
        # For embedding queries
        self._embedder = None
        
        self._initialized = False
        
        if auto_start:
            try:
                self.initialize()
            except Exception as e:
                logger.warning(f"Auto-initialization failed: {e}")
                
    def initialize(self, timeout: int = 60) -> bool:
        """Initialize the vector database system.
        
        Args:
            timeout: Timeout for initialization in seconds
            
        Returns:
            True if initialization successful
            
        Raises:
            VectorDBError: If initialization fails
        """
        try:
            logger.info("Initializing vector database service")
            
            # Start Docker container if needed
            if not self.docker_manager.is_running():
                logger.info("Starting Qdrant container")
                if not self.docker_manager.start_container():
                    raise VectorDBError("Failed to start Qdrant container")
                    
                # Wait for health
                if not self.docker_manager.wait_for_health(timeout):
                    raise VectorDBError("Qdrant health check timeout")
                    
            # Connect client
            logger.info("Connecting to Qdrant")
            self.client.connect()
            
            # Create default collection if configured
            default_collection = self.config.get("vector_db.collection_name")
            if default_collection and not self.collections.collection_exists(default_collection):
                logger.info(f"Creating default collection '{default_collection}'")
                
                config = CollectionConfig(
                    name=default_collection,
                    vector_size=self.config.get("embedding.dimensions", 768),
                    distance=self.config.get("vector_db.distance_metric", "Cosine")
                )
                self.collections.create_from_config(config)
                
            self._initialized = True
            logger.info("Vector database service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            raise VectorDBError(f"Initialization failed: {e}")
            
    def shutdown(self, stop_container: bool = False) -> None:
        """Shutdown the vector database service.
        
        Args:
            stop_container: Whether to stop the Docker container
        """
        logger.info("Shutting down vector database service")
        
        # Disconnect client
        if self.client.is_connected:
            self.client.disconnect()
            
        # Stop container if requested
        if stop_container and self.docker_manager.is_running():
            logger.info("Stopping Qdrant container")
            self.docker_manager.stop_container()
            
        # Cleanup
        self.docker_manager.cleanup()
        self._initialized = False
        
    def store_processed_documents(
        self,
        documents: List[ProcessedDocument],
        collection_name: Optional[str] = None,
        show_progress: bool = True
    ) -> StorageResult:
        """Store processed documents with embeddings.
        
        Args:
            documents: List of processed documents
            collection_name: Target collection name
            show_progress: Whether to show progress
            
        Returns:
            StorageResult with statistics
        """
        self._ensure_initialized()
        
        logger.info(f"Storing {len(documents)} documents")
        
        # Filter documents with embeddings
        valid_docs = [doc for doc in documents if doc.embeddings]
        if len(valid_docs) < len(documents):
            logger.warning(
                f"Skipping {len(documents) - len(valid_docs)} documents "
                f"without embeddings"
            )
            
        if not valid_docs:
            return StorageResult(
                success=False,
                stored_count=0,
                failed_count=len(documents),
                collection_name=collection_name or "documents",
                duration=0.0,
                errors=["No documents with embeddings to store"]
            )
            
        # Store documents
        return self.storage.store_documents(valid_docs, collection_name)
        
    def search_similar(
        self,
        query_text: str,
        limit: int = 10,
        collection_name: Optional[str] = None,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents using text query.
        
        Args:
            query_text: Query text
            limit: Maximum number of results
            collection_name: Collection to search
            score_threshold: Minimum similarity score
            filters: Metadata filters
            
        Returns:
            List of search results
        """
        self._ensure_initialized()
        
        # Use default collection if not specified
        if collection_name is None:
            collection_name = self.config.get("vector_db.collection_name", "documents")
            
        # Generate query embedding
        query_embedding = self._get_query_embedding(query_text)
        
        # Search
        return self.operations.search(
            collection_name=collection_name,
            query_vector=query_embedding.to_list(),
            limit=limit,
            score_threshold=score_threshold,
            filters=filters
        )
        
    def search_similar_vector(
        self,
        query_vector: Union[List[float], "np.ndarray"],
        limit: int = 10,
        collection_name: Optional[str] = None,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents using vector.
        
        Args:
            query_vector: Query vector
            limit: Maximum number of results
            collection_name: Collection to search
            score_threshold: Minimum similarity score
            filters: Metadata filters
            
        Returns:
            List of search results
        """
        self._ensure_initialized()
        
        # Use default collection if not specified
        if collection_name is None:
            collection_name = self.config.get("vector_db.collection_name", "documents")
            
        # Search
        return self.operations.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            filters=filters
        )
        
    def process_and_store(
        self,
        file_paths: Union[Path, List[Path]],
        collection_name: Optional[str] = None,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """Process documents and store embeddings in one operation.
        
        Args:
            file_paths: File or list of files to process
            collection_name: Target collection
            show_progress: Whether to show progress
            
        Returns:
            Dictionary with processing and storage results
        """
        self._ensure_initialized()
        
        # Ensure list
        if isinstance(file_paths, (str, Path)):
            file_paths = [Path(file_paths)]
        else:
            file_paths = [Path(p) for p in file_paths]
            
        # Process documents
        processor = DocumentProcessor()
        documents = processor.process_files(file_paths)
        
        # Store documents
        storage_result = self.store_processed_documents(
            documents,
            collection_name,
            show_progress
        )
        
        return {
            "processing_stats": processor.get_stats().get_summary(),
            "storage_result": storage_result.get_summary(),
            "documents_processed": len(documents),
            "vectors_stored": storage_result.stored_count,
            "errors": storage_result.errors
        }
        
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information.
        
        Returns:
            Status dictionary
        """
        status = {
            "service_initialized": self._initialized,
            "docker_running": False,
            "client_connected": False,
            "health_status": None,
            "storage_stats": None,
            "collections": []
        }
        
        try:
            # Check Docker
            status["docker_running"] = self.docker_manager.is_running()
            
            if status["docker_running"]:
                status["docker_info"] = self.docker_manager.get_container_info()
                
            # Check client
            status["client_connected"] = self.client.is_connected
            
            if status["client_connected"]:
                # Get health status
                health = self.client.health_check()
                status["health_status"] = health.to_dict()
                
                # Get storage stats
                stats = self.storage.get_storage_stats()
                status["storage_stats"] = {
                    "total_vectors": stats.total_vectors,
                    "total_collections": stats.total_collections,
                    "collections": stats.collections
                }
                
                # Get collection details
                collections = self.collections.list_collections()
                status["collections"] = [
                    {
                        "name": col.name,
                        "vectors": col.vectors_count,
                        "vector_size": col.vector_size,
                        "status": col.status
                    }
                    for col in collections
                ]
                
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            status["error"] = str(e)
            
        return status
        
    def _ensure_initialized(self) -> None:
        """Ensure service is initialized.
        
        Raises:
            VectorDBError: If not initialized
        """
        if not self._initialized:
            raise VectorDBError("Service not initialized. Call initialize() first.")
            
    def _get_query_embedding(self, text: str):
        """Generate embedding for query text.
        
        Args:
            text: Query text
            
        Returns:
            Embedding object
        """
        if self._embedder is None:
            self._embedder = GeminiEmbedder(
                dimensions=self.config.get("embedding.dimensions", 768),
                task_type="RETRIEVAL_QUERY"  # Optimize for queries
            )
            
        return self._embedder.embed_single(text)