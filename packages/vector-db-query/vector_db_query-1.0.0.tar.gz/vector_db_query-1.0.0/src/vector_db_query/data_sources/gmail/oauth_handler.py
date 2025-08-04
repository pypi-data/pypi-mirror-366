"""OAuth2 callback handler for Gmail authentication."""

import asyncio
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional, Tuple
import json
import time

from ...utils.logger import get_logger

logger = get_logger(__name__)


class OAuth2CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth2 callback."""
    
    def log_message(self, format, *args):
        """Override to suppress default HTTP logging."""
        pass
    
    def do_GET(self):
        """Handle GET request for OAuth2 callback."""
        # Parse the URL
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/callback':
            # Extract query parameters
            query_params = parse_qs(parsed_url.query)
            
            # Check for authorization code
            if 'code' in query_params:
                code = query_params['code'][0]
                state = query_params.get('state', [None])[0]
                
                # Store the code in the server instance
                self.server.auth_code = code
                self.server.auth_state = state
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                success_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Successful</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background-color: #f0f0f0;
                        }
                        .container {
                            text-align: center;
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        }
                        h1 { color: #4CAF50; }
                        p { color: #666; }
                        .close-hint { 
                            margin-top: 20px;
                            font-size: 14px;
                            color: #999;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>✓ Authentication Successful!</h1>
                        <p>You have successfully authorized Ansera to access your Gmail account.</p>
                        <p>You can now close this window and return to the application.</p>
                        <p class="close-hint">This window will close automatically in 5 seconds...</p>
                    </div>
                    <script>
                        setTimeout(function() {
                            window.close();
                        }, 5000);
                    </script>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode())
                
            elif 'error' in query_params:
                # Handle error response
                error = query_params['error'][0]
                error_description = query_params.get('error_description', ['Unknown error'])[0]
                
                self.server.auth_error = f"{error}: {error_description}"
                
                # Send error response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Authentication Failed</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                            background-color: #f0f0f0;
                        }}
                        .container {{
                            text-align: center;
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        }}
                        h1 {{ color: #f44336; }}
                        p {{ color: #666; }}
                        .error {{ 
                            background: #ffebee;
                            padding: 10px;
                            border-radius: 5px;
                            margin: 20px 0;
                            color: #c62828;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>✗ Authentication Failed</h1>
                        <p>There was an error during authentication:</p>
                        <div class="error">{error}: {error_description}</div>
                        <p>Please close this window and try again.</p>
                    </div>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode())
        else:
            # Return 404 for other paths
            self.send_error(404)


class OAuth2BrowserFlow:
    """Handles browser-based OAuth2 flow for Gmail."""
    
    def __init__(self, port: int = 8080):
        """Initialize OAuth2 browser flow handler.
        
        Args:
            port: Local port for callback server
        """
        self.port = port
        self.server = None
        self.server_thread = None
        
    async def get_authorization_code(self, auth_url: str, timeout: int = 300) -> Tuple[Optional[str], Optional[str]]:
        """Open browser for authorization and get the code.
        
        Args:
            auth_url: Authorization URL to open
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (authorization_code, state) or (None, error_message)
        """
        # Create HTTP server
        self.server = HTTPServer(('localhost', self.port), OAuth2CallbackHandler)
        self.server.auth_code = None
        self.server.auth_state = None
        self.server.auth_error = None
        
        # Start server in background thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        logger.info(f"Started OAuth2 callback server on port {self.port}")
        
        # Open browser
        logger.info("Opening browser for Gmail authorization...")
        webbrowser.open(auth_url)
        
        # Wait for callback
        start_time = time.time()
        try:
            while time.time() - start_time < timeout:
                if self.server.auth_code:
                    logger.info("Authorization code received")
                    return self.server.auth_code, self.server.auth_state
                
                if self.server.auth_error:
                    logger.error(f"Authorization error: {self.server.auth_error}")
                    return None, self.server.auth_error
                
                await asyncio.sleep(0.5)
            
            # Timeout
            logger.error("Authorization timeout")
            return None, "Authorization timeout"
            
        finally:
            # Stop server
            self.stop_server()
    
    def stop_server(self):
        """Stop the callback server."""
        if self.server:
            logger.info("Stopping OAuth2 callback server")
            self.server.shutdown()
            self.server = None
        
        if self.server_thread:
            self.server_thread.join(timeout=5)
            self.server_thread = None


class GmailOAuth2Setup:
    """Helper class for Gmail OAuth2 setup."""
    
    @staticmethod
    def check_credentials() -> Tuple[bool, str]:
        """Check if OAuth2 credentials are configured.
        
        Returns:
            Tuple of (is_configured, message)
        """
        import os
        
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not client_id:
            return False, "GOOGLE_CLIENT_ID environment variable not set"
        
        if not client_secret:
            return False, "GOOGLE_CLIENT_SECRET environment variable not set"
        
        return True, "OAuth2 credentials configured"
    
    @staticmethod
    async def interactive_setup() -> Dict[str, str]:
        """Interactive setup for Gmail OAuth2.
        
        Returns:
            Configuration dictionary
        """
        print("\n=== Gmail OAuth2 Setup ===\n")
        
        print("To set up Gmail integration, you need to:")
        print("1. Create a Google Cloud project")
        print("2. Enable Gmail API")
        print("3. Create OAuth2 credentials")
        print("\nDetailed instructions available at:")
        print("https://console.cloud.google.com/")
        
        print("\nEnter your OAuth2 credentials:")
        
        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()
        
        # Test configuration
        print("\nTesting configuration...")
        
        config = {
            'GOOGLE_CLIENT_ID': client_id,
            'GOOGLE_CLIENT_SECRET': client_secret,
            'GOOGLE_REDIRECT_URI': 'http://localhost:8080/callback'
        }
        
        return config