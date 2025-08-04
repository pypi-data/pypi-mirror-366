"""Multi-dimension query system for handling collections with different vector sizes."""

import os
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import CollectionInfo

from vector_db_query.utils.logger import get_logger
from vector_db_query.utils.config import get_config

logger = get_logger(__name__)


class EmbeddingModel(Enum):
    """Supported embedding models with their dimensions."""
    GEMINI_768 = ("models/embedding-001", 768, "gemini")
    # Future support for other models
    # OPENAI_384 = ("text-embedding-3-small", 384, "openai")
    # OPENAI_1536 = ("text-embedding-3-large", 1536, "openai")
    

@dataclass
class ModelConfig:
    """Configuration for an embedding model."""
    name: str
    dimension: int
    provider: str
    task_type: str = "retrieval_query"


class MultiDimensionQuerySystem:
    """Query system that handles collections with different vector dimensions."""
    
    def __init__(self):
        """Initialize the multi-dimension query system."""
        self.config = get_config()
        self.qdrant_client = self._init_qdrant()
        
        # Cache for initialized models
        self._model_cache: Dict[int, ModelConfig] = {}
        self._embedders: Dict[int, any] = {}
        
        # Initialize Google AI
        api_key = os.getenv("GOOGLE_API_KEY") or self.config.get("embeddings.api_key")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        genai.configure(api_key=api_key)
        
        # Map dimensions to models
        self._dimension_map = {
            768: ModelConfig("models/embedding-001", 768, "gemini"),
            # For 384-dim collections, we'll use 768 and let Qdrant handle it
            384: ModelConfig("models/embedding-001", 768, "gemini"),
        }
        
    def _init_qdrant(self) -> QdrantClient:
        """Initialize Qdrant client."""
        return QdrantClient(
            host=self.config.get("qdrant.host", "localhost"),
            port=self.config.get("qdrant.port", 6333),
            api_key=self.config.get("qdrant.api_key"),
            timeout=self.config.get("qdrant.timeout", 30)
        )
        
    def get_collection_info(self, collection_name: str) -> CollectionInfo:
        """Get information about a collection."""
        try:
            return self.qdrant_client.get_collection(collection_name)
        except Exception as e:
            logger.error(f"Failed to get collection info for {collection_name}: {e}")
            raise
            
    def get_collection_dimension(self, collection_name: str) -> int:
        """Get the vector dimension of a collection."""
        info = self.get_collection_info(collection_name)
        return info.config.params.vectors.size
        
    def get_all_collections(self) -> List[Tuple[str, int]]:
        """Get all collections with their dimensions."""
        collections = []
        try:
            response = self.qdrant_client.get_collections()
            for col in response.collections:
                try:
                    dim = self.get_collection_dimension(col.name)
                    collections.append((col.name, dim))
                except Exception as e:
                    logger.warning(f"Could not get dimension for {col.name}: {e}")
        except Exception as e:
            logger.error(f"Failed to get collections: {e}")
        return collections
        
    def _get_embedder_for_dimension(self, dimension: int):
        """Get or create an embedder for the specified dimension."""
        if dimension not in self._embedders:
            model_config = self._dimension_map.get(dimension)
            if not model_config:
                # Default to 768-dim model
                logger.warning(f"No model config for dimension {dimension}, using 768-dim model")
                model_config = self._dimension_map[768]
                
            self._model_cache[dimension] = model_config
            self._embedders[dimension] = model_config
            
        return self._embedders[dimension]
        
    def generate_embedding(self, text: str, target_dimension: int) -> List[float]:
        """Generate embedding for text, handling dimension requirements."""
        model_config = self._get_embedder_for_dimension(target_dimension)
        
        try:
            # For now, we only support Gemini
            response = genai.embed_content(
                model=model_config.name,
                content=text,
                task_type=model_config.task_type
            )
            embedding = response['embedding']
            
            # Handle dimension mismatch
            if len(embedding) != target_dimension:
                if target_dimension == 384 and len(embedding) == 768:
                    # Truncate 768 to 384 (simple approach)
                    logger.info(f"Truncating embedding from {len(embedding)} to {target_dimension}")
                    embedding = embedding[:target_dimension]
                else:
                    logger.warning(f"Dimension mismatch: got {len(embedding)}, expected {target_dimension}")
                    
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
            
    def search_collection(
        self,
        collection_name: str,
        query_text: str,
        limit: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict]:
        """Search a specific collection, handling its dimension requirements."""
        try:
            # Get collection dimension
            dimension = self.get_collection_dimension(collection_name)
            logger.info(f"Searching {collection_name} (dim={dimension}) for: {query_text}")
            
            # Generate embedding with appropriate dimension
            query_vector = self.generate_embedding(query_text, dimension)
            
            # Search
            results = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Convert to standard format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': str(result.id),
                    'score': result.score,
                    'payload': result.payload or {},
                    'collection': collection_name,
                    'dimension': dimension
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed for {collection_name}: {e}")
            raise
            
    def search_all_collections(
        self,
        query_text: str,
        limit_per_collection: int = 3
    ) -> Dict[str, List[Dict]]:
        """Search across all collections, handling different dimensions."""
        all_results = {}
        collections = self.get_all_collections()
        
        for collection_name, dimension in collections:
            try:
                results = self.search_collection(
                    collection_name,
                    query_text,
                    limit=limit_per_collection
                )
                if results:
                    all_results[collection_name] = results
                    logger.info(f"Found {len(results)} results in {collection_name}")
            except Exception as e:
                logger.error(f"Failed to search {collection_name}: {e}")
                all_results[collection_name] = [{
                    'error': str(e),
                    'dimension': dimension
                }]
                
        return all_results
        
    def read_collection(
        self,
        collection_name: str,
        limit: int = 100,
        offset: Optional[str] = None
    ) -> Tuple[List[Dict], Optional[str]]:
        """Read documents from a collection without needing embeddings."""
        try:
            # Use scroll to read documents
            records, next_offset = self.qdrant_client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False  # Don't need vectors for reading
            )
            
            # Format results
            documents = []
            for record in records:
                documents.append({
                    'id': str(record.id),
                    'payload': record.payload or {},
                    'collection': collection_name
                })
                
            return documents, next_offset
            
        except Exception as e:
            logger.error(f"Failed to read from {collection_name}: {e}")
            raise