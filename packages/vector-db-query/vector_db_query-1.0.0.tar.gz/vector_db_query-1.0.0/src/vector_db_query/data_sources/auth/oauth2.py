"""OAuth2 authentication implementation."""

import asyncio
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode, parse_qs, urlparse
import httpx
import secrets
import json

from .base import AuthProvider, AuthToken
from ..exceptions import AuthenticationError
from ...utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class OAuth2Config:
    """OAuth2 configuration."""
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    redirect_uri: str = "http://localhost:8080/callback"
    scopes: List[str] = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = []


class OAuth2Provider(AuthProvider):
    """OAuth2 authentication provider."""
    
    def __init__(self, config: OAuth2Config):
        """Initialize OAuth2 provider.
        
        Args:
            config: OAuth2 configuration
        """
        self.config = config
        self.http_client = httpx.AsyncClient()
        self._server = None
        self._auth_code = None
        self._state = None
    
    async def authenticate(self) -> AuthToken:
        """Perform OAuth2 authentication flow.
        
        Returns:
            AuthToken with access token and refresh token
        """
        # Generate state for CSRF protection
        self._state = secrets.token_urlsafe(32)
        
        # Build authorization URL
        auth_params = {
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'response_type': 'code',
            'state': self._state,
            'access_type': 'offline',  # For refresh token
            'prompt': 'consent'  # Force consent to get refresh token
        }
        
        if self.config.scopes:
            auth_params['scope'] = ' '.join(self.config.scopes)
        
        auth_url = f"{self.config.auth_url}?{urlencode(auth_params)}"
        
        # Start local server to receive callback
        from aiohttp import web
        
        async def handle_callback(request):
            """Handle OAuth2 callback."""
            query = request.rel_url.query
            
            # Verify state
            if query.get('state') != self._state:
                return web.Response(text="Invalid state parameter", status=400)
            
            # Check for error
            if 'error' in query:
                error = query.get('error')
                error_desc = query.get('error_description', '')
                return web.Response(
                    text=f"Authentication failed: {error} - {error_desc}",
                    status=400
                )
            
            # Get authorization code
            self._auth_code = query.get('code')
            if not self._auth_code:
                return web.Response(text="No authorization code received", status=400)
            
            # Return success page
            html = """
            <html>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: green;">✓ Authentication Successful!</h1>
                <p>You can now close this window and return to the application.</p>
                <script>window.setTimeout(function(){window.close();}, 2000);</script>
            </body>
            </html>
            """
            return web.Response(text=html, content_type='text/html')
        
        # Create app and start server
        app = web.Application()
        app.router.add_get('/callback', handle_callback)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Parse redirect URI to get host and port
        parsed = urlparse(self.config.redirect_uri)
        host = parsed.hostname or 'localhost'
        port = parsed.port or 8080
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"Started OAuth2 callback server on {host}:{port}")
        
        try:
            # Open browser for authentication
            logger.info("Opening browser for authentication...")
            webbrowser.open(auth_url)
            
            # Wait for callback (timeout after 5 minutes)
            timeout = 300  # 5 minutes
            start_time = asyncio.get_event_loop().time()
            
            while self._auth_code is None:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    raise AuthenticationError("Authentication timeout - no response received")
                
                await asyncio.sleep(0.1)
            
            # Exchange code for tokens
            token = await self._exchange_code_for_token(self._auth_code)
            
            return token
            
        finally:
            # Cleanup server
            await runner.cleanup()
    
    async def _exchange_code_for_token(self, code: str) -> AuthToken:
        """Exchange authorization code for access token.
        
        Args:
            code: Authorization code
            
        Returns:
            AuthToken with access and refresh tokens
        """
        token_data = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'code': code,
            'redirect_uri': self.config.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = await self.http_client.post(
                self.config.token_url,
                data=token_data
            )
            response.raise_for_status()
            
            token_response = response.json()
            
            # Calculate expiration time
            expires_at = None
            if 'expires_in' in token_response:
                expires_at = datetime.utcnow() + timedelta(seconds=token_response['expires_in'])
            
            return AuthToken(
                access_token=token_response['access_token'],
                token_type=token_response.get('token_type', 'Bearer'),
                expires_at=expires_at,
                refresh_token=token_response.get('refresh_token'),
                scope=token_response.get('scope')
            )
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(f"Token exchange failed: {error_detail}")
            raise AuthenticationError(f"Failed to exchange code for token: {error_detail}")
        except Exception as e:
            logger.error(f"Token exchange error: {e}")
            raise AuthenticationError(f"Token exchange failed: {str(e)}")
    
    async def refresh(self, token: AuthToken) -> AuthToken:
        """Refresh an access token using refresh token.
        
        Args:
            token: Current token with refresh token
            
        Returns:
            New AuthToken with refreshed access token
        """
        if not token.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        refresh_data = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'refresh_token': token.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = await self.http_client.post(
                self.config.token_url,
                data=refresh_data
            )
            response.raise_for_status()
            
            token_response = response.json()
            
            # Calculate new expiration time
            expires_at = None
            if 'expires_in' in token_response:
                expires_at = datetime.utcnow() + timedelta(seconds=token_response['expires_in'])
            
            return AuthToken(
                access_token=token_response['access_token'],
                token_type=token_response.get('token_type', 'Bearer'),
                expires_at=expires_at,
                refresh_token=token_response.get('refresh_token', token.refresh_token),
                scope=token_response.get('scope', token.scope)
            )
            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(f"Token refresh failed: {error_detail}")
            raise AuthenticationError(f"Failed to refresh token: {error_detail}")
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    async def revoke(self, token: AuthToken) -> bool:
        """Revoke a token (if supported by provider).
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revocation successful
        """
        # Note: Not all OAuth2 providers support token revocation
        logger.warning("Token revocation not implemented for this provider")
        return False
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.http_client.aclose()