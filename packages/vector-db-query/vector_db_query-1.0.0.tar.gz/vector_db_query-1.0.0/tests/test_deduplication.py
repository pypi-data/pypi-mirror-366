"""Tests for content deduplication system."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import json
import tempfile
import shutil

from vector_db_query.data_sources.deduplication import (
    ContentDeduplicator, DeduplicationResult, DuplicateEntry
)
from vector_db_query.data_sources.models import ProcessedDocument, SourceType


class TestContentDeduplicator:
    """Test content deduplication functionality."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def deduplicator(self, temp_cache_dir):
        """Create deduplicator instance."""
        return ContentDeduplicator(temp_cache_dir)
    
    @pytest.fixture
    def sample_document(self):
        """Create sample document."""
        return ProcessedDocument(
            id="doc_123",
            source_type=SourceType.GMAIL,
            source_id="gmail_123",
            title="Test Document",
            content="This is a test document with some content for deduplication testing.",
            processed_at=datetime.utcnow(),
            metadata={"sender": "test@example.com"}
        )
    
    def test_initialization(self, deduplicator, temp_cache_dir):
        """Test deduplicator initialization."""
        assert deduplicator.cache_dir == temp_cache_dir
        assert deduplicator.cache_dir.exists()
        assert (deduplicator.cache_dir / "hashes.db").exists()
        assert (deduplicator.cache_dir / "entries.json").exists()
    
    def test_content_hashing(self, deduplicator):
        """Test content hashing."""
        content1 = "This is test content"
        content2 = "This is test content"  # Same content
        content3 = "This is different content"
        
        hash1 = deduplicator._compute_content_hash(content1)
        hash2 = deduplicator._compute_content_hash(content2)
        hash3 = deduplicator._compute_content_hash(content3)
        
        assert hash1 == hash2  # Same content should have same hash
        assert hash1 != hash3  # Different content should have different hash
        assert len(hash1) == 64  # SHA-256 produces 64 character hex string
    
    def test_content_normalization(self, deduplicator):
        """Test content normalization."""
        # Test with extra whitespace
        content1 = "This   is    test\n\ncontent"
        content2 = "This is test content"
        
        normalized1 = deduplicator._normalize_content(content1)
        normalized2 = deduplicator._normalize_content(content2)
        
        assert normalized1 == normalized2
        
        # Test case insensitivity
        content3 = "THIS IS TEST CONTENT"
        normalized3 = deduplicator._normalize_content(content3)
        
        assert normalized2 == normalized3
    
    def test_similarity_calculation(self, deduplicator):
        """Test content similarity calculation."""
        # Identical content
        similarity = deduplicator._calculate_similarity(
            "This is test content",
            "This is test content"
        )
        assert similarity == 1.0
        
        # Completely different content
        similarity = deduplicator._calculate_similarity(
            "This is test content",
            "Completely different text here"
        )
        assert similarity < 0.5
        
        # Similar but not identical
        similarity = deduplicator._calculate_similarity(
            "This is test content for deduplication",
            "This is test content for testing"
        )
        assert 0.5 < similarity < 1.0
    
    def test_register_document(self, deduplicator, sample_document):
        """Test registering a document."""
        # Register document
        deduplicator.register_document(sample_document)
        
        # Verify entry exists
        entries = deduplicator._load_entries()
        assert len(entries) == 1
        
        entry = entries[0]
        assert entry['document_id'] == sample_document.id
        assert entry['source_type'] == sample_document.source_type.value
        assert entry['title'] == sample_document.title
        assert 'content_hash' in entry
        assert 'timestamp' in entry
    
    def test_exact_duplicate_detection(self, deduplicator, sample_document):
        """Test exact duplicate detection."""
        # Register original document
        deduplicator.register_document(sample_document)
        
        # Create exact duplicate
        duplicate_doc = ProcessedDocument(
            id="doc_456",
            source_type=SourceType.GMAIL,
            source_id="gmail_456",
            title="Test Document",  # Same title
            content=sample_document.content,  # Same content
            processed_at=datetime.utcnow()
        )
        
        # Check for duplicate
        result = deduplicator.check_duplicate(duplicate_doc)
        
        assert result.is_duplicate is True
        assert result.duplicate_of == sample_document.id
        assert result.similarity == 1.0
        assert result.match_type == "exact"
    
    def test_fuzzy_duplicate_detection(self, deduplicator, sample_document):
        """Test fuzzy duplicate detection."""
        # Register original document
        deduplicator.register_document(sample_document)
        
        # Create similar document
        similar_doc = ProcessedDocument(
            id="doc_789",
            source_type=SourceType.GMAIL,
            source_id="gmail_789",
            title="Test Document - Updated",
            content="This is a test document with some content for deduplication testing. Minor changes here.",
            processed_at=datetime.utcnow()
        )
        
        # Check for duplicate with lower threshold
        result = deduplicator.check_duplicate(similar_doc, threshold=0.8)
        
        assert result.is_duplicate is True
        assert result.duplicate_of == sample_document.id
        assert 0.8 < result.similarity < 1.0
        assert result.match_type == "fuzzy"
    
    def test_non_duplicate_detection(self, deduplicator, sample_document):
        """Test non-duplicate detection."""
        # Register original document
        deduplicator.register_document(sample_document)
        
        # Create different document
        different_doc = ProcessedDocument(
            id="doc_999",
            source_type=SourceType.FIREFLIES,
            source_id="fireflies_999",
            title="Completely Different Meeting",
            content="This is a meeting transcript about project planning and deadlines.",
            processed_at=datetime.utcnow()
        )
        
        # Check for duplicate
        result = deduplicator.check_duplicate(different_doc)
        
        assert result.is_duplicate is False
        assert result.duplicate_of is None
        assert result.similarity == 0.0
    
    def test_cross_source_deduplication(self, deduplicator):
        """Test deduplication across different sources."""
        # Create document from Gmail
        gmail_doc = ProcessedDocument(
            id="gmail_doc",
            source_type=SourceType.GMAIL,
            source_id="gmail_123",
            title="Meeting Notes",
            content="Discussion about Q1 planning and objectives",
            processed_at=datetime.utcnow()
        )
        
        # Create similar document from Google Drive
        drive_doc = ProcessedDocument(
            id="drive_doc",
            source_type=SourceType.GOOGLE_DRIVE,
            source_id="drive_123",
            title="Meeting Notes - Q1 Planning",
            content="Discussion about Q1 planning and objectives for the team",
            processed_at=datetime.utcnow()
        )
        
        # Register Gmail document
        deduplicator.register_document(gmail_doc)
        
        # Check Drive document for duplicates (cross-source enabled)
        result = deduplicator.check_duplicate(drive_doc, threshold=0.8)
        
        assert result.is_duplicate is True
        assert result.duplicate_of == gmail_doc.id
        assert result.duplicate_source == SourceType.GMAIL.value
    
    def test_source_specific_deduplication(self, deduplicator):
        """Test deduplication within same source only."""
        # Create documents from different sources with same content
        gmail_doc = ProcessedDocument(
            id="gmail_doc",
            source_type=SourceType.GMAIL,
            source_id="gmail_123",
            title="Test Content",
            content="This is test content",
            processed_at=datetime.utcnow()
        )
        
        fireflies_doc = ProcessedDocument(
            id="fireflies_doc",
            source_type=SourceType.FIREFLIES,
            source_id="fireflies_123",
            title="Test Content",
            content="This is test content",
            processed_at=datetime.utcnow()
        )
        
        # Register Gmail document
        deduplicator.register_document(gmail_doc)
        
        # Check Fireflies document with source-specific check
        result = deduplicator.check_duplicate(
            fireflies_doc,
            source_type=SourceType.FIREFLIES.value
        )
        
        assert result.is_duplicate is False  # Should not match across sources
    
    def test_get_statistics(self, deduplicator):
        """Test statistics retrieval."""
        # Register multiple documents
        docs = []
        for i in range(5):
            doc = ProcessedDocument(
                id=f"doc_{i}",
                source_type=SourceType.GMAIL,
                source_id=f"gmail_{i}",
                title=f"Document {i}",
                content=f"Content for document {i}",
                processed_at=datetime.utcnow()
            )
            docs.append(doc)
            deduplicator.register_document(doc)
        
        # Add some duplicates
        for i in range(2):
            dup_doc = ProcessedDocument(
                id=f"dup_{i}",
                source_type=SourceType.GMAIL,
                source_id=f"dup_gmail_{i}",
                title=f"Document {i}",  # Same as original
                content=f"Content for document {i}",  # Same as original
                processed_at=datetime.utcnow()
            )
            result = deduplicator.check_duplicate(dup_doc)
            assert result.is_duplicate
        
        # Get statistics
        stats = deduplicator.get_statistics()
        
        assert stats['total_documents'] == 5
        assert stats['unique_documents'] == 5
        assert stats['total_checks'] >= 2
        assert stats['duplicates_found'] >= 2
        assert stats['by_source']['gmail'] == 5
    
    def test_cleanup_old_entries(self, deduplicator):
        """Test cleanup of old entries."""
        # Create old and new documents
        old_doc = ProcessedDocument(
            id="old_doc",
            source_type=SourceType.GMAIL,
            source_id="old_gmail",
            title="Old Document",
            content="Old content",
            processed_at=datetime.utcnow() - timedelta(days=100)
        )
        
        new_doc = ProcessedDocument(
            id="new_doc",
            source_type=SourceType.GMAIL,
            source_id="new_gmail",
            title="New Document",
            content="New content",
            processed_at=datetime.utcnow()
        )
        
        # Register both documents
        deduplicator.register_document(old_doc)
        deduplicator.register_document(new_doc)
        
        # Manually set timestamp for old entry
        entries = deduplicator._load_entries()
        for entry in entries:
            if entry['document_id'] == 'old_doc':
                entry['timestamp'] = (datetime.utcnow() - timedelta(days=100)).isoformat()
        deduplicator._save_entries(entries)
        
        # Cleanup entries older than 90 days
        removed = deduplicator.cleanup_old_entries(90)
        
        assert removed == 1
        
        # Verify old entry is removed
        entries = deduplicator._load_entries()
        assert len(entries) == 1
        assert entries[0]['document_id'] == 'new_doc'
    
    def test_persistence(self, temp_cache_dir):
        """Test data persistence across instances."""
        # Create first deduplicator instance
        dedup1 = ContentDeduplicator(temp_cache_dir)
        
        # Register document
        doc = ProcessedDocument(
            id="persist_doc",
            source_type=SourceType.GMAIL,
            source_id="persist_gmail",
            title="Persistent Document",
            content="This should persist",
            processed_at=datetime.utcnow()
        )
        dedup1.register_document(doc)
        
        # Create second deduplicator instance
        dedup2 = ContentDeduplicator(temp_cache_dir)
        
        # Check if document is recognized as duplicate
        duplicate_doc = ProcessedDocument(
            id="dup_persist",
            source_type=SourceType.GMAIL,
            source_id="dup_persist_gmail",
            title="Persistent Document",
            content="This should persist",
            processed_at=datetime.utcnow()
        )
        
        result = dedup2.check_duplicate(duplicate_doc)
        assert result.is_duplicate is True
        assert result.duplicate_of == "persist_doc"
    
    def test_concurrent_access(self, deduplicator):
        """Test handling concurrent access (basic test)."""
        # Register multiple documents quickly
        docs = []
        for i in range(10):
            doc = ProcessedDocument(
                id=f"concurrent_{i}",
                source_type=SourceType.GMAIL,
                source_id=f"concurrent_gmail_{i}",
                title=f"Concurrent {i}",
                content=f"Concurrent content {i}",
                processed_at=datetime.utcnow()
            )
            docs.append(doc)
        
        # Register all documents
        for doc in docs:
            deduplicator.register_document(doc)
        
        # Verify all were registered
        entries = deduplicator._load_entries()
        assert len(entries) == 10
    
    def test_empty_content_handling(self, deduplicator):
        """Test handling of empty content."""
        # Document with empty content
        empty_doc = ProcessedDocument(
            id="empty_doc",
            source_type=SourceType.GMAIL,
            source_id="empty_gmail",
            title="Empty Document",
            content="",
            processed_at=datetime.utcnow()
        )
        
        # Should not crash
        deduplicator.register_document(empty_doc)
        
        # Check for duplicate with another empty document
        another_empty = ProcessedDocument(
            id="another_empty",
            source_type=SourceType.GMAIL,
            source_id="another_empty_gmail",
            title="Another Empty",
            content="",
            processed_at=datetime.utcnow()
        )
        
        result = deduplicator.check_duplicate(another_empty)
        assert result.is_duplicate is True


class TestDeduplicationResult:
    """Test DeduplicationResult model."""
    
    def test_result_creation(self):
        """Test creating deduplication result."""
        result = DeduplicationResult(
            is_duplicate=True,
            similarity=0.95,
            duplicate_of="doc_123",
            duplicate_source="gmail",
            match_type="fuzzy"
        )
        
        assert result.is_duplicate is True
        assert result.similarity == 0.95
        assert result.duplicate_of == "doc_123"
        assert result.duplicate_source == "gmail"
        assert result.match_type == "fuzzy"
    
    def test_non_duplicate_result(self):
        """Test non-duplicate result."""
        result = DeduplicationResult(
            is_duplicate=False,
            similarity=0.0
        )
        
        assert result.is_duplicate is False
        assert result.similarity == 0.0
        assert result.duplicate_of is None
        assert result.duplicate_source is None
        assert result.match_type == "none"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])