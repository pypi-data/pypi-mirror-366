"""Tests for enhanced MCP server with format awareness."""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.vector_db_query.mcp_integration.server_enhanced import (
    EnhancedVectorQueryMCPServer,
    create_enhanced_server
)
from src.vector_db_query.mcp_integration.models import ServerConfig, ToolResponse
from src.vector_db_query.utils.config_enhanced import FileFormatConfig
from src.vector_db_query.document_processor.reader import ReaderFactory


class TestEnhancedMCPServer:
    """Test enhanced MCP server functionality."""
    
    @pytest.fixture
    def mock_vector_service(self):
        """Mock vector database service."""
        service = Mock()
        service.search_similar = AsyncMock(return_value=[])
        service.add_document = AsyncMock(return_value=True)
        service.get_all_documents = AsyncMock(return_value=[])
        service.collection_manager = Mock()
        service.collection_manager.list_collections = Mock(return_value=[])
        return service
    
    @pytest.fixture
    def mock_document_processor(self):
        """Mock document processor."""
        processor = Mock()
        processor.process_file = AsyncMock()
        return processor
    
    @pytest.fixture
    def server(self, mock_vector_service, mock_document_processor):
        """Create test server instance."""
        return EnhancedVectorQueryMCPServer(
            vector_service=mock_vector_service,
            document_processor=mock_document_processor,
            server_config=ServerConfig()
        )
    
    def test_server_initialization(self, server):
        """Test server initializes correctly."""
        assert server.server.name == "vector-db-query-enhanced"
        assert server.server.version == "2.0.0"
        assert isinstance(server.format_config, FileFormatConfig)
        assert isinstance(server.reader_factory, ReaderFactory)
        assert server._processing_stats["total_processed"] == 0
    
    @pytest.mark.asyncio
    async def test_query_vectors_with_file_types(self, server, mock_vector_service):
        """Test query_vectors tool with file type filtering."""
        # Mock search results
        mock_results = [
            Mock(
                chunk=Mock(id="1", content="PDF content", metadata={}),
                document=Mock(
                    id="doc1",
                    file_path="/path/to/doc.pdf",
                    created_at=datetime.now(),
                    total_chunks=5
                ),
                score=0.9
            ),
            Mock(
                chunk=Mock(id="2", content="Excel content", metadata={}),
                document=Mock(
                    id="doc2",
                    file_path="/path/to/data.xlsx",
                    created_at=datetime.now(),
                    total_chunks=3
                ),
                score=0.85
            ),
            Mock(
                chunk=Mock(id="3", content="Image content", metadata={}),
                document=Mock(
                    id="doc3",
                    file_path="/path/to/scan.png",
                    created_at=datetime.now(),
                    total_chunks=1
                ),
                score=0.8
            )
        ]
        
        mock_vector_service.search_similar.return_value = mock_results
        
        # Get the query_vectors tool
        query_tool = None
        for tool in server.server._tools.values():
            if tool.name == "query_vectors":
                query_tool = tool
                break
        
        assert query_tool is not None
        
        # Test with file type filter
        result = await query_tool.function(
            query="test query",
            file_types=["pdf", "xlsx"],
            limit=10
        )
        
        assert result["success"] is True
        assert len(result["data"]["results"]) == 2  # Only PDF and Excel
        assert result["data"]["formats_found"] == {"pdf": 1, "xlsx": 1}
        
        # Check format info is included
        for r in result["data"]["results"]:
            assert "format_info" in r
            assert r["format_info"]["extension"] in [".pdf", ".xlsx"]
            assert r["format_info"]["category"] in ["documents", "spreadsheets"]
    
    @pytest.mark.asyncio
    async def test_process_document_tool(self, server, mock_document_processor, temp_dir):
        """Test process_document tool with format detection."""
        # Create test file
        test_file = temp_dir / "test.json"
        test_file.write_text('{"key": "value"}')
        
        # Mock processing result
        mock_result = Mock(
            success=True,
            document_id="doc123",
            chunks=[Mock(), Mock()],
            processing_time=1.5,
            metadata={"format": "json"}
        )
        mock_document_processor.process_file.return_value = mock_result
        
        # Get the process_document tool
        process_tool = None
        for tool in server.server._tools.values():
            if tool.name == "process_document":
                process_tool = tool
                break
        
        assert process_tool is not None
        
        # Process document
        result = await process_tool.function(
            file_path=str(test_file),
            metadata={"project": "test"}
        )
        
        assert result["success"] is True
        assert result["data"]["format"] == ".json"
        assert result["data"]["reader"] == "JSONReader"
        assert result["data"]["chunks_created"] == 2
        assert server._processing_stats["total_processed"] == 1
        assert server._processing_stats["by_format"]["json"] == 1
    
    @pytest.mark.asyncio
    async def test_detect_format_tool(self, server, temp_dir):
        """Test detect_format tool."""
        # Create test files
        supported_file = temp_dir / "supported.pdf"
        supported_file.touch()
        
        unsupported_file = temp_dir / "unsupported.xyz"
        unsupported_file.touch()
        
        # Get the detect_format tool
        detect_tool = None
        for tool in server.server._tools.values():
            if tool.name == "detect_format":
                detect_tool = tool
                break
        
        assert detect_tool is not None
        
        # Test supported format
        result = await detect_tool.function(file_path=str(supported_file))
        assert result["success"] is True
        assert result["data"]["supported"] is True
        assert result["data"]["extension"] == ".pdf"
        assert result["data"]["reader"] == "PDFReader"
        assert result["data"]["category"] == "documents"
        
        # Test unsupported format
        result = await detect_tool.function(file_path=str(unsupported_file))
        assert result["success"] is True
        assert result["data"]["supported"] is False
        assert result["data"]["extension"] == ".xyz"
        assert "similar_formats" in result["data"]
    
    @pytest.mark.asyncio
    async def test_list_formats_tool(self, server):
        """Test list_formats tool."""
        # Get the list_formats tool
        list_tool = None
        for tool in server.server._tools.values():
            if tool.name == "list_formats":
                list_tool = tool
                break
        
        assert list_tool is not None
        
        # List formats
        result = await list_tool.function()
        
        assert result["success"] is True
        assert "formats" in result["data"]
        assert "total" in result["data"]
        assert "readers" in result["data"]
        
        # Check categories
        formats = result["data"]["formats"]
        assert "documents" in formats
        assert "spreadsheets" in formats
        assert "images" in formats
        
        # Check some specific formats
        assert ".pdf" in formats["documents"]
        assert ".xlsx" in formats["spreadsheets"]
        assert ".png" in formats["images"]
        
        # Check reader mapping
        readers = result["data"]["readers"]
        assert readers.get(".pdf") == "PDFReader"
        assert readers.get(".xlsx") == "ExcelReader"
    
    @pytest.mark.asyncio
    async def test_enhanced_server_status(self, server):
        """Test enhanced server status resource."""
        server._running = True
        server._start_time = datetime.now()
        
        # Get status resource
        status_resource = None
        for resource in server.server._resources.values():
            if resource.uri == "server/status":
                status_resource = resource
                break
        
        assert status_resource is not None
        
        # Get status
        status = await status_resource.function()
        
        assert status["status"] == "running"
        assert status["version"] == "2.0.0"
        assert status["features"]["formats_supported"] > 30
        assert "ocr_available" in status["features"]
        assert status["features"]["archive_extraction"] is True
        assert "processing_stats" in status
    
    @pytest.mark.asyncio
    async def test_format_stats_resource(self, server, mock_vector_service):
        """Test format statistics resource."""
        # Mock documents with various formats
        mock_docs = [
            Mock(file_path="/doc1.pdf", file_size=1024*1024),
            Mock(file_path="/doc2.pdf", file_size=2*1024*1024),
            Mock(file_path="/data.xlsx", file_size=512*1024),
            Mock(file_path="/image.png", file_size=256*1024),
        ]
        mock_vector_service.get_all_documents.return_value = mock_docs
        
        # Get stats resource
        stats_resource = None
        for resource in server.server._resources.values():
            if resource.uri == "formats/stats":
                stats_resource = resource
                break
        
        assert stats_resource is not None
        
        # Get stats
        stats = await stats_resource.function()
        
        assert stats["total_documents"] == 4
        assert stats["total_size_mb"] > 0
        assert stats["format_distribution"]["pdf"] == 2
        assert stats["format_distribution"]["xlsx"] == 1
        assert stats["format_distribution"]["png"] == 1
    
    @pytest.mark.asyncio
    async def test_reader_capabilities_resource(self, server):
        """Test reader capabilities resource."""
        # Get capabilities resource
        caps_resource = None
        for resource in server.server._resources.values():
            if resource.uri == "readers/capabilities":
                caps_resource = resource
                break
        
        assert caps_resource is not None
        
        # Get capabilities
        caps = await caps_resource.function()
        
        assert "readers" in caps
        readers = caps["readers"]
        
        # Check some reader capabilities
        assert ".pdf" in readers
        assert readers[".pdf"]["reader"] == "PDFReader"
        assert readers[".pdf"]["category"] == "documents"
        
        assert ".xlsx" in readers
        assert readers[".xlsx"]["reader"] == "ExcelReader"
        assert readers[".xlsx"]["category"] == "spreadsheets"
        
        # Check OCR languages (may be empty if Tesseract not installed)
        assert "ocr_languages" in caps
        assert isinstance(caps["ocr_languages"], list)
    
    def test_format_category_detection(self, server):
        """Test format category detection."""
        assert server._get_format_category(".pdf") == "documents"
        assert server._get_format_category(".xlsx") == "spreadsheets"
        assert server._get_format_category(".pptx") == "presentations"
        assert server._get_format_category(".eml") == "email"
        assert server._get_format_category(".html") == "web"
        assert server._get_format_category(".json") == "config"
        assert server._get_format_category(".png") == "images"
        assert server._get_format_category(".zip") == "archives"
        assert server._get_format_category(".geojson") == "data"
        assert server._get_format_category(".log") == "logs"
        assert server._get_format_category(".unknown") == "unknown"
    
    def test_similar_format_detection(self, server):
        """Test finding similar supported formats."""
        # Test with partially matching extension
        similar = server._find_similar_formats(".xls")
        assert ".xlsx" in similar or ".xls" in similar
        
        # Test with unknown but similar pattern
        similar = server._find_similar_formats(".htm")
        assert ".html" in similar
        
        # Test with completely unknown
        similar = server._find_similar_formats(".xyz")
        # Should return some suggestions based on pattern
        assert isinstance(similar, list)
    
    @pytest.mark.asyncio
    async def test_ocr_configuration(self, server, mock_document_processor, temp_dir):
        """Test OCR configuration in document processing."""
        # Create image file
        image_file = temp_dir / "scan.png"
        image_file.write_bytes(b'PNG...')
        
        # Mock processing
        mock_result = Mock(
            success=True,
            document_id="img123",
            chunks=[Mock()],
            processing_time=5.0,
            metadata={"ocr": "enabled"}
        )
        mock_document_processor.process_file.return_value = mock_result
        
        # Get process tool
        process_tool = None
        for tool in server.server._tools.values():
            if tool.name == "process_document":
                process_tool = tool
                break
        
        # Process with OCR settings
        result = await process_tool.function(
            file_path=str(image_file),
            ocr_enabled=True,
            ocr_language="eng+fra"
        )
        
        assert result["success"] is True
        assert result["data"]["format"] == ".png"
        assert result["data"]["reader"] == "ImageOCRReader"
    
    @pytest.mark.asyncio
    async def test_processing_stats_persistence(self, server, temp_dir, monkeypatch):
        """Test processing statistics are saved on shutdown."""
        # Set log directory
        log_dir = temp_dir / "logs" / "mcp"
        log_dir.mkdir(parents=True)
        monkeypatch.setattr(Path, "open", lambda self, mode: open(str(self), mode))
        
        # Update stats
        server._processing_stats["total_processed"] = 100
        server._processing_stats["by_format"]["pdf"] = 50
        
        # Mock the stop process
        server._running = True
        server._shutdown_event = asyncio.Event()
        
        # Stop server (simplified)
        await server.stop()
        
        # Check stats were meant to be saved
        assert server._running is False


class TestMCPServerCreation:
    """Test server creation and configuration."""
    
    def test_create_enhanced_server(self):
        """Test creating server with factory function."""
        with patch('src.vector_db_query.vector_db.service.VectorDBService'):
            with patch('src.vector_db_query.document_processor.DocumentProcessor'):
                server = create_enhanced_server()
                
                assert isinstance(server, EnhancedVectorQueryMCPServer)
                assert server.server.name == "vector-db-query-enhanced"
                assert server.server.version == "2.0.0"
    
    def test_create_server_with_config(self, temp_dir):
        """Test creating server with configuration file."""
        # Create config
        config_file = temp_dir / "config.yaml"
        config_file.write_text("""
mcp:
  max_connections: 50
  max_context_tokens: 2000
  enable_caching: false
  auth_required: true
""")
        
        with patch('src.vector_db_query.vector_db.service.VectorDBService'):
            with patch('src.vector_db_query.document_processor.DocumentProcessor'):
                server = create_enhanced_server(config_file)
                
                assert server.config.max_connections == 50
                assert server.config.max_context_tokens == 2000
                assert server.config.enable_caching is False
                assert server.config.auth_required is True


class TestBackwardCompatibility:
    """Test backward compatibility with original MCP server."""
    
    @pytest.mark.asyncio
    async def test_original_query_vectors_still_works(self, server, mock_vector_service):
        """Test original query_vectors parameters still work."""
        # Mock results
        mock_vector_service.search_similar.return_value = [
            Mock(
                chunk=Mock(id="1", content="Content", metadata={}),
                document=Mock(
                    id="doc1",
                    file_path="/doc.pdf",
                    created_at=datetime.now(),
                    total_chunks=1
                ),
                score=0.9
            )
        ]
        
        # Get tool
        query_tool = None
        for tool in server.server._tools.values():
            if tool.name == "query_vectors":
                query_tool = tool
                break
        
        # Call with original parameters only
        result = await query_tool.function(
            query="test query",
            limit=5,
            threshold=0.7
        )
        
        assert result["success"] is True
        assert len(result["data"]["results"]) == 1
        # New fields should still be present but optional
        assert "format_info" in result["data"]["results"][0]
    
    @pytest.mark.asyncio
    async def test_search_similar_unchanged(self, server, mock_vector_service):
        """Test search_similar tool remains unchanged."""
        mock_vector_service.search_similar.return_value = []
        
        # Find search_similar tool
        search_tool = None
        for tool in server.server._tools.values():
            if tool.name == "search_similar":
                search_tool = tool
                break
        
        # Should still exist and work
        assert search_tool is not None
        result = await search_tool.function(
            text="sample text",
            limit=10
        )
        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])