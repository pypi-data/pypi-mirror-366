# Vector DB Query - Enterprise Monitoring Dashboard Guide

## Overview

The Vector DB Query monitoring dashboard provides comprehensive real-time insights into your document processing pipeline, system performance, and operational health. Built with Streamlit, it offers an intuitive interface for monitoring, controlling, and optimizing your vector database operations.

## Features

### 🎯 Core Capabilities

1. **Real-Time System Monitoring**
   - CPU, memory, and disk usage tracking
   - Process status and resource consumption
   - Network I/O statistics
   - Queue depth and processing rates

2. **Advanced Scheduling System**
   - Cron-based task scheduling
   - File system event watchers
   - Multi-folder monitoring
   - Schedule templates and bulk operations

3. **Service Control**
   - Start/stop/restart services
   - Dynamic parameter adjustment
   - Queue pause/resume capabilities
   - Process priority management

4. **Multi-Channel Notifications**
   - Toast notifications in dashboard
   - Email alerts for critical events
   - Push notifications support
   - Webhook integrations

5. **Performance Optimization**
   - Smart caching strategies
   - Connection pooling
   - Batch processing optimization
   - Query performance tracking

## Getting Started

### Installation

The monitoring dashboard is included with Vector DB Query v1.0.0+:

```bash
pip install vector-db-query[monitoring]
```

### Starting the Dashboard

```bash
# Start the monitoring dashboard
vdq monitor

# Or with custom port
vdq monitor --port 8502

# With authentication enabled
vdq monitor --auth
```

### First-Time Setup

1. **Access the Dashboard**
   - Open http://localhost:8501 in your browser
   - Default credentials (if auth enabled): admin/admin

2. **Configure Services**
   - Navigate to "Service Control" tab
   - Configure your Qdrant connection
   - Set up MCP server parameters
   - Adjust processing thresholds

3. **Set Up Notifications**
   - Go to "Notifications" → "Configuration"
   - Add email settings for alerts
   - Configure notification rules
   - Test notification channels

## Dashboard Components

### 1. System Overview

The main dashboard provides at-a-glance system health:

- **Resource Usage**: Real-time CPU, memory, disk metrics
- **Service Status**: All services with health indicators
- **Processing Stats**: Documents processed, queue depth, error rates
- **Performance Metrics**: Query latency, throughput, cache hit rates

### 2. Scheduling Tab

Comprehensive scheduling management:

- **Create Schedules**: Cron expressions with visual helper
- **File Watchers**: Monitor directories for changes
- **Multi-Folder Support**: Watch multiple locations
- **Schedule History**: Execution logs and statistics

### 3. Service Control

Advanced service management:

- **Process Control**: Start/stop/restart with one click
- **Parameter Adjustment**: Modify settings without restart
- **Queue Management**: Pause/resume processing
- **Resource Limits**: Set CPU/memory constraints

### 4. Notifications

Multi-channel alert system:

- **Email Alerts**: SMTP configuration with templates
- **Toast Messages**: In-dashboard notifications
- **Push Notifications**: Mobile app support
- **Event Rules**: Configure trigger conditions

### 5. Monitoring

Deep system insights:

- **Connection Monitor**: Database connection health
- **MCP Metrics**: Server performance tracking
- **Qdrant Management**: Collection statistics
- **Query Performance**: Slow query analysis

### 6. Performance

Optimization tools:

- **Cache Manager**: View and manage caches
- **Connection Pools**: Pool statistics and tuning
- **Batch Processing**: Configure batch sizes
- **Query Optimizer**: Optimization suggestions

## Advanced Features

### Performance Optimization

The dashboard includes several performance optimization features:

1. **Smart Caching**
   - Multi-level cache (memory/disk/distributed)
   - LRU, LFU, FIFO, TTL strategies
   - Automatic cache warming
   - Hit rate analytics

2. **Connection Pooling**
   - Auto-scaling pools
   - Health checking
   - Connection recycling
   - Pool statistics

3. **Batch Processing**
   - Adaptive batch sizing
   - Priority queuing
   - Retry with backoff
   - Throughput optimization

### Security Features

- **API Key Management**: Secure key storage and rotation
- **Audit Logging**: Complete activity tracking
- **Access Control**: Role-based permissions
- **SSL/TLS Support**: Encrypted communications

### Integration Capabilities

- **Webhooks**: Send events to external systems
- **REST API**: Programmatic dashboard access
- **Metrics Export**: Prometheus/Grafana compatible
- **Log Aggregation**: Centralized logging support

## Configuration

### Environment Variables

```bash
# Dashboard configuration
VDQ_MONITOR_PORT=8501
VDQ_MONITOR_HOST=0.0.0.0
VDQ_MONITOR_AUTH=true
VDQ_MONITOR_SSL_CERT=/path/to/cert.pem
VDQ_MONITOR_SSL_KEY=/path/to/key.pem

# Notification settings
VDQ_SMTP_HOST=smtp.gmail.com
VDQ_SMTP_PORT=587
VDQ_SMTP_USER=your-email@gmail.com
VDQ_SMTP_PASS=your-app-password

# Performance settings
VDQ_CACHE_SIZE=1000
VDQ_POOL_SIZE=10
VDQ_BATCH_SIZE=100
```

### Configuration File

Create `~/.vdq/monitor-config.yaml`:

```yaml
dashboard:
  port: 8501
  host: localhost
  auth_enabled: true
  theme: dark

notifications:
  email:
    enabled: true
    smtp_host: smtp.gmail.com
    smtp_port: 587
    from_address: alerts@yourdomain.com
  
  rules:
    - name: high_cpu_alert
      condition: cpu_usage > 80
      channels: [email, toast]
      severity: warning
    
    - name: service_down
      condition: service_status == "down"
      channels: [email, push]
      severity: critical

performance:
  cache:
    strategy: lru
    max_size: 1000
    ttl: 3600
  
  pools:
    qdrant:
      min_size: 5
      max_size: 20
      timeout: 30
```

## Best Practices

### 1. Monitoring Setup

- **Set Resource Alerts**: Configure CPU/memory thresholds
- **Monitor Queue Depth**: Alert on processing backlogs
- **Track Error Rates**: Set up error spike notifications
- **Review Performance**: Weekly performance reviews

### 2. Scheduling

- **Use Templates**: Create reusable schedule patterns
- **Test Schedules**: Verify cron expressions before saving
- **Monitor Execution**: Check schedule history regularly
- **Handle Failures**: Configure retry policies

### 3. Performance Tuning

- **Cache Appropriately**: Cache frequently accessed data
- **Pool Connections**: Use connection pooling for databases
- **Batch Operations**: Process documents in batches
- **Optimize Queries**: Use query analyzer recommendations

### 4. Security

- **Rotate API Keys**: Regular key rotation policy
- **Enable Auth**: Always use authentication in production
- **Audit Access**: Review audit logs periodically
- **Use SSL**: Enable HTTPS for production

## Troubleshooting

### Common Issues

1. **Dashboard Won't Start**
   ```bash
   # Check if port is in use
   lsof -i :8501
   
   # Try different port
   vdq monitor --port 8502
   ```

2. **Services Show as Down**
   ```bash
   # Check service logs
   vdq logs --service qdrant
   
   # Restart services
   vdq restart --all
   ```

3. **High Memory Usage**
   ```bash
   # Clear caches
   vdq cache clear
   
   # Reduce batch sizes
   vdq config set batch_size 50
   ```

4. **Notification Failures**
   ```bash
   # Test SMTP connection
   vdq test smtp
   
   # Check notification logs
   vdq logs --service notifications
   ```

## API Reference

The monitoring dashboard exposes a REST API for programmatic access:

### Endpoints

```bash
# Get system metrics
GET /api/v1/metrics

# Get service status
GET /api/v1/services

# Control services
POST /api/v1/services/{service_id}/start
POST /api/v1/services/{service_id}/stop
POST /api/v1/services/{service_id}/restart

# Manage schedules
GET /api/v1/schedules
POST /api/v1/schedules
DELETE /api/v1/schedules/{schedule_id}

# Query performance
GET /api/v1/performance/queries
GET /api/v1/performance/cache/stats
```

### Authentication

```python
import requests

# Using API key
headers = {"Authorization": "Bearer your-api-key"}
response = requests.get("http://localhost:8501/api/v1/metrics", headers=headers)

# Using session
session = requests.Session()
session.post("http://localhost:8501/api/v1/auth/login", 
             json={"username": "admin", "password": "password"})
response = session.get("http://localhost:8501/api/v1/metrics")
```

## Advanced Usage

### Custom Widgets

Create custom monitoring widgets:

```python
from vector_db_query.monitoring.widgets import BaseWidget, register_widget

@register_widget("custom_metric")
class CustomMetricWidget(BaseWidget):
    def render(self):
        # Your custom rendering logic
        return self.create_metric_card(
            title="Custom Metric",
            value=self.get_custom_value(),
            delta=self.calculate_delta()
        )
```

### Event Handlers

Subscribe to system events:

```python
from vector_db_query.monitoring import event_bus

@event_bus.on("service.started")
def on_service_start(service_id, timestamp):
    print(f"Service {service_id} started at {timestamp}")

@event_bus.on("alert.triggered")
def on_alert(alert_name, severity, message):
    # Custom alert handling
    send_to_slack(f"Alert: {alert_name} - {message}")
```

## Performance Impact

The monitoring dashboard is designed for minimal overhead:

- **CPU Usage**: < 2% in idle state
- **Memory**: ~50-100MB base footprint
- **Network**: Negligible unless streaming logs
- **Storage**: Logs rotate at 100MB by default

## Conclusion

The Vector DB Query monitoring dashboard provides enterprise-grade observability for your document processing pipeline. With its comprehensive features, intuitive interface, and extensive customization options, it enables you to maintain optimal performance and reliability.

For more information:
- [API Documentation](api-reference.md)
- [Configuration Guide](configuration-guide.md)
- [Troubleshooting Guide](troubleshooting.md)
- [GitHub Issues](https://github.com/your-org/vector-db-query/issues)