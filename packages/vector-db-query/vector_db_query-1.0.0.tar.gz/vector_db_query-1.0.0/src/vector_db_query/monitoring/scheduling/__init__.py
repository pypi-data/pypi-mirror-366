"""
Ansera Scheduling Module

Provides enterprise-grade scheduling capabilities for automated document processing.

Components:
- SchedulerService: Core scheduling engine with cron and event-driven triggers
- CronScheduler: Cron expression parsing and time-based scheduling
- FileWatcher: File system event monitoring for real-time triggers
- ScheduleManager: Schedule configuration and management
- TaskExecutor: Job execution and error handling

Usage:
    from vector_db_query.monitoring.scheduling import SchedulerService, ScheduleManager
    
    # Create scheduler
    scheduler = SchedulerService()
    
    # Add cron schedule
    scheduler.add_cron_schedule(
        name="daily_processing",
        cron_expression="0 2 * * *",  # 2 AM daily
        task="process_documents",
        folder_path="/data/documents"
    )
    
    # Start scheduler
    scheduler.start()
"""

from .core import SchedulerService
from .cron_scheduler import CronScheduler
from .file_watcher import FileWatcher
from .schedule_manager import ScheduleManager
from .task_executor import TaskExecutor
from .models import Schedule, ScheduleType, TaskResult, ScheduleStatus

__all__ = [
    'SchedulerService',
    'CronScheduler', 
    'FileWatcher',
    'ScheduleManager',
    'TaskExecutor',
    'Schedule',
    'ScheduleType',
    'TaskResult',
    'ScheduleStatus'
]

__version__ = '1.0.0'