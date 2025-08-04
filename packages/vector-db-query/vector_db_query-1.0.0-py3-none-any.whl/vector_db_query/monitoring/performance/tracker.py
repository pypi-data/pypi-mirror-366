"""
Query performance tracking service.
"""

import asyncio
import logging
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from collections import defaultdict, deque
import numpy as np
from threading import RLock
import json
import hashlib

from .models import (
    QueryMetrics, QueryTrace, QueryTraceStep, QueryPlan,
    QueryPattern, PerformanceSnapshot, PerformanceTrend,
    OptimizationRecommendation, QueryType, QueryStatus,
    PerformanceGrade, QueryComplexity
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Tracks and analyzes query performance across the system.
    """
    
    def __init__(self, retention_hours: int = 24):
        """
        Initialize performance tracker.
        
        Args:
            retention_hours: Hours to retain performance data
        """
        self._lock = RLock()
        self.retention_hours = retention_hours
        self.change_tracker = get_change_tracker()
        
        # Active queries
        self._active_queries: Dict[str, QueryMetrics] = {}
        self._query_traces: Dict[str, QueryTrace] = {}
        
        # Historical data
        self._completed_queries: deque = deque(maxlen=10000)
        self._query_patterns: Dict[str, QueryPattern] = {}
        self._performance_snapshots: deque = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        
        # Trends
        self._performance_trends: Dict[str, PerformanceTrend] = {
            'response_time': PerformanceTrend('response_time', 24),
            'query_rate': PerformanceTrend('query_rate', 24),
            'error_rate': PerformanceTrend('error_rate', 24),
            'cpu_usage': PerformanceTrend('cpu_usage', 24),
            'memory_usage': PerformanceTrend('memory_usage', 24)
        }
        
        # Recommendations
        self._recommendations: Dict[str, OptimizationRecommendation] = {}
        
        # Callbacks
        self._performance_callbacks: List[Callable[[QueryMetrics], None]] = []
        self._anomaly_callbacks: List[Callable[[str, Any], None]] = []
        
        # Background tasks
        self._snapshot_task: Optional[asyncio.Task] = None
        self._analysis_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Statistics
        self._stats = {
            'queries_tracked': 0,
            'patterns_detected': 0,
            'recommendations_generated': 0,
            'anomalies_detected': 0
        }
        
        logger.info("PerformanceTracker initialized")
    
    async def start(self):
        """Start background tracking tasks."""
        self._snapshot_task = asyncio.create_task(self._snapshot_loop())
        self._analysis_task = asyncio.create_task(self._analysis_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Performance tracking started")
    
    async def stop(self):
        """Stop background tracking tasks."""
        tasks = [self._snapshot_task, self._analysis_task, self._cleanup_task]
        
        for task in tasks:
            if task:
                task.cancel()
        
        await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)
        
        logger.info("Performance tracking stopped")
    
    def start_query(self, query_type: QueryType, query_text: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start tracking a query.
        
        Args:
            query_type: Type of query
            query_text: Optional query text
            metadata: Optional metadata
            
        Returns:
            Query ID for tracking
        """
        metrics = QueryMetrics(
            query_type=query_type,
            status=QueryStatus.RUNNING,
            started_at=datetime.now()
        )
        
        # Create trace
        trace = QueryTrace(query_id=metrics.query_id)
        
        with self._lock:
            self._active_queries[metrics.query_id] = metrics
            self._query_traces[metrics.query_id] = trace
            self._stats['queries_tracked'] += 1
        
        # Log start
        logger.debug(f"Started tracking query {metrics.query_id} of type {query_type.value}")
        
        return metrics.query_id
    
    def add_trace_step(self, query_id: str, step_name: str, 
                      duration_ms: float, details: Optional[Dict[str, Any]] = None):
        """Add a trace step to a query."""
        with self._lock:
            trace = self._query_traces.get(query_id)
            if trace:
                trace.add_step(step_name, duration_ms, details)
    
    def update_query_metrics(self, query_id: str, **kwargs):
        """
        Update metrics for a query.
        
        Args:
            query_id: Query ID
            **kwargs: Metric updates
        """
        with self._lock:
            metrics = self._active_queries.get(query_id)
            if metrics:
                for key, value in kwargs.items():
                    if hasattr(metrics, key):
                        setattr(metrics, key, value)
    
    def complete_query(self, query_id: str, status: QueryStatus = QueryStatus.COMPLETED,
                      error_message: Optional[str] = None):
        """
        Mark a query as completed.
        
        Args:
            query_id: Query ID
            status: Final status
            error_message: Optional error message
        """
        with self._lock:
            metrics = self._active_queries.pop(query_id, None)
            trace = self._query_traces.pop(query_id, None)
            
            if not metrics:
                return
            
            # Update final metrics
            metrics.status = status
            metrics.error_message = error_message
            metrics.completed_at = datetime.now()
            
            # Calculate total time if not set
            if metrics.total_time_ms == 0:
                metrics.total_time_ms = (
                    metrics.completed_at - metrics.started_at
                ).total_seconds() * 1000
            
            # Store completed query
            self._completed_queries.append(metrics)
            
            # Update pattern detection
            self._update_patterns(metrics)
            
            # Check for anomalies
            self._check_anomalies(metrics)
            
            # Trigger callbacks
            for callback in self._performance_callbacks:
                try:
                    callback(metrics)
                except Exception as e:
                    logger.error(f"Error in performance callback: {e}")
        
        # Log completion
        logger.debug(
            f"Completed tracking query {query_id} with status {status.value} "
            f"in {metrics.total_time_ms:.0f}ms"
        )
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.MONITORING,
            change_type=ChangeType.UPDATE,
            description=f"Query {query_id} completed",
            details={
                'query_type': metrics.query_type.value,
                'duration_ms': metrics.total_time_ms,
                'status': status.value,
                'grade': metrics.calculate_grade().value
            }
        )
    
    def _update_patterns(self, metrics: QueryMetrics):
        """Update query patterns based on completed query."""
        # Simple pattern detection based on query type
        pattern_key = f"{metrics.query_type.value}"
        
        pattern = self._query_patterns.get(pattern_key)
        if not pattern:
            pattern = QueryPattern(
                pattern_type=metrics.query_type.value,
                description=f"Pattern for {metrics.query_type.value} queries",
                query_template=pattern_key
            )
            self._query_patterns[pattern_key] = pattern
            self._stats['patterns_detected'] += 1
        
        # Update pattern statistics
        pattern.frequency += 1
        pattern.last_seen = datetime.now()
        
        # Update performance metrics
        if pattern.min_duration_ms == float('inf'):
            pattern.min_duration_ms = metrics.total_time_ms
        else:
            pattern.min_duration_ms = min(pattern.min_duration_ms, metrics.total_time_ms)
        
        pattern.max_duration_ms = max(pattern.max_duration_ms, metrics.total_time_ms)
        
        # Update running average
        if pattern.avg_duration_ms == 0:
            pattern.avg_duration_ms = metrics.total_time_ms
        else:
            # Exponential moving average
            pattern.avg_duration_ms = (
                pattern.avg_duration_ms * 0.9 + metrics.total_time_ms * 0.1
            )
        
        # Update resource metrics
        if metrics.cpu_usage_percent > 0:
            if pattern.avg_cpu_percent == 0:
                pattern.avg_cpu_percent = metrics.cpu_usage_percent
            else:
                pattern.avg_cpu_percent = (
                    pattern.avg_cpu_percent * 0.9 + metrics.cpu_usage_percent * 0.1
                )
        
        if metrics.memory_used_mb > 0:
            if pattern.avg_memory_mb == 0:
                pattern.avg_memory_mb = metrics.memory_used_mb
            else:
                pattern.avg_memory_mb = (
                    pattern.avg_memory_mb * 0.9 + metrics.memory_used_mb * 0.1
                )
    
    def _check_anomalies(self, metrics: QueryMetrics):
        """Check for performance anomalies."""
        # Check against pattern averages
        pattern_key = f"{metrics.query_type.value}"
        pattern = self._query_patterns.get(pattern_key)
        
        if not pattern or pattern.frequency < 10:
            return  # Not enough data
        
        # Check for slow queries
        if metrics.total_time_ms > pattern.avg_duration_ms * 3:
            self._trigger_anomaly(
                'slow_query',
                {
                    'query_id': metrics.query_id,
                    'duration_ms': metrics.total_time_ms,
                    'expected_ms': pattern.avg_duration_ms,
                    'deviation_factor': metrics.total_time_ms / pattern.avg_duration_ms
                }
            )
        
        # Check for high resource usage
        if metrics.cpu_usage_percent > pattern.avg_cpu_percent * 2:
            self._trigger_anomaly(
                'high_cpu',
                {
                    'query_id': metrics.query_id,
                    'cpu_percent': metrics.cpu_usage_percent,
                    'expected_percent': pattern.avg_cpu_percent
                }
            )
    
    def _trigger_anomaly(self, anomaly_type: str, details: Dict[str, Any]):
        """Trigger anomaly callbacks."""
        self._stats['anomalies_detected'] += 1
        
        for callback in self._anomaly_callbacks:
            try:
                callback(anomaly_type, details)
            except Exception as e:
                logger.error(f"Error in anomaly callback: {e}")
    
    async def _snapshot_loop(self):
        """Take periodic performance snapshots."""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                await self._take_snapshot()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in snapshot loop: {e}")
    
    async def _take_snapshot(self):
        """Take a performance snapshot."""
        snapshot = PerformanceSnapshot()
        
        with self._lock:
            # Get recent queries (last minute)
            cutoff = datetime.now() - timedelta(minutes=1)
            recent_queries = [
                q for q in self._completed_queries 
                if q.started_at > cutoff
            ]
            
            if not recent_queries:
                return
            
            # Calculate metrics
            snapshot.total_queries = len(recent_queries)
            snapshot.queries_per_second = len(recent_queries) / 60.0
            
            # Grade distribution
            for query in recent_queries:
                grade = query.calculate_grade()
                snapshot.grade_distribution[grade] = \
                    snapshot.grade_distribution.get(grade, 0) + 1
            
            # Type distribution
            for query in recent_queries:
                snapshot.type_distribution[query.query_type] = \
                    snapshot.type_distribution.get(query.query_type, 0) + 1
            
            # Timing statistics
            response_times = [q.total_time_ms for q in recent_queries]
            if response_times:
                snapshot.avg_response_time_ms = np.mean(response_times)
                snapshot.median_response_time_ms = np.median(response_times)
                snapshot.p95_response_time_ms = np.percentile(response_times, 95)
                snapshot.p99_response_time_ms = np.percentile(response_times, 99)
            
            # Resource utilization
            cpu_values = [q.cpu_usage_percent for q in recent_queries if q.cpu_usage_percent > 0]
            if cpu_values:
                snapshot.avg_cpu_percent = np.mean(cpu_values)
                snapshot.peak_cpu_percent = np.max(cpu_values)
            
            memory_values = [q.memory_used_mb for q in recent_queries if q.memory_used_mb > 0]
            if memory_values:
                snapshot.avg_memory_mb = np.mean(memory_values)
                snapshot.peak_memory_mb = np.max(memory_values)
            
            # Cache performance
            cache_hits = sum(1 for q in recent_queries if q.cache_hit)
            snapshot.cache_hit_rate = cache_hits / len(recent_queries)
            
            # Error metrics
            errors = sum(1 for q in recent_queries if q.status != QueryStatus.COMPLETED)
            snapshot.error_rate = errors / len(recent_queries)
            
            timeouts = sum(1 for q in recent_queries if q.status == QueryStatus.TIMEOUT)
            snapshot.timeout_rate = timeouts / len(recent_queries)
            
            # Top issues
            slow_queries = sorted(
                recent_queries,
                key=lambda q: q.total_time_ms,
                reverse=True
            )[:5]
            snapshot.slowest_queries = [q.query_id for q in slow_queries]
            
            # Store snapshot
            self._performance_snapshots.append(snapshot)
            
            # Update trends
            self._update_trends(snapshot)
    
    def _update_trends(self, snapshot: PerformanceSnapshot):
        """Update performance trends."""
        timestamp = snapshot.timestamp
        
        # Response time trend
        self._performance_trends['response_time'].add_point(
            timestamp, snapshot.avg_response_time_ms
        )
        
        # Query rate trend
        self._performance_trends['query_rate'].add_point(
            timestamp, snapshot.queries_per_second
        )
        
        # Error rate trend
        self._performance_trends['error_rate'].add_point(
            timestamp, snapshot.error_rate
        )
        
        # CPU usage trend
        self._performance_trends['cpu_usage'].add_point(
            timestamp, snapshot.avg_cpu_percent
        )
        
        # Memory usage trend
        self._performance_trends['memory_usage'].add_point(
            timestamp, snapshot.avg_memory_mb
        )
    
    async def _analysis_loop(self):
        """Periodic performance analysis."""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                await self._analyze_performance()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
    
    async def _analyze_performance(self):
        """Analyze performance and generate recommendations."""
        with self._lock:
            # Analyze patterns
            for pattern in self._query_patterns.values():
                if pattern.frequency < 10:
                    continue
                
                # Calculate optimization score
                if pattern.avg_duration_ms > 500:  # Slow queries
                    pattern.optimization_score = min(
                        100,
                        (pattern.avg_duration_ms / 100) * pattern.frequency / 100
                    )
                    
                    # Generate recommendation
                    if pattern.optimization_score > 50:
                        self._generate_recommendation(pattern)
    
    def _generate_recommendation(self, pattern: QueryPattern):
        """Generate optimization recommendation for a pattern."""
        rec = OptimizationRecommendation(
            query_pattern_id=pattern.pattern_id,
            title=f"Optimize {pattern.pattern_type} queries",
            description=f"Queries of type {pattern.pattern_type} are averaging "
                       f"{pattern.avg_duration_ms:.0f}ms with {pattern.frequency} executions"
        )
        
        # Determine impact and effort
        if pattern.avg_duration_ms > 1000:
            rec.impact = "critical"
        elif pattern.avg_duration_ms > 500:
            rec.impact = "high"
        else:
            rec.impact = "medium"
        
        # Estimate improvements
        rec.expected_time_reduction_percent = min(50, pattern.avg_duration_ms / 20)
        rec.expected_resource_reduction_percent = min(30, pattern.avg_cpu_percent / 3)
        rec.affected_queries_per_hour = pattern.frequency / 24
        
        # Add implementation suggestions
        if pattern.pattern_type == QueryType.VECTOR_SEARCH.value:
            rec.implementation_type = "index"
            rec.implementation_steps = [
                "Review vector index configuration",
                "Consider HNSW index for better performance",
                "Optimize vector dimension if possible"
            ]
        elif pattern.pattern_type == QueryType.METADATA_FILTER.value:
            rec.implementation_type = "index"
            rec.implementation_steps = [
                "Add indexes on frequently filtered fields",
                "Consider composite indexes for common filter combinations"
            ]
        
        # Store recommendation
        self._recommendations[rec.recommendation_id] = rec
        self._stats['recommendations_generated'] += 1
        
        logger.info(f"Generated optimization recommendation: {rec.title}")
    
    async def _cleanup_loop(self):
        """Clean up old data periodically."""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def _cleanup_old_data(self):
        """Remove data older than retention period."""
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        
        with self._lock:
            # Clean completed queries
            while self._completed_queries and self._completed_queries[0].started_at < cutoff:
                self._completed_queries.popleft()
            
            # Clean patterns that haven't been seen recently
            stale_patterns = [
                key for key, pattern in self._query_patterns.items()
                if pattern.last_seen < cutoff
            ]
            for key in stale_patterns:
                del self._query_patterns[key]
    
    def get_active_queries(self) -> List[QueryMetrics]:
        """Get currently active queries."""
        with self._lock:
            return list(self._active_queries.values())
    
    def get_recent_queries(self, limit: int = 100) -> List[QueryMetrics]:
        """Get recent completed queries."""
        with self._lock:
            queries = list(self._completed_queries)
            return queries[-limit:]
    
    def get_query_patterns(self) -> List[QueryPattern]:
        """Get detected query patterns."""
        with self._lock:
            return list(self._query_patterns.values())
    
    def get_performance_trends(self) -> Dict[str, PerformanceTrend]:
        """Get performance trends."""
        with self._lock:
            return dict(self._performance_trends)
    
    def get_recommendations(self) -> List[OptimizationRecommendation]:
        """Get optimization recommendations."""
        with self._lock:
            return sorted(
                self._recommendations.values(),
                key=lambda r: r.calculate_priority_score(),
                reverse=True
            )
    
    def get_latest_snapshot(self) -> Optional[PerformanceSnapshot]:
        """Get the latest performance snapshot."""
        with self._lock:
            return self._performance_snapshots[-1] if self._performance_snapshots else None
    
    def get_statistics(self) -> Dict[str, int]:
        """Get tracker statistics."""
        with self._lock:
            return dict(self._stats)
    
    def add_performance_callback(self, callback: Callable[[QueryMetrics], None]):
        """Add a callback for query completion."""
        self._performance_callbacks.append(callback)
    
    def add_anomaly_callback(self, callback: Callable[[str, Any], None]):
        """Add a callback for anomaly detection."""
        self._anomaly_callbacks.append(callback)


# Singleton instance
_performance_tracker: Optional[PerformanceTracker] = None
_tracker_lock = RLock()


def get_performance_tracker() -> PerformanceTracker:
    """Get singleton performance tracker instance."""
    global _performance_tracker
    
    with _tracker_lock:
        if _performance_tracker is None:
            _performance_tracker = PerformanceTracker()
        
        return _performance_tracker


def reset_performance_tracker():
    """Reset the singleton performance tracker."""
    global _performance_tracker
    
    with _tracker_lock:
        if _performance_tracker:
            asyncio.create_task(_performance_tracker.stop())
        
        _performance_tracker = None