# Monitoring Dashboard Setup Guide

## Overview
The Vector DB Query monitoring dashboard provides real-time insights into:
- System metrics (CPU, memory, disk usage)
- Active processes and services
- Document processing queue status
- PM2-managed services (if available)

## Installation

### Quick Install (Recommended)
To install all monitoring dependencies:
```bash
pip install vector-db-query[monitoring]

# For zsh users (if you get "no matches found" error):
pip install "vector-db-query[monitoring]"
# or
pip install vector-db-query\[monitoring\]
```

This installs:
- `streamlit` - Web dashboard framework
- `plotly` - Interactive charts
- `psutil` - System metrics
- `watchdog` - File monitoring

### Manual Installation
If you prefer to install dependencies individually:

#### Using pip:
```bash
pip install streamlit plotly psutil watchdog
```

#### Using conda:
```bash
conda install -c conda-forge streamlit plotly psutil watchdog
```

## Usage

### Starting the Dashboard
```bash
# Default (opens browser automatically)
vector-db-query monitor

# Or using the short alias
vdq monitor

# Custom port
vdq monitor --port 8080

# No browser auto-open
vdq monitor --no-browser

# Bind to all interfaces (for remote access)
vdq monitor --host 0.0.0.0
```

### Command Options
- `--port`: Port to run the dashboard on (default: 8501)
- `--host`: Host to bind the dashboard to (default: localhost)
- `--browser/--no-browser`: Open browser automatically (default: True)

## Features

### System Metrics
- Real-time CPU and memory usage
- Disk space monitoring
- Process tracking for Ansera services

### Process Control
- Start/stop/restart PM2-managed services
- Manual MCP server restart
- Export system logs

### Queue Monitoring
- Document processing queue status
- Processing rate and average time
- Queue health indicators
- Recent job history

### Interactive Controls
- Auto-refresh with configurable interval
- Manual refresh button
- Queue clearing
- Log export

## Troubleshooting

### Common Issues

1. **"Streamlit is not installed" error**
   - Solution: Run `pip install streamlit` or `pip install vector-db-query[monitoring]`

2. **"No module named 'plotly'" error**
   - Solution: Install plotly with `pip install plotly`

3. **Port already in use**
   - Solution: Use a different port with `--port` option

4. **Cannot access from remote machine**
   - Solution: Use `--host 0.0.0.0` to bind to all interfaces

### Requirements
- Python 3.9+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Network access to specified host/port

## Security Notes
- By default, the dashboard binds to localhost only
- Use `--host 0.0.0.0` with caution in production environments
- Consider using a reverse proxy for secure remote access