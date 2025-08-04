"""Data models for data source integrations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from pathlib import Path


class SourceType(Enum):
    """Types of data sources supported."""
    GMAIL = "gmail"
    FIREFLIES = "fireflies"
    GOOGLE_DRIVE = "google_drive"


class SyncStatus(Enum):
    """Status of sync operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some items failed


class ItemType(Enum):
    """Types of items from data sources."""
    EMAIL = "email"
    EMAIL_ATTACHMENT = "email_attachment"
    TRANSCRIPT = "transcript"
    DOCUMENT = "document"


@dataclass
class DataItem:
    """Represents an item from a data source."""
    source_type: SourceType
    source_id: str  # Unique ID from source (email msgid, doc id, etc.)
    item_type: ItemType
    title: str
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    file_path: Optional[Path] = None
    parent_id: Optional[str] = None  # For attachments linked to emails
    
    def __post_init__(self):
        """Ensure datetime fields are datetime objects."""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.modified_at, str):
            self.modified_at = datetime.fromisoformat(self.modified_at)
    
    @property
    def unique_key(self) -> str:
        """Generate unique key for deduplication."""
        return f"{self.source_type.value}:{self.source_id}"


@dataclass
class EmailMetadata:
    """Metadata specific to emails."""
    sender: str
    recipients: List[str] = field(default_factory=list)
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    subject: str = ""
    labels: List[str] = field(default_factory=list)
    folder: str = "INBOX"
    has_attachments: bool = False
    attachment_count: int = 0
    message_id: str = ""
    in_reply_to: Optional[str] = None
    thread_id: Optional[str] = None


@dataclass 
class TranscriptMetadata:
    """Metadata specific to meeting transcripts."""
    meeting_title: str
    participants: List[str] = field(default_factory=list)
    duration_seconds: Optional[int] = None
    platform: Optional[str] = None  # Zoom, Teams, Meet, etc.
    recording_url: Optional[str] = None
    speakers: Dict[str, str] = field(default_factory=dict)  # speaker_id -> name
    
    @property
    def duration_formatted(self) -> str:
        """Format duration as HH:MM:SS."""
        if not self.duration_seconds:
            return "00:00:00"
        
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@dataclass
class GeminiTranscriptMetadata(TranscriptMetadata):
    """Metadata specific to Gemini transcripts."""
    calendar_event_id: str = ""
    transcript_tab_id: str = ""
    summary: Optional[str] = None
    action_items: List[str] = field(default_factory=list)
    document_url: str = ""
    owner_email: str = ""


@dataclass
class SyncState:
    """Tracks sync state for a data source."""
    source_type: SourceType
    last_sync_timestamp: Optional[datetime] = None
    sync_token: Optional[str] = None  # For incremental syncs
    configuration: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    error_count: int = 0
    last_error: Optional[str] = None
    last_error_timestamp: Optional[datetime] = None
    
    def record_error(self, error: str):
        """Record a sync error."""
        self.error_count += 1
        self.last_error = error
        self.last_error_timestamp = datetime.utcnow()
    
    def clear_errors(self):
        """Clear error state after successful sync."""
        self.error_count = 0
        self.last_error = None
        self.last_error_timestamp = None


@dataclass
class SyncResult:
    """Result of a sync operation."""
    source_type: SourceType
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: SyncStatus = SyncStatus.PENDING
    items_processed: int = 0
    items_created: List[str] = field(default_factory=list)  # File paths
    items_updated: List[str] = field(default_factory=list)
    items_failed: int = 0
    errors: List[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate sync duration in seconds."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        total = self.items_processed + self.items_failed
        if total == 0:
            return 100.0
        return (self.items_processed / total) * 100


@dataclass
class ProcessedDocument:
    """Represents a document processed from a data source."""
    source_id: str  # Unique ID from the source
    source_type: str  # Type of source (gmail, fireflies, google_drive)
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None
    processed_at: datetime = field(default_factory=datetime.utcnow)
    embedding_status: str = "pending"  # pending, completed, failed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "file_path": self.file_path,
            "processed_at": self.processed_at.isoformat(),
            "embedding_status": self.embedding_status
        }


@dataclass 
class DeduplicationResult:
    """Result of content deduplication check."""
    is_duplicate: bool
    similarity: float  # 0.0 to 1.0
    duplicate_of: Optional[str] = None  # source_id of original
    duplicate_source: Optional[str] = None  # source_type of original
    match_type: str = 'none'  # 'exact', 'fuzzy', 'none'
    metadata: Dict[str, Any] = field(default_factory=dict)