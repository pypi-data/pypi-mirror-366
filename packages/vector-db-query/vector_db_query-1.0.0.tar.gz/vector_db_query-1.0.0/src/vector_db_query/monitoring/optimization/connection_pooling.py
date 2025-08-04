"""
Advanced connection pooling system for database and service connections.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union, Type
from threading import RLock, Semaphore, Event
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty, Full
import logging
from contextlib import contextmanager
import sqlite3
import psutil
from abc import ABC, abstractmethod


class ConnectionType(Enum):
    """Types of connections managed by the pool."""
    DATABASE = "database"
    HTTP = "http"
    QDRANT = "qdrant"
    REDIS = "redis"
    CUSTOM = "custom"


class ConnectionState(Enum):
    """Connection lifecycle states."""
    IDLE = "idle"
    ACTIVE = "active"
    TESTING = "testing"
    INVALID = "invalid"
    CLOSED = "closed"


@dataclass
class ConnectionStats:
    """Statistics for a single connection."""
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    use_count: int = 0
    total_duration_ms: float = 0.0
    error_count: int = 0
    last_error: Optional[str] = None
    
    @property
    def average_duration_ms(self) -> float:
        """Calculate average usage duration."""
        return self.total_duration_ms / self.use_count if self.use_count > 0 else 0.0
    
    @property
    def age_seconds(self) -> float:
        """Get connection age in seconds."""
        return (datetime.now() - self.created_at).total_seconds()


@dataclass
class PooledConnection:
    """Wrapper for pooled connections."""
    connection_id: str
    connection: Any
    connection_type: ConnectionType
    state: ConnectionState = ConnectionState.IDLE
    stats: ConnectionStats = field(default_factory=ConnectionStats)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def use(self) -> None:
        """Mark connection as in use."""
        self.state = ConnectionState.ACTIVE
        self.stats.last_used = datetime.now()
        self.stats.use_count += 1
    
    def release(self, duration_ms: float = 0.0) -> None:
        """Release connection back to pool."""
        self.state = ConnectionState.IDLE
        self.stats.total_duration_ms += duration_ms
    
    def mark_error(self, error: str) -> None:
        """Mark connection error."""
        self.stats.error_count += 1
        self.stats.last_error = error
        if self.stats.error_count >= 3:
            self.state = ConnectionState.INVALID


class ConnectionFactory(ABC):
    """Abstract factory for creating connections."""
    
    @abstractmethod
    def create_connection(self, **kwargs) -> Any:
        """Create a new connection."""
        pass
    
    @abstractmethod
    def validate_connection(self, connection: Any) -> bool:
        """Validate that connection is healthy."""
        pass
    
    @abstractmethod
    def close_connection(self, connection: Any) -> None:
        """Close a connection."""
        pass


class SQLiteConnectionFactory(ConnectionFactory):
    """Factory for SQLite connections."""
    
    def __init__(self, database_path: str, **kwargs):
        self.database_path = database_path
        self.connection_kwargs = kwargs
    
    def create_connection(self, **kwargs) -> sqlite3.Connection:
        """Create SQLite connection."""
        return sqlite3.connect(self.database_path, **self.connection_kwargs)
    
    def validate_connection(self, connection: sqlite3.Connection) -> bool:
        """Validate SQLite connection."""
        try:
            connection.execute("SELECT 1")
            return True
        except:
            return False
    
    def close_connection(self, connection: sqlite3.Connection) -> None:
        """Close SQLite connection."""
        try:
            connection.close()
        except:
            pass


@dataclass
class PoolConfiguration:
    """Connection pool configuration."""
    min_size: int = 2
    max_size: int = 10
    max_idle_time_seconds: int = 300
    connection_timeout_seconds: float = 5.0
    validation_interval_seconds: int = 60
    enable_statistics: bool = True
    enable_auto_scaling: bool = True
    scale_up_threshold: float = 0.8  # Scale up when 80% connections in use
    scale_down_threshold: float = 0.2  # Scale down when 20% connections in use


class ConnectionPoolManager:
    """
    Advanced connection pooling manager with multiple pool support.
    """
    
    def __init__(self):
        """Initialize connection pool manager."""
        self._lock = RLock()
        self.pools: Dict[str, 'ConnectionPool'] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_pool(self, 
                   pool_name: str,
                   connection_type: ConnectionType,
                   factory: ConnectionFactory,
                   config: PoolConfiguration = None) -> 'ConnectionPool':
        """Create a new connection pool."""
        with self._lock:
            if pool_name in self.pools:
                raise ValueError(f"Pool '{pool_name}' already exists")
            
            pool = ConnectionPool(
                name=pool_name,
                connection_type=connection_type,
                factory=factory,
                config=config or PoolConfiguration()
            )
            
            self.pools[pool_name] = pool
            pool.start()
            
            return pool
    
    def get_pool(self, pool_name: str) -> Optional['ConnectionPool']:
        """Get connection pool by name."""
        with self._lock:
            return self.pools.get(pool_name)
    
    def remove_pool(self, pool_name: str) -> bool:
        """Remove and shutdown a connection pool."""
        with self._lock:
            if pool_name in self.pools:
                pool = self.pools[pool_name]
                pool.shutdown()
                del self.pools[pool_name]
                return True
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics for all pools."""
        with self._lock:
            stats = {}
            for name, pool in self.pools.items():
                stats[name] = pool.get_statistics()
            return stats
    
    def shutdown_all(self) -> None:
        """Shutdown all connection pools."""
        with self._lock:
            for pool in self.pools.values():
                pool.shutdown()
            self.pools.clear()


class ConnectionPool:
    """
    Individual connection pool implementation.
    """
    
    def __init__(self,
                 name: str,
                 connection_type: ConnectionType,
                 factory: ConnectionFactory,
                 config: PoolConfiguration):
        """Initialize connection pool."""
        self.name = name
        self.connection_type = connection_type
        self.factory = factory
        self.config = config
        
        # Pool state
        self._lock = RLock()
        self.active = False
        self.connections: Dict[str, PooledConnection] = {}
        self.available_connections: Queue[str] = Queue()
        self.semaphore = Semaphore(config.max_size)
        
        # Statistics
        self.total_created = 0
        self.total_destroyed = 0
        self.total_requests = 0
        self.total_timeouts = 0
        self.total_errors = 0
        
        # Background threads
        self.validation_thread: Optional[threading.Thread] = None
        self.scaling_thread: Optional[threading.Thread] = None
        self.stop_event = Event()
        
        # Logger
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def start(self) -> None:
        """Start the connection pool."""
        with self._lock:
            if self.active:
                return
            
            self.active = True
            self.stop_event.clear()
            
            # Create minimum connections
            for _ in range(self.config.min_size):
                self._create_connection()
            
            # Start background threads
            if self.config.validation_interval_seconds > 0:
                self.validation_thread = threading.Thread(
                    target=self._validation_loop,
                    daemon=True,
                    name=f"{self.name}_validator"
                )
                self.validation_thread.start()
            
            if self.config.enable_auto_scaling:
                self.scaling_thread = threading.Thread(
                    target=self._scaling_loop,
                    daemon=True,
                    name=f"{self.name}_scaler"
                )
                self.scaling_thread.start()
            
            self.logger.info(f"Connection pool '{self.name}' started with {len(self.connections)} connections")
    
    def shutdown(self) -> None:
        """Shutdown the connection pool."""
        with self._lock:
            if not self.active:
                return
            
            self.active = False
            self.stop_event.set()
            
            # Wait for threads
            if self.validation_thread:
                self.validation_thread.join(timeout=5)
            if self.scaling_thread:
                self.scaling_thread.join(timeout=5)
            
            # Close all connections
            for conn_id, pooled_conn in self.connections.items():
                try:
                    self.factory.close_connection(pooled_conn.connection)
                except Exception as e:
                    self.logger.error(f"Error closing connection {conn_id}: {e}")
            
            self.connections.clear()
            self.logger.info(f"Connection pool '{self.name}' shutdown")
    
    @contextmanager
    def get_connection(self, timeout: Optional[float] = None):
        """Get a connection from the pool."""
        if not self.active:
            raise RuntimeError(f"Connection pool '{self.name}' is not active")
        
        timeout = timeout or self.config.connection_timeout_seconds
        conn_id = None
        pooled_conn = None
        start_time = time.time()
        
        try:
            # Acquire semaphore
            if not self.semaphore.acquire(timeout=timeout):
                self.total_timeouts += 1
                raise TimeoutError(f"Connection pool timeout after {timeout}s")
            
            # Get available connection
            try:
                conn_id = self.available_connections.get(timeout=timeout)
                pooled_conn = self.connections.get(conn_id)
                
                if not pooled_conn or pooled_conn.state == ConnectionState.INVALID:
                    # Connection is invalid, create new one
                    if pooled_conn:
                        self._destroy_connection(conn_id)
                    conn_id = self._create_connection()
                    pooled_conn = self.connections[conn_id]
                
            except Empty:
                # No available connections, create new one if possible
                if len(self.connections) < self.config.max_size:
                    conn_id = self._create_connection()
                    pooled_conn = self.connections[conn_id]
                else:
                    self.total_timeouts += 1
                    raise TimeoutError(f"No available connections in pool '{self.name}'")
            
            # Mark connection as active
            pooled_conn.use()
            self.total_requests += 1
            
            # Yield the actual connection
            yield pooled_conn.connection
            
            # Calculate usage duration
            duration_ms = (time.time() - start_time) * 1000
            pooled_conn.release(duration_ms)
            
        except Exception as e:
            self.total_errors += 1
            if pooled_conn:
                pooled_conn.mark_error(str(e))
            raise
            
        finally:
            # Return connection to pool
            if conn_id and pooled_conn and pooled_conn.state != ConnectionState.INVALID:
                self.available_connections.put(conn_id)
            
            # Release semaphore
            self.semaphore.release()
    
    def _create_connection(self) -> str:
        """Create a new connection."""
        conn_id = f"{self.name}_{self.total_created}"
        
        try:
            # Create actual connection
            connection = self.factory.create_connection()
            
            # Create pooled connection wrapper
            pooled_conn = PooledConnection(
                connection_id=conn_id,
                connection=connection,
                connection_type=self.connection_type
            )
            
            # Store connection
            self.connections[conn_id] = pooled_conn
            self.available_connections.put(conn_id)
            self.total_created += 1
            
            self.logger.debug(f"Created connection {conn_id}")
            return conn_id
            
        except Exception as e:
            self.logger.error(f"Failed to create connection: {e}")
            raise
    
    def _destroy_connection(self, conn_id: str) -> None:
        """Destroy a connection."""
        if conn_id not in self.connections:
            return
        
        pooled_conn = self.connections[conn_id]
        
        try:
            self.factory.close_connection(pooled_conn.connection)
        except Exception as e:
            self.logger.error(f"Error closing connection {conn_id}: {e}")
        
        del self.connections[conn_id]
        self.total_destroyed += 1
        
        self.logger.debug(f"Destroyed connection {conn_id}")
    
    def _validation_loop(self) -> None:
        """Background thread for connection validation."""
        while self.active and not self.stop_event.is_set():
            try:
                # Wait for validation interval
                self.stop_event.wait(self.config.validation_interval_seconds)
                
                if not self.active:
                    break
                
                # Validate connections
                with self._lock:
                    for conn_id, pooled_conn in list(self.connections.items()):
                        if pooled_conn.state == ConnectionState.IDLE:
                            # Check idle time
                            if pooled_conn.stats.last_used:
                                idle_time = (datetime.now() - pooled_conn.stats.last_used).total_seconds()
                                if idle_time > self.config.max_idle_time_seconds:
                                    self._destroy_connection(conn_id)
                                    continue
                            
                            # Validate connection
                            pooled_conn.state = ConnectionState.TESTING
                            try:
                                if not self.factory.validate_connection(pooled_conn.connection):
                                    pooled_conn.state = ConnectionState.INVALID
                                    self._destroy_connection(conn_id)
                                else:
                                    pooled_conn.state = ConnectionState.IDLE
                            except Exception:
                                pooled_conn.state = ConnectionState.INVALID
                                self._destroy_connection(conn_id)
                
            except Exception as e:
                self.logger.error(f"Error in validation loop: {e}")
    
    def _scaling_loop(self) -> None:
        """Background thread for auto-scaling."""
        while self.active and not self.stop_event.is_set():
            try:
                # Wait for scaling check interval
                self.stop_event.wait(10)  # Check every 10 seconds
                
                if not self.active:
                    break
                
                with self._lock:
                    total_connections = len(self.connections)
                    available_count = self.available_connections.qsize()
                    in_use_count = total_connections - available_count
                    
                    if total_connections > 0:
                        usage_ratio = in_use_count / total_connections
                        
                        # Scale up
                        if usage_ratio >= self.config.scale_up_threshold and total_connections < self.config.max_size:
                            new_connections = min(2, self.config.max_size - total_connections)
                            for _ in range(new_connections):
                                self._create_connection()
                            self.logger.info(f"Scaled up pool '{self.name}' to {len(self.connections)} connections")
                        
                        # Scale down
                        elif usage_ratio <= self.config.scale_down_threshold and total_connections > self.config.min_size:
                            # Remove idle connections
                            remove_count = min(2, total_connections - self.config.min_size)
                            removed = 0
                            
                            for conn_id, pooled_conn in list(self.connections.items()):
                                if removed >= remove_count:
                                    break
                                if pooled_conn.state == ConnectionState.IDLE:
                                    self._destroy_connection(conn_id)
                                    removed += 1
                            
                            if removed > 0:
                                self.logger.info(f"Scaled down pool '{self.name}' to {len(self.connections)} connections")
                
            except Exception as e:
                self.logger.error(f"Error in scaling loop: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self._lock:
            total_connections = len(self.connections)
            available_count = self.available_connections.qsize()
            in_use_count = total_connections - available_count
            
            # Calculate connection statistics
            total_uses = sum(conn.stats.use_count for conn in self.connections.values())
            total_errors = sum(conn.stats.error_count for conn in self.connections.values())
            avg_duration = sum(conn.stats.average_duration_ms for conn in self.connections.values()) / total_connections if total_connections > 0 else 0
            
            return {
                'name': self.name,
                'type': self.connection_type.value,
                'active': self.active,
                'total_connections': total_connections,
                'available_connections': available_count,
                'in_use_connections': in_use_count,
                'usage_percentage': (in_use_count / total_connections * 100) if total_connections > 0 else 0,
                'total_created': self.total_created,
                'total_destroyed': self.total_destroyed,
                'total_requests': self.total_requests,
                'total_timeouts': self.total_timeouts,
                'total_errors': self.total_errors,
                'connection_stats': {
                    'total_uses': total_uses,
                    'total_errors': total_errors,
                    'average_duration_ms': round(avg_duration, 2)
                },
                'config': {
                    'min_size': self.config.min_size,
                    'max_size': self.config.max_size,
                    'max_idle_time_seconds': self.config.max_idle_time_seconds
                }
            }


# Global connection pool manager
_pool_manager = None
_manager_lock = RLock()


def get_connection_pool_manager() -> ConnectionPoolManager:
    """
    Get the global connection pool manager instance (singleton).
    
    Returns:
        Global connection pool manager instance
    """
    global _pool_manager
    with _manager_lock:
        if _pool_manager is None:
            _pool_manager = ConnectionPoolManager()
        return _pool_manager


def reset_connection_pool_manager() -> None:
    """Reset the global connection pool manager (mainly for testing)."""
    global _pool_manager
    with _manager_lock:
        if _pool_manager:
            _pool_manager.shutdown_all()
        _pool_manager = None