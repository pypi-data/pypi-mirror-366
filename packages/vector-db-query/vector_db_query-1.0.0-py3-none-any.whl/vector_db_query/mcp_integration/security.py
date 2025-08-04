"""Security hardening for MCP server."""

import hashlib
import logging
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from .exceptions import MCPSecurityError, MCPValidationError


logger = logging.getLogger(__name__)


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    
    # Input validation
    max_query_length: int = 5000
    max_result_size: int = 1000000  # 1MB
    allowed_characters_pattern: str = r'^[\w\s\-.,!?\'\"()[\]{}:;/@#$%^&*+=<>|\\~`]+$'
    
    # Rate limiting
    max_requests_per_minute: int = 100
    max_requests_per_hour: int = 1000
    burst_limit: int = 20
    
    # Query restrictions
    forbidden_patterns: List[str] = None
    max_collection_name_length: int = 100
    
    # Result filtering
    sensitive_field_patterns: List[str] = None
    max_metadata_fields: int = 50
    
    # Timeout settings
    query_timeout_seconds: int = 30
    connection_timeout_seconds: int = 60
    
    def __post_init__(self):
        """Initialize default patterns."""
        if self.forbidden_patterns is None:
            self.forbidden_patterns = [
                r'(?i)(drop|delete|truncate|alter)\s+(table|database|collection)',
                r'(?i)(exec|execute|eval)\s*\(',
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'data:text/html',
            ]
        
        if self.sensitive_field_patterns is None:
            self.sensitive_field_patterns = [
                r'(?i)(password|passwd|pwd)',
                r'(?i)(secret|api_key|apikey)',
                r'(?i)(token|auth|authorization)',
                r'(?i)(ssn|social_security)',
                r'(?i)(credit_card|cc_number)',
            ]


class SecurityValidator:
    """Validates and sanitizes inputs for security."""
    
    def __init__(self, policy: Optional[SecurityPolicy] = None):
        """Initialize security validator.
        
        Args:
            policy: Security policy to use
        """
        self.policy = policy or SecurityPolicy()
        self._compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for efficiency."""
        return {
            "forbidden": [
                re.compile(pattern) for pattern in self.policy.forbidden_patterns
            ],
            "sensitive": [
                re.compile(pattern) for pattern in self.policy.sensitive_field_patterns
            ]
        }
    
    def validate_query(self, query: str) -> str:
        """Validate and sanitize a query string.
        
        Args:
            query: Query to validate
            
        Returns:
            Sanitized query
            
        Raises:
            MCPValidationError: If query is invalid
        """
        # Check length
        if len(query) > self.policy.max_query_length:
            raise MCPValidationError(
                f"Query too long: {len(query)} > {self.policy.max_query_length}",
                field="query"
            )
        
        # Check for empty query
        if not query or not query.strip():
            raise MCPValidationError("Query cannot be empty", field="query")
        
        # Check for forbidden patterns
        for pattern in self._compiled_patterns["forbidden"]:
            if pattern.search(query):
                raise MCPValidationError(
                    "Query contains forbidden pattern",
                    field="query",
                    details={"pattern": pattern.pattern}
                )
        
        # Check allowed characters
        if not re.match(self.policy.allowed_characters_pattern, query):
            raise MCPValidationError(
                "Query contains invalid characters",
                field="query"
            )
        
        # Sanitize whitespace
        sanitized = " ".join(query.split())
        
        return sanitized
    
    def validate_collection_name(self, name: str) -> str:
        """Validate collection name.
        
        Args:
            name: Collection name
            
        Returns:
            Validated name
            
        Raises:
            MCPValidationError: If name is invalid
        """
        if not name:
            raise MCPValidationError("Collection name cannot be empty")
        
        if len(name) > self.policy.max_collection_name_length:
            raise MCPValidationError(
                f"Collection name too long: {len(name)} > {self.policy.max_collection_name_length}"
            )
        
        # Allow only alphanumeric, underscore, and hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise MCPValidationError(
                "Collection name can only contain letters, numbers, underscore, and hyphen"
            )
        
        return name
    
    def validate_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata filters.
        
        Args:
            filters: Filters to validate
            
        Returns:
            Validated filters
            
        Raises:
            MCPValidationError: If filters are invalid
        """
        if not isinstance(filters, dict):
            raise MCPValidationError("Filters must be a dictionary")
        
        if len(filters) > self.policy.max_metadata_fields:
            raise MCPValidationError(
                f"Too many filter fields: {len(filters)} > {self.policy.max_metadata_fields}"
            )
        
        validated = {}
        
        for key, value in filters.items():
            # Validate key
            if not isinstance(key, str) or not key:
                raise MCPValidationError(f"Invalid filter key: {key}")
            
            if not re.match(r'^[a-zA-Z0-9_.-]+$', key):
                raise MCPValidationError(
                    f"Filter key contains invalid characters: {key}"
                )
            
            # Validate value (basic types only)
            if not isinstance(value, (str, int, float, bool, type(None))):
                raise MCPValidationError(
                    f"Invalid filter value type for {key}: {type(value).__name__}"
                )
            
            validated[key] = value
        
        return validated
    
    def sanitize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize response data.
        
        Args:
            response: Response to sanitize
            
        Returns:
            Sanitized response
        """
        # Check size
        response_str = str(response)
        if len(response_str) > self.policy.max_result_size:
            logger.warning(f"Response too large: {len(response_str)} bytes")
            # Truncate results
            if "results" in response and isinstance(response["results"], list):
                # Keep only first few results
                max_results = 10
                response["results"] = response["results"][:max_results]
                response["truncated"] = True
                response["original_count"] = len(response["results"])
        
        # Filter sensitive fields
        return self._filter_sensitive_fields(response)
    
    def _filter_sensitive_fields(self, data: Any) -> Any:
        """Recursively filter sensitive fields.
        
        Args:
            data: Data to filter
            
        Returns:
            Filtered data
        """
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                # Check if key matches sensitive pattern
                is_sensitive = any(
                    pattern.search(key)
                    for pattern in self._compiled_patterns["sensitive"]
                )
                
                if is_sensitive:
                    filtered[key] = "***REDACTED***"
                else:
                    filtered[key] = self._filter_sensitive_fields(value)
            
            return filtered
        
        elif isinstance(data, list):
            return [self._filter_sensitive_fields(item) for item in data]
        
        else:
            return data


class RateLimiter:
    """Rate limiting for MCP requests."""
    
    def __init__(self, policy: Optional[SecurityPolicy] = None):
        """Initialize rate limiter.
        
        Args:
            policy: Security policy
        """
        self.policy = policy or SecurityPolicy()
        self._request_history: Dict[str, List[float]] = {}
        self._burst_tokens: Dict[str, int] = {}
    
    def check_rate_limit(self, client_id: str) -> Tuple[bool, Optional[str]]:
        """Check if request is within rate limits.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Tuple of (allowed, reason)
        """
        current_time = datetime.now().timestamp()
        
        # Initialize client history if needed
        if client_id not in self._request_history:
            self._request_history[client_id] = []
            self._burst_tokens[client_id] = self.policy.burst_limit
        
        # Clean old requests
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        self._request_history[client_id] = [
            ts for ts in self._request_history[client_id]
            if ts > hour_ago
        ]
        
        # Count recent requests
        requests_last_minute = sum(
            1 for ts in self._request_history[client_id]
            if ts > minute_ago
        )
        
        requests_last_hour = len(self._request_history[client_id])
        
        # Check hourly limit
        if requests_last_hour >= self.policy.max_requests_per_hour:
            return False, f"Hourly limit exceeded: {requests_last_hour}/{self.policy.max_requests_per_hour}"
        
        # Check minute limit
        if requests_last_minute >= self.policy.max_requests_per_minute:
            return False, f"Minute limit exceeded: {requests_last_minute}/{self.policy.max_requests_per_minute}"
        
        # Check burst limit
        if self._burst_tokens[client_id] <= 0:
            # Regenerate tokens slowly
            time_since_last = current_time - self._request_history[client_id][-1]
            tokens_to_add = int(time_since_last / 3)  # 1 token per 3 seconds
            self._burst_tokens[client_id] = min(
                self.policy.burst_limit,
                self._burst_tokens[client_id] + tokens_to_add
            )
            
            if self._burst_tokens[client_id] <= 0:
                return False, "Burst limit exceeded, please slow down"
        
        # Request allowed
        self._request_history[client_id].append(current_time)
        self._burst_tokens[client_id] -= 1
        
        return True, None
    
    def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        """Get rate limit statistics for a client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Statistics dictionary
        """
        if client_id not in self._request_history:
            return {
                "requests_last_minute": 0,
                "requests_last_hour": 0,
                "burst_tokens": self.policy.burst_limit
            }
        
        current_time = datetime.now().timestamp()
        minute_ago = current_time - 60
        
        requests_last_minute = sum(
            1 for ts in self._request_history[client_id]
            if ts > minute_ago
        )
        
        return {
            "requests_last_minute": requests_last_minute,
            "requests_last_hour": len(self._request_history[client_id]),
            "burst_tokens": self._burst_tokens.get(client_id, 0)
        }


class InputSanitizer:
    """Sanitizes inputs to prevent injection attacks."""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize a string value.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            raise ValueError(f"Expected string, got {type(value)}")
        
        # Truncate if too long
        if len(value) > max_length:
            value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Escape control characters
        value = ''.join(
            char if char.isprintable() or char in '\n\r\t' else ''
            for char in value
        )
        
        return value.strip()
    
    @staticmethod
    def sanitize_path(path: str) -> str:
        """Sanitize a file path.
        
        Args:
            path: Path to sanitize
            
        Returns:
            Sanitized path
            
        Raises:
            ValueError: If path is invalid
        """
        # Remove null bytes
        path = path.replace('\x00', '')
        
        # Check for path traversal
        if '..' in path or path.startswith('/'):
            raise ValueError("Invalid path: potential traversal attack")
        
        # Remove multiple slashes
        path = re.sub(r'/+', '/', path)
        
        # Validate characters
        if not re.match(r'^[a-zA-Z0-9._/\-]+$', path):
            raise ValueError("Path contains invalid characters")
        
        return path
    
    @staticmethod
    def sanitize_json(data: Any, max_depth: int = 10) -> Any:
        """Sanitize JSON-like data structure.
        
        Args:
            data: Data to sanitize
            max_depth: Maximum nesting depth
            
        Returns:
            Sanitized data
        """
        def _sanitize(obj, depth=0):
            if depth > max_depth:
                raise ValueError("Maximum nesting depth exceeded")
            
            if isinstance(obj, dict):
                return {
                    InputSanitizer.sanitize_string(k, 100): _sanitize(v, depth + 1)
                    for k, v in obj.items()
                    if isinstance(k, str)
                }
            
            elif isinstance(obj, list):
                return [_sanitize(item, depth + 1) for item in obj]
            
            elif isinstance(obj, str):
                return InputSanitizer.sanitize_string(obj)
            
            elif isinstance(obj, (int, float, bool, type(None))):
                return obj
            
            else:
                # Convert to string and sanitize
                return InputSanitizer.sanitize_string(str(obj))
        
        return _sanitize(data)


def generate_request_id() -> str:
    """Generate a secure request ID.
    
    Returns:
        Request ID
    """
    return f"req_{secrets.token_urlsafe(16)}"


def hash_client_ip(ip_address: str) -> str:
    """Hash an IP address for privacy.
    
    Args:
        ip_address: IP to hash
        
    Returns:
        Hashed IP
    """
    return hashlib.sha256(ip_address.encode()).hexdigest()[:16]


def validate_jwt_claims(claims: Dict[str, Any]) -> bool:
    """Validate JWT token claims.
    
    Args:
        claims: JWT claims
        
    Returns:
        True if valid
    """
    # Check required claims
    required = ["client_id", "exp", "iat"]
    if not all(claim in claims for claim in required):
        return False
    
    # Check expiration
    if claims["exp"] < datetime.now().timestamp():
        return False
    
    # Check issued time
    if claims["iat"] > datetime.now().timestamp():
        return False  # Token from the future
    
    # Check token age
    token_age = datetime.now().timestamp() - claims["iat"]
    if token_age > 86400:  # 24 hours
        return False
    
    return True