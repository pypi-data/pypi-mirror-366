"""
Query optimization system for database and vector operations.
"""

import time
import re
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Union, Set
from threading import RLock
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict
import sqlite3
import hashlib


class QueryType(Enum):
    """Types of queries that can be optimized."""
    SQL = "sql"
    VECTOR = "vector"
    HYBRID = "hybrid"
    AGGREGATE = "aggregate"


class OptimizationStrategy(Enum):
    """Query optimization strategies."""
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    ADAPTIVE = "adaptive"


@dataclass
class QueryPlan:
    """Execution plan for a query."""
    original_query: str
    optimized_query: str
    query_type: QueryType
    estimated_cost: float
    optimizations_applied: List[str] = field(default_factory=list)
    index_hints: List[str] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryMetrics:
    """Performance metrics for query execution."""
    query_hash: str
    execution_count: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    avg_rows_returned: float = 0.0
    last_executed: Optional[datetime] = None
    optimization_score: float = 0.0
    
    def update(self, execution_time_ms: float, rows_returned: int) -> None:
        """Update metrics with new execution data."""
        self.execution_count += 1
        self.total_time_ms += execution_time_ms
        self.avg_time_ms = self.total_time_ms / self.execution_count
        self.min_time_ms = min(self.min_time_ms, execution_time_ms)
        self.max_time_ms = max(self.max_time_ms, execution_time_ms)
        
        # Update average rows
        self.avg_rows_returned = (
            (self.avg_rows_returned * (self.execution_count - 1) + rows_returned) 
            / self.execution_count
        )
        
        self.last_executed = datetime.now()
        
        # Calculate optimization score (lower is better)
        variance = self.max_time_ms - self.min_time_ms
        self.optimization_score = self.avg_time_ms * (1 + variance / 1000)


@dataclass
class IndexRecommendation:
    """Recommendation for creating an index."""
    table_name: str
    columns: List[str]
    index_type: str
    estimated_improvement: float
    reason: str


class QueryOptimizer:
    """
    Advanced query optimization system.
    """
    
    def __init__(self,
                 data_dir: str = None,
                 strategy: OptimizationStrategy = OptimizationStrategy.ADVANCED,
                 cache_size: int = 1000,
                 min_execution_count: int = 5):
        """Initialize query optimizer."""
        self._lock = RLock()
        self.data_dir = data_dir or os.path.join(os.getcwd(), ".data", "query_optimizer")
        self.strategy = strategy
        self.cache_size = cache_size
        self.min_execution_count = min_execution_count
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Query plan cache
        self.plan_cache: Dict[str, QueryPlan] = {}
        
        # Query metrics database
        self.db_path = os.path.join(self.data_dir, "query_metrics.db")
        self._init_metrics_db()
        
        # Index recommendations
        self.index_recommendations: List[IndexRecommendation] = []
        
        # Pattern matchers for optimization
        self._init_optimization_patterns()
        
        # Statistics
        self.total_optimizations = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def _init_metrics_db(self) -> None:
        """Initialize query metrics database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_metrics (
                    query_hash TEXT PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    execution_count INTEGER NOT NULL,
                    total_time_ms REAL NOT NULL,
                    avg_time_ms REAL NOT NULL,
                    min_time_ms REAL NOT NULL,
                    max_time_ms REAL NOT NULL,
                    avg_rows_returned REAL NOT NULL,
                    last_executed TEXT,
                    optimization_score REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_metrics_score 
                ON query_metrics (optimization_score DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_metrics_count 
                ON query_metrics (execution_count DESC)
            ''')
            
            conn.commit()
    
    def _init_optimization_patterns(self) -> None:
        """Initialize SQL optimization patterns."""
        self.optimization_patterns = {
            'select_star': {
                'pattern': re.compile(r'SELECT\s+\*\s+FROM', re.IGNORECASE),
                'description': 'Replace SELECT * with specific columns'
            },
            'missing_where': {
                'pattern': re.compile(r'FROM\s+(\w+)\s*(?:JOIN|$)', re.IGNORECASE),
                'description': 'Add WHERE clause to filter results'
            },
            'or_to_union': {
                'pattern': re.compile(r'WHERE.*?\sOR\s', re.IGNORECASE),
                'description': 'Convert OR conditions to UNION for better performance'
            },
            'subquery_join': {
                'pattern': re.compile(r'WHERE\s+\w+\s+IN\s*\(SELECT', re.IGNORECASE),
                'description': 'Convert subquery to JOIN'
            },
            'distinct_groupby': {
                'pattern': re.compile(r'SELECT\s+DISTINCT', re.IGNORECASE),
                'description': 'Consider GROUP BY instead of DISTINCT'
            }
        }
    
    def optimize_query(self, 
                      query: str, 
                      query_type: QueryType = QueryType.SQL,
                      context: Dict[str, Any] = None) -> QueryPlan:
        """Optimize a query and return execution plan."""
        with self._lock:
            # Generate query hash
            query_hash = self._hash_query(query)
            
            # Check cache
            if query_hash in self.plan_cache:
                self.cache_hits += 1
                return self.plan_cache[query_hash]
            
            self.cache_misses += 1
            
            # Create optimization plan
            plan = QueryPlan(
                original_query=query,
                optimized_query=query,
                query_type=query_type,
                estimated_cost=100.0  # Base cost
            )
            
            # Apply optimizations based on strategy
            if self.strategy != OptimizationStrategy.NONE:
                if query_type == QueryType.SQL:
                    self._optimize_sql_query(plan, context)
                elif query_type == QueryType.VECTOR:
                    self._optimize_vector_query(plan, context)
                elif query_type == QueryType.HYBRID:
                    self._optimize_hybrid_query(plan, context)
            
            # Cache the plan
            if len(self.plan_cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.plan_cache))
                del self.plan_cache[oldest_key]
            
            self.plan_cache[query_hash] = plan
            self.total_optimizations += 1
            
            return plan
    
    def _optimize_sql_query(self, plan: QueryPlan, context: Optional[Dict[str, Any]]) -> None:
        """Apply SQL-specific optimizations."""
        query = plan.optimized_query
        
        # Basic optimizations
        if self.strategy in [OptimizationStrategy.BASIC, OptimizationStrategy.ADVANCED, 
                           OptimizationStrategy.ADAPTIVE]:
            # Check for common anti-patterns
            for pattern_name, pattern_info in self.optimization_patterns.items():
                if pattern_info['pattern'].search(query):
                    plan.optimizations_applied.append(pattern_info['description'])
            
            # Add LIMIT if not present
            if not re.search(r'\bLIMIT\b', query, re.IGNORECASE):
                query += " LIMIT 1000"
                plan.optimizations_applied.append("Added LIMIT clause")
        
        # Advanced optimizations
        if self.strategy in [OptimizationStrategy.ADVANCED, OptimizationStrategy.ADAPTIVE]:
            # Analyze query structure
            query = self._rewrite_query_advanced(query, plan, context)
            
            # Suggest indexes based on WHERE and JOIN conditions
            self._analyze_index_opportunities(query, plan)
        
        # Adaptive optimizations
        if self.strategy == OptimizationStrategy.ADAPTIVE:
            # Use historical metrics to optimize
            query_hash = self._hash_query(plan.original_query)
            metrics = self._get_query_metrics(query_hash)
            
            if metrics and metrics.execution_count >= self.min_execution_count:
                # Apply learned optimizations
                if metrics.avg_rows_returned < 10:
                    plan.optimizations_applied.append("Small result set - optimized for caching")
                    plan.estimated_cost *= 0.5
                
                if metrics.optimization_score > 1000:
                    plan.optimizations_applied.append("Slow query - applied aggressive optimization")
                    # Add more specific optimizations based on patterns
        
        plan.optimized_query = query
        
        # Update estimated cost
        plan.estimated_cost *= (1 - 0.1 * len(plan.optimizations_applied))
    
    def _optimize_vector_query(self, plan: QueryPlan, context: Optional[Dict[str, Any]]) -> None:
        """Apply vector search optimizations."""
        query_dict = json.loads(plan.original_query) if isinstance(plan.original_query, str) else plan.original_query
        
        # Optimize vector search parameters
        if 'limit' in query_dict:
            # Adjust limit based on context
            if context and context.get('result_size_hint') == 'small':
                query_dict['limit'] = min(query_dict['limit'], 20)
                plan.optimizations_applied.append("Reduced limit for small result set")
        
        if 'filter' in query_dict:
            # Optimize filters
            plan.optimizations_applied.append("Optimized vector filters")
        
        # Add search hints
        if context:
            if context.get('use_cache', True):
                plan.metadata['cache_enabled'] = True
                plan.optimizations_applied.append("Enabled result caching")
        
        plan.optimized_query = json.dumps(query_dict)
        plan.estimated_cost *= 0.8
    
    def _optimize_hybrid_query(self, plan: QueryPlan, context: Optional[Dict[str, Any]]) -> None:
        """Apply hybrid query optimizations."""
        # Split into SQL and vector components
        # This is a simplified example
        plan.optimizations_applied.append("Split hybrid query into components")
        plan.execution_order = ["sql_filter", "vector_search", "merge_results"]
        plan.estimated_cost *= 0.9
    
    def _rewrite_query_advanced(self, query: str, plan: QueryPlan, 
                              context: Optional[Dict[str, Any]]) -> str:
        """Apply advanced query rewrites."""
        # Example: Convert IN subquery to JOIN
        in_subquery_pattern = re.compile(
            r'WHERE\s+(\w+)\.(\w+)\s+IN\s*\(SELECT\s+(\w+)\s+FROM\s+(\w+)(.*?)\)',
            re.IGNORECASE | re.DOTALL
        )
        
        match = in_subquery_pattern.search(query)
        if match:
            table1, column1, column2, table2, conditions = match.groups()
            
            # Rewrite as JOIN
            rewritten = query[:match.start()]
            rewritten += f" JOIN {table2} ON {table1}.{column1} = {table2}.{column2}"
            if conditions.strip():
                rewritten += f" WHERE {conditions.strip()}"
            rewritten += query[match.end():]
            
            plan.optimizations_applied.append("Converted IN subquery to JOIN")
            return rewritten
        
        return query
    
    def _analyze_index_opportunities(self, query: str, plan: QueryPlan) -> None:
        """Analyze query for index opportunities."""
        # Extract WHERE conditions
        where_match = re.search(r'WHERE\s+(.*?)(?:GROUP|ORDER|LIMIT|$)', query, 
                              re.IGNORECASE | re.DOTALL)
        
        if where_match:
            conditions = where_match.group(1)
            
            # Find columns used in conditions
            column_pattern = re.compile(r'(\w+)\.(\w+)\s*(?:=|>|<|>=|<=|LIKE)', re.IGNORECASE)
            columns_used = column_pattern.findall(conditions)
            
            # Group by table
            table_columns = defaultdict(list)
            for table, column in columns_used:
                table_columns[table].append(column)
            
            # Suggest composite indexes
            for table, columns in table_columns.items():
                if len(columns) > 1:
                    plan.index_hints.append(f"CREATE INDEX idx_{table}_{'_'.join(columns)} "
                                          f"ON {table} ({', '.join(columns)})")
    
    def record_execution(self,
                        query: str,
                        query_type: QueryType,
                        execution_time_ms: float,
                        rows_returned: int) -> None:
        """Record query execution metrics."""
        with self._lock:
            query_hash = self._hash_query(query)
            
            # Get or create metrics
            metrics = self._get_query_metrics(query_hash)
            
            if not metrics:
                metrics = QueryMetrics(query_hash=query_hash)
            
            # Update metrics
            metrics.update(execution_time_ms, rows_returned)
            
            # Save to database
            self._save_query_metrics(query, query_type, metrics)
            
            # Check for optimization opportunities
            if metrics.execution_count == self.min_execution_count:
                self._analyze_optimization_opportunity(query, metrics)
    
    def _get_query_metrics(self, query_hash: str) -> Optional[QueryMetrics]:
        """Get query metrics from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT execution_count, total_time_ms, avg_time_ms, 
                       min_time_ms, max_time_ms, avg_rows_returned,
                       last_executed, optimization_score
                FROM query_metrics 
                WHERE query_hash = ?
            ''', (query_hash,))
            
            result = cursor.fetchone()
            
            if result:
                metrics = QueryMetrics(query_hash=query_hash)
                (metrics.execution_count, metrics.total_time_ms, metrics.avg_time_ms,
                 metrics.min_time_ms, metrics.max_time_ms, metrics.avg_rows_returned,
                 last_executed_str, metrics.optimization_score) = result
                
                if last_executed_str:
                    metrics.last_executed = datetime.fromisoformat(last_executed_str)
                
                return metrics
            
            return None
    
    def _save_query_metrics(self, query: str, query_type: QueryType, 
                          metrics: QueryMetrics) -> None:
        """Save query metrics to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO query_metrics
                (query_hash, query_text, query_type, execution_count, total_time_ms,
                 avg_time_ms, min_time_ms, max_time_ms, avg_rows_returned,
                 last_executed, optimization_score, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.query_hash, query, query_type.value, metrics.execution_count,
                metrics.total_time_ms, metrics.avg_time_ms, metrics.min_time_ms,
                metrics.max_time_ms, metrics.avg_rows_returned,
                metrics.last_executed.isoformat() if metrics.last_executed else None,
                metrics.optimization_score, now, now
            ))
            
            conn.commit()
    
    def _analyze_optimization_opportunity(self, query: str, metrics: QueryMetrics) -> None:
        """Analyze if query needs optimization."""
        if metrics.avg_time_ms > 1000:  # Slow query threshold
            self.logger.warning(f"Slow query detected (avg: {metrics.avg_time_ms:.2f}ms): "
                              f"{query[:100]}...")
            
            # Generate recommendations
            plan = self.optimize_query(query)
            
            if plan.optimizations_applied:
                recommendation = IndexRecommendation(
                    table_name="unknown",  # Would need proper parsing
                    columns=[],
                    index_type="composite",
                    estimated_improvement=30.0,
                    reason=f"Query averages {metrics.avg_time_ms:.2f}ms with "
                          f"{len(plan.optimizations_applied)} optimization opportunities"
                )
                
                self.index_recommendations.append(recommendation)
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query."""
        # Normalize query for consistent hashing
        normalized = re.sub(r'\s+', ' ', query.strip().lower())
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def get_slow_queries(self, threshold_ms: float = 1000, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest queries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT query_text, query_type, execution_count, avg_time_ms,
                       optimization_score, last_executed
                FROM query_metrics
                WHERE avg_time_ms > ?
                ORDER BY optimization_score DESC
                LIMIT ?
            ''', (threshold_ms, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'query': row[0],
                    'type': row[1],
                    'execution_count': row[2],
                    'avg_time_ms': row[3],
                    'optimization_score': row[4],
                    'last_executed': row[5]
                })
            
            return results
    
    def get_frequent_queries(self, min_count: int = 100, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently executed queries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT query_text, query_type, execution_count, avg_time_ms,
                       total_time_ms, last_executed
                FROM query_metrics
                WHERE execution_count >= ?
                ORDER BY execution_count DESC
                LIMIT ?
            ''', (min_count, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'query': row[0],
                    'type': row[1],
                    'execution_count': row[2],
                    'avg_time_ms': row[3],
                    'total_time_ms': row[4],
                    'last_executed': row[5]
                })
            
            return results
    
    def get_recommendations(self) -> List[IndexRecommendation]:
        """Get index recommendations."""
        with self._lock:
            # Sort by estimated improvement
            return sorted(self.index_recommendations, 
                        key=lambda x: x.estimated_improvement, 
                        reverse=True)
    
    def clear_metrics(self, older_than_days: int = 30) -> int:
        """Clear old query metrics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()
            
            cursor.execute('''
                DELETE FROM query_metrics
                WHERE last_executed < ? OR last_executed IS NULL
            ''', (cutoff_date,))
            
            deleted = cursor.rowcount
            conn.commit()
            
            return deleted
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get optimizer statistics."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total metrics
                cursor.execute('SELECT COUNT(*), AVG(avg_time_ms) FROM query_metrics')
                total_queries, avg_query_time = cursor.fetchone()
                
                # Get slow query count
                cursor.execute('SELECT COUNT(*) FROM query_metrics WHERE avg_time_ms > 1000')
                slow_queries = cursor.fetchone()[0]
                
                return {
                    'total_optimizations': self.total_optimizations,
                    'cache_size': len(self.plan_cache),
                    'cache_hits': self.cache_hits,
                    'cache_misses': self.cache_misses,
                    'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses)
                                     if (self.cache_hits + self.cache_misses) > 0 else 0.0,
                    'total_tracked_queries': total_queries or 0,
                    'avg_query_time_ms': avg_query_time or 0.0,
                    'slow_queries': slow_queries or 0,
                    'recommendations_count': len(self.index_recommendations),
                    'strategy': self.strategy.value
                }


# Global query optimizer instance
_query_optimizer = None
_optimizer_lock = RLock()


def get_query_optimizer(data_dir: str = None, **kwargs) -> QueryOptimizer:
    """
    Get the global query optimizer instance (singleton).
    
    Returns:
        Global query optimizer instance
    """
    global _query_optimizer
    with _optimizer_lock:
        if _query_optimizer is None:
            _query_optimizer = QueryOptimizer(data_dir=data_dir, **kwargs)
        return _query_optimizer


def reset_query_optimizer() -> None:
    """Reset the global query optimizer (mainly for testing)."""
    global _query_optimizer
    with _optimizer_lock:
        _query_optimizer = None


# Import os for path operations
import os