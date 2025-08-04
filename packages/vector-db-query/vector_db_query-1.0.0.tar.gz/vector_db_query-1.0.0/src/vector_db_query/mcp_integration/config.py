"""Configuration management for MCP server."""

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings
from .models import ServerConfig


class MCPSettings(BaseSettings):
    """MCP server settings."""
    
    # Server configuration
    server_host: str = Field("localhost", description="MCP server host")
    server_port: int = Field(5000, description="MCP server port")
    max_connections: int = Field(10, description="Maximum concurrent connections")
    
    # Authentication
    auth_enabled: bool = Field(True, description="Enable authentication")
    jwt_secret: str = Field("", description="JWT secret key")
    token_expiry: int = Field(3600, description="Token expiry in seconds")
    
    # Security
    allowed_clients: List[str] = Field(default_factory=list, description="Allowed client IDs")
    rate_limit_requests: int = Field(100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(60, description="Rate limit window in seconds")
    
    # Context management
    max_context_tokens: int = Field(100000, description="Maximum context tokens")
    default_result_limit: int = Field(10, description="Default result limit")
    max_result_limit: int = Field(100, description="Maximum result limit")
    
    # Caching
    enable_caching: bool = Field(True, description="Enable query result caching")
    cache_ttl: int = Field(300, description="Cache TTL in seconds")
    cache_max_size: int = Field(1000, description="Maximum cache entries")
    
    # Logging
    log_requests: bool = Field(True, description="Log all requests")
    log_responses: bool = Field(False, description="Log all responses")
    audit_enabled: bool = Field(True, description="Enable audit logging")
    
    class Config:
        env_prefix = "MCP_"
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from config files
    
    def to_server_config(self) -> ServerConfig:
        """Convert to ServerConfig model."""
        return ServerConfig(
            host=self.server_host,
            port=self.server_port,
            max_connections=self.max_connections,
            auth_required=self.auth_enabled,
            token_expiry=self.token_expiry,
            max_context_tokens=self.max_context_tokens,
            enable_caching=self.enable_caching,
            cache_ttl=self.cache_ttl
        )
    
    @classmethod
    def load_from_file(cls, config_path: Optional[Path] = None) -> "MCPSettings":
        """Load settings from configuration file.
        
        Args:
            config_path: Path to config file (defaults to config/mcp.yaml)
            
        Returns:
            MCPSettings instance
        """
        if config_path is None:
            config_path = Path("config/mcp.yaml")
        
        settings_dict = {}
        
        # Load from file if exists
        if config_path.exists():
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f) or {}
                settings_dict.update(file_config.get("mcp", {}))
        
        # Environment variables override file settings
        settings = cls(**settings_dict)
        
        # Generate JWT secret if not provided
        if not settings.jwt_secret and settings.auth_enabled:
            import secrets
            settings.jwt_secret = secrets.token_urlsafe(32)
            # Save generated secret
            if config_path.parent.exists():
                cls._save_jwt_secret(config_path, settings.jwt_secret)
        
        return settings
    
    @staticmethod
    def _save_jwt_secret(config_path: Path, secret: str):
        """Save generated JWT secret to config file."""
        config = {}
        if config_path.exists():
            with open(config_path, "r") as f:
                config = yaml.safe_load(f) or {}
        
        if "mcp" not in config:
            config["mcp"] = {}
        
        config["mcp"]["jwt_secret"] = secret
        
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)


def create_default_mcp_config() -> Dict:
    """Create default MCP configuration."""
    return {
        "mcp": {
            "server_host": "localhost",
            "server_port": 5000,
            "max_connections": 10,
            "auth_enabled": True,
            "jwt_secret": "",  # Will be generated on first run
            "token_expiry": 3600,
            "allowed_clients": [],
            "rate_limit_requests": 100,
            "rate_limit_window": 60,
            "max_context_tokens": 100000,
            "default_result_limit": 10,
            "max_result_limit": 100,
            "enable_caching": True,
            "cache_ttl": 300,
            "cache_max_size": 1000,
            "log_requests": True,
            "log_responses": False,
            "audit_enabled": True
        }
    }