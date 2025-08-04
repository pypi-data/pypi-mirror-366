# Ansera Monitoring System Documentation

## Overview

The Ansera Monitoring System provides comprehensive visibility and control over all background processes in the Vector DB Query System. It addresses the challenge of monitoring and managing background jobs through a user-friendly dashboard interface.

## Features

### 1. Real-time System Monitoring
- **CPU Usage**: Track processor utilization
- **Memory Usage**: Monitor RAM consumption
- **Disk Usage**: Check storage capacity
- **Process Tracking**: View all Ansera-related processes
- **Qdrant Health**: Monitor vector database status
- **Docker Integration**: Track container status

### 2. Document Processing Queue
- **Queue Management**: Track pending, processing, completed, and failed jobs
- **Processing Metrics**: View processing rate and average times
- **Queue Health**: Monitor queue status (healthy/warning/critical)
- **Job History**: Review recent processing jobs

### 3. Process Control
- **Service Management**: Start/stop/restart services
- **PM2 Integration**: Manage processes via PM2
- **Log Export**: Export system logs for analysis
- **Queue Operations**: Clear or reset processing queue

### 4. PM2 Process Management
- **Ecosystem Configuration**: Manage all services from one config
- **Automatic Restarts**: Services restart on failure
- **Resource Limits**: Prevent memory leaks
- **Log Rotation**: Automatic log management

## Installation

### Prerequisites
```bash
# Python dependencies
pip install -r requirements.txt

# For PM2 support (optional but recommended)
npm install -g pm2
```

### Quick Start
```bash
# Start monitoring dashboard
make monitor

# Or use the CLI directly
vdq monitor
```

## Usage

### Starting the Dashboard

#### Basic Usage
```bash
vdq monitor
```

#### Custom Configuration
```bash
# Different port
vdq monitor --port 8080

# Allow external access
vdq monitor --host 0.0.0.0

# Disable auto-browser
vdq monitor --no-browser
```

### Using PM2 for Process Management

#### Start All Services
```bash
make pm2-start
# or
./scripts/pm2-manage.sh start
```

#### Check Status
```bash
make pm2-status
# or
pm2 list
```

#### View Logs
```bash
make pm2-logs
# or
pm2 logs ansera-mcp-server
```

#### Stop Services
```bash
make pm2-stop
# or
./scripts/pm2-manage.sh stop
```

### Dashboard Features

#### System Metrics Panel
- Real-time CPU, memory, and disk usage
- Qdrant database health status
- Docker container monitoring

#### Process Control Panel
- **Start All**: Launch all Ansera services
- **Stop All**: Gracefully stop all services
- **Restart MCP**: Restart the MCP server
- **Clear Queue**: Reset the processing queue
- **Export Logs**: Download system logs as ZIP

#### Queue Monitoring Panel
- View pending, processing, completed, and failed jobs
- Monitor processing rate (docs/minute)
- Check average processing time
- Queue health indicator

#### Active Processes Panel
- List all PM2-managed services
- View system processes
- Monitor CPU and memory per process
- Check process uptime and restart count

## Architecture

### Components

1. **SystemMonitor** (`metrics.py`)
   - Collects system resource metrics
   - Monitors Qdrant health
   - Tracks Docker containers
   - Implements caching for performance

2. **QueueMonitor** (`process_manager.py`)
   - Manages document processing queue
   - Tracks job states and transitions
   - Calculates processing metrics
   - Persists queue state to disk

3. **ProcessController** (`controls.py`)
   - Manages service lifecycle
   - Integrates with PM2
   - Handles log exports
   - Controls Qdrant container

4. **PM2Controller** (`pm2_control.py`)
   - Python interface to PM2
   - Service start/stop/restart
   - Process information retrieval
   - Log management

5. **Dashboard** (`dashboard.py`)
   - Streamlit-based web UI
   - Real-time data updates
   - Interactive controls
   - Responsive design

### Data Flow

```
System Resources → SystemMonitor → 
                                  ↘
Document Queue → QueueMonitor →    Dashboard UI → User
                                  ↗
PM2 Processes → ProcessController →
```

## Configuration

### PM2 Ecosystem Configuration

The `ecosystem.config.js` file defines all managed services:

```javascript
{
  apps: [
    {
      name: 'ansera-mcp-server',
      script: 'python',
      args: '-m vector_db_query.mcp_integration.server',
      // ... configuration
    },
    {
      name: 'ansera-monitor',
      script: 'streamlit',
      args: 'run src/vector_db_query/monitoring/dashboard.py',
      // ... configuration
    },
    // ... other services
  ]
}
```

### Environment Variables

- `QUEUE_BATCH_SIZE`: Number of documents to process in batch (default: 10)
- `QUEUE_POLL_INTERVAL`: Seconds between queue checks (default: 5)
- `QDRANT_CHECK_INTERVAL`: Seconds between health checks (default: 60)
- `PYTHONUNBUFFERED`: Set to '1' for real-time logs

## Testing

### Run All Monitoring Tests
```bash
make test-monitoring
```

### Run Specific Test Suites
```bash
# Unit tests only
make test-monitoring-unit

# Integration tests only
make test-monitoring-integration

# Specific module
python tests/run_monitoring_tests.py metrics
```

### Test Coverage
```bash
pytest tests/test_monitoring_*.py --cov=src/vector_db_query/monitoring
```

## Troubleshooting

### Dashboard Won't Start
1. Check if port is already in use
2. Verify Streamlit is installed: `pip install streamlit`
3. Check Python path: `which python`

### PM2 Services Not Starting
1. Verify PM2 is installed: `pm2 --version`
2. Check ecosystem.config.js exists
3. Review PM2 logs: `pm2 logs`

### Queue Processing Issues
1. Check queue directory permissions
2. Verify queue files aren't corrupted
3. Reset queue if needed: Clear Queue button

### High Resource Usage
1. Check PM2 memory limits in ecosystem.config.js
2. Review process list for runaway processes
3. Check log file sizes

## API Reference

### CLI Commands
```bash
vdq monitor [OPTIONS]
  --port INTEGER     Port to run dashboard on (default: 8501)
  --host TEXT        Host to bind to (default: localhost)
  --browser/--no-browser  Open browser (default: True)
```

### Python API
```python
from vector_db_query.monitoring import SystemMonitor, QueueMonitor

# Get system stats
monitor = SystemMonitor()
stats = monitor.get_quick_stats()

# Check queue status
queue = QueueMonitor()
metrics = queue.get_queue_metrics()
```

## Best Practices

1. **Regular Monitoring**: Check dashboard daily for queue health
2. **Log Rotation**: Export and archive logs weekly
3. **Resource Limits**: Set appropriate PM2 memory limits
4. **Error Handling**: Monitor failed jobs and investigate causes
5. **Performance**: Use caching for frequently accessed metrics

## Future Enhancements

- [ ] Email alerts for critical events
- [ ] Historical metrics storage
- [ ] Advanced analytics dashboard
- [ ] REST API for external monitoring
- [ ] Kubernetes deployment support
- [ ] Grafana integration

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `logs/` directory
3. Run diagnostic tests
4. Create an issue on GitHub