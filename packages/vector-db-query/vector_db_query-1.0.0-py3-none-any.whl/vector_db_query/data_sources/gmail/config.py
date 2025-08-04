"""Gmail configuration settings."""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..models import DataSourceConfig


@dataclass
class GmailConfig(DataSourceConfig):
    """Configuration for Gmail data source."""
    
    # OAuth2 settings (inherited from base)
    # client_id, client_secret, redirect_uri are in parent class
    
    # Gmail-specific settings
    email_address: Optional[str] = None  # Primary email address
    
    # Filtering options
    label_filters: list[str] = field(default_factory=lambda: ['INBOX'])
    exclude_labels: list[str] = field(default_factory=lambda: ['SPAM', 'TRASH'])
    sender_whitelist: list[str] = field(default_factory=list)
    sender_blacklist: list[str] = field(default_factory=list)
    
    # Processing options
    fetch_attachments: bool = True
    max_attachment_size_mb: int = 10
    include_thread_context: bool = True
    
    # Sync settings
    max_results_per_page: int = 100
    initial_history_days: int = 30  # How far back to fetch on first sync
    
    # Content extraction
    extract_meeting_links: bool = True
    extract_calendar_events: bool = True
    
    def __post_init__(self):
        """Initialize Gmail configuration."""
        self.source_type = "gmail"
        super().__post_init__()
    
    def validate(self) -> bool:
        """Validate Gmail configuration.
        
        Returns:
            True if configuration is valid
        """
        # Base validation
        if not super().validate():
            return False
        
        # Gmail-specific validation
        if self.max_attachment_size_mb < 1 or self.max_attachment_size_mb > 50:
            raise ValueError("max_attachment_size_mb must be between 1 and 50 MB")
        
        if self.max_results_per_page < 1 or self.max_results_per_page > 500:
            raise ValueError("max_results_per_page must be between 1 and 500")
        
        if self.initial_history_days < 1 or self.initial_history_days > 365:
            raise ValueError("initial_history_days must be between 1 and 365")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        config = super().to_dict()
        
        # Add Gmail-specific fields
        config.update({
            'email_address': self.email_address,
            'label_filters': self.label_filters,
            'exclude_labels': self.exclude_labels,
            'sender_whitelist': self.sender_whitelist,
            'sender_blacklist': self.sender_blacklist,
            'fetch_attachments': self.fetch_attachments,
            'max_attachment_size_mb': self.max_attachment_size_mb,
            'include_thread_context': self.include_thread_context,
            'max_results_per_page': self.max_results_per_page,
            'initial_history_days': self.initial_history_days,
            'extract_meeting_links': self.extract_meeting_links,
            'extract_calendar_events': self.extract_calendar_events
        })
        
        return config
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GmailConfig':
        """Create configuration from dictionary.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            GmailConfig instance
        """
        # Extract Gmail-specific fields
        gmail_fields = {
            'email_address': data.get('email_address'),
            'label_filters': data.get('label_filters', ['INBOX']),
            'exclude_labels': data.get('exclude_labels', ['SPAM', 'TRASH']),
            'sender_whitelist': data.get('sender_whitelist', []),
            'sender_blacklist': data.get('sender_blacklist', []),
            'fetch_attachments': data.get('fetch_attachments', True),
            'max_attachment_size_mb': data.get('max_attachment_size_mb', 10),
            'include_thread_context': data.get('include_thread_context', True),
            'max_results_per_page': data.get('max_results_per_page', 100),
            'initial_history_days': data.get('initial_history_days', 30),
            'extract_meeting_links': data.get('extract_meeting_links', True),
            'extract_calendar_events': data.get('extract_calendar_events', True)
        }
        
        # Add base fields
        base_fields = {
            'source_id': data.get('source_id'),
            'enabled': data.get('enabled', True),
            'sync_interval_minutes': data.get('sync_interval_minutes', 30),
            'knowledge_base_path': data.get('knowledge_base_path'),
            'client_id': data.get('client_id'),
            'client_secret': data.get('client_secret'),
            'redirect_uri': data.get('redirect_uri')
        }
        
        # Combine all fields
        all_fields = {**base_fields, **gmail_fields}
        
        return cls(**all_fields)


# Default configuration
DEFAULT_GMAIL_CONFIG = GmailConfig(
    source_id="gmail_default",
    enabled=True,
    sync_interval_minutes=30,
    label_filters=['INBOX'],
    exclude_labels=['SPAM', 'TRASH'],
    fetch_attachments=True,
    max_attachment_size_mb=10,
    include_thread_context=True,
    max_results_per_page=100,
    initial_history_days=30,
    extract_meeting_links=True,
    extract_calendar_events=True
)