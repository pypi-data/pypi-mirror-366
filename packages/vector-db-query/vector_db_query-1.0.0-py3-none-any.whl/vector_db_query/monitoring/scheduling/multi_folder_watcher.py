"""
Enhanced file watcher with multi-folder support.

This module extends the basic file watcher to support monitoring
multiple folders with different patterns and configurations.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from threading import RLock
import json

from .file_watcher import FileWatcher, ScheduleEventHandler
from .models import FileEvent, EventType, Schedule, ScheduleType

logger = logging.getLogger(__name__)


@dataclass
class FolderWatchConfig:
    """Configuration for watching a specific folder."""
    path: str
    patterns: List[str] = field(default_factory=list)
    recursive: bool = True
    event_types: List[EventType] = field(default_factory=lambda: [EventType.CREATED, EventType.MODIFIED])
    ignore_patterns: List[str] = field(default_factory=list)
    min_file_size: Optional[int] = None  # Minimum file size in bytes
    max_file_size: Optional[int] = None  # Maximum file size in bytes
    
    def matches_filters(self, file_path: str, size: Optional[int] = None) -> bool:
        """Check if file matches this folder's filters."""
        path_obj = Path(file_path)
        
        # Check ignore patterns first
        for pattern in self.ignore_patterns:
            if path_obj.match(pattern):
                return False
        
        # Check file patterns
        if self.patterns:
            matches_pattern = any(path_obj.match(pattern) for pattern in self.patterns)
            if not matches_pattern:
                return False
        
        # Check file size filters
        if size is not None:
            if self.min_file_size is not None and size < self.min_file_size:
                return False
            if self.max_file_size is not None and size > self.max_file_size:
                return False
        
        return True


@dataclass
class MultiFolderSchedule(Schedule):
    """Extended schedule with multi-folder support."""
    folder_configs: List[FolderWatchConfig] = field(default_factory=list)
    cross_folder_dedup: bool = True  # Deduplicate events across folders
    aggregate_events: bool = False  # Aggregate multiple events before triggering
    aggregation_window: int = 5  # Seconds to wait for aggregation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary including folder configs."""
        base_dict = super().to_dict() if hasattr(super(), 'to_dict') else {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'schedule_type': self.schedule_type.value,
            'enabled': self.enabled,
            'task_name': self.task_name,
            'task_params': self.task_params
        }
        
        base_dict['folder_configs'] = [
            {
                'path': config.path,
                'patterns': config.patterns,
                'recursive': config.recursive,
                'event_types': [e.value for e in config.event_types],
                'ignore_patterns': config.ignore_patterns,
                'min_file_size': config.min_file_size,
                'max_file_size': config.max_file_size
            }
            for config in self.folder_configs
        ]
        
        base_dict['cross_folder_dedup'] = self.cross_folder_dedup
        base_dict['aggregate_events'] = self.aggregate_events
        base_dict['aggregation_window'] = self.aggregation_window
        
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultiFolderSchedule':
        """Create from dictionary."""
        # Extract folder configs
        folder_configs = []
        for fc_data in data.get('folder_configs', []):
            folder_configs.append(FolderWatchConfig(
                path=fc_data['path'],
                patterns=fc_data.get('patterns', []),
                recursive=fc_data.get('recursive', True),
                event_types=[EventType(e) for e in fc_data.get('event_types', ['created', 'modified'])],
                ignore_patterns=fc_data.get('ignore_patterns', []),
                min_file_size=fc_data.get('min_file_size'),
                max_file_size=fc_data.get('max_file_size')
            ))
        
        # Create schedule
        schedule = cls(
            name=data['name'],
            description=data.get('description', ''),
            schedule_type=ScheduleType.FILE_EVENT,
            enabled=data.get('enabled', True),
            task_name=data['task_name'],
            task_params=data.get('task_params', {}),
            folder_configs=folder_configs,
            cross_folder_dedup=data.get('cross_folder_dedup', True),
            aggregate_events=data.get('aggregate_events', False),
            aggregation_window=data.get('aggregation_window', 5)
        )
        
        return schedule


class MultiFolderWatcher(FileWatcher):
    """
    Enhanced file watcher supporting multiple folders with different configurations.
    
    Extends FileWatcher with:
    - Multiple folder monitoring with different patterns
    - Cross-folder event deduplication
    - Event aggregation
    - Advanced filtering
    """
    
    def __init__(self):
        """Initialize multi-folder watcher."""
        super().__init__()
        
        # Multi-folder tracking
        self._folder_configs: Dict[str, List[FolderWatchConfig]] = {}  # schedule_id -> configs
        self._path_to_schedule: Dict[str, Set[str]] = {}  # path -> set of schedule_ids
        
        # Event aggregation
        self._event_buffer: Dict[str, List[FileEvent]] = {}  # schedule_id -> events
        self._aggregation_timers: Dict[str, Any] = {}  # schedule_id -> timer
        
        # Deduplication
        self._recent_events: Dict[str, datetime] = {}  # "file_path:event_type" -> timestamp
        self._dedup_window = 2  # seconds
        
        logger.info("MultiFolderWatcher initialized")
    
    def add_multi_folder_schedule(
        self,
        schedule: MultiFolderSchedule,
        callback=None
    ) -> bool:
        """
        Add a multi-folder schedule to monitor.
        
        Args:
            schedule: Multi-folder schedule configuration
            callback: Optional callback function
            
        Returns:
            True if added successfully
        """
        if schedule.schedule_type != ScheduleType.FILE_EVENT:
            logger.error(f"Invalid schedule type: {schedule.schedule_type}")
            return False
        
        if not schedule.folder_configs:
            logger.error(f"No folder configurations for schedule: {schedule.name}")
            return False
        
        with self._lock:
            # Store folder configurations
            self._folder_configs[schedule.id] = schedule.folder_configs
            
            # Add watchers for each folder
            for config in schedule.folder_configs:
                path = Path(config.path)
                
                if not path.exists():
                    logger.warning(f"Path does not exist: {config.path}")
                    continue
                
                # Track path to schedule mapping
                if config.path not in self._path_to_schedule:
                    self._path_to_schedule[config.path] = set()
                self._path_to_schedule[config.path].add(schedule.id)
                
                # Create handler for this specific folder config
                handler = MultiFolderEventHandler(
                    schedule_id=schedule.id,
                    folder_config=config,
                    callback=self._handle_multi_folder_event,
                    dedup_check=self._is_duplicate_event if schedule.cross_folder_dedup else None
                )
                
                # Add to observer
                if self._observer:
                    watch = self._observer.schedule(
                        handler,
                        config.path,
                        recursive=config.recursive
                    )
                    
                    if schedule.id not in self._watches:
                        self._watches[schedule.id] = []
                    self._watches[schedule.id].append(watch)
                    
                    logger.info(f"Added watcher for {config.path} (schedule: {schedule.name})")
            
            # Store schedule and callback
            self._schedules[schedule.id] = schedule
            if callback:
                self._callbacks[schedule.id] = callback
            
            # Initialize event buffer if aggregation is enabled
            if schedule.aggregate_events:
                self._event_buffer[schedule.id] = []
            
            return True
    
    def _handle_multi_folder_event(
        self,
        event: FileEvent,
        schedule_id: str,
        folder_config: FolderWatchConfig
    ):
        """Handle file event from multi-folder watcher."""
        schedule = self._schedules.get(schedule_id)
        if not schedule or not isinstance(schedule, MultiFolderSchedule):
            return
        
        # Apply folder-specific filters
        file_size = event.size if hasattr(event, 'size') else None
        if not folder_config.matches_filters(event.file_path, file_size):
            logger.debug(f"Event filtered out by folder config: {event.file_path}")
            return
        
        # Check for duplicates if enabled
        if schedule.cross_folder_dedup and self._is_duplicate_event(event):
            logger.debug(f"Duplicate event filtered: {event.file_path}")
            return
        
        # Handle aggregation if enabled
        if schedule.aggregate_events:
            self._aggregate_event(event, schedule_id)
        else:
            # Process immediately
            self._process_multi_folder_event(event, schedule_id)
    
    def _is_duplicate_event(self, event: FileEvent) -> bool:
        """Check if this is a duplicate event across folders."""
        event_key = f"{event.file_path}:{event.event_type.value}"
        now = datetime.now()
        
        with self._lock:
            if event_key in self._recent_events:
                last_time = self._recent_events[event_key]
                if (now - last_time).total_seconds() < self._dedup_window:
                    return True
            
            # Record this event
            self._recent_events[event_key] = now
            
            # Clean old entries
            cutoff = now
            to_remove = [
                k for k, v in self._recent_events.items()
                if (cutoff - v).total_seconds() > self._dedup_window * 2
            ]
            for key in to_remove:
                del self._recent_events[key]
        
        return False
    
    def _aggregate_event(self, event: FileEvent, schedule_id: str):
        """Add event to aggregation buffer."""
        import threading
        
        with self._lock:
            # Add to buffer
            self._event_buffer[schedule_id].append(event)
            
            # Cancel existing timer if any
            if schedule_id in self._aggregation_timers:
                self._aggregation_timers[schedule_id].cancel()
            
            # Start new timer
            schedule = self._schedules[schedule_id]
            timer = threading.Timer(
                schedule.aggregation_window,
                self._flush_aggregated_events,
                args=[schedule_id]
            )
            self._aggregation_timers[schedule_id] = timer
            timer.start()
    
    def _flush_aggregated_events(self, schedule_id: str):
        """Process all aggregated events for a schedule."""
        with self._lock:
            events = self._event_buffer.get(schedule_id, [])
            if not events:
                return
            
            # Clear buffer
            self._event_buffer[schedule_id] = []
            
            # Remove timer
            if schedule_id in self._aggregation_timers:
                del self._aggregation_timers[schedule_id]
        
        # Process aggregated events
        logger.info(f"Processing {len(events)} aggregated events for schedule {schedule_id}")
        
        # Create summary event
        summary_event = FileEvent(
            event_type=EventType.CREATED,  # Generic type for aggregated
            file_path=f"[{len(events)} files]",
            is_directory=False,
            timestamp=datetime.now()
        )
        
        # Add details about aggregated events
        summary_event.aggregated_events = events
        
        self._process_multi_folder_event(summary_event, schedule_id)
    
    def _process_multi_folder_event(self, event: FileEvent, schedule_id: str):
        """Process a multi-folder event."""
        # Mark as due for execution
        with self._lock:
            self._due_schedules.add(schedule_id)
        
        # Call callback if registered
        callback = self._callbacks.get(schedule_id)
        if callback:
            try:
                callback(event, schedule_id)
            except Exception as e:
                logger.error(f"Error in callback for {schedule_id}: {str(e)}")
    
    def get_folder_statistics(self, schedule_id: str) -> Dict[str, Any]:
        """Get statistics for a multi-folder schedule."""
        schedule = self._schedules.get(schedule_id)
        if not schedule or not isinstance(schedule, MultiFolderSchedule):
            return {}
        
        stats = {
            'schedule_name': schedule.name,
            'folder_count': len(schedule.folder_configs),
            'folders': []
        }
        
        for config in schedule.folder_configs:
            folder_stats = {
                'path': config.path,
                'exists': Path(config.path).exists(),
                'patterns': config.patterns,
                'recursive': config.recursive,
                'event_types': [e.value for e in config.event_types]
            }
            
            # Count files matching patterns
            if Path(config.path).exists():
                matching_files = 0
                path = Path(config.path)
                
                if config.recursive:
                    for pattern in config.patterns:
                        matching_files += len(list(path.rglob(pattern)))
                else:
                    for pattern in config.patterns:
                        matching_files += len(list(path.glob(pattern)))
                
                folder_stats['matching_files'] = matching_files
            
            stats['folders'].append(folder_stats)
        
        return stats
    
    def update_folder_config(
        self,
        schedule_id: str,
        folder_index: int,
        new_config: FolderWatchConfig
    ) -> bool:
        """Update configuration for a specific folder in a schedule."""
        with self._lock:
            if schedule_id not in self._folder_configs:
                return False
            
            configs = self._folder_configs[schedule_id]
            if folder_index >= len(configs):
                return False
            
            # Update configuration
            old_config = configs[folder_index]
            configs[folder_index] = new_config
            
            # Restart watcher if path changed
            if old_config.path != new_config.path:
                # Remove old schedule and re-add
                self.remove_schedule(schedule_id)
                
                # Re-add with updated config
                schedule = self._schedules.get(schedule_id)
                if schedule and isinstance(schedule, MultiFolderSchedule):
                    schedule.folder_configs = configs
                    return self.add_multi_folder_schedule(schedule)
        
        return True
    
    def add_folder_to_schedule(
        self,
        schedule_id: str,
        folder_config: FolderWatchConfig
    ) -> bool:
        """Add a new folder to an existing multi-folder schedule."""
        with self._lock:
            schedule = self._schedules.get(schedule_id)
            if not schedule or not isinstance(schedule, MultiFolderSchedule):
                return False
            
            # Add to configurations
            schedule.folder_configs.append(folder_config)
            self._folder_configs[schedule_id].append(folder_config)
            
            # Add watcher for new folder
            if self._observer and Path(folder_config.path).exists():
                handler = MultiFolderEventHandler(
                    schedule_id=schedule_id,
                    folder_config=folder_config,
                    callback=self._handle_multi_folder_event,
                    dedup_check=self._is_duplicate_event if schedule.cross_folder_dedup else None
                )
                
                watch = self._observer.schedule(
                    handler,
                    folder_config.path,
                    recursive=folder_config.recursive
                )
                
                self._watches[schedule_id].append(watch)
                
                logger.info(f"Added folder {folder_config.path} to schedule {schedule.name}")
                return True
        
        return False
    
    def remove_folder_from_schedule(
        self,
        schedule_id: str,
        folder_path: str
    ) -> bool:
        """Remove a folder from a multi-folder schedule."""
        with self._lock:
            schedule = self._schedules.get(schedule_id)
            if not schedule or not isinstance(schedule, MultiFolderSchedule):
                return False
            
            # Find and remove configuration
            configs = self._folder_configs[schedule_id]
            config_to_remove = None
            
            for i, config in enumerate(configs):
                if config.path == folder_path:
                    config_to_remove = i
                    break
            
            if config_to_remove is None:
                return False
            
            # Remove configuration
            configs.pop(config_to_remove)
            schedule.folder_configs.pop(config_to_remove)
            
            # Update path mapping
            if folder_path in self._path_to_schedule:
                self._path_to_schedule[folder_path].discard(schedule_id)
                if not self._path_to_schedule[folder_path]:
                    del self._path_to_schedule[folder_path]
            
            # Restart watcher to apply changes
            self.remove_schedule(schedule_id)
            if configs:  # If there are still folders to watch
                return self.add_multi_folder_schedule(schedule)
            
            return True


class MultiFolderEventHandler(ScheduleEventHandler):
    """Extended event handler for multi-folder support."""
    
    def __init__(
        self,
        schedule_id: str,
        folder_config: FolderWatchConfig,
        callback,
        dedup_check=None
    ):
        """Initialize multi-folder event handler."""
        super().__init__(
            schedule_id=schedule_id,
            patterns=folder_config.patterns,
            event_types=folder_config.event_types,
            callback=self._wrapped_callback
        )
        
        self.folder_config = folder_config
        self._multi_callback = callback
        self._dedup_check = dedup_check
    
    def _wrapped_callback(self, event: FileEvent, schedule_id: str):
        """Wrap callback to include folder config."""
        self._multi_callback(event, schedule_id, self.folder_config)