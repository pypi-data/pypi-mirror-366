# Usage Examples

This guide provides practical examples for common use cases with Vector DB Query.

## Table of Contents

1. [Basic Document Processing](#basic-document-processing)
2. [Format-Specific Processing](#format-specific-processing)
3. [OCR Processing](#ocr-processing)
4. [Advanced Querying](#advanced-querying)
5. [Configuration Examples](#configuration-examples)
6. [Python API Examples](#python-api-examples)
7. [MCP Integration](#mcp-integration)
8. [Monitoring and Management](#monitoring-and-management)

## Basic Document Processing

### Process a Single Directory

```bash
# Process all documents in a directory
vector-db-query process ~/Documents/projects

# Process recursively
vector-db-query process ~/Documents/projects --recursive

# Show what would be processed without actually processing
vector-db-query process ~/Documents/projects --dry-run --verbose
```

### Process Specific Files

```bash
# Process individual files
vector-db-query process -i file1.pdf -i file2.docx -i file3.xlsx

# Process with glob patterns
vector-db-query process ~/Documents/*.pdf

# Process from a file list
find ~/Documents -name "*.pdf" | xargs vector-db-query process -i
```

## Format-Specific Processing

### Documents Only

```bash
# Process only PDF and Word documents
vector-db-query process ~/Documents --formats pdf,docx

# Process only text-based documents
vector-db-query process ~/Documents --formats txt,md,rtf
```

### Spreadsheets with Special Options

```bash
# Enable formula extraction for Excel files
export VECTOR_DB_EXCEL_EXTRACT_FORMULAS=true
export VECTOR_DB_EXCEL_MAX_ROWS=5000
vector-db-query process ~/Spreadsheets --formats xlsx,xls,csv

# Or use configuration
vector-db-query config set document_processing.format_settings.excel.extract_formulas true
vector-db-query process ~/Spreadsheets
```

### Email Processing

```bash
# Process emails with attachment extraction
export VECTOR_DB_EMAIL_EXTRACT_ATTACHMENTS=true
vector-db-query process ~/Mail/archives --formats eml,mbox

# Process without attachments for faster processing
export VECTOR_DB_EMAIL_EXTRACT_ATTACHMENTS=false
vector-db-query process ~/Mail/archives
```

### Web Content

```bash
# Convert HTML to markdown during processing
export VECTOR_DB_HTML_CONVERT_MARKDOWN=true
vector-db-query process ~/web-scrapes --formats html,htm

# Process with link preservation
vector-db-query config set document_processing.format_settings.html.preserve_links true
```

## OCR Processing

### Basic OCR

```bash
# Process images with OCR (English)
vector-db-query process ~/Images --ocr

# Process with specific language
vector-db-query process ~/Images --ocr --ocr-lang fra

# Multiple languages
vector-db-query process ~/Documents --ocr --ocr-lang "eng+fra+deu"
```

### Advanced OCR Configuration

```bash
# Set OCR configuration
vector-db-query config set document_processing.format_settings.ocr.enabled true
vector-db-query config set document_processing.format_settings.ocr.language "eng+fra"
vector-db-query config set document_processing.format_settings.ocr.confidence_threshold 70.0

# Process mixed documents (PDFs with images, scanned documents, etc.)
vector-db-query process ~/MixedDocuments --ocr
```

### Check OCR Support

```bash
# Check if OCR is available
vector-db-query formats --check-ocr

# See which files would use OCR
vector-db-query formats ~/Documents --recursive | grep -E "\.(png|jpg|jpeg|tiff|bmp)"
```

## Advanced Querying

### Natural Language Search

```bash
# Simple query
vector-db-query query "How to implement authentication?"

# Query with more results
vector-db-query query "machine learning algorithms" --limit 20

# Query with minimum score threshold
vector-db-query query "Python async programming" --score-threshold 0.8
```

### Filtered Queries

```bash
# Query only PDF files
vector-db-query query "security best practices" --filter file_type=pdf

# Query documents from last week
vector-db-query query "meeting notes" --filter "date>2025-07-24"

# Multiple filters
vector-db-query query "budget report" --filter file_type=xlsx --filter "date>2025-01-01"
```

### Export Results

```bash
# Export to JSON
vector-db-query query "API documentation" --export results.json

# Export to Markdown
vector-db-query query "project requirements" --export results.md --format markdown

# Export to CSV
vector-db-query query "customer data" --export results.csv --format csv
```

## Configuration Examples

### Initial Setup

```bash
# Interactive setup
vector-db-query config setup

# Manual configuration
vector-db-query config set embedding.model "gemini-embedding-001"
vector-db-query config set vector_db.host "localhost"
vector-db-query config set vector_db.port 6333
```

### Chunking Configuration

```bash
# Adjust chunk size for larger documents
vector-db-query config set document_processing.chunk_size 2000
vector-db-query config set document_processing.chunk_overlap 400

# Use semantic chunking
vector-db-query config set document_processing.chunking_strategy "semantic"
```

### Performance Tuning

```bash
# Enable parallel processing
vector-db-query config set document_processing.parallel_processing true
vector-db-query config set document_processing.max_workers 8

# Set memory limits
vector-db-query config set document_processing.memory_limit_mb 2048
```

## Python API Examples

### Basic Processing

```python
from vector_db_query import DocumentProcessor
from pathlib import Path

# Initialize processor
processor = DocumentProcessor(
    chunk_size=1000,
    chunk_overlap=200,
    enable_ocr=True,
    ocr_language="eng"
)

# Process a directory
documents = processor.process_directory(
    Path("/path/to/documents"),
    recursive=True
)

for doc in documents:
    print(f"Processed: {doc.file_path}")
    print(f"Chunks: {len(doc.chunks)}")
    print(f"Processing time: {doc.processing_time:.2f}s")
```

### Format-Specific Processing

```python
from vector_db_query import DocumentProcessor

# Process only specific formats
processor = DocumentProcessor(
    allowed_formats=["pdf", "docx", "xlsx"],
    enable_ocr=False  # Disable OCR for faster processing
)

# Process with progress callback
def on_progress(current, total, file_name):
    percent = (current / total) * 100
    print(f"[{percent:.1f}%] Processing: {file_name}")

documents = list(processor.process_directory(
    Path("/data"),
    recursive=True,
    progress_callback=on_progress
))
```

### Custom Configuration

```python
from vector_db_query.utils.config import ConfigManager

# Load custom configuration
config = ConfigManager("/path/to/custom-config.yaml")

# Update settings programmatically
config.set("document_processing.format_settings.excel.extract_formulas", True)
config.set("document_processing.format_settings.email.extract_attachments", True)

# Save configuration
config.config.save(Path("updated-config.yaml"))
```

### Query API

```python
from vector_db_query import VectorDBClient

# Initialize client
client = VectorDBClient()

# Simple query
results = client.query(
    "machine learning",
    limit=10,
    score_threshold=0.7
)

for result in results:
    print(f"Score: {result.score:.3f}")
    print(f"File: {result.metadata['file_path']}")
    print(f"Text: {result.text[:200]}...")
    print("-" * 80)

# Advanced query with filters
results = client.query(
    "Python programming",
    filters={
        "file_type": "py",
        "date": {"$gte": "2025-01-01"}
    },
    limit=20
)
```

## MCP Integration

### Start MCP Server

```bash
# Initialize MCP configuration
vector-db-query mcp init

# Start the server
vector-db-query mcp start

# Start with custom settings
vector-db-query mcp start --host 0.0.0.0 --port 5001
```

### Connect from Claude

```javascript
// In Claude Desktop settings
{
  "mcpServers": {
    "vector-db": {
      "command": "vector-db-query",
      "args": ["mcp", "serve"],
      "env": {
        "MCP_AUTH_TOKEN": "your-token-here"
      }
    }
  }
}
```

### Use MCP Tools

```python
# From Claude or other MCP clients
await use_mcp_tool("query-vector-db", {
    "query": "How to implement caching?",
    "limit": 5,
    "filters": {"file_type": "py"}
})

await use_mcp_tool("search-similar", {
    "document_id": "doc-123",
    "limit": 10
})
```

## Monitoring and Management

### Real-time Monitoring

```bash
# Start monitoring dashboard
vector-db-query monitor start

# View processing statistics
vector-db-query monitor stats

# Check system health
vector-db-query monitor health
```

### Batch Processing Management

```bash
# Process large dataset with monitoring
vector-db-query process /large-dataset --recursive &
PROCESS_ID=$!

# Monitor progress
vector-db-query monitor progress $PROCESS_ID

# View logs
vector-db-query monitor logs --tail 100
```

### Database Management

```bash
# Check database status
vector-db-query vector status

# Show collection statistics
vector-db-query vector stats

# Backup collection
vector-db-query vector backup --output backup.snapshot

# Clear and rebuild
vector-db-query vector clear --confirm
vector-db-query process /documents --recursive
```

## Common Workflows

### Initial Document Import

```bash
# 1. Check what will be processed
vector-db-query process ~/Documents --dry-run --stats

# 2. Configure processing options
vector-db-query config set document_processing.chunk_size 1500
vector-db-query config set document_processing.format_settings.ocr.enabled true

# 3. Process documents
vector-db-query process ~/Documents --recursive --verbose

# 4. Verify import
vector-db-query vector stats
```

### Regular Updates

```bash
# Process only new files since last run
find ~/Documents -type f -mtime -7 | xargs vector-db-query process -i

# Or use built-in incremental processing (future feature)
vector-db-query process ~/Documents --incremental
```

### Migration from Another System

```python
import json
from pathlib import Path
from vector_db_query import DocumentProcessor, VectorDBClient

# Load existing data
with open("legacy_data.json") as f:
    legacy_docs = json.load(f)

processor = DocumentProcessor()
client = VectorDBClient()

# Process and import
for doc in legacy_docs:
    # Create temporary file
    temp_file = Path(f"/tmp/{doc['id']}.txt")
    temp_file.write_text(doc['content'])
    
    # Process
    processed = processor.process_file(temp_file)
    
    # Add with metadata
    client.add_document(
        processed,
        metadata={
            "legacy_id": doc['id'],
            "imported_from": "legacy_system",
            **doc.get('metadata', {})
        }
    )
    
    # Clean up
    temp_file.unlink()
```

## Troubleshooting Examples

### Debug Processing Issues

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
vector-db-query process problem-file.pdf --verbose

# Check file format support
vector-db-query formats problem-file.pdf --debug

# Test with single file
vector-db-query process -i problem-file.pdf --dry-run
```

### Fix Encoding Issues

```python
from vector_db_query.document_processor import DocumentProcessor

# Force specific encoding
processor = DocumentProcessor()
processor.reader_factory._readers['text'].encoding = 'latin-1'

# Process problematic files
doc = processor.process_file("problematic-file.txt")
```

### Optimize for Large Files

```bash
# Increase chunk size for large documents
vector-db-query config set document_processing.chunk_size 3000
vector-db-query config set document_processing.scanner.max_file_size_mb 500

# Process with memory limits
vector-db-query process /large-files --memory-limit 4096
```

---

For more examples, see the [File Formats Guide](file-formats-guide.md) or run `vector-db-query --help`.