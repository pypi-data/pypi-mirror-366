"""Custom exceptions for MCP integration."""

from typing import Optional, Dict, Any


class MCPError(Exception):
    """Base exception for MCP-related errors."""
    
    def __init__(self, message: str, code: str = "MCP_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class MCPAuthenticationError(MCPError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTH_FAILED", details)


class MCPConnectionError(MCPError):
    """Raised when connection to MCP server fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONNECTION_FAILED", details)


class MCPToolError(MCPError):
    """Raised when a tool execution fails."""
    
    def __init__(self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["tool"] = tool_name
        super().__init__(message, "TOOL_ERROR", details)


class MCPValidationError(MCPError):
    """Raised when request validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)


class MCPRateLimitError(MCPError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)


class MCPTimeoutError(MCPError):
    """Raised when operation times out."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(message, "TIMEOUT", details)


class MCPPermissionError(MCPError):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str, required_permission: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(message, "PERMISSION_DENIED", details)


class MCPResourceNotFoundError(MCPError):
    """Raised when requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details.update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, "RESOURCE_NOT_FOUND", details)


class MCPServerError(MCPError):
    """Raised for internal server errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SERVER_ERROR", details)


class MCPProtocolError(MCPError):
    """Raised when MCP protocol is violated."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "PROTOCOL_ERROR", details)


class MCPSecurityError(MCPError):
    """Raised when security violation is detected."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SECURITY_ERROR", details)