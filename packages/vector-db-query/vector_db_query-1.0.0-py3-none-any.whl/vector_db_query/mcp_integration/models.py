"""Data models for MCP integration."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


@dataclass
class ToolResponse:
    """Standard response format for MCP tools."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_mcp_response(self) -> Dict[str, Any]:
        """Convert to MCP protocol format."""
        response = {
            "success": self.success,
            "metadata": self.metadata
        }
        
        if self.success and self.data:
            response["data"] = self.data
        elif not self.success and self.error:
            response["error"] = {
                "message": self.error,
                "code": self.metadata.get("error_code", "UNKNOWN_ERROR")
            }
            
        return response


@dataclass
class MCPSearchResult:
    """Search result formatted for MCP response."""
    
    chunk_id: str
    document_id: str
    score: float
    content: str  # Truncated to fit context
    metadata: Dict[str, Any]
    source_info: "SourceInfo"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "score": self.score,
            "content": self.content,
            "metadata": self.metadata,
            "source": self.source_info.to_dict()
        }


@dataclass
class SourceInfo:
    """Source information for a search result."""
    
    file_name: str
    file_path: str
    chunk_index: int
    total_chunks: int
    created_at: str
    file_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_name": self.file_name,
            "file_path": self.file_path,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "created_at": self.created_at,
            "file_type": self.file_type
        }


@dataclass
class ExpandedContext:
    """Expanded context for a document chunk."""
    
    chunk_id: str
    document_id: str
    content: str
    before_context: str
    after_context: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "before_context": self.before_context,
            "after_context": self.after_context,
            "metadata": self.metadata
        }


@dataclass
class AuthToken:
    """Authentication token for MCP access."""
    
    token: str
    client_id: str
    created_at: datetime
    expires_at: datetime
    permissions: List[str] = field(default_factory=list)
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now() > self.expires_at
        
    def has_permission(self, permission: str) -> bool:
        """Check if token has specific permission."""
        return permission in self.permissions or "*" in self.permissions


class QueryVectorsRequest(BaseModel):
    """Request model for query-vectors tool."""
    
    query: str = Field(..., description="Search query text")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum similarity score")
    collection: Optional[str] = Field(None, description="Target collection name")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class SearchSimilarRequest(BaseModel):
    """Request model for search-similar tool."""
    
    text: str = Field(..., description="Reference text to find similar documents")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    collection: Optional[str] = Field(None, description="Target collection name")
    include_source: bool = Field(True, description="Include source information")


class GetContextRequest(BaseModel):
    """Request model for get-context tool."""
    
    document_id: str = Field(..., description="Document identifier")
    chunk_id: str = Field(..., description="Specific chunk ID")
    context_size: int = Field(500, ge=100, le=2000, description="Characters before/after chunk")


class ServerConfig(BaseModel):
    """Configuration for MCP server."""
    
    host: str = Field("localhost", description="Server host")
    port: int = Field(5000, description="Server port")
    max_connections: int = Field(10, description="Maximum concurrent connections")
    auth_required: bool = Field(True, description="Whether authentication is required")
    token_expiry: int = Field(3600, description="Token expiry in seconds")
    max_context_tokens: int = Field(100000, description="Maximum context tokens")
    enable_caching: bool = Field(True, description="Enable query result caching")
    cache_ttl: int = Field(300, description="Cache TTL in seconds")