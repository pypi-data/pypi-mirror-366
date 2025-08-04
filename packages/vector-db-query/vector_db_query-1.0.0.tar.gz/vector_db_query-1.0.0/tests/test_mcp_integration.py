"""Tests for MCP (Model Context Protocol) integration."""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch

from src.vector_db_query.mcp_integration.server import VectorQueryMCPServer
from src.vector_db_query.mcp_integration.handlers import (
    SearchHandler, ProcessDocumentHandler, StatusHandler,
    ListDocumentsHandler, GetDocumentHandler
)
from src.vector_db_query.config import MCPConfig


class TestMCPServer:
    """Test MCP server functionality."""
    
    def test_server_initialization(self, mock_vector_service):
        """Test MCP server initialization."""
        config = MCPConfig(enabled=True, port=8080)
        server = VectorQueryMCPServer(mock_vector_service, config)
        
        assert server.vector_service == mock_vector_service
        assert server.config == config
        assert len(server.handlers) > 0
    
    def test_handler_registration(self, mock_vector_service):
        """Test handler registration."""
        config = MCPConfig(enabled=True)
        server = VectorQueryMCPServer(mock_vector_service, config)
        
        # Check handlers are registered
        handler_types = [type(h) for h in server.handlers.values()]
        assert SearchHandler in handler_types
        assert ProcessDocumentHandler in handler_types
        assert StatusHandler in handler_types
    
    @pytest.mark.asyncio
    async def test_handle_request(self, mock_vector_service):
        """Test request handling."""
        config = MCPConfig(enabled=True)
        server = VectorQueryMCPServer(mock_vector_service, config)
        
        # Create test request
        request = {
            "method": "vector_db.search",
            "params": {
                "query": "test query",
                "limit": 5
            }
        }
        
        # Mock search results
        mock_vector_service.search.return_value = []
        
        response = await server.handle_request(request)
        
        assert "result" in response
        assert response["result"]["success"] is True
        mock_vector_service.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_vector_service):
        """Test error handling in request processing."""
        config = MCPConfig(enabled=True)
        server = VectorQueryMCPServer(mock_vector_service, config)
        
        # Invalid request
        request = {
            "method": "invalid.method",
            "params": {}
        }
        
        response = await server.handle_request(request)
        
        assert "error" in response
        assert response["error"]["code"] == -32601  # Method not found


class TestSearchHandler:
    """Test search handler functionality."""
    
    @pytest.mark.asyncio
    async def test_search_handler(self, mock_vector_service):
        """Test search request handling."""
        handler = SearchHandler(mock_vector_service)
        
        # Mock search results
        from src.vector_db_query.models.documents import Document, DocumentMetadata
        mock_results = [
            Document(
                id="1",
                content="Test result",
                embedding=[0.1] * 768,
                metadata=DocumentMetadata(
                    source="test.txt",
                    file_type="txt",
                    chunk_index=0,
                    total_chunks=1
                )
            )
        ]
        mock_vector_service.search.return_value = mock_results
        
        # Handle request
        params = {
            "query": "test query",
            "limit": 10,
            "score_threshold": 0.7
        }
        
        result = await handler.handle(params)
        
        assert result["success"] is True
        assert len(result["results"]) == 1
        assert result["results"][0]["content"] == "Test result"
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, mock_vector_service):
        """Test search with metadata filters."""
        handler = SearchHandler(mock_vector_service)
        mock_vector_service.search.return_value = []
        
        params = {
            "query": "test",
            "filters": {"file_type": "pdf"},
            "limit": 5
        }
        
        result = await handler.handle(params)
        
        assert result["success"] is True
        
        # Verify filters were passed
        call_args = mock_vector_service.search.call_args
        assert call_args[1]["filters"] == {"file_type": "pdf"}


class TestProcessDocumentHandler:
    """Test document processing handler."""
    
    @pytest.mark.asyncio
    async def test_process_text_document(self, mock_vector_service):
        """Test processing text document."""
        handler = ProcessDocumentHandler(mock_vector_service)
        
        # Mock document processor
        with patch('src.vector_db_query.mcp_integration.handlers.DocumentProcessor') as mock_proc_class:
            mock_processor = AsyncMock()
            mock_proc_class.return_value = mock_processor
            
            from src.vector_db_query.models.documents import Document, DocumentMetadata
            mock_docs = [
                Document(
                    id="1",
                    content="Processed content",
                    embedding=[0.1] * 768,
                    metadata=DocumentMetadata(
                        source="inline",
                        file_type="txt",
                        chunk_index=0,
                        total_chunks=1
                    )
                )
            ]
            mock_processor.process_text.return_value = mock_docs
            
            params = {
                "content": "Test document content",
                "metadata": {"title": "Test Doc"}
            }
            
            result = await handler.handle(params)
            
            assert result["success"] is True
            assert result["documents_processed"] == 1
            mock_vector_service.add_document.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_file_path(self, mock_vector_service, temp_dir):
        """Test processing file by path."""
        handler = ProcessDocumentHandler(mock_vector_service)
        
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("File content")
        
        with patch('src.vector_db_query.mcp_integration.handlers.DocumentProcessor') as mock_proc_class:
            mock_processor = AsyncMock()
            mock_proc_class.return_value = mock_processor
            mock_processor.process_file.return_value = []
            
            params = {
                "file_path": str(test_file)
            }
            
            result = await handler.handle(params)
            
            assert result["success"] is True
            mock_processor.process_file.assert_called_once()


class TestStatusHandler:
    """Test status handler."""
    
    @pytest.mark.asyncio
    async def test_status_handler(self, mock_vector_service):
        """Test status request handling."""
        handler = StatusHandler(mock_vector_service)
        
        # Mock statistics
        mock_vector_service.get_statistics.return_value = {
            "vectors_count": 1000,
            "collections_count": 1
        }
        
        mock_vector_service.get_collection_info.return_value = {
            "name": "test_collection",
            "vector_size": 768
        }
        
        result = await handler.handle({})
        
        assert result["success"] is True
        assert result["statistics"]["vectors_count"] == 1000
        assert result["collection_info"]["vector_size"] == 768


class TestListDocumentsHandler:
    """Test list documents handler."""
    
    @pytest.mark.asyncio
    async def test_list_documents(self, mock_vector_service):
        """Test listing documents."""
        handler = ListDocumentsHandler(mock_vector_service)
        
        # For now, this returns empty since we don't have a list method
        result = await handler.handle({"limit": 10})
        
        assert result["success"] is True
        assert "documents" in result


class TestMCPSecurity:
    """Test MCP security features."""
    
    def test_auth_required(self, mock_vector_service):
        """Test authentication requirement."""
        config = MCPConfig(
            enabled=True,
            auth_required=True,
            auth_token="secret-token"
        )
        server = VectorQueryMCPServer(mock_vector_service, config)
        
        # Request without auth
        request = {
            "method": "vector_db.search",
            "params": {"query": "test"}
        }
        
        # Should check auth
        assert server.config.auth_required is True
        assert server.config.auth_token == "secret-token"
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, mock_vector_service):
        """Test rate limiting configuration."""
        config = MCPConfig(
            enabled=True,
            rate_limit=10,  # 10 requests per minute
            rate_limit_window=60
        )
        server = VectorQueryMCPServer(mock_vector_service, config)
        
        # Rate limiting should be configured
        assert server.config.rate_limit == 10
        assert server.config.rate_limit_window == 60


class TestMCPIntegrationFlow:
    """Test complete MCP integration flows."""
    
    @pytest.mark.asyncio
    async def test_complete_mcp_workflow(self, mock_vector_service, temp_dir):
        """Test complete MCP workflow: process and search."""
        config = MCPConfig(enabled=True)
        server = VectorQueryMCPServer(mock_vector_service, config)
        
        # Step 1: Process document
        process_request = {
            "method": "vector_db.process_document",
            "params": {
                "content": "This is a test document about Python programming.",
                "metadata": {"source": "mcp_test"}
            }
        }
        
        with patch('src.vector_db_query.mcp_integration.handlers.DocumentProcessor') as mock_proc_class:
            mock_processor = AsyncMock()
            mock_proc_class.return_value = mock_processor
            mock_processor.process_text.return_value = [Mock()]
            
            process_response = await server.handle_request(process_request)
            assert process_response["result"]["success"] is True
        
        # Step 2: Search for document
        search_request = {
            "method": "vector_db.search",
            "params": {
                "query": "Python programming",
                "limit": 5
            }
        }
        
        mock_vector_service.search.return_value = [
            Mock(
                id="1",
                content="This is a test document about Python programming.",
                score=0.95,
                metadata={"source": "mcp_test"}
            )
        ]
        
        search_response = await server.handle_request(search_request)
        assert search_response["result"]["success"] is True
        assert len(search_response["result"]["results"]) == 1
        assert search_response["result"]["results"][0]["score"] == 0.95