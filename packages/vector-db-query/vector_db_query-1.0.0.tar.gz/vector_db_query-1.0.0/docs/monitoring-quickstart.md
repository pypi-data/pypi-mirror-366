# Monitoring Dashboard Quick Start

## Installation

Since the package may be installed in editable mode without extras support, install the monitoring dependencies directly:

```bash
# Direct installation (recommended)
pip install streamlit plotly psutil watchdog

# Or if using conda:
conda install -c conda-forge streamlit plotly psutil watchdog
```

## Running the Dashboard

```bash
# Start the monitoring dashboard
vector-db-query monitor

# Or use the short alias
vdq monitor

# To run without opening browser
vdq monitor --no-browser

# Custom port
vdq monitor --port 8080
```

## Access the Dashboard

Once started, the dashboard is available at:
- Default: http://localhost:8501
- Custom port: http://localhost:[your-port]

## Features Available

- **System Metrics**: CPU, memory, disk usage
- **Process Monitoring**: Active Ansera processes
- **Queue Status**: Document processing queue
- **PM2 Integration**: If PM2 is available
- **Real-time Updates**: Auto-refresh capability

## Troubleshooting

### zsh "no matches found" error
If using zsh and getting errors with square brackets:
```bash
# Use quotes
pip install "vector-db-query[monitoring]"
# Or escape brackets
pip install vector-db-query\[monitoring\]
```

### Streamlit warnings
The warnings about "missing ScriptRunContext" can be safely ignored when running from the CLI.

### ImportError: attempted relative import
If you see this error, ensure you're using the latest version of the code. The monitor command now uses a special runner script to handle imports correctly.

### Port already in use
If port 8501 is already in use:
```bash
vdq monitor --port 8502
```