"""
Data models for the scheduling system.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path


class ScheduleType(Enum):
    """Types of schedules supported."""
    CRON = "cron"
    FILE_EVENT = "file_event" 
    INTERVAL = "interval"
    ONE_TIME = "one_time"


class ScheduleStatus(Enum):
    """Schedule execution status."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    ERROR = "error"


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(Enum):
    """File system event types."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class Schedule:
    """Represents a scheduled task configuration."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    schedule_type: ScheduleType = ScheduleType.CRON
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    
    # Schedule configuration
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    run_at: Optional[datetime] = None
    
    # File watching configuration
    watch_path: Optional[str] = None
    file_patterns: List[str] = field(default_factory=list)
    event_types: List[EventType] = field(default_factory=lambda: [EventType.CREATED, EventType.MODIFIED])
    recursive: bool = True
    
    # Task configuration
    task_name: str = "process_documents"
    task_parameters: Dict[str, Any] = field(default_factory=dict)
    max_concurrent_tasks: int = 1
    timeout_seconds: int = 3600  # 1 hour default
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    # Execution tracking
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], EventType):
                data[key] = [event.value for event in value]
            elif isinstance(value, (ScheduleType, ScheduleStatus)):
                data[key] = value.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        """Create from dictionary."""
        # Convert ISO strings back to datetime objects
        datetime_fields = ['created_at', 'updated_at', 'last_run_at', 'next_run_at', 'run_at']
        for field_name in datetime_fields:
            if field_name in data and data[field_name]:
                if isinstance(data[field_name], str):
                    data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Convert enum strings back to enums
        if 'schedule_type' in data:
            data['schedule_type'] = ScheduleType(data['schedule_type'])
        if 'status' in data:
            data['status'] = ScheduleStatus(data['status'])
        if 'event_types' in data:
            data['event_types'] = [EventType(event) for event in data['event_types']]
        
        return cls(**data)


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schedule_id: str = ""
    task_name: str = ""
    status: TaskStatus = TaskStatus.PENDING
    
    # Execution details
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Results
    success: bool = False
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    
    # Context
    triggered_by: str = "scheduler"  # scheduler, file_event, manual
    trigger_details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def execution_time(self) -> Optional[float]:
        """Calculate execution time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return self.duration_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, TaskStatus):
                data[key] = value.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskResult':
        """Create from dictionary."""
        # Convert ISO strings back to datetime objects
        datetime_fields = ['started_at', 'completed_at']
        for field_name in datetime_fields:
            if field_name in data and data[field_name]:
                if isinstance(data[field_name], str):
                    data[field_name] = datetime.fromisoformat(data[field_name])
        
        # Convert status
        if 'status' in data:
            data['status'] = TaskStatus(data['status'])
        
        return cls(**data)


@dataclass
class FileEvent:
    """Represents a file system event."""
    event_type: EventType
    file_path: str
    timestamp: datetime = field(default_factory=datetime.now)
    is_directory: bool = False
    
    # For moved events
    src_path: Optional[str] = None
    dest_path: Optional[str] = None
    
    @property
    def file_name(self) -> str:
        """Get the file name."""
        return Path(self.file_path).name
    
    @property
    def file_extension(self) -> str:
        """Get the file extension."""
        return Path(self.file_path).suffix.lower()
    
    def matches_pattern(self, patterns: List[str]) -> bool:
        """Check if the file matches any of the given patterns."""
        if not patterns:
            return True
        
        file_path = Path(self.file_path)
        for pattern in patterns:
            if file_path.match(pattern):
                return True
        return False


@dataclass
class SchedulerStats:
    """Statistics for the scheduler service."""
    active_schedules: int = 0
    paused_schedules: int = 0
    total_schedules: int = 0
    
    running_tasks: int = 0
    queued_tasks: int = 0
    
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    
    uptime_seconds: float = 0
    last_execution: Optional[datetime] = None
    
    # File watching statistics
    watched_paths: int = 0
    file_events_processed: int = 0
    
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_executions == 0:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100


@dataclass
class ScheduleEvent:
    """Event emitted by the scheduler."""
    event_type: str  # schedule_added, schedule_removed, task_started, task_completed, etc.
    timestamp: datetime = field(default_factory=datetime.now)
    schedule_id: Optional[str] = None
    task_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'schedule_id': self.schedule_id,
            'task_id': self.task_id,
            'data': self.data
        }