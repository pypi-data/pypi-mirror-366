"""Base classes for Microsoft Office document readers."""

from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional

from vector_db_query.document_processor.base import DocumentReader
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class OfficeDocumentReader(DocumentReader):
    """Base class for Microsoft Office document readers."""
    
    def __init__(self):
        """Initialize the Office document reader."""
        super().__init__()
        self._metadata: Dict[str, Any] = {}
        
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get document metadata extracted during reading."""
        return self._metadata
        
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract common metadata from Office documents.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'file_type': file_path.suffix.lower(),
        }
        return metadata
        
    @abstractmethod
    def _process_content(self, content: Any) -> str:
        """Process the raw content into text.
        
        Args:
            content: Raw content from the document
            
        Returns:
            Processed text content
        """
        pass


class SpreadsheetReader(OfficeDocumentReader):
    """Base class for spreadsheet readers (Excel, CSV)."""
    
    def __init__(self, 
                 include_formulas: bool = True,
                 include_comments: bool = True,
                 sheet_separator: str = "\n---\n"):
        """Initialize spreadsheet reader.
        
        Args:
            include_formulas: Whether to include formula definitions
            include_comments: Whether to include cell comments
            sheet_separator: Text to insert between sheets
        """
        super().__init__()
        self.include_formulas = include_formulas
        self.include_comments = include_comments
        self.sheet_separator = sheet_separator
        
    def _format_table_data(self, rows: list) -> str:
        """Format tabular data into readable text.
        
        Args:
            rows: List of row data
            
        Returns:
            Formatted text representation
        """
        if not rows:
            return ""
            
        # Simple text representation
        text_parts = []
        for row in rows:
            if any(cell for cell in row if cell):
                row_text = " | ".join(str(cell) if cell else "" for cell in row)
                text_parts.append(row_text)
                
        return "\n".join(text_parts)


class PresentationReader(OfficeDocumentReader):
    """Base class for presentation readers (PowerPoint)."""
    
    def __init__(self,
                 include_notes: bool = True,
                 include_comments: bool = True,
                 slide_separator: str = "\n===\n"):
        """Initialize presentation reader.
        
        Args:
            include_notes: Whether to include speaker notes
            include_comments: Whether to include comments
            slide_separator: Text to insert between slides
        """
        super().__init__()
        self.include_notes = include_notes
        self.include_comments = include_comments
        self.slide_separator = slide_separator
        
    def _format_slide(self, slide_num: int, title: str, content: str, 
                     notes: Optional[str] = None) -> str:
        """Format a single slide into text.
        
        Args:
            slide_num: Slide number
            title: Slide title
            content: Slide content
            notes: Speaker notes (optional)
            
        Returns:
            Formatted slide text
        """
        parts = [f"Slide {slide_num}"]
        
        if title:
            parts.append(f"Title: {title}")
            
        if content:
            parts.append(f"Content:\n{content}")
            
        if notes and self.include_notes:
            parts.append(f"Notes:\n{notes}")
            
        return "\n".join(parts)