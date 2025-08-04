"""
Test performance optimization components.
"""

import os
import pytest
import time
import tempfile
import shutil
from datetime import datetime, timedelta
import threading
import sqlite3

from vector_db_query.monitoring.optimization import (
    CacheManager, CacheLevel, CacheStrategy, get_cache_manager,
    PerformanceOptimizer, OptimizationLevel, get_performance_optimizer,
    BatchProcessor, BatchConfig, BatchStrategy, get_batch_processor,
    ConnectionPoolManager, ConnectionType, PoolConfiguration, get_connection_pool_manager,
    LazyLoader, LoadStrategy, get_lazy_loader,
    QueryOptimizer, QueryType, OptimizationStrategy, get_query_optimizer
)


class TestCacheManager:
    """Test CacheManager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(
            data_dir=self.test_dir,
            max_memory_size_mb=10,
            max_disk_size_mb=50
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_memory_cache_operations(self):
        """Test basic memory cache operations."""
        # Set value
        assert self.cache_manager.set("key1", "value1", level=CacheLevel.MEMORY)
        
        # Get value
        assert self.cache_manager.get("key1") == "value1"
        
        # Delete value
        assert self.cache_manager.delete("key1")
        assert self.cache_manager.get("key1") is None
    
    def test_disk_cache_operations(self):
        """Test disk cache operations."""
        # Set large value to disk
        large_value = "x" * 1000
        assert self.cache_manager.set("large_key", large_value, level=CacheLevel.DISK)
        
        # Get from disk
        assert self.cache_manager.get("large_key", level=CacheLevel.DISK) == large_value
    
    def test_cache_expiration(self):
        """Test TTL expiration."""
        # Set with short TTL
        self.cache_manager.set("expire_key", "value", ttl_seconds=1)
        assert self.cache_manager.get("expire_key") == "value"
        
        # Wait for expiration
        time.sleep(1.1)
        assert self.cache_manager.get("expire_key") is None
    
    def test_cache_eviction(self):
        """Test cache eviction strategies."""
        # Fill cache
        for i in range(20):
            self.cache_manager.set(f"key{i}", f"value{i}" * 100)
        
        # Check that some entries were evicted
        stats = self.cache_manager.get_stats()
        assert stats.evictions > 0
    
    def test_cache_statistics(self):
        """Test cache statistics."""
        # Generate some activity
        self.cache_manager.set("stat_key1", "value1")
        self.cache_manager.get("stat_key1")  # Hit
        self.cache_manager.get("missing_key")  # Miss
        
        stats = self.cache_manager.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.hit_rate == 0.5


class TestPerformanceOptimizer:
    """Test PerformanceOptimizer functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.optimizer = PerformanceOptimizer(
            optimization_level=OptimizationLevel.BALANCED,
            monitor_interval_seconds=1
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        self.optimizer.shutdown()
    
    def test_monitoring_lifecycle(self):
        """Test monitoring start/stop."""
        # Start monitoring
        self.optimizer.start_monitoring()
        assert self.optimizer.monitoring_active
        
        # Let it collect some metrics
        time.sleep(2)
        
        # Stop monitoring
        self.optimizer.stop_monitoring()
        assert not self.optimizer.monitoring_active
        
        # Check metrics were collected
        summary = self.optimizer.get_metrics_summary()
        assert summary['metrics_count'] > 0
    
    def test_optimization_rules(self):
        """Test optimization rule management."""
        # Get initial rule count
        initial_count = len(self.optimizer.optimization_rules)
        
        # Add custom rule
        def custom_action():
            pass
        
        from vector_db_query.monitoring.optimization.performance_optimizer import OptimizationRule, ResourceType
        
        rule = OptimizationRule(
            name="test_rule",
            resource_type=ResourceType.CPU,
            threshold=50.0,
            duration_seconds=5,
            action=custom_action
        )
        
        self.optimizer.add_rule(rule)
        assert len(self.optimizer.optimization_rules) == initial_count + 1
        
        # Remove rule
        assert self.optimizer.remove_rule("test_rule")
        assert len(self.optimizer.optimization_rules) == initial_count
    
    def test_optimization_levels(self):
        """Test different optimization levels."""
        # Test level changes
        self.optimizer.set_optimization_level(OptimizationLevel.MINIMAL)
        assert self.optimizer.optimization_level == OptimizationLevel.MINIMAL
        
        self.optimizer.set_optimization_level(OptimizationLevel.AGGRESSIVE)
        assert self.optimizer.optimization_level == OptimizationLevel.AGGRESSIVE


class TestBatchProcessor:
    """Test BatchProcessor functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.results = []
        
        def processor_func(items):
            """Test processor function."""
            time.sleep(0.01)  # Simulate processing
            self.results.extend(items)
            return [f"processed_{item}" for item in items]
        
        self.processor = BatchProcessor(
            processor_func=processor_func,
            config=BatchConfig(
                max_batch_size=10,
                max_wait_time_ms=100,
                strategy=BatchStrategy.HYBRID
            )
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        self.processor.stop()
    
    def test_batch_processing(self):
        """Test basic batch processing."""
        # Start processor
        self.processor.start()
        
        # Add items
        for i in range(15):
            self.processor.add_item(f"item_{i}", f"data_{i}")
        
        # Wait for processing
        time.sleep(0.5)
        
        # Check results
        assert len(self.results) == 15
        assert all(item.startswith("data_") for item in self.results)
    
    def test_batch_statistics(self):
        """Test batch processor statistics."""
        self.processor.start()
        
        # Process some batches
        for i in range(25):
            self.processor.add_item(f"item_{i}", f"data_{i}")
        
        time.sleep(0.5)
        
        # Get statistics
        stats = self.processor.get_statistics()
        assert stats['total_items_processed'] == 25
        assert stats['total_batches'] > 0
        assert stats['average_batch_size'] > 0
    
    def test_priority_processing(self):
        """Test priority-based processing."""
        self.processor.start()
        
        # Add items with different priorities
        self.processor.add_item("low_priority", "data_low", priority=1)
        self.processor.add_item("high_priority", "data_high", priority=10)
        self.processor.add_item("medium_priority", "data_medium", priority=5)
        
        time.sleep(0.5)
        
        # High priority items should be processed first
        assert "data_high" in self.results


class TestConnectionPooling:
    """Test ConnectionPoolManager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.pool_manager = ConnectionPoolManager()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.pool_manager.shutdown_all()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_pool_creation(self):
        """Test connection pool creation."""
        from vector_db_query.monitoring.optimization.connection_pooling import (
            SQLiteConnectionFactory, ConnectionType, PoolConfiguration
        )
        
        # Create SQLite connection factory
        factory = SQLiteConnectionFactory(
            database_path=os.path.join(self.test_dir, "test.db")
        )
        
        # Create pool
        config = PoolConfiguration(min_size=2, max_size=5)
        pool = self.pool_manager.create_pool(
            "test_pool",
            ConnectionType.DATABASE,
            factory,
            config
        )
        
        assert pool is not None
        assert pool.name == "test_pool"
    
    def test_connection_lifecycle(self):
        """Test connection get/release lifecycle."""
        from vector_db_query.monitoring.optimization.connection_pooling import (
            SQLiteConnectionFactory, ConnectionType
        )
        
        factory = SQLiteConnectionFactory(
            database_path=os.path.join(self.test_dir, "test.db")
        )
        
        pool = self.pool_manager.create_pool(
            "lifecycle_pool",
            ConnectionType.DATABASE,
            factory
        )
        
        # Get connection
        with pool.get_connection() as conn:
            assert conn is not None
            # Use connection
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.commit()
        
        # Connection should be returned to pool
        stats = pool.get_statistics()
        assert stats['total_requests'] == 1
    
    def test_pool_statistics(self):
        """Test pool statistics."""
        from vector_db_query.monitoring.optimization.connection_pooling import (
            SQLiteConnectionFactory, ConnectionType
        )
        
        factory = SQLiteConnectionFactory(
            database_path=os.path.join(self.test_dir, "test.db")
        )
        
        pool = self.pool_manager.create_pool(
            "stats_pool",
            ConnectionType.DATABASE,
            factory
        )
        
        # Use connections
        for _ in range(5):
            with pool.get_connection() as conn:
                pass
        
        stats = pool.get_statistics()
        assert stats['total_requests'] == 5
        assert stats['total_connections'] > 0


class TestLazyLoader:
    """Test LazyLoader functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.loader = LazyLoader(max_memory_mb=10)
        self.loaded_resources = []
    
    def teardown_method(self):
        """Clean up test environment."""
        self.loader.shutdown()
    
    def test_lazy_loading(self):
        """Test lazy resource loading."""
        # Register resource
        def load_resource():
            self.loaded_resources.append("resource1")
            return {"data": "test_data"}
        
        self.loader.register(
            "resource1",
            load_resource,
            strategy=LoadStrategy.LAZY
        )
        
        # Resource should not be loaded yet
        assert len(self.loaded_resources) == 0
        
        # Get resource - should trigger loading
        resource = self.loader.get("resource1")
        assert resource == {"data": "test_data"}
        assert len(self.loaded_resources) == 1
        
        # Get again - should use cached version
        resource2 = self.loader.get("resource1")
        assert resource2 == {"data": "test_data"}
        assert len(self.loaded_resources) == 1  # Not loaded again
    
    def test_eager_loading(self):
        """Test eager resource loading."""
        def load_resource():
            return "eager_data"
        
        # Register with eager strategy
        self.loader.register(
            "eager_resource",
            load_resource,
            strategy=LoadStrategy.EAGER
        )
        
        # Should be loaded immediately
        time.sleep(0.1)
        stats = self.loader.get_statistics()
        assert stats['loaded_resources'] == 1
    
    def test_resource_dependencies(self):
        """Test resource dependency management."""
        # Register base resource
        self.loader.register(
            "base",
            lambda: {"base": "data"},
            strategy=LoadStrategy.EAGER
        )
        
        # Register dependent resource
        self.loader.register(
            "dependent",
            lambda: {"dependent": "data"},
            dependencies={"base"}
        )
        
        # Get dependent - should work since base is loaded
        resource = self.loader.get("dependent")
        assert resource is not None
    
    def test_loader_statistics(self):
        """Test loader statistics."""
        # Register and use resources
        self.loader.register("stat1", lambda: "data1")
        self.loader.register("stat2", lambda: "data2")
        
        self.loader.get("stat1")
        self.loader.get("stat1")  # Cache hit
        self.loader.get("stat2")
        self.loader.get("missing")  # Miss
        
        stats = self.loader.get_statistics()
        assert stats['total_resources'] == 2
        assert stats['loaded_resources'] == 2
        assert stats['cache_hits'] == 1
        assert stats['cache_misses'] == 2


class TestQueryOptimizer:
    """Test QueryOptimizer functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.optimizer = QueryOptimizer(
            data_dir=self.test_dir,
            strategy=OptimizationStrategy.ADVANCED
        )
    
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_sql_optimization(self):
        """Test SQL query optimization."""
        # Optimize a simple query
        query = "SELECT * FROM users WHERE status = 'active'"
        plan = self.optimizer.optimize_query(query, QueryType.SQL)
        
        assert plan.original_query == query
        assert len(plan.optimizations_applied) > 0
        assert "Added LIMIT clause" in plan.optimizations_applied
    
    def test_query_metrics_recording(self):
        """Test query metrics recording."""
        query = "SELECT id, name FROM products WHERE price > 100"
        
        # Record executions
        for i in range(10):
            self.optimizer.record_execution(
                query,
                QueryType.SQL,
                execution_time_ms=100 + i * 10,
                rows_returned=50
            )
        
        # Check metrics were recorded
        stats = self.optimizer.get_statistics()
        assert stats['total_tracked_queries'] > 0
    
    def test_slow_query_detection(self):
        """Test slow query detection."""
        # Record a slow query
        slow_query = "SELECT * FROM large_table"
        
        for _ in range(5):
            self.optimizer.record_execution(
                slow_query,
                QueryType.SQL,
                execution_time_ms=2000,
                rows_returned=10000
            )
        
        # Get slow queries
        slow_queries = self.optimizer.get_slow_queries(threshold_ms=1000)
        assert len(slow_queries) > 0
        assert slow_queries[0]['avg_time_ms'] > 1000
    
    def test_query_plan_caching(self):
        """Test query plan caching."""
        query = "SELECT * FROM users"
        
        # First optimization - cache miss
        plan1 = self.optimizer.optimize_query(query)
        initial_misses = self.optimizer.cache_misses
        
        # Second optimization - cache hit
        plan2 = self.optimizer.optimize_query(query)
        assert self.optimizer.cache_hits > 0
        assert plan1.optimized_query == plan2.optimized_query
    
    def test_index_recommendations(self):
        """Test index recommendation generation."""
        # Query with WHERE clause
        query = """
        SELECT * FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.status = 'pending' AND c.country = 'US'
        """
        
        plan = self.optimizer.optimize_query(query, QueryType.SQL)
        
        # Should have index hints
        assert len(plan.index_hints) > 0