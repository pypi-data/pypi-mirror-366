"""Integration tests for the complete system."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from src.vector_db_query.config import Config
from src.vector_db_query.services.document_processor import DocumentProcessor
from src.vector_db_query.services.vector_db import VectorDBService
from src.vector_db_query.services.embeddings import EmbeddingService
from src.vector_db_query.cli.interactive.app import InteractiveApp


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_document_processing_workflow(self, test_config, temp_dir):
        """Test complete document processing workflow."""
        # Create test documents
        doc1 = temp_dir / "doc1.txt"
        doc1.write_text("This is the first test document about Python programming.")
        
        doc2 = temp_dir / "doc2.md"
        doc2.write_text("# Markdown Document\n\nThis document discusses machine learning.")
        
        # Mock services
        with patch('src.vector_db_query.services.embeddings.GoogleGenerativeAIEmbeddings') as mock_embed_class:
            mock_embeddings = Mock()
            mock_embeddings.embed_documents.return_value = [[0.1] * 768, [0.2] * 768]
            mock_embeddings.embed_query.return_value = [0.15] * 768
            mock_embed_class.return_value = mock_embeddings
            
            with patch('qdrant_client.QdrantClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value = mock_client
                mock_client.get_collections.return_value = Mock(collections=[])
                mock_client.search.return_value = []
                
                # Initialize services
                embedding_service = EmbeddingService(test_config)
                doc_processor = DocumentProcessor(test_config)
                doc_processor.embedding_service = embedding_service
                
                vector_service = VectorDBService(test_config)
                await vector_service.initialize()
                
                # Process documents
                all_docs = []
                for doc_path in [doc1, doc2]:
                    docs = await doc_processor.process_file(doc_path)
                    all_docs.extend(docs)
                    
                    # Add to vector DB
                    for doc in docs:
                        await vector_service.add_document(doc)
                
                # Verify processing
                assert len(all_docs) > 0
                assert mock_client.upsert.called
                assert mock_embeddings.embed_documents.called
    
    @pytest.mark.asyncio
    async def test_search_workflow(self, test_config):
        """Test complete search workflow."""
        with patch('src.vector_db_query.services.embeddings.GoogleGenerativeAIEmbeddings') as mock_embed_class:
            mock_embeddings = Mock()
            mock_embeddings.embed_query.return_value = [0.3] * 768
            mock_embed_class.return_value = mock_embeddings
            
            with patch('qdrant_client.QdrantClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value = mock_client
                
                # Mock search results
                mock_client.search.return_value = [
                    Mock(
                        id="doc-1",
                        score=0.92,
                        payload={
                            "content": "Python is a great programming language",
                            "source": "doc1.txt",
                            "file_type": "txt",
                            "chunk_index": 0,
                            "total_chunks": 1,
                            "created_at": "2024-01-01"
                        }
                    )
                ]
                
                # Initialize services
                embedding_service = EmbeddingService(test_config)
                vector_service = VectorDBService(test_config)
                vector_service.client = mock_client
                vector_service.embedding_service = embedding_service
                
                # Perform search
                results = await vector_service.search(
                    query="Python programming",
                    limit=10
                )
                
                # Verify results
                assert len(results) == 1
                assert results[0].content == "Python is a great programming language"
                assert results[0].score == 0.92
                assert mock_embeddings.embed_query.called
                assert mock_client.search.called


class TestCLIIntegration:
    """Test CLI integration."""
    
    @pytest.mark.asyncio
    @patch('src.vector_db_query.cli.interactive.app.questionary')
    async def test_interactive_app_initialization(self, mock_questionary, test_config, temp_dir):
        """Test interactive app initialization."""
        # Setup config
        config_path = temp_dir / "config.yaml"
        test_config.save_yaml(config_path)
        
        # Mock user inputs
        mock_questionary.confirm.return_value.ask.return_value = False  # Skip onboarding
        
        with patch('qdrant_client.QdrantClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.get_collections.return_value = Mock(collections=[])
            
            # Create app
            app = InteractiveApp(config_path)
            
            # Initialize
            success = await app.initialize()
            assert success is True
            
            # Verify services initialized
            assert app.vector_service is not None
            assert app.doc_processor is not None
            assert app.config is not None
    
    @pytest.mark.asyncio
    async def test_mcp_server_integration(self, test_config):
        """Test MCP server integration."""
        # Enable MCP in config
        test_config.mcp_config.enabled = True
        
        with patch('src.vector_db_query.services.embeddings.GoogleGenerativeAIEmbeddings'):
            with patch('qdrant_client.QdrantClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value = mock_client
                mock_client.get_collections.return_value = Mock(collections=[])
                
                # Initialize services
                vector_service = VectorDBService(test_config)
                await vector_service.initialize()
                
                # Create MCP server
                from src.vector_db_query.mcp_integration.server import VectorQueryMCPServer
                mcp_server = VectorQueryMCPServer(vector_service, test_config.mcp_config)
                
                # Verify server creation
                assert mcp_server is not None
                assert mcp_server.vector_service == vector_service


class TestErrorHandling:
    """Test error handling across the system."""
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, test_config):
        """Test handling of connection errors."""
        with patch('qdrant_client.QdrantClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.get_collections.side_effect = Exception("Connection refused")
            
            vector_service = VectorDBService(test_config)
            
            with pytest.raises(Exception, match="Connection refused"):
                await vector_service.initialize()
    
    @pytest.mark.asyncio
    async def test_file_processing_error_handling(self, test_config, temp_dir):
        """Test handling of file processing errors."""
        # Create invalid file
        invalid_file = temp_dir / "invalid.bin"
        invalid_file.write_bytes(b"\x00\x01\x02\x03")
        
        with patch('src.vector_db_query.services.embeddings.GoogleGenerativeAIEmbeddings'):
            doc_processor = DocumentProcessor(test_config)
            
            # Should handle binary file gracefully
            with pytest.raises(ValueError):
                await doc_processor.process_file(invalid_file)
    
    @pytest.mark.asyncio
    async def test_embedding_service_error_handling(self, test_config):
        """Test handling of embedding service errors."""
        with patch('src.vector_db_query.services.embeddings.GoogleGenerativeAIEmbeddings') as mock_embed_class:
            mock_embeddings = Mock()
            mock_embeddings.embed_documents.side_effect = Exception("API quota exceeded")
            mock_embed_class.return_value = mock_embeddings
            
            embedding_service = EmbeddingService(test_config)
            
            with pytest.raises(Exception, match="API quota exceeded"):
                embedding_service.embed_text("Test text")


class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self, test_config, temp_dir):
        """Test batch processing performance."""
        # Create many small files
        files = []
        for i in range(50):
            file_path = temp_dir / f"file_{i}.txt"
            file_path.write_text(f"This is test file number {i}")
            files.append(file_path)
        
        with patch('src.vector_db_query.services.embeddings.GoogleGenerativeAIEmbeddings') as mock_embed_class:
            mock_embeddings = Mock()
            # Return embeddings for all files
            mock_embeddings.embed_documents.return_value = [[0.1] * 768] * 50
            mock_embed_class.return_value = mock_embeddings
            
            doc_processor = DocumentProcessor(test_config)
            doc_processor.embedding_service = EmbeddingService(test_config)
            
            # Process all files and measure time
            import time
            start_time = time.time()
            
            all_docs = []
            for file_path in files:
                docs = await doc_processor.process_file(file_path)
                all_docs.extend(docs)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should process 50 files reasonably quickly
            assert len(all_docs) == 50
            assert processing_time < 5.0  # Should take less than 5 seconds
    
    def test_caching_performance(self):
        """Test caching improves performance."""
        from src.vector_db_query.cli.interactive.optimization import cache_manager
        import time
        
        @cache_manager.cached("perf_test")
        def slow_operation(n):
            time.sleep(0.1)  # Simulate slow operation
            return n * n
        
        # First call (slow)
        start = time.time()
        result1 = slow_operation(5)
        first_call_time = time.time() - start
        
        # Second call (cached, fast)
        start = time.time()
        result2 = slow_operation(5)
        cached_call_time = time.time() - start
        
        assert result1 == result2 == 25
        assert cached_call_time < first_call_time / 10  # At least 10x faster