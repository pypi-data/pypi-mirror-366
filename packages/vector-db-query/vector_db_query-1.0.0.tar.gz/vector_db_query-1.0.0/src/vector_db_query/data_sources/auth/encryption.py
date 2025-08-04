"""Credential encryption utilities."""

import base64
import os
from typing import Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ...utils.logger import get_logger

logger = get_logger(__name__)


class CredentialEncryption:
    """Handles encryption and decryption of credentials."""
    
    def __init__(self, key: Union[str, bytes] = None):
        """Initialize encryptor with key.
        
        Args:
            key: Encryption key (string or bytes). If None, generates new key.
        """
        if key is None:
            self.key = Fernet.generate_key()
        elif isinstance(key, str):
            self.key = self._derive_key(key.encode())
        else:
            self.key = key
        
        self.cipher = Fernet(self.key)
    
    @staticmethod
    def _derive_key(password: bytes, salt: bytes = None) -> bytes:
        """Derive encryption key from password.
        
        Args:
            password: Password bytes
            salt: Salt bytes (generated if not provided)
            
        Returns:
            Derived key suitable for Fernet
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """Encrypt data.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Base64 encoded encrypted data
        """
        if isinstance(data, str):
            data = data.encode()
        
        encrypted = self.cipher.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Failed to decrypt data")
    
    @classmethod
    def generate_key(cls) -> str:
        """Generate a new encryption key.
        
        Returns:
            Base64 encoded key string
        """
        return Fernet.generate_key().decode()
    
    @classmethod
    def from_env_key(cls, env_var: str = "VECTOR_DB_ENCRYPTION_KEY") -> 'CredentialEncryption':
        """Create encryptor from environment variable.
        
        Args:
            env_var: Environment variable name containing key
            
        Returns:
            CredentialEncryption instance
        """
        key = os.environ.get(env_var)
        if not key:
            logger.warning(f"No encryption key found in {env_var}, generating new key")
            key = cls.generate_key()
            logger.info(f"Generated key: {key}")
            logger.info(f"Set this in your environment: export {env_var}='{key}'")
        
        return cls(key)