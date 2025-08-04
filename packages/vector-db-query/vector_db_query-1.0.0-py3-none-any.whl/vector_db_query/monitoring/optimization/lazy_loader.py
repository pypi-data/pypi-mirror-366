"""
Lazy loading system for resource optimization.
"""

import os
import time
import weakref
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, Union, TypeVar, Generic, Set
from threading import RLock
from dataclasses import dataclass, field
from enum import Enum
import logging
import importlib
import inspect
from concurrent.futures import ThreadPoolExecutor, Future
from abc import ABC, abstractmethod


T = TypeVar('T')


class LoadStrategy(Enum):
    """Resource loading strategies."""
    EAGER = "eager"              # Load immediately
    LAZY = "lazy"                # Load on first access
    PRELOAD = "preload"          # Load in background
    ON_DEMAND = "on_demand"      # Load only when explicitly requested


class ResourceState(Enum):
    """Resource lifecycle states."""
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    UNLOADING = "unloading"


@dataclass
class ResourceMetadata:
    """Metadata for lazy-loaded resources."""
    name: str
    resource_type: str
    loader: Callable[[], Any]
    size_estimate_bytes: Optional[int] = None
    priority: int = 0
    ttl_seconds: Optional[int] = None
    dependencies: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceInfo:
    """Information about a loaded resource."""
    resource: Any
    metadata: ResourceMetadata
    state: ResourceState = ResourceState.NOT_LOADED
    loaded_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    load_time_ms: Optional[float] = None
    error: Optional[str] = None
    future: Optional[Future] = None
    
    def access(self) -> None:
        """Record resource access."""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def is_expired(self) -> bool:
        """Check if resource TTL has expired."""
        if not self.metadata.ttl_seconds or not self.loaded_at:
            return False
        
        expiry = self.loaded_at + timedelta(seconds=self.metadata.ttl_seconds)
        return datetime.now() > expiry


class ResourceLoader(ABC):
    """Abstract base class for resource loaders."""
    
    @abstractmethod
    def load(self) -> Any:
        """Load the resource."""
        pass
    
    @abstractmethod
    def unload(self, resource: Any) -> None:
        """Unload the resource."""
        pass
    
    @abstractmethod
    def estimate_size(self) -> int:
        """Estimate resource size in bytes."""
        pass


class ModuleLoader(ResourceLoader):
    """Loader for Python modules."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
    
    def load(self) -> Any:
        """Load Python module."""
        return importlib.import_module(self.module_name)
    
    def unload(self, resource: Any) -> None:
        """Unload Python module."""
        # Note: Python modules can't truly be unloaded, but we can delete references
        if hasattr(resource, '__name__'):
            module_name = resource.__name__
            if module_name in sys.modules:
                del sys.modules[module_name]
    
    def estimate_size(self) -> int:
        """Estimate module size."""
        # This is a rough estimate
        return 100 * 1024  # 100KB default estimate


class FileLoader(ResourceLoader):
    """Loader for file resources."""
    
    def __init__(self, file_path: str, mode: str = 'r', encoding: str = 'utf-8'):
        self.file_path = file_path
        self.mode = mode
        self.encoding = encoding
    
    def load(self) -> Any:
        """Load file content."""
        if 'b' in self.mode:
            with open(self.file_path, self.mode) as f:
                return f.read()
        else:
            with open(self.file_path, self.mode, encoding=self.encoding) as f:
                return f.read()
    
    def unload(self, resource: Any) -> None:
        """Unload file content."""
        # For files, we just let garbage collection handle it
        pass
    
    def estimate_size(self) -> int:
        """Get file size."""
        try:
            return os.path.getsize(self.file_path)
        except:
            return 0


class LazyLoader(Generic[T]):
    """
    Advanced lazy loading system for resource management.
    """
    
    def __init__(self,
                 max_memory_mb: int = 500,
                 default_strategy: LoadStrategy = LoadStrategy.LAZY,
                 cleanup_interval_seconds: int = 300,
                 max_workers: int = 5):
        """Initialize lazy loader."""
        self._lock = RLock()
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_strategy = default_strategy
        self.cleanup_interval = cleanup_interval_seconds
        
        # Resource registry
        self.resources: Dict[str, ResourceInfo] = {}
        self.weak_refs: Dict[str, weakref.ref] = {}
        
        # Loading queue and executor
        self.loading_queue: Set[str] = set()
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="LazyLoader")
        
        # Cleanup thread
        self.cleanup_thread: Optional[threading.Thread] = None
        self.cleanup_active = False
        
        # Statistics
        self.total_loads = 0
        self.total_unloads = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Callbacks
        self.load_callbacks: List[Callable[[str, Any], None]] = []
        self.unload_callbacks: List[Callable[[str], None]] = []
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def register(self,
                 name: str,
                 loader: Union[Callable[[], T], ResourceLoader],
                 resource_type: str = "generic",
                 size_estimate: Optional[int] = None,
                 priority: int = 0,
                 ttl_seconds: Optional[int] = None,
                 dependencies: Optional[Set[str]] = None,
                 strategy: Optional[LoadStrategy] = None) -> None:
        """Register a resource for lazy loading."""
        with self._lock:
            # Create loader function
            if isinstance(loader, ResourceLoader):
                loader_func = loader.load
                size_estimate = size_estimate or loader.estimate_size()
            else:
                loader_func = loader
            
            # Create metadata
            metadata = ResourceMetadata(
                name=name,
                resource_type=resource_type,
                loader=loader_func,
                size_estimate_bytes=size_estimate,
                priority=priority,
                ttl_seconds=ttl_seconds,
                dependencies=dependencies or set()
            )
            
            # Create resource info
            resource_info = ResourceInfo(
                resource=None,
                metadata=metadata
            )
            
            self.resources[name] = resource_info
            
            # Handle different strategies
            load_strategy = strategy or self.default_strategy
            
            if load_strategy == LoadStrategy.EAGER:
                # Load immediately
                self._load_resource(name)
            elif load_strategy == LoadStrategy.PRELOAD:
                # Load in background
                self._preload_resource(name)
    
    def get(self, name: str, timeout: Optional[float] = None) -> Optional[T]:
        """Get a resource, loading it if necessary."""
        with self._lock:
            if name not in self.resources:
                self.logger.error(f"Resource '{name}' not registered")
                return None
            
            resource_info = self.resources[name]
            
            # Check if already loaded
            if resource_info.state == ResourceState.LOADED:
                if not resource_info.is_expired():
                    resource_info.access()
                    self.cache_hits += 1
                    return resource_info.resource
                else:
                    # Expired, reload
                    self._unload_resource(name)
            
            # Check if currently loading
            if resource_info.state == ResourceState.LOADING:
                if resource_info.future:
                    # Wait for loading to complete
                    try:
                        self._lock.release()
                        resource_info.future.result(timeout=timeout)
                        self._lock.acquire()
                    except Exception as e:
                        self.logger.error(f"Error waiting for resource '{name}': {e}")
                        return None
            
            # Load resource if needed
            if resource_info.state in [ResourceState.NOT_LOADED, ResourceState.ERROR]:
                self.cache_misses += 1
                if not self._load_resource(name):
                    return None
            
            return resource_info.resource
    
    def _load_resource(self, name: str) -> bool:
        """Load a resource synchronously."""
        resource_info = self.resources[name]
        
        # Check dependencies first
        for dep in resource_info.metadata.dependencies:
            if dep not in self.resources or self.resources[dep].state != ResourceState.LOADED:
                self.logger.error(f"Dependency '{dep}' not loaded for resource '{name}'")
                return False
        
        # Check memory before loading
        if not self._ensure_memory_capacity(resource_info.metadata.size_estimate_bytes or 0):
            self.logger.error(f"Insufficient memory to load resource '{name}'")
            return False
        
        resource_info.state = ResourceState.LOADING
        start_time = time.time()
        
        try:
            # Load the resource
            resource = resource_info.metadata.loader()
            
            # Update resource info
            resource_info.resource = resource
            resource_info.state = ResourceState.LOADED
            resource_info.loaded_at = datetime.now()
            resource_info.load_time_ms = (time.time() - start_time) * 1000
            resource_info.error = None
            
            # Create weak reference
            self.weak_refs[name] = weakref.ref(resource, lambda ref: self._on_resource_deleted(name))
            
            self.total_loads += 1
            self.logger.info(f"Loaded resource '{name}' in {resource_info.load_time_ms:.2f}ms")
            
            # Notify callbacks
            self._notify_load(name, resource)
            
            return True
            
        except Exception as e:
            resource_info.state = ResourceState.ERROR
            resource_info.error = str(e)
            self.logger.error(f"Error loading resource '{name}': {e}")
            return False
    
    def _preload_resource(self, name: str) -> None:
        """Preload a resource in the background."""
        if name in self.loading_queue:
            return
        
        self.loading_queue.add(name)
        resource_info = self.resources[name]
        
        # Submit loading task
        future = self.executor.submit(self._load_resource_async, name)
        resource_info.future = future
        resource_info.state = ResourceState.LOADING
    
    def _load_resource_async(self, name: str) -> None:
        """Load resource asynchronously."""
        try:
            with self._lock:
                self._load_resource(name)
        finally:
            self.loading_queue.discard(name)
    
    def _unload_resource(self, name: str) -> None:
        """Unload a resource."""
        if name not in self.resources:
            return
        
        resource_info = self.resources[name]
        
        if resource_info.state != ResourceState.LOADED:
            return
        
        resource_info.state = ResourceState.UNLOADING
        
        try:
            # Check if resource has unloader
            if hasattr(resource_info.metadata.loader, '__self__') and \
               isinstance(resource_info.metadata.loader.__self__, ResourceLoader):
                resource_info.metadata.loader.__self__.unload(resource_info.resource)
            
            # Clear references
            resource_info.resource = None
            resource_info.state = ResourceState.NOT_LOADED
            
            # Remove weak reference
            if name in self.weak_refs:
                del self.weak_refs[name]
            
            self.total_unloads += 1
            self.logger.info(f"Unloaded resource '{name}'")
            
            # Notify callbacks
            self._notify_unload(name)
            
        except Exception as e:
            self.logger.error(f"Error unloading resource '{name}': {e}")
            resource_info.state = ResourceState.ERROR
    
    def _ensure_memory_capacity(self, required_bytes: int) -> bool:
        """Ensure memory capacity for new resource."""
        current_usage = self._estimate_memory_usage()
        
        if current_usage + required_bytes <= self.max_memory_bytes:
            return True
        
        # Try to free memory by unloading least recently used resources
        candidates = sorted(
            [(name, info) for name, info in self.resources.items() 
             if info.state == ResourceState.LOADED],
            key=lambda x: x[1].last_accessed or datetime.min
        )
        
        for name, info in candidates:
            if current_usage + required_bytes <= self.max_memory_bytes:
                return True
            
            # Skip if has dependents
            if any(name in r.metadata.dependencies for r in self.resources.values() 
                   if r.state == ResourceState.LOADED):
                continue
            
            # Unload resource
            self._unload_resource(name)
            current_usage = self._estimate_memory_usage()
        
        return current_usage + required_bytes <= self.max_memory_bytes
    
    def _estimate_memory_usage(self) -> int:
        """Estimate current memory usage."""
        total = 0
        for info in self.resources.values():
            if info.state == ResourceState.LOADED and info.metadata.size_estimate_bytes:
                total += info.metadata.size_estimate_bytes
        return total
    
    def _on_resource_deleted(self, name: str) -> None:
        """Handle resource garbage collection."""
        with self._lock:
            if name in self.resources:
                self.resources[name].state = ResourceState.NOT_LOADED
                self.logger.debug(f"Resource '{name}' was garbage collected")
    
    def start_cleanup(self) -> None:
        """Start automatic cleanup thread."""
        with self._lock:
            if not self.cleanup_active:
                self.cleanup_active = True
                self.cleanup_thread = threading.Thread(
                    target=self._cleanup_loop,
                    daemon=True,
                    name="LazyLoader_cleanup"
                )
                self.cleanup_thread.start()
    
    def stop_cleanup(self) -> None:
        """Stop automatic cleanup thread."""
        with self._lock:
            if self.cleanup_active:
                self.cleanup_active = False
                if self.cleanup_thread:
                    self.cleanup_thread.join(timeout=5)
    
    def _cleanup_loop(self) -> None:
        """Periodic cleanup of expired resources."""
        while self.cleanup_active:
            try:
                time.sleep(self.cleanup_interval)
                
                with self._lock:
                    # Find expired resources
                    expired = []
                    for name, info in self.resources.items():
                        if info.state == ResourceState.LOADED and info.is_expired():
                            expired.append(name)
                    
                    # Unload expired resources
                    for name in expired:
                        self._unload_resource(name)
                        self.logger.info(f"Cleaned up expired resource '{name}'")
                
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    def preload_priority(self, min_priority: int = 0) -> None:
        """Preload resources above a certain priority."""
        with self._lock:
            to_load = [
                (name, info) for name, info in self.resources.items()
                if info.state == ResourceState.NOT_LOADED and 
                   info.metadata.priority >= min_priority
            ]
            
            # Sort by priority (descending)
            to_load.sort(key=lambda x: x[1].metadata.priority, reverse=True)
            
            # Preload resources
            for name, _ in to_load:
                self._preload_resource(name)
    
    def unload_all(self) -> None:
        """Unload all loaded resources."""
        with self._lock:
            loaded_resources = [
                name for name, info in self.resources.items()
                if info.state == ResourceState.LOADED
            ]
            
            for name in loaded_resources:
                self._unload_resource(name)
    
    def add_load_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Add callback for resource load events."""
        with self._lock:
            self.load_callbacks.append(callback)
    
    def add_unload_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback for resource unload events."""
        with self._lock:
            self.unload_callbacks.append(callback)
    
    def _notify_load(self, name: str, resource: Any) -> None:
        """Notify callbacks of resource load."""
        for callback in self.load_callbacks:
            try:
                callback(name, resource)
            except Exception as e:
                self.logger.error(f"Error in load callback: {e}")
    
    def _notify_unload(self, name: str) -> None:
        """Notify callbacks of resource unload."""
        for callback in self.unload_callbacks:
            try:
                callback(name)
            except Exception as e:
                self.logger.error(f"Error in unload callback: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get loader statistics."""
        with self._lock:
            loaded_count = sum(1 for info in self.resources.values() 
                             if info.state == ResourceState.LOADED)
            
            return {
                'total_resources': len(self.resources),
                'loaded_resources': loaded_count,
                'loading_resources': len(self.loading_queue),
                'memory_usage_bytes': self._estimate_memory_usage(),
                'memory_limit_bytes': self.max_memory_bytes,
                'total_loads': self.total_loads,
                'total_unloads': self.total_unloads,
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) 
                           if (self.cache_hits + self.cache_misses) > 0 else 0.0
            }
    
    def shutdown(self) -> None:
        """Shutdown the lazy loader."""
        self.stop_cleanup()
        self.unload_all()
        self.executor.shutdown(wait=True)


# Global lazy loader instance
_lazy_loader = None
_loader_lock = RLock()


def get_lazy_loader(**kwargs) -> LazyLoader:
    """
    Get the global lazy loader instance (singleton).
    
    Returns:
        Global lazy loader instance
    """
    global _lazy_loader
    with _loader_lock:
        if _lazy_loader is None:
            _lazy_loader = LazyLoader(**kwargs)
        return _lazy_loader


def reset_lazy_loader() -> None:
    """Reset the global lazy loader (mainly for testing)."""
    global _lazy_loader
    with _loader_lock:
        if _lazy_loader:
            _lazy_loader.shutdown()
        _lazy_loader = None


# Import sys for module management
import sys