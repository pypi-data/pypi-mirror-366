# Data Sources Operations Guide

Comprehensive operational documentation for the Vector DB Query Data Sources system.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Deployment Guide](#deployment-guide)
4. [Configuration Management](#configuration-management)
5. [Operations Procedures](#operations-procedures)
6. [Monitoring & Alerting](#monitoring--alerting)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)
9. [Security Considerations](#security-considerations)
10. [Performance Tuning](#performance-tuning)
11. [Disaster Recovery](#disaster-recovery)
12. [API Reference](#api-reference)

## System Overview

The Data Sources system integrates Gmail, Fireflies.ai, and Google Drive to automatically sync and process documents for the Vector DB Query knowledge base.

### Key Features
- **Multi-source Integration**: Gmail (IMAP/OAuth2), Fireflies (API), Google Drive (OAuth2)
- **Real-time Processing**: Webhook support for instant updates
- **Content Intelligence**: NLP extraction, sentiment analysis, entity recognition
- **Deduplication**: Cross-source duplicate detection
- **Selective Processing**: Configurable filters and rules
- **Monitoring**: Real-time dashboards and metrics

### System Requirements
- Python 3.8+
- PostgreSQL 12+ or SQLite
- Redis (optional, for caching)
- 4GB+ RAM recommended
- 50GB+ storage for knowledge base

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources System                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Gmail     │  │  Fireflies   │  │  Google Drive   │  │
│  │  Connector  │  │  Connector   │  │   Connector     │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘  │
│         │                 │                    │           │
│         └─────────────────┴────────────────────┘           │
│                           │                                │
│                    ┌──────▼──────┐                        │
│                    │ Orchestrator│                        │
│                    └──────┬──────┘                        │
│                           │                                │
│         ┌─────────────────┴────────────────────┐          │
│         │                                       │          │
│    ┌────▼─────┐  ┌────────────┐  ┌───────────▼────┐     │
│    │Processing│  │Deduplication│  │ NLP Extraction │     │
│    │ Pipeline │  │   Engine    │  │    Engine      │     │
│    └────┬─────┘  └────────────┘  └────────────────┘     │
│         │                                                  │
│    ┌────▼────────────────────────┐                       │
│    │    Vector DB (Qdrant)       │                       │
│    └─────────────────────────────┘                       │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Source Authentication**: OAuth2/API key validation
2. **Data Retrieval**: Fetch emails/transcripts/documents
3. **Processing Pipeline**:
   - Content extraction
   - Metadata enrichment
   - NLP analysis
   - Deduplication check
4. **Vector Storage**: Embedding generation and storage
5. **Monitoring**: Metrics collection and dashboard updates

## Deployment Guide

### Prerequisites

1. **System Dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3.8 python3-pip postgresql redis-server
   
   # macOS
   brew install python@3.8 postgresql redis
   ```

2. **Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # PostgreSQL
   createdb vector_db_query
   
   # Run migrations
   alembic upgrade head
   ```

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-org/vector-db-query.git
   cd vector-db-query
   ```

2. **Install Dependencies**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt  # For development
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run Setup Wizard**
   ```bash
   vdq setup
   ```

5. **Start Services**
   ```bash
   # Start Qdrant
   docker-compose up -d qdrant
   
   # Start monitoring dashboard
   vdq monitor
   
   # Start data sync
   vdq datasources sync
   ```

### Production Deployment

#### Using Docker

```dockerfile
# Dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["vdq", "datasources", "sync", "--daemon"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  vector-db-query:
    build: .
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/vector_db
      - QDRANT_URL=http://qdrant:6333
    volumes:
      - ./config:/app/config
      - ./knowledge_base:/app/knowledge_base
    depends_on:
      - db
      - qdrant
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=vector_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  postgres_data:
  qdrant_data:
```

#### Using Kubernetes

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vector-db-query
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vector-db-query
  template:
    metadata:
      labels:
        app: vector-db-query
    spec:
      containers:
      - name: vector-db-query
        image: your-registry/vector-db-query:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: knowledge-base
          mountPath: /app/knowledge_base
      volumes:
      - name: config
        configMap:
          name: vdq-config
      - name: knowledge-base
        persistentVolumeClaim:
          claimName: knowledge-base-pvc
```

## Configuration Management

### Configuration Structure

```yaml
# config/default.yaml
data_sources:
  gmail:
    enabled: true
    email: user@example.com
    oauth_credentials_file: /path/to/credentials.json
    folders: ["INBOX", "[Gmail]/Sent Mail"]
    initial_history_days: 30
    sync_interval: 300  # seconds
    
  fireflies:
    enabled: true
    api_key: ${FIREFLIES_API_KEY}  # From environment
    webhook_enabled: true
    webhook_secret: ${FIREFLIES_WEBHOOK_SECRET}
    
  google_drive:
    enabled: true
    search_patterns: ["Notes by Gemini"]
    folder_ids: []  # Empty for all folders
    
  processing:
    parallel_sources: true
    max_concurrent_items: 10
    batch_size: 50
    
  deduplication:
    enabled: true
    similarity_threshold: 0.95
    cache_ttl: 86400  # 24 hours
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | sqlite:///./data.db | No |
| `QDRANT_URL` | Qdrant server URL | http://localhost:6333 | Yes |
| `GOOGLE_API_KEY` | Google API key for embeddings | - | Yes |
| `FIREFLIES_API_KEY` | Fireflies.ai API key | - | If Fireflies enabled |
| `LOG_LEVEL` | Logging level | INFO | No |
| `REDIS_URL` | Redis connection for caching | - | No |
| `SENTRY_DSN` | Sentry error tracking | - | No |

### Configuration Best Practices

1. **Use Environment Variables for Secrets**
   ```bash
   export FIREFLIES_API_KEY="your-api-key"
   export GOOGLE_API_KEY="your-google-key"
   ```

2. **Separate Configs by Environment**
   ```
   config/
   ├── default.yaml     # Base configuration
   ├── development.yaml # Dev overrides
   ├── staging.yaml     # Staging overrides
   └── production.yaml  # Production overrides
   ```

3. **Version Control Considerations**
   ```gitignore
   # .gitignore
   config/production.yaml
   *.json  # OAuth tokens
   .env
   ```

## Operations Procedures

### Daily Operations

#### 1. Health Checks
```bash
# Check system status
vdq datasources status

# Check specific source
vdq datasources status --source gmail

# Test connections
vdq datasources test
```

#### 2. Manual Sync
```bash
# Sync all sources
vdq datasources sync

# Sync specific source
vdq datasources sync --source fireflies

# Sync with date range
vdq datasources sync --start-date 2024-01-01 --end-date 2024-01-31
```

#### 3. Monitor Processing
```bash
# Open monitoring dashboard
vdq monitor

# Check processing stats
vdq datasources stats

# View recent errors
vdq datasources errors --limit 10
```

### Batch Operations

#### 1. Bulk Import
```bash
# Import historical data
vdq datasources import --source gmail --days 365

# Import with filters
vdq datasources import --source google_drive \
  --pattern "Meeting Notes" \
  --start-date 2023-01-01
```

#### 2. Reprocessing
```bash
# Reprocess failed items
vdq datasources reprocess --failed

# Reprocess by date range
vdq datasources reprocess --start-date 2024-01-01

# Force reprocess (ignore deduplication)
vdq datasources reprocess --force --source gmail
```

#### 3. Data Cleanup
```bash
# Remove duplicates
vdq datasources deduplicate

# Clean old cache
vdq datasources clean --cache --older-than 30d

# Remove processed items
vdq datasources clean --processed --older-than 90d
```

### Scheduled Tasks

#### Using Cron
```bash
# crontab -e
# Sync every 5 minutes
*/5 * * * * /usr/bin/vdq datasources sync --quiet

# Daily cleanup at 2 AM
0 2 * * * /usr/bin/vdq datasources clean --cache --older-than 7d

# Weekly deduplication
0 3 * * 0 /usr/bin/vdq datasources deduplicate
```

#### Using Systemd
```ini
# /etc/systemd/system/vdq-sync.service
[Unit]
Description=Vector DB Query Data Sync
After=network.target

[Service]
Type=simple
User=vdq
WorkingDirectory=/opt/vector-db-query
ExecStart=/usr/bin/vdq datasources sync --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/vdq-sync.timer
[Unit]
Description=Vector DB Query Sync Timer

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

## Monitoring & Alerting

### Metrics Collection

#### Key Metrics
- **Source Metrics**
  - Items processed per minute
  - Processing success rate
  - Average processing time
  - Queue length
  - Error rate

- **System Metrics**
  - CPU usage
  - Memory usage
  - Disk I/O
  - Network throughput
  - Database connections

#### Prometheus Integration
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'vector-db-query'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
```

### Dashboard Configuration

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Vector DB Query Data Sources",
    "panels": [
      {
        "title": "Processing Rate",
        "targets": [
          {
            "expr": "rate(vdq_items_processed_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(vdq_errors_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### Alert Rules

#### Critical Alerts
1. **Source Connection Failed**
   ```yaml
   - alert: SourceConnectionFailed
     expr: vdq_source_connection_status == 0
     for: 5m
     annotations:
       summary: "Data source {{ $labels.source }} connection failed"
   ```

2. **High Error Rate**
   ```yaml
   - alert: HighErrorRate
     expr: rate(vdq_errors_total[5m]) > 0.1
     for: 10m
     annotations:
       summary: "High error rate detected: {{ $value }}"
   ```

3. **Processing Queue Backlog**
   ```yaml
   - alert: ProcessingBacklog
     expr: vdq_queue_length > 1000
     for: 15m
     annotations:
       summary: "Large processing backlog: {{ $value }} items"
   ```

### Logging Configuration

```python
# logging_config.py
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/vdq.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/errors.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'json',
            'level': 'ERROR'
        }
    },
    'loggers': {
        'vector_db_query': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Gmail OAuth2 Error**
```
Error: OAuth2 token expired or invalid
```

**Solution:**
```bash
# Remove old token
rm .gmail_token.json

# Re-authenticate
vdq datasources auth --source gmail
```

**Fireflies API Key Invalid**
```
Error: 401 Unauthorized from Fireflies API
```

**Solution:**
```bash
# Update API key
vdq datasources configure --source fireflies
# Or set environment variable
export FIREFLIES_API_KEY="new-api-key"
```

#### 2. Processing Errors

**Memory Issues**
```
Error: Out of memory while processing large document
```

**Solution:**
```bash
# Reduce batch size
vdq config set processing.batch_size 10

# Increase memory limit
export PYTHONMEMORY=4G
```

**Timeout Errors**
```
Error: Timeout while fetching from source
```

**Solution:**
```yaml
# Increase timeout in config/default.yaml
data_sources:
  gmail:
    timeout: 120  # seconds
    retry_attempts: 5
```

#### 3. Database Issues

**Connection Pool Exhausted**
```
Error: QueuePool limit of size 5 overflow 10 reached
```

**Solution:**
```python
# Increase pool size in config
database:
  pool_size: 20
  max_overflow: 30
```

**Migration Errors**
```
Error: Database schema out of sync
```

**Solution:**
```bash
# Check migration status
alembic current

# Apply pending migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
vdq datasources sync --debug

# Trace specific component
vdq datasources sync --trace gmail

# Dry run mode
vdq datasources sync --dry-run
```

### Performance Profiling

```bash
# Profile processing performance
vdq datasources profile --source gmail --items 100

# Generate flame graph
vdq datasources profile --flame-graph --output profile.svg

# Memory profiling
vdq datasources profile --memory --source fireflies
```

## Maintenance

### Regular Maintenance Tasks

#### Daily
- Check error logs
- Monitor processing queues
- Verify source connections
- Review dashboard metrics

#### Weekly
- Run deduplication
- Clean old cache files
- Update NLP models
- Review and optimize slow queries

#### Monthly
- Database optimization
- Storage cleanup
- Security audit
- Performance review
- Update dependencies

### Database Maintenance

```sql
-- Vacuum and analyze PostgreSQL
VACUUM ANALYZE;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Find slow queries
SELECT 
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Storage Management

```bash
# Check storage usage
vdq storage stats

# Archive old data
vdq storage archive --older-than 180d --output /backup/archive.tar.gz

# Cleanup temporary files
vdq storage clean --temp --cache

# Compress knowledge base
vdq storage compress --source knowledge_base/
```

### Backup Procedures

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/vdq/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup database
pg_dump $DATABASE_URL > "$BACKUP_DIR/database.sql"

# Backup configuration
cp -r config/ "$BACKUP_DIR/config/"

# Backup knowledge base
tar -czf "$BACKUP_DIR/knowledge_base.tar.gz" knowledge_base/

# Backup vector database
docker exec qdrant qdrant-backup create /backup/qdrant.snapshot
cp /var/lib/docker/volumes/qdrant_data/_data/backup/qdrant.snapshot "$BACKUP_DIR/"

# Upload to S3
aws s3 sync "$BACKUP_DIR" s3://backups/vdq/
```

## Security Considerations

### Authentication Security

1. **OAuth2 Best Practices**
   - Use separate OAuth apps for production
   - Implement token rotation
   - Store tokens encrypted
   - Use minimal scopes

2. **API Key Management**
   - Use environment variables
   - Rotate keys regularly
   - Monitor key usage
   - Implement rate limiting

### Data Security

1. **Encryption**
   ```python
   # Enable encryption at rest
   from cryptography.fernet import Fernet
   
   encryption_key = Fernet.generate_key()
   cipher = Fernet(encryption_key)
   
   # Encrypt sensitive data
   encrypted_content = cipher.encrypt(content.encode())
   ```

2. **Access Control**
   ```yaml
   # rbac.yaml
   roles:
     admin:
       - datasources:*
       - config:*
     operator:
       - datasources:read
       - datasources:sync
     viewer:
       - datasources:read
   ```

### Network Security

1. **TLS Configuration**
   ```nginx
   # nginx.conf
   server {
       listen 443 ssl http2;
       ssl_certificate /etc/ssl/certs/vdq.crt;
       ssl_certificate_key /etc/ssl/private/vdq.key;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers HIGH:!aNULL:!MD5;
   }
   ```

2. **Firewall Rules**
   ```bash
   # iptables rules
   iptables -A INPUT -p tcp --dport 8501 -s 10.0.0.0/8 -j ACCEPT
   iptables -A INPUT -p tcp --dport 6333 -s 127.0.0.1 -j ACCEPT
   iptables -A INPUT -p tcp --dport 5432 -s 10.0.0.0/8 -j ACCEPT
   ```

### Compliance

1. **GDPR Compliance**
   - Implement data retention policies
   - Support right to deletion
   - Maintain audit logs
   - Encrypt PII data

2. **Audit Logging**
   ```python
   @audit_log
   def process_email(email_id: str):
       """Process email with audit trail."""
       audit.log({
           'action': 'process_email',
           'resource': email_id,
           'user': current_user,
           'timestamp': datetime.utcnow()
       })
   ```

## Performance Tuning

### Database Optimization

1. **Indexes**
   ```sql
   -- Create indexes for common queries
   CREATE INDEX idx_items_source_date ON processed_items(source_type, processed_at);
   CREATE INDEX idx_items_hash ON processed_items(content_hash);
   CREATE INDEX idx_metadata_item ON item_metadata(item_id);
   ```

2. **Query Optimization**
   ```python
   # Use batch operations
   def batch_insert(items: List[Dict]):
       with db.engine.begin() as conn:
           conn.execute(
               insert(ProcessedItem),
               items
           )
   ```

### Processing Optimization

1. **Parallel Processing**
   ```python
   # Configure thread pool
   from concurrent.futures import ThreadPoolExecutor
   
   executor = ThreadPoolExecutor(
       max_workers=10,
       thread_name_prefix='vdq-processor'
   )
   ```

2. **Caching Strategy**
   ```python
   # Redis caching
   from redis import Redis
   
   cache = Redis.from_url(REDIS_URL)
   
   @cache_result(ttl=3600)
   def get_processed_hashes():
       return set(db.query(ProcessedItem.content_hash).all())
   ```

### Resource Management

1. **Memory Optimization**
   ```python
   # Stream large files
   def process_large_file(filepath):
       with open(filepath, 'rb') as f:
           for chunk in iter(lambda: f.read(4096), b''):
               yield process_chunk(chunk)
   ```

2. **Connection Pooling**
   ```python
   # Database connection pool
   engine = create_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=30,
       pool_pre_ping=True,
       pool_recycle=3600
   )
   ```

## Disaster Recovery

### Backup Strategy

1. **Automated Backups**
   - Database: Daily full + hourly incremental
   - Configuration: Daily snapshot
   - Knowledge base: Weekly full + daily incremental
   - Vector DB: Daily snapshot

2. **Backup Retention**
   - Daily backups: 7 days
   - Weekly backups: 4 weeks
   - Monthly backups: 12 months

### Recovery Procedures

1. **Database Recovery**
   ```bash
   # Restore from backup
   pg_restore -d vector_db_query backup.dump
   
   # Point-in-time recovery
   pg_basebackup -D /recovery -Fp -Xs -P
   ```

2. **Knowledge Base Recovery**
   ```bash
   # Restore knowledge base
   tar -xzf knowledge_base_backup.tar.gz -C /
   
   # Verify integrity
   vdq storage verify --path knowledge_base/
   ```

3. **Vector DB Recovery**
   ```bash
   # Restore Qdrant snapshot
   docker exec qdrant qdrant-backup restore /backup/qdrant.snapshot
   
   # Rebuild if needed
   vdq vectors rebuild --source knowledge_base/
   ```

### Failover Procedures

1. **Manual Failover**
   ```bash
   # Switch to standby
   vdq failover --target standby1 --confirm
   
   # Update DNS
   vdq dns update --record datasources.example.com --target standby1
   ```

2. **Automated Failover**
   ```yaml
   # keepalived.conf
   vrrp_instance VI_1 {
       state MASTER
       interface eth0
       virtual_router_id 51
       priority 100
       advert_int 1
       authentication {
           auth_type PASS
           auth_pass secret
       }
       virtual_ipaddress {
           10.0.0.100
       }
   }
   ```

## API Reference

### REST API Endpoints

#### Source Management
```
GET    /api/v1/sources              - List all sources
GET    /api/v1/sources/{source}     - Get source details
POST   /api/v1/sources/{source}/sync - Trigger sync
DELETE /api/v1/sources/{source}/cache - Clear source cache
```

#### Processing Control
```
POST   /api/v1/process/start        - Start processing
POST   /api/v1/process/stop         - Stop processing
GET    /api/v1/process/status       - Get processing status
POST   /api/v1/process/reprocess    - Reprocess items
```

#### Monitoring
```
GET    /api/v1/metrics              - Get all metrics
GET    /api/v1/health               - Health check
GET    /api/v1/stats                - Get statistics
```

### Python API

```python
from vector_db_query.data_sources import DataSourceOrchestrator
from vector_db_query.data_sources.models import SourceType

# Initialize orchestrator
orchestrator = DataSourceOrchestrator()

# Sync all sources
await orchestrator.sync_all()

# Sync specific source
await orchestrator.sync_source(SourceType.GMAIL)

# Get source status
status = await orchestrator.get_source_status(SourceType.FIREFLIES)

# Process with custom options
await orchestrator.sync_source(
    SourceType.GOOGLE_DRIVE,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    force=True
)
```

### CLI Commands

```bash
# Source management
vdq datasources list
vdq datasources status [--source SOURCE]
vdq datasources sync [--source SOURCE] [--force]
vdq datasources test [--source SOURCE]

# Configuration
vdq datasources configure [--source SOURCE]
vdq config get [KEY]
vdq config set KEY VALUE

# Monitoring
vdq monitor
vdq datasources stats [--source SOURCE]
vdq datasources errors [--limit N]

# Maintenance
vdq datasources clean [--cache] [--processed] [--older-than DAYS]
vdq datasources deduplicate [--dry-run]
vdq storage stats
vdq storage archive --older-than DAYS --output FILE
```

## Appendices

### A. Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| DS001 | Authentication failed | Check credentials |
| DS002 | Connection timeout | Check network/firewall |
| DS003 | Rate limit exceeded | Reduce request rate |
| DS004 | Invalid configuration | Verify config file |
| DS005 | Processing failed | Check logs for details |
| DS006 | Deduplication error | Run deduplicate command |
| DS007 | Storage full | Free up disk space |
| DS008 | Database error | Check DB connection |

### B. Environment Variables Reference

```bash
# Core Settings
DATABASE_URL=postgresql://user:pass@localhost/vdq
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379

# API Keys
GOOGLE_API_KEY=your-google-api-key
FIREFLIES_API_KEY=your-fireflies-key

# Performance
MAX_WORKERS=10
BATCH_SIZE=50
CACHE_TTL=3600

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_URL=http://localhost:3000
SENTRY_DSN=https://key@sentry.io/project

# Security
ENCRYPTION_KEY=your-encryption-key
JWT_SECRET=your-jwt-secret
```

### C. Useful Scripts

```bash
#!/bin/bash
# health-check.sh
# Comprehensive health check script

set -e

echo "Checking Vector DB Query Health..."

# Check database
if psql $DATABASE_URL -c "SELECT 1" > /dev/null 2>&1; then
    echo "✓ Database connection OK"
else
    echo "✗ Database connection FAILED"
    exit 1
fi

# Check Qdrant
if curl -s $QDRANT_URL/health | grep -q "ok"; then
    echo "✓ Qdrant connection OK"
else
    echo "✗ Qdrant connection FAILED"
    exit 1
fi

# Check sources
for source in gmail fireflies google_drive; do
    if vdq datasources test --source $source > /dev/null 2>&1; then
        echo "✓ $source connection OK"
    else
        echo "✗ $source connection FAILED"
    fi
done

echo "Health check complete."
```

---

*Last Updated: $(date)*
*Version: 1.0*