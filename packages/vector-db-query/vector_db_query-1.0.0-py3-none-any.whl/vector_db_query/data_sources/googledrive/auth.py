"""Google Drive OAuth2 authentication implementation."""

import json
import asyncio
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from ..auth import OAuth2Provider, AuthToken
from .config import GoogleDriveConfig
from ...utils.logger import get_logger

logger = get_logger(__name__)


class GoogleDriveOAuth2Provider(OAuth2Provider):
    """OAuth2 provider for Google Drive API."""
    
    def __init__(self, config: GoogleDriveConfig):
        """Initialize Google Drive OAuth2 provider.
        
        Args:
            config: Google Drive configuration
        """
        super().__init__(
            client_id="",  # Will be loaded from credentials file
            client_secret="",  # Will be loaded from credentials file
            redirect_uri="http://localhost:8080",
            scopes=config.scopes
        )
        self.config = config
        self._load_client_config()
    
    def _load_client_config(self):
        """Load OAuth2 client configuration from file."""
        if not self.config.oauth_credentials_file:
            raise ValueError("OAuth credentials file not configured")
        
        creds_path = Path(self.config.oauth_credentials_file)
        if not creds_path.exists():
            raise FileNotFoundError(f"Credentials file not found: {creds_path}")
        
        try:
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
            
            # Handle different credential file formats
            if 'installed' in creds_data:
                app_creds = creds_data['installed']
            elif 'web' in creds_data:
                app_creds = creds_data['web']
            else:
                raise ValueError("Invalid credentials file format")
            
            self.client_id = app_creds['client_id']
            self.client_secret = app_creds['client_secret']
            
            # Update redirect URIs if specified
            if 'redirect_uris' in app_creds:
                self.redirect_uri = app_creds['redirect_uris'][0]
            
            logger.info("Loaded Google OAuth2 credentials")
            
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise
    
    async def authenticate(self) -> AuthToken:
        """Authenticate with Google Drive API.
        
        Returns:
            AuthToken with access credentials
        """
        token_path = Path(self.config.oauth_token_file)
        
        # Try to load existing token
        if token_path.exists():
            try:
                token = await self._load_token(token_path)
                if not self._is_token_expired(token):
                    logger.info("Using cached Google Drive token")
                    return token
                else:
                    # Try to refresh
                    logger.info("Token expired, attempting refresh")
                    refreshed_token = await self.refresh(token)
                    if refreshed_token:
                        return refreshed_token
            except Exception as e:
                logger.warning(f"Failed to load/refresh token: {e}")
        
        # Need new authentication
        logger.info("Starting Google Drive OAuth2 flow")
        
        # Create flow
        flow = Flow.from_client_config(
            {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        # Get authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Use the parent class browser flow
        auth_code = await self._browser_auth_flow(auth_url)
        
        # Exchange code for token
        flow.fetch_token(code=auth_code)
        
        # Create AuthToken
        creds = flow.credentials
        token = AuthToken(
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            expires_at=creds.expiry,
            token_type="Bearer",
            scopes=list(creds.scopes) if creds.scopes else self.scopes
        )
        
        # Save token
        await self._save_token(token, token_path)
        
        logger.info("Successfully authenticated with Google Drive")
        return token
    
    async def refresh(self, token: AuthToken) -> Optional[AuthToken]:
        """Refresh an expired token.
        
        Args:
            token: Expired token to refresh
            
        Returns:
            New AuthToken if refresh successful, None otherwise
        """
        if not token.refresh_token:
            logger.error("No refresh token available")
            return None
        
        try:
            # Create credentials object
            creds = Credentials(
                token=token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=token.scopes or self.scopes
            )
            
            # Refresh the token
            creds.refresh(Request())
            
            # Create new AuthToken
            new_token = AuthToken(
                access_token=creds.token,
                refresh_token=creds.refresh_token or token.refresh_token,
                expires_at=creds.expiry,
                token_type="Bearer",
                scopes=list(creds.scopes) if creds.scopes else token.scopes
            )
            
            # Save refreshed token
            token_path = Path(self.config.oauth_token_file)
            await self._save_token(new_token, token_path)
            
            logger.info("Successfully refreshed Google Drive token")
            return new_token
            
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return None
    
    async def _load_token(self, token_path: Path) -> AuthToken:
        """Load token from file.
        
        Args:
            token_path: Path to token file
            
        Returns:
            Loaded AuthToken
        """
        async with aiofiles.open(token_path, 'r') as f:
            data = json.loads(await f.read())
        
        return AuthToken(
            access_token=data['access_token'],
            refresh_token=data.get('refresh_token'),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            token_type=data.get('token_type', 'Bearer'),
            scopes=data.get('scopes', self.scopes)
        )
    
    async def _save_token(self, token: AuthToken, token_path: Path) -> None:
        """Save token to file.
        
        Args:
            token: Token to save
            token_path: Path to save token
        """
        data = {
            'access_token': token.access_token,
            'refresh_token': token.refresh_token,
            'expires_at': token.expires_at.isoformat() if token.expires_at else None,
            'token_type': token.token_type,
            'scopes': token.scopes
        }
        
        token_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(token_path, 'w') as f:
            await f.write(json.dumps(data, indent=2))
        
        # Secure the file
        token_path.chmod(0o600)
    
    def _is_token_expired(self, token: AuthToken) -> bool:
        """Check if token is expired.
        
        Args:
            token: Token to check
            
        Returns:
            True if expired
        """
        if not token.expires_at:
            return False
        
        # Consider expired if less than 5 minutes remaining
        return datetime.utcnow() > (token.expires_at - timedelta(minutes=5))
    
    async def test_connection(self, token: AuthToken) -> bool:
        """Test Google Drive API connection.
        
        Args:
            token: Authentication token
            
        Returns:
            True if connection successful
        """
        try:
            # Create credentials
            creds = Credentials(
                token=token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            # Build service
            service = build('drive', 'v3', credentials=creds)
            
            # Test with a simple query
            result = service.files().list(
                pageSize=1,
                fields="files(id, name)"
            ).execute()
            
            logger.info("Google Drive connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Google Drive connection test failed: {e}")
            return False