"""Tests for vector database functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from qdrant_client.models import Distance, VectorParams, PointStruct

from src.vector_db_query.services.vector_db import VectorDBService
from src.vector_db_query.models.documents import Document, DocumentMetadata


class TestVectorDBService:
    """Test vector database service functionality."""
    
    @pytest.mark.asyncio
    @patch('qdrant_client.QdrantClient')
    async def test_initialize(self, mock_client_class, test_config):
        """Test service initialization."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        service = VectorDBService(test_config)
        await service.initialize()
        
        # Check client creation
        mock_client_class.assert_called_once_with(
            host=test_config.qdrant_config.host,
            port=test_config.qdrant_config.port,
            api_key=test_config.qdrant_config.api_key,
            timeout=test_config.qdrant_config.timeout
        )
        
        # Check collection creation
        mock_client.create_collection.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('qdrant_client.QdrantClient')
    async def test_add_document(self, mock_client_class, test_config):
        """Test adding document to vector DB."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        service = VectorDBService(test_config)
        service.client = mock_client
        
        # Create test document
        doc = Document(
            id="test-123",
            content="Test content",
            embedding=[0.1] * 768,
            metadata=DocumentMetadata(
                source="test.txt",
                file_type="txt",
                chunk_index=0,
                total_chunks=1
            )
        )
        
        await service.add_document(doc)
        
        # Check upsert was called
        mock_client.upsert.assert_called_once()
        call_args = mock_client.upsert.call_args
        
        assert call_args[1]["collection_name"] == test_config.qdrant_config.collection_name
        assert len(call_args[1]["points"]) == 1
        assert call_args[1]["points"][0].id == "test-123"
    
    @pytest.mark.asyncio
    @patch('qdrant_client.QdrantClient')
    async def test_search(self, mock_client_class, test_config):
        """Test vector search."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock search results
        mock_results = [
            Mock(
                id="doc-1",
                score=0.95,
                payload={
                    "content": "Result 1",
                    "source": "file1.txt",
                    "file_type": "txt",
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "created_at": "2024-01-01T00:00:00"
                }
            ),
            Mock(
                id="doc-2",
                score=0.85,
                payload={
                    "content": "Result 2",
                    "source": "file2.txt",
                    "file_type": "txt",
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "created_at": "2024-01-01T00:00:00"
                }
            )
        ]
        mock_client.search.return_value = mock_results
        
        service = VectorDBService(test_config)
        service.client = mock_client
        
        # Perform search
        results = await service.search(
            query="test query",
            limit=10,
            score_threshold=0.7
        )
        
        assert len(results) == 2
        assert results[0].id == "doc-1"
        assert results[0].score == 0.95
        assert results[0].content == "Result 1"
        assert results[1].id == "doc-2"
        assert results[1].score == 0.85
    
    @pytest.mark.asyncio
    @patch('qdrant_client.QdrantClient')
    async def test_search_with_filters(self, mock_client_class, test_config):
        """Test search with metadata filters."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = []
        
        service = VectorDBService(test_config)
        service.client = mock_client
        
        # Search with filters
        await service.search(
            query="test",
            limit=10,
            filters={"file_type": "pdf"}
        )
        
        # Check filter was applied
        call_args = mock_client.search.call_args
        assert "query_filter" in call_args[1]
    
    @pytest.mark.asyncio
    @patch('qdrant_client.QdrantClient')
    async def test_delete_documents(self, mock_client_class, test_config):
        """Test deleting documents."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        service = VectorDBService(test_config)
        service.client = mock_client
        
        # Delete documents
        await service.delete_documents(["doc-1", "doc-2", "doc-3"])
        
        mock_client.delete.assert_called_once_with(
            collection_name=test_config.qdrant_config.collection_name,
            points_selector=["doc-1", "doc-2", "doc-3"]
        )
    
    @pytest.mark.asyncio
    @patch('qdrant_client.QdrantClient')
    async def test_get_statistics(self, mock_client_class, test_config):
        """Test getting collection statistics."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock collection info
        mock_client.get_collection.return_value = Mock(
            vectors_count=1000,
            points_count=1000,
            indexed_vectors_count=1000
        )
        
        service = VectorDBService(test_config)
        service.client = mock_client
        
        stats = await service.get_statistics()
        
        assert stats["vectors_count"] == 1000
        assert stats["indexed_vectors_count"] == 1000
    
    @pytest.mark.asyncio
    @patch('qdrant_client.QdrantClient')
    async def test_collection_exists(self, mock_client_class, test_config):
        """Test checking if collection exists."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock collections list
        mock_client.get_collections.return_value = Mock(
            collections=[
                Mock(name="test_documents"),
                Mock(name="other_collection")
            ]
        )
        
        service = VectorDBService(test_config)
        service.client = mock_client
        
        exists = await service.collection_exists()
        assert exists is True
        
        # Test non-existing collection
        mock_client.get_collections.return_value = Mock(collections=[])
        exists = await service.collection_exists()
        assert exists is False
    
    @pytest.mark.asyncio
    @patch('qdrant_client.QdrantClient')
    async def test_batch_add_documents(self, mock_client_class, test_config):
        """Test batch adding documents."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        service = VectorDBService(test_config)
        service.client = mock_client
        
        # Create test documents
        documents = []
        for i in range(150):  # More than batch size
            doc = Document(
                id=f"doc-{i}",
                content=f"Content {i}",
                embedding=[0.1] * 768,
                metadata=DocumentMetadata(
                    source=f"file{i}.txt",
                    file_type="txt",
                    chunk_index=0,
                    total_chunks=1
                )
            )
            documents.append(doc)
        
        await service.add_documents_batch(documents)
        
        # Should be called twice (100 + 50)
        assert mock_client.upsert.call_count == 2
    
    @pytest.mark.asyncio
    @patch('qdrant_client.QdrantClient')
    async def test_error_handling(self, mock_client_class, test_config):
        """Test error handling in vector operations."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock client to raise error
        mock_client.search.side_effect = Exception("Connection failed")
        
        service = VectorDBService(test_config)
        service.client = mock_client
        
        with pytest.raises(Exception, match="Connection failed"):
            await service.search("test query")