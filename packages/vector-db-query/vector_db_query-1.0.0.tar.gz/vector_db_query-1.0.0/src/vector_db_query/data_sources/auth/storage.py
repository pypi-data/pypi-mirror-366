"""Token storage for authentication credentials."""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import os

from cryptography.fernet import Fernet

from .models import AuthToken
from ..models import SourceType
from ...utils.logger import get_logger

logger = get_logger(__name__)


class TokenStorage:
    """Secure storage for authentication tokens."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize token storage.
        
        Args:
            storage_path: Path to store tokens (default: ~/.vector-db-query/tokens)
        """
        if storage_path is None:
            storage_path = Path.home() / ".vector-db-query" / "tokens"
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption key."""
        key_file = self.storage_path / ".key"
        
        if key_file.exists():
            # Load existing key
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Secure the key file
            os.chmod(key_file, 0o600)
        
        self.cipher = Fernet(key)
    
    async def store(self, source_type: SourceType, token: AuthToken):
        """Store token for a source.
        
        Args:
            source_type: Type of data source
            token: Authentication token
        """
        try:
            # Convert token to dict
            token_data = {
                'access_token': token.access_token,
                'refresh_token': token.refresh_token,
                'expires_at': token.expires_at.isoformat() if token.expires_at else None,
                'token_type': token.token_type,
                'scope': token.scope,
                'metadata': token.metadata
            }
            
            # Encrypt sensitive data
            encrypted_data = {
                'access_token': self._encrypt(token.access_token) if token.access_token else None,
                'refresh_token': self._encrypt(token.refresh_token) if token.refresh_token else None,
                'expires_at': token_data['expires_at'],
                'token_type': token_data['token_type'],
                'scope': token_data['scope'],
                'metadata': token_data['metadata']
            }
            
            # Save to file
            token_file = self.storage_path / f"{source_type.value}.json"
            with open(token_file, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            
            # Secure the token file
            os.chmod(token_file, 0o600)
            
            logger.info(f"Stored token for {source_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to store token: {e}")
            raise
    
    async def get(self, source_type: SourceType) -> Optional[AuthToken]:
        """Get stored token for a source.
        
        Args:
            source_type: Type of data source
            
        Returns:
            Authentication token or None
        """
        try:
            token_file = self.storage_path / f"{source_type.value}.json"
            
            if not token_file.exists():
                return None
            
            # Load encrypted data
            with open(token_file, 'r') as f:
                encrypted_data = json.load(f)
            
            # Decrypt and reconstruct token
            token = AuthToken(
                access_token=self._decrypt(encrypted_data['access_token']) if encrypted_data.get('access_token') else None,
                refresh_token=self._decrypt(encrypted_data['refresh_token']) if encrypted_data.get('refresh_token') else None,
                expires_at=datetime.fromisoformat(encrypted_data['expires_at']) if encrypted_data.get('expires_at') else None,
                token_type=encrypted_data.get('token_type', 'Bearer'),
                scope=encrypted_data.get('scope', ''),
                metadata=encrypted_data.get('metadata', {})
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to retrieve token: {e}")
            return None
    
    async def delete(self, source_type: SourceType):
        """Delete stored token for a source.
        
        Args:
            source_type: Type of data source
        """
        try:
            token_file = self.storage_path / f"{source_type.value}.json"
            
            if token_file.exists():
                token_file.unlink()
                logger.info(f"Deleted token for {source_type.value}")
                
        except Exception as e:
            logger.error(f"Failed to delete token: {e}")
    
    def _encrypt(self, data: str) -> str:
        """Encrypt string data.
        
        Args:
            data: String to encrypt
            
        Returns:
            Base64 encoded encrypted data
        """
        if not data:
            return ""
        
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string
        """
        if not encrypted_data:
            return ""
        
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    async def list_tokens(self) -> Dict[str, bool]:
        """List all stored tokens.
        
        Returns:
            Dict mapping source type to whether token exists
        """
        tokens = {}
        
        for source_type in SourceType:
            token_file = self.storage_path / f"{source_type.value}.json"
            tokens[source_type.value] = token_file.exists()
        
        return tokens