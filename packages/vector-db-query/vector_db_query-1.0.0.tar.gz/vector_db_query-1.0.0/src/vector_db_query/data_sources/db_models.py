"""SQLAlchemy database models for data sources."""

from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer, Text, JSON,
    Enum as SQLEnum, CheckConstraint, Index, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
import enum

from .models import SourceType, SyncStatus

Base = declarative_base()


class ProcessStatus(enum.Enum):
    """Processing status for data source items."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DataSource(Base):
    """Model for tracking fetched data source items."""
    
    __tablename__ = 'data_sources'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source identification
    source_type = Column(
        SQLEnum(SourceType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )
    source_id = Column(String(255), unique=True, nullable=False)
    
    # Timestamps
    fetch_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Processing status
    process_status = Column(
        SQLEnum(ProcessStatus, values_callable=lambda x: [e.value for e in x]),
        default=ProcessStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Metadata storage
    metadata = Column(JSONB, default=dict, nullable=False)
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            source_type.in_(['gmail', 'fireflies', 'google_drive']),
            name='valid_source_type'
        ),
        CheckConstraint(
            process_status.in_(['pending', 'processing', 'completed', 'failed']),
            name='valid_process_status'
        ),
        Index('idx_data_sources_metadata', metadata, postgresql_using='gin'),
    )
    
    def __repr__(self):
        return (f"<DataSource(id={self.id}, source_type={self.source_type}, "
                f"source_id={self.source_id}, status={self.process_status})>")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'source_type': self.source_type.value if hasattr(self.source_type, 'value') else self.source_type,
            'source_id': self.source_id,
            'fetch_timestamp': self.fetch_timestamp.isoformat() if self.fetch_timestamp else None,
            'process_status': self.process_status.value if hasattr(self.process_status, 'value') else self.process_status,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @validates('source_type')
    def validate_source_type(self, key, value):
        """Validate source type."""
        if isinstance(value, str):
            try:
                return SourceType(value)
            except ValueError:
                raise ValueError(f"Invalid source_type: {value}")
        return value
    
    @validates('process_status')
    def validate_process_status(self, key, value):
        """Validate process status."""
        if isinstance(value, str):
            try:
                return ProcessStatus(value)
            except ValueError:
                raise ValueError(f"Invalid process_status: {value}")
        return value


class SyncState(Base):
    """Model for tracking synchronization state per data source."""
    
    __tablename__ = 'sync_state'
    
    # Primary key is the source type itself
    source_type = Column(
        SQLEnum(SourceType, values_callable=lambda x: [e.value for e in x]),
        primary_key=True
    )
    
    # Sync tracking
    last_sync_timestamp = Column(DateTime, nullable=True)
    sync_token = Column(Text, nullable=True)  # For incremental syncs
    
    # Configuration
    configuration = Column(JSONB, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Error tracking
    error_count = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    last_error_timestamp = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            source_type.in_(['gmail', 'fireflies', 'google_drive']),
            name='valid_sync_source_type'
        ),
    )
    
    def __repr__(self):
        return (f"<SyncState(source_type={self.source_type}, "
                f"active={self.is_active}, errors={self.error_count})>")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'source_type': self.source_type.value if hasattr(self.source_type, 'value') else self.source_type,
            'last_sync_timestamp': self.last_sync_timestamp.isoformat() if self.last_sync_timestamp else None,
            'sync_token': self.sync_token,
            'configuration': self.configuration,
            'is_active': self.is_active,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'last_error_timestamp': self.last_error_timestamp.isoformat() if self.last_error_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def record_error(self, error_message: str):
        """Record a sync error."""
        self.error_count += 1
        self.last_error = error_message[:1000]  # Truncate to reasonable length
        self.last_error_timestamp = datetime.utcnow()
    
    def clear_errors(self):
        """Clear error state after successful sync."""
        self.error_count = 0
        self.last_error = None
        self.last_error_timestamp = None
    
    def update_sync_time(self, sync_token: Optional[str] = None):
        """Update last sync time and optionally the sync token."""
        self.last_sync_timestamp = datetime.utcnow()
        if sync_token is not None:
            self.sync_token = sync_token
        self.clear_errors()  # Clear errors on successful sync
    
    @validates('source_type')
    def validate_source_type(self, key, value):
        """Validate source type."""
        if isinstance(value, str):
            try:
                return SourceType(value)
            except ValueError:
                raise ValueError(f"Invalid source_type: {value}")
        return value


# Create all tables function
def create_tables(engine):
    """Create all data source tables.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)


# Drop all tables function (use with caution!)
def drop_tables(engine):
    """Drop all data source tables.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(engine)