"""
Cron-based scheduler implementation using APScheduler.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from threading import RLock

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.jobstores.memory import MemoryJobStore
    from apscheduler.executors.pool import ThreadPoolExecutor
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False

from .models import Schedule, ScheduleType

logger = logging.getLogger(__name__)


class CronScheduler:
    """
    Cron-based scheduler using APScheduler for precise timing.
    
    Handles cron expressions and manages scheduled job execution.
    """
    
    def __init__(self, max_workers: int = 10):
        """
        Initialize the cron scheduler.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self._lock = RLock()
        self._running = False
        self._schedules: Dict[str, Schedule] = {}
        self._due_schedules: Set[str] = set()
        
        if not APSCHEDULER_AVAILABLE:
            logger.warning("APScheduler not available. Cron scheduling will use basic implementation.")
            self._scheduler = None
            self._fallback_schedules: Dict[str, datetime] = {}
        else:
            # Configure APScheduler
            jobstores = {
                'default': MemoryJobStore()
            }
            executors = {
                'default': ThreadPoolExecutor(max_workers)
            }
            job_defaults = {
                'coalesce': False,
                'max_instances': 1,
                'misfire_grace_time': 30
            }
            
            self._scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='UTC'
            )
            
            # Add event listeners
            self._scheduler.add_listener(
                self._job_executed_listener,
                EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
            )
        
        logger.info(f"CronScheduler initialized with max_workers={max_workers}")
    
    def start(self) -> None:
        """Start the cron scheduler."""
        if self._running:
            logger.warning("CronScheduler is already running")
            return
        
        with self._lock:
            self._running = True
            
            if self._scheduler:
                self._scheduler.start()
                logger.info("APScheduler started")
            else:
                logger.info("Using fallback cron implementation")
        
        logger.info("CronScheduler started successfully")
    
    def stop(self) -> None:
        """Stop the cron scheduler."""
        if not self._running:
            logger.warning("CronScheduler is not running")
            return
        
        with self._lock:
            self._running = False
            
            if self._scheduler:
                self._scheduler.shutdown(wait=True)
                logger.info("APScheduler stopped")
            
            self._schedules.clear()
            self._due_schedules.clear()
        
        logger.info("CronScheduler stopped successfully")
    
    def add_schedule(self, schedule: Schedule) -> bool:
        """
        Add a cron schedule.
        
        Args:
            schedule: Schedule configuration
            
        Returns:
            True if added successfully
        """
        if schedule.schedule_type != ScheduleType.CRON:
            logger.error(f"Invalid schedule type for cron scheduler: {schedule.schedule_type}")
            return False
        
        if not schedule.cron_expression:
            logger.error(f"No cron expression provided for schedule: {schedule.name}")
            return False
        
        with self._lock:
            self._schedules[schedule.id] = schedule
            
            if self._scheduler:
                try:
                    # Parse cron expression
                    trigger = CronTrigger.from_crontab(schedule.cron_expression)
                    
                    # Add job to scheduler
                    self._scheduler.add_job(
                        func=self._schedule_triggered,
                        trigger=trigger,
                        args=[schedule.id],
                        id=schedule.id,
                        name=schedule.name,
                        replace_existing=True
                    )
                    
                    # Calculate next run time
                    next_run = self._scheduler.get_job(schedule.id).next_run_time
                    schedule.next_run_at = next_run
                    
                    logger.info(f"Added cron schedule: {schedule.name} ({schedule.cron_expression})")
                    logger.info(f"Next run: {next_run}")
                    
                except Exception as e:
                    logger.error(f"Failed to add cron schedule {schedule.name}: {str(e)}")
                    return False
            
            else:
                # Fallback implementation
                try:
                    next_run = self._calculate_next_run_fallback(schedule.cron_expression)
                    schedule.next_run_at = next_run
                    self._fallback_schedules[schedule.id] = next_run
                    
                    logger.info(f"Added fallback cron schedule: {schedule.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to add fallback cron schedule {schedule.name}: {str(e)}")
                    return False
        
        return True
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a cron schedule.
        
        Args:
            schedule_id: Schedule ID to remove
            
        Returns:
            True if removed successfully
        """
        with self._lock:
            if schedule_id not in self._schedules:
                return False
            
            schedule = self._schedules[schedule_id]
            
            if self._scheduler:
                try:
                    self._scheduler.remove_job(schedule_id)
                    logger.info(f"Removed cron schedule: {schedule.name}")
                except Exception as e:
                    logger.error(f"Failed to remove cron schedule {schedule.name}: {str(e)}")
                    return False
            
            else:
                # Fallback implementation
                if schedule_id in self._fallback_schedules:
                    del self._fallback_schedules[schedule_id]
            
            del self._schedules[schedule_id]
            self._due_schedules.discard(schedule_id)
        
        return True
    
    def get_due_schedules(self) -> List[str]:
        """
        Get schedules that are due for execution.
        
        Returns:
            List of schedule IDs that are due
        """
        with self._lock:
            if self._scheduler:
                # APScheduler handles this automatically via callbacks
                due = list(self._due_schedules)
                self._due_schedules.clear()
                return due
            
            else:
                # Fallback implementation
                now = datetime.now()
                due_schedules = []
                
                for schedule_id, next_run in list(self._fallback_schedules.items()):
                    if now >= next_run:
                        due_schedules.append(schedule_id)
                        
                        # Calculate next run time
                        schedule = self._schedules.get(schedule_id)
                        if schedule:
                            try:
                                next_next_run = self._calculate_next_run_fallback(
                                    schedule.cron_expression, 
                                    from_time=now
                                )
                                self._fallback_schedules[schedule_id] = next_next_run
                                schedule.next_run_at = next_next_run
                            except Exception as e:
                                logger.error(f"Failed to calculate next run for {schedule.name}: {str(e)}")
                
                return due_schedules
    
    def get_next_run_time(self, schedule_id: str) -> Optional[datetime]:
        """
        Get the next run time for a schedule.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Next run time or None
        """
        with self._lock:
            if schedule_id not in self._schedules:
                return None
            
            if self._scheduler:
                job = self._scheduler.get_job(schedule_id)
                return job.next_run_time if job else None
            
            else:
                return self._fallback_schedules.get(schedule_id)
    
    def get_schedule_info(self, schedule_id: str) -> Optional[Dict]:
        """
        Get detailed information about a schedule.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Schedule information dictionary
        """
        with self._lock:
            if schedule_id not in self._schedules:
                return None
            
            schedule = self._schedules[schedule_id]
            
            info = {
                'id': schedule.id,
                'name': schedule.name,
                'cron_expression': schedule.cron_expression,
                'next_run_time': self.get_next_run_time(schedule_id),
                'run_count': schedule.run_count,
                'success_count': schedule.success_count,
                'failure_count': schedule.failure_count,
                'last_run_at': schedule.last_run_at
            }
            
            if self._scheduler:
                job = self._scheduler.get_job(schedule_id)
                if job:
                    info.update({
                        'pending': job.pending,
                        'max_instances': job.max_instances,
                        'misfire_grace_time': job.misfire_grace_time
                    })
            
            return info
    
    def _schedule_triggered(self, schedule_id: str):
        """Handle schedule trigger (APScheduler callback)."""
        with self._lock:
            self._due_schedules.add(schedule_id)
        
        logger.debug(f"Schedule triggered: {schedule_id}")
    
    def _job_executed_listener(self, event):
        """Listen to APScheduler job execution events."""
        schedule_id = event.job_id
        
        if event.exception:
            logger.error(f"Cron job {schedule_id} failed: {event.exception}")
        else:
            logger.debug(f"Cron job {schedule_id} executed successfully")
    
    def _calculate_next_run_fallback(
        self, 
        cron_expression: str, 
        from_time: Optional[datetime] = None
    ) -> datetime:
        """
        Fallback cron calculation for basic expressions.
        
        This is a simplified implementation that supports basic cron patterns.
        For full cron support, APScheduler should be used.
        """
        if from_time is None:
            from_time = datetime.now()
        
        # Parse basic cron expression: minute hour day month weekday
        parts = cron_expression.strip().split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expression}")
        
        minute_part, hour_part, day_part, month_part, weekday_part = parts
        
        # Start from next minute
        next_run = from_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        # Simple daily schedule support (e.g., "0 2 * * *" for 2 AM daily)
        if (minute_part.isdigit() and hour_part.isdigit() and 
            day_part == '*' and month_part == '*' and weekday_part == '*'):
            
            target_hour = int(hour_part)
            target_minute = int(minute_part)
            
            # Set target time for today
            target_time = from_time.replace(
                hour=target_hour, 
                minute=target_minute, 
                second=0, 
                microsecond=0
            )
            
            # If target time has passed today, schedule for tomorrow
            if target_time <= from_time:
                target_time += timedelta(days=1)
            
            return target_time
        
        # Simple hourly schedule support (e.g., "30 * * * *" for 30 minutes past every hour)
        elif (minute_part.isdigit() and hour_part == '*' and 
              day_part == '*' and month_part == '*' and weekday_part == '*'):
            
            target_minute = int(minute_part)
            
            # Set target minute for current hour
            target_time = from_time.replace(minute=target_minute, second=0, microsecond=0)
            
            # If target time has passed this hour, schedule for next hour
            if target_time <= from_time:
                target_time += timedelta(hours=1)
            
            return target_time
        
        else:
            # For complex expressions, default to next hour
            logger.warning(f"Complex cron expression not fully supported: {cron_expression}")
            return next_run + timedelta(hours=1)
    
    def validate_cron_expression(self, cron_expression: str) -> bool:
        """
        Validate a cron expression.
        
        Args:
            cron_expression: Cron expression to validate
            
        Returns:
            True if valid
        """
        try:
            if self._scheduler:
                # Use APScheduler validation
                CronTrigger.from_crontab(cron_expression)
                return True
            else:
                # Basic validation for fallback
                parts = cron_expression.strip().split()
                return len(parts) == 5
        
        except Exception:
            return False
    
    @property
    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self._running
    
    @property
    def job_count(self) -> int:
        """Get the number of active jobs."""
        with self._lock:
            return len(self._schedules)