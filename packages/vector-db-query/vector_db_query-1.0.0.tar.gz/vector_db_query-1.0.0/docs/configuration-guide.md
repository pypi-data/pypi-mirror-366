# Configuration Guide

## TASK-017: Update Configuration System - Completed

### Overview
The configuration system has been enhanced to support all new file formats, OCR settings, monitoring options, and advanced features. The system is fully backward compatible while providing new capabilities.

### Key Features

1. **Comprehensive File Format Support**
   - 39+ supported file formats organized by category
   - Custom extension support
   - Easy format validation and checking

2. **OCR Configuration**
   - Language selection (single or multiple)
   - DPI and preprocessing settings
   - Confidence thresholds
   - Tesseract path configuration

3. **Enhanced Settings**
   - Document processing options
   - Performance tuning
   - Monitoring configuration
   - Advanced query settings

4. **Configuration Management**
   - YAML-based configuration
   - Environment variable overrides
   - CLI management commands
   - Validation and health checks

### Configuration Structure

```yaml
app:
  name: "Vector DB Query System"
  version: "1.0.0"
  log_level: "INFO"

paths:
  data_dir: "./data"
  log_dir: "./logs"
  config_dir: "./config"
  temp_dir: "./temp"

document_processing:
  chunk_size: 1000
  chunk_overlap: 200
  max_file_size_mb: 100
  
  file_formats:
    documents: [".pdf", ".doc", ".docx", ".txt", ".md"]
    spreadsheets: [".xlsx", ".xls", ".csv"]
    presentations: [".pptx", ".ppt"]
    email: [".eml", ".mbox"]
    web: [".html", ".htm", ".xml"]
    config: [".json", ".yaml", ".ini", ".cfg"]
    images: [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"]
    logs: [".log"]
    data: [".geojson", ".jsonl"]
    archives: [".zip", ".tar", ".tar.gz"]
    custom_extensions: []
  
  ocr:
    enabled: true
    language: "eng"
    additional_languages: []
    dpi: 300
    confidence_threshold: 60.0
```

### Environment Variables

The following environment variables can override configuration:

| Variable | Config Path | Description |
|----------|-------------|-------------|
| `VECTOR_DB_LOG_LEVEL` | `app.log_level` | Logging level |
| `VECTOR_DB_DATA_DIR` | `paths.data_dir` | Data directory |
| `EMBEDDING_MODEL` | `embedding.model` | Embedding model name |
| `QDRANT_HOST` | `vector_db.host` | Qdrant host |
| `QDRANT_PORT` | `vector_db.port` | Qdrant port |
| `OCR_LANGUAGE` | `document_processing.ocr.language` | OCR language |
| `CHUNK_SIZE` | `document_processing.chunk_size` | Chunk size |
| `MONITORING_ENABLED` | `monitoring.enabled` | Enable monitoring |

### CLI Commands

The new configuration management commands:

```bash
# Show current configuration
vector-db-query config show
vector-db-query config show --format yaml
vector-db-query config show --format table
vector-db-query config show --format env

# Show specific section
vector-db-query config show --section document_processing

# Get/Set values
vector-db-query config get document_processing.chunk_size
vector-db-query config set document_processing.chunk_size 2000 --type int

# Validate configuration
vector-db-query config validate

# Show supported formats
vector-db-query config formats

# Add custom format
vector-db-query config add-format .xyz

# Export configuration
vector-db-query config export --output my-config.yaml

# Load configuration
vector-db-query config load custom-config.yaml
vector-db-query config load custom-config.yaml --merge

# Show environment variables
vector-db-query config env
```

### Configuration Locations

The system looks for configuration in these locations (in order):

1. Environment variable: `VECTOR_DB_CONFIG_PATH`
2. User home: `~/.vector-db-query/config.yaml`
3. System: `/etc/vector-db-query/config.yaml`
4. Package default: `<package>/config/default.yaml`
5. Current directory: `./config.yaml`

### Programmatic Usage

```python
from vector_db_query.utils.config import get_config

# Get configuration manager
config = get_config()

# Access values
log_level = config.get("app.log_level")
chunk_size = config.get("document_processing.chunk_size")

# Set values
config.set("app.log_level", "DEBUG")

# Subscribe to changes
def on_config_change(key, value):
    print(f"Config changed: {key} = {value}")
    
config.subscribe(on_config_change)

# Validate configuration
issues = config.validate()
if issues:
    print(f"Configuration issues: {issues}")

# Export as environment variables
env_vars = config.export_env()
```

### File Format Access

```python
# Check if format is supported
config = get_config()
formats = config.config.document_processing.file_formats

if formats.is_supported(".pdf"):
    print("PDF is supported")

# Get all supported formats
all_formats = formats.all_supported
print(f"Supporting {len(all_formats)} formats")

# Add custom format
formats.custom_extensions.append(".custom")
```

### OCR Configuration

```python
# Access OCR settings
ocr = config.config.document_processing.ocr

if ocr.enabled:
    print(f"OCR enabled with language: {ocr.languages}")
    print(f"Confidence threshold: {ocr.confidence_threshold}%")
```

### Advanced Features

1. **Configuration Validation**
   - Automatic validation on load
   - Path existence checks
   - Value range validation
   - Consistency checks

2. **Change Notifications**
   - Subscribe to configuration changes
   - Callback system for updates
   - Real-time configuration reloading

3. **Performance Settings**
   - Worker pool configuration
   - Memory limits
   - Batch processing settings
   - Connection pool tuning

4. **Monitoring Integration**
   - Metrics collection settings
   - Health check configuration
   - Alert webhook support
   - Performance tracking options

### Migration from Old Config

The new system is fully backward compatible. Existing configurations will work without changes. To access new features, you can:

1. Generate a new config: `vector-db-query config export --output new-config.yaml`
2. Edit to add new sections
3. Load the updated config: `vector-db-query config load new-config.yaml`

### Best Practices

1. **Use environment variables for deployment**
   - Keep sensitive data in environment
   - Use config files for defaults
   - Override with env vars in production

2. **Validate configuration**
   - Run `config validate` before deployment
   - Check for missing paths
   - Verify resource limits

3. **Monitor configuration changes**
   - Use callbacks for critical settings
   - Log configuration changes
   - Implement configuration versioning

4. **Optimize for your use case**
   - Adjust chunk sizes for your documents
   - Configure OCR for your languages
   - Tune worker pools for your hardware

### Troubleshooting

1. **Configuration not loading**
   - Check file path and permissions
   - Validate YAML syntax
   - Look for error messages in logs

2. **Environment variables not working**
   - Verify variable names (use `config env` to see mappings)
   - Check for typos and case sensitivity
   - Ensure variables are exported

3. **Validation failures**
   - Run `config validate` for details
   - Check path existence
   - Verify numeric ranges

4. **OCR not working**
   - Verify Tesseract installation
   - Check language data files
   - Review confidence thresholds