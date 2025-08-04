# Production Deployment Guide

Complete guide for deploying the Ansera Data Sources system to production.

## Overview

This guide covers production deployment using two methods:
1. **Docker Compose** - For single-server deployments
2. **Kubernetes** - For scalable, multi-node deployments

## Prerequisites

### Required Tools

#### For Docker Deployment
- Docker Engine 20.10+
- Docker Compose 2.0+
- 16GB RAM minimum
- 100GB disk space

#### For Kubernetes Deployment
- Kubernetes 1.22+
- kubectl configured
- Helm 3.0+ (recommended)
- Container registry access

### Required Credentials
- Google API Key
- Gmail OAuth2 credentials
- Fireflies API key
- MCP authentication token
- SSL certificates for HTTPS

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Backup procedures in place
- [ ] Monitoring configured
- [ ] Security scan completed

## Docker Deployment

### 1. Prepare Environment

```bash
# Clone repository
git clone https://github.com/yourusername/vector-db-query.git
cd vector-db-query

# Copy and configure environment
cp deploy/.env.production.example deploy/.env.production
nano deploy/.env.production
```

### 2. Configure SSL

```bash
# Create SSL directory
mkdir -p deploy/nginx/ssl

# Copy certificates
cp /path/to/cert.pem deploy/nginx/ssl/
cp /path/to/key.pem deploy/nginx/ssl/
```

### 3. Deploy with Docker

```bash
# Run deployment script
./deploy/scripts/deploy.sh production docker

# Or manually:
cd deploy
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Verify Deployment

```bash
# Check service health
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f data-sources

# Test endpoints
curl https://yourdomain.com/api/health
```

## Kubernetes Deployment

### 1. Create Namespace and Secrets

```bash
# Create namespace
kubectl create namespace ansera

# Create secrets from env file
kubectl create secret generic ansera-secrets \
  --from-env-file=deploy/.env.production \
  --namespace=ansera
```

### 2. Deploy Infrastructure

```bash
# Deploy PostgreSQL
kubectl apply -f deploy/kubernetes/postgres.yaml

# Deploy Redis
kubectl apply -f deploy/kubernetes/redis.yaml

# Deploy Qdrant
kubectl apply -f deploy/kubernetes/qdrant.yaml

# Wait for infrastructure
kubectl wait --for=condition=ready pod -l app=postgres -n ansera --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n ansera --timeout=300s
kubectl wait --for=condition=ready pod -l app=qdrant -n ansera --timeout=300s
```

### 3. Deploy Application

```bash
# Build and push Docker image
docker build -f deploy/Dockerfile -t your-registry/ansera-data-sources:latest .
docker push your-registry/ansera-data-sources:latest

# Update image in deployment.yaml if needed
sed -i 's|ansera/data-sources:latest|your-registry/ansera-data-sources:latest|g' deploy/kubernetes/deployment.yaml

# Deploy application
kubectl apply -f deploy/kubernetes/deployment.yaml

# Check deployment status
kubectl rollout status deployment/ansera-data-sources -n ansera
```

### 4. Configure Ingress

```bash
# Update ingress with your domain
nano deploy/kubernetes/deployment.yaml

# Apply ingress
kubectl apply -f deploy/kubernetes/deployment.yaml

# Verify ingress
kubectl get ingress -n ansera
```

## Service Configuration

### API Endpoints

| Service | Port | Path | Description |
|---------|------|------|-------------|
| REST API | 8080 | /api/* | Main API endpoints |
| Monitoring | 8081 | /monitor/* | Streamlit dashboard |
| MCP Server | 5555 | /mcp/* | LLM integration |
| Prometheus | 9090 | /metrics | Metrics endpoint |
| Grafana | 3000 | / | Monitoring dashboards |

### Environment Variables

Key production environment variables:

```bash
# Environment
ENV=production
LOG_LEVEL=INFO

# Performance
MAX_CONCURRENT_ITEMS=30
BATCH_SIZE=150
PARALLEL_SOURCES=true
MEMORY_LIMIT_MB=4096

# Caching
CACHE_BACKEND=redis
CACHE_TTL=7200

# Security
MCP_AUTH_TOKEN=<secure-token>
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
```

## Monitoring Setup

### 1. Access Grafana

```bash
# Default credentials
Username: admin
Password: <from GRAFANA_PASSWORD env>

# Access URL
https://yourdomain.com:3000
```

### 2. Import Dashboards

1. Navigate to Dashboards > Import
2. Upload `deploy/monitoring/grafana/dashboards/data-sources-dashboard.json`
3. Select Prometheus datasource
4. Click Import

### 3. Configure Alerts

Alerts are automatically configured via Prometheus. Key alerts:
- High error rate (>5%)
- Low processing rate (<2 items/sec)
- Queue backlog (>1000 items)
- Service downtime

## Security Hardening

### 1. Network Security

```yaml
# Restrict internal services
# In docker-compose.prod.yml
services:
  postgres:
    expose:
      - "5432"  # Not ports, only internal
```

### 2. API Rate Limiting

Rate limits are configured in Nginx:
- API endpoints: 10 req/s
- Webhook endpoints: 50 req/s

### 3. Authentication

Ensure all services use strong authentication:
- PostgreSQL: Strong password
- Redis: Password authentication
- MCP: Token-based auth
- API: OAuth2 for user endpoints

## Backup and Recovery

### 1. Database Backup

```bash
# Automated daily backup
0 2 * * * docker exec ansera-postgres-prod pg_dump -U ansera_user ansera_prod | gzip > /backup/postgres-$(date +\%Y\%m\%d).sql.gz
```

### 2. Redis Backup

```bash
# Redis persistence is enabled
# Snapshots saved every 60 seconds
```

### 3. Qdrant Backup

```bash
# Backup Qdrant data
docker exec ansera-qdrant-prod tar -czf /backup/qdrant-backup.tar.gz /qdrant/storage
```

## Rollback Procedures

### Quick Rollback

```bash
# Docker rollback
./deploy/scripts/rollback.sh docker

# Kubernetes rollback
./deploy/scripts/rollback.sh kubernetes
```

### Manual Rollback

```bash
# Docker
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Kubernetes
kubectl rollout undo deployment/ansera-data-sources -n ansera
```

## Performance Tuning

### 1. Run Performance Analysis

```bash
# Inside container
vdq performance optimize --analyze
```

### 2. Apply Optimizations

```bash
# Apply balanced profile
vdq performance optimize --optimize --profile balanced
```

### 3. Monitor Performance

Access monitoring dashboard:
- URL: https://yourdomain.com/monitor/
- Check processing rates
- Monitor resource usage
- Review error rates

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs data-sources
kubectl logs -n ansera deployment/ansera-data-sources

# Common issues:
# - Database connection failed
# - Missing environment variables
# - Port conflicts
```

### High Memory Usage

```bash
# Reduce batch size
docker exec ansera-data-sources-prod \
  vdq config set data_sources.processing.batch_size 50

# Switch to disk cache
docker exec ansera-data-sources-prod \
  vdq config set data_sources.deduplication.cache_backend disk
```

### Slow Processing

```bash
# Increase concurrency
docker exec ansera-data-sources-prod \
  vdq config set data_sources.processing.max_concurrent_items 40

# Enable parallel sources
docker exec ansera-data-sources-prod \
  vdq config set data_sources.processing.parallel_sources true
```

## Maintenance

### Daily Tasks
- Check service health
- Review error logs
- Monitor queue length

### Weekly Tasks
- Review performance metrics
- Check disk usage
- Update dependencies

### Monthly Tasks
- Security updates
- Performance optimization
- Backup verification

## Support

For production support:
1. Check logs and metrics
2. Review troubleshooting guide
3. Contact support with:
   - Error messages
   - Log excerpts
   - Performance metrics
   - Steps to reproduce

---

*Last Updated: $(date)*
*Version: 1.0*