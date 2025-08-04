# PM2 Explained - Process Management for Vector DB Query

## What is PM2?

PM2 (Process Manager 2) is a production-grade process manager for Node.js and Python applications. It's designed to keep your applications running continuously, manage multiple processes, and provide monitoring capabilities.

## Why PM2 Shows as "Not Available"

When you see "PM2 not available - using manual process control" in the monitoring dashboard, it means:

1. **PM2 is not installed** on your system
2. The monitoring dashboard detected this and falls back to basic process control
3. This is completely normal and doesn't prevent the dashboard from working

## What PM2 Provides (When Available)

### 1. **Process Management**
- Start/stop/restart multiple services with one command
- Keep services running continuously (auto-restart on crash)
- Manage all Vector DB Query services together:
  - MCP Server (for Claude integration)
  - Monitoring Dashboard
  - Document Queue Processor
  - Qdrant Health Monitor

### 2. **Advanced Features**
- **Memory limits**: Restart services if they use too much memory
- **Log management**: Centralized logging with rotation
- **Clustering**: Run multiple instances for better performance
- **Monitoring**: Built-in process monitoring
- **Zero-downtime reload**: Update code without service interruption

### 3. **Benefits for Vector DB Query**
- All services managed from one `ecosystem.config.js` file
- Automatic restart if services crash
- Better resource management
- Production-ready deployment

## Do You Need PM2?

### You DON'T need PM2 if:
- You're just testing or developing locally
- You manually start/stop services as needed
- You're running services temporarily
- You prefer simple, direct control

### You MIGHT want PM2 if:
- You're running services in production
- You want services to auto-restart after crashes
- You need to manage multiple services together
- You want professional monitoring and logging

## How to Install PM2 (Optional)

If you decide you want PM2's features:

```bash
# Install PM2 globally
npm install -g pm2

# Verify installation
pm2 --version

# Start all Vector DB Query services
cd /path/to/vector-db-query
pm2 start ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs

# Stop all services
pm2 stop all
```

## Without PM2 - Manual Control

The monitoring dashboard works perfectly without PM2:

1. **Start services manually**:
   ```bash
   # Start MCP server
   vector-db-query mcp start
   
   # Start monitoring dashboard
   vector-db-query monitor
   ```

2. **Basic process control**:
   - Restart MCP server from dashboard
   - View running processes
   - Monitor system resources
   - Manage document queue

## Dashboard Behavior

### With PM2:
- Shows "PM2 is managing X Ansera services"
- Buttons: Start All, Stop All, Restart MCP
- Can control all services from dashboard

### Without PM2:
- Shows "PM2 not available - using manual process control"
- Button: Restart MCP (still works)
- Can still monitor all metrics and queues

## Summary

PM2 is an **optional enhancement** that provides professional process management capabilities. The Vector DB Query system and monitoring dashboard work perfectly fine without it. The "PM2 not available" message is simply informational - it's not an error or problem.

Think of it like cruise control in a car - nice to have for long highway drives, but you can drive perfectly well without it!