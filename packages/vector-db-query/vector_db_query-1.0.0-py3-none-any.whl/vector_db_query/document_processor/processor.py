"""Main document processor that orchestrates the pipeline."""

import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Iterator

from vector_db_query.document_processor.scanner import FileScanner
from vector_db_query.document_processor.reader import ReaderFactory
from vector_db_query.document_processor.chunker import SlidingWindowChunker, SemanticChunker
from vector_db_query.document_processor.embedder import GeminiEmbedder, EmbeddingBatcher
from vector_db_query.document_processor.models import (
    ProcessedDocument, ProcessingStats, ProcessingError, Chunk
)
from vector_db_query.document_processor.exceptions import DocumentProcessingError
from vector_db_query.utils.config import get_config
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Orchestrates the document processing pipeline."""
    
    def __init__(
        self,
        embedder: Optional[GeminiEmbedder] = None,
        chunking_strategy: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        batch_size: Optional[int] = None,
        allowed_formats: Optional[List[str]] = None,
        enable_ocr: bool = False,
        ocr_language: str = "eng"
    ):
        """Initialize the document processor.
        
        Args:
            embedder: Embedding generator (creates default if not provided)
            chunking_strategy: Strategy to use ('sliding_window' or 'semantic')
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            batch_size: Batch size for embedding generation
            allowed_formats: List of allowed file extensions (None = all)
            enable_ocr: Enable OCR for image files
            ocr_language: OCR language code
        """
        config = get_config()
        
        # Initialize components
        self.scanner = FileScanner(allowed_formats=allowed_formats)
        self.reader_factory = ReaderFactory(enable_ocr=enable_ocr, ocr_language=ocr_language)
        self.enable_ocr = enable_ocr
        self.ocr_language = ocr_language
        
        # Set up chunking
        self.chunking_strategy = chunking_strategy or config.get(
            "document_processing.chunking.strategy", "sliding_window"
        )
        self.chunk_size = chunk_size or config.get(
            "document_processing.chunking.chunk_size", 1000
        )
        self.chunk_overlap = chunk_overlap or config.get(
            "document_processing.chunking.chunk_overlap", 200
        )
        
        if self.chunking_strategy == "semantic":
            self.chunker = SemanticChunker()
        else:
            self.chunker = SlidingWindowChunker()
            
        # Set up embedding
        self.embedder = embedder or GeminiEmbedder()
        batch_size = batch_size or config.get("embedding.batch_size", 100)
        self.batcher = EmbeddingBatcher(self.embedder, batch_size=batch_size)
        
        # Statistics
        self.stats = ProcessingStats()
        
        logger.info(
            f"DocumentProcessor initialized - Strategy: {self.chunking_strategy}, "
            f"Chunk size: {self.chunk_size}, Overlap: {self.chunk_overlap}"
        )
        
    def process_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = True,
        progress_callback: Optional[callable] = None
    ) -> Iterator[ProcessedDocument]:
        """Process all documents in a directory.
        
        Args:
            directory: Directory to process
            recursive: Whether to process subdirectories
            progress_callback: Optional callback for progress updates
            
        Yields:
            ProcessedDocument objects
        """
        directory = Path(directory)
        
        # Get list of files to process
        files = list(self.scanner.scan_directory(directory, recursive))
        self.stats.total_files = len(files)
        
        logger.info(f"Found {len(files)} files to process in {directory}")
        
        for i, file_path in enumerate(files):
            if progress_callback:
                progress_callback(
                    current=i,
                    total=len(files),
                    message=f"Processing {file_path.name}"
                )
                
            try:
                doc = self.process_file(file_path)
                self.stats.add_document(doc)
                yield doc
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                # Create failed document
                doc = self._create_failed_document(file_path, e)
                self.stats.add_document(doc)
                yield doc
                
        if progress_callback:
            progress_callback(
                current=len(files),
                total=len(files),
                message="Processing complete"
            )
            
    def process_files(
        self,
        file_paths: List[Union[str, Path]],
        progress_callback: Optional[callable] = None
    ) -> List[ProcessedDocument]:
        """Process a list of files.
        
        Args:
            file_paths: List of file paths to process
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of ProcessedDocument objects
        """
        file_paths = [Path(p) for p in file_paths]
        self.stats.total_files = len(file_paths)
        
        documents = []
        
        for i, file_path in enumerate(file_paths):
            if progress_callback:
                progress_callback(
                    current=i,
                    total=len(file_paths),
                    message=f"Processing {file_path.name}"
                )
                
            try:
                doc = self.process_file(file_path)
                self.stats.add_document(doc)
                documents.append(doc)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                doc = self._create_failed_document(file_path, e)
                self.stats.add_document(doc)
                documents.append(doc)
                
        if progress_callback:
            progress_callback(
                current=len(file_paths),
                total=len(file_paths),
                message="Processing complete"
            )
            
        return documents
        
    def process_file(self, file_path: Union[str, Path]) -> ProcessedDocument:
        """Process a single file through the pipeline.
        
        Args:
            file_path: Path to the file
            
        Returns:
            ProcessedDocument object
            
        Raises:
            DocumentProcessingError: If processing fails
        """
        file_path = Path(file_path)
        start_time = time.time()
        errors = []
        
        logger.info(f"Processing file: {file_path}")
        
        try:
            # Get metadata
            metadata = self.scanner.get_file_metadata(file_path)
            
            # Read document with OCR settings
            text = self.reader_factory.read_document(file_path, enable_ocr=self.enable_ocr, ocr_language=self.ocr_language)
            if not text:
                raise DocumentProcessingError(
                    "No text content extracted from document",
                    file_path=str(file_path)
                )
                
            # Update metadata with encoding if available
            if hasattr(self.reader_factory.get_reader(file_path), 'last_encoding'):
                metadata.encoding = self.reader_factory.get_reader(file_path).last_encoding
                
            # Chunk text
            chunks = self.chunker.chunk(
                text,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            
            if not chunks:
                raise DocumentProcessingError(
                    "No chunks created from document",
                    file_path=str(file_path)
                )
                
            # Update metadata
            metadata.chunk_count = len(chunks)
            
            # Add file reference to chunk metadata
            for chunk in chunks:
                chunk.metadata['source_file'] = str(file_path)
                chunk.metadata['file_type'] = metadata.file_type
                
            # Generate embeddings
            chunk_texts = [chunk.text for chunk in chunks]
            chunk_ids = [chunk.chunk_id for chunk in chunks]
            
            try:
                embeddings = self.batcher.process_with_progress(
                    chunk_texts,
                    chunk_ids
                )
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                errors.append(
                    ProcessingError(
                        error_type="EmbeddingError",
                        message=str(e),
                        file_path=str(file_path),
                        recoverable=True
                    )
                )
                embeddings = []
                
            processing_time = time.time() - start_time
            
            return ProcessedDocument(
                file_path=file_path,
                chunks=chunks,
                embeddings=embeddings,
                metadata=metadata,
                processing_time=processing_time,
                errors=errors
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Document processing failed for {file_path}: {e}")
            
            # Try to get whatever metadata we can
            try:
                metadata = self.scanner.get_file_metadata(file_path)
            except:
                metadata = None
                
            if metadata:
                return ProcessedDocument(
                    file_path=file_path,
                    chunks=[],
                    embeddings=[],
                    metadata=metadata,
                    processing_time=processing_time,
                    errors=[
                        ProcessingError(
                            error_type=type(e).__name__,
                            message=str(e),
                            file_path=str(file_path),
                            recoverable=False
                        )
                    ]
                )
            else:
                raise DocumentProcessingError(
                    f"Failed to process document: {e}",
                    file_path=str(file_path)
                )
                
    def _create_failed_document(
        self,
        file_path: Path,
        error: Exception
    ) -> ProcessedDocument:
        """Create a ProcessedDocument for a failed file.
        
        Args:
            file_path: Path to the file
            error: The exception that occurred
            
        Returns:
            ProcessedDocument with error information
        """
        try:
            metadata = self.scanner.get_file_metadata(file_path)
        except:
            # Create minimal metadata
            metadata = DocumentMetadata(
                filename=file_path.name,
                file_path=str(file_path),
                file_size=0,
                file_type=file_path.suffix,
                modified_time=datetime.now(),
                chunk_count=0,
                processing_date=datetime.now()
            )
            
        return ProcessedDocument(
            file_path=file_path,
            chunks=[],
            embeddings=[],
            metadata=metadata,
            processing_time=0.0,
            errors=[
                ProcessingError(
                    error_type=type(error).__name__,
                    message=str(error),
                    file_path=str(file_path),
                    recoverable=False
                )
            ]
        )
        
    def get_stats(self) -> ProcessingStats:
        """Get processing statistics.
        
        Returns:
            Current processing statistics
        """
        return self.stats
        
    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self.stats = ProcessingStats()


# Import datetime for the failed document creation
from datetime import datetime