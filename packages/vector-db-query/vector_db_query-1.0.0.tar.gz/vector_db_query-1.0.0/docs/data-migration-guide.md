# Data Migration Guide

Complete guide for migrating existing data to the Ansera Data Sources system.

## Overview

The data migration process transfers your existing emails, transcripts, and documents into the new system while:
- Preserving all metadata
- Avoiding duplicates
- Extracting entities and insights
- Building vector embeddings
- Maintaining data integrity

## Migration Phases

### Phase 1: Preparation
1. System health check
2. Credential verification
3. Backup creation
4. Resource allocation

### Phase 2: Migration
1. Source-by-source migration
2. Progress monitoring
3. Error handling
4. Incremental processing

### Phase 3: Validation
1. Data verification
2. Quality checks
3. Performance testing
4. Report generation

## Pre-Migration Checklist

Run the automated checklist:

```bash
# Check system readiness
./scripts/migration_checklist.sh

# Or use CLI
vdq migrate checklist
```

Manual checklist:
- [ ] All services running (PostgreSQL, Redis, Qdrant)
- [ ] Sufficient disk space (>20GB recommended)
- [ ] API credentials configured
- [ ] Database migrations applied
- [ ] Backup strategy in place

## Migration Commands

### Quick Start

```bash
# Migrate all sources with defaults
vdq migrate run --sources all

# Dry run first (recommended)
vdq migrate run --sources all --dry-run

# Migrate specific source
vdq migrate run --sources gmail --days 7
```

### Advanced Options

```bash
# Full migration with custom settings
python scripts/migrate_data_sources.py \
  --sources gmail fireflies google_drive \
  --gmail-days 7 \
  --gmail-folders INBOX Sent Important \
  --fireflies-days 30 \
  --drive-folder "1234567890" \
  --drive-days 30
```

### Production Migration

For production environments:

```bash
# Interactive mode (recommended for first run)
./deploy/scripts/migrate-production.sh interactive

# Automatic mode (for automation)
./deploy/scripts/migrate-production.sh auto

# Scheduled mode (for cron jobs)
./deploy/scripts/migrate-production.sh scheduled
```

## Source-Specific Configuration

### Gmail Migration

```yaml
# Default configuration
gmail:
  days_back: 7
  folders:
    - INBOX
    - Sent
    - Important
  batch_size: 100
  include_attachments: true
```

Important folders:
- **INBOX** - Primary inbox
- **Sent** - Sent messages
- **Important** - Gmail important flag
- **[Gmail]/All Mail** - All emails
- **Custom Labels** - Your labels

### Fireflies Migration

```yaml
# Default configuration
fireflies:
  days_back: 30
  batch_size: 50
  include_summaries: true
  include_action_items: true
```

Data migrated:
- Meeting transcripts
- Summaries
- Action items
- Attendee information
- Meeting metadata

### Google Drive Migration

```yaml
# Default configuration
google_drive:
  days_back: 30
  folder_id: root  # or specific folder ID
  pattern: "Notes by Gemini"
  recursive: true
  batch_size: 100
```

File detection:
- Pattern matching for "Notes by Gemini"
- Google Docs format
- Modified date filtering
- Folder hierarchy preserved

## Migration Strategies

### 1. Full Historical Migration

Best for initial setup:

```bash
# Migrate all available history
vdq migrate run --sources all --days 365
```

Considerations:
- Takes longer
- Higher resource usage
- Complete data set

### 2. Recent Data Migration

Best for quick start:

```bash
# Migrate last week only
vdq migrate run --sources all --days 7
```

Benefits:
- Fast migration
- Recent data focus
- Lower resource usage

### 3. Incremental Migration

Best for ongoing sync:

```bash
# Migrate since last sync
vdq migrate run --sources all --days 1
```

Use cases:
- Daily cron jobs
- Continuous updates
- Minimal overhead

### 4. Source-by-Source Migration

Best for control:

```bash
# Migrate sources individually
vdq migrate run --sources gmail --days 7
vdq migrate run --sources fireflies --days 30
vdq migrate run --sources google_drive --days 30
```

Advantages:
- Error isolation
- Resource management
- Progress tracking

## Monitoring Migration

### Real-time Progress

```bash
# Check migration status
vdq migrate status

# Watch logs
vdq migrate logs --follow

# Monitor specific source
vdq migrate status --source gmail
```

### Progress Indicators

The migration shows:
- Items processed
- Items skipped (duplicates)
- Errors encountered
- Processing rate
- Time remaining

### Error Handling

View errors:

```bash
# Show recent errors
vdq migrate logs --errors

# Show errors for specific source
vdq migrate logs --errors --source gmail

# Detailed error information
vdq migrate logs --errors --lines 100
```

## Post-Migration Validation

### 1. Verify Counts

```bash
# Check item counts
vdq migrate status

# Detailed report
vdq migrate report --output validation_report.json
```

### 2. Test Queries

```bash
# Test each source
vdq query "test" --source gmail --limit 5
vdq query "meeting" --source fireflies --limit 5
vdq query "notes" --source google_drive --limit 5
```

### 3. Check Data Quality

```python
# Verify entity extraction
from vector_db_query.db.manager import DatabaseManager

db = DatabaseManager()
with db.get_session() as session:
    # Check for entities
    entities = session.execute(
        "SELECT COUNT(*) FROM entities"
    ).scalar()
    print(f"Entities extracted: {entities}")
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

```bash
# Re-authenticate Gmail
vdq setup gmail

# Check credentials
vdq auth status
```

#### 2. Rate Limiting

```yaml
# Adjust rate limits in config
data_sources:
  gmail:
    rate_limit: 10  # requests per second
    retry_delay: 60  # seconds
```

#### 3. Memory Issues

```bash
# Reduce batch size
vdq migrate run --batch-size 50

# Use disk cache
vdq config set data_sources.deduplication.cache_backend disk
```

#### 4. Duplicate Processing

```bash
# Clear duplicate cache
redis-cli FLUSHDB

# Force reprocessing
vdq migrate run --force
```

### Debug Mode

Enable detailed logging:

```bash
# Set debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
vdq migrate run --sources gmail -v
```

## Performance Optimization

### 1. Batch Size Tuning

```bash
# Larger batches for better throughput
vdq config set data_sources.processing.batch_size 200

# Smaller batches for limited memory
vdq config set data_sources.processing.batch_size 50
```

### 2. Parallel Processing

```bash
# Enable parallel source processing
vdq config set data_sources.processing.parallel_sources true

# Set concurrent items
vdq config set data_sources.processing.max_concurrent_items 20
```

### 3. Resource Limits

```bash
# Set memory limit
vdq config set data_sources.processing.memory_limit_mb 4096

# Set CPU limit
vdq config set data_sources.processing.cpu_limit_percent 70
```

## Scheduled Migration

### Cron Setup

```bash
# Daily incremental migration
0 2 * * * /app/deploy/scripts/migrate-production.sh scheduled >> /var/log/migration.log 2>&1

# Weekly full sync
0 3 * * 0 /app/deploy/scripts/migrate-production.sh auto >> /var/log/migration-weekly.log 2>&1
```

### Systemd Timer

```ini
# /etc/systemd/system/ansera-migration.service
[Unit]
Description=Ansera Data Migration
After=network.target

[Service]
Type=oneshot
ExecStart=/app/deploy/scripts/migrate-production.sh scheduled
User=ansera

# /etc/systemd/system/ansera-migration.timer
[Unit]
Description=Daily Ansera Migration

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

## Migration Reports

### Generate Report

```bash
# Default report
vdq migrate report

# Custom output
vdq migrate report --output /reports/migration_$(date +%Y%m%d).json

# Include performance metrics
vdq migrate report --detailed
```

### Report Contents

- Migration timestamp
- Items processed per source
- Success/error rates
- Processing duration
- Resource usage
- Recommendations

## Best Practices

### 1. Start Small
- Begin with dry run
- Migrate recent data first
- Validate before full migration

### 2. Monitor Resources
- Check CPU and memory usage
- Monitor disk space
- Watch for rate limits

### 3. Handle Errors Gracefully
- Review error logs
- Fix issues before retry
- Use incremental approach

### 4. Maintain Backups
- Backup before migration
- Keep migration logs
- Document configuration

### 5. Plan Maintenance Windows
- Schedule during low usage
- Notify users
- Have rollback plan

## Recovery Procedures

### Rollback Migration

```bash
# Stop current migration
pkill -f migrate_data_sources.py

# Restore from backup
pg_restore -h postgres -U ansera_user -d ansera_prod < backup.sql

# Clear processed items
psql -h postgres -U ansera_user -d ansera_prod -c "TRUNCATE data_sources.processed_items"

# Reset sync status
psql -h postgres -U ansera_user -d ansera_prod -c "UPDATE data_sources.sync_status SET status = 'idle'"
```

### Partial Recovery

```bash
# Remove specific source data
DELETE FROM data_sources.processed_items WHERE source_type = 'gmail';

# Reset source status
UPDATE data_sources.sync_status SET status = 'idle' WHERE source_type = 'gmail';

# Re-run migration
vdq migrate run --sources gmail
```

---

*Last Updated: $(date)*
*Version: 1.0*