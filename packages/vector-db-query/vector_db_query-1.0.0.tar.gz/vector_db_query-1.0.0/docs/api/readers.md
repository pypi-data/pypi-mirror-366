# Document Readers API

This document describes the API for all document readers in the Vector DB Query system.

## Base Classes

### DocumentReader

The abstract base class for all document readers.

```python
from vector_db_query.document_processor.base import DocumentReader
from pathlib import Path
from typing import List

class DocumentReader(ABC):
    """Abstract base class for document readers."""
    
    @abstractmethod
    def can_read(self, file_path: Path) -> bool:
        """Check if this reader can handle the file type."""
        pass
    
    @abstractmethod
    def read(self, file_path: Path) -> str:
        """Read and extract text from the file."""
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        pass
```

## Document Readers

### TextReader

Reads plain text and markdown files with encoding detection.

```python
from vector_db_query.document_processor.reader import TextReader

reader = TextReader()
text = reader.read(Path("document.txt"))
```

**Supported Extensions:** `.txt`, `.md`, `.text`, `.markdown`

### PDFReader

Extracts text from PDF documents.

```python
from vector_db_query.document_processor.reader import PDFReader

reader = PDFReader()
text = reader.read(Path("document.pdf"))
```

**Supported Extensions:** `.pdf`

### DocxReader

Reads Microsoft Word documents.

```python
from vector_db_query.document_processor.reader import DocxReader

reader = DocxReader()
text = reader.read(Path("document.docx"))
```

**Supported Extensions:** `.docx`, `.doc`

## Spreadsheet Readers

### ExcelReader

Extracts data from Excel spreadsheets with advanced features.

```python
from vector_db_query.document_processor.excel_reader import ExcelReader

reader = ExcelReader()
text = reader.read(Path("spreadsheet.xlsx"))

# Configuration
reader.extract_formulas = True
reader.extract_comments = True
reader.process_all_sheets = True
reader.max_rows_per_sheet = 10000
```

**Supported Extensions:** `.xlsx`, `.xls`, `.csv`

**Features:**
- Cell values and formulas
- Comments extraction
- Multi-sheet support
- CSV handling

## Presentation Readers

### PowerPointReader

Extracts content from PowerPoint presentations.

```python
from vector_db_query.document_processor.powerpoint_reader import PowerPointReader

reader = PowerPointReader()
text = reader.read(Path("presentation.pptx"))

# Configuration
reader.extract_speaker_notes = True
reader.extract_slide_numbers = True
reader.include_master_slides = False
```

**Supported Extensions:** `.pptx`, `.ppt`

**Features:**
- Slide content and titles
- Speaker notes
- Table extraction
- Slide numbering

## Email Readers

### EmailReader

Processes email messages and archives.

```python
from vector_db_query.document_processor.email_reader import EmailReader

reader = EmailReader()
text = reader.read(Path("message.eml"))

# Configuration
reader.extract_attachments = True
reader.thread_detection = True
reader.sanitize_content = True
reader.include_headers = True
```

**Supported Extensions:** `.eml`, `.mbox`

**Features:**
- Header extraction
- Body content (text/HTML)
- Attachment processing
- Thread detection

## Web Content Readers

### HTMLReader

Extracts text from HTML documents.

```python
from vector_db_query.document_processor.html_reader import HTMLReader

reader = HTMLReader()
text = reader.read(Path("page.html"))

# Configuration
reader.remove_scripts = True
reader.remove_styles = True
reader.convert_to_markdown = False
reader.preserve_links = True
```

**Supported Extensions:** `.html`, `.htm`, `.xhtml`

**Features:**
- Script/style removal
- Structure preservation
- Markdown conversion
- Link extraction

## Configuration Readers

### JSONReader

Reads JSON files with pretty printing.

```python
from vector_db_query.document_processor.config_reader import JSONReader

reader = JSONReader()
text = reader.read(Path("config.json"))
```

**Supported Extensions:** `.json`

### XMLReader

Extracts structured data from XML files.

```python
from vector_db_query.document_processor.config_reader import XMLReader

reader = XMLReader()
text = reader.read(Path("data.xml"))
```

**Supported Extensions:** `.xml`

### YAMLReader

Processes YAML configuration files.

```python
from vector_db_query.document_processor.config_reader import YAMLReader

reader = YAMLReader()
text = reader.read(Path("config.yaml"))
```

**Supported Extensions:** `.yaml`, `.yml`

### INIReader

Reads INI-style configuration files.

```python
from vector_db_query.document_processor.config_reader import INIReader

reader = INIReader()
text = reader.read(Path("settings.ini"))
```

**Supported Extensions:** `.ini`, `.cfg`, `.conf`

### LogReader

Processes log files with analysis.

```python
from vector_db_query.document_processor.config_reader import LogReader

reader = LogReader()
text = reader.read(Path("application.log"))

# Configuration
reader.summarize = True
reader.extract_patterns = True
reader.max_lines = 10000
```

**Supported Extensions:** `.log`

**Features:**
- Pattern extraction
- Summary generation
- Line limiting

## Image Readers (OCR)

### ImageOCRReader

Extracts text from images using OCR.

```python
from vector_db_query.document_processor.image_ocr_reader import ImageOCRReader

reader = ImageOCRReader(language="eng", confidence_threshold=60.0)
text = reader.read(Path("document.png"))

# Multi-language support
reader = ImageOCRReader(language="eng+fra+deu")

# Check if OCR is available
from vector_db_query.document_processor.image_ocr_reader import check_ocr_available
if check_ocr_available():
    print("OCR is available")
```

**Supported Extensions:** `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.tif`

**Configuration:**
- `language`: OCR language(s) (default: "eng")
- `confidence_threshold`: Minimum confidence (0-100)
- `preprocess`: Enable preprocessing
- `dpi`: Resolution for processing

## ReaderFactory

The factory class for managing document readers.

```python
from vector_db_query.document_processor.reader import ReaderFactory

# Create factory
factory = ReaderFactory(enable_ocr=True, ocr_language="eng")

# Get reader for a file
reader = factory.get_reader(Path("document.pdf"))

# Read document directly
text = factory.read_document(Path("document.pdf"))

# Get all supported extensions
extensions = factory.supported_extensions

# Register custom reader
from my_readers import CustomReader
factory.register_reader("custom", CustomReader())
```

## Advanced Usage

### Custom Reader Implementation

```python
from vector_db_query.document_processor.base import DocumentReader
from pathlib import Path
from typing import List

class CustomFormatReader(DocumentReader):
    """Reader for custom file format."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def can_read(self, file_path: Path) -> bool:
        """Check if file has custom extension."""
        return file_path.suffix.lower() == '.custom'
    
    def read(self, file_path: Path) -> str:
        """Extract text from custom format."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process content based on custom format
            processed = self._process_custom_format(content)
            return processed
            
        except Exception as e:
            raise DocumentReadError(f"Failed to read custom file: {e}")
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.custom']
    
    def _process_custom_format(self, content: str) -> str:
        """Process custom format logic."""
        # Implementation here
        return content
```

### Reader Configuration

```python
# Configure readers globally
from vector_db_query.utils.config import get_config

config = get_config()
config.set("document_processing.format_settings.excel.extract_formulas", True)
config.set("document_processing.format_settings.email.extract_attachments", False)

# Or use environment variables
import os
os.environ["VECTOR_DB_EXCEL_EXTRACT_FORMULAS"] = "true"
os.environ["VECTOR_DB_EMAIL_EXTRACT_ATTACHMENTS"] = "false"
```

### Error Handling

```python
from vector_db_query.document_processor.exceptions import (
    DocumentReadError,
    UnsupportedFileTypeError,
    FileTooLargeError
)

try:
    text = factory.read_document(Path("file.xyz"))
except UnsupportedFileTypeError as e:
    print(f"Unsupported file type: {e}")
except DocumentReadError as e:
    print(f"Error reading document: {e}")
except FileTooLargeError as e:
    print(f"File too large: {e}")
```

### Performance Optimization

```python
# Batch processing with parallel readers
from vector_db_query.document_processor import DocumentProcessor

processor = DocumentProcessor(
    enable_ocr=True,
    ocr_language="eng",
    allowed_formats=["pdf", "docx", "xlsx"]
)

# Process with multiple workers
documents = processor.process_directory(
    Path("/data"),
    recursive=True,
    max_workers=8
)
```

## Testing Readers

```python
import pytest
from pathlib import Path
from vector_db_query.document_processor.reader import ReaderFactory

def test_pdf_reader():
    factory = ReaderFactory()
    text = factory.read_document(Path("test.pdf"))
    assert "expected content" in text

def test_excel_formulas():
    from vector_db_query.document_processor.excel_reader import ExcelReader
    reader = ExcelReader()
    reader.extract_formulas = True
    
    text = reader.read(Path("test.xlsx"))
    assert "=SUM(" in text  # Formula extracted

def test_ocr_availability():
    from vector_db_query.document_processor.image_ocr_reader import check_ocr_available
    if check_ocr_available():
        factory = ReaderFactory(enable_ocr=True)
        text = factory.read_document(Path("image.png"))
        assert len(text) > 0
```

## Best Practices

1. **Error Handling**: Always handle reader exceptions
2. **Configuration**: Set appropriate options for your use case
3. **Performance**: Use batch processing for multiple files
4. **OCR**: Install Tesseract for image support
5. **Memory**: Monitor memory usage for large files
6. **Testing**: Test with various file formats and edge cases

---

For more details, see the [File Formats Guide](../file-formats-guide.md) or the [source code](https://github.com/your-org/vector-db-query).