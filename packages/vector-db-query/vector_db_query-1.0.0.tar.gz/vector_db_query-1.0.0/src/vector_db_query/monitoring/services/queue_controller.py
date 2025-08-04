"""
Queue pause/resume controller for monitoring dashboard.

This module provides functionality to pause and resume queue processing
without stopping services entirely, enabling maintenance and flow control.
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock, Event, Thread
import time

from .parameter_manager import get_parameter_manager
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class QueueState(Enum):
    """Queue processing states."""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    DRAINING = "draining"  # Finishing current tasks before pause
    RESUMING = "resuming"


class PauseMode(Enum):
    """Different pause modes available."""
    IMMEDIATE = "immediate"     # Stop processing immediately
    GRACEFUL = "graceful"       # Finish current tasks then pause
    SCHEDULED = "scheduled"     # Pause at specific time
    DRAIN = "drain"             # Process all queued items then pause


@dataclass
class QueueMetrics:
    """Queue processing metrics."""
    items_processed: int = 0
    items_pending: int = 0
    items_in_progress: int = 0
    items_failed: int = 0
    processing_rate: float = 0.0  # items per second
    average_processing_time: float = 0.0  # seconds
    last_activity: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'items_processed': self.items_processed,
            'items_pending': self.items_pending,
            'items_in_progress': self.items_in_progress,
            'items_failed': self.items_failed,
            'processing_rate': self.processing_rate,
            'average_processing_time': self.average_processing_time,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }


@dataclass
class PauseSchedule:
    """Scheduled pause configuration."""
    id: str
    name: str
    pause_time: datetime
    resume_time: Optional[datetime] = None
    mode: PauseMode = PauseMode.GRACEFUL
    reason: str = ""
    recurring: bool = False
    enabled: bool = True
    created_by: Optional[str] = None
    
    def is_active(self) -> bool:
        """Check if schedule is currently active."""
        if not self.enabled:
            return False
        
        now = datetime.now()
        
        # Check if pause time has passed
        if now >= self.pause_time:
            # If no resume time, pause is indefinite
            if not self.resume_time:
                return True
            
            # Check if still within pause window
            return now < self.resume_time
        
        return False


class QueueController:
    """
    Queue controller with pause/resume capabilities.
    
    Provides granular control over queue processing including
    immediate pause, graceful shutdown, scheduled pauses, and
    metric tracking.
    """
    
    def __init__(self, queue_name: str = "default"):
        """
        Initialize queue controller.
        
        Args:
            queue_name: Name of the queue to control
        """
        self.queue_name = queue_name
        self._lock = RLock()
        
        # Queue state
        self._state = QueueState.STOPPED
        self._pause_reason = ""
        self._paused_at: Optional[datetime] = None
        self._resumed_at: Optional[datetime] = None
        
        # Processing control
        self._pause_event = Event()
        self._stop_event = Event()
        self._pause_event.set()  # Start unpaused
        
        # Metrics
        self._metrics = QueueMetrics()
        self._processing_times: List[float] = []
        self._max_timing_samples = 100
        
        # Scheduled pauses
        self._pause_schedules: Dict[str, PauseSchedule] = {}
        
        # Worker threads
        self._workers: Set[Thread] = set()
        self._max_workers = 5
        
        # Integration
        self._param_manager = get_parameter_manager()
        self._change_tracker = get_change_tracker()
        
        # Register parameters
        self._register_parameters()
        
        # Schedule checker thread
        self._schedule_checker = Thread(
            target=self._check_schedules,
            daemon=True,
            name=f"schedule-checker-{queue_name}"
        )
        self._schedule_checker.start()
        
        logger.info(f"QueueController initialized for queue: {queue_name}")
    
    def _register_parameters(self):
        """Register queue-specific parameters."""
        from .parameter_manager import ParameterDefinition, ParameterType, ParameterScope
        
        # Max workers parameter
        self._param_manager.register_parameter(
            service_id=f"queue_{self.queue_name}",
            parameter=ParameterDefinition(
                name="max_workers",
                type=ParameterType.INTEGER,
                description="Maximum number of worker threads",
                default_value=5,
                current_value=5,
                min_value=1,
                max_value=20,
                category="performance"
            )
        )
        
        # Batch size parameter
        self._param_manager.register_parameter(
            service_id=f"queue_{self.queue_name}",
            parameter=ParameterDefinition(
                name="batch_size",
                type=ParameterType.INTEGER,
                description="Number of items to process in each batch",
                default_value=10,
                current_value=10,
                min_value=1,
                max_value=100,
                category="performance"
            )
        )
        
        # Processing interval parameter
        self._param_manager.register_parameter(
            service_id=f"queue_{self.queue_name}",
            parameter=ParameterDefinition(
                name="processing_interval",
                type=ParameterType.FLOAT,
                description="Seconds between processing cycles",
                default_value=1.0,
                current_value=1.0,
                min_value=0.1,
                max_value=60.0,
                category="performance"
            )
        )
    
    def start(self) -> bool:
        """Start queue processing."""
        with self._lock:
            if self._state == QueueState.RUNNING:
                logger.warning(f"Queue {self.queue_name} is already running")
                return True
            
            self._state = QueueState.RUNNING
            self._stop_event.clear()
            self._pause_event.set()
            
            # Start worker threads
            max_workers = self._param_manager.get_value(
                f"queue_{self.queue_name}", "max_workers", self._max_workers
            )
            
            for i in range(max_workers):
                worker = Thread(
                    target=self._worker_loop,
                    daemon=True,
                    name=f"queue-worker-{self.queue_name}-{i}"
                )
                worker.start()
                self._workers.add(worker)
            
            # Track the change
            self._change_tracker.track_change(
                category=ChangeCategory.SERVICE,
                change_type=ChangeType.EXECUTED,
                entity_type="queue",
                entity_id=self.queue_name,
                entity_name=f"Queue {self.queue_name}",
                description=f"Queue processing started",
                details={'workers': max_workers}
            )
            
            logger.info(f"Started queue processing for {self.queue_name} with {max_workers} workers")
            return True
    
    def stop(self, graceful: bool = True) -> bool:
        """Stop queue processing."""
        with self._lock:
            if self._state == QueueState.STOPPED:
                logger.warning(f"Queue {self.queue_name} is already stopped")
                return True
            
            self._state = QueueState.STOPPING
            self._stop_event.set()
            
            if graceful:
                # Wait for workers to finish current tasks
                logger.info(f"Gracefully stopping queue {self.queue_name}...")
                
                # Wait for workers with timeout
                timeout = 30  # seconds
                start_time = time.time()
                
                for worker in self._workers:
                    remaining_time = timeout - (time.time() - start_time)
                    if remaining_time > 0:
                        worker.join(timeout=remaining_time)
            
            self._state = QueueState.STOPPED
            self._workers.clear()
            
            # Track the change
            self._change_tracker.track_change(
                category=ChangeCategory.SERVICE,
                change_type=ChangeType.EXECUTED,
                entity_type="queue",
                entity_id=self.queue_name,
                entity_name=f"Queue {self.queue_name}",
                description=f"Queue processing stopped ({'graceful' if graceful else 'immediate'})"
            )
            
            logger.info(f"Stopped queue processing for {self.queue_name}")
            return True
    
    def pause(self, mode: PauseMode = PauseMode.GRACEFUL, reason: str = "") -> bool:
        """Pause queue processing."""
        with self._lock:
            if self._state == QueueState.PAUSED:
                logger.warning(f"Queue {self.queue_name} is already paused")
                return True
            
            if self._state != QueueState.RUNNING:
                logger.error(f"Cannot pause queue {self.queue_name} - not running")
                return False
            
            self._pause_reason = reason
            self._paused_at = datetime.now()
            
            if mode == PauseMode.IMMEDIATE:
                self._state = QueueState.PAUSED
                self._pause_event.clear()
                
            elif mode == PauseMode.GRACEFUL:
                self._state = QueueState.DRAINING
                self._pause_event.clear()
                
                # Will transition to PAUSED when workers finish current tasks
                
            elif mode == PauseMode.DRAIN:
                self._state = QueueState.DRAINING
                self._pause_event.clear()
                
                # Workers will process all queued items then pause
            
            # Track the change
            self._change_tracker.track_change(
                category=ChangeCategory.SERVICE,
                change_type=ChangeType.EXECUTED,
                entity_type="queue",
                entity_id=self.queue_name,
                entity_name=f"Queue {self.queue_name}",
                description=f"Queue processing paused ({mode.value})",
                details={
                    'mode': mode.value,
                    'reason': reason,
                    'paused_at': self._paused_at.isoformat()
                }
            )
            
            logger.info(f"Paused queue {self.queue_name} with mode {mode.value}: {reason}")
            return True
    
    def resume(self, reason: str = "") -> bool:
        """Resume queue processing."""
        with self._lock:
            if self._state == QueueState.RUNNING:
                logger.warning(f"Queue {self.queue_name} is already running")
                return True
            
            if self._state not in [QueueState.PAUSED, QueueState.DRAINING]:
                logger.error(f"Cannot resume queue {self.queue_name} - not paused")
                return False
            
            self._state = QueueState.RESUMING
            self._resumed_at = datetime.now()
            
            # Calculate pause duration
            pause_duration = None
            if self._paused_at and self._resumed_at:
                pause_duration = (self._resumed_at - self._paused_at).total_seconds()
            
            # Resume processing
            self._pause_event.set()
            self._state = QueueState.RUNNING
            
            # Track the change
            self._change_tracker.track_change(
                category=ChangeCategory.SERVICE,
                change_type=ChangeType.EXECUTED,
                entity_type="queue",
                entity_id=self.queue_name,
                entity_name=f"Queue {self.queue_name}",
                description=f"Queue processing resumed",
                details={
                    'reason': reason,
                    'resumed_at': self._resumed_at.isoformat(),
                    'pause_duration_seconds': pause_duration,
                    'previous_pause_reason': self._pause_reason
                }
            )
            
            # Clear pause info
            self._pause_reason = ""
            self._paused_at = None
            
            logger.info(f"Resumed queue {self.queue_name}: {reason}")
            return True
    
    def schedule_pause(
        self,
        schedule: PauseSchedule
    ) -> bool:
        """Schedule a future pause."""
        with self._lock:
            self._pause_schedules[schedule.id] = schedule
            
            # Track the change
            self._change_tracker.track_change(
                category=ChangeCategory.CONFIGURATION,
                change_type=ChangeType.CREATED,
                entity_type="pause_schedule",
                entity_id=schedule.id,
                entity_name=schedule.name,
                description=f"Scheduled pause created for queue {self.queue_name}",
                details={
                    'pause_time': schedule.pause_time.isoformat(),
                    'resume_time': schedule.resume_time.isoformat() if schedule.resume_time else None,
                    'mode': schedule.mode.value,
                    'reason': schedule.reason,
                    'recurring': schedule.recurring
                }
            )
            
            logger.info(f"Scheduled pause {schedule.id} for queue {self.queue_name}")
            return True
    
    def cancel_scheduled_pause(self, schedule_id: str) -> bool:
        """Cancel a scheduled pause."""
        with self._lock:
            if schedule_id in self._pause_schedules:
                schedule = self._pause_schedules.pop(schedule_id)
                
                # Track the change
                self._change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.DELETED,
                    entity_type="pause_schedule",
                    entity_id=schedule_id,
                    entity_name=schedule.name,
                    description=f"Scheduled pause cancelled for queue {self.queue_name}"
                )
                
                logger.info(f"Cancelled scheduled pause {schedule_id} for queue {self.queue_name}")
                return True
            
            return False
    
    def get_state(self) -> Dict[str, Any]:
        """Get current queue state and metrics."""
        with self._lock:
            state_info = {
                'queue_name': self.queue_name,
                'state': self._state.value,
                'metrics': self._metrics.to_dict(),
                'pause_info': {
                    'reason': self._pause_reason,
                    'paused_at': self._paused_at.isoformat() if self._paused_at else None,
                    'pause_duration': (
                        (datetime.now() - self._paused_at).total_seconds()
                        if self._paused_at else None
                    )
                },
                'workers': {
                    'active': len([w for w in self._workers if w.is_alive()]),
                    'total': len(self._workers)
                },
                'scheduled_pauses': [
                    {
                        'id': s.id,
                        'name': s.name,
                        'pause_time': s.pause_time.isoformat(),
                        'resume_time': s.resume_time.isoformat() if s.resume_time else None,
                        'mode': s.mode.value,
                        'reason': s.reason,
                        'enabled': s.enabled,
                        'is_active': s.is_active()
                    }
                    for s in self._pause_schedules.values()
                ]
            }
            
            return state_info
    
    def get_metrics(self) -> QueueMetrics:
        """Get current queue metrics."""
        with self._lock:
            return self._metrics
    
    def _worker_loop(self):
        """Main worker loop for processing queue items."""
        worker_name = Thread.current_thread().name
        logger.debug(f"Worker {worker_name} started")
        
        while not self._stop_event.is_set():
            # Wait if paused
            self._pause_event.wait()
            
            # Check if we should stop
            if self._stop_event.is_set():
                break
            
            # Get processing parameters
            batch_size = self._param_manager.get_value(
                f"queue_{self.queue_name}", "batch_size", 10
            )
            processing_interval = self._param_manager.get_value(
                f"queue_{self.queue_name}", "processing_interval", 1.0
            )
            
            try:
                # Simulate processing work
                items_processed = self._process_batch(batch_size)
                
                if items_processed > 0:
                    with self._lock:
                        self._metrics.items_processed += items_processed
                        self._metrics.last_activity = datetime.now()
                
                # Wait between processing cycles
                time.sleep(processing_interval)
                
            except Exception as e:
                logger.error(f"Error in worker {worker_name}: {str(e)}")
                with self._lock:
                    self._metrics.items_failed += 1
        
        logger.debug(f"Worker {worker_name} stopped")
    
    def _process_batch(self, batch_size: int) -> int:
        """Process a batch of queue items (mock implementation)."""
        # In real implementation, this would:
        # 1. Fetch items from actual queue
        # 2. Process each item
        # 3. Update metrics
        # 4. Handle errors
        
        # Mock processing
        start_time = time.time()
        
        # Simulate variable processing time
        import random
        processing_time = random.uniform(0.1, 0.5)
        time.sleep(processing_time)
        
        # Update timing metrics
        with self._lock:
            self._processing_times.append(processing_time)
            if len(self._processing_times) > self._max_timing_samples:
                self._processing_times.pop(0)
            
            # Calculate average processing time
            if self._processing_times:
                self._metrics.average_processing_time = sum(self._processing_times) / len(self._processing_times)
            
            # Calculate processing rate
            if processing_time > 0:
                self._metrics.processing_rate = 1.0 / processing_time
        
        # Return number of items processed (mock)
        return min(batch_size, random.randint(1, 5))
    
    def _check_schedules(self):
        """Background thread to check for scheduled pauses/resumes."""
        while True:
            try:
                current_schedules = list(self._pause_schedules.values())
                
                for schedule in current_schedules:
                    if not schedule.enabled:
                        continue
                    
                    now = datetime.now()
                    
                    # Check for pause time
                    if (self._state == QueueState.RUNNING and 
                        now >= schedule.pause_time and 
                        (not hasattr(schedule, '_pause_triggered') or not schedule._pause_triggered)):
                        
                        logger.info(f"Triggering scheduled pause: {schedule.name}")
                        self.pause(schedule.mode, f"Scheduled pause: {schedule.reason}")
                        schedule._pause_triggered = True
                    
                    # Check for resume time
                    if (schedule.resume_time and 
                        self._state == QueueState.PAUSED and 
                        now >= schedule.resume_time and 
                        hasattr(schedule, '_pause_triggered') and schedule._pause_triggered):
                        
                        logger.info(f"Triggering scheduled resume: {schedule.name}")
                        self.resume(f"Scheduled resume: {schedule.name}")
                        
                        # Clean up one-time schedules
                        if not schedule.recurring:
                            self.cancel_scheduled_pause(schedule.id)
                        else:
                            # Reset for next cycle
                            schedule._pause_triggered = False
                
                # Sleep between checks
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in schedule checker: {str(e)}")
                time.sleep(30)  # Wait longer on error


# Global registry of queue controllers
_queue_controllers: Dict[str, QueueController] = {}
_controllers_lock = RLock()


def get_queue_controller(queue_name: str = "default") -> QueueController:
    """Get or create a queue controller instance."""
    with _controllers_lock:
        if queue_name not in _queue_controllers:
            _queue_controllers[queue_name] = QueueController(queue_name)
        return _queue_controllers[queue_name]


def get_all_queue_controllers() -> Dict[str, QueueController]:
    """Get all active queue controllers."""
    with _controllers_lock:
        return _queue_controllers.copy()
