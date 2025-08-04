"""Enhanced MCP server with format awareness and processing capabilities."""

import asyncio
import json
import logging
import signal
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from mcp.server import Server
from mcp import Tool, Resource
from mcp.server import stdio

from ..utils.config import Config
from ..utils.config_enhanced import FileFormatConfig
from ..vector_db.service import VectorDBService
from ..document_processor.reader import ReaderFactory
from ..document_processor import DocumentProcessor
from .config import MCPSettings
from .exceptions import (
    MCPAuthenticationError,
    MCPConnectionError,
    MCPRateLimitError,
    MCPSecurityError,
    MCPServerError,
    MCPToolError,
)
from .logging import MCPLogger, RequestMetrics
from .models import ServerConfig, ToolResponse
from .security import SecurityValidator, RateLimiter, SecurityPolicy


logger = logging.getLogger(__name__)


class EnhancedVectorQueryMCPServer:
    """Enhanced MCP server with format awareness and document processing."""
    
    def __init__(
        self,
        vector_service: VectorDBService,
        document_processor: Optional[DocumentProcessor] = None,
        server_config: Optional[ServerConfig] = None,
        settings: Optional[MCPSettings] = None
    ):
        """Initialize enhanced MCP server.
        
        Args:
            vector_service: Vector database service instance
            document_processor: Document processor instance
            server_config: Server configuration
            settings: Application settings
        """
        self.vector_service = vector_service
        self.document_processor = document_processor or DocumentProcessor()
        self.config = server_config or ServerConfig()
        self.settings = settings or MCPSettings()
        
        # Initialize format configuration
        self.format_config = FileFormatConfig()
        self.reader_factory = ReaderFactory()
        
        # Initialize MCP server
        self.server = Server(
            name="vector-db-query-enhanced",
            version="2.0.0"
        )
        
        # Server state
        self._running = False
        self._clients: Set[str] = set()
        self._shutdown_event = asyncio.Event()
        self._processing_stats = {
            "total_processed": 0,
            "by_format": {},
            "errors": 0,
            "last_processed": None
        }
        
        # Initialize logger
        self.mcp_logger = MCPLogger(
            log_dir=Path("logs/mcp"),
            enable_audit=self.config.auth_required,
            enable_metrics=True
        )
        
        # Initialize security components
        self.security_policy = SecurityPolicy()
        self.security_validator = SecurityValidator(self.security_policy)
        self.rate_limiter = RateLimiter(self.security_policy)
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        # Register enhanced tools
        self._register_tools()
        
        # Register enhanced resources
        self._register_resources()
        
        logger.info(f"Enhanced MCP server initialized: {self.server.name} v{self.server.version}")
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, initiating shutdown...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _register_tools(self):
        """Register enhanced MCP tools with format awareness."""
        
        # Original query_vectors tool (preserved)
        @self.server.tool()
        async def query_vectors(
            query: str,
            limit: int = 10,
            threshold: Optional[float] = None,
            collection: Optional[str] = None,
            filters: Optional[Dict[str, Any]] = None,
            file_types: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Search vector database with optional format filtering.
            
            Args:
                query: Search query text
                limit: Maximum number of results (1-100)
                threshold: Minimum similarity score (0.0-1.0)
                collection: Target collection name
                filters: Metadata filters
                file_types: Filter by file types (e.g., ['pdf', 'docx'])
            
            Returns:
                Search results with document information
            """
            request_id = str(uuid.uuid4())
            client_id = "unknown"
            
            # Check rate limit
            allowed, reason = self.rate_limiter.check_rate_limit(client_id)
            if not allowed:
                raise MCPRateLimitError(reason, retry_after=60)
            
            # Log request
            metrics = self.mcp_logger.log_request(
                request_id=request_id,
                tool_name="query_vectors",
                client_id=client_id,
                parameters={
                    "query": query,
                    "limit": limit,
                    "threshold": threshold,
                    "collection": collection,
                    "file_types": file_types
                }
            )
            
            try:
                # Validate parameters
                query = self.security_validator.validate_query(query)
                limit = max(1, min(limit, 100))
                
                if threshold is not None:
                    threshold = max(0.0, min(threshold, 1.0))
                
                # Perform search
                results = await asyncio.to_thread(
                    self.vector_service.search_similar,
                    query_text=query,
                    limit=limit,
                    collection_name=collection
                )
                
                # Apply threshold filter
                if threshold is not None:
                    results = [r for r in results if r.score >= threshold]
                
                # Apply file type filter
                if file_types:
                    results = [
                        r for r in results
                        if Path(r.document.file_path).suffix[1:] in file_types
                    ]
                
                # Apply metadata filters
                if filters:
                    results = self._apply_filters(results, filters)
                
                # Format response with format info
                formatted_results = []
                for r in results:
                    result_data = self._format_result(r)
                    # Add format-specific info
                    file_ext = Path(r.document.file_path).suffix
                    result_data["format_info"] = {
                        "extension": file_ext,
                        "category": self._get_format_category(file_ext),
                        "reader": self._get_reader_name(file_ext)
                    }
                    formatted_results.append(result_data)
                
                response = ToolResponse(
                    success=True,
                    data={
                        "results": formatted_results,
                        "query": query,
                        "total": len(formatted_results),
                        "formats_found": self._count_formats(results)
                    },
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "collection": collection or "default"
                    }
                )
                
                # Log successful response
                token_count = sum(self.mcp_logger.metrics.estimate_tokens(str(r)) for r in results)
                self.mcp_logger.log_response(metrics, response.data, token_count)
                
                return response.to_mcp_response()
                
            except Exception as e:
                logger.error(f"Error in query_vectors: {str(e)}")
                self.mcp_logger.log_error(metrics, e)
                return ToolResponse(
                    success=False,
                    error=str(e),
                    metadata={"tool": "query_vectors", "request_id": request_id}
                ).to_mcp_response()
        
        # New tool: Process document with format awareness
        @self.server.tool()
        async def process_document(
            file_path: str,
            collection: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None,
            ocr_enabled: Optional[bool] = None,
            ocr_language: Optional[str] = None
        ) -> Dict[str, Any]:
            """Process and index a document with format detection.
            
            Args:
                file_path: Path to the document
                collection: Target collection name
                metadata: Additional metadata
                ocr_enabled: Enable OCR for images
                ocr_language: OCR language (e.g., 'eng', 'fra')
            
            Returns:
                Processing result with format information
            """
            request_id = str(uuid.uuid4())
            
            try:
                path = Path(file_path)
                if not path.exists():
                    raise MCPToolError("process_document", f"File not found: {file_path}")
                
                # Detect format
                extension = path.suffix.lower()
                if not self.format_config.is_supported(extension):
                    return ToolResponse(
                        success=False,
                        error=f"Unsupported format: {extension}",
                        data={
                            "supported_formats": list(self.format_config.all_supported)
                        }
                    ).to_mcp_response()
                
                # Get appropriate reader
                reader = self.reader_factory.get_reader(str(path))
                reader_name = reader.__class__.__name__
                
                # Configure OCR if applicable
                if hasattr(reader, 'ocr_enabled') and ocr_enabled is not None:
                    reader.ocr_enabled = ocr_enabled
                if hasattr(reader, 'language') and ocr_language:
                    reader.language = ocr_language
                
                logger.info(f"Processing {path.name} with {reader_name}")
                
                # Process document
                processed_doc = await self.document_processor.process_file(
                    file_path=str(path),
                    metadata=metadata,
                    collection_name=collection
                )
                
                # Update processing stats
                self._processing_stats["total_processed"] += 1
                format_key = extension[1:] if extension else "unknown"
                self._processing_stats["by_format"][format_key] = \
                    self._processing_stats["by_format"].get(format_key, 0) + 1
                self._processing_stats["last_processed"] = datetime.now().isoformat()
                
                # Store in vector database
                if processed_doc.success:
                    await self.vector_service.add_document(
                        processed_doc,
                        collection_name=collection
                    )
                
                response = ToolResponse(
                    success=processed_doc.success,
                    data={
                        "document_id": processed_doc.document_id,
                        "file_name": path.name,
                        "format": extension,
                        "reader": reader_name,
                        "chunks_created": len(processed_doc.chunks),
                        "processing_time": processed_doc.processing_time,
                        "metadata": processed_doc.metadata
                    },
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "request_id": request_id
                    }
                )
                
                return response.to_mcp_response()
                
            except Exception as e:
                logger.error(f"Error processing document: {str(e)}")
                self._processing_stats["errors"] += 1
                return ToolResponse(
                    success=False,
                    error=str(e),
                    metadata={"tool": "process_document", "request_id": request_id}
                ).to_mcp_response()
        
        # New tool: Detect file format
        @self.server.tool()
        async def detect_format(
            file_path: str
        ) -> Dict[str, Any]:
            """Detect if a file format is supported.
            
            Args:
                file_path: Path to check
            
            Returns:
                Format detection result
            """
            try:
                path = Path(file_path)
                extension = path.suffix.lower()
                
                is_supported = self.format_config.is_supported(extension)
                
                result = {
                    "file_name": path.name,
                    "extension": extension,
                    "supported": is_supported
                }
                
                if is_supported:
                    reader = self.reader_factory.get_reader(str(path))
                    result.update({
                        "reader": reader.__class__.__name__,
                        "category": self._get_format_category(extension),
                        "has_ocr": hasattr(reader, 'ocr_enabled')
                    })
                else:
                    # Find similar supported formats
                    similar = self._find_similar_formats(extension)
                    result["similar_formats"] = similar
                    result["reason"] = f"No reader available for {extension}"
                
                return ToolResponse(
                    success=True,
                    data=result
                ).to_mcp_response()
                
            except Exception as e:
                logger.error(f"Error detecting format: {str(e)}")
                return ToolResponse(
                    success=False,
                    error=str(e),
                    metadata={"tool": "detect_format"}
                ).to_mcp_response()
        
        # New tool: List supported formats
        @self.server.tool()
        async def list_formats() -> Dict[str, Any]:
            """List all supported file formats.
            
            Returns:
                Categorized list of supported formats
            """
            try:
                formats_by_category = {
                    "documents": list(self.format_config.documents),
                    "spreadsheets": list(self.format_config.spreadsheets),
                    "presentations": list(self.format_config.presentations),
                    "email": list(self.format_config.email),
                    "web": list(self.format_config.web),
                    "config": list(self.format_config.config),
                    "images": list(self.format_config.images),
                    "archives": list(self.format_config.archives),
                    "data": list(self.format_config.data),
                    "logs": list(self.format_config.logs),
                    "custom": list(self.format_config.custom_extensions)
                }
                
                # Add reader info
                reader_info = {}
                for ext in self.format_config.all_supported:
                    try:
                        reader = self.reader_factory.get_reader(f"test{ext}")
                        reader_info[ext] = reader.__class__.__name__
                    except:
                        reader_info[ext] = "Unknown"
                
                return ToolResponse(
                    success=True,
                    data={
                        "formats": formats_by_category,
                        "total": len(self.format_config.all_supported),
                        "readers": reader_info
                    }
                ).to_mcp_response()
                
            except Exception as e:
                logger.error(f"Error listing formats: {str(e)}")
                return ToolResponse(
                    success=False,
                    error=str(e),
                    metadata={"tool": "list_formats"}
                ).to_mcp_response()
        
        logger.info("Registered 6 enhanced MCP tools with format awareness")
    
    def _register_resources(self):
        """Register enhanced MCP resources."""
        
        # Original resources preserved
        @self.server.resource("collections")
        async def list_collections() -> Dict[str, Any]:
            """List available vector collections."""
            try:
                collections = await asyncio.to_thread(
                    self.vector_service.collection_manager.list_collections
                )
                
                return {
                    "collections": [
                        {
                            "name": col.name,
                            "vectors_count": col.vectors_count,
                            "status": col.status
                        }
                        for col in collections
                    ]
                }
            except Exception as e:
                logger.error(f"Error listing collections: {str(e)}")
                return {"error": str(e)}
        
        # Enhanced server status
        @self.server.resource("server/status")
        async def server_status() -> Dict[str, Any]:
            """Get enhanced server status."""
            return {
                "status": "running" if self._running else "stopped",
                "version": self.server.version,
                "features": {
                    "formats_supported": len(self.format_config.all_supported),
                    "ocr_available": self._check_ocr_available(),
                    "archive_extraction": True,
                    "config_parsing": True
                },
                "uptime": self._get_uptime(),
                "connected_clients": len(self._clients),
                "processing_stats": self._processing_stats
            }
        
        # Format statistics resource
        @self.server.resource("formats/stats")
        async def format_stats() -> Dict[str, Any]:
            """Get format processing statistics."""
            try:
                # Query database for format distribution
                all_docs = await asyncio.to_thread(
                    self.vector_service.get_all_documents
                )
                
                format_counts = {}
                total_size = 0
                
                for doc in all_docs:
                    ext = Path(doc.file_path).suffix[1:].lower()
                    format_counts[ext] = format_counts.get(ext, 0) + 1
                    if hasattr(doc, 'file_size'):
                        total_size += doc.file_size
                
                return {
                    "total_documents": len(all_docs),
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "format_distribution": format_counts,
                    "processing_history": self._processing_stats
                }
                
            except Exception as e:
                logger.error(f"Error getting format stats: {str(e)}")
                return {"error": str(e)}
        
        # Reader capabilities resource
        @self.server.resource("readers/capabilities")
        async def reader_capabilities() -> Dict[str, Any]:
            """Get detailed reader capabilities."""
            capabilities = {}
            
            for ext in self.format_config.all_supported:
                try:
                    reader = self.reader_factory.get_reader(f"test{ext}")
                    caps = {
                        "reader": reader.__class__.__name__,
                        "category": self._get_format_category(ext)
                    }
                    
                    # Check for special capabilities
                    if hasattr(reader, 'extract_tables'):
                        caps["can_extract_tables"] = True
                    if hasattr(reader, 'extract_images'):
                        caps["can_extract_images"] = True
                    if hasattr(reader, 'ocr_enabled'):
                        caps["supports_ocr"] = True
                    if hasattr(reader, 'stream_content'):
                        caps["supports_streaming"] = True
                    
                    capabilities[ext] = caps
                except:
                    capabilities[ext] = {"error": "Reader not available"}
            
            return {
                "readers": capabilities,
                "ocr_languages": self._get_available_ocr_languages()
            }
        
        logger.info("Registered 4 enhanced MCP resources with format statistics")
    
    def _format_result(self, result: Any) -> Dict[str, Any]:
        """Format search result with enhanced metadata."""
        base_result = {
            "chunk_id": result.chunk.id,
            "document_id": result.document.id,
            "score": result.score,
            "content": result.chunk.content[:self.config.max_context_tokens],
            "metadata": result.chunk.metadata,
            "source": {
                "file_name": Path(result.document.file_path).name,
                "file_path": result.document.file_path,
                "file_type": Path(result.document.file_path).suffix[1:],
                "chunk_index": result.chunk.chunk_index,
                "total_chunks": result.document.total_chunks,
                "created_at": result.document.created_at.isoformat()
            }
        }
        
        # Add file size if available
        if hasattr(result.document, 'file_size'):
            base_result["source"]["file_size"] = result.document.file_size
        
        return base_result
    
    def _get_format_category(self, extension: str) -> str:
        """Get category for a file extension."""
        ext = extension.lower()
        if not ext.startswith('.'):
            ext = f'.{ext}'
        
        if ext in self.format_config.documents:
            return "documents"
        elif ext in self.format_config.spreadsheets:
            return "spreadsheets"
        elif ext in self.format_config.presentations:
            return "presentations"
        elif ext in self.format_config.email:
            return "email"
        elif ext in self.format_config.web:
            return "web"
        elif ext in self.format_config.config:
            return "config"
        elif ext in self.format_config.images:
            return "images"
        elif ext in self.format_config.archives:
            return "archives"
        elif ext in self.format_config.data:
            return "data"
        elif ext in self.format_config.logs:
            return "logs"
        elif ext in self.format_config.custom_extensions:
            return "custom"
        else:
            return "unknown"
    
    def _get_reader_name(self, extension: str) -> str:
        """Get reader name for an extension."""
        try:
            reader = self.reader_factory.get_reader(f"test{extension}")
            return reader.__class__.__name__
        except:
            return "Unknown"
    
    def _count_formats(self, results: List[Any]) -> Dict[str, int]:
        """Count formats in search results."""
        format_counts = {}
        for r in results:
            ext = Path(r.document.file_path).suffix[1:].lower()
            format_counts[ext] = format_counts.get(ext, 0) + 1
        return format_counts
    
    def _find_similar_formats(self, extension: str) -> List[str]:
        """Find similar supported formats."""
        similar = []
        ext_lower = extension.lower().strip('.')
        
        for supported in self.format_config.all_supported:
            supported_lower = supported.strip('.').lower()
            # Check for partial matches or similar patterns
            if (ext_lower in supported_lower or 
                supported_lower in ext_lower or
                ext_lower[:3] == supported_lower[:3]):
                similar.append(supported)
        
        return similar[:5]  # Return top 5 similar
    
    def _check_ocr_available(self) -> bool:
        """Check if OCR is available."""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
    
    def _get_available_ocr_languages(self) -> List[str]:
        """Get available OCR languages."""
        try:
            import pytesseract
            langs = pytesseract.get_languages()
            return langs
        except:
            return []
    
    def _apply_filters(self, results: List[Any], filters: Dict[str, Any]) -> List[Any]:
        """Apply metadata filters to results."""
        filtered = []
        for result in results:
            match = True
            for key, value in filters.items():
                if key not in result.chunk.metadata:
                    match = False
                    break
                if result.chunk.metadata[key] != value:
                    match = False
                    break
            if match:
                filtered.append(result)
        return filtered
    
    def _get_uptime(self) -> str:
        """Get server uptime."""
        if not hasattr(self, "_start_time"):
            return "0s"
        
        uptime = datetime.now() - self._start_time
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if uptime.days > 0:
            return f"{uptime.days}d {hours}h {minutes}m"
        return f"{hours}h {minutes}m {seconds}s"
    
    async def start(self):
        """Start the enhanced MCP server."""
        if self._running:
            logger.warning("Server is already running")
            return
        
        try:
            self._running = True
            self._start_time = datetime.now()
            
            logger.info(f"Starting enhanced MCP server v{self.server.version}...")
            logger.info(f"Supported formats: {len(self.format_config.all_supported)}")
            
            # Run the server
            await self.server.run(
                read_stream=sys.stdin.buffer,
                write_stream=sys.stdout.buffer
            )
            
        except Exception as e:
            logger.error(f"Error starting server: {str(e)}")
            self._running = False
            raise MCPServerError(f"Failed to start server: {str(e)}")
    
    async def stop(self):
        """Stop the MCP server gracefully."""
        if not self._running:
            logger.warning("Server is not running")
            return
        
        logger.info("Stopping enhanced MCP server...")
        
        try:
            # Set shutdown event
            self._shutdown_event.set()
            
            # Close active connections
            logger.info(f"Closing {len(self._clients)} active connections")
            self._clients.clear()
            
            # Save statistics
            stats_file = Path("logs/mcp/processing_stats.json")
            stats_file.parent.mkdir(parents=True, exist_ok=True)
            with stats_file.open('w') as f:
                json.dump(self._processing_stats, f, indent=2)
            
            # Mark as stopped
            self._running = False
            
            logger.info("Enhanced MCP server stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping server: {str(e)}")
            raise MCPServerError(f"Failed to stop server: {str(e)}")


def create_enhanced_server(config_path: Optional[Path] = None) -> EnhancedVectorQueryMCPServer:
    """Create an enhanced MCP server instance."""
    # Load configuration
    if config_path:
        config = Config.from_yaml(config_path)
    else:
        config = Config()
    
    # Initialize services
    vector_service = VectorDBService(config)
    document_processor = DocumentProcessor(config)
    
    # Create server config
    server_config = ServerConfig(
        max_connections=config.get("mcp.max_connections", 100),
        max_context_tokens=config.get("mcp.max_context_tokens", 1000),
        enable_caching=config.get("mcp.enable_caching", True),
        auth_required=config.get("mcp.auth_required", False)
    )
    
    # Create MCP settings
    mcp_settings = MCPSettings()
    
    # Create and return server
    return EnhancedVectorQueryMCPServer(
        vector_service=vector_service,
        document_processor=document_processor,
        server_config=server_config,
        settings=mcp_settings
    )


if __name__ == "__main__":
    """Run the enhanced MCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Vector Query MCP Server")
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run server
    server = create_enhanced_server(args.config)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)