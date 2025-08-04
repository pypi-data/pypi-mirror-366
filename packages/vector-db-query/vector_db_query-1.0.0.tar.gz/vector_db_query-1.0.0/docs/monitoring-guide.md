# Monitoring and Stabilization Guide

Complete guide for monitoring and maintaining the Ansera Data Sources system in production.

## Overview

The monitoring system provides:
- Real-time health monitoring
- Performance metrics tracking
- Automated alerts
- System stabilization procedures
- Comprehensive dashboards

## Monitoring Components

### 1. CLI Monitor

Interactive command-line monitoring:

```bash
# Live dashboard (default)
vdq monitor

# Single health check
vdq monitor -m check

# Continuous monitoring with alerts
vdq monitor -m watch --interval 10
```

### 2. Web Dashboards

#### Streamlit Dashboard
- URL: http://localhost:8081
- Real-time metrics
- Data source status
- Processing queues
- Error logs

#### Grafana Dashboard
- URL: http://localhost:3000
- Historical metrics
- Performance trends
- Custom alerts
- Multiple dashboards

#### Prometheus
- URL: http://localhost:9090
- Raw metrics
- Query interface
- Alert rules

### 3. Python Monitor Script

Advanced monitoring capabilities:

```bash
# Live dashboard with custom layout
python scripts/monitor_production.py dashboard

# Health check with JSON output
python scripts/monitor_production.py check

# Continuous monitoring
python scripts/monitor_production.py watch --interval 5
```

## Key Metrics

### System Metrics
- **CPU Usage**: Target < 80%
- **Memory Usage**: Target < 85%
- **Disk Usage**: Target < 90%
- **Network I/O**: Monitor for spikes

### Service Metrics
- **API Response Time**: Target < 200ms
- **Database Connections**: Monitor pool usage
- **Queue Length**: Alert if > 1000
- **Cache Hit Rate**: Target > 90%

### Data Source Metrics
- **Processing Rate**: Target > 2 items/sec
- **Error Rate**: Target < 5%
- **Success Rate**: Target > 95%
- **Sync Frequency**: Based on configuration

## Alert Thresholds

### Critical Alerts
```yaml
alerts:
  - name: ServiceDown
    condition: up == 0
    duration: 2m
    severity: critical
    
  - name: HighErrorRate
    condition: error_rate > 10%
    duration: 5m
    severity: critical
    
  - name: DatabaseConnectionExhausted
    condition: connection_pool_usage > 90%
    duration: 5m
    severity: critical
```

### Warning Alerts
```yaml
alerts:
  - name: HighCPU
    condition: cpu_usage > 80%
    duration: 10m
    severity: warning
    
  - name: LowProcessingRate
    condition: processing_rate < 2
    duration: 10m
    severity: warning
    
  - name: LargeQueue
    condition: queue_length > 1000
    duration: 5m
    severity: warning
```

## Monitoring Procedures

### Daily Monitoring

1. **Morning Check** (9 AM)
   ```bash
   vdq monitor health
   vdq migrate status
   ```

2. **Midday Review** (12 PM)
   - Check Grafana dashboards
   - Review error logs
   - Verify processing rates

3. **Evening Summary** (5 PM)
   ```bash
   vdq migrate report
   python scripts/monitor_production.py check
   ```

### Weekly Monitoring

1. **Performance Review**
   ```bash
   vdq performance report
   ```

2. **Capacity Planning**
   - Review growth trends
   - Check resource utilization
   - Plan scaling needs

3. **Error Analysis**
   ```bash
   vdq migrate logs --errors --lines 100
   ```

## System Stabilization

### Automatic Stabilization

Run the stabilization script:

```bash
# Full stabilization
./scripts/stabilize_system.sh

# Or via CLI
vdq monitor stabilize
```

This performs:
1. Database connection cleanup
2. Redis memory optimization
3. Qdrant collection optimization
4. Log rotation
5. Queue cleanup
6. Service health verification
7. Performance tuning
8. Monitoring automation setup

### Manual Stabilization

#### 1. Database Cleanup
```sql
-- Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND state_change < NOW() - INTERVAL '1 hour';

-- Vacuum tables
VACUUM ANALYZE data_sources.processed_items;
```

#### 2. Redis Optimization
```bash
# Clear expired keys
redis-cli --scan --pattern "*" | xargs redis-cli DEL

# Set memory policy
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### 3. Queue Management
```sql
-- Clear stuck items
DELETE FROM data_sources.webhook_logs 
WHERE status = 'pending' 
AND received_at < NOW() - INTERVAL '24 hours';
```

## Monitoring Dashboard Features

### Real-time Metrics
- Processing rate gauge
- Success rate percentage
- Queue length indicator
- Resource usage graphs

### Historical Analysis
- 24-hour trends
- Weekly patterns
- Monthly summaries
- Year-over-year comparison

### Error Tracking
- Recent errors list
- Error rate trends
- Error categorization
- Root cause analysis

## Troubleshooting with Monitoring

### High CPU Usage

1. Check processing rate:
   ```bash
   vdq monitor health --detailed
   ```

2. Identify bottleneck:
   - High NLP processing?
   - Too many concurrent items?
   - Inefficient queries?

3. Apply fix:
   ```bash
   vdq config set data_sources.processing.max_concurrent_items 10
   ```

### Memory Issues

1. Check memory metrics:
   ```bash
   python scripts/monitor_production.py check
   ```

2. Identify cause:
   - Cache size too large?
   - Memory leaks?
   - Large batch sizes?

3. Apply fix:
   ```bash
   vdq performance optimize --profile conservative
   ```

### Slow Processing

1. Check performance metrics:
   ```bash
   vdq performance report
   ```

2. Identify bottleneck:
   - Database queries slow?
   - API rate limits?
   - Network latency?

3. Apply optimization:
   ```bash
   vdq performance optimize --optimize
   ```

## Custom Monitoring

### Adding Custom Metrics

```python
# In your code
from vector_db_query.monitoring.metrics import MetricsCollector

metrics = MetricsCollector()

# Record custom metric
metrics.record('custom_operation_duration', duration_ms)
metrics.increment('custom_counter')
```

### Creating Custom Alerts

```yaml
# prometheus/alerts/custom.yml
groups:
  - name: custom_alerts
    rules:
      - alert: CustomMetricHigh
        expr: custom_metric > 100
        for: 5m
        annotations:
          summary: "Custom metric is high"
```

### Custom Dashboard Panels

Add to Grafana dashboard:
```json
{
  "title": "Custom Metric",
  "targets": [
    {
      "expr": "rate(custom_metric[5m])",
      "legendFormat": "Custom Rate"
    }
  ]
}
```

## Monitoring Best Practices

### 1. Regular Reviews
- Daily health checks
- Weekly performance reviews
- Monthly capacity planning

### 2. Proactive Monitoring
- Set up alerts before issues occur
- Monitor trends, not just current values
- Plan for growth

### 3. Documentation
- Document all custom metrics
- Keep runbooks updated
- Record incident responses

### 4. Testing
- Test alert configurations
- Verify monitoring accuracy
- Practice incident response

## Integration with External Systems

### Slack Notifications

```bash
# Configure webhook
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."

# Add to monitoring script
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Alert: High error rate detected"}'
```

### PagerDuty Integration

```yaml
# alertmanager.yml
receivers:
  - name: pagerduty
    pagerduty_configs:
      - service_key: YOUR_SERVICE_KEY
```

### Email Alerts

```yaml
# alertmanager.yml
receivers:
  - name: email
    email_configs:
      - to: ops@example.com
        from: alerts@example.com
```

## Monitoring Commands Reference

```bash
# Health checks
vdq monitor health                    # Quick health check
vdq monitor health --detailed        # Detailed metrics
vdq monitor health --source gmail    # Source-specific

# Monitoring modes
vdq monitor                          # Live dashboard
vdq monitor -m check                 # Single check
vdq monitor -m watch                 # Continuous

# Stabilization
vdq monitor stabilize                # Run stabilization

# Dashboard access
vdq monitor urls                     # Get dashboard URLs

# Performance
vdq performance benchmark            # Run benchmarks
vdq performance report              # View report
vdq performance optimize            # Optimize config
```

---

*Last Updated: $(date)*
*Version: 1.0*