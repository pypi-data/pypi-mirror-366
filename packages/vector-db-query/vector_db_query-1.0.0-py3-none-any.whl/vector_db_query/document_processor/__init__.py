"""Document processing module for Vector DB Query System."""

from vector_db_query.document_processor.processor import DocumentProcessor
from vector_db_query.document_processor.scanner import FileScanner
from vector_db_query.document_processor.reader import ReaderFactory
from vector_db_query.document_processor.chunker import SlidingWindowChunker, SemanticChunker
from vector_db_query.document_processor.embedder import GeminiEmbedder, EmbeddingBatcher
from vector_db_query.document_processor.models import (
    Chunk,
    Embedding,
    DocumentMetadata,
    ProcessedDocument,
    ProcessingError,
    ProcessingStats
)
from vector_db_query.document_processor.exceptions import (
    DocumentProcessingError,
    DocumentReadError,
    UnsupportedFileTypeError,
    FileTooLargeError,
    ChunkingError,
    EmbeddingError
)

# Base classes for new format families
from vector_db_query.document_processor.office_readers import (
    OfficeDocumentReader,
    SpreadsheetReader,
    PresentationReader
)
from vector_db_query.document_processor.web_readers import (
    WebDocumentReader,
    EmailDocumentReader
)
from vector_db_query.document_processor.image_readers import (
    ImageDocumentReader
)

# Concrete reader implementations
from vector_db_query.document_processor.excel_reader import ExcelReader
from vector_db_query.document_processor.powerpoint_reader import PowerPointReader

__all__ = [
    # Main processor
    "DocumentProcessor",
    
    # Components
    "FileScanner",
    "ReaderFactory",
    "SlidingWindowChunker",
    "SemanticChunker",
    "GeminiEmbedder",
    "EmbeddingBatcher",
    
    # Models
    "Chunk",
    "Embedding",
    "DocumentMetadata",
    "ProcessedDocument",
    "ProcessingError",
    "ProcessingStats",
    
    # Exceptions
    "DocumentProcessingError",
    "DocumentReadError",
    "UnsupportedFileTypeError",
    "FileTooLargeError",
    "ChunkingError",
    "EmbeddingError",
    
    # Base classes for new formats
    "OfficeDocumentReader",
    "SpreadsheetReader",
    "PresentationReader",
    "WebDocumentReader",
    "EmailDocumentReader",
    "ImageDocumentReader",
    
    # Concrete readers
    "ExcelReader",
    "PowerPointReader",
]