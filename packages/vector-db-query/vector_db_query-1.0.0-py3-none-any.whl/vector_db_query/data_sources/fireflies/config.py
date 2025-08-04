"""Configuration for Fireflies.ai integration."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import os

from ..base import DataSourceConfig


@dataclass
class FirefliesConfig(DataSourceConfig):
    """Configuration for Fireflies data source."""
    
    # API Configuration
    api_key: str = field(default_factory=lambda: os.getenv("FIREFLIES_API_KEY", ""))
    api_url: str = "https://api.fireflies.ai/graphql"
    
    # Webhook Configuration
    webhook_secret: str = field(default_factory=lambda: os.getenv("FIREFLIES_WEBHOOK_SECRET", ""))
    webhook_endpoint: str = "/api/webhooks/fireflies"
    
    # Processing Configuration
    fetch_transcripts: bool = True
    fetch_audio: bool = False
    fetch_video: bool = False
    fetch_summary: bool = True
    fetch_action_items: bool = True
    
    # Filtering
    included_users: List[str] = field(default_factory=list)  # Empty = all users
    excluded_users: List[str] = field(default_factory=list)
    min_duration_seconds: int = 300  # 5 minutes minimum
    max_duration_seconds: int = 14400  # 4 hours maximum
    
    # Storage
    knowledge_base_path: str = field(
        default_factory=lambda: os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base")
    )
    
    # Sync Configuration
    initial_history_days: int = 30
    sync_interval_minutes: int = 60
    batch_size: int = 10
    
    # Meeting Platform Filters
    platform_filters: List[str] = field(
        default_factory=lambda: ["zoom", "teams", "meet", "webex"]
    )
    
    def validate(self) -> bool:
        """Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        if not self.api_key:
            raise ValueError("Fireflies API key is required")
        
        if self.fetch_transcripts and not self.knowledge_base_path:
            raise ValueError("Knowledge base path required for transcript storage")
        
        if self.min_duration_seconds < 0:
            raise ValueError("Minimum duration must be positive")
        
        if self.max_duration_seconds < self.min_duration_seconds:
            raise ValueError("Maximum duration must be greater than minimum")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage.
        
        Returns:
            Configuration dictionary
        """
        return {
            'api_url': self.api_url,
            'webhook_endpoint': self.webhook_endpoint,
            'fetch_transcripts': self.fetch_transcripts,
            'fetch_audio': self.fetch_audio,
            'fetch_video': self.fetch_video,
            'fetch_summary': self.fetch_summary,
            'fetch_action_items': self.fetch_action_items,
            'included_users': self.included_users,
            'excluded_users': self.excluded_users,
            'min_duration_seconds': self.min_duration_seconds,
            'max_duration_seconds': self.max_duration_seconds,
            'initial_history_days': self.initial_history_days,
            'sync_interval_minutes': self.sync_interval_minutes,
            'batch_size': self.batch_size,
            'platform_filters': self.platform_filters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FirefliesConfig':
        """Create configuration from dictionary.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            FirefliesConfig instance
        """
        config = cls()
        
        # Update fields from dictionary
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config