"""MCP server implementation for vector database queries."""

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
from ..vector_db.service import VectorDBService
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


class VectorQueryMCPServer:
    """MCP server for vector database queries."""
    
    def __init__(
        self,
        vector_service: VectorDBService,
        server_config: Optional[ServerConfig] = None,
        settings: Optional[MCPSettings] = None
    ):
        """Initialize MCP server.
        
        Args:
            vector_service: Vector database service instance
            server_config: Server configuration
            settings: Application settings
        """
        self.vector_service = vector_service
        self.config = server_config or ServerConfig()
        self.settings = settings or MCPSettings()
        
        # Initialize MCP server
        self.server = Server(
            name="vector-db-query",
            version="1.0.0",
            description="Query vector database for document retrieval"
        )
        
        # Server state
        self._running = False
        self._clients: Set[str] = set()
        self._shutdown_event = asyncio.Event()
        
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
        
        # Register tools
        self._register_tools()
        
        # Register resources
        self._register_resources()
        
        logger.info(f"MCP server initialized: {self.server.name} v{self.server.version}")
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, initiating shutdown...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _register_tools(self):
        """Register MCP tools."""
        # Query vectors tool
        @self.server.tool()
        async def query_vectors(
            query: str,
            limit: int = 10,
            threshold: Optional[float] = None,
            collection: Optional[str] = None,
            filters: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Search vector database for similar documents.
            
            Args:
                query: Search query text
                limit: Maximum number of results (1-100)
                threshold: Minimum similarity score (0.0-1.0)
                collection: Target collection name
                filters: Metadata filters
            
            Returns:
                Search results with relevant document chunks
            """
            # Generate request ID
            request_id = str(uuid.uuid4())
            client_id = "unknown"  # TODO: Get from auth context
            
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
                    "collection": collection
                }
            )
            
            try:
                # Validate and sanitize query
                query = self.security_validator.validate_query(query)
                
                # Validate collection name if provided
                if collection:
                    collection = self.security_validator.validate_collection_name(collection)
                
                # Validate filters if provided
                if filters:
                    filters = self.security_validator.validate_filters(filters)
                
                # Validate parameters
                limit = max(1, min(limit, 100))
                if threshold is not None:
                    threshold = max(0.0, min(threshold, 1.0))
                
                # Log query
                logger.info(f"Processing query: {query[:50]}... (limit={limit})")
                
                # Perform search
                results = await asyncio.to_thread(
                    self.vector_service.search_similar,
                    query_text=query,
                    limit=limit,
                    collection_name=collection
                )
                
                # Filter by threshold if specified
                if threshold is not None:
                    results = [r for r in results if r.score >= threshold]
                
                # Apply metadata filters if specified
                if filters:
                    results = self._apply_filters(results, filters)
                
                # Format response
                response = ToolResponse(
                    success=True,
                    data={
                        "results": [self._format_result(r) for r in results],
                        "query": query,
                        "total": len(results)
                    },
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "collection": collection or "default"
                    }
                )
                
                # Sanitize response
                sanitized_data = self.security_validator.sanitize_response(response.data)
                response.data = sanitized_data
                
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
        
        # Search similar tool
        @self.server.tool()
        async def search_similar(
            text: str,
            limit: int = 10,
            collection: Optional[str] = None,
            include_source: bool = True
        ) -> Dict[str, Any]:
            """Find documents similar to provided text.
            
            Args:
                text: Reference text to find similar documents
                limit: Maximum number of results (1-100)
                collection: Target collection name
                include_source: Include source information
            
            Returns:
                Similar documents with metadata
            """
            try:
                # Validate parameters
                limit = max(1, min(limit, 100))
                
                logger.info(f"Finding similar to: {text[:50]}... (limit={limit})")
                
                # Perform search
                results = await asyncio.to_thread(
                    self.vector_service.search_similar,
                    query_text=text,
                    limit=limit,
                    collection_name=collection
                )
                
                # Format response
                formatted_results = []
                for r in results:
                    result_data = {
                        "content": r.chunk.content[:self.config.max_context_tokens],
                        "score": r.score,
                        "metadata": r.chunk.metadata
                    }
                    
                    if include_source:
                        result_data["source"] = {
                            "file_name": Path(r.document.file_path).name,
                            "file_path": r.document.file_path,
                            "document_id": r.document.id
                        }
                    
                    formatted_results.append(result_data)
                
                response = ToolResponse(
                    success=True,
                    data={
                        "results": formatted_results,
                        "total": len(formatted_results)
                    },
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "collection": collection or "default"
                    }
                )
                
                return response.to_mcp_response()
                
            except Exception as e:
                logger.error(f"Error in search_similar: {str(e)}")
                return ToolResponse(
                    success=False,
                    error=str(e),
                    metadata={"tool": "search_similar"}
                ).to_mcp_response()
        
        # Get context tool
        @self.server.tool()
        async def get_context(
            document_id: str,
            chunk_id: str,
            context_size: int = 500
        ) -> Dict[str, Any]:
            """Get expanded context for a document chunk.
            
            Args:
                document_id: Document identifier
                chunk_id: Specific chunk ID
                context_size: Characters before/after chunk (100-2000)
            
            Returns:
                Expanded context with surrounding text
            """
            try:
                # Validate parameters
                context_size = max(100, min(context_size, 2000))
                
                logger.info(f"Getting context for chunk {chunk_id} in document {document_id}")
                
                # Get document and chunk
                document = await asyncio.to_thread(
                    self.vector_service.storage.get_document,
                    document_id
                )
                
                if not document:
                    raise MCPToolError("get_context", f"Document {document_id} not found")
                
                # Find the chunk
                chunk = None
                chunk_index = -1
                for idx, c in enumerate(document.chunks):
                    if c.id == chunk_id:
                        chunk = c
                        chunk_index = idx
                        break
                
                if not chunk:
                    raise MCPToolError("get_context", f"Chunk {chunk_id} not found")
                
                # Get before and after context
                before_context = ""
                after_context = ""
                
                # Before context
                if chunk_index > 0:
                    before_chunk = document.chunks[chunk_index - 1]
                    before_context = before_chunk.content[-context_size:]
                
                # After context
                if chunk_index < len(document.chunks) - 1:
                    after_chunk = document.chunks[chunk_index + 1]
                    after_context = after_chunk.content[:context_size]
                
                response = ToolResponse(
                    success=True,
                    data={
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "content": chunk.content,
                        "before_context": before_context,
                        "after_context": after_context,
                        "metadata": chunk.metadata
                    },
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "chunk_index": chunk_index,
                        "total_chunks": len(document.chunks)
                    }
                )
                
                return response.to_mcp_response()
                
            except Exception as e:
                logger.error(f"Error in get_context: {str(e)}")
                return ToolResponse(
                    success=False,
                    error=str(e),
                    metadata={"tool": "get_context"}
                ).to_mcp_response()
        
        logger.info("Registered 3 MCP tools: query_vectors, search_similar, get_context")
    
    def _register_resources(self):
        """Register MCP resources."""
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
        
        @self.server.resource("server/status")
        async def server_status() -> Dict[str, Any]:
            """Get server status information."""
            return {
                "status": "running" if self._running else "stopped",
                "version": self.server.version,
                "uptime": self._get_uptime(),
                "connected_clients": len(self._clients),
                "config": {
                    "max_connections": self.config.max_connections,
                    "auth_required": self.config.auth_required,
                    "cache_enabled": self.config.enable_caching
                }
            }
        
        @self.server.resource("server/metrics")
        async def server_metrics() -> Dict[str, Any]:
            """Get server metrics and statistics."""
            return self.mcp_logger.get_metrics_summary()
        
        logger.info("Registered 3 MCP resources: collections, server/status, server/metrics")
    
    def _format_result(self, result: Any) -> Dict[str, Any]:
        """Format search result for MCP response."""
        return {
            "chunk_id": result.chunk.id,
            "document_id": result.document.id,
            "score": result.score,
            "content": result.chunk.content[:self.config.max_context_tokens],
            "metadata": result.chunk.metadata,
            "source": {
                "file_name": Path(result.document.file_path).name,
                "file_path": result.document.file_path,
                "chunk_index": result.chunk.chunk_index,
                "total_chunks": result.document.total_chunks,
                "created_at": result.document.created_at.isoformat()
            }
        }
    
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
        
        return f"{hours}h {minutes}m {seconds}s"
    
    async def start(self):
        """Start the MCP server."""
        if self._running:
            logger.warning("Server is already running")
            return
        
        try:
            self._running = True
            self._start_time = datetime.now()
            
            logger.info(f"Starting MCP server on stdio...")
            
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
        
        logger.info("Stopping MCP server...")
        
        try:
            # Set shutdown event
            self._shutdown_event.set()
            
            # Close active connections
            logger.info(f"Closing {len(self._clients)} active connections")
            self._clients.clear()
            
            # Mark as stopped
            self._running = False
            
            logger.info("MCP server stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping server: {str(e)}")
            raise MCPServerError(f"Failed to stop server: {str(e)}")
    
    def handle_connection(self, client_id: str):
        """Handle new client connection."""
        self._clients.add(client_id)
        logger.info(f"Client connected: {client_id} (total: {len(self._clients)})")
        self.mcp_logger.log_connection_event("connected", client_id)
    
    def handle_disconnection(self, client_id: str):
        """Handle client disconnection."""
        self._clients.discard(client_id)
        logger.info(f"Client disconnected: {client_id} (remaining: {len(self._clients)})")
        self.mcp_logger.log_connection_event("disconnected", client_id)