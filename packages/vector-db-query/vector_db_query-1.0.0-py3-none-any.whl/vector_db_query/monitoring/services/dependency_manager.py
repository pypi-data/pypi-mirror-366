"""
Service dependency management for the monitoring dashboard.

This module provides service dependency tracking and management,
including dependency validation, startup ordering, and cascading operations.
"""

import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from threading import RLock
import json
from pathlib import Path

from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of service dependencies."""
    REQUIRED = "required"  # Must be running
    OPTIONAL = "optional"  # Should be running but not critical
    CONFLICT = "conflict"  # Cannot run simultaneously
    SEQUENCE = "sequence"  # Must start/stop in order


class ServiceStatus(Enum):
    """Service status states."""
    UNKNOWN = "unknown"
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"


@dataclass
class ServiceDependency:
    """Represents a dependency relationship between services."""
    dependent_service: str
    required_service: str
    dependency_type: DependencyType
    required_status: ServiceStatus = ServiceStatus.RUNNING
    timeout_seconds: int = 30
    description: str = ""
    created_at: datetime = None
    created_by: str = "system"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ServiceDefinition:
    """Defines a service and its properties."""
    name: str
    display_name: str
    description: str = ""
    startup_timeout: int = 30
    shutdown_timeout: int = 15
    health_check_endpoint: Optional[str] = None
    restart_policy: str = "on_failure"  # always, on_failure, never
    priority: int = 0  # Higher priority starts first
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class DependencyValidationError(Exception):
    """Raised when dependency validation fails."""
    pass


class CircularDependencyError(DependencyValidationError):
    """Raised when circular dependencies are detected."""
    pass


class DependencyManager:
    """
    Manages service dependencies and orchestrates service operations.
    
    Provides dependency validation, startup ordering, health monitoring,
    and cascading operations for service management.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize dependency manager.
        
        Args:
            config_path: Path to dependency configuration file
        """
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # Service definitions and dependencies
        self._services: Dict[str, ServiceDefinition] = {}
        self._dependencies: List[ServiceDependency] = []
        self._service_status: Dict[str, ServiceStatus] = {}
        
        # Configuration
        self.config_path = Path(config_path) if config_path else Path("dependencies.json")
        
        # Load existing configuration
        self._load_configuration()
        
        # Validate dependencies
        self._validate_all_dependencies()
        
        logger.info(f"DependencyManager initialized with {len(self._services)} services and {len(self._dependencies)} dependencies")
    
    def add_service(self, service: ServiceDefinition) -> bool:
        """
        Add a service definition.
        
        Args:
            service: Service definition to add
            
        Returns:
            True if added successfully
        """
        with self._lock:
            try:
                # Validate service definition
                if not service.name or not service.display_name:
                    raise ValueError("Service name and display_name are required")
                
                # Add service
                old_service = self._services.get(service.name)
                self._services[service.name] = service
                
                # Initialize status if new
                if service.name not in self._service_status:
                    self._service_status[service.name] = ServiceStatus.UNKNOWN
                
                # Track change
                operation = "updated" if old_service else "added"
                self.change_tracker.track_change(
                    category=ChangeCategory.SERVICE,
                    change_type=ChangeType.UPDATE if old_service else ChangeType.CREATE,
                    description=f"Service {operation}: {service.name}",
                    details={
                        "service_name": service.name,
                        "display_name": service.display_name,
                        "operation": operation,
                        "old_service": asdict(old_service) if old_service else None,
                        "new_service": asdict(service)
                    }
                )
                
                # Save configuration
                self._save_configuration()
                
                logger.info(f"Service {operation}: {service.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add service {service.name}: {e}")
                return False
    
    def remove_service(self, service_name: str) -> bool:
        """
        Remove a service definition.
        
        Args:
            service_name: Name of service to remove
            
        Returns:
            True if removed successfully
        """
        with self._lock:
            try:
                if service_name not in self._services:
                    logger.warning(f"Service not found: {service_name}")
                    return False
                
                # Check for dependencies
                dependent_services = self.get_dependent_services(service_name)
                if dependent_services:
                    raise DependencyValidationError(
                        f"Cannot remove service {service_name}: "
                        f"It has dependents: {', '.join(dependent_services)}"
                    )
                
                # Remove service
                service = self._services.pop(service_name)
                self._service_status.pop(service_name, None)
                
                # Remove all dependencies involving this service
                self._dependencies = [
                    dep for dep in self._dependencies
                    if dep.dependent_service != service_name and dep.required_service != service_name
                ]
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.SERVICE,
                    change_type=ChangeType.DELETE,
                    description=f"Service removed: {service_name}",
                    details={
                        "service_name": service_name,
                        "removed_service": asdict(service)
                    }
                )
                
                # Save configuration
                self._save_configuration()
                
                logger.info(f"Service removed: {service_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to remove service {service_name}: {e}")
                return False
    
    def add_dependency(self, dependency: ServiceDependency) -> bool:
        """
        Add a service dependency.
        
        Args:
            dependency: Dependency to add
            
        Returns:
            True if added successfully
        """
        with self._lock:
            try:
                # Validate services exist
                if dependency.dependent_service not in self._services:
                    raise ValueError(f"Dependent service not found: {dependency.dependent_service}")
                
                if dependency.required_service not in self._services:
                    raise ValueError(f"Required service not found: {dependency.required_service}")
                
                # Check for existing dependency
                existing = self._find_dependency(dependency.dependent_service, dependency.required_service)
                if existing:
                    # Update existing
                    existing.dependency_type = dependency.dependency_type
                    existing.required_status = dependency.required_status
                    existing.timeout_seconds = dependency.timeout_seconds
                    existing.description = dependency.description
                    operation = "updated"
                else:
                    # Add new
                    self._dependencies.append(dependency)
                    operation = "added"
                
                # Validate no circular dependencies
                self._validate_circular_dependencies()
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.DEPENDENCY,
                    change_type=ChangeType.UPDATE if existing else ChangeType.CREATE,
                    description=f"Dependency {operation}: {dependency.dependent_service} -> {dependency.required_service}",
                    details={
                        "dependent_service": dependency.dependent_service,
                        "required_service": dependency.required_service,
                        "dependency_type": dependency.dependency_type.value,
                        "operation": operation
                    }
                )
                
                # Save configuration
                self._save_configuration()
                
                logger.info(f"Dependency {operation}: {dependency.dependent_service} -> {dependency.required_service}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add dependency: {e}")
                return False
    
    def remove_dependency(self, dependent_service: str, required_service: str) -> bool:
        """
        Remove a service dependency.
        
        Args:
            dependent_service: Name of dependent service
            required_service: Name of required service
            
        Returns:
            True if removed successfully
        """
        with self._lock:
            try:
                dependency = self._find_dependency(dependent_service, required_service)
                if not dependency:
                    logger.warning(f"Dependency not found: {dependent_service} -> {required_service}")
                    return False
                
                # Remove dependency
                self._dependencies.remove(dependency)
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.DEPENDENCY,
                    change_type=ChangeType.DELETE,
                    description=f"Dependency removed: {dependent_service} -> {required_service}",
                    details={
                        "dependent_service": dependent_service,
                        "required_service": required_service,
                        "removed_dependency": asdict(dependency)
                    }
                )
                
                # Save configuration
                self._save_configuration()
                
                logger.info(f"Dependency removed: {dependent_service} -> {required_service}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to remove dependency: {e}")
                return False
    
    def get_startup_order(self, services: Optional[List[str]] = None) -> List[List[str]]:
        """
        Get the optimal startup order for services.
        
        Args:
            services: List of services to order (default: all services)
            
        Returns:
            List of service groups that can start in parallel
        """
        with self._lock:
            if services is None:
                services = list(self._services.keys())
            
            # Filter to existing services
            services = [s for s in services if s in self._services]
            
            if not services:
                return []
            
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(services)
            
            # Topological sort with priorities
            return self._topological_sort_with_priorities(services, dependency_graph)
    
    def get_shutdown_order(self, services: Optional[List[str]] = None) -> List[List[str]]:
        """
        Get the optimal shutdown order for services (reverse of startup).
        
        Args:
            services: List of services to order (default: all services)
            
        Returns:
            List of service groups that can stop in parallel
        """
        startup_order = self.get_startup_order(services)
        # Reverse the order for shutdown
        return list(reversed(startup_order))
    
    def validate_dependencies(self, service_name: str) -> Tuple[bool, List[str]]:
        """
        Validate that all dependencies for a service are satisfied.
        
        Args:
            service_name: Name of service to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        with self._lock:
            issues = []
            
            if service_name not in self._services:
                return False, [f"Service not found: {service_name}"]
            
            # Check all dependencies
            for dep in self._dependencies:
                if dep.dependent_service != service_name:
                    continue
                
                required_status = self._service_status.get(dep.required_service, ServiceStatus.UNKNOWN)
                
                if dep.dependency_type == DependencyType.REQUIRED:
                    if required_status != dep.required_status:
                        issues.append(
                            f"Required service {dep.required_service} is {required_status.value}, "
                            f"expected {dep.required_status.value}"
                        )
                
                elif dep.dependency_type == DependencyType.CONFLICT:
                    if required_status == ServiceStatus.RUNNING:
                        issues.append(f"Conflicting service {dep.required_service} is running")
            
            return len(issues) == 0, issues
    
    def get_dependent_services(self, service_name: str) -> List[str]:
        """
        Get list of services that depend on the given service.
        
        Args:
            service_name: Name of service
            
        Returns:
            List of dependent service names
        """
        with self._lock:
            return [
                dep.dependent_service for dep in self._dependencies
                if dep.required_service == service_name
            ]
    
    def get_required_services(self, service_name: str) -> List[str]:
        """
        Get list of services required by the given service.
        
        Args:
            service_name: Name of service
            
        Returns:
            List of required service names
        """
        with self._lock:
            return [
                dep.required_service for dep in self._dependencies
                if dep.dependent_service == service_name
            ]
    
    def update_service_status(self, service_name: str, status: ServiceStatus) -> bool:
        """
        Update the status of a service.
        
        Args:
            service_name: Name of service
            status: New status
            
        Returns:
            True if updated successfully
        """
        with self._lock:
            try:
                if service_name not in self._services:
                    logger.warning(f"Cannot update status for unknown service: {service_name}")
                    return False
                
                old_status = self._service_status.get(service_name, ServiceStatus.UNKNOWN)
                self._service_status[service_name] = status
                
                # Track change if status actually changed
                if old_status != status:
                    self.change_tracker.track_change(
                        category=ChangeCategory.SERVICE,
                        change_type=ChangeType.UPDATE,
                        description=f"Service status changed: {service_name} {old_status.value} -> {status.value}",
                        details={
                            "service_name": service_name,
                            "old_status": old_status.value,
                            "new_status": status.value
                        }
                    )
                    
                    logger.info(f"Service status updated: {service_name} -> {status.value}")
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to update service status: {e}")
                return False
    
    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete information about a service.
        
        Args:
            service_name: Name of service
            
        Returns:
            Service information dictionary or None if not found
        """
        with self._lock:
            if service_name not in self._services:
                return None
            
            service = self._services[service_name]
            status = self._service_status.get(service_name, ServiceStatus.UNKNOWN)
            
            # Get dependencies
            required = [
                {"service": dep.required_service, "type": dep.dependency_type.value}
                for dep in self._dependencies if dep.dependent_service == service_name
            ]
            
            dependents = [
                {"service": dep.dependent_service, "type": dep.dependency_type.value}
                for dep in self._dependencies if dep.required_service == service_name
            ]
            
            # Validate current dependencies
            is_valid, issues = self.validate_dependencies(service_name)
            
            return {
                "service": asdict(service),
                "status": status.value,
                "required_services": required,
                "dependent_services": dependents,
                "dependency_validation": {
                    "is_valid": is_valid,
                    "issues": issues
                }
            }
    
    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all services.
        
        Returns:
            Dictionary mapping service names to service info
        """
        with self._lock:
            result = {}
            for service_name in self._services:
                result[service_name] = self.get_service_info(service_name)
            return result
    
    def export_configuration(self) -> Dict[str, Any]:
        """
        Export complete dependency configuration.
        
        Returns:
            Configuration dictionary
        """
        with self._lock:
            return {
                "services": {name: asdict(service) for name, service in self._services.items()},
                "dependencies": [asdict(dep) for dep in self._dependencies],
                "service_status": {name: status.value for name, status in self._service_status.items()},
                "exported_at": datetime.now().isoformat()
            }
    
    def import_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Import dependency configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if imported successfully
        """
        with self._lock:
            try:
                # Clear existing configuration
                old_services = self._services.copy()
                old_dependencies = self._dependencies.copy()
                
                self._services.clear()
                self._dependencies.clear()
                self._service_status.clear()
                
                # Import services
                for name, service_data in config.get("services", {}).items():
                    service = ServiceDefinition(**service_data)
                    self._services[name] = service
                
                # Import dependencies
                for dep_data in config.get("dependencies", []):
                    # Convert datetime string back to datetime object
                    if isinstance(dep_data.get("created_at"), str):
                        dep_data["created_at"] = datetime.fromisoformat(dep_data["created_at"])
                    
                    dependency = ServiceDependency(**dep_data)
                    self._dependencies.append(dependency)
                
                # Import service status
                for name, status_str in config.get("service_status", {}).items():
                    self._service_status[name] = ServiceStatus(status_str)
                
                # Validate imported configuration
                self._validate_all_dependencies()
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.SYSTEM,
                    change_type=ChangeType.UPDATE,
                    description="Dependency configuration imported",
                    details={
                        "services_imported": len(self._services),
                        "dependencies_imported": len(self._dependencies),
                        "previous_services": len(old_services),
                        "previous_dependencies": len(old_dependencies)
                    }
                )
                
                # Save configuration
                self._save_configuration()
                
                logger.info(f"Configuration imported: {len(self._services)} services, {len(self._dependencies)} dependencies")
                return True
                
            except Exception as e:
                # Restore previous configuration on error
                self._services = old_services
                self._dependencies = old_dependencies
                logger.error(f"Failed to import configuration: {e}")
                return False
    
    def _find_dependency(self, dependent_service: str, required_service: str) -> Optional[ServiceDependency]:
        """Find existing dependency between two services."""
        for dep in self._dependencies:
            if dep.dependent_service == dependent_service and dep.required_service == required_service:
                return dep
        return None
    
    def _build_dependency_graph(self, services: List[str]) -> Dict[str, Set[str]]:
        """Build dependency graph for given services."""
        graph = {service: set() for service in services}
        
        for dep in self._dependencies:
            if (dep.dependent_service in services and 
                dep.required_service in services and
                dep.dependency_type in [DependencyType.REQUIRED, DependencyType.OPTIONAL]):
                
                graph[dep.dependent_service].add(dep.required_service)
        
        return graph
    
    def _topological_sort_with_priorities(self, services: List[str], graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Perform topological sort considering service priorities."""
        # Calculate in-degrees
        in_degree = {service: 0 for service in services}
        for service in services:
            for dependency in graph[service]:
                in_degree[dependency] += 1
        
        result = []
        remaining = set(services)
        
        while remaining:
            # Find services with no dependencies
            ready = [service for service in remaining if in_degree[service] == 0]
            
            if not ready:
                # Should not happen with valid dependencies
                raise CircularDependencyError("Circular dependency detected")
            
            # Sort by priority (higher priority first)
            ready.sort(key=lambda s: self._services[s].priority, reverse=True)
            
            result.append(ready)
            
            # Remove ready services and update in-degrees
            for service in ready:
                remaining.remove(service)
                for dependent in graph:
                    if service in graph[dependent]:
                        in_degree[dependent] -= 1
        
        return result
    
    def _validate_circular_dependencies(self):
        """Validate that there are no circular dependencies."""
        try:
            self.get_startup_order()
        except CircularDependencyError:
            raise CircularDependencyError("Circular dependency detected in service dependencies")
    
    def _validate_all_dependencies(self):
        """Validate all dependencies for consistency."""
        # Check that all referenced services exist
        all_services = set(self._services.keys())
        
        for dep in self._dependencies:
            if dep.dependent_service not in all_services:
                raise DependencyValidationError(f"Unknown dependent service: {dep.dependent_service}")
            
            if dep.required_service not in all_services:
                raise DependencyValidationError(f"Unknown required service: {dep.required_service}")
        
        # Check for circular dependencies
        self._validate_circular_dependencies()
    
    def _load_configuration(self):
        """Load configuration from file."""
        if not self.config_path.exists():
            logger.info(f"No configuration file found at {self.config_path}, starting with empty configuration")
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            if self.import_configuration(config):
                logger.info(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    def _save_configuration(self):
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = self.export_configuration()
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")


# Singleton instance
_dependency_manager: Optional[DependencyManager] = None
_manager_lock = RLock()


def get_dependency_manager(config_path: Optional[str] = None) -> DependencyManager:
    """
    Get singleton dependency manager instance.
    
    Args:
        config_path: Path to configuration file (only used on first call)
        
    Returns:
        DependencyManager instance
    """
    global _dependency_manager
    
    with _manager_lock:
        if _dependency_manager is None:
            _dependency_manager = DependencyManager(config_path)
        
        return _dependency_manager


def reset_dependency_manager():
    """Reset the singleton dependency manager (mainly for testing)."""
    global _dependency_manager
    
    with _manager_lock:
        _dependency_manager = None