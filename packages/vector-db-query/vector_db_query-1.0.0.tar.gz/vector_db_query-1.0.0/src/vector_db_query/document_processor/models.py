"""Data models for document processing."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class Chunk:
    """Represents a text chunk from a document."""
    
    text: str
    start_pos: int
    end_pos: int
    chunk_id: str
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def size(self) -> int:
        """Get the size of the chunk in characters."""
        return len(self.text)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary."""
        return {
            "text": self.text,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "chunk_id": self.chunk_id,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata
        }


@dataclass
class Embedding:
    """Represents an embedding vector."""
    
    vector: np.ndarray
    chunk_id: str
    dimensions: int
    model: str
    normalized: bool = False
    
    def __post_init__(self):
        """Validate embedding after initialization."""
        if self.vector.shape[0] != self.dimensions:
            raise ValueError(
                f"Vector dimensions {self.vector.shape[0]} "
                f"don't match specified dimensions {self.dimensions}"
            )
            
    @property
    def norm(self) -> float:
        """Get the norm of the vector."""
        return float(np.linalg.norm(self.vector))
        
    def normalize(self) -> "Embedding":
        """Return a normalized copy of the embedding."""
        if self.normalized:
            return self
            
        norm = self.norm
        if norm == 0:
            raise ValueError("Cannot normalize zero vector")
            
        return Embedding(
            vector=self.vector / norm,
            chunk_id=self.chunk_id,
            dimensions=self.dimensions,
            model=self.model,
            normalized=True
        )
        
    def to_list(self) -> List[float]:
        """Convert vector to list."""
        return self.vector.tolist()


@dataclass
class DocumentMetadata:
    """Metadata for a processed document."""
    
    filename: str
    file_path: str
    file_size: int
    file_type: str
    modified_time: datetime
    chunk_count: int
    processing_date: datetime
    encoding: Optional[str] = None
    custom_tags: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_path(cls, file_path: Path) -> "DocumentMetadata":
        """Create metadata from file path."""
        stat = file_path.stat()
        return cls(
            filename=file_path.name,
            file_path=str(file_path),
            file_size=stat.st_size,
            file_type=file_path.suffix.lower(),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            chunk_count=0,  # Will be updated during processing
            processing_date=datetime.now()
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "modified_time": self.modified_time.isoformat(),
            "chunk_count": self.chunk_count,
            "processing_date": self.processing_date.isoformat(),
            "encoding": self.encoding,
            "custom_tags": self.custom_tags
        }


@dataclass
class ProcessingError:
    """Represents an error during document processing."""
    
    error_type: str
    message: str
    file_path: Optional[str] = None
    chunk_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    recoverable: bool = False
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation of the error."""
        parts = [f"[{self.error_type}] {self.message}"]
        if self.file_path:
            parts.append(f"File: {self.file_path}")
        if self.chunk_id:
            parts.append(f"Chunk: {self.chunk_id}")
        return " | ".join(parts)


@dataclass
class ProcessedDocument:
    """Represents a fully processed document."""
    
    file_path: Path
    chunks: List[Chunk]
    embeddings: List[Embedding]
    metadata: DocumentMetadata
    processing_time: float
    errors: List[ProcessingError] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Check if processing was successful."""
        return len(self.chunks) > 0 and len(self.embeddings) == len(self.chunks)
        
    @property
    def partial_success(self) -> bool:
        """Check if processing was partially successful."""
        return len(self.embeddings) > 0
        
    def get_summary(self) -> Dict[str, Any]:
        """Get processing summary."""
        return {
            "file": self.metadata.filename,
            "chunks": len(self.chunks),
            "embeddings": len(self.embeddings),
            "errors": len(self.errors),
            "processing_time": f"{self.processing_time:.2f}s",
            "success": self.success
        }


@dataclass
class ProcessingStats:
    """Statistics for document processing batch."""
    
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    total_chunks: int = 0
    total_embeddings: int = 0
    total_errors: int = 0
    processing_time: float = 0.0
    
    def add_document(self, doc: ProcessedDocument) -> None:
        """Add document stats to totals."""
        if doc.success:
            self.processed_files += 1
        elif doc.partial_success:
            self.processed_files += 1
        else:
            self.failed_files += 1
            
        self.total_chunks += len(doc.chunks)
        self.total_embeddings += len(doc.embeddings)
        self.total_errors += len(doc.errors)
        self.processing_time += doc.processing_time
        
    def get_summary(self) -> str:
        """Get summary string."""
        return (
            f"Processed: {self.processed_files}/{self.total_files} files | "
            f"Failed: {self.failed_files} | "
            f"Chunks: {self.total_chunks} | "
            f"Embeddings: {self.total_embeddings} | "
            f"Time: {self.processing_time:.1f}s"
        )