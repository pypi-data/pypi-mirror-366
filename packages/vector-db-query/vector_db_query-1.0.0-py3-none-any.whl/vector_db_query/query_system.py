"""Production-ready query system for Vector DB Query."""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import google.generativeai as genai
from dotenv import load_dotenv

from vector_db_query.utils.logger import get_logger
from vector_db_query.utils.config import get_config

logger = get_logger(__name__)


@dataclass
class QueryResult:
    """Structured query result."""
    content: str
    source: str
    score: float
    metadata: Dict[str, Any]
    chunk_id: Optional[str] = None


class VectorQuerySystem:
    """Production-ready vector query system."""
    
    def __init__(self, collection_name: str = "documents"):
        """Initialize the query system.
        
        Args:
            collection_name: Name of the Qdrant collection to query
        """
        # Load configuration
        load_dotenv()
        self.config = get_config()
        
        # Initialize clients
        self._init_qdrant()
        self._init_embedder()
        
        self.collection_name = collection_name
        self._ensure_collection()
        
    def _init_qdrant(self):
        """Initialize Qdrant client."""
        self.qdrant_client = QdrantClient(
            host=self.config.get("qdrant.host", "localhost"),
            port=self.config.get("qdrant.port", 6333),
            api_key=self.config.get("qdrant.api_key"),
            timeout=self.config.get("qdrant.timeout", 30)
        )
        logger.info("Qdrant client initialized")
        
    def _init_embedder(self):
        """Initialize Google Generative AI for embeddings."""
        api_key = os.getenv("GOOGLE_API_KEY") or self.config.get("embeddings.api_key")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment or config")
            
        genai.configure(api_key=api_key)
        self.embedding_model = self.config.get("embeddings.model", "models/embedding-001")
        logger.info(f"Embedder initialized with model: {self.embedding_model}")
        
    def _ensure_collection(self):
        """Ensure the collection exists."""
        try:
            self.qdrant_client.get_collection(self.collection_name)
            logger.info(f"Collection '{self.collection_name}' exists")
        except Exception:
            logger.warning(f"Collection '{self.collection_name}' not found, creating...")
            self.create_collection()
            
    def create_collection(self):
        """Create the collection with proper configuration."""
        vector_size = self.config.get("embeddings.dimension", 768)
        distance_metric = getattr(Distance, self.config.get("qdrant.distance_metric", "COSINE"))
        
        self.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=distance_metric
            )
        )
        logger.info(f"Created collection '{self.collection_name}' with vector size {vector_size}")
        
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text query.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_query"
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
            
    def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.0,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[QueryResult]:
        """Search for documents similar to the query.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter_conditions: Optional filter conditions
            
        Returns:
            List of query results
        """
        logger.info(f"Searching for: '{query}'")
        
        # Generate query embedding
        query_vector = self.generate_embedding(query)
        
        # Perform search
        try:
            results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_conditions
            )
            
            # Convert to QueryResult objects
            query_results = []
            for result in results:
                payload = result.payload or {}
                query_results.append(
                    QueryResult(
                        content=payload.get('chunk_text', payload.get('content', '')),
                        source=payload.get('source_file', payload.get('source', 'Unknown')),
                        score=result.score,
                        metadata=payload,
                        chunk_id=str(result.id) if result.id else None
                    )
                )
                
            logger.info(f"Found {len(query_results)} results")
            return query_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
            
    def store_document(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """Store a single document in the vector database.
        
        Args:
            content: Document content
            source: Source file or identifier
            metadata: Optional metadata
            doc_id: Optional document ID
            
        Returns:
            Document ID
        """
        # Generate embedding
        embedding = self.generate_embedding(content)
        
        # Create point
        point_id = doc_id or str(hash(content))
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "content": content,
                "source": source,
                "metadata": metadata or {}
            }
        )
        
        # Store in Qdrant
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        logger.info(f"Stored document from {source} with ID {point_id}")
        return point_id
        
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection.
        
        Returns:
            Collection information
        """
        try:
            info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance
                }
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
            
    def delete_collection(self):
        """Delete the collection."""
        try:
            self.qdrant_client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise


# Convenience function for quick searches
def quick_search(query: str, collection: str = "documents", limit: int = 5) -> List[Dict[str, Any]]:
    """Perform a quick search without instantiating the full system.
    
    Args:
        query: Search query
        collection: Collection name
        limit: Number of results
        
    Returns:
        List of results as dictionaries
    """
    system = VectorQuerySystem(collection_name=collection)
    results = system.search(query, limit=limit)
    
    return [
        {
            "content": r.content,
            "source": r.source,
            "score": r.score,
            "metadata": r.metadata
        }
        for r in results
    ]