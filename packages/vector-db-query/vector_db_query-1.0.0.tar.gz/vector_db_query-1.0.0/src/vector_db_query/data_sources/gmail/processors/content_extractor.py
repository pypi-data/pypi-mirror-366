"""Email content extraction and cleaning."""

import re
from typing import Dict, Any, List, Optional
from html.parser import HTMLParser
from io import StringIO

from .base import EmailProcessor
from ....utils.logger import get_logger

logger = get_logger(__name__)


class HTMLTextExtractor(HTMLParser):
    """Extract text from HTML content."""
    
    def __init__(self):
        super().__init__()
        self.text = StringIO()
        self.skip_tags = {'script', 'style', 'meta', 'link'}
        self.current_tag = None
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        # Add line breaks for block elements
        if tag in ['p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']:
            self.text.write('\n')
    
    def handle_endtag(self, tag):
        if tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.text.write('\n')
        self.current_tag = None
    
    def handle_data(self, data):
        if self.current_tag not in self.skip_tags:
            self.text.write(data)
    
    def get_text(self):
        return self.text.getvalue()


class ContentExtractor(EmailProcessor):
    """Extract and clean email content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content extractor.
        
        Config options:
            extract_urls: Extract URLs from content (default: True)
            extract_emails: Extract email addresses (default: True)
            extract_phone_numbers: Extract phone numbers (default: True)
            remove_signatures: Try to remove email signatures (default: True)
            max_content_length: Maximum content length to process (default: 100000)
        """
        super().__init__(config)
        
        # URL patterns
        self.url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+', 
            re.IGNORECASE
        )
        
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone number patterns
        self.phone_patterns = [
            re.compile(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'),
            re.compile(r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'),
            re.compile(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}')
        ]
        
        # Common signature indicators
        self.signature_patterns = [
            re.compile(r'^--\s*$', re.MULTILINE),
            re.compile(r'^(Best|Kind|Warm|Regards|Sincerely|Thanks|Thank you|Best wishes)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'^(Sent from|Get Outlook|Sent with)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'^\s*_{3,}\s*$', re.MULTILINE),  # Underscores
            re.compile(r'^\s*-{3,}\s*$', re.MULTILINE),  # Dashes
        ]
    
    async def process(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and process email content.
        
        Args:
            email_data: Raw email data
            
        Returns:
            Email data with extracted content
        """
        # Get text content
        text_content = email_data.get('body_text', '')
        html_content = email_data.get('body_html', '')
        
        # Extract text from HTML if needed
        if html_content and not text_content:
            text_content = self._extract_text_from_html(html_content)
        
        # Clean and process content
        cleaned_content = self._clean_content(text_content)
        
        # Remove signature if configured
        if self.config.get('remove_signatures', True):
            cleaned_content = self._remove_signature(cleaned_content)
        
        # Extract entities
        extracted_data = {
            'cleaned_content': cleaned_content,
            'content_length': len(cleaned_content),
            'extracted_entities': {}
        }
        
        if self.config.get('extract_urls', True):
            urls = self._extract_urls(cleaned_content + ' ' + html_content)
            if urls:
                extracted_data['extracted_entities']['urls'] = urls
        
        if self.config.get('extract_emails', True):
            emails = self._extract_emails(cleaned_content)
            if emails:
                extracted_data['extracted_entities']['email_addresses'] = emails
        
        if self.config.get('extract_phone_numbers', True):
            phones = self._extract_phone_numbers(cleaned_content)
            if phones:
                extracted_data['extracted_entities']['phone_numbers'] = phones
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(cleaned_content)
        if key_phrases:
            extracted_data['key_phrases'] = key_phrases
        
        # Update email data
        email_data['content'] = extracted_data
        
        return email_data
    
    def _extract_text_from_html(self, html: str) -> str:
        """Extract plain text from HTML content.
        
        Args:
            html: HTML content
            
        Returns:
            Extracted text
        """
        try:
            extractor = HTMLTextExtractor()
            extractor.feed(html)
            text = extractor.get_text()
            
            # Clean up excessive whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = re.sub(r' {2,}', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            logger.warning(f"Failed to extract text from HTML: {e}")
            # Fallback: basic tag removal
            text = re.sub('<[^<]+?>', '', html)
            return text.strip()
    
    def _clean_content(self, content: str) -> str:
        """Clean email content.
        
        Args:
            content: Raw text content
            
        Returns:
            Cleaned content
        """
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove common email artifacts
        content = re.sub(r'^\s*>+\s*', '', content, flags=re.MULTILINE)  # Quote markers
        content = re.sub(r'\r\n', '\n', content)  # Normalize line endings
        
        # Trim to max length if configured
        max_length = self.config.get('max_content_length', 100000)
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content.strip()
    
    def _remove_signature(self, content: str) -> str:
        """Try to remove email signature.
        
        Args:
            content: Email content
            
        Returns:
            Content without signature
        """
        lines = content.split('\n')
        
        # Find potential signature start
        signature_start = len(lines)
        
        for i, line in enumerate(lines):
            for pattern in self.signature_patterns:
                if pattern.search(line):
                    signature_start = min(signature_start, i)
                    break
        
        # If signature found, remove it
        if signature_start < len(lines):
            # Keep some context before signature
            if signature_start > 0:
                content = '\n'.join(lines[:signature_start])
            else:
                content = '\n'.join(lines)
        
        return content.strip()
    
    def _extract_urls(self, content: str) -> List[str]:
        """Extract URLs from content.
        
        Args:
            content: Text content
            
        Returns:
            List of unique URLs
        """
        urls = self.url_pattern.findall(content)
        
        # Clean and deduplicate
        cleaned_urls = []
        seen = set()
        
        for url in urls:
            # Remove trailing punctuation
            url = re.sub(r'[.,;:!?\'"]+$', '', url)
            
            # Skip if already seen
            if url in seen:
                continue
            
            seen.add(url)
            cleaned_urls.append(url)
        
        return cleaned_urls
    
    def _extract_emails(self, content: str) -> List[str]:
        """Extract email addresses from content.
        
        Args:
            content: Text content
            
        Returns:
            List of unique email addresses
        """
        emails = self.email_pattern.findall(content)
        
        # Deduplicate and lowercase
        unique_emails = list(set(email.lower() for email in emails))
        
        return unique_emails
    
    def _extract_phone_numbers(self, content: str) -> List[str]:
        """Extract phone numbers from content.
        
        Args:
            content: Text content
            
        Returns:
            List of potential phone numbers
        """
        phone_numbers = []
        seen = set()
        
        for pattern in self.phone_patterns:
            matches = pattern.findall(content)
            for match in matches:
                # Normalize the number
                normalized = re.sub(r'[^\d+]', '', match)
                
                # Check if it's a reasonable phone number length
                if 7 <= len(normalized) <= 15 and normalized not in seen:
                    seen.add(normalized)
                    phone_numbers.append(match)
        
        return phone_numbers
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract potential key phrases from content.
        
        Args:
            content: Text content
            
        Returns:
            List of key phrases
        """
        key_phrases = []
        
        # Look for common important indicators
        important_patterns = [
            (r'(?:action items?|todo|tasks?):\s*(.+?)(?:\n|$)', 'action_item'),
            (r'(?:deadline|due date|by):\s*(.+?)(?:\n|$)', 'deadline'),
            (r'(?:meeting|call|conference):\s*(.+?)(?:\n|$)', 'meeting'),
            (r'(?:decision|decided|agreed):\s*(.+?)(?:\n|$)', 'decision'),
            (r'(?:urgent|important|critical):\s*(.+?)(?:\n|$)', 'priority')
        ]
        
        for pattern, phrase_type in important_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                phrase = match.strip()[:200]  # Limit length
                if phrase:
                    key_phrases.append({
                        'type': phrase_type,
                        'text': phrase
                    })
        
        return key_phrases