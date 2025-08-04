"""MCP (Model Context Protocol) integration for vector database queries.

This module provides MCP server implementation for querying vector databases
from LLMs like Claude. It includes:

- MCP server with authentication
- Query tools for vector search
- Structured response formatting
- Context management for LLM interactions
"""

from .auth import MCPAuthenticator
from .config import MCPSettings, create_default_mcp_config
from .context import ContextManager, ContextWindow, TokenEstimate
from .exceptions import (
    MCPAuthenticationError,
    MCPConnectionError,
    MCPError,
    MCPPermissionError,
    MCPProtocolError,
    MCPRateLimitError,
    MCPResourceNotFoundError,
    MCPSecurityError,
    MCPServerError,
    MCPTimeoutError,
    MCPToolError,
    MCPValidationError,
)
from .formatter import FormattingConfig, ResponseFormatter
from .lifecycle import MCPServerManager, run_mcp_server
from .logging import MCPLogger, RequestMetrics, ServerMetrics
from .models import (
    AuthToken,
    ExpandedContext,
    GetContextRequest,
    MCPSearchResult,
    QueryVectorsRequest,
    SearchSimilarRequest,
    ServerConfig,
    SourceInfo,
    ToolResponse,
)
from .security import (
    InputSanitizer,
    RateLimiter,
    SecurityPolicy,
    SecurityValidator,
)
from .server import VectorQueryMCPServer
from .token_manager import TokenManager

__all__ = [
    # Server components
    "VectorQueryMCPServer",
    "MCPServerManager",
    "run_mcp_server",
    # Authentication
    "MCPAuthenticator",
    "TokenManager",
    # Configuration
    "MCPSettings",
    "create_default_mcp_config",
    # Formatting and Context
    "ResponseFormatter",
    "FormattingConfig",
    "ContextManager",
    "ContextWindow",
    "TokenEstimate",
    # Logging and Monitoring
    "MCPLogger",
    "RequestMetrics",
    "ServerMetrics",
    # Security
    "SecurityPolicy",
    "SecurityValidator",
    "RateLimiter",
    "InputSanitizer",
    # Models
    "ToolResponse",
    "MCPSearchResult",
    "SourceInfo",
    "ExpandedContext",
    "AuthToken",
    "QueryVectorsRequest",
    "SearchSimilarRequest",
    "GetContextRequest",
    "ServerConfig",
    # Exceptions
    "MCPError",
    "MCPAuthenticationError",
    "MCPConnectionError",
    "MCPToolError",
    "MCPValidationError",
    "MCPRateLimitError",
    "MCPTimeoutError",
    "MCPPermissionError",
    "MCPResourceNotFoundError",
    "MCPServerError",
    "MCPProtocolError",
    "MCPSecurityError",
]

__version__ = "1.0.0"