"""Tests for document processing functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.vector_db_query.services.document_processor import (
    DocumentProcessor, Document, DocumentChunk
)
from src.vector_db_query.models.documents import DocumentMetadata


class TestDocumentProcessor:
    """Test document processor functionality."""
    
    @pytest.mark.asyncio
    async def test_process_text_file(self, test_config, mock_embedding_service, sample_files):
        """Test processing a text file."""
        processor = DocumentProcessor(test_config)
        processor.embedding_service = mock_embedding_service
        
        # Process text file
        documents = await processor.process_file(sample_files["txt"])
        
        assert isinstance(documents, list)
        assert all(isinstance(doc, Document) for doc in documents)
        
        # Check that embeddings were generated
        assert mock_embedding_service.embed_text.called
    
    @pytest.mark.asyncio
    async def test_process_markdown_file(self, test_config, mock_embedding_service, sample_files):
        """Test processing a markdown file."""
        processor = DocumentProcessor(test_config)
        processor.embedding_service = mock_embedding_service
        
        # Process markdown file
        documents = await processor.process_file(sample_files["md"])
        
        assert isinstance(documents, list)
        assert len(documents) > 0
        
        # Check metadata
        for doc in documents:
            assert doc.metadata.file_type == "md"
            assert doc.metadata.source == str(sample_files["md"])
    
    @pytest.mark.asyncio
    async def test_chunk_text(self, test_config, mock_embedding_service):
        """Test text chunking."""
        processor = DocumentProcessor(test_config)
        processor.embedding_service = mock_embedding_service
        
        # Create long text
        long_text = " ".join(["This is a test sentence."] * 200)
        
        chunks = processor._chunk_text(long_text)
        
        assert len(chunks) > 1  # Should create multiple chunks
        assert all(len(chunk) <= test_config.processing_config.chunk_size for chunk in chunks)
        
        # Check overlap
        for i in range(len(chunks) - 1):
            # There should be some overlap between consecutive chunks
            assert chunks[i][-50:] in chunks[i + 1]
    
    @pytest.mark.asyncio
    async def test_process_unsupported_file(self, test_config, mock_embedding_service, temp_dir):
        """Test processing unsupported file type."""
        processor = DocumentProcessor(test_config)
        processor.embedding_service = mock_embedding_service
        
        # Create unsupported file
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("Unsupported content")
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            await processor.process_file(unsupported_file)
    
    @pytest.mark.asyncio
    async def test_process_empty_file(self, test_config, mock_embedding_service, temp_dir):
        """Test processing empty file."""
        processor = DocumentProcessor(test_config)
        processor.embedding_service = mock_embedding_service
        
        # Create empty file
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")
        
        documents = await processor.process_file(empty_file)
        
        assert len(documents) == 0
    
    @pytest.mark.asyncio
    async def test_process_large_file(self, test_config, mock_embedding_service, temp_dir):
        """Test processing file exceeding size limit."""
        processor = DocumentProcessor(test_config)
        processor.embedding_service = mock_embedding_service
        
        # Create large file
        large_file = temp_dir / "large.txt"
        large_content = "x" * (test_config.processing_config.max_file_size + 1)
        large_file.write_text(large_content)
        
        with pytest.raises(ValueError, match="exceeds maximum size"):
            await processor.process_file(large_file)
    
    def test_create_document_chunk(self, test_config):
        """Test document chunk creation."""
        processor = DocumentProcessor(test_config)
        
        chunk = processor._create_chunk(
            content="Test content",
            metadata=DocumentMetadata(
                source="test.txt",
                file_type="txt",
                chunk_index=0,
                total_chunks=1
            ),
            chunk_index=0
        )
        
        assert isinstance(chunk, DocumentChunk)
        assert chunk.content == "Test content"
        assert chunk.metadata.chunk_index == 0
        assert chunk.metadata.source == "test.txt"
    
    @pytest.mark.asyncio
    async def test_batch_processing(self, test_config, mock_embedding_service, sample_files):
        """Test batch processing of multiple files."""
        processor = DocumentProcessor(test_config)
        processor.embedding_service = mock_embedding_service
        
        # Process multiple files
        all_documents = []
        for file in sample_files.values():
            if file.suffix in test_config.processing_config.file_extensions:
                docs = await processor.process_file(file)
                all_documents.extend(docs)
        
        assert len(all_documents) > 0
        assert all(isinstance(doc, Document) for doc in all_documents)
    
    @pytest.mark.asyncio
    @patch('src.vector_db_query.services.document_processor.extract_text_from_pdf')
    async def test_process_pdf_file(self, mock_pdf_extract, test_config, mock_embedding_service, temp_dir):
        """Test PDF file processing."""
        mock_pdf_extract.return_value = "Extracted PDF content"
        
        processor = DocumentProcessor(test_config)
        processor.embedding_service = mock_embedding_service
        
        # Create fake PDF file
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"fake pdf content")
        
        documents = await processor.process_file(pdf_file)
        
        assert len(documents) > 0
        assert mock_pdf_extract.called
        assert documents[0].metadata.file_type == "pdf"