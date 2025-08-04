# Performance Testing & Optimization Guide

Comprehensive guide for testing and optimizing the Vector DB Query Data Sources system performance.

## Overview

The data sources system is designed to handle 500+ items daily with optimal performance. This guide covers:
- Performance testing procedures
- Optimization techniques
- Benchmarking tools
- Troubleshooting performance issues

## Quick Start

### Run Performance Tests

```bash
# Run all performance benchmarks
vdq performance benchmark

# Run quick benchmarks only
vdq performance benchmark --quick

# Run specific scenarios
vdq performance benchmark --scenarios throughput concurrency stress
```

### Optimize Configuration

```bash
# Analyze current configuration
vdq performance optimize --analyze

# Generate and apply optimizations
vdq performance optimize --optimize

# Preview changes without applying
vdq performance optimize --optimize --dry-run
```

### Stress Test

```bash
# Test with 500 items (default)
vdq performance stress

# Test with custom load
vdq performance stress --items 1000

# Custom source distribution
vdq performance stress --distribution gmail 0.6 fireflies 0.3 google_drive 0.1
```

## Performance Benchmarks

### Available Test Scenarios

1. **Throughput Test**
   - Tests overall system throughput
   - Measures items processed per second
   - Validates 500+ daily capacity

2. **Concurrency Test**
   - Tests different concurrency levels
   - Identifies optimal worker count
   - Measures scaling efficiency

3. **Memory Test**
   - Tests memory efficiency
   - Identifies memory leaks
   - Validates batch processing

4. **Deduplication Test**
   - Tests deduplication performance
   - Measures cache efficiency
   - Validates accuracy

5. **NLP Test**
   - Tests NLP processing speed
   - Measures entity extraction performance
   - Validates sentiment analysis

6. **Stress Test**
   - Simulates real-world load
   - Tests system limits
   - Validates reliability

### Running Benchmarks

```bash
# Full benchmark suite
vdq performance benchmark

# Output:
# ✓ Throughput benchmark completed
# ✓ Concurrency benchmark completed
# ✓ Memory benchmark completed
# ✓ Deduplication benchmark completed
# ✓ NLP benchmark completed
# ✓ Stress test completed
#
# Results saved to: benchmark_results/
```

### Viewing Results

```bash
# Generate and view performance report
vdq performance report

# Opens HTML report in browser with:
# - Performance metrics
# - Charts and visualizations
# - Optimization recommendations
```

## Performance Optimization

### Automatic Optimization

The system can automatically optimize configuration based on your hardware:

```bash
# Analyze system and suggest optimizations
vdq performance optimize --analyze

# Output:
# System Resources:
# CPU Cores: 8 physical, 16 logical
# Memory: 32.0 GB total, 24.5 GB available
# Disk Usage: 45.2%
#
# Performance Issues Found:
# 1. Not utilizing available CPU cores
#    Current: 10
#    Recommended: 16
```

### Performance Profiles

Choose from pre-configured performance profiles:

#### Conservative Profile
- Low resource usage
- Suitable for shared systems
- Minimal impact on other processes

```bash
vdq performance optimize --profile conservative
```

#### Balanced Profile (Default)
- Balanced performance and resource usage
- Recommended for most systems
- Good throughput with moderate resource use

```bash
vdq performance optimize --profile balanced
```

#### Aggressive Profile
- Maximum performance
- High resource usage
- Best for dedicated systems

```bash
vdq performance optimize --profile aggressive
```

### Manual Optimization

#### Key Configuration Parameters

```yaml
# config/default.yaml
data_sources:
  processing:
    # Number of concurrent items to process
    max_concurrent_items: 20  # Increase for better throughput
    
    # Batch size for database operations
    batch_size: 100  # Larger batches = better performance
    
    # Process sources in parallel
    parallel_sources: true  # Enable for multi-source speedup
    
    # Memory limit to prevent OOM
    memory_limit_mb: 4096  # Adjust based on available RAM
    
  deduplication:
    # Cache backend for deduplication
    cache_backend: redis  # Use 'redis' for speed, 'disk' for low memory
    
    # Cache time-to-live
    cache_ttl: 7200  # Longer TTL = better cache hit rate
    
  performance:
    # Connection pool size
    connection_pool_size: 50  # Increase for high concurrency
    
    # Enable compression
    compression_enabled: true  # Reduces network overhead
```

#### Optimization Guidelines

1. **CPU Optimization**
   - Set `max_concurrent_items` to 2-4x CPU cores
   - Enable `parallel_sources` for multi-core systems
   - Use process pooling for CPU-intensive tasks

2. **Memory Optimization**
   - Adjust `batch_size` based on available memory
   - Use disk-based cache if memory is limited
   - Set `memory_limit_mb` to 70% of available RAM

3. **I/O Optimization**
   - Enable `compression_enabled` for network transfers
   - Use streaming for large attachments
   - Increase `connection_pool_size` for database operations

4. **Deduplication Optimization**
   - Use Redis for high-performance caching
   - Adjust `similarity_threshold` for accuracy vs speed
   - Enable bloom filters for large datasets

## Performance Monitoring

### Real-time Monitoring

```bash
# Start monitoring dashboard
vdq monitor

# View data sources performance tab for:
# - Processing rate (items/second)
# - Queue length
# - Error rate
# - Resource usage
```

### Performance Metrics

Key metrics to monitor:

1. **Throughput Metrics**
   - Items processed per second
   - Daily processing capacity
   - Source-specific rates

2. **Resource Metrics**
   - CPU usage percentage
   - Memory consumption
   - Disk I/O rates
   - Network bandwidth

3. **Quality Metrics**
   - Success rate
   - Error rate
   - Duplicate detection rate
   - Processing time percentiles

### Alerting Thresholds

```yaml
# Recommended alert thresholds
alerts:
  - metric: processing_rate
    condition: < 2 items/second
    severity: warning
    
  - metric: error_rate
    condition: > 5%
    severity: critical
    
  - metric: memory_usage
    condition: > 80%
    severity: warning
    
  - metric: queue_length
    condition: > 1000
    severity: warning
```

## Troubleshooting Performance Issues

### Slow Processing

**Symptoms:**
- Low items/second rate
- Growing queue length
- Timeouts

**Solutions:**

1. Increase concurrency:
   ```bash
   vdq config set data_sources.processing.max_concurrent_items 30
   ```

2. Enable parallel processing:
   ```bash
   vdq config set data_sources.processing.parallel_sources true
   ```

3. Optimize batch size:
   ```bash
   vdq config set data_sources.processing.batch_size 200
   ```

### High Memory Usage

**Symptoms:**
- Memory usage > 80%
- OOM errors
- System slowdown

**Solutions:**

1. Reduce batch size:
   ```bash
   vdq config set data_sources.processing.batch_size 50
   ```

2. Switch to disk cache:
   ```bash
   vdq config set data_sources.deduplication.cache_backend disk
   ```

3. Set memory limits:
   ```bash
   vdq config set data_sources.processing.memory_limit_mb 2048
   ```

### High CPU Usage

**Symptoms:**
- CPU usage > 80%
- System unresponsive
- Thermal throttling

**Solutions:**

1. Reduce concurrency:
   ```bash
   vdq config set data_sources.processing.max_concurrent_items 10
   ```

2. Disable NLP if not needed:
   ```bash
   vdq config set data_sources.processing.nlp.extract_entities false
   ```

3. Set CPU limits:
   ```bash
   vdq config set data_sources.processing.cpu_limit_percent 70
   ```

## Best Practices

### 1. Regular Performance Testing

- Run benchmarks weekly
- Test after configuration changes
- Monitor trends over time

### 2. Capacity Planning

- Test with expected daily volume
- Add 50% buffer for growth
- Plan for peak loads

### 3. Resource Allocation

- Reserve resources for data sources
- Use dedicated Redis instance
- Monitor database connections

### 4. Optimization Strategy

- Start with balanced profile
- Optimize based on bottlenecks
- Test changes in staging first

## Example Performance Tuning Session

```bash
# 1. Run initial benchmark
vdq performance benchmark --quick

# 2. Analyze current configuration
vdq performance optimize --analyze

# 3. Apply recommended optimizations
vdq performance optimize --optimize --profile balanced

# 4. Run stress test to validate
vdq performance stress --items 1000

# 5. Monitor in production
vdq monitor

# 6. Generate performance report
vdq performance report
```

## Performance Requirements

### Minimum Requirements

- Process 500+ items daily
- < 5% error rate
- < 5 minute processing time for 500 items
- < 2GB memory usage

### Target Performance

- 10+ items/second throughput
- < 1% error rate
- < 100ms average processing time
- 95%+ cache hit rate

### Scale Targets

- Support 10,000+ items daily
- Horizontal scaling ready
- Multi-region capability
- Real-time processing option

---

*Last Updated: $(date)*
*Version: 1.0*