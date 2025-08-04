# Enhanced CLI Features

## TASK-016: Update CLI Commands - Completed

### Overview
Enhanced the CLI commands to support the new file formats and provide better user experience.

### New Features Added

#### 1. Enhanced Process Command (`process`)
- **`--formats`** flag: Shows all supported file formats in a tree view
- **`--extensions`** option: Filter files by specific extensions (e.g., `-e .pdf -e .docx`)
- **`--exclude`** option: Exclude specific file extensions
- **`--ocr-lang`** option: Set OCR language for image processing (default: eng)
- **`--ocr-confidence`** option: Set minimum OCR confidence threshold (0-100)
- **`--no-ocr`** flag: Disable OCR processing for images
- **`--stats`** flag: Show detailed processing statistics with format breakdown
- Enhanced progress reporting with format-specific information

#### 2. New Format Detection Command (`detect-format`)
- Detect if a file or directory contains supported formats
- Shows which reader would be used for each file
- `--detailed` flag for additional format information
- Useful for troubleshooting unsupported files

### Supported File Formats (39 total)

#### Documents
- PDF: `.pdf`
- Word: `.doc`, `.docx`
- Text: `.txt`
- Markdown: `.md`, `.markdown`

#### Spreadsheets
- Excel: `.xlsx`, `.xls`
- CSV: `.csv`

#### Presentations
- PowerPoint: `.pptx`, `.ppt`

#### Email
- Email: `.eml`
- Mailbox: `.mbox`

#### Web
- HTML: `.html`, `.htm`, `.xhtml`

#### Configuration
- JSON: `.json`
- XML: `.xml`
- YAML: `.yaml`, `.yml`
- INI: `.ini`, `.cfg`, `.conf`, `.config`

#### Images (with OCR)
- Common: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`
- TIFF: `.tiff`, `.tif` (multi-page support)
- WebP: `.webp`

#### Logs
- Log files: `.log` (with level analysis)

#### Data
- GeoJSON: `.geojson`
- JSON Lines: `.jsonl`

#### Archives
- ZIP: `.zip`
- TAR: `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz`

### Usage Examples

```bash
# Show all supported formats
vector-db-query process --formats

# Process only specific formats
vector-db-query process --folder /path/to/docs --extensions .pdf --extensions .docx

# Exclude certain formats
vector-db-query process --folder /path/to/docs --exclude .log --exclude .tmp

# Process with custom OCR settings
vector-db-query process --folder /path/to/images --ocr-lang eng+fra --ocr-confidence 70

# Detect format support for a file
vector-db-query detect-format /path/to/file.xyz --detailed

# Process with detailed statistics
vector-db-query process --folder /path/to/docs --stats --verbose
```

### Implementation Details

1. Created `process_enhanced.py` with all new features
2. Updated `ReaderFactory` to support 39 file extensions
3. Integrated OCR status checking and configuration
4. Added format filtering at the CLI level
5. Enhanced progress reporting with format breakdown
6. Made imports graceful to handle optional dependencies

### Next Steps
- Update configuration system (TASK-017)
- Update documentation (TASK-018)
- Add integration tests for new features
- Consider adding batch OCR processing optimization