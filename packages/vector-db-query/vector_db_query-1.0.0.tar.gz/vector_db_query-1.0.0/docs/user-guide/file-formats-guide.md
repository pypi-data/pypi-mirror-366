# File Formats Guide

This guide covers all supported file formats and how to work with them effectively.

## Overview

Vector DB Query supports 39+ file formats across multiple categories. Each format has specialized readers that extract text while preserving structure and metadata.

## Supported Formats by Category

### 📄 Documents

#### PDF Files (`.pdf`)
- Full text extraction with layout preservation
- Table detection and extraction
- Metadata extraction (author, title, creation date)
- Embedded image handling
- Password-protected PDF support (with password)

```bash
# Process PDF files
vector-db-query process /path/to/pdfs --extensions .pdf

# With password
VECTOR_DB_PDF_PASSWORD=secret vector-db-query process secured.pdf
```

#### Microsoft Word (`.doc`, `.docx`)
- Text extraction with formatting awareness
- Table preservation
- Header/footer extraction
- Track changes and comments handling
- Embedded object detection

```bash
# Process Word documents
vector-db-query process /path/to/docs --extensions .doc .docx
```

#### Text Files (`.txt`, `.md`, `.markdown`)
- UTF-8, UTF-16, and other encodings
- Markdown structure preservation
- Code block detection in Markdown
- Line ending normalization

```bash
# Process text files with specific encoding
vector-db-query process /path/to/texts --encoding utf-16
```

### 📊 Spreadsheets

#### Excel Files (`.xlsx`, `.xls`)
- Multi-sheet processing
- Table structure preservation
- Formula results extraction
- Cell formatting awareness
- Named range support

```bash
# Process Excel files
vector-db-query process /path/to/spreadsheets --extensions .xlsx .xls

# Extract tables for structured data
vector-db-query process data.xlsx --extract-tables
```

#### CSV Files (`.csv`)
- Automatic delimiter detection
- Header row identification
- Large file streaming support
- Encoding detection

```bash
# Process CSV files
vector-db-query process /path/to/data --extensions .csv
```

### 🎯 Presentations

#### PowerPoint Files (`.pptx`, `.ppt`)
- Slide text extraction
- Speaker notes inclusion
- Slide layout preservation
- Embedded media detection

```bash
# Process presentations
vector-db-query process /path/to/presentations --extensions .pptx .ppt
```

### 📧 Email

#### Email Files (`.eml`, `.mbox`)
- Header extraction (From, To, Subject, Date)
- Body text extraction (plain and HTML)
- Attachment listing
- Thread reconstruction for mbox

```bash
# Process email archives
vector-db-query process /path/to/emails --extensions .eml .mbox
```

### 🌐 Web & Markup

#### HTML Files (`.html`, `.htm`, `.xhtml`)
- Clean text extraction
- Structure preservation
- Metadata extraction (title, description, keywords)
- JavaScript content removal
- CSS styling removal

```bash
# Process web files
vector-db-query process /path/to/web --extensions .html .htm
```

#### XML Files (`.xml`)
- Structure-aware extraction
- Attribute preservation
- Namespace handling
- XPath-based filtering (optional)

```bash
# Process XML files
vector-db-query process /path/to/xml --extensions .xml
```

### ⚙️ Configuration Files

#### JSON Files (`.json`)
- Pretty-printed extraction
- Nested structure handling
- Large file streaming
- JSON Lines support (`.jsonl`)

```bash
# Process JSON files
vector-db-query process /path/to/configs --extensions .json .jsonl
```

#### YAML Files (`.yaml`, `.yml`)
- Multi-document support
- Anchor/alias resolution
- Comment preservation option

```bash
# Process YAML files
vector-db-query process /path/to/configs --extensions .yaml .yml
```

#### INI/Config Files (`.ini`, `.cfg`, `.conf`, `.config`)
- Section-based extraction
- Comment handling
- Variable interpolation

```bash
# Process config files
vector-db-query process /path/to/configs --extensions .ini .cfg .conf
```

### 🖼️ Images (OCR)

#### Supported Image Formats
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- GIF (`.gif`)
- BMP (`.bmp`)
- TIFF (`.tiff`, `.tif`) - including multi-page
- WebP (`.webp`)

#### OCR Configuration

```bash
# Basic OCR processing
vector-db-query process /path/to/images --extensions .png .jpg

# With specific language
vector-db-query process /path/to/images --ocr-lang fra

# Multiple languages
vector-db-query process /path/to/images --ocr-lang eng+fra+deu

# With confidence threshold
vector-db-query process /path/to/images --ocr-confidence 80

# Disable OCR
vector-db-query process /path/to/images --no-ocr
```

#### OCR Best Practices
1. **Image Quality**: Higher resolution images (300 DPI+) yield better results
2. **Preprocessing**: The system automatically enhances contrast and converts to black/white
3. **Language Data**: Install appropriate Tesseract language packs
4. **Confidence**: Adjust threshold based on your quality requirements

### 📦 Archives

#### ZIP Files (`.zip`)
- Automatic extraction and processing
- Nested archive support
- Password-protected ZIP support
- Maintains folder structure in metadata

```bash
# Process ZIP archives
vector-db-query process /path/to/archives --extensions .zip

# With password
VECTOR_DB_ZIP_PASSWORD=secret vector-db-query process encrypted.zip
```

#### TAR Files (`.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz`)
- Compressed archive support
- Stream processing for large files
- Preserves file permissions in metadata

```bash
# Process TAR archives
vector-db-query process /path/to/archives --extensions .tar .tar.gz
```

### 📋 Log Files

#### Log Files (`.log`)
- Automatic log level detection
- Timestamp extraction
- Error/warning highlighting
- Log format pattern matching

```bash
# Process log files
vector-db-query process /path/to/logs --extensions .log

# Search for errors
vector-db-query query "ERROR" --filter file_type=log
```

## Format Detection

Use the format detection command to check file support:

```bash
# Check single file
vector-db-query detect-format /path/to/file.xyz

# Check directory
vector-db-query detect-format /path/to/directory --detailed

# Output:
# File: document.xyz
# Extension: .xyz
# Status: ✗ Not Supported
# Reason: No reader available for file type: .xyz
# Similar supported formats: .xml, .xls
```

## Custom Formats

Add support for custom file extensions:

```bash
# Add custom extension
vector-db-query config add-format .custom

# Verify it's added
vector-db-query config formats
```

Custom formats will be processed as text files by default.

## Processing Options

### Filtering by Format

```bash
# Process only specific formats
vector-db-query process /path --extensions .pdf .docx .xlsx

# Exclude specific formats
vector-db-query process /path --exclude .log .tmp

# Combine include and exclude
vector-db-query process /path --extensions .pdf .doc --exclude .encrypted.pdf
```

### Format-Specific Settings

Configure format-specific options in `config.yaml`:

```yaml
document_processing:
  format_options:
    pdf:
      extract_images: false
      extract_tables: true
      password: null
    
    excel:
      include_formulas: false
      include_hidden_sheets: false
    
    html:
      remove_scripts: true
      extract_metadata: true
    
    images:
      ocr_enabled: true
      resize_large_images: true
      max_dimension: 4000
```

### Performance Considerations

Different formats have different processing costs:

| Format | Speed | Memory Usage | CPU Usage |
|--------|-------|--------------|-----------|
| TXT/MD | Fast | Low | Low |
| JSON/XML | Fast | Medium | Low |
| HTML | Medium | Low | Medium |
| PDF | Slow | High | High |
| DOCX/XLSX | Medium | Medium | Medium |
| Images (OCR) | Very Slow | High | Very High |

### Batch Processing Tips

1. **Group by Format**: Process similar formats together
   ```bash
   # Process documents first
   vector-db-query process /path --extensions .pdf .docx
   
   # Then process images separately with different settings
   vector-db-query process /path --extensions .png .jpg --ocr-confidence 90
   ```

2. **Use Parallel Processing**: Configure workers based on format
   ```bash
   # More workers for simple formats
   vector-db-query config set document_processing.max_workers 8
   vector-db-query process /path --extensions .txt .md .json
   
   # Fewer workers for heavy formats
   vector-db-query config set document_processing.max_workers 2
   vector-db-query process /path --extensions .pdf --ocr-enabled
   ```

3. **Memory Management**: Set limits for large files
   ```bash
   # Configure memory limit
   vector-db-query config set document_processing.memory_limit_mb 2048
   vector-db-query config set document_processing.max_file_size_mb 500
   ```

## Troubleshooting

### Common Issues

1. **Unsupported Format Error**
   ```
   Error: No reader available for file type: .xyz
   ```
   Solution: Check supported formats with `vector-db-query process --formats`

2. **OCR Not Working**
   ```
   Warning: OCR not available - install pytesseract and Tesseract
   ```
   Solution: Install Tesseract and Python bindings:
   ```bash
   # macOS
   brew install tesseract
   pip install pytesseract
   
   # Ubuntu
   sudo apt-get install tesseract-ocr
   pip install pytesseract
   ```

3. **Memory Errors with Large Files**
   ```
   Error: Memory limit exceeded
   ```
   Solution: Increase memory limit or process in smaller batches:
   ```bash
   vector-db-query config set document_processing.memory_limit_mb 4096
   ```

4. **Encoding Errors**
   ```
   Error: UnicodeDecodeError
   ```
   Solution: Specify correct encoding:
   ```bash
   vector-db-query process file.txt --encoding iso-8859-1
   ```

### Format-Specific Issues

#### PDF Issues
- **Scanned PDFs**: Enable OCR for scanned documents
- **Corrupted PDFs**: Try PDF repair tools before processing
- **Complex Layouts**: May need manual review for tables

#### Excel Issues
- **Large Files**: Enable streaming mode for files >100MB
- **Complex Formulas**: Results extracted, not formulas
- **Pivot Tables**: Extracted as regular tables

#### Image Issues
- **Low Quality**: Increase DPI or use image enhancement
- **Wrong Language**: Specify correct OCR language
- **Skewed Text**: Preprocessing handles minor skewing

## Best Practices

1. **Know Your Data**
   - Identify predominant file formats
   - Configure appropriate settings
   - Plan processing strategy

2. **Test First**
   - Use `--dry-run` to preview
   - Process small sample first
   - Verify extraction quality

3. **Monitor Resources**
   - Watch memory usage for large files
   - Monitor disk space for archives
   - Check CPU for OCR workloads

4. **Optimize Settings**
   - Adjust chunk size for your content
   - Configure parallel workers
   - Set appropriate timeouts

5. **Regular Maintenance**
   - Update OCR language data
   - Clean temporary files
   - Review error logs