"""Configuration for Google Drive integration."""

from typing import List, Optional
from pathlib import Path
from dataclasses import dataclass, field

from ...utils.config import get_config

@dataclass
class GoogleDriveConfig:
    """Configuration for Google Drive data source."""
    
    # OAuth2 settings
    oauth_credentials_file: Optional[str] = None
    oauth_token_file: str = ".gdrive_token.json"
    
    # Search settings
    search_patterns: List[str] = field(default_factory=lambda: ["Notes by Gemini"])
    folder_ids: List[str] = field(default_factory=list)  # Specific folder IDs to search
    
    # Processing settings
    initial_history_days: int = 30
    max_results_per_search: int = 100
    
    # File filters
    min_file_size_bytes: int = 100  # Skip very small files
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10MB max
    
    # Output settings
    knowledge_base_folder: str = "knowledge_base/meetings/gemini"
    
    # API settings
    scopes: List[str] = field(default_factory=lambda: [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.metadata.readonly"
    ])
    
    # Rate limiting
    api_calls_per_second: float = 10.0
    retry_attempts: int = 3
    retry_delay: int = 1  # seconds
    
    @classmethod
    def from_config(cls, config_dict: Optional[dict] = None) -> 'GoogleDriveConfig':
        """Create configuration from dictionary or default config.
        
        Args:
            config_dict: Optional configuration dictionary
            
        Returns:
            GoogleDriveConfig instance
        """
        if config_dict is None:
            app_config = get_config()
            config_dict = app_config.get('data_sources', {}).get('google_drive', {})
        
        return cls(
            oauth_credentials_file=config_dict.get('oauth_credentials_file'),
            oauth_token_file=config_dict.get('oauth_token_file', cls.oauth_token_file),
            search_patterns=config_dict.get('search_patterns', ["Notes by Gemini"]),
            folder_ids=config_dict.get('folder_ids', []),
            initial_history_days=config_dict.get('initial_history_days', 30),
            knowledge_base_folder=config_dict.get('knowledge_base_folder', cls.knowledge_base_folder)
        )
    
    def validate(self) -> List[str]:
        """Validate configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.oauth_credentials_file:
            errors.append("OAuth credentials file not specified")
        elif not Path(self.oauth_credentials_file).exists():
            errors.append(f"OAuth credentials file not found: {self.oauth_credentials_file}")
        
        if not self.search_patterns:
            errors.append("No search patterns specified")
        
        if self.api_calls_per_second <= 0:
            errors.append("API calls per second must be positive")
        
        return errors