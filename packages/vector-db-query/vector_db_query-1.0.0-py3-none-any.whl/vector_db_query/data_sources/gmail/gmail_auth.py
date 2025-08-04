"""Gmail OAuth2 authentication provider."""

import os
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import base64
from urllib.parse import urlencode

from ..auth.oauth2 import OAuth2Provider
from ..auth.models import AuthToken, TokenType
from ...utils.logger import get_logger

logger = get_logger(__name__)


class GmailOAuth2Provider(OAuth2Provider):
    """OAuth2 provider specifically configured for Gmail API access."""
    
    # Gmail OAuth2 endpoints
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    
    # Gmail-specific scopes
    GMAIL_SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.labels"
    ]
    
    def __init__(self, 
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 redirect_uri: Optional[str] = None):
        """Initialize Gmail OAuth2 provider.
        
        Args:
            client_id: Google OAuth2 client ID
            client_secret: Google OAuth2 client secret
            redirect_uri: OAuth2 redirect URI (defaults to local callback)
        """
        # Get credentials from environment or parameters
        client_id = client_id or os.getenv('GOOGLE_CLIENT_ID')
        client_secret = client_secret or os.getenv('GOOGLE_CLIENT_SECRET')
        redirect_uri = redirect_uri or os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080/callback')
        
        if not client_id or not client_secret:
            raise ValueError(
                "Google OAuth2 credentials not configured. "
                "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
            )
        
        super().__init__(
            provider_name="gmail",
            client_id=client_id,
            client_secret=client_secret,
            auth_url=self.GOOGLE_AUTH_URL,
            token_url=self.GOOGLE_TOKEN_URL,
            redirect_uri=redirect_uri,
            scopes=self.GMAIL_SCOPES
        )
        
    def get_auth_url(self, state: Optional[str] = None) -> str:
        """Get Gmail authorization URL.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        # Build authorization URL with Gmail-specific parameters
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.scopes),
            'access_type': 'offline',  # Request refresh token
            'prompt': 'consent'  # Force consent to get refresh token
        }
        
        if state:
            params['state'] = state
            
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code(self, code: str) -> AuthToken:
        """Exchange authorization code for tokens.
        
        Args:
            code: Authorization code from OAuth2 callback
            
        Returns:
            AuthToken containing access and refresh tokens
        """
        # Exchange code for tokens
        token_data = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = await self._make_token_request(token_data)
        
        # Create AuthToken from response
        return self._create_auth_token(response)
    
    async def refresh(self, token: AuthToken) -> AuthToken:
        """Refresh Gmail access token.
        
        Args:
            token: Current auth token with refresh token
            
        Returns:
            New AuthToken with refreshed access token
        """
        if not token.refresh_token:
            raise ValueError("No refresh token available")
        
        # Refresh the token
        token_data = {
            'refresh_token': token.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        
        response = await self._make_token_request(token_data)
        
        # Create new token, preserving refresh token if not returned
        new_token = self._create_auth_token(response)
        if not new_token.refresh_token and token.refresh_token:
            new_token.refresh_token = token.refresh_token
            
        return new_token
    
    def _create_auth_token(self, response: Dict) -> AuthToken:
        """Create AuthToken from OAuth2 response.
        
        Args:
            response: OAuth2 token response
            
        Returns:
            AuthToken instance
        """
        # Calculate expiry time
        expires_in = response.get('expires_in', 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Extract user info from ID token if available
        metadata = {}
        if 'id_token' in response:
            try:
                # Decode JWT payload (not verifying signature for simplicity)
                payload = response['id_token'].split('.')[1]
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded = json.loads(base64.urlsafe_b64decode(payload))
                
                metadata['email'] = decoded.get('email')
                metadata['email_verified'] = decoded.get('email_verified', False)
                metadata['name'] = decoded.get('name')
                
            except Exception as e:
                logger.warning(f"Failed to decode ID token: {e}")
        
        return AuthToken(
            provider="gmail",
            token_type=TokenType.BEARER,
            access_token=response['access_token'],
            refresh_token=response.get('refresh_token'),
            expires_at=expires_at,
            scopes=response.get('scope', '').split() if response.get('scope') else self.scopes,
            metadata=metadata
        )
    
    async def validate_token(self, token: AuthToken) -> bool:
        """Validate Gmail access token.
        
        Args:
            token: Token to validate
            
        Returns:
            True if token is valid
        """
        # Check basic validity
        if not await super().validate_token(token):
            return False
        
        # Additional Gmail-specific validation could be added here
        # For example, making a test API call
        
        return True
    
    def get_required_config(self) -> List[Dict[str, str]]:
        """Get required configuration for Gmail OAuth2.
        
        Returns:
            List of configuration parameters
        """
        return [
            {
                'name': 'GOOGLE_CLIENT_ID',
                'description': 'Google OAuth2 Client ID',
                'required': True
            },
            {
                'name': 'GOOGLE_CLIENT_SECRET',
                'description': 'Google OAuth2 Client Secret',
                'required': True
            },
            {
                'name': 'GOOGLE_REDIRECT_URI',
                'description': 'OAuth2 Redirect URI (defaults to http://localhost:8080/callback)',
                'required': False
            }
        ]
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for Gmail OAuth2.
        
        Returns:
            Setup instructions text
        """
        return """
Gmail OAuth2 Setup Instructions:

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Gmail API:
   - Go to APIs & Services > Library
   - Search for "Gmail API"
   - Click Enable
4. Create OAuth2 credentials:
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > OAuth client ID
   - Choose "Web application"
   - Add authorized redirect URI: http://localhost:8080/callback
   - Copy Client ID and Client Secret
5. Set environment variables:
   export GOOGLE_CLIENT_ID="your_client_id"
   export GOOGLE_CLIENT_SECRET="your_client_secret"
6. (Optional) For production, update redirect URI and set:
   export GOOGLE_REDIRECT_URI="https://your-domain.com/callback"
"""