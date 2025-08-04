"""
Enhanced service controller with parameter adjustment capabilities.

This module extends basic service control with runtime parameter
adjustment, pause/resume, and live configuration updates.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from threading import RLock
import subprocess
import signal
import psutil

from .parameter_manager import get_parameter_manager, ParameterDefinition
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class ServiceState(Enum):
    """Extended service states."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"
    RESTARTING = "restarting"


class ControlAction(Enum):
    """Service control actions."""
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    PAUSE = "pause"
    RESUME = "resume"
    RELOAD_CONFIG = "reload_config"
    UPDATE_PARAM = "update_param"


@dataclass
class ServiceInfo:
    """Extended service information."""
    id: str
    name: str
    state: ServiceState
    pid: Optional[int] = None
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    uptime: Optional[float] = None
    restart_count: int = 0
    last_error: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    paused_at: Optional[datetime] = None
    config_file: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state.value,
            'pid': self.pid,
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'uptime': self.uptime,
            'restart_count': self.restart_count,
            'last_error': self.last_error,
            'parameters': self.parameters,
            'paused_at': self.paused_at.isoformat() if self.paused_at else None,
            'config_file': self.config_file
        }


class EnhancedServiceController:
    """
    Enhanced service controller with advanced features.
    
    Provides service control with parameter adjustment,
    pause/resume capabilities, and live updates.
    """
    
    def __init__(self):
        """
        Initialize enhanced service controller.
        """
        self._lock = RLock()
        
        # Service registry
        self._services: Dict[str, ServiceInfo] = {}
        
        # Parameter manager integration
        self._param_manager = get_parameter_manager()
        
        # Change tracker integration
        self._change_tracker = get_change_tracker()
        
        # Control hooks
        self._control_hooks: Dict[str, List[callable]] = {}
        
        # Pause/resume support
        self._paused_services: Dict[str, Dict[str, Any]] = {}
        
        # Initialize known services
        self._initialize_services()
        
        # Register parameter change callbacks
        self._register_parameter_callbacks()
        
        logger.info("EnhancedServiceController initialized")
    
    def _initialize_services(self):
        """Initialize known services."""
        # Register queue processor
        self.register_service(
            service_id="queue_processor",
            name="Queue Processor",
            config_file="/etc/vector_db_query/queue_processor.conf"
        )
        
        # Register MCP server
        self.register_service(
            service_id="mcp_server",
            name="MCP Server",
            config_file="/etc/vector_db_query/mcp_server.conf"
        )
        
        # Register monitoring service
        self.register_service(
            service_id="monitoring_service",
            name="Monitoring Service",
            config_file="/etc/vector_db_query/monitoring.conf"
        )
    
    def _register_parameter_callbacks(self):
        """Register callbacks for parameter changes."""
        # Register global callback for all parameter changes
        self._param_manager.register_change_callback(
            "*", "*", self._on_parameter_change
        )
    
    def _on_parameter_change(
        self,
        service_id: str,
        parameter_name: str,
        old_value: Any,
        new_value: Any
    ):
        """Handle parameter change events."""
        logger.info(
            f"Parameter change detected: {service_id}.{parameter_name} "
            f"{old_value} -> {new_value}"
        )
        
        # Check if service supports live updates
        service = self._services.get(service_id)
        
        if service and service.state == ServiceState.RUNNING:
            # Check if parameter requires restart
            param_def = self._param_manager.get_parameter(service_id, parameter_name)
            
            if param_def and not param_def.requires_restart:
                # Apply parameter without restart
                self._apply_parameter_live(service_id, parameter_name, new_value)
            else:
                logger.warning(
                    f"Parameter {parameter_name} requires restart for {service_id}"
                )
    
    def register_service(
        self,
        service_id: str,
        name: str,
        config_file: Optional[str] = None
    ) -> bool:
        """
        Register a service with the controller.
        
        Args:
            service_id: Unique service identifier
            name: Display name
            config_file: Configuration file path
            
        Returns:
            Success status
        """
        with self._lock:
            if service_id not in self._services:
                self._services[service_id] = ServiceInfo(
                    id=service_id,
                    name=name,
                    state=ServiceState.STOPPED,
                    config_file=config_file
                )
                
                logger.info(f"Registered service: {service_id}")
                return True
            
            return False
    
    def get_service_info(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service information."""
        with self._lock:
            return self._services.get(service_id)
    
    def get_all_services(self) -> List[ServiceInfo]:
        """Get all registered services."""
        with self._lock:
            return list(self._services.values())
    
    def control_service(
        self,
        service_id: str,
        action: ControlAction,
        parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Control a service with specified action.
        
        Args:
            service_id: Service to control
            action: Control action to perform
            parameters: Additional parameters for action
            
        Returns:
            Success status
        """
        with self._lock:
            service = self._services.get(service_id)
            
            if not service:
                logger.error(f"Service not found: {service_id}")
                return False
            
            # Track the control action
            self._change_tracker.track_change(
                category=ChangeCategory.SERVICE,
                change_type=ChangeType.EXECUTED,
                entity_type="service",
                entity_id=service_id,
                entity_name=service.name,
                description=f"Service control action: {action.value}",
                details={
                    'action': action.value,
                    'parameters': parameters or {},
                    'previous_state': service.state.value
                }
            )
            
            # Execute control action
            try:
                if action == ControlAction.START:
                    return self._start_service(service)
                
                elif action == ControlAction.STOP:
                    return self._stop_service(service)
                
                elif action == ControlAction.RESTART:
                    return self._restart_service(service)
                
                elif action == ControlAction.PAUSE:
                    return self._pause_service(service)
                
                elif action == ControlAction.RESUME:
                    return self._resume_service(service)
                
                elif action == ControlAction.RELOAD_CONFIG:
                    return self._reload_config(service)
                
                elif action == ControlAction.UPDATE_PARAM:
                    if parameters:
                        return self._update_parameters(service, parameters)
                    else:
                        logger.error("No parameters provided for update")
                        return False
                
                else:
                    logger.error(f"Unknown action: {action}")
                    return False
            
            except Exception as e:
                logger.error(f"Error executing {action} on {service_id}: {str(e)}")
                service.state = ServiceState.ERROR
                service.last_error = str(e)
                return False
    
    def _start_service(self, service: ServiceInfo) -> bool:
        """Start a service."""
        if service.state == ServiceState.RUNNING:
            logger.warning(f"Service {service.id} is already running")
            return True
        
        service.state = ServiceState.STARTING
        
        try:
            # Get current parameter values
            params = self._param_manager.get_service_parameters(service.id)
            service.parameters = {
                name: param.current_value
                for name, param in params.items()
            }
            
            # Start the service (mock implementation)
            # In real implementation, this would start the actual service
            logger.info(f"Starting service {service.id} with parameters: {service.parameters}")
            
            # Simulate service start
            service.state = ServiceState.RUNNING
            service.pid = os.getpid()  # Mock PID
            service.uptime = 0.0
            
            return True
        
        except Exception as e:
            service.state = ServiceState.ERROR
            service.last_error = str(e)
            return False
    
    def _stop_service(self, service: ServiceInfo) -> bool:
        """Stop a service."""
        if service.state == ServiceState.STOPPED:
            logger.warning(f"Service {service.id} is already stopped")
            return True
        
        service.state = ServiceState.STOPPING
        
        try:
            # Stop the service (mock implementation)
            logger.info(f"Stopping service {service.id}")
            
            # Clear pause state if paused
            if service.id in self._paused_services:
                del self._paused_services[service.id]
            
            service.state = ServiceState.STOPPED
            service.pid = None
            service.uptime = None
            service.paused_at = None
            
            return True
        
        except Exception as e:
            service.state = ServiceState.ERROR
            service.last_error = str(e)
            return False
    
    def _restart_service(self, service: ServiceInfo) -> bool:
        """Restart a service."""
        service.state = ServiceState.RESTARTING
        service.restart_count += 1
        
        # Stop then start
        if self._stop_service(service):
            return self._start_service(service)
        
        return False
    
    def _pause_service(self, service: ServiceInfo) -> bool:
        """Pause a service."""
        if service.state != ServiceState.RUNNING:
            logger.error(f"Can only pause running services. Current state: {service.state}")
            return False
        
        try:
            # Save current state
            self._paused_services[service.id] = {
                'parameters': service.parameters.copy(),
                'state_data': {}
            }
            
            # Pause the service (mock implementation)
            logger.info(f"Pausing service {service.id}")
            
            service.state = ServiceState.PAUSED
            service.paused_at = datetime.now()
            
            return True
        
        except Exception as e:
            service.last_error = str(e)
            return False
    
    def _resume_service(self, service: ServiceInfo) -> bool:
        """Resume a paused service."""
        if service.state != ServiceState.PAUSED:
            logger.error(f"Can only resume paused services. Current state: {service.state}")
            return False
        
        try:
            # Restore saved state
            saved_state = self._paused_services.get(service.id, {})
            
            # Resume the service (mock implementation)
            logger.info(f"Resuming service {service.id}")
            
            service.state = ServiceState.RUNNING
            service.paused_at = None
            
            # Remove from paused services
            if service.id in self._paused_services:
                del self._paused_services[service.id]
            
            return True
        
        except Exception as e:
            service.last_error = str(e)
            return False
    
    def _reload_config(self, service: ServiceInfo) -> bool:
        """Reload service configuration."""
        if service.state != ServiceState.RUNNING:
            logger.error(f"Can only reload config for running services")
            return False
        
        try:
            # Reload configuration (mock implementation)
            logger.info(f"Reloading configuration for {service.id}")
            
            # In real implementation, would send SIGHUP or similar
            if service.pid:
                # os.kill(service.pid, signal.SIGHUP)
                pass
            
            return True
        
        except Exception as e:
            service.last_error = str(e)
            return False
    
    def _update_parameters(self, service: ServiceInfo, parameters: Dict[str, Any]) -> bool:
        """Update service parameters."""
        try:
            # Update each parameter
            for param_name, new_value in parameters.items():
                # Update in parameter manager
                success = self._param_manager.set_value(
                    service_id=service.id,
                    parameter_name=param_name,
                    new_value=new_value,
                    changed_by="controller",
                    reason="Service control update"
                )
                
                if success:
                    # Update local copy
                    service.parameters[param_name] = new_value
                else:
                    logger.error(f"Failed to update parameter {param_name}")
                    return False
            
            return True
        
        except Exception as e:
            service.last_error = str(e)
            return False
    
    def _apply_parameter_live(self, service_id: str, parameter_name: str, new_value: Any):
        """Apply parameter change to running service."""
        service = self._services.get(service_id)
        
        if not service or service.state != ServiceState.RUNNING:
            return
        
        try:
            # Update local parameter copy
            service.parameters[parameter_name] = new_value
            
            # In real implementation, would communicate with service
            # to apply the parameter change (e.g., via IPC, API, etc.)
            logger.info(
                f"Applied parameter {parameter_name}={new_value} "
                f"to running service {service_id}"
            )
            
            # Notify hooks
            self._notify_control_hooks(service_id, 'parameter_applied', {
                'parameter': parameter_name,
                'value': new_value
            })
        
        except Exception as e:
            logger.error(f"Error applying live parameter update: {str(e)}")
    
    def register_control_hook(self, service_id: str, hook: callable):
        """Register a control hook for service events."""
        with self._lock:
            if service_id not in self._control_hooks:
                self._control_hooks[service_id] = []
            
            self._control_hooks[service_id].append(hook)
    
    def _notify_control_hooks(self, service_id: str, event: str, data: Dict[str, Any]):
        """Notify registered control hooks."""
        hooks = self._control_hooks.get(service_id, [])
        
        for hook in hooks:
            try:
                hook(service_id, event, data)
            except Exception as e:
                logger.error(f"Error in control hook: {str(e)}")
    
    def get_service_metrics(self, service_id: str) -> Dict[str, Any]:
        """Get service performance metrics."""
        service = self._services.get(service_id)
        
        if not service:
            return {}
        
        metrics = {
            'state': service.state.value,
            'uptime': service.uptime,
            'cpu_percent': service.cpu_percent,
            'memory_percent': service.memory_percent,
            'restart_count': service.restart_count
        }
        
        # Add pause duration if paused
        if service.paused_at:
            pause_duration = (datetime.now() - service.paused_at).total_seconds()
            metrics['pause_duration'] = pause_duration
        
        return metrics
    
    def export_service_states(self) -> Dict[str, Any]:
        """Export all service states for backup/restore."""
        with self._lock:
            return {
                'timestamp': datetime.now().isoformat(),
                'services': {
                    service_id: service.to_dict()
                    for service_id, service in self._services.items()
                },
                'paused_states': self._paused_services
            }


# Singleton instance
_controller: Optional[EnhancedServiceController] = None


def get_enhanced_controller() -> EnhancedServiceController:
    """Get the singleton enhanced controller instance."""
    global _controller
    if _controller is None:
        _controller = EnhancedServiceController()
    return _controller
