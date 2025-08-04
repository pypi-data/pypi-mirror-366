"""Base classes for web content readers."""

from abc import abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import re

from vector_db_query.document_processor.base import DocumentReader
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class WebDocumentReader(DocumentReader):
    """Base class for web content readers (HTML, XML)."""
    
    def __init__(self, 
                 remove_scripts: bool = True,
                 remove_styles: bool = True,
                 preserve_structure: bool = True):
        """Initialize web document reader.
        
        Args:
            remove_scripts: Whether to remove script tags
            remove_styles: Whether to remove style tags
            preserve_structure: Whether to preserve document structure
        """
        super().__init__()
        self.remove_scripts = remove_scripts
        self.remove_styles = remove_styles
        self.preserve_structure = preserve_structure
        
    def _clean_whitespace(self, text: str) -> str:
        """Clean excessive whitespace while preserving structure.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove trailing whitespace
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove leading/trailing whitespace
        return text.strip()
        
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from web content.
        
        Args:
            content: Raw web content
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
            
        # Extract meta tags
        meta_pattern = r'<meta\s+(?:name|property)=["\']([^"\']+)["\']\s+content=["\']([^"\']+)["\']'
        for match in re.finditer(meta_pattern, content, re.IGNORECASE):
            key = match.group(1).lower().replace(':', '_')
            metadata[f'meta_{key}'] = match.group(2)
            
        return metadata
        
    @abstractmethod
    def _parse_content(self, content: str) -> str:
        """Parse web content into text.
        
        Args:
            content: Raw web content
            
        Returns:
            Parsed text content
        """
        pass


class EmailDocumentReader(DocumentReader):
    """Base class for email readers."""
    
    def __init__(self,
                 process_attachments: bool = True,
                 detect_threads: bool = True,
                 headers_to_include: Optional[list] = None):
        """Initialize email reader.
        
        Args:
            process_attachments: Whether to process attachments
            detect_threads: Whether to detect email threads
            headers_to_include: List of headers to include
        """
        super().__init__()
        self.process_attachments = process_attachments
        self.detect_threads = detect_threads
        self.headers_to_include = headers_to_include or [
            'from', 'to', 'cc', 'subject', 'date'
        ]
        
    def _format_email_header(self, headers: Dict[str, str]) -> str:
        """Format email headers into readable text.
        
        Args:
            headers: Dictionary of email headers
            
        Returns:
            Formatted header text
        """
        parts = []
        for key in self.headers_to_include:
            if key in headers and headers[key]:
                formatted_key = key.title()
                parts.append(f"{formatted_key}: {headers[key]}")
                
        return "\n".join(parts)
        
    def _sanitize_email_content(self, content: str) -> str:
        """Sanitize email content for security.
        
        Args:
            content: Raw email content
            
        Returns:
            Sanitized content
        """
        # Remove potential script injections
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove potentially dangerous URLs
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        
        return content
        
    @abstractmethod
    def _parse_email(self, email_data: Any) -> Dict[str, Any]:
        """Parse email data into structured format.
        
        Args:
            email_data: Raw email data
            
        Returns:
            Dictionary with headers and body
        """
        pass