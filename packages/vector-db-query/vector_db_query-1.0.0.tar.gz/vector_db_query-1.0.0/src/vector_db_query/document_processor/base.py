"""Base classes for document processing."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from vector_db_query.document_processor.models import Chunk, Embedding


class DocumentReader(ABC):
    """Abstract base class for document readers."""
    
    @abstractmethod
    def can_read(self, file_path: Path) -> bool:
        """Check if this reader can handle the file type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the reader can handle this file type
        """
        pass
        
    @abstractmethod
    def read(self, file_path: Path) -> str:
        """Read the document and return its text content.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Text content of the document
            
        Raises:
            DocumentReadError: If the document cannot be read
        """
        pass
        
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions.
        
        Returns:
            List of extensions (e.g., ['.txt', '.md'])
        """
        pass


class ChunkingStrategy(ABC):
    """Abstract base class for text chunking strategies."""
    
    @abstractmethod
    def chunk(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs
    ) -> List[Chunk]:
        """Split text into chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            List of text chunks
        """
        pass
        
    def validate_parameters(self, chunk_size: int, chunk_overlap: int) -> None:
        """Validate chunking parameters.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap
            
        Raises:
            ValueError: If parameters are invalid
        """
        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        if chunk_overlap < 0:
            raise ValueError("Chunk overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")


class EmbeddingGenerator(ABC):
    """Abstract base class for embedding generators."""
    
    @abstractmethod
    def embed_single(self, text: str) -> Embedding:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding object
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass
        
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[Embedding]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding objects
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass
        
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the name of the embedding model.
        
        Returns:
            Model name
        """
        pass
        
    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Get the dimensionality of embeddings.
        
        Returns:
            Number of dimensions
        """
        pass