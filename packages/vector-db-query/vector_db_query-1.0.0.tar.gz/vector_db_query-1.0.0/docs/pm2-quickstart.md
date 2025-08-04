# PM2 Quick Start Guide for Vector DB Query

## Installation Confirmed ✅
You've successfully installed PM2 globally.

## Starting PM2 Services

### 1. Navigate to the Project Directory
Make sure you're in the vector-db-query directory:
```bash
cd "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query"
```

### 2. Start All Services
```bash
pm2 start ecosystem.config.js
```

### 3. Check Service Status
```bash
pm2 status
# or
pm2 list
```

### 4. View Logs
```bash
# All logs
pm2 logs

# Specific service logs
pm2 logs ansera-mcp-server
pm2 logs ansera-monitor
pm2 logs ansera-queue-processor
```

### 5. Stop Services
```bash
# Stop all
pm2 stop all

# Stop specific service
pm2 stop ansera-monitor
```

### 6. Restart Services
```bash
# Restart all
pm2 restart all

# Restart specific
pm2 restart ansera-mcp-server
```

## PM2 Services for Vector DB Query

The ecosystem.config.js configures these services:

1. **ansera-mcp-server** - MCP Server for Claude integration
2. **ansera-monitor** - Monitoring Dashboard (Streamlit)
3. **ansera-queue-processor** - Document processing queue
4. **ansera-qdrant-monitor** - Qdrant health monitor

## Common PM2 Commands

```bash
# Save current process list
pm2 save

# Set PM2 to start on system boot
pm2 startup

# Monitor processes in real-time
pm2 monit

# Show detailed info about a process
pm2 describe ansera-monitor

# Flush all logs
pm2 flush

# Kill PM2 daemon
pm2 kill
```

## Troubleshooting

### "File ecosystem.config.js not found"
This means you're not in the correct directory. Always run PM2 commands from:
```bash
/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query
```

### Services won't start
Check logs for errors:
```bash
pm2 logs --lines 50
```

### Port already in use
Stop the service using the port or change the port in ecosystem.config.js

## Next Steps

1. Start PM2 services:
   ```bash
   cd "/Users/haithamdata/Documents/Haitham Old/Npipeline/APP/Personal/Ansera/vector-db-query"
   pm2 start ecosystem.config.js
   ```

2. Access the monitoring dashboard:
   - It will be available at http://localhost:8501
   - The dashboard will now show "PM2 is managing X Ansera services"

3. You can now control all services from the monitoring dashboard!