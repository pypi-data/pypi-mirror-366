"""
Connection pool monitoring and management service.
"""

import asyncio
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from collections import defaultdict, deque
import json
from threading import RLock

from .models import (
    PoolType, ConnectionState, PoolHealth,
    PoolConnection, ConnectionPool, PoolMetrics,
    PoolEvent, PoolOptimization
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class PoolManager:
    """
    Manages and monitors connection pools across the system.
    """
    
    def __init__(self):
        """Initialize pool manager."""
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # Pool registry
        self._pools: Dict[str, ConnectionPool] = {}
        self._pool_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1440))  # 24 hours at 1-minute intervals
        self._pool_events: deque = deque(maxlen=10000)
        
        # Optimizations
        self._optimizations: Dict[str, List[PoolOptimization]] = defaultdict(list)
        
        # Monitoring
        self._monitor_callbacks: List[Callable[[str, PoolMetrics], None]] = []
        self._event_callbacks: List[Callable[[PoolEvent], None]] = []
        
        # Background tasks
        self._monitor_task: Optional[asyncio.Task] = None
        self._optimizer_task: Optional[asyncio.Task] = None
        
        # Statistics
        self._stats = {
            'pools_managed': 0,
            'total_connections': 0,
            'total_requests': 0,
            'optimizations_generated': 0
        }
        
        # Initialize default pools
        self._initialize_default_pools()
        
        logger.info("PoolManager initialized")
    
    def _initialize_default_pools(self):
        """Initialize default connection pools."""
        # Database pool
        db_pool = ConnectionPool(
            name="Main Database",
            pool_type=PoolType.DATABASE,
            min_size=2,
            max_size=20,
            target_size=5
        )
        self.register_pool(db_pool)
        
        # HTTP client pool
        http_pool = ConnectionPool(
            name="HTTP Client",
            pool_type=PoolType.HTTP,
            min_size=5,
            max_size=50,
            target_size=10,
            max_idle_seconds=120
        )
        self.register_pool(http_pool)
        
        # Qdrant pool
        qdrant_pool = ConnectionPool(
            name="Qdrant Vector DB",
            pool_type=PoolType.QDRANT,
            min_size=1,
            max_size=10,
            target_size=3
        )
        self.register_pool(qdrant_pool)
        
        # MCP pool
        mcp_pool = ConnectionPool(
            name="MCP Server",
            pool_type=PoolType.MCP,
            min_size=1,
            max_size=5,
            target_size=2
        )
        self.register_pool(mcp_pool)
    
    async def start(self):
        """Start monitoring tasks."""
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        self._optimizer_task = asyncio.create_task(self._optimizer_loop())
        
        logger.info("Pool monitoring started")
    
    async def stop(self):
        """Stop monitoring tasks."""
        tasks = [self._monitor_task, self._optimizer_task]
        
        for task in tasks:
            if task:
                task.cancel()
        
        await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)
        
        logger.info("Pool monitoring stopped")
    
    def register_pool(self, pool: ConnectionPool) -> str:
        """Register a connection pool for monitoring."""
        with self._lock:
            self._pools[pool.pool_id] = pool
            self._stats['pools_managed'] += 1
            
            # Create initial connections
            self._ensure_minimum_connections(pool)
            
            # Log event
            self._log_event(PoolEvent(
                pool_id=pool.pool_id,
                event_type="pool_registered",
                description=f"Pool '{pool.name}' registered",
                metadata={'pool_type': pool.pool_type.value}
            ))
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.MONITORING,
                change_type=ChangeType.CREATE,
                description=f"Registered connection pool: {pool.name}",
                details={'pool_id': pool.pool_id, 'type': pool.pool_type.value}
            )
        
        return pool.pool_id
    
    def _ensure_minimum_connections(self, pool: ConnectionPool):
        """Ensure pool has minimum connections."""
        current_size = len(pool.connections)
        
        while current_size < pool.min_size:
            conn = self._create_connection(pool)
            pool.connections[conn.connection_id] = conn
            current_size += 1
    
    def _create_connection(self, pool: ConnectionPool) -> PoolConnection:
        """Create a new connection."""
        conn = PoolConnection(
            pool_id=pool.pool_id,
            state=ConnectionState.IDLE,
            protocol=pool.pool_type.value
        )
        
        pool.total_connections_created += 1
        self._stats['total_connections'] += 1
        
        # Log event
        self._log_event(PoolEvent(
            pool_id=pool.pool_id,
            connection_id=conn.connection_id,
            event_type="connection_created",
            description="New connection created"
        ))
        
        return conn
    
    def acquire_connection(self, pool_id: str, request_id: Optional[str] = None) -> Optional[PoolConnection]:
        """Acquire a connection from the pool."""
        with self._lock:
            pool = self._pools.get(pool_id)
            if not pool:
                return None
            
            # Find idle connection
            for conn in pool.connections.values():
                if conn.state == ConnectionState.IDLE:
                    # Mark as active
                    conn.state = ConnectionState.ACTIVE
                    conn.last_used_at = datetime.now()
                    conn.use_count += 1
                    conn.current_request_id = request_id
                    conn.current_request_started = datetime.now()
                    
                    pool.total_requests_handled += 1
                    self._stats['total_requests'] += 1
                    
                    return conn
            
            # No idle connections, try to create new one
            if len(pool.connections) < pool.max_size:
                conn = self._create_connection(pool)
                conn.state = ConnectionState.ACTIVE
                conn.last_used_at = datetime.now()
                conn.use_count += 1
                conn.current_request_id = request_id
                conn.current_request_started = datetime.now()
                
                pool.connections[conn.connection_id] = conn
                pool.total_requests_handled += 1
                self._stats['total_requests'] += 1
                
                return conn
            
            # Pool exhausted
            self._log_event(PoolEvent(
                pool_id=pool_id,
                event_type="pool_exhausted",
                description="No connections available",
                severity="warning"
            ))
            
            return None
    
    def release_connection(self, connection_id: str, success: bool = True, error: Optional[str] = None):
        """Release a connection back to the pool."""
        with self._lock:
            # Find connection
            conn = None
            pool = None
            
            for p in self._pools.values():
                if connection_id in p.connections:
                    conn = p.connections[connection_id]
                    pool = p
                    break
            
            if not conn or not pool:
                return
            
            # Update connection state
            if conn.current_request_started:
                duration = (datetime.now() - conn.current_request_started).total_seconds() * 1000
                conn.last_activity_duration_ms = duration
                conn.total_time_active_ms += duration
            
            conn.state = ConnectionState.IDLE
            conn.current_request_id = None
            conn.current_request_started = None
            
            if not success:
                conn.error_count += 1
                conn.last_error = error
                pool.total_errors += 1
                
                # Check if connection should be marked as error
                if conn.error_count > 3:
                    conn.state = ConnectionState.ERROR
                    self._log_event(PoolEvent(
                        pool_id=pool.pool_id,
                        connection_id=connection_id,
                        event_type="connection_error",
                        description=f"Connection marked as error after {conn.error_count} failures",
                        severity="error"
                    ))
            
            # Check if connection is stale
            if conn.is_stale(pool.max_idle_seconds):
                conn.state = ConnectionState.STALE
    
    def destroy_connection(self, connection_id: str):
        """Destroy a connection."""
        with self._lock:
            # Find and remove connection
            for pool in self._pools.values():
                if connection_id in pool.connections:
                    conn = pool.connections.pop(connection_id)
                    pool.total_connections_destroyed += 1
                    
                    self._log_event(PoolEvent(
                        pool_id=pool.pool_id,
                        connection_id=connection_id,
                        event_type="connection_destroyed",
                        description=f"Connection destroyed (state: {conn.state.value})"
                    ))
                    
                    # Ensure minimum connections
                    self._ensure_minimum_connections(pool)
                    
                    break
    
    async def _monitor_loop(self):
        """Monitor pools periodically."""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                await self._monitor_pools()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
    
    async def _monitor_pools(self):
        """Monitor all pools and collect metrics."""
        with self._lock:
            for pool in self._pools.values():
                # Create metrics snapshot
                metrics = self._create_pool_metrics(pool)
                
                # Store metrics
                self._pool_metrics[pool.pool_id].append(metrics)
                
                # Check pool health
                self._check_pool_health(pool, metrics)
                
                # Clean up stale/error connections
                self._cleanup_connections(pool)
                
                # Trigger callbacks
                for callback in self._monitor_callbacks:
                    try:
                        callback(pool.pool_id, metrics)
                    except Exception as e:
                        logger.error(f"Error in monitor callback: {e}")
    
    def _create_pool_metrics(self, pool: ConnectionPool) -> PoolMetrics:
        """Create metrics snapshot for a pool."""
        counts = pool.get_connection_counts()
        
        metrics = PoolMetrics(pool_id=pool.pool_id)
        
        # Connection counts
        metrics.total_connections = len(pool.connections)
        metrics.active_connections = counts.get(ConnectionState.ACTIVE, 0)
        metrics.idle_connections = counts.get(ConnectionState.IDLE, 0)
        metrics.stale_connections = counts.get(ConnectionState.STALE, 0)
        
        # Performance metrics from connections
        if pool.connections:
            active_conns = pool.get_active_connections()
            if active_conns:
                metrics.avg_request_time_ms = sum(
                    c.last_activity_duration_ms for c in active_conns
                ) / len(active_conns)
            
            # Error rate
            total_requests = pool.total_requests_handled
            if total_requests > 0:
                metrics.error_rate = pool.total_errors / total_requests
        
        # Resource usage (simulated)
        try:
            process = psutil.Process()
            metrics.cpu_usage_percent = process.cpu_percent(interval=0.1)
            metrics.memory_used_mb = process.memory_info().rss / 1024 / 1024
        except:
            pass
        
        return metrics
    
    def _check_pool_health(self, pool: ConnectionPool, metrics: PoolMetrics):
        """Check and update pool health status."""
        old_health = pool.health_status
        
        # Determine health based on metrics
        if metrics.error_rate > 0.1:
            pool.health_status = PoolHealth.CRITICAL
        elif metrics.error_rate > 0.05 or metrics.stale_connections > pool.max_size * 0.3:
            pool.health_status = PoolHealth.DEGRADED
        elif metrics.active_connections == pool.max_size:
            pool.health_status = PoolHealth.WARNING
        else:
            pool.health_status = PoolHealth.HEALTHY
        
        pool.last_health_check = datetime.now()
        
        # Log health change
        if old_health != pool.health_status:
            self._log_event(PoolEvent(
                pool_id=pool.pool_id,
                event_type="health_changed",
                description=f"Health changed from {old_health.value} to {pool.health_status.value}",
                severity="warning" if pool.health_status != PoolHealth.HEALTHY else "info"
            ))
    
    def _cleanup_connections(self, pool: ConnectionPool):
        """Clean up stale and error connections."""
        to_destroy = []
        
        for conn_id, conn in pool.connections.items():
            if conn.state in [ConnectionState.STALE, ConnectionState.ERROR, ConnectionState.CLOSED]:
                to_destroy.append(conn_id)
        
        for conn_id in to_destroy:
            self.destroy_connection(conn_id)
    
    async def _optimizer_loop(self):
        """Generate optimization recommendations periodically."""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                await self._generate_optimizations()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimizer loop: {e}")
    
    async def _generate_optimizations(self):
        """Generate optimization recommendations for pools."""
        with self._lock:
            for pool in self._pools.values():
                # Skip if recent optimizations exist
                recent_opts = [
                    opt for opt in self._optimizations[pool.pool_id]
                    if opt.status == "pending" and 
                    (datetime.now() - opt.created_at).total_seconds() < 3600
                ]
                if recent_opts:
                    continue
                
                # Analyze recent metrics
                recent_metrics = list(self._pool_metrics[pool.pool_id])[-60:]  # Last hour
                if not recent_metrics:
                    continue
                
                # Generate recommendations based on patterns
                self._analyze_pool_sizing(pool, recent_metrics)
                self._analyze_pool_performance(pool, recent_metrics)
    
    def _analyze_pool_sizing(self, pool: ConnectionPool, metrics: List[PoolMetrics]):
        """Analyze pool sizing and generate recommendations."""
        if not metrics:
            return
        
        # Calculate average utilization
        avg_utilization = sum(
            (m.active_connections / max(m.total_connections, 1)) * 100 
            for m in metrics
        ) / len(metrics)
        
        # High utilization - recommend scaling up
        if avg_utilization > 80:
            opt = PoolOptimization(
                pool_id=pool.pool_id,
                title=f"Scale up {pool.name} pool",
                description=f"Pool utilization averaging {avg_utilization:.1f}%. "
                           f"Consider increasing pool size.",
                category="sizing",
                priority="high",
                suggested_max_size=min(pool.max_size * 2, 100),
                suggested_target_size=int(pool.target_size * 1.5),
                expected_improvement_percent=20
            )
            
            self._optimizations[pool.pool_id].append(opt)
            self._stats['optimizations_generated'] += 1
            
        # Low utilization - recommend scaling down
        elif avg_utilization < 20 and pool.min_size > 1:
            opt = PoolOptimization(
                pool_id=pool.pool_id,
                title=f"Scale down {pool.name} pool",
                description=f"Pool utilization averaging {avg_utilization:.1f}%. "
                           f"Consider reducing pool size to save resources.",
                category="cost",
                priority="medium",
                suggested_min_size=max(1, pool.min_size // 2),
                suggested_target_size=max(2, pool.target_size // 2),
                expected_cost_change_percent=-30
            )
            
            self._optimizations[pool.pool_id].append(opt)
            self._stats['optimizations_generated'] += 1
    
    def _analyze_pool_performance(self, pool: ConnectionPool, metrics: List[PoolMetrics]):
        """Analyze pool performance and generate recommendations."""
        if not metrics:
            return
        
        # Check error rates
        avg_error_rate = sum(m.error_rate for m in metrics) / len(metrics)
        
        if avg_error_rate > 0.05:
            opt = PoolOptimization(
                pool_id=pool.pool_id,
                title=f"Reduce errors in {pool.name} pool",
                description=f"Error rate averaging {avg_error_rate * 100:.1f}%. "
                           f"Consider adjusting timeouts or retry settings.",
                category="reliability",
                priority="critical" if avg_error_rate > 0.1 else "high",
                suggested_timeout_ms=pool.connection_timeout_ms * 2,
                expected_improvement_percent=50
            )
            
            self._optimizations[pool.pool_id].append(opt)
            self._stats['optimizations_generated'] += 1
    
    def _log_event(self, event: PoolEvent):
        """Log a pool event."""
        self._pool_events.append(event)
        
        # Trigger callbacks
        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")
    
    def get_pool(self, pool_id: str) -> Optional[ConnectionPool]:
        """Get a pool by ID."""
        with self._lock:
            return self._pools.get(pool_id)
    
    def get_all_pools(self) -> List[ConnectionPool]:
        """Get all registered pools."""
        with self._lock:
            return list(self._pools.values())
    
    def get_pool_metrics(self, pool_id: str, hours: int = 24) -> List[PoolMetrics]:
        """Get historical metrics for a pool."""
        with self._lock:
            metrics = list(self._pool_metrics[pool_id])
            
            # Filter by time range
            cutoff = datetime.now() - timedelta(hours=hours)
            return [m for m in metrics if m.timestamp > cutoff]
    
    def get_pool_events(self, pool_id: Optional[str] = None, hours: int = 24) -> List[PoolEvent]:
        """Get pool events."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            events = list(self._pool_events)
            
            # Filter by pool and time
            if pool_id:
                events = [e for e in events if e.pool_id == pool_id]
            
            return [e for e in events if e.timestamp > cutoff]
    
    def get_optimizations(self, pool_id: Optional[str] = None, 
                         status: Optional[str] = None) -> List[PoolOptimization]:
        """Get optimization recommendations."""
        with self._lock:
            if pool_id:
                opts = self._optimizations.get(pool_id, [])
            else:
                opts = []
                for pool_opts in self._optimizations.values():
                    opts.extend(pool_opts)
            
            if status:
                opts = [o for o in opts if o.status == status]
            
            return sorted(opts, key=lambda o: (
                {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(o.priority, 4),
                o.created_at
            ))
    
    def apply_optimization(self, recommendation_id: str) -> bool:
        """Apply an optimization recommendation."""
        with self._lock:
            # Find recommendation
            opt = None
            for pool_opts in self._optimizations.values():
                for o in pool_opts:
                    if o.recommendation_id == recommendation_id:
                        opt = o
                        break
            
            if not opt or opt.status != "pending":
                return False
            
            pool = self._pools.get(opt.pool_id)
            if not pool:
                return False
            
            # Apply suggested changes
            if opt.suggested_min_size is not None:
                pool.min_size = opt.suggested_min_size
            if opt.suggested_max_size is not None:
                pool.max_size = opt.suggested_max_size
            if opt.suggested_target_size is not None:
                pool.target_size = opt.suggested_target_size
            if opt.suggested_timeout_ms is not None:
                pool.connection_timeout_ms = opt.suggested_timeout_ms
            
            # Update optimization status
            opt.status = "implemented"
            opt.implemented_at = datetime.now()
            
            # Log event
            self._log_event(PoolEvent(
                pool_id=pool.pool_id,
                event_type="optimization_applied",
                description=f"Applied optimization: {opt.title}",
                metadata={'recommendation_id': recommendation_id}
            ))
            
            # Track change
            self.change_tracker.track_change(
                category=ChangeCategory.MONITORING,
                change_type=ChangeType.UPDATE,
                description=f"Applied pool optimization: {opt.title}",
                details={'pool_id': pool.pool_id, 'optimization': opt.to_dict()}
            )
            
            return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get manager statistics."""
        with self._lock:
            total_connections = sum(len(p.connections) for p in self._pools.values())
            active_connections = sum(
                len(p.get_active_connections()) for p in self._pools.values()
            )
            
            return {
                'pools_managed': self._stats['pools_managed'],
                'total_connections': total_connections,
                'active_connections': active_connections,
                'total_requests': self._stats['total_requests'],
                'optimizations_generated': self._stats['optimizations_generated'],
                'events_logged': len(self._pool_events)
            }
    
    def add_monitor_callback(self, callback: Callable[[str, PoolMetrics], None]):
        """Add a callback for pool monitoring."""
        self._monitor_callbacks.append(callback)
    
    def add_event_callback(self, callback: Callable[[PoolEvent], None]):
        """Add a callback for pool events."""
        self._event_callbacks.append(callback)


# Singleton instance
_pool_manager: Optional[PoolManager] = None
_manager_lock = RLock()


def get_pool_manager() -> PoolManager:
    """Get singleton pool manager instance."""
    global _pool_manager
    
    with _manager_lock:
        if _pool_manager is None:
            _pool_manager = PoolManager()
        
        return _pool_manager


def reset_pool_manager():
    """Reset the singleton pool manager."""
    global _pool_manager
    
    with _manager_lock:
        if _pool_manager:
            asyncio.create_task(_pool_manager.stop())
        
        _pool_manager = None