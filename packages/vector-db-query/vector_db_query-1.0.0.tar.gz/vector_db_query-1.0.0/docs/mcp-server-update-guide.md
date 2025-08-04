# MCP Server Update Guide

## Overview

This guide describes the updates made to the MCP server to support the extended file format capabilities introduced in EPIC-005.

## New Features

### 1. Format-Aware Search

The `query_vectors` tool now supports filtering by file type:

```json
{
  "tool": "query_vectors",
  "parameters": {
    "query": "machine learning algorithms",
    "file_types": ["pdf", "docx", "md"],
    "limit": 20
  }
}
```

Search results now include format information:

```json
{
  "results": [{
    "content": "...",
    "format_info": {
      "extension": ".pdf",
      "category": "documents",
      "reader": "PDFReader"
    }
  }]
}
```

### 2. Document Processing Tool

New tool for processing documents with format detection:

```json
{
  "tool": "process_document",
  "parameters": {
    "file_path": "/path/to/document.xlsx",
    "ocr_enabled": true,
    "ocr_language": "eng",
    "metadata": {
      "project": "Q4-reports"
    }
  }
}
```

Features:
- Automatic format detection
- OCR configuration for images
- Custom metadata support
- Processing statistics

### 3. Format Detection Tool

Check if a file format is supported:

```json
{
  "tool": "detect_format",
  "parameters": {
    "file_path": "/path/to/file.xyz"
  }
}
```

Response includes:
- Support status
- Reader information
- Similar supported formats

### 4. List Formats Tool

Get all supported file formats:

```json
{
  "tool": "list_formats"
}
```

Returns categorized format list with reader mappings.

## New Resources

### 1. Enhanced Server Status

`GET /resources/server/status`

```json
{
  "status": "running",
  "version": "2.0.0",
  "features": {
    "formats_supported": 39,
    "ocr_available": true,
    "archive_extraction": true
  },
  "processing_stats": {
    "total_processed": 1234,
    "by_format": {
      "pdf": 500,
      "docx": 300,
      "xlsx": 200
    }
  }
}
```

### 2. Format Statistics

`GET /resources/formats/stats`

```json
{
  "total_documents": 5000,
  "total_size_mb": 12500.5,
  "format_distribution": {
    "pdf": 2000,
    "docx": 1500,
    "xlsx": 800
  }
}
```

### 3. Reader Capabilities

`GET /resources/readers/capabilities`

```json
{
  "readers": {
    ".pdf": {
      "reader": "PDFReader",
      "category": "documents",
      "can_extract_tables": true
    },
    ".xlsx": {
      "reader": "ExcelReader",
      "category": "spreadsheets",
      "supports_streaming": true
    }
  },
  "ocr_languages": ["eng", "fra", "deu", "spa"]
}
```

## Migration Steps

### 1. Update Server Implementation

Replace the existing server with the enhanced version:

```python
# Before
from vector_db_query.mcp_integration.server import VectorQueryMCPServer

# After
from vector_db_query.mcp_integration.server_enhanced import EnhancedVectorQueryMCPServer
```

### 2. Update Configuration

Add format-specific settings to your MCP configuration:

```yaml
mcp:
  server:
    name: "vector-db-query-enhanced"
    version: "2.0.0"
  
  features:
    format_filtering: true
    ocr_processing: true
    archive_extraction: true
  
  processing:
    max_file_size_mb: 100
    ocr_languages: ["eng", "fra", "deu"]
    parallel_processing: true
```

### 3. Update Claude Configuration

Update your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "vector-db-query": {
      "command": "python",
      "args": [
        "-m",
        "vector_db_query.mcp_integration.server_enhanced"
      ],
      "env": {
        "PYTHONPATH": "/path/to/vector-db-query/src"
      }
    }
  }
}
```

### 4. Update Client Integration

If you have custom MCP clients, update them to use new features:

```python
# Example: Search with format filtering
response = await mcp_client.call_tool(
    "query_vectors",
    query="financial reports",
    file_types=["xlsx", "csv"],
    limit=50
)

# Example: Process various formats
for file_path in document_paths:
    # Check format first
    format_check = await mcp_client.call_tool(
        "detect_format",
        file_path=file_path
    )
    
    if format_check["data"]["supported"]:
        # Process the document
        result = await mcp_client.call_tool(
            "process_document",
            file_path=file_path,
            ocr_enabled=format_check["data"].get("has_ocr", False)
        )
```

## Backward Compatibility

The enhanced server maintains backward compatibility:

1. **Existing Tools**: All original tools (`query_vectors`, `search_similar`, `get_context`) work as before
2. **Optional Parameters**: New parameters (like `file_types`) are optional
3. **Response Format**: Core response structure unchanged, new fields are additions

## Performance Considerations

### 1. Format-Specific Optimizations

Different formats have different processing costs:

```python
# Configure workers based on format
if file_extension in ['.pdf', '.docx']:
    max_workers = 4  # CPU-intensive
elif file_extension in ['.png', '.jpg']:
    max_workers = 2  # Very CPU-intensive (OCR)
else:
    max_workers = 8  # Light processing
```

### 2. Caching Strategy

The enhanced server includes format-aware caching:

- Document metadata cached by format
- OCR results cached separately
- Format detection results cached

### 3. Resource Limits

Set appropriate limits for different formats:

```yaml
processing_limits:
  pdf:
    max_size_mb: 100
    timeout_seconds: 300
  images:
    max_size_mb: 50
    ocr_timeout_seconds: 120
  archives:
    max_size_mb: 500
    max_files: 1000
```

## Monitoring

### 1. Format-Specific Metrics

Monitor processing by format:

```python
# Log format-specific metrics
logger.info(f"Processed {file_type}: {processing_time}s")

# Track errors by format
if error:
    metrics.increment(f"processing_errors.{file_type}")
```

### 2. Performance Tracking

Track performance by format category:

```json
{
  "processing_times": {
    "documents": {"avg": 2.5, "p95": 5.0},
    "spreadsheets": {"avg": 1.8, "p95": 4.0},
    "images": {"avg": 8.2, "p95": 15.0}
  }
}
```

## Troubleshooting

### Common Issues

1. **OCR Not Working**
   ```bash
   # Check Tesseract installation
   tesseract --version
   
   # Install language data
   sudo apt-get install tesseract-ocr-fra
   ```

2. **Format Not Recognized**
   ```python
   # Check supported formats
   response = await mcp_client.call_tool("list_formats")
   print(response["data"]["formats"])
   ```

3. **Slow Processing**
   - Check file size limits
   - Verify OCR settings
   - Monitor resource usage

### Debug Mode

Enable detailed logging:

```bash
python -m vector_db_query.mcp_integration.server_enhanced \
  --log-level DEBUG \
  --config config.yaml
```

## Best Practices

1. **Format Filtering**: Use `file_types` parameter to improve search relevance
2. **OCR Configuration**: Only enable OCR when needed to save resources
3. **Batch Processing**: Process similar formats together for efficiency
4. **Error Handling**: Check format support before processing
5. **Monitoring**: Track format distribution to optimize resources

## Future Enhancements

Planned improvements:

1. **Format Conversion**: Convert between compatible formats
2. **Preview Generation**: Generate previews for all formats
3. **Format-Specific Search**: Search within specific document structures
4. **Smart OCR**: Automatic language detection for OCR
5. **Format Recommendations**: Suggest best format for content type