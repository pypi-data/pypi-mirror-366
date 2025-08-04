"""Token management utilities for MCP server."""

import json
import logging
import secrets
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .auth import MCPAuthenticator
from .exceptions import MCPAuthenticationError


logger = logging.getLogger(__name__)


class TokenManager:
    """Manages authentication tokens for MCP clients."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize token manager.
        
        Args:
            config_path: Path to authentication config file
        """
        self.config_path = config_path or Path("config/mcp_auth.yaml")
        self.authenticator: Optional[MCPAuthenticator] = None
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Ensure authentication config file exists."""
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create default config
            default_config = {
                "jwt_secret": secrets.token_urlsafe(32),
                "token_expiry": 3600,
                "algorithm": "HS256",
                "clients": []
            }
            
            with open(self.config_path, "w") as f:
                yaml.dump(default_config, f, default_flow_style=False)
            
            logger.info(f"Created default auth config at: {self.config_path}")
    
    def load_authenticator(self) -> MCPAuthenticator:
        """Load authenticator from config.
        
        Returns:
            MCPAuthenticator instance
        """
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        
        self.authenticator = MCPAuthenticator.from_config(config)
        return self.authenticator
    
    def save_config(self):
        """Save current configuration."""
        if not self.authenticator:
            return
        
        # Load existing config
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Update clients (preserve secrets)
        existing_clients = {c["client_id"]: c for c in config.get("clients", [])}
        
        for client_id in self.authenticator.list_clients():
            client_info = self.authenticator.get_client_info(client_id)
            if client_id not in existing_clients:
                # Skip clients not in config (dynamically added)
                continue
            
            # Update permissions and rate limit
            existing_clients[client_id]["permissions"] = client_info.permissions
            existing_clients[client_id]["rate_limit"] = client_info.rate_limit
        
        config["clients"] = list(existing_clients.values())
        
        # Save config
        with open(self.config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def create_client(
        self,
        client_id: str,
        permissions: Optional[List[str]] = None,
        rate_limit: int = 100
    ) -> Dict[str, str]:
        """Create a new client with credentials.
        
        Args:
            client_id: Client identifier
            permissions: List of permissions
            rate_limit: Rate limit per minute
            
        Returns:
            Dictionary with client_id and client_secret
        """
        # Generate client secret
        client_secret = secrets.token_urlsafe(32)
        
        # Load config
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Check if client exists
        existing_clients = [c["client_id"] for c in config.get("clients", [])]
        if client_id in existing_clients:
            raise ValueError(f"Client {client_id} already exists")
        
        # Add client to config
        client_config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "permissions": permissions or ["read"],
            "rate_limit": rate_limit
        }
        
        config["clients"].append(client_config)
        
        # Save config
        with open(self.config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Created client: {client_id}")
        
        # Reload authenticator if loaded
        if self.authenticator:
            self.authenticator.register_client(
                client_id=client_id,
                client_secret=client_secret,
                permissions=permissions,
                rate_limit=rate_limit
            )
        
        return {
            "client_id": client_id,
            "client_secret": client_secret
        }
    
    def generate_token(self, client_id: str, client_secret: str) -> str:
        """Generate a token for a client.
        
        Args:
            client_id: Client identifier
            client_secret: Client secret
            
        Returns:
            JWT token
        """
        if not self.authenticator:
            self.load_authenticator()
        
        # Authenticate client
        if not self.authenticator.authenticate_client(client_id, client_secret):
            raise MCPAuthenticationError("Invalid client credentials")
        
        # Generate token
        return self.authenticator.generate_token(client_id)
    
    def revoke_token(self, token: str):
        """Revoke a token.
        
        Args:
            token: Token to revoke
        """
        if not self.authenticator:
            self.load_authenticator()
        
        self.authenticator.revoke_token(token)
    
    def list_clients(self) -> List[Dict[str, any]]:
        """List all clients (without secrets).
        
        Returns:
            List of client information
        """
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        
        clients = []
        for client in config.get("clients", []):
            clients.append({
                "client_id": client["client_id"],
                "permissions": client.get("permissions", ["read"]),
                "rate_limit": client.get("rate_limit", 100)
            })
        
        return clients
    
    def update_client_permissions(
        self,
        client_id: str,
        permissions: List[str]
    ):
        """Update client permissions.
        
        Args:
            client_id: Client identifier
            permissions: New permissions list
        """
        # Load config
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Find and update client
        updated = False
        for client in config.get("clients", []):
            if client["client_id"] == client_id:
                client["permissions"] = permissions
                updated = True
                break
        
        if not updated:
            raise ValueError(f"Client {client_id} not found")
        
        # Save config
        with open(self.config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Updated permissions for client: {client_id}")
        
        # Update in authenticator if loaded
        if self.authenticator:
            client_info = self.authenticator.get_client_info(client_id)
            if client_info:
                client_info.permissions = permissions
    
    def remove_client(self, client_id: str):
        """Remove a client.
        
        Args:
            client_id: Client identifier
        """
        # Load config
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Remove client
        config["clients"] = [
            c for c in config.get("clients", [])
            if c["client_id"] != client_id
        ]
        
        # Save config
        with open(self.config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Removed client: {client_id}")
        
        # Revoke all tokens if authenticator loaded
        if self.authenticator:
            self.authenticator.revoke_all_client_tokens(client_id)
    
    def export_client_config(self, client_id: str, output_path: Path):
        """Export client configuration for distribution.
        
        Args:
            client_id: Client identifier
            output_path: Path to save config
        """
        # Load config
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Find client
        client_config = None
        for client in config.get("clients", []):
            if client["client_id"] == client_id:
                client_config = client
                break
        
        if not client_config:
            raise ValueError(f"Client {client_id} not found")
        
        # Create export config
        export_config = {
            "mcp_server": {
                "endpoint": "stdio",  # MCP uses stdio
                "auth": {
                    "client_id": client_config["client_id"],
                    "client_secret": client_config["client_secret"]
                }
            }
        }
        
        # Save export
        with open(output_path, "w") as f:
            yaml.dump(export_config, f, default_flow_style=False)
        
        # Set restrictive permissions
        output_path.chmod(0o600)
        
        logger.info(f"Exported config for client {client_id} to: {output_path}")