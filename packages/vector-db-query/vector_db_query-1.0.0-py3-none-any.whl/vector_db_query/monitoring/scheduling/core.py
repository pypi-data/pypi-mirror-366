"""
Core scheduling service implementation.
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Set
from concurrent.futures import ThreadPoolExecutor, Future

from .models import (
    Schedule, ScheduleType, ScheduleStatus, TaskResult, TaskStatus,
    SchedulerStats, ScheduleEvent, FileEvent
)
from .cron_scheduler import CronScheduler
from .file_watcher import FileWatcher
from .task_executor import TaskExecutor
from .schedule_manager import ScheduleManager

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Enterprise-grade scheduling service for automated document processing.
    
    Features:
    - Cron-based scheduling
    - File system event triggers
    - Multi-folder support with independent schedules
    - Task queuing and execution
    - Event emission for real-time updates
    """
    
    def __init__(
        self,
        max_concurrent_tasks: int = 5,
        storage_path: Optional[str] = None,
        event_callback: Optional[Callable[[ScheduleEvent], None]] = None
    ):
        """
        Initialize the scheduler service.
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent task executions
            storage_path: Path to store schedule configurations
            event_callback: Callback function for scheduler events
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.storage_path = Path(storage_path or "data/schedules")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Event handling
        self.event_callback = event_callback
        self.event_listeners: List[Callable[[ScheduleEvent], None]] = []
        
        # Core components
        self.schedule_manager = ScheduleManager(self.storage_path)
        self.cron_scheduler = CronScheduler()
        self.file_watcher = FileWatcher()
        self.task_executor = TaskExecutor(max_workers=max_concurrent_tasks)
        
        # State management
        self._running = False
        self._start_time: Optional[datetime] = None
        self._stats = SchedulerStats()
        self._active_tasks: Dict[str, Future] = {}
        self._task_queue: asyncio.Queue = asyncio.Queue()
        
        # Threading
        self._scheduler_thread: Optional[threading.Thread] = None
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self._lock = threading.RLock()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        logger.info(f"SchedulerService initialized with max_concurrent_tasks={max_concurrent_tasks}")
    
    def _setup_event_handlers(self):
        """Setup internal event handlers."""
        # File watcher events
        self.file_watcher.on_event = self._handle_file_event
        
        # Task executor events
        self.task_executor.on_task_started = self._handle_task_started
        self.task_executor.on_task_completed = self._handle_task_completed
        self.task_executor.on_task_failed = self._handle_task_failed
    
    def start(self) -> None:
        """Start the scheduler service."""
        if self._running:
            logger.warning("Scheduler service is already running")
            return
        
        logger.info("Starting scheduler service...")
        
        with self._lock:
            self._running = True
            self._start_time = datetime.now()
            
            # Load existing schedules
            self.schedule_manager.load_schedules()
            
            # Start components
            self.cron_scheduler.start()
            self.file_watcher.start()
            self.task_executor.start()
            
            # Start scheduler thread
            self._scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                name="SchedulerService",
                daemon=True
            )
            self._scheduler_thread.start()
            
            # Setup active schedules
            self._setup_active_schedules()
            
            # Emit start event
            self._emit_event(ScheduleEvent(
                event_type="scheduler_started",
                data={"timestamp": datetime.now().isoformat()}
            ))
        
        logger.info("Scheduler service started successfully")
    
    def stop(self) -> None:
        """Stop the scheduler service."""
        if not self._running:
            logger.warning("Scheduler service is not running")
            return
        
        logger.info("Stopping scheduler service...")
        
        with self._lock:
            self._running = False
            
            # Stop components
            self.cron_scheduler.stop()
            self.file_watcher.stop()
            self.task_executor.stop()
            
            # Cancel active tasks
            for task_id, future in self._active_tasks.items():
                if not future.done():
                    future.cancel()
                    logger.info(f"Cancelled task {task_id}")
            
            self._active_tasks.clear()
            
            # Shutdown executor
            self._executor.shutdown(wait=True)
            
            # Save schedules
            self.schedule_manager.save_schedules()
            
            # Emit stop event
            self._emit_event(ScheduleEvent(
                event_type="scheduler_stopped",
                data={"timestamp": datetime.now().isoformat()}
            ))
        
        logger.info("Scheduler service stopped successfully")
    
    def add_schedule(self, schedule: Schedule) -> None:
        """Add a new schedule."""
        logger.info(f"Adding schedule: {schedule.name} ({schedule.schedule_type.value})")
        
        # Validate schedule
        self._validate_schedule(schedule)
        
        # Add to manager
        self.schedule_manager.add_schedule(schedule)
        
        # Setup if active
        if schedule.status == ScheduleStatus.ACTIVE and self._running:
            self._setup_schedule(schedule)
        
        # Update stats
        self._update_stats()
        
        # Emit event
        self._emit_event(ScheduleEvent(
            event_type="schedule_added",
            schedule_id=schedule.id,
            data=schedule.to_dict()
        ))
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """Remove a schedule."""
        schedule = self.schedule_manager.get_schedule(schedule_id)
        if not schedule:
            return False
        
        logger.info(f"Removing schedule: {schedule.name}")
        
        # Remove from components
        self._teardown_schedule(schedule)
        
        # Remove from manager
        result = self.schedule_manager.remove_schedule(schedule_id)
        
        # Update stats
        self._update_stats()
        
        # Emit event
        self._emit_event(ScheduleEvent(
            event_type="schedule_removed",
            schedule_id=schedule_id,
            data={"name": schedule.name}
        ))
        
        return result
    
    def update_schedule(self, schedule: Schedule) -> None:
        """Update an existing schedule."""
        logger.info(f"Updating schedule: {schedule.name}")
        
        # Validate schedule
        self._validate_schedule(schedule)
        
        # Get old schedule for comparison
        old_schedule = self.schedule_manager.get_schedule(schedule.id)
        
        # Update in manager
        schedule.updated_at = datetime.now()
        self.schedule_manager.update_schedule(schedule)
        
        # Reconfigure if needed
        if old_schedule and self._running:
            self._teardown_schedule(old_schedule)
            if schedule.status == ScheduleStatus.ACTIVE:
                self._setup_schedule(schedule)
        
        # Update stats
        self._update_stats()
        
        # Emit event
        self._emit_event(ScheduleEvent(
            event_type="schedule_updated",
            schedule_id=schedule.id,
            data=schedule.to_dict()
        ))
    
    def pause_schedule(self, schedule_id: str) -> bool:
        """Pause a schedule."""
        schedule = self.schedule_manager.get_schedule(schedule_id)
        if not schedule:
            return False
        
        schedule.status = ScheduleStatus.PAUSED
        self.update_schedule(schedule)
        
        logger.info(f"Paused schedule: {schedule.name}")
        return True
    
    def resume_schedule(self, schedule_id: str) -> bool:
        """Resume a paused schedule."""
        schedule = self.schedule_manager.get_schedule(schedule_id)
        if not schedule:
            return False
        
        schedule.status = ScheduleStatus.ACTIVE
        self.update_schedule(schedule)
        
        logger.info(f"Resumed schedule: {schedule.name}")
        return True
    
    def trigger_schedule(self, schedule_id: str, manual: bool = True) -> Optional[str]:
        """Manually trigger a schedule execution."""
        schedule = self.schedule_manager.get_schedule(schedule_id)
        if not schedule:
            return None
        
        logger.info(f"Manually triggering schedule: {schedule.name}")
        
        # Create task result
        task_result = TaskResult(
            schedule_id=schedule.id,
            task_name=schedule.task_name,
            triggered_by="manual" if manual else "scheduler",
            trigger_details={"manual_trigger": manual}
        )
        
        # Execute task
        task_id = self._execute_task(schedule, task_result)
        
        return task_id
    
    def get_schedules(self) -> List[Schedule]:
        """Get all schedules."""
        return self.schedule_manager.get_all_schedules()
    
    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Get a specific schedule."""
        return self.schedule_manager.get_schedule(schedule_id)
    
    def get_stats(self) -> SchedulerStats:
        """Get scheduler statistics."""
        self._update_stats()
        return self._stats
    
    def add_event_listener(self, callback: Callable[[ScheduleEvent], None]) -> None:
        """Add an event listener."""
        self.event_listeners.append(callback)
    
    def remove_event_listener(self, callback: Callable[[ScheduleEvent], None]) -> None:
        """Remove an event listener."""
        if callback in self.event_listeners:
            self.event_listeners.remove(callback)
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        logger.info("Scheduler loop started")
        
        while self._running:
            try:
                # Check cron schedules
                due_schedules = self.cron_scheduler.get_due_schedules()
                for schedule_id in due_schedules:
                    schedule = self.schedule_manager.get_schedule(schedule_id)
                    if schedule and schedule.status == ScheduleStatus.ACTIVE:
                        self._trigger_schedule_execution(schedule, "cron")
                
                # Process task queue (if using async tasks)
                # This can be expanded for more complex task queuing
                
                # Sleep for a short interval
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(5)  # Longer sleep on error
        
        logger.info("Scheduler loop stopped")
    
    def _setup_active_schedules(self):
        """Setup all active schedules."""
        for schedule in self.schedule_manager.get_all_schedules():
            if schedule.status == ScheduleStatus.ACTIVE:
                self._setup_schedule(schedule)
    
    def _setup_schedule(self, schedule: Schedule):
        """Setup a single schedule."""
        try:
            if schedule.schedule_type == ScheduleType.CRON:
                self.cron_scheduler.add_schedule(schedule)
            
            elif schedule.schedule_type == ScheduleType.FILE_EVENT:
                if schedule.watch_path:
                    self.file_watcher.add_watch(
                        path=schedule.watch_path,
                        schedule_id=schedule.id,
                        patterns=schedule.file_patterns,
                        event_types=schedule.event_types,
                        recursive=schedule.recursive
                    )
            
            logger.debug(f"Setup completed for schedule: {schedule.name}")
            
        except Exception as e:
            logger.error(f"Failed to setup schedule {schedule.name}: {str(e)}")
            schedule.status = ScheduleStatus.ERROR
            self.schedule_manager.update_schedule(schedule)
    
    def _teardown_schedule(self, schedule: Schedule):
        """Teardown a schedule."""
        try:
            if schedule.schedule_type == ScheduleType.CRON:
                self.cron_scheduler.remove_schedule(schedule.id)
            
            elif schedule.schedule_type == ScheduleType.FILE_EVENT:
                self.file_watcher.remove_watch(schedule.id)
            
            logger.debug(f"Teardown completed for schedule: {schedule.name}")
            
        except Exception as e:
            logger.error(f"Failed to teardown schedule {schedule.name}: {str(e)}")
    
    def _validate_schedule(self, schedule: Schedule):
        """Validate a schedule configuration."""
        if not schedule.name:
            raise ValueError("Schedule name is required")
        
        if schedule.schedule_type == ScheduleType.CRON:
            if not schedule.cron_expression:
                raise ValueError("Cron expression is required for cron schedules")
        
        elif schedule.schedule_type == ScheduleType.FILE_EVENT:
            if not schedule.watch_path:
                raise ValueError("Watch path is required for file event schedules")
            
            if not Path(schedule.watch_path).exists():
                raise ValueError(f"Watch path does not exist: {schedule.watch_path}")
        
        elif schedule.schedule_type == ScheduleType.INTERVAL:
            if not schedule.interval_seconds or schedule.interval_seconds <= 0:
                raise ValueError("Valid interval_seconds is required for interval schedules")
        
        elif schedule.schedule_type == ScheduleType.ONE_TIME:
            if not schedule.run_at:
                raise ValueError("run_at is required for one-time schedules")
    
    def _trigger_schedule_execution(self, schedule: Schedule, trigger_source: str):
        """Trigger execution of a schedule."""
        # Check concurrent task limit
        if len(self._active_tasks) >= self.max_concurrent_tasks:
            logger.warning(f"Max concurrent tasks reached, skipping schedule: {schedule.name}")
            return
        
        # Create task result
        task_result = TaskResult(
            schedule_id=schedule.id,
            task_name=schedule.task_name,
            triggered_by=trigger_source
        )
        
        # Execute task
        self._execute_task(schedule, task_result)
    
    def _execute_task(self, schedule: Schedule, task_result: TaskResult) -> str:
        """Execute a task asynchronously."""
        # Submit task to executor
        future = self._executor.submit(
            self.task_executor.execute_task,
            schedule,
            task_result
        )
        
        # Track active task
        self._active_tasks[task_result.task_id] = future
        
        # Add completion callback
        future.add_done_callback(
            lambda f: self._task_completed_callback(task_result.task_id, f)
        )
        
        logger.info(f"Task {task_result.task_id} submitted for schedule: {schedule.name}")
        
        return task_result.task_id
    
    def _task_completed_callback(self, task_id: str, future: Future):
        """Callback when a task completes."""
        with self._lock:
            if task_id in self._active_tasks:
                del self._active_tasks[task_id]
        
        try:
            result = future.result()
            logger.info(f"Task {task_id} completed successfully")
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
    
    def _handle_file_event(self, event: FileEvent, schedule_id: str):
        """Handle file system events."""
        schedule = self.schedule_manager.get_schedule(schedule_id)
        if not schedule or schedule.status != ScheduleStatus.ACTIVE:
            return
        
        logger.info(f"File event detected for schedule {schedule.name}: {event.file_path}")
        
        # Create task result with file event details
        task_result = TaskResult(
            schedule_id=schedule.id,
            task_name=schedule.task_name,
            triggered_by="file_event",
            trigger_details={
                "event_type": event.event_type.value,
                "file_path": event.file_path,
                "timestamp": event.timestamp.isoformat()
            }
        )
        
        # Execute task
        self._execute_task(schedule, task_result)
    
    def _handle_task_started(self, task_result: TaskResult):
        """Handle task started event."""
        self._emit_event(ScheduleEvent(
            event_type="task_started",
            schedule_id=task_result.schedule_id,
            task_id=task_result.task_id,
            data=task_result.to_dict()
        ))
    
    def _handle_task_completed(self, task_result: TaskResult):
        """Handle task completed event."""
        # Update schedule statistics
        schedule = self.schedule_manager.get_schedule(task_result.schedule_id)
        if schedule:
            schedule.run_count += 1
            schedule.last_run_at = datetime.now()
            if task_result.success:
                schedule.success_count += 1
            else:
                schedule.failure_count += 1
            
            self.schedule_manager.update_schedule(schedule)
        
        # Emit event
        self._emit_event(ScheduleEvent(
            event_type="task_completed",
            schedule_id=task_result.schedule_id,
            task_id=task_result.task_id,
            data=task_result.to_dict()
        ))
    
    def _handle_task_failed(self, task_result: TaskResult):
        """Handle task failed event."""
        # Update schedule statistics
        schedule = self.schedule_manager.get_schedule(task_result.schedule_id)
        if schedule:
            schedule.run_count += 1
            schedule.failure_count += 1
            schedule.last_run_at = datetime.now()
            
            self.schedule_manager.update_schedule(schedule)
        
        # Emit event
        self._emit_event(ScheduleEvent(
            event_type="task_failed",
            schedule_id=task_result.schedule_id,
            task_id=task_result.task_id,
            data=task_result.to_dict()
        ))
    
    def _update_stats(self):
        """Update scheduler statistics."""
        schedules = self.schedule_manager.get_all_schedules()
        
        self._stats.total_schedules = len(schedules)
        self._stats.active_schedules = sum(1 for s in schedules if s.status == ScheduleStatus.ACTIVE)
        self._stats.paused_schedules = sum(1 for s in schedules if s.status == ScheduleStatus.PAUSED)
        
        self._stats.running_tasks = len(self._active_tasks)
        
        # Calculate uptime
        if self._start_time:
            self._stats.uptime_seconds = (datetime.now() - self._start_time).total_seconds()
        
        # Aggregate execution stats
        total_executions = sum(s.run_count for s in schedules)
        successful_executions = sum(s.success_count for s in schedules)
        failed_executions = sum(s.failure_count for s in schedules)
        
        self._stats.total_executions = total_executions
        self._stats.successful_executions = successful_executions
        self._stats.failed_executions = failed_executions
        
        # Find last execution
        last_runs = [s.last_run_at for s in schedules if s.last_run_at]
        if last_runs:
            self._stats.last_execution = max(last_runs)
    
    def _emit_event(self, event: ScheduleEvent):
        """Emit an event to listeners."""
        try:
            # Call main callback
            if self.event_callback:
                self.event_callback(event)
            
            # Call additional listeners
            for callback in self.event_listeners:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event listener: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error emitting event: {str(e)}")
    
    @property
    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self._running
    
    @property
    def uptime(self) -> timedelta:
        """Get scheduler uptime."""
        if self._start_time:
            return datetime.now() - self._start_time
        return timedelta()