"""
Task execution engine for scheduled jobs.
"""

import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor, Future
from threading import RLock

from .models import Schedule, TaskResult, TaskStatus

logger = logging.getLogger(__name__)


class TaskExecutor:
    """
    Executes scheduled tasks with proper error handling and result tracking.
    
    Supports various task types and provides execution context management.
    """
    
    def __init__(self, max_workers: int = 5):
        """
        Initialize task executor.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = RLock()
        self._running = False
        
        # Task registry
        self._task_functions: Dict[str, Callable] = {}
        self._active_tasks: Dict[str, Future] = {}
        
        # Event callbacks
        self.on_task_started: Optional[Callable[[TaskResult], None]] = None
        self.on_task_completed: Optional[Callable[[TaskResult], None]] = None
        self.on_task_failed: Optional[Callable[[TaskResult], None]] = None
        
        # Register built-in tasks
        self._register_builtin_tasks()
        
        logger.info(f"TaskExecutor initialized with max_workers={max_workers}")
    
    def start(self) -> None:
        """Start the task executor."""
        with self._lock:
            self._running = True
        logger.info("TaskExecutor started")
    
    def stop(self) -> None:
        """Stop the task executor."""
        with self._lock:
            self._running = False
            
            # Cancel active tasks
            for task_id, future in self._active_tasks.items():
                if not future.done():
                    future.cancel()
                    logger.info(f"Cancelled task {task_id}")
            
            self._active_tasks.clear()
            
            # Shutdown executor
            self._executor.shutdown(wait=True)
        
        logger.info("TaskExecutor stopped")
    
    def register_task(self, task_name: str, task_function: Callable) -> None:
        """
        Register a task function.
        
        Args:
            task_name: Name of the task
            task_function: Function to execute (should accept schedule and parameters)
        """
        with self._lock:
            self._task_functions[task_name] = task_function
        
        logger.info(f"Registered task function: {task_name}")
    
    def unregister_task(self, task_name: str) -> bool:
        """
        Unregister a task function.
        
        Args:
            task_name: Name of the task to unregister
            
        Returns:
            True if unregistered successfully
        """
        with self._lock:
            if task_name in self._task_functions:
                del self._task_functions[task_name]
                logger.info(f"Unregistered task function: {task_name}")
                return True
        
        return False
    
    def execute_task(self, schedule: Schedule, task_result: TaskResult) -> TaskResult:
        """
        Execute a task synchronously.
        
        Args:
            schedule: Schedule configuration
            task_result: Task result object to populate
            
        Returns:
            Updated task result
        """
        task_result.started_at = datetime.now()
        task_result.status = TaskStatus.RUNNING
        
        # Emit task started event
        if self.on_task_started:
            try:
                self.on_task_started(task_result)
            except Exception as e:
                logger.error(f"Error in task started callback: {str(e)}")
        
        try:
            # Get task function
            task_function = self._task_functions.get(schedule.task_name)
            if not task_function:
                raise ValueError(f"Task function not found: {schedule.task_name}")
            
            logger.info(f"Executing task: {schedule.task_name} for schedule: {schedule.name}")
            
            # Prepare task parameters
            task_params = {
                'schedule': schedule,
                'task_result': task_result,
                **schedule.task_parameters
            }
            
            # Execute task
            result_data = task_function(**task_params)
            
            # Update task result
            task_result.completed_at = datetime.now()
            task_result.duration_seconds = (
                task_result.completed_at - task_result.started_at
            ).total_seconds()
            task_result.status = TaskStatus.COMPLETED
            task_result.success = True
            task_result.result_data = result_data or {}
            
            logger.info(f"Task completed successfully: {schedule.task_name}")
            
            # Emit task completed event
            if self.on_task_completed:
                try:
                    self.on_task_completed(task_result)
                except Exception as e:
                    logger.error(f"Error in task completed callback: {str(e)}")
        
        except Exception as e:
            # Handle task failure
            task_result.completed_at = datetime.now()
            task_result.duration_seconds = (
                task_result.completed_at - task_result.started_at
            ).total_seconds()
            task_result.status = TaskStatus.FAILED
            task_result.success = False
            task_result.error_message = str(e)
            task_result.error_traceback = traceback.format_exc()
            
            logger.error(f"Task failed: {schedule.task_name} - {str(e)}")
            
            # Emit task failed event
            if self.on_task_failed:
                try:
                    self.on_task_failed(task_result)
                except Exception as callback_error:
                    logger.error(f"Error in task failed callback: {str(callback_error)}")
        
        return task_result
    
    def submit_task(self, schedule: Schedule, task_result: TaskResult) -> Future:
        """
        Submit a task for asynchronous execution.
        
        Args:
            schedule: Schedule configuration
            task_result: Task result object
            
        Returns:
            Future object for the task
        """
        future = self._executor.submit(self.execute_task, schedule, task_result)
        
        with self._lock:
            self._active_tasks[task_result.task_id] = future
        
        # Add completion callback
        future.add_done_callback(
            lambda f: self._task_completion_callback(task_result.task_id, f)
        )
        
        return future
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        with self._lock:
            if task_id in self._active_tasks:
                future = self._active_tasks[task_id]
                if not future.done():
                    result = future.cancel()
                    if result:
                        logger.info(f"Cancelled task: {task_id}")
                    return result
        
        return False
    
    def get_active_tasks(self) -> List[str]:
        """
        Get list of active task IDs.
        
        Returns:
            List of active task IDs
        """
        with self._lock:
            return [
                task_id for task_id, future in self._active_tasks.items()
                if not future.done()
            ]
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """
        Get status of a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status or None if not found
        """
        with self._lock:
            if task_id in self._active_tasks:
                future = self._active_tasks[task_id]
                if future.running():
                    return "running"
                elif future.cancelled():
                    return "cancelled"
                elif future.done():
                    return "completed" if not future.exception() else "failed"
                else:
                    return "pending"
        
        return None
    
    def _task_completion_callback(self, task_id: str, future: Future):
        """Callback when a task completes."""
        with self._lock:
            if task_id in self._active_tasks:
                del self._active_tasks[task_id]
        
        if future.cancelled():
            logger.info(f"Task cancelled: {task_id}")
        elif future.exception():
            logger.error(f"Task failed: {task_id} - {future.exception()}")
        else:
            logger.debug(f"Task completed: {task_id}")
    
    def _register_builtin_tasks(self):
        """Register built-in task functions."""
        
        # Document processing task
        self.register_task("process_documents", self._process_documents_task)
        
        # File cleanup task
        self.register_task("cleanup_files", self._cleanup_files_task)
        
        # Health check task
        self.register_task("health_check", self._health_check_task)
        
        # Custom command task
        self.register_task("run_command", self._run_command_task)
    
    def _process_documents_task(self, schedule: Schedule, task_result: TaskResult, **params) -> Dict[str, Any]:
        """
        Built-in document processing task.
        
        This task processes documents in a specified folder.
        """
        from ...document_processor import DocumentProcessor
        from ...vector_db.service import VectorDBService
        from ...utils.config import Config
        
        # Get parameters
        folder_path = params.get('folder_path') or schedule.task_parameters.get('folder_path')
        if not folder_path:
            raise ValueError("folder_path parameter is required for document processing")
        
        collection_name = params.get('collection_name') or schedule.task_parameters.get('collection_name')
        file_patterns = params.get('file_patterns') or schedule.task_parameters.get('file_patterns', ['*'])
        
        logger.info(f"Processing documents in: {folder_path}")
        
        # Initialize services
        config = Config()
        processor = DocumentProcessor(config)
        vector_service = VectorDBService(config)
        
        # Process documents
        folder = Path(folder_path)
        if not folder.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")
        
        processed_files = []
        failed_files = []
        
        # Find files to process
        files_to_process = []
        for pattern in file_patterns:
            files_to_process.extend(folder.glob(pattern))
        
        # Remove duplicates and filter files
        files_to_process = list(set(files_to_process))
        files_to_process = [f for f in files_to_process if f.is_file()]
        
        logger.info(f"Found {len(files_to_process)} files to process")
        
        for file_path in files_to_process:
            try:
                # Process document
                doc_result = processor.process_file(
                    file_path=str(file_path),
                    collection_name=collection_name
                )
                
                if doc_result.success:
                    # Add to vector database
                    vector_service.add_document(doc_result, collection_name=collection_name)
                    processed_files.append(str(file_path))
                    logger.info(f"Processed: {file_path.name}")
                else:
                    failed_files.append({
                        'file': str(file_path),
                        'error': doc_result.error_message or "Unknown error"
                    })
                    logger.error(f"Failed to process: {file_path.name}")
            
            except Exception as e:
                failed_files.append({
                    'file': str(file_path),
                    'error': str(e)
                })
                logger.error(f"Error processing {file_path.name}: {str(e)}")
        
        return {
            'folder_path': folder_path,
            'total_files': len(files_to_process),
            'processed_files': len(processed_files),
            'failed_files': len(failed_files),
            'processed_list': processed_files,
            'failed_list': failed_files,
            'collection_name': collection_name
        }
    
    def _cleanup_files_task(self, schedule: Schedule, task_result: TaskResult, **params) -> Dict[str, Any]:
        """
        Built-in file cleanup task.
        
        This task removes old files based on age criteria.
        """
        import os
        import time
        
        # Get parameters
        folder_path = params.get('folder_path') or schedule.task_parameters.get('folder_path')
        max_age_days = params.get('max_age_days') or schedule.task_parameters.get('max_age_days', 30)
        file_patterns = params.get('file_patterns') or schedule.task_parameters.get('file_patterns', ['*'])
        
        if not folder_path:
            raise ValueError("folder_path parameter is required for file cleanup")
        
        logger.info(f"Cleaning up files in: {folder_path} (older than {max_age_days} days)")
        
        folder = Path(folder_path)
        if not folder.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")
        
        # Calculate cutoff time
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        deleted_files = []
        failed_deletions = []
        
        # Find files to delete
        for pattern in file_patterns:
            for file_path in folder.glob(pattern):
                if file_path.is_file():
                    try:
                        # Check file age
                        file_mtime = file_path.stat().st_mtime
                        if file_mtime < cutoff_time:
                            file_path.unlink()
                            deleted_files.append(str(file_path))
                            logger.info(f"Deleted old file: {file_path.name}")
                    
                    except Exception as e:
                        failed_deletions.append({
                            'file': str(file_path),
                            'error': str(e)
                        })
                        logger.error(f"Failed to delete {file_path.name}: {str(e)}")
        
        return {
            'folder_path': folder_path,
            'max_age_days': max_age_days,
            'deleted_files': len(deleted_files),
            'failed_deletions': len(failed_deletions),
            'deleted_list': deleted_files,
            'failed_list': failed_deletions
        }
    
    def _health_check_task(self, schedule: Schedule, task_result: TaskResult, **params) -> Dict[str, Any]:
        """
        Built-in health check task.
        
        This task performs system health checks.
        """
        import psutil
        from ...vector_db.service import VectorDBService
        from ...utils.config import Config
        
        logger.info("Performing system health check")
        
        health_results = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'services': {},
            'overall_status': 'healthy'
        }
        
        try:
            # System metrics
            health_results['system'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
            
            # Check vector database
            try:
                config = Config()
                vector_service = VectorDBService(config)
                collections = vector_service.collection_manager.list_collections()
                
                health_results['services']['vector_db'] = {
                    'status': 'healthy',
                    'collections_count': len(collections),
                    'total_vectors': sum(col.vectors_count for col in collections)
                }
            except Exception as e:
                health_results['services']['vector_db'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_results['overall_status'] = 'degraded'
            
            # Check disk space
            if health_results['system']['disk_percent'] > 90:
                health_results['overall_status'] = 'warning'
            
            # Check memory usage
            if health_results['system']['memory_percent'] > 90:
                health_results['overall_status'] = 'warning'
        
        except Exception as e:
            health_results['overall_status'] = 'error'
            health_results['error'] = str(e)
        
        return health_results
    
    def _run_command_task(self, schedule: Schedule, task_result: TaskResult, **params) -> Dict[str, Any]:
        """
        Built-in command execution task.
        
        This task runs shell commands.
        """
        import subprocess
        
        # Get parameters
        command = params.get('command') or schedule.task_parameters.get('command')
        if not command:
            raise ValueError("command parameter is required for run_command task")
        
        timeout = params.get('timeout') or schedule.task_parameters.get('timeout', 300)
        working_dir = params.get('working_dir') or schedule.task_parameters.get('working_dir')
        
        logger.info(f"Executing command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir
            )
            
            return {
                'command': command,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0,
                'timeout': timeout,
                'working_dir': working_dir
            }
        
        except subprocess.TimeoutExpired:
            raise Exception(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise Exception(f"Command execution failed: {str(e)}")
    
    @property
    def is_running(self) -> bool:
        """Check if the executor is running."""
        return self._running
    
    @property
    def active_task_count(self) -> int:
        """Get the number of active tasks."""
        with self._lock:
            return len([f for f in self._active_tasks.values() if not f.done()])