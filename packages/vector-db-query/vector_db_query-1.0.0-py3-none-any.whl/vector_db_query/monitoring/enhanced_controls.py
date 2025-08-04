"""
Enhanced process control functionality with pause/resume and parameter adjustment.

This module extends the ProcessController with advanced capabilities for
enterprise-grade service management.
"""

import os
import subprocess
import signal
import logging
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import psutil

from .controls import ProcessController
from .pm2_control import get_pm2_controller

logger = logging.getLogger(__name__)


class ServiceState(Enum):
    """Service operational states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSING = "pausing"
    PAUSED = "paused"
    RESUMING = "resuming"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"


class QueueState(Enum):
    """Queue processing states."""
    ACTIVE = "active"
    PAUSED = "paused"
    DRAINING = "draining"
    STOPPED = "stopped"


@dataclass
class ServiceParameters:
    """Configurable service parameters."""
    # Worker configuration
    worker_count: int = 4
    max_workers: int = 16
    min_workers: int = 1
    
    # Memory limits
    memory_limit_mb: int = 1024
    heap_size_mb: Optional[int] = None
    
    # Processing configuration
    batch_size: int = 10
    processing_timeout: int = 300  # seconds
    retry_attempts: int = 3
    
    # Queue configuration
    max_queue_size: int = 10000
    queue_timeout: int = 60
    
    # Performance tuning
    enable_profiling: bool = False
    log_level: str = "INFO"
    metrics_interval: int = 60
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def validate(self) -> List[str]:
        """Validate parameters and return list of issues."""
        issues = []
        
        if self.worker_count < self.min_workers:
            issues.append(f"worker_count ({self.worker_count}) less than min_workers ({self.min_workers})")
        
        if self.worker_count > self.max_workers:
            issues.append(f"worker_count ({self.worker_count}) greater than max_workers ({self.max_workers})")
        
        if self.memory_limit_mb < 128:
            issues.append("memory_limit_mb should be at least 128 MB")
        
        if self.batch_size < 1:
            issues.append("batch_size must be at least 1")
        
        return issues


@dataclass
class ServiceInfo:
    """Service information and state."""
    name: str
    state: ServiceState
    pid: Optional[int] = None
    uptime_seconds: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    parameters: ServiceParameters = field(default_factory=ServiceParameters)
    last_state_change: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    
    @property
    def is_running(self) -> bool:
        """Check if service is running."""
        return self.state in [ServiceState.RUNNING, ServiceState.PAUSING, ServiceState.RESUMING]
    
    @property
    def can_pause(self) -> bool:
        """Check if service can be paused."""
        return self.state == ServiceState.RUNNING
    
    @property
    def can_resume(self) -> bool:
        """Check if service can be resumed."""
        return self.state == ServiceState.PAUSED


class EnhancedProcessController(ProcessController):
    """
    Enhanced process controller with pause/resume and parameter adjustment.
    
    Extends the base ProcessController with advanced service management capabilities.
    """
    
    def __init__(self):
        """Initialize enhanced process controller."""
        super().__init__()
        
        # Service tracking
        self._services: Dict[str, ServiceInfo] = {}
        self._queue_states: Dict[str, QueueState] = {}
        self._parameter_files: Dict[str, Path] = {}
        
        # State persistence
        self.state_dir = self.base_dir / ".ansera" / "service_states"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Event callbacks
        self._state_change_callbacks: List[Callable[[str, ServiceState], None]] = []
        
        # Load saved states
        self._load_states()
        
        logger.info("EnhancedProcessController initialized")
    
    def pause_service(self, service_name: str) -> Dict[str, Any]:
        """
        Pause a running service without stopping it.
        
        Args:
            service_name: Name of the service to pause
            
        Returns:
            Status dictionary
        """
        try:
            service = self._get_or_create_service_info(service_name)
            
            if not service.can_pause:
                return {
                    "status": "error",
                    "message": f"Service {service_name} cannot be paused (state: {service.state.value})"
                }
            
            logger.info(f"Pausing service: {service_name}")
            
            # Update state
            self._update_service_state(service_name, ServiceState.PAUSING)
            
            # Service-specific pause logic
            if service_name == "document_processor":
                result = self._pause_document_processor()
            elif service_name == "mcp_server":
                result = self._pause_mcp_server()
            elif service_name == "scheduler":
                result = self._pause_scheduler()
            else:
                # Generic pause using signals
                result = self._pause_generic_service(service_name)
            
            if result["status"] == "success":
                self._update_service_state(service_name, ServiceState.PAUSED)
                logger.info(f"Service {service_name} paused successfully")
            else:
                self._update_service_state(service_name, ServiceState.ERROR, result.get("message"))
            
            return result
            
        except Exception as e:
            logger.error(f"Error pausing service {service_name}: {e}")
            self._update_service_state(service_name, ServiceState.ERROR, str(e))
            return {
                "status": "error",
                "message": f"Failed to pause service: {str(e)}"
            }
    
    def resume_service(self, service_name: str) -> Dict[str, Any]:
        """
        Resume a paused service.
        
        Args:
            service_name: Name of the service to resume
            
        Returns:
            Status dictionary
        """
        try:
            service = self._get_or_create_service_info(service_name)
            
            if not service.can_resume:
                return {
                    "status": "error",
                    "message": f"Service {service_name} cannot be resumed (state: {service.state.value})"
                }
            
            logger.info(f"Resuming service: {service_name}")
            
            # Update state
            self._update_service_state(service_name, ServiceState.RESUMING)
            
            # Service-specific resume logic
            if service_name == "document_processor":
                result = self._resume_document_processor()
            elif service_name == "mcp_server":
                result = self._resume_mcp_server()
            elif service_name == "scheduler":
                result = self._resume_scheduler()
            else:
                # Generic resume using signals
                result = self._resume_generic_service(service_name)
            
            if result["status"] == "success":
                self._update_service_state(service_name, ServiceState.RUNNING)
                logger.info(f"Service {service_name} resumed successfully")
            else:
                self._update_service_state(service_name, ServiceState.ERROR, result.get("message"))
            
            return result
            
        except Exception as e:
            logger.error(f"Error resuming service {service_name}: {e}")
            self._update_service_state(service_name, ServiceState.ERROR, str(e))
            return {
                "status": "error",
                "message": f"Failed to resume service: {str(e)}"
            }
    
    def adjust_parameters(
        self,
        service_name: str,
        parameters: Dict[str, Any],
        apply_immediately: bool = True
    ) -> Dict[str, Any]:
        """
        Adjust service parameters dynamically.
        
        Args:
            service_name: Name of the service
            parameters: Parameter updates
            apply_immediately: Apply changes without restart
            
        Returns:
            Status dictionary
        """
        try:
            service = self._get_or_create_service_info(service_name)
            
            # Update parameters
            old_params = service.parameters.to_dict()
            for key, value in parameters.items():
                if hasattr(service.parameters, key):
                    setattr(service.parameters, key, value)
                else:
                    logger.warning(f"Unknown parameter: {key}")
            
            # Validate new parameters
            issues = service.parameters.validate()
            if issues:
                # Revert changes
                for key, value in old_params.items():
                    setattr(service.parameters, key, value)
                
                return {
                    "status": "error",
                    "message": "Invalid parameters",
                    "issues": issues
                }
            
            # Save parameters
            self._save_service_parameters(service_name, service.parameters)
            
            # Apply changes if requested and service is running
            if apply_immediately and service.is_running:
                logger.info(f"Applying parameter changes to {service_name}")
                
                if service_name == "document_processor":
                    result = self._apply_processor_parameters(service.parameters)
                elif service_name == "mcp_server":
                    result = self._apply_mcp_parameters(service.parameters)
                elif service_name == "scheduler":
                    result = self._apply_scheduler_parameters(service.parameters)
                else:
                    result = self._apply_generic_parameters(service_name, service.parameters)
                
                if result["status"] != "success":
                    return result
            
            return {
                "status": "success",
                "message": f"Parameters updated for {service_name}",
                "parameters": service.parameters.to_dict(),
                "applied": apply_immediately and service.is_running
            }
            
        except Exception as e:
            logger.error(f"Error adjusting parameters for {service_name}: {e}")
            return {
                "status": "error",
                "message": f"Failed to adjust parameters: {str(e)}"
            }
    
    def pause_queue(self, queue_name: str = "default") -> Dict[str, Any]:
        """
        Pause processing of a specific queue.
        
        Args:
            queue_name: Name of the queue to pause
            
        Returns:
            Status dictionary
        """
        try:
            current_state = self._queue_states.get(queue_name, QueueState.ACTIVE)
            
            if current_state != QueueState.ACTIVE:
                return {
                    "status": "error",
                    "message": f"Queue {queue_name} is not active (state: {current_state.value})"
                }
            
            logger.info(f"Pausing queue: {queue_name}")
            
            # Update queue state
            self._queue_states[queue_name] = QueueState.PAUSED
            
            # Write pause flag file
            queue_dir = Path.home() / ".vector_db_query" / "queue"
            queue_dir.mkdir(parents=True, exist_ok=True)
            
            pause_file = queue_dir / f"{queue_name}_paused.flag"
            pause_file.write_text(datetime.now().isoformat())
            
            # Notify processors
            self._notify_queue_state_change(queue_name, QueueState.PAUSED)
            
            return {
                "status": "success",
                "message": f"Queue {queue_name} paused",
                "queue": queue_name,
                "state": QueueState.PAUSED.value
            }
            
        except Exception as e:
            logger.error(f"Error pausing queue {queue_name}: {e}")
            return {
                "status": "error",
                "message": f"Failed to pause queue: {str(e)}"
            }
    
    def resume_queue(self, queue_name: str = "default") -> Dict[str, Any]:
        """
        Resume processing of a paused queue.
        
        Args:
            queue_name: Name of the queue to resume
            
        Returns:
            Status dictionary
        """
        try:
            current_state = self._queue_states.get(queue_name, QueueState.ACTIVE)
            
            if current_state != QueueState.PAUSED:
                return {
                    "status": "error",
                    "message": f"Queue {queue_name} is not paused (state: {current_state.value})"
                }
            
            logger.info(f"Resuming queue: {queue_name}")
            
            # Update queue state
            self._queue_states[queue_name] = QueueState.ACTIVE
            
            # Remove pause flag file
            queue_dir = Path.home() / ".vector_db_query" / "queue"
            pause_file = queue_dir / f"{queue_name}_paused.flag"
            
            if pause_file.exists():
                pause_file.unlink()
            
            # Notify processors
            self._notify_queue_state_change(queue_name, QueueState.ACTIVE)
            
            return {
                "status": "success",
                "message": f"Queue {queue_name} resumed",
                "queue": queue_name,
                "state": QueueState.ACTIVE.value
            }
            
        except Exception as e:
            logger.error(f"Error resuming queue {queue_name}: {e}")
            return {
                "status": "error",
                "message": f"Failed to resume queue: {str(e)}"
            }
    
    def get_enhanced_service_status(self) -> Dict[str, Any]:
        """
        Get detailed status of all services with enhanced information.
        
        Returns:
            Comprehensive service status
        """
        try:
            # Get basic status from parent
            basic_status = self.get_service_status()
            
            # Enhance with additional information
            enhanced_status = {
                "timestamp": datetime.now().isoformat(),
                "services": {},
                "queues": {},
                "system": basic_status.get("system", {})
            }
            
            # Add enhanced service information
            for service_name, service_info in self._services.items():
                # Update runtime metrics if running
                if service_info.pid:
                    try:
                        proc = psutil.Process(service_info.pid)
                        service_info.cpu_percent = proc.cpu_percent(interval=0.1)
                        service_info.memory_usage_mb = proc.memory_info().rss / 1024 / 1024
                        service_info.uptime_seconds = time.time() - proc.create_time()
                    except psutil.NoSuchProcess:
                        service_info.state = ServiceState.STOPPED
                        service_info.pid = None
                
                enhanced_status["services"][service_name] = {
                    "state": service_info.state.value,
                    "pid": service_info.pid,
                    "uptime_seconds": service_info.uptime_seconds,
                    "memory_usage_mb": service_info.memory_usage_mb,
                    "cpu_percent": service_info.cpu_percent,
                    "can_pause": service_info.can_pause,
                    "can_resume": service_info.can_resume,
                    "parameters": service_info.parameters.to_dict(),
                    "last_state_change": service_info.last_state_change.isoformat(),
                    "error_message": service_info.error_message
                }
            
            # Add queue states
            for queue_name, queue_state in self._queue_states.items():
                enhanced_status["queues"][queue_name] = {
                    "state": queue_state.value,
                    "can_pause": queue_state == QueueState.ACTIVE,
                    "can_resume": queue_state == QueueState.PAUSED
                }
            
            # Add PM2 status if available
            if self.pm2.check_pm2_status():
                enhanced_status["pm2"] = {
                    "available": True,
                    "processes": self.pm2.list_processes()
                }
            else:
                enhanced_status["pm2"] = {"available": False}
            
            return enhanced_status
            
        except Exception as e:
            logger.error(f"Error getting enhanced service status: {e}")
            return {
                "status": "error",
                "message": f"Failed to get service status: {str(e)}"
            }
    
    def register_state_change_callback(self, callback: Callable[[str, ServiceState], None]):
        """Register a callback for service state changes."""
        self._state_change_callbacks.append(callback)
    
    def _pause_document_processor(self) -> Dict[str, Any]:
        """Pause document processor service."""
        # Send pause signal to processor
        pause_file = self.base_dir / ".ansera" / "processor_pause.flag"
        pause_file.parent.mkdir(parents=True, exist_ok=True)
        pause_file.write_text(datetime.now().isoformat())
        
        return {
            "status": "success",
            "message": "Document processor paused"
        }
    
    def _resume_document_processor(self) -> Dict[str, Any]:
        """Resume document processor service."""
        # Remove pause signal
        pause_file = self.base_dir / ".ansera" / "processor_pause.flag"
        if pause_file.exists():
            pause_file.unlink()
        
        return {
            "status": "success",
            "message": "Document processor resumed"
        }
    
    def _pause_mcp_server(self) -> Dict[str, Any]:
        """Pause MCP server."""
        # MCP server doesn't support pause, return error
        return {
            "status": "error",
            "message": "MCP server does not support pause operation"
        }
    
    def _resume_mcp_server(self) -> Dict[str, Any]:
        """Resume MCP server."""
        return {
            "status": "error",
            "message": "MCP server does not support resume operation"
        }
    
    def _pause_scheduler(self) -> Dict[str, Any]:
        """Pause scheduler service."""
        # Write pause configuration
        scheduler_config = self.base_dir / ".ansera" / "scheduler_config.json"
        scheduler_config.parent.mkdir(parents=True, exist_ok=True)
        
        config = {"paused": True, "timestamp": datetime.now().isoformat()}
        with scheduler_config.open('w') as f:
            json.dump(config, f)
        
        return {
            "status": "success",
            "message": "Scheduler paused"
        }
    
    def _resume_scheduler(self) -> Dict[str, Any]:
        """Resume scheduler service."""
        # Update scheduler configuration
        scheduler_config = self.base_dir / ".ansera" / "scheduler_config.json"
        
        if scheduler_config.exists():
            with scheduler_config.open('r') as f:
                config = json.load(f)
            
            config["paused"] = False
            config["resumed_at"] = datetime.now().isoformat()
            
            with scheduler_config.open('w') as f:
                json.dump(config, f)
        
        return {
            "status": "success",
            "message": "Scheduler resumed"
        }
    
    def _pause_generic_service(self, service_name: str) -> Dict[str, Any]:
        """Generic pause using SIGSTOP signal."""
        service = self._services.get(service_name)
        if not service or not service.pid:
            return {
                "status": "error",
                "message": f"Service {service_name} not found or not running"
            }
        
        try:
            os.kill(service.pid, signal.SIGSTOP)
            return {
                "status": "success",
                "message": f"Service {service_name} paused"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to pause service: {str(e)}"
            }
    
    def _resume_generic_service(self, service_name: str) -> Dict[str, Any]:
        """Generic resume using SIGCONT signal."""
        service = self._services.get(service_name)
        if not service or not service.pid:
            return {
                "status": "error",
                "message": f"Service {service_name} not found"
            }
        
        try:
            os.kill(service.pid, signal.SIGCONT)
            return {
                "status": "success",
                "message": f"Service {service_name} resumed"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to resume service: {str(e)}"
            }
    
    def _apply_processor_parameters(self, params: ServiceParameters) -> Dict[str, Any]:
        """Apply parameters to document processor."""
        # Write parameter file
        param_file = self.base_dir / ".ansera" / "processor_params.json"
        param_file.parent.mkdir(parents=True, exist_ok=True)
        
        with param_file.open('w') as f:
            json.dump(params.to_dict(), f)
        
        # Send reload signal
        service = self._services.get("document_processor")
        if service and service.pid:
            try:
                os.kill(service.pid, signal.SIGHUP)  # Reload signal
            except:
                pass
        
        return {
            "status": "success",
            "message": "Parameters applied to document processor"
        }
    
    def _apply_mcp_parameters(self, params: ServiceParameters) -> Dict[str, Any]:
        """Apply parameters to MCP server."""
        # MCP server requires restart for parameter changes
        return {
            "status": "warning",
            "message": "MCP server requires restart for parameter changes"
        }
    
    def _apply_scheduler_parameters(self, params: ServiceParameters) -> Dict[str, Any]:
        """Apply parameters to scheduler."""
        # Update scheduler configuration
        scheduler_config = self.base_dir / ".ansera" / "scheduler_params.json"
        scheduler_config.parent.mkdir(parents=True, exist_ok=True)
        
        with scheduler_config.open('w') as f:
            json.dump(params.to_dict(), f)
        
        return {
            "status": "success",
            "message": "Parameters applied to scheduler"
        }
    
    def _apply_generic_parameters(
        self,
        service_name: str,
        params: ServiceParameters
    ) -> Dict[str, Any]:
        """Apply parameters to generic service."""
        # Write parameter file
        param_file = self.state_dir / f"{service_name}_params.json"
        
        with param_file.open('w') as f:
            json.dump(params.to_dict(), f)
        
        return {
            "status": "success",
            "message": f"Parameters saved for {service_name} (restart required)"
        }
    
    def _get_or_create_service_info(self, service_name: str) -> ServiceInfo:
        """Get or create service info."""
        if service_name not in self._services:
            self._services[service_name] = ServiceInfo(
                name=service_name,
                state=ServiceState.UNKNOWN
            )
        return self._services[service_name]
    
    def _update_service_state(
        self,
        service_name: str,
        state: ServiceState,
        error_message: Optional[str] = None
    ):
        """Update service state and notify callbacks."""
        service = self._get_or_create_service_info(service_name)
        service.state = state
        service.last_state_change = datetime.now()
        service.error_message = error_message
        
        # Save state
        self._save_states()
        
        # Notify callbacks
        for callback in self._state_change_callbacks:
            try:
                callback(service_name, state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
    
    def _save_service_parameters(self, service_name: str, params: ServiceParameters):
        """Save service parameters to file."""
        param_file = self.state_dir / f"{service_name}_params.json"
        with param_file.open('w') as f:
            json.dump(params.to_dict(), f, indent=2)
    
    def _load_service_parameters(self, service_name: str) -> Optional[ServiceParameters]:
        """Load service parameters from file."""
        param_file = self.state_dir / f"{service_name}_params.json"
        if param_file.exists():
            try:
                with param_file.open('r') as f:
                    data = json.load(f)
                params = ServiceParameters()
                for key, value in data.items():
                    if hasattr(params, key):
                        setattr(params, key, value)
                return params
            except Exception as e:
                logger.error(f"Error loading parameters for {service_name}: {e}")
        return None
    
    def _save_states(self):
        """Save all service states to disk."""
        state_file = self.state_dir / "service_states.json"
        
        states = {}
        for service_name, service_info in self._services.items():
            states[service_name] = {
                "state": service_info.state.value,
                "pid": service_info.pid,
                "last_state_change": service_info.last_state_change.isoformat(),
                "error_message": service_info.error_message
            }
        
        queue_states = {
            name: state.value
            for name, state in self._queue_states.items()
        }
        
        data = {
            "services": states,
            "queues": queue_states,
            "timestamp": datetime.now().isoformat()
        }
        
        with state_file.open('w') as f:
            json.dump(data, f, indent=2)
    
    def _load_states(self):
        """Load service states from disk."""
        state_file = self.state_dir / "service_states.json"
        
        if state_file.exists():
            try:
                with state_file.open('r') as f:
                    data = json.load(f)
                
                # Load service states
                for service_name, state_data in data.get("services", {}).items():
                    service_info = ServiceInfo(
                        name=service_name,
                        state=ServiceState(state_data["state"]),
                        pid=state_data.get("pid"),
                        last_state_change=datetime.fromisoformat(state_data["last_state_change"]),
                        error_message=state_data.get("error_message")
                    )
                    
                    # Load parameters if available
                    params = self._load_service_parameters(service_name)
                    if params:
                        service_info.parameters = params
                    
                    self._services[service_name] = service_info
                
                # Load queue states
                for queue_name, state_value in data.get("queues", {}).items():
                    self._queue_states[queue_name] = QueueState(state_value)
                
                logger.info(f"Loaded states for {len(self._services)} services")
                
            except Exception as e:
                logger.error(f"Error loading states: {e}")
    
    def _notify_queue_state_change(self, queue_name: str, state: QueueState):
        """Notify processors of queue state change."""
        # Write notification file
        notify_file = self.state_dir / f"queue_{queue_name}_state.txt"
        notify_file.write_text(f"{state.value}\n{datetime.now().isoformat()}")
        
        # Could also send signals or use other IPC mechanisms


# Singleton instance
_enhanced_controller = None


def get_enhanced_controller() -> EnhancedProcessController:
    """Get the singleton enhanced process controller instance."""
    global _enhanced_controller
    if _enhanced_controller is None:
        _enhanced_controller = EnhancedProcessController()
    return _enhanced_controller