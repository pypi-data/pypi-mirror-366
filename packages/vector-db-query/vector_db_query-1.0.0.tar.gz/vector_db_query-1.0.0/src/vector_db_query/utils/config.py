"""Configuration management for Vector DB Query System.

This module maintains backward compatibility while using the enhanced configuration system.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

# Import from enhanced config
from .config_enhanced import (
    AppConfig,
    PathsConfig,
    EmbeddingConfig,
    DocumentProcessingConfig,
    VectorDBConfig,
    MCPConfig,
    CLIConfig,
    QueryConfig,
    LoggingConfig,
    Config,
    ConfigManager,
    get_config as get_enhanced_config,
    reload_config as reload_enhanced_config,
    reset_config as reset_enhanced_config,
)

# Export enhanced config functions with backward-compatible names
get_config = get_enhanced_config
reload_config = reload_enhanced_config
reset_config = reset_enhanced_config

# For backward compatibility, also export all classes and functions
__all__ = [
    "AppConfig",
    "PathsConfig", 
    "EmbeddingConfig",
    "DocumentProcessingConfig",
    "VectorDBConfig",
    "MCPConfig",
    "CLIConfig",
    "QueryConfig",
    "LoggingConfig",
    "Config",
    "ConfigManager",
    "get_config",
    "reload_config",
    "reset_config",
]