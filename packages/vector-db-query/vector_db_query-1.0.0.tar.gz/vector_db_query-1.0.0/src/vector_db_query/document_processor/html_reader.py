"""HTML file reader implementation."""

import re
from pathlib import Path
from typing import List, Optional, Dict, Any
import chardet
from bs4 import BeautifulSoup, NavigableString, Comment
import html2text
import warnings

from vector_db_query.document_processor.web_readers import WebDocumentReader
from vector_db_query.document_processor.exceptions import DocumentReadError
from vector_db_query.utils.logger import get_logger

# Suppress BeautifulSoup warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

logger = get_logger(__name__)


class HTMLReader(WebDocumentReader):
    """Reader for HTML files."""
    
    def __init__(self,
                 remove_scripts: bool = True,
                 remove_styles: bool = True,
                 preserve_structure: bool = True,
                 convert_to_markdown: bool = False,
                 ignore_links: bool = False,
                 ignore_images: bool = True,
                 body_width: int = 0):
        """Initialize HTML reader.
        
        Args:
            remove_scripts: Whether to remove script tags
            remove_styles: Whether to remove style tags
            preserve_structure: Whether to preserve document structure
            convert_to_markdown: Whether to convert HTML to markdown
            ignore_links: Whether to ignore links in markdown conversion
            ignore_images: Whether to ignore images in markdown conversion
            body_width: Line width for markdown conversion (0 = no wrapping)
        """
        super().__init__(remove_scripts, remove_styles, preserve_structure)
        self.convert_to_markdown = convert_to_markdown
        self.ignore_links = ignore_links
        self.ignore_images = ignore_images
        self.body_width = body_width
        
        # Initialize html2text converter if needed
        if self.convert_to_markdown:
            self.html_converter = html2text.HTML2Text()
            self.html_converter.ignore_links = ignore_links
            self.html_converter.ignore_images = ignore_images
            self.html_converter.body_width = body_width
            self.html_converter.unicode_snob = True
        
    def can_read(self, file_path: Path) -> bool:
        """Check if this reader can handle the file type."""
        return file_path.suffix.lower() in self.supported_extensions
        
    def read(self, file_path: Path) -> str:
        """Read HTML file and extract text content."""
        # Ensure file_path is a Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        logger.info(f"Reading HTML file: {file_path.name}")
        
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding_info = chardet.detect(raw_data)
                encoding = encoding_info.get('encoding', 'utf-8')
                
            # Read file with detected encoding
            with open(file_path, 'r', encoding=encoding) as f:
                html_content = f.read()
                
            # Extract metadata
            self._metadata = self._extract_metadata(html_content)
            
            # Parse and extract content
            if self.convert_to_markdown:
                return self._convert_to_markdown(html_content)
            else:
                return self._parse_content(html_content)
                
        except Exception as e:
            raise DocumentReadError(
                f"Failed to read HTML file: {e}",
                file_path=str(file_path)
            )
            
    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.html', '.htm', '.xhtml']
        
    def supports_extension(self, extension: str) -> bool:
        """Check if a file extension is supported.
        
        Args:
            extension: File extension (with or without dot)
            
        Returns:
            True if the extension is supported
        """
        if not extension:
            return False
            
        # Normalize extension
        if not extension.startswith('.'):
            extension = f'.{extension}'
            
        return extension.lower() in self.supported_extensions
        
    def _parse_content(self, content: str) -> str:
        """Parse HTML content into text.
        
        Args:
            content: Raw HTML content
            
        Returns:
            Parsed text content
        """
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove unwanted elements
        if self.remove_scripts:
            for script in soup.find_all('script'):
                script.decompose()
                
        if self.remove_styles:
            for style in soup.find_all('style'):
                style.decompose()
                
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
            
        # Extract text with structure preservation
        if self.preserve_structure:
            text_parts = []
            self._extract_structured_text(soup.body or soup, text_parts)
            # Join parts directly - spacing is now preserved in extraction
            text = ''.join(text_parts)
        else:
            # Simple text extraction
            text = soup.get_text(separator='\n', strip=True)
            
        # Clean whitespace
        return self._clean_whitespace(text)
        
    def _extract_structured_text(self, element, text_parts: List[str], depth: int = 0):
        """Extract text while preserving structure.
        
        Args:
            element: BeautifulSoup element
            text_parts: List to accumulate text parts
            depth: Current depth in the DOM tree
        """
        # Skip if element is None
        if element is None:
            return
            
        # Handle text nodes
        if isinstance(element, NavigableString):
            text = str(element)
            if text and not text.isspace():
                # Don't strip whitespace from text nodes to preserve spaces
                text_parts.append(text)
            return
            
        # Handle specific elements
        tag_name = element.name
        
        # Headings
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            text = element.get_text(strip=True)
            if text:
                # Add heading with markdown-style markers
                text_parts.append('\n')
                text_parts.append('#' * level + ' ' + text)
                text_parts.append('\n')
                
        # Paragraphs - process children to preserve inline formatting
        elif tag_name == 'p':
            text_parts.append('\n')
            for child in element.children:
                self._extract_structured_text(child, text_parts, depth + 1)
            text_parts.append('\n')
                
        # Lists
        elif tag_name in ['ul', 'ol']:
            text_parts.append('\n')
            for i, li in enumerate(element.find_all('li', recursive=False)):
                prefix = f"{i+1}. " if tag_name == 'ol' else "- "
                text = li.get_text(strip=True)
                if text:
                    text_parts.append(prefix + text)
                    text_parts.append('\n')
            
        # Tables
        elif tag_name == 'table':
            text_parts.append('\n')
            rows = element.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_text = ' | '.join(cell.get_text(strip=True) for cell in cells)
                    text_parts.append(row_text)
                    text_parts.append('\n')
            
        # Blockquotes
        elif tag_name == 'blockquote':
            text = element.get_text(strip=True)
            if text:
                text_parts.append('\n')
                text_parts.append('> ' + text)
                text_parts.append('\n')
                
        # Code blocks
        elif tag_name == 'pre':
            code = element.get_text(strip=False)
            if code:
                text_parts.append('\n')
                text_parts.append('```')
                text_parts.append('\n')
                text_parts.append(code)
                text_parts.append('\n')
                text_parts.append('```')
                text_parts.append('\n')
                
        # Inline code
        elif tag_name == 'code' and element.parent.name != 'pre':
            text = element.get_text(strip=True)
            if text:
                text_parts.append(f'`{text}`')
                
        # Links (preserve URL)
        elif tag_name == 'a':
            text = element.get_text(strip=True)
            href = element.get('href', '')
            if text:
                if href and not self.ignore_links:
                    text_parts.append(f'[{text}]({href})')
                else:
                    text_parts.append(text)
                    
        # Line breaks
        elif tag_name == 'br':
            text_parts.append('\n')
            
        # Inline elements that should preserve surrounding spaces
        elif tag_name in ['span', 'strong', 'em', 'b', 'i', 'u']:
            for child in element.children:
                self._extract_structured_text(child, text_parts, depth + 1)
                
        # Default: recursively process children
        else:
            for child in element.children:
                self._extract_structured_text(child, text_parts, depth + 1)
                
    def _convert_to_markdown(self, html_content: str) -> str:
        """Convert HTML to markdown format.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Markdown formatted text
        """
        # Use html2text for conversion
        markdown = self.html_converter.handle(html_content)
        
        # Clean up excessive blank lines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        return markdown.strip()
        
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from HTML content.
        
        Args:
            content: Raw HTML content
            
        Returns:
            Dictionary of metadata
        """
        metadata = super()._extract_metadata(content)
        
        # Parse with BeautifulSoup for additional metadata
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract from meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content_value = meta.get('content')
            
            if name and content_value:
                key = name.lower().replace(':', '_').replace('-', '_')
                metadata[f'meta_{key}'] = content_value
                
        # Extract language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag['lang']
            
        # Count various elements
        metadata['heading_count'] = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
        metadata['paragraph_count'] = len(soup.find_all('p'))
        metadata['link_count'] = len(soup.find_all('a'))
        metadata['image_count'] = len(soup.find_all('img'))
        
        return metadata
        
    def _process_content(self, content: Any) -> str:
        """Process the raw content into text.
        
        This is implemented through the _parse_content method.
        """
        # Not used in this implementation
        pass