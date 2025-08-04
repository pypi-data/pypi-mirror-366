# Dev-Agent Logging Integration Guide

## Overview

The Ansera Monitoring System integrates seamlessly with the dev-agent logging framework to provide comprehensive visibility into all system operations. This integration ensures complete traceability and accountability for monitoring activities.

## Architecture

### Logging Hierarchy

```
.dev-workflow/logs/
├── monitoring/               # Monitoring-specific logs
│   ├── activities/          # Daily activity logs
│   ├── changes/            # Pre/post change tracking
│   ├── metrics/            # System metrics data
│   ├── queue/              # Queue processing events
│   ├── processes/          # Process management logs
│   ├── errors/             # Error logs and stack traces
│   ├── snapshots/          # System state snapshots
│   └── reports/            # Generated reports
├── monitoring-master.log    # Master monitoring log
└── master-index.md         # Dev-agent master index
```

## Integration Components

### 1. MonitoringLogger Class

The core logging component that integrates with dev-agent:

```python
from vector_db_query.monitoring.logging import get_monitoring_logger

logger = get_monitoring_logger()
```

### 2. Logging Decorators

Automatic logging for monitoring operations:

```python
from vector_db_query.monitoring.logging_integration import (
    with_activity_logging,
    with_metrics_logging,
    with_queue_logging,
    with_process_logging,
    with_change_logging
)
```

### 3. CLI Integration

Access logging through the CLI:

```bash
vdq logging init      # Initialize logging system
vdq logging view      # View recent logs
vdq logging search    # Search logs
vdq logging report    # Generate reports
vdq logging status    # Show logging status
```

## Usage Patterns

### Pre/Post Change Logging

Track state changes in monitoring operations:

```python
# Before making changes
pre_log = logger.log_pre_change(
    "ComponentName",
    "change_type",
    "Description of change"
)

try:
    # Perform operations
    perform_monitoring_task()
    
    # Log success
    logger.log_post_change(
        pre_log,
        "ComponentName",
        "change_type",
        "SUCCESS",
        {"additional": "details"}
    )
except Exception as e:
    # Log failure
    logger.log_post_change(
        pre_log,
        "ComponentName",
        "change_type",
        "FAILURE",
        {"error": str(e)}
    )
```

### Activity Logging

Track all monitoring activities:

```python
logger.log_activity(
    "SystemMonitor",
    "metric_collection",
    "Collected CPU, memory, and disk metrics"
)
```

### Metrics Logging

Store system metrics for analysis:

```python
metrics = {
    "cpu": 45.5,
    "memory": {"percent": 60.0, "used_gb": 8.0},
    "disk": {"percent": 30.0, "used_gb": 150.0}
}
logger.log_metrics(metrics)
```

### Queue Event Logging

Track document processing:

```python
logger.log_queue_event(
    "document_added",
    job_id,
    {
        "document": "report.pdf",
        "size": 1024000,
        "timestamp": datetime.now().isoformat()
    }
)
```

### Process Event Logging

Monitor process lifecycle:

```python
logger.log_process_event(
    "mcp-server",
    "restart",
    pid=12345,
    details={"reason": "scheduled restart"}
)
```

### Error Logging

Comprehensive error tracking:

```python
try:
    risky_operation()
except Exception as e:
    logger.log_error(
        "ComponentName",
        "operation_failed",
        str(e)
    )
```

## Snapshots

Create system state snapshots at important points:

```python
snapshot_dir = logger.create_snapshot(
    "deployment-complete",
    "deployment",
    "Snapshot after successful deployment"
)
```

## Reports

Generate comprehensive daily reports:

```python
# Generate today's report
report_path = logger.generate_daily_report()

# Generate report for specific date
report_path = logger.generate_daily_report("20240730")
```

## Integration with Dev-Agent Commands

### Logging Library

Source the logging library in dev-agent commands:

```bash
# In dev-agent command
source .dev-workflow/logging-lib.sh

# Use logging functions
log_activity "dev-agent-monitor" "deployment" "Starting monitoring dashboard"
```

### Command Integration

Add logging to custom dev-agent commands:

```bash
# At command start
PRE_LOG=$(log_pre_change "dev-agent-monitor" "dashboard-start" "Starting monitoring dashboard")

# During execution
log_activity "dev-agent-monitor" "config" "Loading configuration"

# At completion
log_post_change "$PRE_LOG" "dev-agent-monitor" "dashboard-start" "SUCCESS"
```

## Best Practices

### 1. Consistent Component Names

Use consistent component names for easy tracking:
- `SystemMonitor` - System metrics collection
- `QueueMonitor` - Queue management
- `ProcessController` - Process control
- `PM2Controller` - PM2 integration

### 2. Meaningful Activity Types

Use descriptive activity types:
- `startup` - Component initialization
- `shutdown` - Component shutdown
- `metric_collection` - Collecting metrics
- `queue_processing` - Processing queue items
- `error_recovery` - Recovering from errors

### 3. Structured Details

Include structured details in logs:

```python
details = {
    "timestamp": datetime.now().isoformat(),
    "user": os.getenv("USER"),
    "action": "restart_service",
    "service": "mcp-server",
    "reason": "memory_threshold_exceeded"
}
```

### 4. Regular Snapshots

Create snapshots at key points:
- Before major operations
- After successful deployments
- Before system updates
- After configuration changes

### 5. Error Context

Include context in error logs:

```python
logger.log_error(
    "QueueProcessor",
    "document_parse_error",
    str(e),
    stack_trace=traceback.format_exc()
)
```

## Viewing and Analyzing Logs

### Real-time Monitoring

```bash
# View latest activities
vdq logging view --lines 50

# View component-specific logs
vdq logging view --component SystemMonitor

# View today's metrics
vdq logging metrics
```

### Historical Analysis

```bash
# Search logs
vdq logging search "error" --days 7

# View specific date
vdq logging view --date 20240730

# Generate report
vdq logging report --date 20240730
```

### Error Investigation

```bash
# View today's errors
vdq logging errors

# View errors for specific date
vdq logging errors --date 20240730
```

## Maintenance

### Log Cleanup

Remove old logs to save space:

```bash
# Dry run to see what would be deleted
vdq logging cleanup --days 30 --dry-run

# Actually clean up
vdq logging cleanup --days 30
```

### Log Rotation

Logs are automatically organized by date. Consider archiving old logs:

```bash
# Archive logs older than 90 days
tar -czf logs-archive-$(date +%Y%m).tar.gz .dev-workflow/logs/monitoring/
```

## Troubleshooting

### Logging Not Working

1. Check initialization:
   ```bash
   vdq logging status
   ```

2. Verify directory permissions:
   ```bash
   ls -la .dev-workflow/logs/monitoring/
   ```

3. Check master log:
   ```bash
   tail .dev-workflow/logs/monitoring-master.log
   ```

### Missing Logs

1. Ensure logging is imported:
   ```python
   from vector_db_query.monitoring.logging import get_monitoring_logger
   ```

2. Check component is using logger:
   ```python
   logger = get_monitoring_logger()
   ```

### Performance Impact

Logging is designed to be lightweight:
- Asynchronous writes where possible
- Automatic log rotation
- Efficient JSON serialization
- Minimal overhead decorators

## Examples

See `examples/monitoring_with_logging.py` for comprehensive examples of:
- Basic logging
- Queue monitoring with logging
- Process monitoring with logging
- Error handling
- Report generation
- Using decorators

## Future Enhancements

- [ ] Real-time log streaming
- [ ] Log aggregation across nodes
- [ ] Advanced search capabilities
- [ ] Custom report templates
- [ ] Integration with external logging services
- [ ] Automated anomaly detection
- [ ] Log-based alerting