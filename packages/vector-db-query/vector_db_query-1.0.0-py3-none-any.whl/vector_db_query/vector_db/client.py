"""Qdrant client wrapper for vector database operations."""

import os
import time
from typing import Optional

from qdrant_client import QdrantClient as QdrantClientBase
from qdrant_client.models import Distance
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse

from vector_db_query.vector_db.models import HealthStatus
from vector_db_query.vector_db.exceptions import (
    ConnectionError,
    HealthCheckError
)
from vector_db_query.utils.config import get_config
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class QdrantClient:
    """Wrapper for Qdrant client with enhanced functionality."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        api_key: Optional[str] = None,
        prefer_grpc: bool = False,
        timeout: Optional[int] = None
    ):
        """Initialize Qdrant client.
        
        Args:
            host: Qdrant host address
            port: Qdrant port
            api_key: API key for authentication
            prefer_grpc: Whether to prefer gRPC over HTTP
            timeout: Request timeout in seconds
        """
        config = get_config()
        
        self.host = host or config.get("vector_db.host", "localhost")
        self.port = port or config.get("vector_db.port", 6333)
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.prefer_grpc = prefer_grpc
        self.timeout = timeout or config.get("vector_db.timeout", 30)
        
        self._client: Optional[QdrantClientBase] = None
        self._connected = False
        
    def connect(self, retry_attempts: int = 3, retry_delay: float = 2.0) -> bool:
        """Connect to Qdrant server with retry logic.
        
        Args:
            retry_attempts: Number of connection attempts
            retry_delay: Delay between attempts in seconds
            
        Returns:
            True if connection successful
            
        Raises:
            ConnectionError: If connection fails after all attempts
        """
        last_error = None
        
        for attempt in range(retry_attempts):
            try:
                logger.info(
                    f"Connecting to Qdrant at {self.host}:{self.port} "
                    f"(attempt {attempt + 1}/{retry_attempts})"
                )
                
                # Create client
                self._client = QdrantClientBase(
                    host=self.host,
                    port=self.port,
                    api_key=self.api_key,
                    prefer_grpc=self.prefer_grpc,
                    timeout=self.timeout
                )
                
                # Test connection
                info = self._client.get_collections()
                
                self._connected = True
                logger.info(f"Successfully connected to Qdrant (found {len(info.collections)} collections)")
                return True
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Connection attempt {attempt + 1} failed: {e}"
                )
                
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    
        # All attempts failed
        raise ConnectionError(
            f"Failed to connect to Qdrant after {retry_attempts} attempts: {last_error}"
        )
        
    def disconnect(self) -> None:
        """Disconnect from Qdrant server."""
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass  # Ignore errors during cleanup
            finally:
                self._client = None
                self._connected = False
                
        logger.info("Disconnected from Qdrant")
        
    def health_check(self) -> HealthStatus:
        """Check health status of Qdrant server.
        
        Returns:
            HealthStatus object
        """
        if not self._client:
            return HealthStatus(
                is_healthy=False,
                error="Client not connected"
            )
            
        try:
            # Get cluster info
            info = self._client.get_cluster_info()
            
            # Get collections info
            collections = self._client.get_collections()
            
            # Count total vectors
            total_vectors = 0
            for collection in collections.collections:
                try:
                    collection_info = self._client.get_collection(collection.name)
                    total_vectors += collection_info.points_count
                except Exception:
                    pass  # Skip if collection info fails
                    
            # Parse version
            version = "unknown"
            if hasattr(info, 'version'):
                version = info.version
            elif hasattr(info, 'commit'):
                version = f"commit-{info.commit[:8]}"
                
            return HealthStatus(
                is_healthy=True,
                version=version,
                collections_count=len(collections.collections),
                vectors_count=total_vectors,
                # Disk and memory usage would require additional API calls
                disk_usage_mb=0.0,
                memory_usage_mb=0.0
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthStatus(
                is_healthy=False,
                error=str(e)
            )
            
    def get_collections(self) -> list:
        """Get list of all collections.
        
        Returns:
            List of collection names
            
        Raises:
            ConnectionError: If not connected
        """
        self._ensure_connected()
        
        try:
            result = self._client.get_collections()
            return [col.name for col in result.collections]
        except Exception as e:
            logger.error(f"Failed to get collections: {e}")
            raise ConnectionError(f"Failed to get collections: {e}")
            
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self._client is not None
        
    @property
    def native_client(self) -> QdrantClientBase:
        """Get native Qdrant client for direct operations.
        
        Returns:
            Native Qdrant client
            
        Raises:
            ConnectionError: If not connected
        """
        self._ensure_connected()
        return self._client
        
    def _ensure_connected(self) -> None:
        """Ensure client is connected.
        
        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected:
            raise ConnectionError("Client not connected. Call connect() first.")
            
    @staticmethod
    def distance_from_string(distance: str) -> Distance:
        """Convert string distance metric to Qdrant Distance enum.
        
        Args:
            distance: Distance metric name (Cosine, Euclidean, Dot)
            
        Returns:
            Distance enum value
        """
        distance_map = {
            "cosine": Distance.COSINE,
            "euclidean": Distance.EUCLID,
            "dot": Distance.DOT,
        }
        
        return distance_map.get(distance.lower(), Distance.COSINE)