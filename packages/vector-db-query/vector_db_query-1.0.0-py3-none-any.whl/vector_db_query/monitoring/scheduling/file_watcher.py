"""
File system event watcher implementation using watchdog.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Set
from threading import RLock

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

from .models import FileEvent, EventType

logger = logging.getLogger(__name__)


class ScheduleEventHandler(FileSystemEventHandler):
    """Event handler for file system events tied to schedules."""
    
    def __init__(
        self,
        schedule_id: str,
        patterns: List[str],
        event_types: List[EventType],
        callback: Callable[[FileEvent, str], None]
    ):
        """
        Initialize event handler.
        
        Args:
            schedule_id: ID of the schedule this handler serves
            patterns: File patterns to match
            event_types: Event types to monitor
            callback: Callback function for events
        """
        super().__init__()
        self.schedule_id = schedule_id
        self.patterns = patterns or []
        self.event_types = event_types or []
        self.callback = callback
        
        # Convert EventType enums to sets for quick lookup
        self.event_type_set = {event_type for event_type in self.event_types}
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if EventType.CREATED in self.event_type_set:
            self._handle_event(event, EventType.CREATED)
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if EventType.MODIFIED in self.event_type_set:
            self._handle_event(event, EventType.MODIFIED)
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events."""
        if EventType.DELETED in self.event_type_set:
            self._handle_event(event, EventType.DELETED)
    
    def on_moved(self, event: FileSystemEvent):
        """Handle file move events."""
        if EventType.MOVED in self.event_type_set:
            self._handle_event(event, EventType.MOVED)
    
    def _handle_event(self, event: FileSystemEvent, event_type: EventType):
        """Process a file system event."""
        # Skip directory events for now (can be configurable later)
        if event.is_directory:
            return
        
        # Create FileEvent object
        file_event = FileEvent(
            event_type=event_type,
            file_path=event.src_path,
            timestamp=datetime.now(),
            is_directory=event.is_directory
        )
        
        # Add destination path for move events
        if hasattr(event, 'dest_path'):
            file_event.dest_path = event.dest_path
        
        # Check if file matches patterns
        if self.patterns and not file_event.matches_pattern(self.patterns):
            logger.debug(f"File {file_event.file_path} does not match patterns {self.patterns}")
            return
        
        logger.info(f"File event detected: {event_type.value} - {file_event.file_path}")
        
        try:
            self.callback(file_event, self.schedule_id)
        except Exception as e:
            logger.error(f"Error in file event callback: {str(e)}")


class FallbackWatcher:
    """Fallback file watcher using polling when watchdog is not available."""
    
    def __init__(self, check_interval: int = 5):
        """
        Initialize fallback watcher.
        
        Args:
            check_interval: Polling interval in seconds
        """
        self.check_interval = check_interval
        self.watches: Dict[str, Dict] = {}
        self.file_states: Dict[str, Dict[str, float]] = {}  # path -> {file: mtime}
        self._running = False
        self._lock = RLock()
    
    def add_watch(
        self,
        path: str,
        schedule_id: str,
        patterns: List[str],
        event_types: List[EventType],
        recursive: bool,
        callback: Callable[[FileEvent, str], None]
    ):
        """Add a directory watch."""
        with self._lock:
            self.watches[schedule_id] = {
                'path': path,
                'patterns': patterns,
                'event_types': event_types,
                'recursive': recursive,
                'callback': callback
            }
            
            # Initialize file state
            self._update_file_state(path, schedule_id, recursive)
    
    def remove_watch(self, schedule_id: str):
        """Remove a directory watch."""
        with self._lock:
            if schedule_id in self.watches:
                del self.watches[schedule_id]
            if schedule_id in self.file_states:
                del self.file_states[schedule_id]
    
    def start(self):
        """Start the fallback watcher."""
        self._running = True
        logger.info("FallbackWatcher started (polling mode)")
    
    def stop(self):
        """Stop the fallback watcher."""
        self._running = False
        logger.info("FallbackWatcher stopped")
    
    def check_changes(self):
        """Check for file changes (called by main loop)."""
        if not self._running:
            return
        
        with self._lock:
            for schedule_id, watch in self.watches.items():
                try:
                    self._check_watch_changes(schedule_id, watch)
                except Exception as e:
                    logger.error(f"Error checking changes for watch {schedule_id}: {str(e)}")
    
    def _check_watch_changes(self, schedule_id: str, watch: Dict):
        """Check changes for a specific watch."""
        path = Path(watch['path'])
        if not path.exists():
            return
        
        recursive = watch['recursive']
        patterns = watch['patterns']
        event_types = watch['event_types']
        callback = watch['callback']
        
        # Get current file states
        current_states = {}
        self._scan_directory(path, current_states, recursive)
        
        # Compare with previous states
        previous_states = self.file_states.get(schedule_id, {})
        
        # Check for new/modified files
        for file_path, mtime in current_states.items():
            if file_path not in previous_states:
                # New file
                if EventType.CREATED in event_types:
                    file_event = FileEvent(
                        event_type=EventType.CREATED,
                        file_path=file_path,
                        timestamp=datetime.now()
                    )
                    if not patterns or file_event.matches_pattern(patterns):
                        callback(file_event, schedule_id)
            
            elif mtime > previous_states[file_path]:
                # Modified file
                if EventType.MODIFIED in event_types:
                    file_event = FileEvent(
                        event_type=EventType.MODIFIED,
                        file_path=file_path,
                        timestamp=datetime.now()
                    )
                    if not patterns or file_event.matches_pattern(patterns):
                        callback(file_event, schedule_id)
        
        # Check for deleted files
        if EventType.DELETED in event_types:
            for file_path in previous_states:
                if file_path not in current_states:
                    file_event = FileEvent(
                        event_type=EventType.DELETED,
                        file_path=file_path,
                        timestamp=datetime.now()
                    )
                    if not patterns or file_event.matches_pattern(patterns):
                        callback(file_event, schedule_id)
        
        # Update stored states
        self.file_states[schedule_id] = current_states
    
    def _update_file_state(self, path: str, schedule_id: str, recursive: bool):
        """Update file state for a path."""
        current_states = {}
        self._scan_directory(Path(path), current_states, recursive)
        self.file_states[schedule_id] = current_states
    
    def _scan_directory(self, path: Path, states: Dict[str, float], recursive: bool):
        """Scan directory and collect file modification times."""
        try:
            if path.is_file():
                states[str(path)] = path.stat().st_mtime
                return
            
            if path.is_dir():
                for item in path.iterdir():
                    if item.is_file():
                        states[str(item)] = item.stat().st_mtime
                    elif item.is_dir() and recursive:
                        self._scan_directory(item, states, recursive)
        
        except (OSError, IOError) as e:
            logger.warning(f"Error scanning {path}: {str(e)}")


class FileWatcher:
    """
    File system event watcher using watchdog or fallback polling.
    
    Monitors file system events and triggers schedule executions.
    """
    
    def __init__(self, check_interval: int = 5):
        """
        Initialize file watcher.
        
        Args:
            check_interval: Polling interval for fallback mode
        """
        self.check_interval = check_interval
        self._lock = RLock()
        self._running = False
        
        # Event callback
        self.on_event: Optional[Callable[[FileEvent, str], None]] = None
        
        if WATCHDOG_AVAILABLE:
            self._observer = Observer()
            self._handlers: Dict[str, ScheduleEventHandler] = {}
            self._watches: Dict[str, Any] = {}  # schedule_id -> watch descriptor
            logger.info("FileWatcher initialized with watchdog support")
        else:
            self._observer = None
            self._fallback_watcher = FallbackWatcher(check_interval)
            logger.warning("Watchdog not available. Using fallback polling file watcher.")
    
    def start(self) -> None:
        """Start the file watcher."""
        if self._running:
            logger.warning("FileWatcher is already running")
            return
        
        with self._lock:
            self._running = True
            
            if self._observer:
                self._observer.start()
                logger.info("Watchdog observer started")
            else:
                self._fallback_watcher.start()
                # Note: fallback watcher needs external polling loop
        
        logger.info("FileWatcher started successfully")
    
    def stop(self) -> None:
        """Stop the file watcher."""
        if not self._running:
            logger.warning("FileWatcher is not running")
            return
        
        with self._lock:
            self._running = False
            
            if self._observer:
                self._observer.stop()
                self._observer.join()
                self._handlers.clear()
                self._watches.clear()
                logger.info("Watchdog observer stopped")
            else:
                self._fallback_watcher.stop()
        
        logger.info("FileWatcher stopped successfully")
    
    def add_watch(
        self,
        path: str,
        schedule_id: str,
        patterns: Optional[List[str]] = None,
        event_types: Optional[List[EventType]] = None,
        recursive: bool = True
    ) -> bool:
        """
        Add a directory watch for a schedule.
        
        Args:
            path: Directory path to watch
            schedule_id: Schedule ID
            patterns: File patterns to match (glob style)
            event_types: Event types to monitor
            recursive: Watch subdirectories
            
        Returns:
            True if watch added successfully
        """
        if not Path(path).exists():
            logger.error(f"Watch path does not exist: {path}")
            return False
        
        patterns = patterns or []
        event_types = event_types or [EventType.CREATED, EventType.MODIFIED]
        
        with self._lock:
            if self._observer:
                try:
                    # Create event handler
                    handler = ScheduleEventHandler(
                        schedule_id=schedule_id,
                        patterns=patterns,
                        event_types=event_types,
                        callback=self._handle_file_event
                    )
                    
                    # Add watch
                    watch = self._observer.schedule(
                        event_handler=handler,
                        path=path,
                        recursive=recursive
                    )
                    
                    # Store references
                    self._handlers[schedule_id] = handler
                    self._watches[schedule_id] = watch
                    
                    logger.info(f"Added watchdog watch for schedule {schedule_id}: {path}")
                    
                except Exception as e:
                    logger.error(f"Failed to add watchdog watch: {str(e)}")
                    return False
            
            else:
                # Fallback watcher
                try:
                    self._fallback_watcher.add_watch(
                        path=path,
                        schedule_id=schedule_id,
                        patterns=patterns,
                        event_types=event_types,
                        recursive=recursive,
                        callback=self._handle_file_event
                    )
                    
                    logger.info(f"Added fallback watch for schedule {schedule_id}: {path}")
                    
                except Exception as e:
                    logger.error(f"Failed to add fallback watch: {str(e)}")
                    return False
        
        return True
    
    def remove_watch(self, schedule_id: str) -> bool:
        """
        Remove a directory watch.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            True if watch removed successfully
        """
        with self._lock:
            if self._observer:
                if schedule_id in self._watches:
                    try:
                        watch = self._watches[schedule_id]
                        self._observer.unschedule(watch)
                        
                        del self._watches[schedule_id]
                        del self._handlers[schedule_id]
                        
                        logger.info(f"Removed watchdog watch for schedule {schedule_id}")
                        return True
                    
                    except Exception as e:
                        logger.error(f"Failed to remove watchdog watch: {str(e)}")
                        return False
            
            else:
                # Fallback watcher
                try:
                    self._fallback_watcher.remove_watch(schedule_id)
                    logger.info(f"Removed fallback watch for schedule {schedule_id}")
                    return True
                
                except Exception as e:
                    logger.error(f"Failed to remove fallback watch: {str(e)}")
                    return False
        
        return False
    
    def check_changes(self):
        """Check for changes (used by fallback watcher)."""
        if not self._observer and self._running:
            self._fallback_watcher.check_changes()
    
    def _handle_file_event(self, event: FileEvent, schedule_id: str):
        """Handle file system events."""
        logger.debug(f"File event for schedule {schedule_id}: {event.event_type.value} - {event.file_path}")
        
        if self.on_event:
            try:
                self.on_event(event, schedule_id)
            except Exception as e:
                logger.error(f"Error in file event callback: {str(e)}")
    
    @property
    def is_running(self) -> bool:
        """Check if the watcher is running."""
        return self._running
    
    @property
    def watch_count(self) -> int:
        """Get the number of active watches."""
        with self._lock:
            if self._observer:
                return len(self._watches)
            else:
                return len(self._fallback_watcher.watches)
    
    def get_watch_info(self, schedule_id: str) -> Optional[Dict]:
        """Get information about a watch."""
        with self._lock:
            if self._observer:
                if schedule_id in self._handlers:
                    handler = self._handlers[schedule_id]
                    return {
                        'schedule_id': schedule_id,
                        'patterns': handler.patterns,
                        'event_types': [et.value for et in handler.event_types],
                        'backend': 'watchdog'
                    }
            else:
                if schedule_id in self._fallback_watcher.watches:
                    watch = self._fallback_watcher.watches[schedule_id]
                    return {
                        'schedule_id': schedule_id,
                        'path': watch['path'],
                        'patterns': watch['patterns'],
                        'event_types': [et.value for et in watch['event_types']],
                        'recursive': watch['recursive'],
                        'backend': 'polling'
                    }
        
        return None