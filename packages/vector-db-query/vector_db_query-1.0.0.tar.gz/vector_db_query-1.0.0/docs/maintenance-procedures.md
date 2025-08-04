# Data Sources Maintenance Procedures

Regular maintenance procedures for the Vector DB Query Data Sources system.

## Maintenance Schedule

### Daily Tasks (Automated)

| Time | Task | Duration | Impact |
|------|------|----------|--------|
| 02:00 | Log rotation | 5 min | None |
| 02:15 | Cache cleanup | 10 min | None |
| 02:30 | Health checks | 5 min | None |
| 03:00 | Incremental backup | 30 min | Minimal |

### Weekly Tasks

| Day | Task | Duration | Impact |
|-----|------|----------|--------|
| Sunday 03:00 | Full deduplication | 1 hour | Moderate |
| Sunday 04:00 | Database optimization | 30 min | Minimal |
| Sunday 05:00 | Index rebuilding | 45 min | Moderate |
| Sunday 06:00 | Full system backup | 2 hours | None |

### Monthly Tasks

| Date | Task | Duration | Impact |
|------|------|----------|--------|
| 1st, 04:00 | Security updates | 2 hours | Downtime |
| 1st, 06:00 | Dependency updates | 1 hour | Downtime |
| 15th, 03:00 | Performance analysis | 3 hours | None |
| Last day | Storage cleanup | 2 hours | Minimal |

## Daily Maintenance

### Log Rotation

```bash
#!/bin/bash
# /opt/vdq/scripts/daily/rotate-logs.sh

LOG_DIR="/var/log/vdq"
RETENTION_DAYS=30

echo "[$(date)] Starting log rotation"

# Rotate application logs
find $LOG_DIR -name "*.log" -type f -exec gzip {} \;
find $LOG_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

# Rotate system logs
systemctl restart rsyslog

# Archive audit logs
tar -czf $LOG_DIR/audit/audit-$(date +%Y%m%d).tar.gz $LOG_DIR/audit/*.log
find $LOG_DIR/audit -name "*.log" -delete

echo "[$(date)] Log rotation complete"
```

### Cache Cleanup

```python
# cache_cleanup.py
import redis
import os
from datetime import datetime, timedelta
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)

def cleanup_cache():
    """Clean up expired cache entries."""
    r = redis.Redis.from_url(os.environ['REDIS_URL'])
    
    # Clean expired keys
    expired = 0
    for key in r.scan_iter("cache:*"):
        ttl = r.ttl(key)
        if ttl == -1:  # No expiration set
            r.expire(key, 86400)  # Set 24h expiration
        elif ttl == -2:  # Key doesn't exist
            expired += 1
    
    # Clean deduplication cache older than 90 days
    cutoff = datetime.now() - timedelta(days=90)
    pattern = f"dedup:*:{cutoff.strftime('%Y%m%d')}*"
    
    for key in r.scan_iter(pattern):
        r.delete(key)
        expired += 1
    
    logger.info(f"Cache cleanup complete. Removed {expired} expired keys")
    
    # Report cache statistics
    info = r.info('memory')
    logger.info(f"Cache memory usage: {info['used_memory_human']}")
    
if __name__ == "__main__":
    cleanup_cache()
```

### Health Checks

```bash
#!/bin/bash
# health_check.sh

SLACK_WEBHOOK="${SLACK_WEBHOOK_URL}"
ERRORS=0

function check_service() {
    SERVICE=$1
    if systemctl is-active --quiet $SERVICE; then
        echo "✓ $SERVICE is running"
    else
        echo "✗ $SERVICE is DOWN"
        ERRORS=$((ERRORS+1))
        notify_slack "$SERVICE is down!"
    fi
}

function check_endpoint() {
    NAME=$1
    URL=$2
    EXPECTED=$3
    
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $URL)
    if [ "$RESPONSE" = "$EXPECTED" ]; then
        echo "✓ $NAME endpoint is healthy"
    else
        echo "✗ $NAME endpoint returned $RESPONSE"
        ERRORS=$((ERRORS+1))
        notify_slack "$NAME endpoint unhealthy: $RESPONSE"
    fi
}

function notify_slack() {
    MESSAGE=$1
    curl -X POST -H 'Content-type: application/json' \
         --data "{\"text\":\"⚠️ VDQ Alert: $MESSAGE\"}" \
         $SLACK_WEBHOOK
}

echo "=== Vector DB Query Health Check ==="
echo "Time: $(date)"
echo ""

# Check services
check_service "vdq-sync"
check_service "postgresql"
check_service "redis"
check_service "nginx"

# Check endpoints
check_endpoint "Dashboard" "https://vdq.example.com/health" "200"
check_endpoint "API" "https://vdq.example.com/api/v1/health" "200"
check_endpoint "Qdrant" "http://localhost:6333/health" "200"

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "✗ Disk usage critical: $DISK_USAGE%"
    ERRORS=$((ERRORS+1))
    notify_slack "Disk usage critical: $DISK_USAGE%"
else
    echo "✓ Disk usage: $DISK_USAGE%"
fi

# Check database connections
DB_CONNECTIONS=$(psql -U vdq -d vector_db_query -t -c "SELECT count(*) FROM pg_stat_activity;")
if [ $DB_CONNECTIONS -gt 80 ]; then
    echo "✗ Database connections high: $DB_CONNECTIONS"
    notify_slack "Database connections high: $DB_CONNECTIONS"
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All systems healthy"
else
    echo "❌ $ERRORS health check(s) failed"
    exit 1
fi
```

## Weekly Maintenance

### Full Deduplication

```python
# weekly_deduplication.py
import asyncio
from datetime import datetime, timedelta
from vector_db_query.data_sources.deduplication import DeduplicationService
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)

async def run_full_deduplication():
    """Run comprehensive deduplication across all sources."""
    dedup_service = DeduplicationService()
    
    start_time = datetime.now()
    logger.info("Starting full deduplication run")
    
    # Phase 1: Analyze duplicates
    logger.info("Phase 1: Analyzing duplicates")
    stats = await dedup_service.analyze_duplicates(
        cross_source=True,
        date_range=timedelta(days=90)
    )
    
    logger.info(f"Found {stats['total_duplicates']} duplicate sets")
    logger.info(f"Potential space savings: {stats['space_savings_mb']} MB")
    
    # Phase 2: Mark duplicates
    logger.info("Phase 2: Marking duplicates")
    marked = await dedup_service.mark_duplicates(
        strategy='keep_newest',
        dry_run=False
    )
    
    logger.info(f"Marked {marked} items as duplicates")
    
    # Phase 3: Clean up
    logger.info("Phase 3: Cleaning up marked duplicates")
    if input("Proceed with cleanup? (y/n): ").lower() == 'y':
        cleaned = await dedup_service.cleanup_duplicates()
        logger.info(f"Removed {cleaned} duplicate items")
    
    # Phase 4: Rebuild indices
    logger.info("Phase 4: Rebuilding deduplication indices")
    await dedup_service.rebuild_indices()
    
    duration = datetime.now() - start_time
    logger.info(f"Full deduplication complete in {duration}")
    
    # Generate report
    report = await dedup_service.generate_report()
    logger.info(f"Report saved to: {report['path']}")

if __name__ == "__main__":
    asyncio.run(run_full_deduplication())
```

### Database Optimization

```sql
-- weekly_db_optimization.sql
-- Run every Sunday at 4 AM

-- Vacuum and analyze all tables
VACUUM ANALYZE;

-- Rebuild indexes that are bloated
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT 
            schemaname,
            tablename,
            indexname,
            pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes
        WHERE 
            schemaname = 'public' AND
            idx_scan < 100 AND
            pg_relation_size(indexrelid) > 1000000 -- 1MB
    LOOP
        EXECUTE 'REINDEX INDEX ' || quote_ident(r.schemaname) || '.' || quote_ident(r.indexname);
        RAISE NOTICE 'Reindexed: %.%', r.schemaname, r.indexname;
    END LOOP;
END $$;

-- Update table statistics
ANALYZE;

-- Find and fix any corrupted indexes
SELECT 
    n.nspname AS schema_name,
    c.relname AS table_name,
    c2.relname AS index_name
FROM pg_catalog.pg_class c
JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
JOIN pg_catalog.pg_index i ON i.indrelid = c.oid
JOIN pg_catalog.pg_class c2 ON c2.oid = i.indexrelid
WHERE 
    c.relkind = 'r' AND
    i.indisvalid = false;

-- Clean up old partitions (if using partitioning)
DO $$
DECLARE
    cutoff_date DATE := CURRENT_DATE - INTERVAL '6 months';
    partition_name TEXT;
BEGIN
    FOR partition_name IN
        SELECT tablename 
        FROM pg_tables 
        WHERE 
            schemaname = 'public' AND
            tablename LIKE 'processed_items_2%' AND
            tablename < 'processed_items_' || to_char(cutoff_date, 'YYYYMM')
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(partition_name);
        RAISE NOTICE 'Dropped old partition: %', partition_name;
    END LOOP;
END $$;

-- Report on table sizes and bloat
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS indexes_size,
    round(100 * pg_total_relation_size(schemaname||'.'||tablename) / NULLIF(sum(pg_total_relation_size(schemaname||'.'||tablename)) OVER (), 0), 2) AS percentage
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Index Optimization

```python
# index_optimization.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)

def optimize_indexes():
    """Analyze and optimize database indexes."""
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Find unused indexes
            cur.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                FROM pg_stat_user_indexes
                WHERE 
                    idx_scan = 0 AND
                    indexname NOT LIKE '%_pkey' AND
                    pg_relation_size(indexrelid) > 1000000  -- 1MB
                ORDER BY pg_relation_size(indexrelid) DESC;
            """)
            
            unused_indexes = cur.fetchall()
            if unused_indexes:
                logger.warning(f"Found {len(unused_indexes)} unused indexes")
                for idx in unused_indexes:
                    logger.info(f"Unused index: {idx['indexname']} ({idx['index_size']})")
            
            # Find duplicate indexes
            cur.execute("""
                WITH index_data AS (
                    SELECT 
                        indrelid,
                        indexrelid,
                        indkey,
                        indclass
                    FROM pg_index
                )
                SELECT 
                    a.indexrelid::regclass AS index1,
                    b.indexrelid::regclass AS index2,
                    pg_size_pretty(pg_relation_size(a.indexrelid)) AS size1,
                    pg_size_pretty(pg_relation_size(b.indexrelid)) AS size2
                FROM index_data a
                JOIN index_data b ON 
                    a.indrelid = b.indrelid AND
                    a.indkey = b.indkey AND
                    a.indexrelid > b.indexrelid;
            """)
            
            duplicate_indexes = cur.fetchall()
            if duplicate_indexes:
                logger.warning(f"Found {len(duplicate_indexes)} duplicate indexes")
                for dup in duplicate_indexes:
                    logger.info(f"Duplicate: {dup['index1']} duplicates {dup['index2']}")
            
            # Create missing indexes based on slow queries
            cur.execute("""
                SELECT 
                    query,
                    calls,
                    mean_exec_time,
                    total_exec_time
                FROM pg_stat_statements
                WHERE 
                    mean_exec_time > 1000 AND  -- queries taking > 1s
                    calls > 10
                ORDER BY mean_exec_time DESC
                LIMIT 10;
            """)
            
            slow_queries = cur.fetchall()
            if slow_queries:
                logger.info(f"Analyzing {len(slow_queries)} slow queries for index opportunities")
                # Here you would analyze the queries and suggest indexes
                
    finally:
        conn.close()

if __name__ == "__main__":
    optimize_indexes()
```

## Monthly Maintenance

### Security Updates

```bash
#!/bin/bash
# monthly_security_updates.sh

set -e

LOG_FILE="/var/log/vdq/security-updates-$(date +%Y%m%d).log"
BACKUP_DIR="/backup/pre-update-$(date +%Y%m%d)"

function log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "Starting monthly security updates"

# Create backup
log "Creating pre-update backup"
mkdir -p $BACKUP_DIR
cp -r /opt/vector-db-query $BACKUP_DIR/
pg_dump vector_db_query > $BACKUP_DIR/database.sql

# Update system packages
log "Updating system packages"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get autoremove -y

# Update Python dependencies
log "Checking Python dependencies for vulnerabilities"
cd /opt/vector-db-query
source venv/bin/activate

# Security audit
pip-audit --fix --desc

# Update specific security-sensitive packages
pip install --upgrade \
    cryptography \
    certifi \
    requests \
    urllib3 \
    paramiko

# Run security scans
log "Running security scans"
bandit -r src/ -f json -o $LOG_FILE.bandit.json
safety check --json > $LOG_FILE.safety.json

# Check for exposed secrets
log "Scanning for exposed secrets"
trufflehog filesystem /opt/vector-db-query --json > $LOG_FILE.trufflehog.json || true

# Update SSL certificates
log "Updating SSL certificates"
certbot renew --quiet

# Restart services
log "Restarting services"
systemctl restart vdq-sync vdq-monitor nginx

log "Security updates complete"
```

### Performance Analysis

```python
# monthly_performance_analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import asyncio
from vector_db_query.monitoring.metrics import MetricsCollector
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = MetricsCollector()
        self.report_dir = f"/var/reports/performance/{datetime.now().strftime('%Y%m')}"
        os.makedirs(self.report_dir, exist_ok=True)
    
    async def analyze_processing_performance(self):
        """Analyze processing performance over the past month."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Fetch metrics
        metrics = await self.metrics.get_historical_metrics(
            start_date=start_date,
            end_date=end_date,
            metrics=[
                'items_processed',
                'processing_time',
                'error_count',
                'queue_length'
            ]
        )
        
        df = pd.DataFrame(metrics)
        
        # Processing rate analysis
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 2, 1)
        df.groupby([pd.Grouper(key='timestamp', freq='D'), 'source'])['items_processed'].sum().plot()
        plt.title('Daily Processing Volume by Source')
        plt.ylabel('Items Processed')
        
        # Error rate analysis
        plt.subplot(2, 2, 2)
        error_rate = df.groupby(pd.Grouper(key='timestamp', freq='D'))['error_count'].sum() / \
                     df.groupby(pd.Grouper(key='timestamp', freq='D'))['items_processed'].sum() * 100
        error_rate.plot(color='red')
        plt.title('Daily Error Rate')
        plt.ylabel('Error Rate (%)')
        
        # Processing time trends
        plt.subplot(2, 2, 3)
        df.groupby([pd.Grouper(key='timestamp', freq='D'), 'source'])['processing_time'].mean().plot()
        plt.title('Average Processing Time by Source')
        plt.ylabel('Time (seconds)')
        
        # Queue length analysis
        plt.subplot(2, 2, 4)
        df.groupby(pd.Grouper(key='timestamp', freq='H'))['queue_length'].mean().plot()
        plt.title('Average Queue Length (Hourly)')
        plt.ylabel('Queue Length')
        
        plt.tight_layout()
        plt.savefig(f"{self.report_dir}/processing_performance.png")
        plt.close()
        
        # Generate statistics
        stats = {
            'total_processed': df['items_processed'].sum(),
            'average_daily_volume': df.groupby(pd.Grouper(key='timestamp', freq='D'))['items_processed'].sum().mean(),
            'total_errors': df['error_count'].sum(),
            'average_error_rate': (df['error_count'].sum() / df['items_processed'].sum() * 100),
            'average_processing_time': df['processing_time'].mean(),
            'peak_queue_length': df['queue_length'].max(),
            'sources': {
                source: {
                    'processed': df[df['source'] == source]['items_processed'].sum(),
                    'errors': df[df['source'] == source]['error_count'].sum(),
                    'avg_time': df[df['source'] == source]['processing_time'].mean()
                }
                for source in df['source'].unique()
            }
        }
        
        return stats
    
    async def analyze_resource_usage(self):
        """Analyze system resource usage."""
        # Fetch resource metrics
        metrics = await self.metrics.get_resource_metrics(
            period=timedelta(days=30)
        )
        
        df = pd.DataFrame(metrics)
        
        # Resource usage visualization
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # CPU usage
        df.groupby(pd.Grouper(key='timestamp', freq='H'))['cpu_percent'].mean().plot(ax=axes[0, 0])
        axes[0, 0].set_title('CPU Usage (%)')
        axes[0, 0].axhline(y=80, color='r', linestyle='--', label='Warning threshold')
        
        # Memory usage
        df.groupby(pd.Grouper(key='timestamp', freq='H'))['memory_percent'].mean().plot(ax=axes[0, 1])
        axes[0, 1].set_title('Memory Usage (%)')
        axes[0, 1].axhline(y=80, color='r', linestyle='--', label='Warning threshold')
        
        # Disk I/O
        df.groupby(pd.Grouper(key='timestamp', freq='H'))['disk_io_read_mb'].sum().plot(ax=axes[1, 0], label='Read')
        df.groupby(pd.Grouper(key='timestamp', freq='H'))['disk_io_write_mb'].sum().plot(ax=axes[1, 0], label='Write')
        axes[1, 0].set_title('Disk I/O (MB/hour)')
        axes[1, 0].legend()
        
        # Network I/O
        df.groupby(pd.Grouper(key='timestamp', freq='H'))['network_in_mb'].sum().plot(ax=axes[1, 1], label='In')
        df.groupby(pd.Grouper(key='timestamp', freq='H'))['network_out_mb'].sum().plot(ax=axes[1, 1], label='Out')
        axes[1, 1].set_title('Network I/O (MB/hour)')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig(f"{self.report_dir}/resource_usage.png")
        plt.close()
        
        return {
            'avg_cpu': df['cpu_percent'].mean(),
            'max_cpu': df['cpu_percent'].max(),
            'avg_memory': df['memory_percent'].mean(),
            'max_memory': df['memory_percent'].max(),
            'total_disk_read': df['disk_io_read_mb'].sum(),
            'total_disk_write': df['disk_io_write_mb'].sum(),
            'total_network_in': df['network_in_mb'].sum(),
            'total_network_out': df['network_out_mb'].sum()
        }
    
    async def generate_report(self):
        """Generate comprehensive performance report."""
        logger.info("Generating monthly performance report")
        
        # Collect all analyses
        processing_stats = await self.analyze_processing_performance()
        resource_stats = await self.analyze_resource_usage()
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>VDQ Performance Report - {datetime.now().strftime('%B %Y')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .metric {{ font-size: 24px; font-weight: bold; color: #007bff; }}
                .warning {{ color: #ff6b6b; }}
                .success {{ color: #51cf66; }}
                img {{ max-width: 100%; height: auto; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Vector DB Query Performance Report</h1>
            <p>Report Period: {(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}</p>
            
            <h2>Executive Summary</h2>
            <table>
                <tr>
                    <td>Total Items Processed</td>
                    <td class="metric">{processing_stats['total_processed']:,}</td>
                </tr>
                <tr>
                    <td>Average Daily Volume</td>
                    <td class="metric">{processing_stats['average_daily_volume']:,.0f}</td>
                </tr>
                <tr>
                    <td>Error Rate</td>
                    <td class="metric {'warning' if processing_stats['average_error_rate'] > 1 else 'success'}">
                        {processing_stats['average_error_rate']:.2f}%
                    </td>
                </tr>
                <tr>
                    <td>Average Processing Time</td>
                    <td class="metric">{processing_stats['average_processing_time']:.2f}s</td>
                </tr>
            </table>
            
            <h2>Processing Performance</h2>
            <img src="processing_performance.png" alt="Processing Performance Charts">
            
            <h2>Source Breakdown</h2>
            <table>
                <tr>
                    <th>Source</th>
                    <th>Items Processed</th>
                    <th>Errors</th>
                    <th>Error Rate</th>
                    <th>Avg Time</th>
                </tr>
        """
        
        for source, stats in processing_stats['sources'].items():
            error_rate = (stats['errors'] / stats['processed'] * 100) if stats['processed'] > 0 else 0
            html_content += f"""
                <tr>
                    <td>{source}</td>
                    <td>{stats['processed']:,}</td>
                    <td>{stats['errors']:,}</td>
                    <td class="{'warning' if error_rate > 1 else ''}">{error_rate:.2f}%</td>
                    <td>{stats['avg_time']:.2f}s</td>
                </tr>
            """
        
        html_content += f"""
            </table>
            
            <h2>Resource Usage</h2>
            <img src="resource_usage.png" alt="Resource Usage Charts">
            
            <table>
                <tr>
                    <td>Average CPU Usage</td>
                    <td class="metric {'warning' if resource_stats['avg_cpu'] > 70 else ''}">
                        {resource_stats['avg_cpu']:.1f}%
                    </td>
                </tr>
                <tr>
                    <td>Peak CPU Usage</td>
                    <td class="metric {'warning' if resource_stats['max_cpu'] > 90 else ''}">
                        {resource_stats['max_cpu']:.1f}%
                    </td>
                </tr>
                <tr>
                    <td>Average Memory Usage</td>
                    <td class="metric {'warning' if resource_stats['avg_memory'] > 70 else ''}">
                        {resource_stats['avg_memory']:.1f}%
                    </td>
                </tr>
                <tr>
                    <td>Total Disk I/O</td>
                    <td class="metric">
                        Read: {resource_stats['total_disk_read']:,.0f} MB<br>
                        Write: {resource_stats['total_disk_write']:,.0f} MB
                    </td>
                </tr>
            </table>
            
            <h2>Recommendations</h2>
            <ul>
        """
        
        # Add recommendations based on analysis
        if processing_stats['average_error_rate'] > 1:
            html_content += "<li class='warning'>High error rate detected. Review error logs and implement fixes.</li>"
        
        if resource_stats['avg_cpu'] > 70:
            html_content += "<li class='warning'>High CPU usage. Consider scaling horizontally or optimizing processing.</li>"
        
        if resource_stats['avg_memory'] > 70:
            html_content += "<li class='warning'>High memory usage. Consider increasing memory or optimizing memory usage.</li>"
        
        if processing_stats['peak_queue_length'] > 1000:
            html_content += "<li>Large queue backlogs observed. Consider increasing processing workers.</li>"
        
        html_content += """
            </ul>
            
            <p><em>Report generated on {}</em></p>
        </body>
        </html>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Save report
        report_path = f"{self.report_dir}/performance_report.html"
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Performance report saved to: {report_path}")
        return report_path

async def main():
    analyzer = PerformanceAnalyzer()
    report_path = await analyzer.generate_report()
    print(f"Report generated: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Storage Cleanup

```bash
#!/bin/bash
# monthly_storage_cleanup.sh

LOG_DIR="/var/log/vdq"
KNOWLEDGE_BASE="/opt/vector-db-query/knowledge_base"
CACHE_DIR="/var/cache/vdq"
BACKUP_DIR="/backup/vdq"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting monthly storage cleanup"

# 1. Clean old logs
log "Cleaning logs older than 90 days"
find $LOG_DIR -type f -name "*.log*" -mtime +90 -delete
find $LOG_DIR -type f -name "*.gz" -mtime +180 -delete

# 2. Archive old knowledge base items
log "Archiving knowledge base items older than 6 months"
ARCHIVE_DATE=$(date -d "6 months ago" +%Y%m%d)
ARCHIVE_FILE="$BACKUP_DIR/kb_archive_$ARCHIVE_DATE.tar.gz"

find $KNOWLEDGE_BASE -type f -mtime +180 -print0 | \
    tar --null -czf $ARCHIVE_FILE --files-from -

# Remove archived files
find $KNOWLEDGE_BASE -type f -mtime +180 -delete

# 3. Clean cache directories
log "Cleaning cache older than 30 days"
find $CACHE_DIR -type f -mtime +30 -delete

# 4. Clean temporary files
log "Cleaning temporary files"
find /tmp -name "vdq_*" -mtime +7 -delete

# 5. Database cleanup
log "Running database cleanup"
psql -U vdq -d vector_db_query << EOF
-- Delete old processed items (archived)
DELETE FROM processed_items 
WHERE processed_at < NOW() - INTERVAL '6 months'
AND status = 'archived';

-- Clean up orphaned metadata
DELETE FROM item_metadata 
WHERE item_id NOT IN (SELECT id FROM processed_items);

-- Vacuum to reclaim space
VACUUM FULL ANALYZE;
EOF

# 6. Clean old backups
log "Cleaning backups older than 90 days"
find $BACKUP_DIR -name "*.tar.gz" -mtime +90 -delete
find $BACKUP_DIR -name "*.sql" -mtime +90 -delete

# 7. Report disk usage
log "Current disk usage:"
df -h | grep -E "Filesystem|/"

log "Storage cleanup complete"

# Send summary email
mail -s "VDQ Monthly Storage Cleanup Report" admin@example.com << EOF
Monthly storage cleanup completed on $(date)

Disk usage after cleanup:
$(df -h | grep -E "Filesystem|/")

Knowledge base size: $(du -sh $KNOWLEDGE_BASE | cut -f1)
Log directory size: $(du -sh $LOG_DIR | cut -f1)
Cache directory size: $(du -sh $CACHE_DIR | cut -f1)
Backup directory size: $(du -sh $BACKUP_DIR | cut -f1)

Archived to: $ARCHIVE_FILE
EOF
```

## Emergency Maintenance

### System Recovery

```bash
#!/bin/bash
# emergency_recovery.sh

set -e

EMERGENCY_LOG="/var/log/vdq/emergency-$(date +%Y%m%d-%H%M%S).log"

function log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $EMERGENCY_LOG
}

function check_system() {
    log "Performing system checks..."
    
    # Check disk space
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 95 ]; then
        log "CRITICAL: Disk usage at $DISK_USAGE%"
        emergency_disk_cleanup
    fi
    
    # Check database
    if ! pg_isready -h localhost -p 5432; then
        log "Database not responding, attempting recovery"
        systemctl restart postgresql
        sleep 10
    fi
    
    # Check services
    for service in vdq-sync vdq-monitor redis nginx; do
        if ! systemctl is-active --quiet $service; then
            log "Service $service is down, restarting"
            systemctl restart $service
        fi
    done
}

function emergency_disk_cleanup() {
    log "Performing emergency disk cleanup"
    
    # Clear all logs older than 7 days
    find /var/log -name "*.log*" -mtime +7 -delete
    
    # Clear cache
    redis-cli FLUSHALL
    
    # Remove old backups
    find /backup -name "*.tar.gz" -mtime +30 -delete
    
    # Truncate large tables
    psql -U vdq -d vector_db_query -c "TRUNCATE TABLE audit_logs;"
}

function restore_from_backup() {
    BACKUP_FILE=$1
    
    log "Restoring from backup: $BACKUP_FILE"
    
    # Stop services
    systemctl stop vdq-sync vdq-monitor
    
    # Restore database
    dropdb vector_db_query || true
    createdb vector_db_query
    pg_restore -U vdq -d vector_db_query $BACKUP_FILE
    
    # Start services
    systemctl start vdq-sync vdq-monitor
    
    log "Restore complete"
}

# Main emergency response
case ${1:-check} in
    check)
        check_system
        ;;
    restore)
        restore_from_backup $2
        ;;
    reset)
        log "Performing system reset"
        systemctl stop vdq-sync vdq-monitor
        redis-cli FLUSHALL
        systemctl start vdq-sync vdq-monitor
        ;;
    *)
        echo "Usage: $0 {check|restore|reset}"
        exit 1
        ;;
esac
```

## Automation Scripts

### Maintenance Scheduler

```python
# maintenance_scheduler.py
import schedule
import time
import subprocess
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/vdq/maintenance-scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MaintenanceScheduler:
    def __init__(self):
        self.setup_schedule()
    
    def run_script(self, script_path, description):
        """Run a maintenance script and log the result."""
        logger.info(f"Starting: {description}")
        try:
            result = subprocess.run(
                ['bash', script_path],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            if result.returncode == 0:
                logger.info(f"Completed: {description}")
            else:
                logger.error(f"Failed: {description}\n{result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout: {description}")
        except Exception as e:
            logger.error(f"Error running {description}: {e}")
    
    def setup_schedule(self):
        """Set up the maintenance schedule."""
        # Daily tasks
        schedule.every().day.at("02:00").do(
            self.run_script, 
            "/opt/vdq/scripts/daily/rotate-logs.sh",
            "Daily log rotation"
        )
        schedule.every().day.at("02:15").do(
            self.run_script,
            "/opt/vdq/scripts/daily/cache-cleanup.sh",
            "Daily cache cleanup"
        )
        schedule.every().day.at("02:30").do(
            self.run_script,
            "/opt/vdq/scripts/daily/health-check.sh",
            "Daily health check"
        )
        
        # Weekly tasks
        schedule.every().sunday.at("03:00").do(
            self.run_script,
            "/opt/vdq/scripts/weekly/deduplication.sh",
            "Weekly deduplication"
        )
        schedule.every().sunday.at("04:00").do(
            self.run_script,
            "/opt/vdq/scripts/weekly/db-optimization.sh",
            "Weekly database optimization"
        )
        
        # Monthly tasks
        # Note: schedule doesn't support monthly, so we check manually
        schedule.every().day.at("04:00").do(self.check_monthly_tasks)
    
    def check_monthly_tasks(self):
        """Check and run monthly tasks on the 1st of each month."""
        if datetime.now().day == 1:
            self.run_script(
                "/opt/vdq/scripts/monthly/security-updates.sh",
                "Monthly security updates"
            )
            self.run_script(
                "/opt/vdq/scripts/monthly/performance-analysis.sh",
                "Monthly performance analysis"
            )
        
        # Storage cleanup on the last day of month
        tomorrow = datetime.now().replace(day=28) + timedelta(days=4)
        if tomorrow.month != datetime.now().month:
            self.run_script(
                "/opt/vdq/scripts/monthly/storage-cleanup.sh",
                "Monthly storage cleanup"
            )
    
    def run(self):
        """Run the scheduler."""
        logger.info("Maintenance scheduler started")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    scheduler = MaintenanceScheduler()
    scheduler.run()
```

---

*Last Updated: $(date)*
*Version: 1.0*