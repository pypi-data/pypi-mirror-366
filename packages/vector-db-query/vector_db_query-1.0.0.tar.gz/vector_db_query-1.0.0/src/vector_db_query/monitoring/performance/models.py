"""
Data models for query performance tracking.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid


class QueryType(Enum):
    """Types of queries in the system."""
    VECTOR_SEARCH = "vector_search"
    HYBRID_SEARCH = "hybrid_search"
    METADATA_FILTER = "metadata_filter"
    AGGREGATION = "aggregation"
    BATCH_QUERY = "batch_query"
    DELETE = "delete"
    UPDATE = "update"
    INSERT = "insert"


class QueryStatus(Enum):
    """Query execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class PerformanceGrade(Enum):
    """Performance grade for queries."""
    EXCELLENT = "excellent"  # < 10ms
    GOOD = "good"           # 10-50ms
    ACCEPTABLE = "acceptable"  # 50-200ms
    SLOW = "slow"           # 200-1000ms
    CRITICAL = "critical"    # > 1000ms


class QueryComplexity(Enum):
    """Query complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXTREME = "extreme"


@dataclass
class QueryMetrics:
    """Metrics for a single query execution."""
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_type: QueryType = QueryType.VECTOR_SEARCH
    
    # Timing metrics (all in milliseconds)
    total_time_ms: float = 0.0
    planning_time_ms: float = 0.0
    execution_time_ms: float = 0.0
    fetch_time_ms: float = 0.0
    
    # Database-specific times
    db_connection_time_ms: float = 0.0
    db_query_time_ms: float = 0.0
    db_fetch_time_ms: float = 0.0
    
    # Vector-specific times
    vector_computation_time_ms: float = 0.0
    similarity_calc_time_ms: float = 0.0
    ranking_time_ms: float = 0.0
    
    # Resource metrics
    cpu_usage_percent: float = 0.0
    memory_used_mb: float = 0.0
    io_operations: int = 0
    
    # Result metrics
    results_returned: int = 0
    results_scanned: int = 0
    bytes_processed: int = 0
    
    # Cache metrics
    cache_hit: bool = False
    cache_partial_hit: bool = False
    cache_miss_reason: Optional[str] = None
    
    # Status and errors
    status: QueryStatus = QueryStatus.PENDING
    error_message: Optional[str] = None
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def calculate_grade(self) -> PerformanceGrade:
        """Calculate performance grade based on total time."""
        if self.total_time_ms < 10:
            return PerformanceGrade.EXCELLENT
        elif self.total_time_ms < 50:
            return PerformanceGrade.GOOD
        elif self.total_time_ms < 200:
            return PerformanceGrade.ACCEPTABLE
        elif self.total_time_ms < 1000:
            return PerformanceGrade.SLOW
        else:
            return PerformanceGrade.CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query_id': self.query_id,
            'query_type': self.query_type.value,
            'timing': {
                'total_ms': self.total_time_ms,
                'planning_ms': self.planning_time_ms,
                'execution_ms': self.execution_time_ms,
                'fetch_ms': self.fetch_time_ms
            },
            'database': {
                'connection_ms': self.db_connection_time_ms,
                'query_ms': self.db_query_time_ms,
                'fetch_ms': self.db_fetch_time_ms
            },
            'vector': {
                'computation_ms': self.vector_computation_time_ms,
                'similarity_ms': self.similarity_calc_time_ms,
                'ranking_ms': self.ranking_time_ms
            },
            'resources': {
                'cpu_percent': self.cpu_usage_percent,
                'memory_mb': self.memory_used_mb,
                'io_operations': self.io_operations
            },
            'results': {
                'returned': self.results_returned,
                'scanned': self.results_scanned,
                'bytes_processed': self.bytes_processed,
                'efficiency': self.results_returned / max(self.results_scanned, 1)
            },
            'cache': {
                'hit': self.cache_hit,
                'partial_hit': self.cache_partial_hit,
                'miss_reason': self.cache_miss_reason
            },
            'status': self.status.value,
            'error': self.error_message,
            'grade': self.calculate_grade().value,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class QueryTrace:
    """Detailed trace of query execution steps."""
    query_id: str
    steps: List['QueryTraceStep'] = field(default_factory=list)
    
    def add_step(self, name: str, duration_ms: float, details: Optional[Dict[str, Any]] = None):
        """Add a step to the trace."""
        step = QueryTraceStep(
            step_number=len(self.steps) + 1,
            name=name,
            duration_ms=duration_ms,
            details=details or {},
            timestamp=datetime.now()
        )
        self.steps.append(step)
    
    def get_critical_path(self) -> List['QueryTraceStep']:
        """Get the critical path (slowest steps)."""
        return sorted(self.steps, key=lambda s: s.duration_ms, reverse=True)[:5]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query_id': self.query_id,
            'steps': [step.to_dict() for step in self.steps],
            'total_steps': len(self.steps),
            'total_duration_ms': sum(s.duration_ms for s in self.steps),
            'critical_path': [s.to_dict() for s in self.get_critical_path()]
        }


@dataclass
class QueryTraceStep:
    """Individual step in query execution trace."""
    step_number: int
    name: str
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'step_number': self.step_number,
            'name': self.name,
            'duration_ms': self.duration_ms,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class QueryPlan:
    """Query execution plan."""
    query_id: str
    plan_type: str = "vector_search"
    estimated_cost: float = 0.0
    estimated_rows: int = 0
    
    # Plan components
    index_scan: bool = False
    index_name: Optional[str] = None
    filter_conditions: List[str] = field(default_factory=list)
    join_operations: List[str] = field(default_factory=list)
    sort_operations: List[str] = field(default_factory=list)
    
    # Optimization hints
    optimization_hints: List[str] = field(default_factory=list)
    missing_indexes: List[str] = field(default_factory=list)
    
    # Complexity assessment
    complexity: QueryComplexity = QueryComplexity.SIMPLE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query_id': self.query_id,
            'plan_type': self.plan_type,
            'estimated_cost': self.estimated_cost,
            'estimated_rows': self.estimated_rows,
            'components': {
                'index_scan': self.index_scan,
                'index_name': self.index_name,
                'filters': self.filter_conditions,
                'joins': self.join_operations,
                'sorts': self.sort_operations
            },
            'optimization': {
                'hints': self.optimization_hints,
                'missing_indexes': self.missing_indexes
            },
            'complexity': self.complexity.value
        }


@dataclass
class QueryPattern:
    """Detected query pattern for optimization."""
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: str = ""
    description: str = ""
    
    # Pattern characteristics
    query_template: str = ""
    parameter_variations: List[Dict[str, Any]] = field(default_factory=list)
    frequency: int = 0
    
    # Performance profile
    avg_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    
    # Resource profile
    avg_cpu_percent: float = 0.0
    avg_memory_mb: float = 0.0
    
    # Optimization potential
    optimization_score: float = 0.0  # 0-100
    suggested_optimizations: List[str] = field(default_factory=list)
    
    # Timestamps
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type,
            'description': self.description,
            'characteristics': {
                'template': self.query_template,
                'variations': len(self.parameter_variations),
                'frequency': self.frequency
            },
            'performance': {
                'avg_ms': self.avg_duration_ms,
                'min_ms': self.min_duration_ms,
                'max_ms': self.max_duration_ms,
                'p95_ms': self.p95_duration_ms
            },
            'resources': {
                'avg_cpu_percent': self.avg_cpu_percent,
                'avg_memory_mb': self.avg_memory_mb
            },
            'optimization': {
                'score': self.optimization_score,
                'suggestions': self.suggested_optimizations
            },
            'timestamps': {
                'first_seen': self.first_seen.isoformat(),
                'last_seen': self.last_seen.isoformat()
            }
        }


@dataclass
class PerformanceSnapshot:
    """Point-in-time performance snapshot."""
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Overall metrics
    total_queries: int = 0
    queries_per_second: float = 0.0
    
    # Performance distribution
    grade_distribution: Dict[PerformanceGrade, int] = field(default_factory=dict)
    type_distribution: Dict[QueryType, int] = field(default_factory=dict)
    
    # Timing statistics
    avg_response_time_ms: float = 0.0
    median_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    
    # Resource utilization
    avg_cpu_percent: float = 0.0
    peak_cpu_percent: float = 0.0
    avg_memory_mb: float = 0.0
    peak_memory_mb: float = 0.0
    
    # Cache performance
    cache_hit_rate: float = 0.0
    
    # Error metrics
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    
    # Top issues
    slowest_queries: List[str] = field(default_factory=list)
    most_frequent_errors: List[Tuple[str, int]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'snapshot_id': self.snapshot_id,
            'timestamp': self.timestamp.isoformat(),
            'overall': {
                'total_queries': self.total_queries,
                'queries_per_second': self.queries_per_second
            },
            'distribution': {
                'by_grade': {k.value: v for k, v in self.grade_distribution.items()},
                'by_type': {k.value: v for k, v in self.type_distribution.items()}
            },
            'timing': {
                'avg_ms': self.avg_response_time_ms,
                'median_ms': self.median_response_time_ms,
                'p95_ms': self.p95_response_time_ms,
                'p99_ms': self.p99_response_time_ms
            },
            'resources': {
                'avg_cpu_percent': self.avg_cpu_percent,
                'peak_cpu_percent': self.peak_cpu_percent,
                'avg_memory_mb': self.avg_memory_mb,
                'peak_memory_mb': self.peak_memory_mb
            },
            'cache': {
                'hit_rate': self.cache_hit_rate
            },
            'errors': {
                'error_rate': self.error_rate,
                'timeout_rate': self.timeout_rate,
                'frequent_errors': self.most_frequent_errors
            },
            'issues': {
                'slowest_queries': self.slowest_queries
            }
        }


@dataclass
class PerformanceTrend:
    """Performance trend analysis."""
    metric_name: str
    period_hours: int = 24
    
    # Trend data points
    timestamps: List[datetime] = field(default_factory=list)
    values: List[float] = field(default_factory=list)
    
    # Statistical analysis
    mean_value: float = 0.0
    std_deviation: float = 0.0
    trend_direction: str = "stable"  # increasing, decreasing, stable, volatile
    trend_strength: float = 0.0  # 0-1
    
    # Anomalies
    anomaly_points: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Forecast
    next_hour_prediction: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    
    def add_point(self, timestamp: datetime, value: float):
        """Add a data point to the trend."""
        self.timestamps.append(timestamp)
        self.values.append(value)
        
        # Keep only data within the period
        cutoff = datetime.now() - timedelta(hours=self.period_hours)
        valid_indices = [i for i, t in enumerate(self.timestamps) if t > cutoff]
        
        self.timestamps = [self.timestamps[i] for i in valid_indices]
        self.values = [self.values[i] for i in valid_indices]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'metric_name': self.metric_name,
            'period_hours': self.period_hours,
            'data_points': len(self.values),
            'statistics': {
                'mean': self.mean_value,
                'std_deviation': self.std_deviation,
                'min': min(self.values) if self.values else 0,
                'max': max(self.values) if self.values else 0
            },
            'trend': {
                'direction': self.trend_direction,
                'strength': self.trend_strength
            },
            'anomalies': len(self.anomaly_points),
            'forecast': {
                'next_hour': self.next_hour_prediction,
                'confidence_interval': self.confidence_interval
            }
        }


@dataclass
class OptimizationRecommendation:
    """Query optimization recommendation."""
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_pattern_id: Optional[str] = None
    
    # Recommendation details
    title: str = ""
    description: str = ""
    impact: str = "medium"  # low, medium, high, critical
    effort: str = "medium"  # low, medium, high
    
    # Expected improvements
    expected_time_reduction_percent: float = 0.0
    expected_resource_reduction_percent: float = 0.0
    affected_queries_per_hour: int = 0
    
    # Implementation
    implementation_type: str = ""  # index, query_rewrite, cache, schema, configuration
    implementation_steps: List[str] = field(default_factory=list)
    sql_commands: List[str] = field(default_factory=list)
    
    # Status
    status: str = "pending"  # pending, in_progress, completed, rejected
    created_at: datetime = field(default_factory=datetime.now)
    implemented_at: Optional[datetime] = None
    
    def calculate_priority_score(self) -> float:
        """Calculate priority score for the recommendation."""
        impact_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        effort_scores = {"low": 3, "medium": 2, "high": 1}
        
        impact_score = impact_scores.get(self.impact, 2)
        effort_score = effort_scores.get(self.effort, 2)
        
        # Higher score = higher priority
        base_score = (impact_score * 2 + effort_score) / 3
        
        # Adjust for expected improvements
        improvement_factor = (self.expected_time_reduction_percent + 
                            self.expected_resource_reduction_percent) / 200
        
        # Adjust for query frequency
        frequency_factor = min(self.affected_queries_per_hour / 100, 1.0)
        
        return base_score * (1 + improvement_factor + frequency_factor)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'recommendation_id': self.recommendation_id,
            'query_pattern_id': self.query_pattern_id,
            'details': {
                'title': self.title,
                'description': self.description,
                'impact': self.impact,
                'effort': self.effort,
                'priority_score': self.calculate_priority_score()
            },
            'expected_improvements': {
                'time_reduction_percent': self.expected_time_reduction_percent,
                'resource_reduction_percent': self.expected_resource_reduction_percent,
                'affected_queries_per_hour': self.affected_queries_per_hour
            },
            'implementation': {
                'type': self.implementation_type,
                'steps': self.implementation_steps,
                'sql_commands': self.sql_commands
            },
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'implemented_at': self.implemented_at.isoformat() if self.implemented_at else None
        }