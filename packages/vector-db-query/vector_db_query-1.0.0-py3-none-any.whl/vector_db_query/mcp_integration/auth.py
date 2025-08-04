"""Authentication system for MCP server."""

import hashlib
import hmac
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set

import jwt
from jwt.exceptions import InvalidTokenError

from .exceptions import (
    MCPAuthenticationError,
    MCPPermissionError,
    MCPRateLimitError,
)
from .models import AuthToken


logger = logging.getLogger(__name__)


@dataclass
class ClientInfo:
    """Client information for authentication."""
    
    client_id: str
    client_secret_hash: str
    permissions: List[str] = field(default_factory=list)
    rate_limit: int = 100  # requests per minute
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_access: Optional[datetime] = None
    active_tokens: Set[str] = field(default_factory=set)


@dataclass
class RateLimitInfo:
    """Rate limiting information for a client."""
    
    requests: int = 0
    window_start: float = field(default_factory=time.time)
    
    def is_allowed(self, limit: int, window: int) -> bool:
        """Check if request is allowed under rate limit."""
        current_time = time.time()
        if current_time - self.window_start > window:
            # Reset window
            self.requests = 0
            self.window_start = current_time
        
        return self.requests < limit
    
    def increment(self):
        """Increment request count."""
        self.requests += 1


class MCPAuthenticator:
    """Handles authentication for MCP server."""
    
    def __init__(
        self,
        secret_key: str,
        token_expiry: int = 3600,
        algorithm: str = "HS256"
    ):
        """Initialize authenticator.
        
        Args:
            secret_key: Secret key for JWT signing
            token_expiry: Token expiry in seconds
            algorithm: JWT signing algorithm
        """
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self.algorithm = algorithm
        
        # Client registry
        self._clients: Dict[str, ClientInfo] = {}
        
        # Active tokens
        self._active_tokens: Dict[str, AuthToken] = {}
        
        # Revoked tokens
        self._revoked_tokens: Set[str] = set()
        
        # Rate limiting
        self._rate_limits: Dict[str, RateLimitInfo] = {}
        
        logger.info("MCP Authenticator initialized")
    
    def register_client(
        self,
        client_id: str,
        client_secret: str,
        permissions: Optional[List[str]] = None,
        rate_limit: int = 100
    ) -> ClientInfo:
        """Register a new client.
        
        Args:
            client_id: Unique client identifier
            client_secret: Client secret
            permissions: List of permissions
            rate_limit: Rate limit per minute
            
        Returns:
            ClientInfo object
        """
        if client_id in self._clients:
            raise ValueError(f"Client {client_id} already registered")
        
        # Hash the client secret
        secret_hash = self._hash_secret(client_secret)
        
        # Create client info
        client_info = ClientInfo(
            client_id=client_id,
            client_secret_hash=secret_hash,
            permissions=permissions or ["read"],
            rate_limit=rate_limit
        )
        
        self._clients[client_id] = client_info
        logger.info(f"Registered client: {client_id}")
        
        return client_info
    
    def authenticate_client(self, client_id: str, client_secret: str) -> bool:
        """Authenticate a client with credentials.
        
        Args:
            client_id: Client identifier
            client_secret: Client secret
            
        Returns:
            True if authentication successful
        """
        client = self._clients.get(client_id)
        if not client:
            logger.warning(f"Unknown client: {client_id}")
            return False
        
        # Verify secret
        secret_hash = self._hash_secret(client_secret)
        if not hmac.compare_digest(client.client_secret_hash, secret_hash):
            logger.warning(f"Invalid credentials for client: {client_id}")
            return False
        
        # Update last access
        client.last_access = datetime.now(timezone.utc)
        
        return True
    
    def generate_token(
        self,
        client_id: str,
        permissions: Optional[List[str]] = None,
        expiry_override: Optional[int] = None
    ) -> str:
        """Generate a JWT token for a client.
        
        Args:
            client_id: Client identifier
            permissions: Optional permission override
            expiry_override: Optional expiry override in seconds
            
        Returns:
            JWT token string
        """
        client = self._clients.get(client_id)
        if not client:
            raise MCPAuthenticationError(f"Unknown client: {client_id}")
        
        # Check rate limit
        if not self._check_rate_limit(client_id, client.rate_limit):
            raise MCPRateLimitError(
                f"Rate limit exceeded for client: {client_id}",
                retry_after=60
            )
        
        # Create token
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(seconds=expiry_override or self.token_expiry)
        
        # Token payload
        payload = {
            "client_id": client_id,
            "permissions": permissions or client.permissions,
            "iat": now.timestamp(),
            "exp": expiry.timestamp(),
            "jti": secrets.token_urlsafe(16)  # Unique token ID
        }
        
        # Generate token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Create AuthToken object
        auth_token = AuthToken(
            token=token,
            client_id=client_id,
            created_at=now,
            expires_at=expiry,
            permissions=permissions or client.permissions
        )
        
        # Store token
        self._active_tokens[token] = auth_token
        client.active_tokens.add(token)
        
        logger.info(f"Generated token for client: {client_id}")
        
        return token
    
    def validate_token(self, token: str) -> AuthToken:
        """Validate a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            AuthToken object
            
        Raises:
            MCPAuthenticationError: If token is invalid
        """
        # Check if revoked
        if token in self._revoked_tokens:
            raise MCPAuthenticationError("Token has been revoked")
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Get client
            client_id = payload.get("client_id")
            client = self._clients.get(client_id)
            if not client:
                raise MCPAuthenticationError(f"Unknown client in token: {client_id}")
            
            # Check if token is in active tokens
            if token not in self._active_tokens:
                # Recreate AuthToken from payload
                auth_token = AuthToken(
                    token=token,
                    client_id=client_id,
                    created_at=datetime.fromtimestamp(payload["iat"], timezone.utc),
                    expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc),
                    permissions=payload.get("permissions", [])
                )
                self._active_tokens[token] = auth_token
            else:
                auth_token = self._active_tokens[token]
            
            # Check expiry
            if auth_token.is_expired:
                self._cleanup_token(token)
                raise MCPAuthenticationError("Token has expired")
            
            # Update client last access
            client.last_access = datetime.now(timezone.utc)
            
            return auth_token
            
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise MCPAuthenticationError(f"Invalid token: {str(e)}")
    
    def revoke_token(self, token: str):
        """Revoke a token.
        
        Args:
            token: JWT token to revoke
        """
        self._revoked_tokens.add(token)
        self._cleanup_token(token)
        logger.info("Token revoked")
    
    def revoke_all_client_tokens(self, client_id: str):
        """Revoke all tokens for a client.
        
        Args:
            client_id: Client identifier
        """
        client = self._clients.get(client_id)
        if not client:
            return
        
        # Revoke all active tokens
        for token in list(client.active_tokens):
            self.revoke_token(token)
        
        logger.info(f"Revoked all tokens for client: {client_id}")
    
    def check_permission(self, auth_token: AuthToken, required_permission: str) -> bool:
        """Check if token has required permission.
        
        Args:
            auth_token: Authenticated token
            required_permission: Required permission
            
        Returns:
            True if permission granted
        """
        return auth_token.has_permission(required_permission)
    
    def require_permission(self, auth_token: AuthToken, required_permission: str):
        """Require a specific permission.
        
        Args:
            auth_token: Authenticated token
            required_permission: Required permission
            
        Raises:
            MCPPermissionError: If permission not granted
        """
        if not self.check_permission(auth_token, required_permission):
            raise MCPPermissionError(
                f"Permission denied: {required_permission}",
                required_permission=required_permission
            )
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from memory."""
        current_time = datetime.now(timezone.utc)
        expired_tokens = []
        
        for token, auth_token in self._active_tokens.items():
            if auth_token.expires_at < current_time:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            self._cleanup_token(token)
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
    
    def get_client_info(self, client_id: str) -> Optional[ClientInfo]:
        """Get client information.
        
        Args:
            client_id: Client identifier
            
        Returns:
            ClientInfo or None
        """
        return self._clients.get(client_id)
    
    def list_clients(self) -> List[str]:
        """List all registered client IDs."""
        return list(self._clients.keys())
    
    def _hash_secret(self, secret: str) -> str:
        """Hash a secret using SHA-256.
        
        Args:
            secret: Secret to hash
            
        Returns:
            Hashed secret
        """
        return hashlib.sha256(secret.encode()).hexdigest()
    
    def _check_rate_limit(self, client_id: str, limit: int) -> bool:
        """Check rate limit for a client.
        
        Args:
            client_id: Client identifier
            limit: Rate limit per minute
            
        Returns:
            True if request allowed
        """
        if client_id not in self._rate_limits:
            self._rate_limits[client_id] = RateLimitInfo()
        
        rate_info = self._rate_limits[client_id]
        
        if rate_info.is_allowed(limit, 60):  # 60 second window
            rate_info.increment()
            return True
        
        return False
    
    def _cleanup_token(self, token: str):
        """Clean up token from memory.
        
        Args:
            token: Token to clean up
        """
        # Remove from active tokens
        auth_token = self._active_tokens.pop(token, None)
        
        # Remove from client's active tokens
        if auth_token:
            client = self._clients.get(auth_token.client_id)
            if client:
                client.active_tokens.discard(token)
    
    def export_clients(self) -> Dict[str, Any]:
        """Export client configuration (without secrets).
        
        Returns:
            Client configuration dictionary
        """
        return {
            "clients": [
                {
                    "client_id": client.client_id,
                    "permissions": client.permissions,
                    "rate_limit": client.rate_limit,
                    "created_at": client.created_at.isoformat(),
                    "last_access": client.last_access.isoformat() if client.last_access else None
                }
                for client in self._clients.values()
            ]
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "MCPAuthenticator":
        """Create authenticator from configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            MCPAuthenticator instance
        """
        auth = cls(
            secret_key=config["jwt_secret"],
            token_expiry=config.get("token_expiry", 3600),
            algorithm=config.get("algorithm", "HS256")
        )
        
        # Register clients from config
        for client_config in config.get("clients", []):
            auth.register_client(
                client_id=client_config["client_id"],
                client_secret=client_config["client_secret"],
                permissions=client_config.get("permissions", ["read"]),
                rate_limit=client_config.get("rate_limit", 100)
            )
        
        return auth