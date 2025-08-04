"""Email file reader implementation for .eml and .mbox formats."""

import email
import mailbox
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
import html2text
from datetime import datetime

from vector_db_query.document_processor.web_readers import EmailDocumentReader
from vector_db_query.document_processor.exceptions import DocumentReadError
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class EmailReader(EmailDocumentReader):
    """Reader for email files (.eml, .mbox)."""
    
    def __init__(self):
        """Initialize the email reader."""
        super().__init__()
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0  # No line wrapping
        self._reader_factory = None  # Will be set when needed to avoid circular imports
        
        # Additional attributes for email processing
        self.include_headers = True
        self.include_attachments = True
        self.include_notes = False  # Not applicable for emails but might be expected
        self.sanitize_content = False
        self.email_separator = "=" * 80
        
    def can_read(self, file_path: Path) -> bool:
        """Check if this reader can handle the file type."""
        return file_path.suffix.lower() in self.supported_extensions
        
    def read(self, file_path: Path) -> str:
        """Read email file and extract content."""
        # Ensure file_path is a Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.eml':
                return self._read_eml(file_path)
            elif extension == '.mbox':
                return self._read_mbox(file_path)
            else:
                raise DocumentReadError(
                    f"Unsupported email format: {extension}",
                    file_path=str(file_path)
                )
        except Exception as e:
            raise DocumentReadError(
                f"Failed to read email file: {e}",
                file_path=str(file_path)
            )
            
    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.eml', '.mbox']
        
    def supports_extension(self, extension: str) -> bool:
        """Check if a file extension is supported.
        
        Args:
            extension: File extension (with or without dot)
            
        Returns:
            True if the extension is supported
        """
        if not extension:
            return False
            
        # Normalize extension (ensure it starts with a dot)
        if not extension.startswith('.'):
            extension = f'.{extension}'
            
        return extension.lower() in self.supported_extensions
        
    def _read_eml(self, file_path: Path) -> str:
        """Read .eml file."""
        logger.info(f"Reading EML file: {file_path.name}")
        
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
            
        return self._extract_email_content(msg, file_path.name)
        
    def _read_mbox(self, file_path: Path) -> str:
        """Read .mbox file containing multiple emails."""
        logger.info(f"Reading MBOX file: {file_path.name}")
        
        mbox = mailbox.mbox(str(file_path))
        email_parts = []
        
        for i, msg in enumerate(mbox):
            try:
                content = self._extract_email_content(msg, f"Email {i+1}")
                if content:
                    email_parts.append(content)
            except Exception as e:
                logger.warning(f"Failed to process email {i+1} in mbox: {e}")
                continue
                
        mbox.close()
        
        if not email_parts:
            return "No readable emails found in mbox file."
            
        return f"\n{self.email_separator}\n".join(email_parts)
        
    def _extract_email_content(self, msg: email.message.Message, identifier: str) -> str:
        """Extract content from an email message."""
        parts = []
        
        # Extract metadata
        self._metadata = self._extract_email_metadata(msg)
        
        # Format headers if enabled
        if self.include_headers:
            headers = self._format_headers(msg)
            if headers:
                parts.append(headers)
                
        # Extract body
        body = self._extract_body(msg)
        if body:
            parts.append(f"Body:\n{body}")
            
        # Process attachments if enabled
        if self.include_attachments:
            attachments = self._extract_attachments(msg)
            if attachments:
                parts.append(f"\nAttachments:\n{attachments}")
                
        # Detect thread information
        if self.detect_threads:
            thread_info = self._extract_thread_info(msg)
            if thread_info:
                parts.append(f"\nThread Info:\n{thread_info}")
                
        # Format the complete email
        content = "\n\n".join(parts)
        
        if self.sanitize_content:
            content = self._sanitize_content(content)
            
        return f"=== {identifier} ===\n{content}" if content else ""
        
    def _extract_email_metadata(self, msg: email.message.Message) -> Dict[str, Any]:
        """Extract metadata from email."""
        metadata = {}
        
        # Basic headers
        for header in ['From', 'To', 'Subject', 'Date', 'Message-ID']:
            value = msg.get(header)
            if value:
                metadata[header.lower()] = value
                
        # Parse date
        date_str = msg.get('Date')
        if date_str:
            try:
                metadata['parsed_date'] = parsedate_to_datetime(date_str)
            except Exception:
                pass
                
        # Count attachments
        attachment_count = 0
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                attachment_count += 1
        metadata['attachment_count'] = attachment_count
        
        return metadata
        
    def _format_headers(self, msg: email.message.Message) -> str:
        """Format email headers."""
        headers = []
        
        # Essential headers
        essential = ['From', 'To', 'Cc', 'Subject', 'Date']
        for header in essential:
            value = msg.get(header)
            if value:
                headers.append(f"{header}: {value}")
                
        return "\n".join(headers) if headers else ""
        
    def _extract_body(self, msg: email.message.Message) -> str:
        """Extract email body text."""
        body_parts = []
        
        for part in msg.walk():
            # Skip container parts
            if part.get_content_maintype() == 'multipart':
                continue
                
            # Skip attachments
            if part.get_content_disposition() == 'attachment':
                continue
                
            content_type = part.get_content_type()
            
            try:
                # Get the payload
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                    
                # Decode based on content type
                if content_type == 'text/plain':
                    charset = part.get_content_charset() or 'utf-8'
                    text = payload.decode(charset, errors='replace')
                    body_parts.append(text)
                    
                elif content_type == 'text/html':
                    charset = part.get_content_charset() or 'utf-8'
                    html = payload.decode(charset, errors='replace')
                    # Convert HTML to text
                    text = self.html_converter.handle(html)
                    body_parts.append(text)
                    
            except Exception as e:
                logger.warning(f"Failed to extract body part: {e}")
                continue
                
        return "\n\n".join(body_parts) if body_parts else ""
        
    def _extract_attachments(self, msg: email.message.Message) -> str:
        """Extract attachment information and optionally their content."""
        attachments = []
        
        for part in msg.walk():
            if part.get_content_disposition() != 'attachment':
                continue
                
            filename = part.get_filename()
            if not filename:
                continue
                
            # Get attachment info
            content_type = part.get_content_type()
            size = len(part.get_payload(decode=True) or b'')
            
            attachment_info = f"- {filename} ({content_type}, {size:,} bytes)"
            
            # Optionally process text attachments
            if self.process_attachments and self._is_processable_attachment(filename, content_type):
                try:
                    content = self._process_attachment(part, filename)
                    if content:
                        attachment_info += f"\n  Content: {content[:200]}..."
                except Exception as e:
                    logger.warning(f"Failed to process attachment {filename}: {e}")
                    
            attachments.append(attachment_info)
            
        return "\n".join(attachments) if attachments else ""
        
    def _is_processable_attachment(self, filename: str, content_type: str) -> bool:
        """Check if attachment can be processed for text content."""
        # Text-based attachments we can process
        text_types = ['text/', 'application/json', 'application/xml']
        return any(content_type.startswith(t) for t in text_types)
        
    def _process_attachment(self, part: email.message.Message, filename: str) -> Optional[str]:
        """Process attachment content if possible."""
        try:
            payload = part.get_payload(decode=True)
            if not payload:
                return None
                
            # Try to decode as text
            charset = part.get_content_charset() or 'utf-8'
            return payload.decode(charset, errors='replace')
            
        except Exception:
            return None
            
    def _extract_thread_info(self, msg: email.message.Message) -> str:
        """Extract thread-related information."""
        thread_info = []
        
        # In-Reply-To header
        in_reply_to = msg.get('In-Reply-To')
        if in_reply_to:
            thread_info.append(f"In-Reply-To: {in_reply_to}")
            
        # References header (thread history)
        references = msg.get('References')
        if references:
            ref_list = references.split()
            thread_info.append(f"Thread References: {len(ref_list)} messages")
            
        # Thread topic from subject
        subject = msg.get('Subject', '')
        thread_subject = self._extract_thread_subject(subject)
        if thread_subject != subject:
            thread_info.append(f"Thread Topic: {thread_subject}")
            
        return "\n".join(thread_info) if thread_info else ""
        
    def _extract_thread_subject(self, subject: str) -> str:
        """Extract the core thread subject, removing Re:, Fwd:, etc."""
        # Remove common prefixes
        prefixes = r'^(Re:|RE:|Fwd:|FWD:|Fw:|FW:)\s*'
        clean_subject = re.sub(prefixes, '', subject, flags=re.IGNORECASE).strip()
        
        # Remove multiple occurrences
        while re.match(prefixes, clean_subject, re.IGNORECASE):
            clean_subject = re.sub(prefixes, '', clean_subject, flags=re.IGNORECASE).strip()
            
        return clean_subject
        
    def _sanitize_content(self, content: str) -> str:
        """Sanitize content for security."""
        # Remove potential script tags or suspicious content
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove potentially sensitive patterns (customize based on needs)
        # Example: Remove credit card-like numbers
        content = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[REDACTED-CC]', content)
        
        # Remove SSN-like patterns
        content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED-SSN]', content)
        
        return content
        
    def _process_content(self, content: Any) -> str:
        """Process the raw content into text.
        
        This is implemented through the read methods above.
        """
        # Not used in this implementation
        pass
        
    def _parse_email(self, email_data: Any) -> Dict[str, Any]:
        """Parse email data into structured format.
        
        Args:
            email_data: Raw email data (email.message.Message object)
            
        Returns:
            Dictionary with headers and body
        """
        result = {
            'headers': {},
            'body': '',
            'attachments': []
        }
        
        # Extract headers
        for header in ['From', 'To', 'Cc', 'Subject', 'Date', 'Message-ID']:
            value = email_data.get(header)
            if value:
                result['headers'][header.lower()] = value
                
        # Extract body
        result['body'] = self._extract_body(email_data)
        
        # Extract attachments info
        for part in email_data.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename:
                    result['attachments'].append({
                        'filename': filename,
                        'content_type': part.get_content_type(),
                        'size': len(part.get_payload(decode=True) or b'')
                    })
                    
        return result