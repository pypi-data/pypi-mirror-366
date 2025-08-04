# Data Sources Troubleshooting Guide

Comprehensive troubleshooting guide for Vector DB Query Data Sources system.

## Quick Diagnosis

Use this flowchart to quickly identify and resolve common issues:

```
┌─────────────────────────┐
│   Issue Encountered?    │
└────────────┬────────────┘
             │
    ┌────────▼────────┐
    │ Authentication  │───Yes──► Check Credentials Section
    │    Failed?      │
    └────────┬────────┘
             │ No
    ┌────────▼────────┐
    │   Connection    │───Yes──► Check Network Section
    │    Timeout?     │
    └────────┬────────┘
             │ No
    ┌────────▼────────┐
    │  Processing     │───Yes──► Check Processing Section
    │    Error?       │
    └────────┬────────┘
             │ No
    ┌────────▼────────┐
    │  Performance    │───Yes──► Check Performance Section
    │    Issue?       │
    └────────┬────────┘
             │ No
    ┌────────▼────────┐
    │     Other       │───────► Check Common Issues
    └─────────────────┘
```

## Authentication Issues

### Gmail OAuth2 Problems

#### Issue: "OAuth2 token expired or invalid"

**Symptoms:**
- Error 401 when accessing Gmail
- "invalid_grant" error
- Token refresh fails

**Solutions:**

1. **Remove and regenerate token:**
   ```bash
   # Remove old token
   rm .gmail_token.json
   
   # Re-authenticate
   vdq datasources auth --source gmail
   ```

2. **Check OAuth2 consent screen:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" > "OAuth consent screen"
   - Ensure your email is added as a test user
   - Check app is not in "Testing" mode for production

3. **Verify API is enabled:**
   ```bash
   # Check if Gmail API is enabled
   gcloud services list --enabled | grep gmail
   
   # Enable if needed
   gcloud services enable gmail.googleapis.com
   ```

4. **Check credentials file:**
   ```python
   import json
   
   # Verify credentials structure
   with open('path/to/credentials.json') as f:
       creds = json.load(f)
       assert 'installed' in creds or 'web' in creds
       assert 'client_id' in creds.get('installed', creds.get('web', {}))
   ```

#### Issue: "Access blocked: App hasn't been verified"

**Solutions:**
1. Add email to test users
2. Complete OAuth verification process
3. Use service account for production

### Fireflies API Authentication

#### Issue: "401 Unauthorized from Fireflies API"

**Symptoms:**
- API calls return 401
- "Invalid API key" error

**Solutions:**

1. **Verify API key:**
   ```bash
   # Test API key directly
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        https://api.fireflies.ai/v1/me
   ```

2. **Check keyring storage:**
   ```python
   import keyring
   
   # Retrieve stored key
   api_key = keyring.get_password("vector-db-query", "fireflies-api-key")
   print(f"Stored key exists: {bool(api_key)}")
   
   # Update if needed
   keyring.set_password("vector-db-query", "fireflies-api-key", "new-key")
   ```

3. **Use environment variable:**
   ```bash
   export FIREFLIES_API_KEY="your-api-key"
   vdq datasources sync --source fireflies
   ```

### Google Drive OAuth2 Issues

#### Issue: "Insufficient permissions"

**Solutions:**

1. **Check OAuth scopes:**
   ```python
   # Required scopes
   SCOPES = [
       'https://www.googleapis.com/auth/drive.readonly',
       'https://www.googleapis.com/auth/drive.metadata.readonly'
   ]
   ```

2. **Re-authorize with correct scopes:**
   ```bash
   # Remove token and re-auth
   rm .gdrive_token.json
   vdq datasources auth --source google_drive
   ```

## Connection & Network Issues

### Timeout Errors

#### Issue: "Connection timeout while fetching data"

**Symptoms:**
- Sync hangs indefinitely
- "TimeoutError" in logs
- Partial data retrieval

**Solutions:**

1. **Increase timeout settings:**
   ```yaml
   # config/default.yaml
   data_sources:
     gmail:
       timeout: 120  # Increase from default 30s
       retry_attempts: 5
       retry_delay: 10
   ```

2. **Check network connectivity:**
   ```bash
   # Test Gmail IMAP
   openssl s_client -connect imap.gmail.com:993
   
   # Test Fireflies API
   curl -I https://api.fireflies.ai/v1/health
   
   # Test Google APIs
   curl -I https://www.googleapis.com/drive/v3/about
   ```

3. **Use connection pooling:**
   ```python
   # For HTTP connections
   import requests
   from requests.adapters import HTTPAdapter
   from urllib3.util.retry import Retry
   
   session = requests.Session()
   retry = Retry(total=5, backoff_factor=0.3)
   adapter = HTTPAdapter(max_retries=retry)
   session.mount('https://', adapter)
   ```

### SSL/TLS Errors

#### Issue: "SSL certificate verification failed"

**Solutions:**

1. **Update certificates:**
   ```bash
   # Update CA certificates
   # Ubuntu/Debian
   sudo apt-get update && sudo apt-get install ca-certificates
   
   # macOS
   brew install ca-certificates
   ```

2. **Corporate proxy settings:**
   ```bash
   # Set proxy environment variables
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   export NO_PROXY=localhost,127.0.0.1
   ```

3. **Custom certificate bundle:**
   ```python
   # Use custom CA bundle
   import os
   os.environ['REQUESTS_CA_BUNDLE'] = '/path/to/company-ca-bundle.crt'
   ```

### Rate Limiting

#### Issue: "Rate limit exceeded"

**Solutions:**

1. **Implement backoff strategy:**
   ```yaml
   # config/default.yaml
   data_sources:
     processing:
       rate_limit:
         max_requests_per_minute: 30
         backoff_multiplier: 2
         max_backoff: 300
   ```

2. **Use batch operations:**
   ```python
   # Batch API calls
   def batch_process(items, batch_size=50):
       for i in range(0, len(items), batch_size):
           batch = items[i:i+batch_size]
           process_batch(batch)
           time.sleep(2)  # Rate limit pause
   ```

## Processing Errors

### Memory Issues

#### Issue: "Out of memory while processing"

**Symptoms:**
- Process killed with OOM
- "MemoryError" exceptions
- System slowdown

**Solutions:**

1. **Reduce batch sizes:**
   ```yaml
   data_sources:
     processing:
       batch_size: 10  # Reduce from 50
       max_concurrent_items: 5  # Reduce from 10
   ```

2. **Enable streaming:**
   ```python
   # Stream large attachments
   def process_large_file(filepath):
       with open(filepath, 'rb') as f:
           chunk_size = 1024 * 1024  # 1MB chunks
           while True:
               chunk = f.read(chunk_size)
               if not chunk:
                   break
               yield process_chunk(chunk)
   ```

3. **Monitor memory usage:**
   ```bash
   # Run with memory profiling
   vdq datasources sync --memory-profile
   
   # Set memory limit
   ulimit -v 4194304  # 4GB limit
   ```

### Encoding Issues

#### Issue: "UnicodeDecodeError"

**Solutions:**

1. **Force UTF-8 encoding:**
   ```python
   # Set default encoding
   import sys
   sys.stdout.reconfigure(encoding='utf-8')
   
   # Read with explicit encoding
   with open(file, 'r', encoding='utf-8', errors='replace') as f:
       content = f.read()
   ```

2. **Handle multiple encodings:**
   ```python
   import chardet
   
   def read_with_detection(filepath):
       with open(filepath, 'rb') as f:
           raw = f.read()
           encoding = chardet.detect(raw)['encoding']
           return raw.decode(encoding or 'utf-8', errors='replace')
   ```

### Database Errors

#### Issue: "Database connection pool exhausted"

**Solutions:**

1. **Increase pool size:**
   ```python
   # config/default.yaml
   database:
     pool_size: 50  # Increase from 20
     max_overflow: 100  # Increase from 30
     pool_timeout: 30
     pool_recycle: 3600
   ```

2. **Fix connection leaks:**
   ```python
   # Ensure proper cleanup
   from contextlib import contextmanager
   
   @contextmanager
   def get_db_session():
       session = SessionLocal()
       try:
           yield session
       finally:
           session.close()
   ```

#### Issue: "Database schema out of sync"

**Solutions:**

1. **Check migration status:**
   ```bash
   # Show current revision
   alembic current
   
   # Show pending migrations
   alembic history
   
   # Apply migrations
   alembic upgrade head
   ```

2. **Manual schema fix:**
   ```sql
   -- Check for missing columns
   SELECT column_name 
   FROM information_schema.columns 
   WHERE table_name = 'processed_items';
   
   -- Add missing column
   ALTER TABLE processed_items 
   ADD COLUMN IF NOT EXISTS nlp_data JSONB;
   ```

## Performance Issues

### Slow Processing

#### Issue: "Processing taking too long"

**Diagnosis:**
```bash
# Profile processing
vdq datasources profile --source gmail --items 100

# Check bottlenecks
vdq datasources stats --detailed
```

**Solutions:**

1. **Enable parallel processing:**
   ```yaml
   data_sources:
     processing:
       parallel_sources: true
       max_workers: 10
       use_multiprocessing: true  # For CPU-bound tasks
   ```

2. **Optimize database queries:**
   ```python
   # Use bulk operations
   def bulk_check_duplicates(hashes):
       existing = db.query(ProcessedItem.content_hash)\
                    .filter(ProcessedItem.content_hash.in_(hashes))\
                    .all()
       return set(h[0] for h in existing)
   ```

3. **Enable caching:**
   ```python
   from functools import lru_cache
   import redis
   
   cache = redis.Redis.from_url(REDIS_URL)
   
   @lru_cache(maxsize=1000)
   def get_cached_result(key):
       return cache.get(key)
   ```

### High Resource Usage

#### Issue: "CPU/Memory usage too high"

**Solutions:**

1. **Limit concurrent operations:**
   ```yaml
   data_sources:
     processing:
       max_concurrent_items: 5
       cpu_limit: 80  # Percentage
       memory_limit: 4096  # MB
   ```

2. **Implement throttling:**
   ```python
   import time
   from threading import Semaphore
   
   throttle = Semaphore(5)  # Max 5 concurrent
   
   def process_with_throttle(item):
       with throttle:
           process_item(item)
           time.sleep(0.1)  # Small delay
   ```

## Data Quality Issues

### Duplicate Processing

#### Issue: "Same items processed multiple times"

**Solutions:**

1. **Check deduplication settings:**
   ```yaml
   data_sources:
     deduplication:
       enabled: true
       similarity_threshold: 0.95
       cross_source_check: true
       cache_ttl: 86400
   ```

2. **Manual deduplication:**
   ```bash
   # Find duplicates
   vdq datasources deduplicate --dry-run
   
   # Remove duplicates
   vdq datasources deduplicate --confirm
   ```

3. **Clear dedup cache:**
   ```bash
   # Clear cache
   vdq datasources clean --cache --type deduplication
   ```

### Missing Data

#### Issue: "Not all items being processed"

**Diagnosis:**
```bash
# Check processing stats
vdq datasources stats --source gmail --detailed

# View skipped items
vdq datasources errors --type skipped --limit 50
```

**Solutions:**

1. **Check filters:**
   ```bash
   # List active filters
   vdq datasources filters --list
   
   # Test filters
   vdq datasources filters --test --source gmail
   ```

2. **Verify date ranges:**
   ```yaml
   data_sources:
     gmail:
       initial_history_days: 365  # Increase if needed
       include_all_folders: true
   ```

## Monitoring Dashboard Issues

### Dashboard Not Loading

#### Issue: "Streamlit dashboard won't start"

**Solutions:**

1. **Check port availability:**
   ```bash
   # Check if port is in use
   lsof -i :8501
   
   # Use different port
   vdq monitor --port 8502
   ```

2. **Clear Streamlit cache:**
   ```bash
   # Clear cache
   rm -rf ~/.streamlit/cache
   
   # Reset config
   rm ~/.streamlit/config.toml
   ```

### Metrics Not Updating

#### Issue: "Dashboard shows stale data"

**Solutions:**

1. **Check metrics collection:**
   ```python
   # Verify metrics are being written
   from vector_db_query.monitoring.metrics import MetricsCollector
   
   collector = MetricsCollector()
   collector.test_write()
   ```

2. **Reset metrics cache:**
   ```bash
   # Clear metrics cache
   vdq monitor reset-cache
   ```

## Common Error Messages

### Error Code Reference

| Code | Message | Solution |
|------|---------|----------|
| DS001 | "Authentication failed" | Check credentials, re-authenticate |
| DS002 | "Connection timeout" | Increase timeout, check network |
| DS003 | "Rate limit exceeded" | Reduce request rate, implement backoff |
| DS004 | "Invalid configuration" | Validate config file, check syntax |
| DS005 | "Processing failed" | Check logs, verify data format |
| DS006 | "Deduplication error" | Clear cache, check hash function |
| DS007 | "Storage full" | Free disk space, archive old data |
| DS008 | "Database error" | Check connection, run migrations |
| DS009 | "Permission denied" | Check file permissions, OAuth scopes |
| DS010 | "Invalid data format" | Validate input, check encoding |

## Advanced Debugging

### Enable Debug Logging

```bash
# Maximum verbosity
export LOG_LEVEL=DEBUG
export VDQ_DEBUG=1

# Debug specific component
vdq datasources sync --debug --trace gmail

# Save debug output
vdq datasources sync --debug 2>&1 | tee debug.log
```

### Component-Specific Debugging

#### Gmail Debugging
```python
# Enable IMAP debug
import imaplib
imaplib.Debug = 4

# OAuth2 debug
import logging
logging.getLogger('google.auth').setLevel(logging.DEBUG)
```

#### Fireflies Debugging
```bash
# Test API endpoints
curl -v -H "Authorization: Bearer $API_KEY" \
     https://api.fireflies.ai/v1/meetings

# Check webhook delivery
ngrok http 8000  # Expose local webhook endpoint
```

#### Google Drive Debugging
```python
# Enable API client debug
import googleapiclient
import httplib2
httplib2.debuglevel = 4
```

### Performance Profiling

```bash
# CPU profiling
python -m cProfile -o profile.pstats $(which vdq) datasources sync
python -m pstats profile.pstats

# Memory profiling
mprof run vdq datasources sync
mprof plot

# Line profiling
kernprof -l -v vdq datasources sync
```

### Database Query Analysis

```sql
-- Slow query log
SET log_min_duration_statement = 1000;  -- Log queries > 1s

-- Query execution plan
EXPLAIN ANALYZE
SELECT * FROM processed_items
WHERE source_type = 'gmail'
AND processed_at > NOW() - INTERVAL '1 day';

-- Lock monitoring
SELECT 
    pid,
    usename,
    query,
    state,
    wait_event_type,
    wait_event
FROM pg_stat_activity
WHERE wait_event IS NOT NULL;
```

## Getting Help

### Collect Diagnostic Information

```bash
#!/bin/bash
# diagnostic.sh - Collect system info for support

OUTPUT="diagnostic-$(date +%Y%m%d-%H%M%S).txt"

echo "Vector DB Query Diagnostic Report" > $OUTPUT
echo "================================" >> $OUTPUT
echo "Date: $(date)" >> $OUTPUT
echo "Version: $(vdq --version)" >> $OUTPUT
echo "" >> $OUTPUT

echo "System Information:" >> $OUTPUT
uname -a >> $OUTPUT
echo "" >> $OUTPUT

echo "Python Information:" >> $OUTPUT
python --version >> $OUTPUT
pip list | grep vector-db-query >> $OUTPUT
echo "" >> $OUTPUT

echo "Configuration:" >> $OUTPUT
vdq config show >> $OUTPUT
echo "" >> $OUTPUT

echo "Source Status:" >> $OUTPUT
vdq datasources status >> $OUTPUT
echo "" >> $OUTPUT

echo "Recent Errors:" >> $OUTPUT
vdq datasources errors --limit 10 >> $OUTPUT
echo "" >> $OUTPUT

echo "Database Status:" >> $OUTPUT
vdq database status >> $OUTPUT
echo "" >> $OUTPUT

echo "Diagnostic report saved to: $OUTPUT"
```

### Support Channels

1. **Documentation**: Check the [official docs](https://docs.vector-db-query.com)
2. **GitHub Issues**: Report bugs at [GitHub](https://github.com/your-org/vector-db-query/issues)
3. **Community Forum**: Ask questions at [forum.vector-db-query.com](https://forum.vector-db-query.com)
4. **Email Support**: support@vector-db-query.com

### When Reporting Issues

Include:
- Diagnostic report (from script above)
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces
- Configuration files (sanitized)

---

*Last Updated: $(date)*
*Version: 1.0*