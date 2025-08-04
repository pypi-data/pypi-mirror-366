"""Base authentication classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
from pathlib import Path

from ..exceptions import AuthenticationError
from ...utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AuthToken:
    """Represents an authentication token."""
    access_token: str
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at
    
    @property
    def expires_in_seconds(self) -> Optional[int]:
        """Get seconds until expiration."""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'access_token': self.access_token,
            'token_type': self.token_type,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'refresh_token': self.refresh_token,
            'scope': self.scope
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthToken':
        """Create from dictionary."""
        expires_at = None
        if data.get('expires_at'):
            expires_at = datetime.fromisoformat(data['expires_at'])
        
        return cls(
            access_token=data['access_token'],
            token_type=data.get('token_type', 'Bearer'),
            expires_at=expires_at,
            refresh_token=data.get('refresh_token'),
            scope=data.get('scope')
        )


class AuthProvider(ABC):
    """Abstract base class for authentication providers."""
    
    @abstractmethod
    async def authenticate(self) -> AuthToken:
        """Perform authentication and return token."""
        pass
    
    @abstractmethod
    async def refresh(self, token: AuthToken) -> AuthToken:
        """Refresh an existing token."""
        pass
    
    @abstractmethod
    async def revoke(self, token: AuthToken) -> bool:
        """Revoke a token."""
        pass


class TokenStorage(ABC):
    """Abstract base class for token storage."""
    
    @abstractmethod
    async def store(self, key: str, token: AuthToken):
        """Store a token."""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[AuthToken]:
        """Retrieve a token."""
        pass
    
    @abstractmethod
    async def delete(self, key: str):
        """Delete a token."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if token exists."""
        pass


class FileTokenStorage(TokenStorage):
    """File-based token storage with encryption."""
    
    def __init__(self, storage_dir: Path, encryption_key: Optional[bytes] = None):
        """Initialize file storage.
        
        Args:
            storage_dir: Directory to store tokens
            encryption_key: Optional encryption key
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.encryption_key = encryption_key
        
        # Import encryption here to avoid circular imports
        if encryption_key:
            from .encryption import CredentialEncryption
            self.encryptor = CredentialEncryption(encryption_key)
        else:
            self.encryptor = None
    
    def _get_token_path(self, key: str) -> Path:
        """Get path for token file."""
        # Sanitize key for filename
        safe_key = key.replace('/', '_').replace('\\', '_')
        return self.storage_dir / f"{safe_key}.token"
    
    async def store(self, key: str, token: AuthToken):
        """Store a token to file."""
        token_path = self._get_token_path(key)
        data = json.dumps(token.to_dict())
        
        # Encrypt if encryptor available
        if self.encryptor:
            data = self.encryptor.encrypt(data)
        
        # Write to file
        token_path.write_text(data)
        logger.debug(f"Stored token for {key}")
    
    async def retrieve(self, key: str) -> Optional[AuthToken]:
        """Retrieve a token from file."""
        token_path = self._get_token_path(key)
        
        if not token_path.exists():
            return None
        
        try:
            data = token_path.read_text()
            
            # Decrypt if encryptor available
            if self.encryptor:
                data = self.encryptor.decrypt(data)
            
            token_dict = json.loads(data)
            return AuthToken.from_dict(token_dict)
            
        except Exception as e:
            logger.error(f"Failed to retrieve token for {key}: {e}")
            return None
    
    async def delete(self, key: str):
        """Delete a token file."""
        token_path = self._get_token_path(key)
        if token_path.exists():
            token_path.unlink()
            logger.debug(f"Deleted token for {key}")
    
    async def exists(self, key: str) -> bool:
        """Check if token file exists."""
        return self._get_token_path(key).exists()


class MemoryTokenStorage(TokenStorage):
    """In-memory token storage (for testing/development)."""
    
    def __init__(self):
        self.tokens: Dict[str, AuthToken] = {}
    
    async def store(self, key: str, token: AuthToken):
        """Store token in memory."""
        self.tokens[key] = token
    
    async def retrieve(self, key: str) -> Optional[AuthToken]:
        """Retrieve token from memory."""
        return self.tokens.get(key)
    
    async def delete(self, key: str):
        """Delete token from memory."""
        self.tokens.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        """Check if token exists in memory."""
        return key in self.tokens