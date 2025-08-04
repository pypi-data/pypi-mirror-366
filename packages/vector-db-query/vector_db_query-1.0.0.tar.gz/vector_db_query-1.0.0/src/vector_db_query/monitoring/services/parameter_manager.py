"""
Service parameter management system for dynamic configuration.

This module provides functionality to adjust service parameters
at runtime without requiring service restarts.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import asyncio
from threading import RLock

from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class ParameterType(Enum):
    """Types of service parameters."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    LIST = "list"
    DICT = "dict"
    PATH = "path"
    URL = "url"
    ENUM = "enum"


class ParameterScope(Enum):
    """Scope of parameter application."""
    GLOBAL = "global"      # Affects all services
    SERVICE = "service"    # Affects specific service
    INSTANCE = "instance"  # Affects specific instance
    SESSION = "session"    # Temporary, session-only


@dataclass
class ParameterDefinition:
    """Definition of a service parameter."""
    name: str
    type: ParameterType
    description: str
    default_value: Any
    current_value: Any
    scope: ParameterScope = ParameterScope.SERVICE
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    validation_regex: Optional[str] = None
    requires_restart: bool = False
    sensitive: bool = False
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self, value: Any) -> bool:
        """Validate a value against parameter constraints."""
        # Type checking
        if self.type == ParameterType.INTEGER:
            if not isinstance(value, int):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
                
        elif self.type == ParameterType.FLOAT:
            if not isinstance(value, (int, float)):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
                
        elif self.type == ParameterType.BOOLEAN:
            if not isinstance(value, bool):
                return False
                
        elif self.type == ParameterType.STRING:
            if not isinstance(value, str):
                return False
            if self.validation_regex:
                import re
                if not re.match(self.validation_regex, value):
                    return False
                    
        elif self.type == ParameterType.LIST:
            if not isinstance(value, list):
                return False
                
        elif self.type == ParameterType.DICT:
            if not isinstance(value, dict):
                return False
                
        elif self.type == ParameterType.PATH:
            if not isinstance(value, str):
                return False
            # Could add path validation here
            
        elif self.type == ParameterType.URL:
            if not isinstance(value, str):
                return False
            # Could add URL validation here
            
        elif self.type == ParameterType.ENUM:
            if self.allowed_values and value not in self.allowed_values:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'type': self.type.value,
            'description': self.description,
            'default_value': self.default_value,
            'current_value': self.current_value,
            'scope': self.scope.value,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'allowed_values': self.allowed_values,
            'validation_regex': self.validation_regex,
            'requires_restart': self.requires_restart,
            'sensitive': self.sensitive,
            'category': self.category,
            'metadata': self.metadata
        }


@dataclass
class ParameterChange:
    """Record of a parameter change."""
    parameter_name: str
    service_id: str
    old_value: Any
    new_value: Any
    timestamp: datetime
    changed_by: str
    reason: Optional[str] = None
    applied: bool = False
    error: Optional[str] = None


class ParameterManager:
    """
    Manages service parameters and their runtime adjustments.
    
    Provides centralized parameter management with validation,
    persistence, and change tracking.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize parameter manager.
        
        Args:
            config_path: Path to parameter configuration file
        """
        self.config_path = config_path or str(
            Path.home() / ".vector_db_query" / "service_parameters.json"
        )
        self._lock = RLock()
        
        # Parameter definitions by service
        self._parameters: Dict[str, Dict[str, ParameterDefinition]] = {}
        
        # Change history
        self._change_history: List[ParameterChange] = []
        
        # Parameter change callbacks
        self._change_callbacks: Dict[str, List[Callable]] = {}
        
        # Change tracker integration
        self._change_tracker = get_change_tracker()
        
        # Load existing configuration
        self._load_configuration()
        
        # Register default parameters
        self._register_default_parameters()
        
        logger.info("ParameterManager initialized")
    
    def _load_configuration(self):
        """Load parameter configuration from file."""
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Load parameter values
                for service_id, params in config.get('parameters', {}).items():
                    if service_id not in self._parameters:
                        self._parameters[service_id] = {}
                    
                    for param_name, param_data in params.items():
                        # Update current values from saved config
                        if param_name in self._parameters[service_id]:
                            self._parameters[service_id][param_name].current_value = \
                                param_data.get('current_value')
                
                logger.info(f"Loaded parameter configuration from {config_file}")
            
            except Exception as e:
                logger.error(f"Error loading parameter configuration: {str(e)}")
    
    def _save_configuration(self):
        """Save current parameter configuration."""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            'version': '1.0',
            'updated_at': datetime.now().isoformat(),
            'parameters': {}
        }
        
        # Save current parameter values
        for service_id, params in self._parameters.items():
            config['parameters'][service_id] = {}
            
            for param_name, param_def in params.items():
                # Don't save sensitive values
                if not param_def.sensitive:
                    config['parameters'][service_id][param_name] = {
                        'current_value': param_def.current_value,
                        'last_modified': datetime.now().isoformat()
                    }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved parameter configuration to {config_file}")
        
        except Exception as e:
            logger.error(f"Error saving parameter configuration: {str(e)}")
    
    def _register_default_parameters(self):
        """Register default parameters for known services."""
        # Queue processor parameters
        self.register_parameter(
            service_id="queue_processor",
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
        
        self.register_parameter(
            service_id="queue_processor",
            parameter=ParameterDefinition(
                name="processing_interval",
                type=ParameterType.FLOAT,
                description="Seconds between processing cycles",
                default_value=5.0,
                current_value=5.0,
                min_value=0.1,
                max_value=60.0,
                category="performance"
            )
        )
        
        self.register_parameter(
            service_id="queue_processor",
            parameter=ParameterDefinition(
                name="max_retries",
                type=ParameterType.INTEGER,
                description="Maximum retry attempts for failed items",
                default_value=3,
                current_value=3,
                min_value=0,
                max_value=10,
                category="reliability"
            )
        )
        
        # MCP server parameters
        self.register_parameter(
            service_id="mcp_server",
            parameter=ParameterDefinition(
                name="connection_timeout",
                type=ParameterType.INTEGER,
                description="Connection timeout in seconds",
                default_value=30,
                current_value=30,
                min_value=5,
                max_value=300,
                category="network"
            )
        )
        
        self.register_parameter(
            service_id="mcp_server",
            parameter=ParameterDefinition(
                name="max_connections",
                type=ParameterType.INTEGER,
                description="Maximum concurrent connections",
                default_value=100,
                current_value=100,
                min_value=1,
                max_value=1000,
                category="performance"
            )
        )
        
        # Global parameters
        self.register_parameter(
            service_id="global",
            parameter=ParameterDefinition(
                name="log_level",
                type=ParameterType.ENUM,
                description="Global logging level",
                default_value="INFO",
                current_value="INFO",
                allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                scope=ParameterScope.GLOBAL,
                category="logging"
            )
        )
        
        self.register_parameter(
            service_id="global",
            parameter=ParameterDefinition(
                name="enable_metrics",
                type=ParameterType.BOOLEAN,
                description="Enable metrics collection",
                default_value=True,
                current_value=True,
                scope=ParameterScope.GLOBAL,
                category="monitoring"
            )
        )
    
    def register_parameter(
        self,
        service_id: str,
        parameter: ParameterDefinition
    ) -> bool:
        """
        Register a parameter definition for a service.
        
        Args:
            service_id: Service identifier
            parameter: Parameter definition
            
        Returns:
            Success status
        """
        with self._lock:
            if service_id not in self._parameters:
                self._parameters[service_id] = {}
            
            self._parameters[service_id][parameter.name] = parameter
            
            logger.info(
                f"Registered parameter '{parameter.name}' for service '{service_id}'"
            )
            
            return True
    
    def get_parameter(
        self,
        service_id: str,
        parameter_name: str
    ) -> Optional[ParameterDefinition]:
        """
        Get a parameter definition.
        
        Args:
            service_id: Service identifier
            parameter_name: Parameter name
            
        Returns:
            Parameter definition or None
        """
        with self._lock:
            return self._parameters.get(service_id, {}).get(parameter_name)
    
    def get_value(
        self,
        service_id: str,
        parameter_name: str,
        default: Any = None
    ) -> Any:
        """
        Get current parameter value.
        
        Args:
            service_id: Service identifier
            parameter_name: Parameter name
            default: Default if parameter not found
            
        Returns:
            Current parameter value
        """
        param = self.get_parameter(service_id, parameter_name)
        
        if param:
            return param.current_value
        
        # Check global parameters
        global_param = self.get_parameter("global", parameter_name)
        if global_param:
            return global_param.current_value
        
        return default
    
    def set_value(
        self,
        service_id: str,
        parameter_name: str,
        new_value: Any,
        changed_by: str = "system",
        reason: Optional[str] = None
    ) -> bool:
        """
        Set parameter value with validation.
        
        Args:
            service_id: Service identifier
            parameter_name: Parameter name
            new_value: New value to set
            changed_by: Who is making the change
            reason: Reason for change
            
        Returns:
            Success status
        """
        with self._lock:
            param = self.get_parameter(service_id, parameter_name)
            
            if not param:
                logger.error(
                    f"Parameter '{parameter_name}' not found for service '{service_id}'"
                )
                return False
            
            # Validate new value
            if not param.validate(new_value):
                logger.error(
                    f"Invalid value '{new_value}' for parameter '{parameter_name}'"
                )
                return False
            
            # Record old value
            old_value = param.current_value
            
            # Create change record
            change = ParameterChange(
                parameter_name=parameter_name,
                service_id=service_id,
                old_value=old_value,
                new_value=new_value,
                timestamp=datetime.now(),
                changed_by=changed_by,
                reason=reason
            )
            
            try:
                # Update value
                param.current_value = new_value
                change.applied = True
                
                # Save configuration
                self._save_configuration()
                
                # Track change
                self._change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATED,
                    entity_type="parameter",
                    entity_id=f"{service_id}.{parameter_name}",
                    entity_name=parameter_name,
                    description=f"Parameter '{parameter_name}' changed for {service_id}",
                    user=changed_by,
                    old_value=old_value,
                    new_value=new_value,
                    details={
                        'service_id': service_id,
                        'reason': reason,
                        'requires_restart': param.requires_restart
                    }
                )
                
                # Notify callbacks
                self._notify_callbacks(service_id, parameter_name, old_value, new_value)
                
                logger.info(
                    f"Updated parameter '{parameter_name}' for service '{service_id}': "
                    f"{old_value} -> {new_value}"
                )
                
                return True
            
            except Exception as e:
                change.error = str(e)
                logger.error(f"Error updating parameter: {str(e)}")
                return False
            
            finally:
                # Record change in history
                self._change_history.append(change)
    
    def get_service_parameters(self, service_id: str) -> Dict[str, ParameterDefinition]:
        """
        Get all parameters for a service.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Dictionary of parameters
        """
        with self._lock:
            service_params = self._parameters.get(service_id, {}).copy()
            
            # Include applicable global parameters
            global_params = self._parameters.get("global", {})
            for name, param in global_params.items():
                if param.scope == ParameterScope.GLOBAL:
                    service_params[f"global.{name}"] = param
            
            return service_params
    
    def get_all_parameters(self) -> Dict[str, Dict[str, ParameterDefinition]]:
        """Get all registered parameters."""
        with self._lock:
            return self._parameters.copy()
    
    def get_parameter_categories(self, service_id: str) -> List[str]:
        """
        Get unique parameter categories for a service.
        
        Args:
            service_id: Service identifier
            
        Returns:
            List of category names
        """
        params = self.get_service_parameters(service_id)
        categories = set(param.category for param in params.values())
        return sorted(list(categories))
    
    def register_change_callback(
        self,
        service_id: str,
        parameter_name: str,
        callback: Callable[[str, str, Any, Any], None]
    ):
        """
        Register callback for parameter changes.
        
        Args:
            service_id: Service identifier
            parameter_name: Parameter name (or '*' for all)
            callback: Function to call on change
        """
        key = f"{service_id}.{parameter_name}"
        
        with self._lock:
            if key not in self._change_callbacks:
                self._change_callbacks[key] = []
            
            self._change_callbacks[key].append(callback)
            
            logger.info(f"Registered change callback for {key}")
    
    def _notify_callbacks(
        self,
        service_id: str,
        parameter_name: str,
        old_value: Any,
        new_value: Any
    ):
        """Notify registered callbacks of parameter change."""
        # Specific parameter callbacks
        specific_key = f"{service_id}.{parameter_name}"
        callbacks = self._change_callbacks.get(specific_key, [])
        
        # Wildcard callbacks for service
        wildcard_key = f"{service_id}.*"
        callbacks.extend(self._change_callbacks.get(wildcard_key, []))
        
        # Global wildcard callbacks
        global_key = "*.*"
        callbacks.extend(self._change_callbacks.get(global_key, []))
        
        # Execute callbacks
        for callback in callbacks:
            try:
                callback(service_id, parameter_name, old_value, new_value)
            except Exception as e:
                logger.error(f"Error in parameter change callback: {str(e)}")
    
    def get_change_history(
        self,
        service_id: Optional[str] = None,
        parameter_name: Optional[str] = None,
        limit: int = 100
    ) -> List[ParameterChange]:
        """
        Get parameter change history.
        
        Args:
            service_id: Filter by service
            parameter_name: Filter by parameter
            limit: Maximum records to return
            
        Returns:
            List of parameter changes
        """
        with self._lock:
            history = self._change_history.copy()
            
            # Apply filters
            if service_id:
                history = [h for h in history if h.service_id == service_id]
            
            if parameter_name:
                history = [h for h in history if h.parameter_name == parameter_name]
            
            # Sort by timestamp descending
            history.sort(key=lambda x: x.timestamp, reverse=True)
            
            return history[:limit]
    
    def export_parameters(self, output_file: str):
        """
        Export all parameter definitions to file.
        
        Args:
            output_file: Output file path
        """
        export_data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'parameters': {}
        }
        
        with self._lock:
            for service_id, params in self._parameters.items():
                export_data['parameters'][service_id] = {
                    name: param.to_dict()
                    for name, param in params.items()
                    if not param.sensitive  # Don't export sensitive params
                }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported parameters to {output_file}")
    
    def import_parameters(self, input_file: str, merge: bool = True):
        """
        Import parameter definitions from file.
        
        Args:
            input_file: Input file path
            merge: Whether to merge with existing or replace
        """
        with open(input_file, 'r') as f:
            import_data = json.load(f)
        
        with self._lock:
            if not merge:
                self._parameters.clear()
            
            # Import parameters
            for service_id, params in import_data.get('parameters', {}).items():
                if service_id not in self._parameters:
                    self._parameters[service_id] = {}
                
                for name, param_data in params.items():
                    # Create parameter definition
                    param = ParameterDefinition(
                        name=param_data['name'],
                        type=ParameterType(param_data['type']),
                        description=param_data['description'],
                        default_value=param_data['default_value'],
                        current_value=param_data.get(
                            'current_value',
                            param_data['default_value']
                        ),
                        scope=ParameterScope(param_data.get('scope', 'service')),
                        min_value=param_data.get('min_value'),
                        max_value=param_data.get('max_value'),
                        allowed_values=param_data.get('allowed_values'),
                        validation_regex=param_data.get('validation_regex'),
                        requires_restart=param_data.get('requires_restart', False),
                        sensitive=param_data.get('sensitive', False),
                        category=param_data.get('category', 'general'),
                        metadata=param_data.get('metadata', {})
                    )
                    
                    self._parameters[service_id][name] = param
        
        # Save configuration
        self._save_configuration()
        
        logger.info(f"Imported parameters from {input_file}")


# Singleton instance
_parameter_manager: Optional[ParameterManager] = None


def get_parameter_manager() -> ParameterManager:
    """Get the singleton parameter manager instance."""
    global _parameter_manager
    if _parameter_manager is None:
        _parameter_manager = ParameterManager()
    return _parameter_manager
