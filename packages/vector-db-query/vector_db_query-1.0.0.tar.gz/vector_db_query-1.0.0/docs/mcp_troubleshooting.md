# MCP Server Troubleshooting Guide

This guide helps you diagnose and fix common issues with the MCP server.

## Quick Diagnostics

Run these commands to check system status:

```bash
# Check if vector database is running
vector-db-query vector status

# Check MCP server configuration
vector-db-query mcp status

# Test MCP server locally
vector-db-query mcp test

# View recent logs
tail -n 50 logs/mcp/mcp_server.log
```

## Common Issues

### 1. Server Won't Start

**Symptoms:**
- `vector-db-query mcp start` fails immediately
- Error: "Failed to start server"

**Solutions:**

1. **Check Vector Database**
   ```bash
   vector-db-query vector status
   # If not running:
   vector-db-query vector init
   ```

2. **Verify Configuration**
   ```bash
   # Check if config exists
   ls -la config/mcp.yaml
   
   # Reinitialize if needed
   vector-db-query mcp init
   ```

3. **Check Port Availability**
   ```bash
   # For stdio mode (default), no port needed
   # For HTTP mode, check port:
   lsof -i :5000
   ```

4. **Permission Issues**
   ```bash
   # Ensure write permissions for logs
   chmod -R 755 logs/
   ```

### 2. Authentication Failures

**Symptoms:**
- Error: "Authentication failed"
- Error: "Invalid token"

**Solutions:**

1. **Verify Client Credentials**
   ```bash
   # List registered clients
   vector-db-query mcp auth list-clients
   
   # Create new client if needed
   vector-db-query mcp auth create-client test-client
   ```

2. **Check Token Expiry**
   ```bash
   # Generate fresh token
   vector-db-query mcp auth generate-token <client-id> <secret>
   ```

3. **Reset Authentication**
   ```bash
   # Backup current config
   cp config/mcp_auth.yaml config/mcp_auth.yaml.bak
   
   # Reinitialize
   rm config/mcp_auth.yaml
   vector-db-query mcp init
   ```

### 3. Rate Limiting Issues

**Symptoms:**
- Error: "Rate limit exceeded"
- HTTP 429 responses

**Solutions:**

1. **Check Current Limits**
   ```bash
   vector-db-query mcp metrics
   ```

2. **Increase Rate Limits**
   Edit `config/mcp.yaml`:
   ```yaml
   mcp:
     rate_limit_requests: 200  # Increase from 100
     burst_limit: 50          # Allow bursts
   ```

3. **Monitor Client Usage**
   ```bash
   # View client-specific metrics
   grep "rate_limit" logs/mcp/mcp_audit.log | tail -20
   ```

### 4. No Results Found

**Symptoms:**
- Queries return empty results
- "No matching documents" errors

**Solutions:**

1. **Verify Documents Processed**
   ```bash
   # Check collection status
   vector-db-query vector list-collections
   
   # Reprocess if needed
   vector-db-query process /path/to/documents
   ```

2. **Adjust Query Parameters**
   ```python
   # Lower threshold for more results
   {
     "query": "your search",
     "threshold": 0.5,  # Lower from 0.7
     "limit": 20        # Increase limit
   }
   ```

3. **Check Collection Name**
   ```bash
   # List available collections
   vector-db-query vector list-collections
   
   # Use correct name in queries
   {
     "collection": "default"  # or your collection name
   }
   ```

### 5. Performance Issues

**Symptoms:**
- Slow query responses
- Timeouts

**Solutions:**

1. **Enable Caching**
   ```yaml
   # config/mcp.yaml
   mcp:
     enable_caching: true
     cache_ttl: 600  # 10 minutes
   ```

2. **Optimize Queries**
   ```python
   # Use filters to reduce search space
   {
     "query": "specific terms",
     "filters": {"category": "tech"},
     "limit": 10  # Don't request too many
   }
   ```

3. **Check System Resources**
   ```bash
   # Monitor CPU/Memory
   htop
   
   # Check disk space
   df -h
   
   # Vector DB stats
   docker stats qdrant
   ```

### 6. Connection Issues

**Symptoms:**
- "Connection refused"
- "Server unavailable"

**Solutions:**

1. **For Stdio Mode** (default)
   ```bash
   # Ensure server is running
   ps aux | grep "vector-db-query mcp"
   
   # Check process health
   ```

2. **Environment Variables**
   ```bash
   # Set required variables
   export MCP_CLIENT_ID="your-client"
   export MCP_CLIENT_SECRET="your-secret"
   ```

3. **Firewall/Network**
   ```bash
   # Check local firewall
   sudo ufw status
   
   # Test connectivity
   nc -zv localhost 5000
   ```

### 7. Invalid Query Errors

**Symptoms:**
- "Query contains forbidden pattern"
- "Invalid characters in query"

**Solutions:**

1. **Check Query Content**
   ```python
   # Avoid SQL-like syntax
   BAD:  "SELECT * FROM documents WHERE..."
   GOOD: "documents about database queries"
   
   # Remove special characters
   BAD:  "machine learning <script>test</script>"
   GOOD: "machine learning test"
   ```

2. **Query Length**
   ```python
   # Keep queries under 5000 characters
   if len(query) > 5000:
       query = query[:5000]
   ```

### 8. Memory Issues

**Symptoms:**
- Out of memory errors
- Server crashes

**Solutions:**

1. **Limit Result Size**
   ```yaml
   # config/mcp.yaml
   mcp:
     max_result_size: 500000  # 500KB per response
     max_results_per_query: 50
   ```

2. **Restart Services**
   ```bash
   # Restart vector DB
   docker restart qdrant
   
   # Clear caches
   rm -rf logs/mcp/cache/*
   ```

## Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Start with debug logging
vector-db-query mcp start --debug

# Or set environment variable
export MCP_DEBUG=1
vector-db-query mcp start
```

## Log Analysis

### Understanding Log Files

1. **Server Log** (`logs/mcp/mcp_server.log`)
   ```bash
   # View errors only
   grep ERROR logs/mcp/mcp_server.log
   
   # Recent activity
   tail -f logs/mcp/mcp_server.log
   ```

2. **Audit Log** (`logs/mcp/mcp_audit.log`)
   ```bash
   # Parse JSON logs
   cat logs/mcp/mcp_audit.log | jq '.'
   
   # Failed requests
   cat logs/mcp/mcp_audit.log | jq 'select(.details.success == false)'
   ```

3. **Error Log** (`logs/mcp/mcp_errors.log`)
   ```bash
   # View stack traces
   less logs/mcp/mcp_errors.log
   ```

### Common Log Patterns

```bash
# Authentication failures
grep "AUTH_FAILED" logs/mcp/mcp_audit.log

# Rate limit violations
grep "RATE_LIMIT" logs/mcp/mcp_server.log

# Query errors
grep "VALIDATION_ERROR" logs/mcp/mcp_audit.log

# Performance issues
grep "duration_ms" logs/mcp/mcp_audit.log | \
  jq 'select(.details.duration_ms > 1000)'
```

## Health Checks

Create a health check script:

```bash
#!/bin/bash
# mcp_health_check.sh

echo "MCP Server Health Check"
echo "======================"

# Check vector DB
echo -n "Vector DB: "
if vector-db-query vector status | grep -q "running"; then
    echo "✓ Running"
else
    echo "✗ Not running"
fi

# Check MCP config
echo -n "MCP Config: "
if [ -f "config/mcp.yaml" ]; then
    echo "✓ Found"
else
    echo "✗ Missing"
fi

# Test query
echo -n "Test Query: "
if vector-db-query mcp test --query "test" | grep -q "Results"; then
    echo "✓ Working"
else
    echo "✗ Failed"
fi

# Check logs
echo -n "Recent Errors: "
ERROR_COUNT=$(tail -100 logs/mcp/mcp_server.log | grep -c ERROR)
echo "$ERROR_COUNT in last 100 lines"
```

## Recovery Procedures

### Complete Reset

If all else fails, perform a complete reset:

```bash
# 1. Backup data
mkdir -p backups/$(date +%Y%m%d)
cp -r config backups/$(date +%Y%m%d)/
cp -r logs backups/$(date +%Y%m%d)/

# 2. Stop services
docker stop qdrant

# 3. Clean state
rm -rf logs/mcp/*
rm -f config/mcp*.yaml

# 4. Reinitialize
vector-db-query vector init
vector-db-query mcp init

# 5. Reprocess documents
vector-db-query process /path/to/documents

# 6. Test
vector-db-query mcp test
```

## Getting Help

If issues persist:

1. **Collect Diagnostics**
   ```bash
   # Create diagnostic bundle
   tar -czf mcp_diagnostics.tar.gz \
     logs/mcp/ \
     config/mcp*.yaml \
     .env
   ```

2. **Check Documentation**
   - [MCP Server Guide](./mcp_server.md)
   - [Integration Guide](./mcp_integration_guide.md)
   - [API Reference](./api_reference.md)

3. **Community Support**
   - GitHub Issues: [Report bugs](https://github.com/your-repo/issues)
   - Discussions: [Ask questions](https://github.com/your-repo/discussions)

## Prevention Tips

1. **Regular Maintenance**
   ```bash
   # Weekly cleanup
   find logs/mcp -name "*.log" -mtime +7 -delete
   
   # Monitor disk space
   df -h | grep -E "(/$|/var)"
   ```

2. **Monitoring Setup**
   ```bash
   # Add to crontab
   */5 * * * * /path/to/mcp_health_check.sh
   ```

3. **Backup Configuration**
   ```bash
   # Daily config backup
   cp config/mcp*.yaml backups/config_$(date +%Y%m%d)/
   ```