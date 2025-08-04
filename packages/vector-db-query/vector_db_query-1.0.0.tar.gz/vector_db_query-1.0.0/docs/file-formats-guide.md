# File Formats Guide

This guide provides detailed information about all supported file formats in Vector DB Query, including format-specific features, configuration options, and best practices.

## Table of Contents

1. [Document Formats](#document-formats)
2. [Spreadsheet Formats](#spreadsheet-formats)
3. [Presentation Formats](#presentation-formats)
4. [Email Formats](#email-formats)
5. [Web & Markup Formats](#web--markup-formats)
6. [Configuration & Data Formats](#configuration--data-formats)
7. [Image Formats (OCR)](#image-formats-ocr)
8. [Archive Formats](#archive-formats)
9. [Log Formats](#log-formats)
10. [Format Detection](#format-detection)
11. [Custom Format Support](#custom-format-support)

## Document Formats

### PDF (.pdf)

**Features:**
- Full text extraction with layout preservation
- Metadata extraction (title, author, creation date)
- Multi-page support
- Embedded image handling

**Configuration:**
```yaml
document_processing:
  pdf:
    extract_images: false  # Future feature
    preserve_layout: true
```

**Best Practices:**
- Ensure PDFs are text-based, not scanned images
- For scanned PDFs, enable OCR processing
- Large PDFs may benefit from increased chunk sizes

### Microsoft Word (.doc, .docx)

**Features:**
- Text extraction from paragraphs and tables
- Header and footer content
- Comments and tracked changes
- Document properties and metadata

**Configuration:**
```yaml
document_processing:
  word:
    extract_comments: true
    include_headers_footers: true
    extract_tables: true
```

**Best Practices:**
- DOCX format provides better extraction than legacy DOC
- Complex formatting may require post-processing
- Tables are converted to structured text

### Plain Text (.txt, .text, .md, .markdown)

**Features:**
- Automatic encoding detection (UTF-8, ISO-8859-1, etc.)
- Markdown structure preservation
- Line ending normalization

**Configuration:**
```yaml
document_processing:
  text:
    encoding: "auto"  # or specific encoding
    preserve_markdown: true
```

**Best Practices:**
- Use UTF-8 encoding when possible
- Markdown files maintain their structure
- Large text files process quickly

## Spreadsheet Formats

### Microsoft Excel (.xlsx, .xls)

**Features:**
- Cell value extraction
- Formula extraction (optional)
- Comments and notes
- Multiple sheet processing
- Named ranges support

**Configuration:**
```yaml
document_processing:
  format_settings:
    excel:
      extract_formulas: true
      extract_comments: true
      process_all_sheets: true
      max_rows_per_sheet: 10000
      include_empty_cells: false
```

**Usage Example:**
```bash
# Process Excel files with formula extraction
vector-db-query process /path/to/spreadsheets --formats xlsx,xls

# Configure via CLI
vector-db-query config set document_processing.format_settings.excel.extract_formulas true
```

**Best Practices:**
- Large spreadsheets may need row limits
- Formula extraction increases processing time
- Empty cells are skipped by default

### CSV (.csv, .tsv)

**Features:**
- Automatic delimiter detection
- Header row recognition
- Encoding detection
- Large file streaming

**Configuration:**
```yaml
document_processing:
  csv:
    has_header: true
    delimiter: "auto"  # or specific: ",", "\t", "|"
    encoding: "utf-8"
```

**Best Practices:**
- Ensure consistent delimiters
- First row assumed as headers
- Tab-separated values use .tsv extension

## Presentation Formats

### Microsoft PowerPoint (.pptx, .ppt)

**Features:**
- Slide content extraction
- Speaker notes capture
- Slide titles and numbers
- Table data extraction
- Shape and text box content

**Configuration:**
```yaml
document_processing:
  format_settings:
    powerpoint:
      extract_speaker_notes: true
      extract_slide_numbers: true
      include_master_slides: false
      extract_shapes: true
```

**Usage Example:**
```bash
# Process presentations with speaker notes
export VECTOR_DB_POWERPOINT_EXTRACT_NOTES=true
vector-db-query process /path/to/presentations
```

**Best Practices:**
- Speaker notes often contain valuable context
- Master slides typically excluded
- Complex animations not extracted

## Email Formats

### Email Messages (.eml)

**Features:**
- Full header extraction (From, To, CC, Subject, Date)
- Body content (plain text and HTML)
- Attachment detection and recursive processing
- Thread identification
- MIME type handling

**Configuration:**
```yaml
document_processing:
  format_settings:
    email:
      extract_attachments: true
      thread_detection: true
      sanitize_content: true
      include_headers: true
      process_html_body: true
```

**Usage Example:**
```bash
# Process emails with attachments
vector-db-query process /path/to/emails --recursive

# Disable attachment extraction for faster processing
export VECTOR_DB_EMAIL_EXTRACT_ATTACHMENTS=false
```

**Best Practices:**
- Enable attachment processing for complete extraction
- Thread detection helps maintain context
- HTML sanitization removes potentially harmful content

### Mailbox (.mbox)

**Features:**
- Multi-message archive support
- Individual message extraction
- Maintains folder structure
- Batch processing

**Best Practices:**
- Large MBOX files process message by message
- Consider splitting very large archives
- Preserves message relationships

## Web & Markup Formats

### HTML (.html, .htm, .xhtml)

**Features:**
- Script and style removal
- Text extraction with structure
- Link preservation
- Optional markdown conversion
- Encoding detection

**Configuration:**
```yaml
document_processing:
  format_settings:
    html:
      remove_scripts: true
      remove_styles: true
      convert_to_markdown: false
      preserve_links: true
      extract_metadata: true
```

**Usage Example:**
```bash
# Convert HTML to markdown during processing
export VECTOR_DB_HTML_CONVERT_MARKDOWN=true
vector-db-query process /path/to/html/files
```

**Best Practices:**
- Remove scripts for cleaner text
- Markdown conversion aids readability
- Preserve links for context

### XML (.xml)

**Features:**
- Structure preservation
- Namespace handling
- Attribute extraction
- XPath support (future)

**Configuration:**
```yaml
document_processing:
  xml:
    preserve_structure: true
    extract_attributes: true
    pretty_print: true
```

**Best Practices:**
- Well-formed XML processes best
- Large XML files may need streaming
- Structure helps maintain context

## Configuration & Data Formats

### JSON (.json)

**Features:**
- Pretty-printed extraction
- Nested structure handling
- Array processing
- Schema validation (optional)

**Configuration:**
```yaml
document_processing:
  format_settings:
    config_files:
      preserve_structure: true
      include_comments: true
      validate_syntax: true
```

**Best Practices:**
- Valid JSON required
- Large files automatically streamed
- Nested structures flattened for indexing

### YAML (.yaml, .yml)

**Features:**
- Multi-document support
- Comment preservation
- Reference resolution
- Structure maintenance

**Usage Example:**
```bash
# Process configuration files
vector-db-query process /path/to/configs --formats yaml,json,ini
```

### INI/Config (.ini, .cfg, .conf)

**Features:**
- Section-based extraction
- Comment handling
- Key-value parsing
- Multi-line value support

**Best Practices:**
- Standard INI format works best
- Sections provide natural chunking
- Comments can provide context

### Log Files (.log)

**Features:**
- Pattern recognition
- Summary generation
- Error extraction
- Timestamp parsing
- Configurable line limits

**Configuration:**
```yaml
document_processing:
  format_settings:
    logs:
      summarize: true
      extract_patterns: true
      max_lines: 10000
      patterns:
        - "ERROR"
        - "WARNING"
        - "Exception"
```

**Usage Example:**
```bash
# Process log files with summarization
export VECTOR_DB_LOG_SUMMARIZE=true
export VECTOR_DB_LOG_MAX_LINES=5000
vector-db-query process /var/log/application/
```

**Best Practices:**
- Set appropriate line limits for large logs
- Pattern extraction helps identify issues
- Summarization reduces noise

## Image Formats (OCR)

### Supported Formats

- **PNG** (.png) - Lossless compression
- **JPEG** (.jpg, .jpeg) - Lossy compression
- **TIFF** (.tiff, .tif) - Multi-page support
- **BMP** (.bmp) - Uncompressed
- **GIF** (.gif) - Limited color palette

### OCR Configuration

**Requirements:**
```bash
# Install Tesseract
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Ubuntu/Debian

# Install language packs
sudo apt-get install tesseract-ocr-fra  # French
sudo apt-get install tesseract-ocr-deu  # German
```

**Configuration:**
```yaml
document_processing:
  format_settings:
    ocr:
      enabled: true
      language: "eng"  # or "eng+fra+deu" for multiple
      confidence_threshold: 60.0
      preprocess_image: true
      dpi: 300
```

**Usage Example:**
```bash
# Enable OCR for image processing
vector-db-query process /path/to/images --ocr --ocr-lang eng+fra

# Check OCR availability
vector-db-query formats --check-ocr
```

**Best Practices:**
- Higher DPI improves accuracy
- Preprocessing enhances results
- Multiple languages slow processing
- Confidence threshold filters poor results

## Archive Formats

### ZIP (.zip)

**Features:**
- Recursive extraction
- Password support (with configuration)
- Maintains folder structure
- Processes contained files

### TAR (.tar, .tar.gz, .tar.bz2, .tar.xz)

**Features:**
- Compression format support
- Preserves permissions
- Handles large archives
- Streaming extraction

**Best Practices:**
- Archives processed recursively
- Large archives may need temp space
- Nested archives supported

## Format Detection

### Automatic Detection

```bash
# Check format support for a file
vector-db-query formats /path/to/unknown.file

# Detect all formats in directory
vector-db-query formats /path/to/directory --recursive
```

### Manual Format Specification

```bash
# Process only specific formats
vector-db-query process /path/to/files --formats pdf,docx,xlsx

# Exclude specific formats
vector-db-query process /path/to/files --exclude-formats log,tmp
```

## Custom Format Support

### Adding Custom Readers

```python
from vector_db_query.document_processor.base import DocumentReader
from pathlib import Path

class CustomReader(DocumentReader):
    def can_read(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.custom'
    
    def read(self, file_path: Path) -> str:
        # Your extraction logic here
        return extracted_text
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.custom']

# Register the reader
from vector_db_query.document_processor import ReaderFactory
factory = ReaderFactory()
factory.register_reader('custom', CustomReader())
```

### Configuration for Custom Formats

```yaml
document_processing:
  custom_formats:
    .custom:
      reader: "custom"
      chunk_size: 1000
      encoding: "utf-8"
```

## Performance Considerations

### Format-Specific Tips

1. **Large Files**
   - Excel: Use row limits
   - Logs: Set max lines
   - Archives: Ensure temp space

2. **Processing Speed**
   - Text files: Fastest
   - PDFs: Moderate
   - Images with OCR: Slowest

3. **Memory Usage**
   - Stream large files
   - Process archives incrementally
   - Limit concurrent workers

### Optimization Strategies

```bash
# Parallel processing for large datasets
vector-db-query process /data --formats pdf,docx --workers 8

# Exclude unnecessary formats
vector-db-query process /data --exclude-formats tmp,bak,cache

# Dry run to estimate processing
vector-db-query process /data --dry-run --stats
```

## Troubleshooting

### Common Issues

1. **Encoding Errors**
   - Set explicit encoding in config
   - Use encoding detection
   - Check file corruption

2. **OCR Failures**
   - Verify Tesseract installation
   - Check language pack availability
   - Adjust confidence threshold

3. **Format Not Recognized**
   - Check file extension
   - Verify format support
   - Try manual format specification

### Debug Commands

```bash
# Verbose output for debugging
vector-db-query process /path/to/file --verbose

# Check specific file support
vector-db-query formats /path/to/file --debug

# Validate configuration
vector-db-query config validate
```

## Best Practices Summary

1. **Pre-Processing**
   - Organize files by type
   - Remove unnecessary files
   - Check file integrity

2. **Configuration**
   - Set appropriate limits
   - Enable needed features
   - Disable unused extractors

3. **Performance**
   - Use parallel processing
   - Monitor memory usage
   - Process in batches

4. **Quality**
   - Verify extraction results
   - Adjust OCR settings
   - Review chunking strategy

---

For more information, see the [main documentation](../README.md) or run `vector-db-query --help`.