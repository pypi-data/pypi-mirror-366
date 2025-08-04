# Data Sources Deployment Guide

Step-by-step guide for deploying the Vector DB Query Data Sources system in production.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Deployment Methods](#deployment-methods)
4. [Security Configuration](#security-configuration)
5. [Production Configuration](#production-configuration)
6. [Deployment Steps](#deployment-steps)
7. [Post-Deployment Tasks](#post-deployment-tasks)
8. [Rollback Procedures](#rollback-procedures)
9. [Monitoring Setup](#monitoring-setup)
10. [Maintenance Windows](#maintenance-windows)

## Pre-Deployment Checklist

### ☑️ System Requirements
- [ ] Python 3.8+ installed
- [ ] PostgreSQL 12+ or SQLite ready
- [ ] Redis server (optional but recommended)
- [ ] Docker/Kubernetes environment (if containerizing)
- [ ] Minimum 4GB RAM, 50GB storage

### ☑️ Credentials & Access
- [ ] Gmail OAuth2 credentials obtained
- [ ] Fireflies API key acquired
- [ ] Google Drive OAuth2 credentials ready
- [ ] Database credentials configured
- [ ] SSL certificates prepared

### ☑️ Configuration Files
- [ ] Production config created
- [ ] Environment variables defined
- [ ] Secrets management configured
- [ ] Backup configuration ready

### ☑️ Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Load testing completed
- [ ] Security scan performed

## Infrastructure Requirements

### Hardware Specifications

#### Minimum Requirements
```yaml
minimum:
  cpu: 2 cores
  memory: 4GB RAM
  storage: 50GB SSD
  network: 100Mbps
```

#### Recommended Production
```yaml
production:
  cpu: 4+ cores
  memory: 16GB RAM
  storage: 500GB SSD
  network: 1Gbps
  redundancy: Active-passive failover
```

### Software Dependencies

```bash
# System packages
sudo apt-get update
sudo apt-get install -y \
  python3.8 python3-pip python3-venv \
  postgresql postgresql-contrib \
  redis-server \
  nginx \
  supervisor \
  git curl wget

# Python global packages
pip3 install --upgrade pip setuptools wheel
pip3 install virtualenv
```

### Network Requirements

#### Inbound Ports
| Port | Service | Description |
|------|---------|-------------|
| 443 | HTTPS | Web interface |
| 8501 | Streamlit | Monitoring dashboard |
| 6333 | Qdrant | Vector database |
| 5432 | PostgreSQL | Database |
| 6379 | Redis | Cache (internal) |

#### Outbound Connections
| Service | Endpoint | Port |
|---------|----------|------|
| Gmail | imap.gmail.com | 993 |
| Fireflies | api.fireflies.ai | 443 |
| Google Drive | www.googleapis.com | 443 |
| Qdrant | Vector DB host | 6333 |

## Deployment Methods

### Method 1: Direct Installation

#### Step 1: System Setup
```bash
# Create application user
sudo useradd -m -s /bin/bash vdq
sudo usermod -aG sudo vdq

# Create directory structure
sudo mkdir -p /opt/vector-db-query
sudo chown vdq:vdq /opt/vector-db-query

# Switch to app user
sudo su - vdq
cd /opt/vector-db-query
```

#### Step 2: Application Installation
```bash
# Clone repository
git clone https://github.com/your-org/vector-db-query.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

#### Step 3: Service Configuration
```ini
# /etc/systemd/system/vdq-sync.service
[Unit]
Description=Vector DB Query Data Sync Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=vdq
Group=vdq
WorkingDirectory=/opt/vector-db-query
Environment="PATH=/opt/vector-db-query/venv/bin"
ExecStart=/opt/vector-db-query/venv/bin/vdq datasources sync --daemon
Restart=always
RestartSec=10
StandardOutput=append:/var/log/vdq/sync.log
StandardError=append:/var/log/vdq/sync-error.log

[Install]
WantedBy=multi-user.target
```

### Method 2: Docker Deployment

#### Dockerfile
```dockerfile
# Dockerfile
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 vdq && chown -R vdq:vdq /app
USER vdq

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD vdq datasources status || exit 1

CMD ["vdq", "datasources", "sync", "--daemon"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: vector_db_query
      POSTGRES_USER: vdq
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vdq"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__HTTP_PORT: 6333

  vdq-sync:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_started
    environment:
      DATABASE_URL: postgresql://vdq:${DB_PASSWORD}@postgres:5432/vector_db_query
      REDIS_URL: redis://redis:6379
      QDRANT_URL: http://qdrant:6333
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      FIREFLIES_API_KEY: ${FIREFLIES_API_KEY}
    volumes:
      - ./config:/app/config:ro
      - ./knowledge_base:/app/knowledge_base
      - vdq_logs:/app/logs
    restart: unless-stopped

  vdq-monitor:
    build: .
    command: ["vdq", "monitor", "--host", "0.0.0.0"]
    depends_on:
      - vdq-sync
    ports:
      - "8501:8501"
    environment:
      DATABASE_URL: postgresql://vdq:${DB_PASSWORD}@postgres:5432/vector_db_query
      REDIS_URL: redis://redis:6379
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - vdq-monitor
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  vdq_logs:
```

### Method 3: Kubernetes Deployment

#### Namespace and ConfigMap
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vector-db-query

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vdq-config
  namespace: vector-db-query
data:
  default.yaml: |
    data_sources:
      gmail:
        enabled: true
        sync_interval: 300
      fireflies:
        enabled: true
        webhook_enabled: true
      google_drive:
        enabled: true
        search_patterns: ["Notes by Gemini"]
```

#### Secrets
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: vdq-secrets
  namespace: vector-db-query
type: Opaque
stringData:
  database-url: "postgresql://vdq:password@postgres:5432/vector_db_query"
  google-api-key: "your-google-api-key"
  fireflies-api-key: "your-fireflies-key"
```

#### Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vdq-sync
  namespace: vector-db-query
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vdq-sync
  template:
    metadata:
      labels:
        app: vdq-sync
    spec:
      serviceAccountName: vdq-sa
      containers:
      - name: vdq-sync
        image: your-registry/vector-db-query:latest
        command: ["vdq", "datasources", "sync", "--daemon"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: vdq-secrets
              key: database-url
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: vdq-secrets
              key: google-api-key
        - name: FIREFLIES_API_KEY
          valueFrom:
            secretKeyRef:
              name: vdq-secrets
              key: fireflies-api-key
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: knowledge-base
          mountPath: /app/knowledge_base
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          exec:
            command:
            - vdq
            - datasources
            - status
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          exec:
            command:
            - vdq
            - datasources
            - test
          initialDelaySeconds: 20
          periodSeconds: 10
      volumes:
      - name: config
        configMap:
          name: vdq-config
      - name: knowledge-base
        persistentVolumeClaim:
          claimName: knowledge-base-pvc
```

#### Service and Ingress
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: vdq-monitor
  namespace: vector-db-query
spec:
  selector:
    app: vdq-monitor
  ports:
  - port: 8501
    targetPort: 8501
    name: streamlit

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vdq-ingress
  namespace: vector-db-query
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - vdq.example.com
    secretName: vdq-tls
  rules:
  - host: vdq.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vdq-monitor
            port:
              number: 8501
```

## Security Configuration

### SSL/TLS Setup

#### Nginx Configuration
```nginx
# nginx.conf
server {
    listen 80;
    server_name vdq.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vdq.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Secrets Management

#### Using HashiCorp Vault
```python
# vault_config.py
import hvac

client = hvac.Client(
    url='https://vault.example.com',
    token=os.environ['VAULT_TOKEN']
)

# Read secrets
secrets = client.secrets.kv.v2.read_secret_version(
    path='vector-db-query/prod'
)

# Set environment variables
os.environ['FIREFLIES_API_KEY'] = secrets['data']['data']['fireflies_api_key']
os.environ['GOOGLE_API_KEY'] = secrets['data']['data']['google_api_key']
```

#### Using AWS Secrets Manager
```python
# aws_secrets.py
import boto3
import json

client = boto3.client('secretsmanager')

response = client.get_secret_value(
    SecretId='vector-db-query/production'
)

secrets = json.loads(response['SecretString'])
os.environ.update(secrets)
```

### Authentication & Authorization

#### API Key Authentication
```python
# api_auth.py
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

#### OAuth2 Integration
```python
# oauth_config.py
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=os.environ['GOOGLE_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)
```

## Production Configuration

### Environment-Specific Configs

```yaml
# config/production.yaml
data_sources:
  gmail:
    enabled: true
    sync_interval: 300  # 5 minutes
    batch_size: 100
    retry_attempts: 5
    timeout: 120
    
  fireflies:
    enabled: true
    webhook_enabled: true
    webhook_url: https://vdq.example.com/webhooks/fireflies
    rate_limit:
      requests_per_minute: 60
      
  google_drive:
    enabled: true
    max_results_per_query: 1000
    
  processing:
    parallel_sources: true
    max_workers: 20
    max_concurrent_items: 50
    
  deduplication:
    enabled: true
    cache_backend: redis
    cache_ttl: 86400
    
database:
  pool_size: 50
  max_overflow: 100
  pool_timeout: 30
  pool_recycle: 3600
  echo: false
  
logging:
  level: INFO
  format: json
  handlers:
    - type: file
      filename: /var/log/vdq/app.log
      max_bytes: 104857600  # 100MB
      backup_count: 10
    - type: syslog
      address: localhost:514
      
monitoring:
  metrics_enabled: true
  prometheus_port: 9090
  statsd:
    host: localhost
    port: 8125
    prefix: vdq
```

### Performance Tuning

```yaml
# performance.yaml
optimizations:
  # Database
  database:
    statement_timeout: 30000  # 30 seconds
    lock_timeout: 10000       # 10 seconds
    idle_in_transaction_timeout: 60000  # 1 minute
    
  # Caching
  cache:
    default_ttl: 3600
    max_entries: 10000
    eviction_policy: lru
    
  # Threading
  threading:
    thread_pool_size: 50
    queue_size: 1000
    
  # Memory
  memory:
    max_memory_percent: 80
    gc_threshold: 100MB
```

## Deployment Steps

### Step 1: Pre-deployment

```bash
#!/bin/bash
# pre-deploy.sh

echo "Running pre-deployment checks..."

# Check Python version
python3 --version | grep -E "3\.[89]|3\.1[0-9]" || exit 1

# Check database connectivity
pg_isready -h $DB_HOST -p $DB_PORT || exit 1

# Run tests
pytest tests/ || exit 1

# Security scan
bandit -r src/ || exit 1

# Check disk space
df -h | grep -E "^/" | awk '{print $5}' | grep -v "[89][0-9]%" || exit 1

echo "Pre-deployment checks passed!"
```

### Step 2: Database Migration

```bash
# Run migrations
alembic upgrade head

# Verify migration
alembic current

# Create initial data
python scripts/init_data.py
```

### Step 3: Deploy Application

```bash
#!/bin/bash
# deploy.sh

# Blue-green deployment
NEW_VERSION=$1
CURRENT_VERSION=$(docker ps --format "table {{.Names}}" | grep vdq-sync | head -1)

echo "Deploying version: $NEW_VERSION"

# Start new version
docker-compose -f docker-compose.prod.yml up -d --scale vdq-sync=2

# Health check
for i in {1..30}; do
    if docker exec vdq-sync-$NEW_VERSION vdq datasources status; then
        echo "New version healthy"
        break
    fi
    sleep 10
done

# Switch traffic
docker-compose -f docker-compose.prod.yml stop $CURRENT_VERSION

echo "Deployment complete"
```

### Step 4: Post-deployment Verification

```bash
#!/bin/bash
# verify-deployment.sh

echo "Verifying deployment..."

# Check services
for service in vdq-sync vdq-monitor postgres redis qdrant; do
    if systemctl is-active --quiet $service; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
        exit 1
    fi
done

# Test endpoints
curl -f https://vdq.example.com/health || exit 1
curl -f https://vdq.example.com/api/v1/sources || exit 1

# Check data flow
vdq datasources stats --check-flow || exit 1

echo "Deployment verified successfully!"
```

## Post-Deployment Tasks

### 1. Configure Monitoring

```bash
# Setup Prometheus
vdq monitoring setup --prometheus

# Configure alerts
vdq monitoring alerts --config alerts.yaml

# Setup dashboards
vdq monitoring dashboards --import
```

### 2. Setup Backups

```bash
# Configure automated backups
crontab -e
# Add:
0 2 * * * /opt/vector-db-query/scripts/backup.sh
```

### 3. Security Hardening

```bash
# Set file permissions
chmod 600 config/production.yaml
chown -R vdq:vdq /opt/vector-db-query

# Configure firewall
ufw allow 443/tcp
ufw allow 8501/tcp
ufw allow from 10.0.0.0/8 to any port 5432
ufw enable
```

### 4. Performance Baseline

```bash
# Run performance tests
vdq performance baseline --duration 1h

# Save results
vdq performance save --name "post-deployment-$(date +%Y%m%d)"
```

## Rollback Procedures

### Automated Rollback

```bash
#!/bin/bash
# rollback.sh

PREVIOUS_VERSION=$1

echo "Rolling back to version: $PREVIOUS_VERSION"

# Stop current version
docker-compose down

# Restore database
pg_restore -d vector_db_query backups/pre-deploy-$PREVIOUS_VERSION.dump

# Start previous version
docker-compose -f docker-compose.$PREVIOUS_VERSION.yml up -d

# Verify
vdq datasources status || exit 1

echo "Rollback complete"
```

### Manual Rollback Steps

1. **Stop Services**
   ```bash
   systemctl stop vdq-sync vdq-monitor
   ```

2. **Restore Code**
   ```bash
   cd /opt/vector-db-query
   git checkout tags/v$PREVIOUS_VERSION
   ```

3. **Restore Database**
   ```bash
   psql -U vdq -d postgres -c "DROP DATABASE vector_db_query;"
   psql -U vdq -d postgres -c "CREATE DATABASE vector_db_query;"
   pg_restore -U vdq -d vector_db_query backups/v$PREVIOUS_VERSION.dump
   ```

4. **Restart Services**
   ```bash
   systemctl start vdq-sync vdq-monitor
   ```

## Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'vector-db-query'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Vector DB Query Production",
    "panels": [
      {
        "title": "Processing Rate",
        "targets": [
          {
            "expr": "rate(vdq_items_processed_total[5m])",
            "legendFormat": "{{source}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(vdq_errors_total[5m])",
            "legendFormat": "{{source}} - {{error_type}}"
          }
        ]
      },
      {
        "title": "System Resources",
        "targets": [
          {
            "expr": "process_resident_memory_bytes{job='vector-db-query'}",
            "legendFormat": "Memory"
          },
          {
            "expr": "rate(process_cpu_seconds_total{job='vector-db-query'}[5m])",
            "legendFormat": "CPU"
          }
        ]
      }
    ]
  }
}
```

### Alert Rules

```yaml
# alerts.yaml
groups:
  - name: vdq_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(vdq_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"
          
      - alert: ProcessingBacklog
        expr: vdq_queue_length > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Large processing backlog"
          
      - alert: DatabaseConnectionFailure
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection lost"
```

## Maintenance Windows

### Scheduled Maintenance

```yaml
# maintenance-schedule.yaml
schedule:
  daily:
    - time: "02:00-02:30"
      tasks:
        - database_vacuum
        - log_rotation
        - cache_cleanup
        
  weekly:
    - day: sunday
      time: "03:00-04:00"
      tasks:
        - deduplication_full
        - index_optimization
        - backup_verification
        
  monthly:
    - day: 1
      time: "04:00-06:00"
      tasks:
        - security_updates
        - dependency_updates
        - performance_analysis
```

### Maintenance Scripts

```bash
#!/bin/bash
# maintenance.sh

MAINTENANCE_TYPE=$1

case $MAINTENANCE_TYPE in
  daily)
    echo "Running daily maintenance..."
    vdq maintenance vacuum
    vdq maintenance rotate-logs
    vdq maintenance clean-cache
    ;;
    
  weekly)
    echo "Running weekly maintenance..."
    vdq maintenance deduplicate --full
    vdq maintenance optimize-indexes
    vdq maintenance verify-backups
    ;;
    
  monthly)
    echo "Running monthly maintenance..."
    vdq maintenance update-dependencies
    vdq maintenance security-scan
    vdq maintenance performance-report
    ;;
esac
```

---

*Last Updated: $(date)*
*Version: 1.0*