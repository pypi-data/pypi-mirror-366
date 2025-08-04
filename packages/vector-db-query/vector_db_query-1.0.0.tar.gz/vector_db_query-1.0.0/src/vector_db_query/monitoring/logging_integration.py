"""
Integration utilities for adding logging to monitoring components.

This module provides decorators and utilities to integrate logging
into existing monitoring classes without modifying their core functionality.
"""

from functools import wraps
from typing import Any, Callable
import logging

from .logging import get_monitoring_logger

# Get logger instances
logger = logging.getLogger(__name__)
monitoring_logger = get_monitoring_logger()


def with_activity_logging(activity_type: str):
    """
    Decorator to add activity logging to monitoring methods.
    
    Args:
        activity_type: Type of activity being performed
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            component = self.__class__.__name__
            
            # Log activity start
            monitoring_logger.log_activity(
                component,
                activity_type,
                f"Starting {func.__name__}"
            )
            
            try:
                # Execute function
                result = func(self, *args, **kwargs)
                
                # Log success
                monitoring_logger.log_activity(
                    component,
                    activity_type,
                    f"Completed {func.__name__} successfully"
                )
                
                return result
                
            except Exception as e:
                # Log error
                monitoring_logger.log_error(
                    component,
                    activity_type,
                    str(e)
                )
                raise
        
        return wrapper
    return decorator


def with_metrics_logging(func: Callable) -> Callable:
    """
    Decorator to automatically log metrics data.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        
        # Log metrics if result contains metric data
        if isinstance(result, dict) and any(k in result for k in ['cpu', 'memory', 'disk']):
            monitoring_logger.log_metrics(result)
        
        return result
    
    return wrapper


def with_queue_logging(event_type: str):
    """
    Decorator to add queue event logging.
    
    Args:
        event_type: Type of queue event
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Extract job_id from args if available
            job_id = args[0] if args else kwargs.get('job_id', 'unknown')
            
            # Log queue event
            monitoring_logger.log_queue_event(
                event_type,
                str(job_id),
                {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs': list(kwargs.keys())
                }
            )
            
            try:
                result = func(self, *args, **kwargs)
                
                # Log completion
                monitoring_logger.log_queue_event(
                    f"{event_type}_complete",
                    str(job_id),
                    {'success': True}
                )
                
                return result
                
            except Exception as e:
                # Log failure
                monitoring_logger.log_queue_event(
                    f"{event_type}_failed",
                    str(job_id),
                    {'error': str(e)}
                )
                raise
        
        return wrapper
    return decorator


def with_process_logging(func: Callable) -> Callable:
    """
    Decorator to add process event logging.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Determine process name and event type from function name
        func_name = func.__name__
        
        if 'restart' in func_name:
            event_type = 'restart'
            process_name = func_name.replace('restart_', '').replace('_', '-')
        elif 'start' in func_name:
            event_type = 'start'
            process_name = func_name.replace('start_', '').replace('_', '-')
        elif 'stop' in func_name:
            event_type = 'stop'
            process_name = func_name.replace('stop_', '').replace('_', '-')
        else:
            event_type = 'operation'
            process_name = 'unknown'
        
        # Log process event
        monitoring_logger.log_process_event(
            process_name,
            event_type,
            details={'function': func_name}
        )
        
        try:
            result = func(self, *args, **kwargs)
            
            # Log success with PID if available
            pid = None
            if isinstance(result, dict):
                pid = result.get('pid')
            
            monitoring_logger.log_process_event(
                process_name,
                f"{event_type}_success",
                pid=pid,
                details={'result': str(result)}
            )
            
            return result
            
        except Exception as e:
            # Log failure
            monitoring_logger.log_process_event(
                process_name,
                f"{event_type}_failed",
                details={'error': str(e)}
            )
            raise
    
    return wrapper


def with_change_logging(change_type: str):
    """
    Decorator to add pre/post change logging.
    
    Args:
        change_type: Type of change being made
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            component = self.__class__.__name__
            
            # Log pre-change state
            pre_log = monitoring_logger.log_pre_change(
                component,
                change_type,
                f"Executing {func.__name__}"
            )
            
            try:
                # Execute function
                result = func(self, *args, **kwargs)
                
                # Log post-change success
                monitoring_logger.log_post_change(
                    pre_log,
                    component,
                    change_type,
                    "SUCCESS",
                    {'result': str(result)}
                )
                
                return result
                
            except Exception as e:
                # Log post-change failure
                monitoring_logger.log_post_change(
                    pre_log,
                    component,
                    change_type,
                    "FAILURE",
                    {'error': str(e)}
                )
                raise
        
        return wrapper
    return decorator


class LoggingMixin:
    """
    Mixin class to add logging capabilities to monitoring components.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = monitoring_logger
    
    def log_activity(self, activity_type: str, details: str):
        """Log an activity."""
        self._logger.log_activity(
            self.__class__.__name__,
            activity_type,
            details
        )
    
    def log_error(self, error_type: str, message: str):
        """Log an error."""
        self._logger.log_error(
            self.__class__.__name__,
            error_type,
            message
        )
    
    def create_snapshot(self, name: str, description: str):
        """Create a snapshot."""
        return self._logger.create_snapshot(
            name,
            self.__class__.__name__,
            description
        )


# Utility functions for manual logging integration

def log_metric_collection(monitor_name: str, metrics: dict):
    """Log metric collection event."""
    monitoring_logger.log_activity(
        monitor_name,
        "metric_collection",
        f"Collected {len(metrics)} metrics"
    )
    monitoring_logger.log_metrics(metrics)


def log_queue_operation(operation: str, job_id: str, details: dict):
    """Log queue operation."""
    monitoring_logger.log_queue_event(operation, job_id, details)


def log_process_operation(process_name: str, operation: str, 
                        pid: Optional[int] = None, details: Optional[dict] = None):
    """Log process operation."""
    monitoring_logger.log_process_event(
        process_name,
        operation,
        pid=pid,
        details=details or {}
    )