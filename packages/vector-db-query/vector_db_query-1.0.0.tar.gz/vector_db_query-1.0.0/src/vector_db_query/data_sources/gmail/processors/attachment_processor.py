"""Process email attachments."""

import os
import mimetypes
from typing import Dict, Any, List, Optional
from pathlib import Path
import hashlib
import json

from .base import EmailProcessor
from ....utils.logger import get_logger

logger = get_logger(__name__)


class AttachmentProcessor(EmailProcessor):
    """Process and categorize email attachments."""
    
    # File categories
    FILE_CATEGORIES = {
        'documents': {
            'extensions': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'mimetypes': ['application/pdf', 'application/msword', 'text/plain']
        },
        'spreadsheets': {
            'extensions': ['.xls', '.xlsx', '.csv', '.ods'],
            'mimetypes': ['application/vnd.ms-excel', 'text/csv']
        },
        'presentations': {
            'extensions': ['.ppt', '.pptx', '.odp'],
            'mimetypes': ['application/vnd.ms-powerpoint']
        },
        'images': {
            'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'mimetypes': ['image/jpeg', 'image/png', 'image/gif']
        },
        'archives': {
            'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'mimetypes': ['application/zip', 'application/x-rar-compressed']
        },
        'calendar': {
            'extensions': ['.ics', '.vcs'],
            'mimetypes': ['text/calendar']
        },
        'code': {
            'extensions': ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs'],
            'mimetypes': ['text/x-python', 'application/javascript']
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize attachment processor.
        
        Config options:
            process_archives: Extract archive contents (default: False)
            max_file_size_mb: Maximum file size to process (default: 50)
            extract_text: Extract text from documents (default: True)
            generate_previews: Generate image previews (default: False)
        """
        super().__init__(config)
        
    async def process(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email attachments.
        
        Args:
            email_data: Email data with attachments
            
        Returns:
            Email data with processed attachment info
        """
        attachments = email_data.get('attachments', [])
        
        if not attachments:
            return email_data
        
        # Process each attachment
        processed_attachments = []
        
        for attachment in attachments:
            processed = await self._process_attachment(attachment, email_data)
            processed_attachments.append(processed)
        
        # Update email data
        email_data['processed_attachments'] = processed_attachments
        
        # Add summary statistics
        email_data['attachment_summary'] = self._generate_summary(processed_attachments)
        
        return email_data
    
    async def _process_attachment(self, attachment: Dict[str, Any], email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single attachment.
        
        Args:
            attachment: Attachment info
            email_data: Parent email data
            
        Returns:
            Processed attachment info
        """
        filename = attachment.get('filename', 'unknown')
        content_type = attachment.get('content_type', '')
        size = attachment.get('size', 0)
        
        # Basic processing
        processed = {
            'filename': filename,
            'content_type': content_type,
            'size': size,
            'size_mb': round(size / (1024 * 1024), 2),
            'extension': Path(filename).suffix.lower(),
            'category': self._categorize_file(filename, content_type),
            'hash': self._generate_hash(filename, size, email_data)
        }
        
        # Check file size limit
        max_size_mb = self.config.get('max_file_size_mb', 50)
        if processed['size_mb'] > max_size_mb:
            processed['skipped'] = True
            processed['skip_reason'] = f'File too large ({processed["size_mb"]} MB)'
            return processed
        
        # Add file-specific metadata
        if processed['category'] == 'calendar':
            processed['calendar_event'] = True
            processed['requires_parsing'] = True
        
        elif processed['category'] == 'documents' and self.config.get('extract_text', True):
            processed['text_extractable'] = True
            processed['requires_parsing'] = True
        
        elif processed['category'] == 'images' and self.config.get('generate_previews', False):
            processed['preview_available'] = True
        
        elif processed['category'] == 'archives' and self.config.get('process_archives', False):
            processed['requires_extraction'] = True
        
        # Detect potentially important files
        processed['importance'] = self._assess_importance(processed, email_data)
        
        return processed
    
    def _categorize_file(self, filename: str, content_type: str) -> str:
        """Categorize file based on extension and MIME type.
        
        Args:
            filename: File name
            content_type: MIME type
            
        Returns:
            File category
        """
        extension = Path(filename).suffix.lower()
        
        # Check by extension first
        for category, info in self.FILE_CATEGORIES.items():
            if extension in info['extensions']:
                return category
        
        # Check by MIME type
        for category, info in self.FILE_CATEGORIES.items():
            for mime in info['mimetypes']:
                if mime in content_type:
                    return category
        
        # Try to guess from mimetypes module
        guessed_type, _ = mimetypes.guess_type(filename)
        if guessed_type:
            for category, info in self.FILE_CATEGORIES.items():
                if guessed_type in info['mimetypes']:
                    return category
        
        return 'other'
    
    def _generate_hash(self, filename: str, size: int, email_data: Dict[str, Any]) -> str:
        """Generate unique hash for attachment.
        
        Args:
            filename: File name
            size: File size
            email_data: Parent email data
            
        Returns:
            Hash string
        """
        # Combine filename, size, and email message ID for uniqueness
        message_id = email_data.get('headers', {}).get('message_id', '')
        hash_input = f"{filename}:{size}:{message_id}"
        
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _assess_importance(self, attachment: Dict[str, Any], email_data: Dict[str, Any]) -> str:
        """Assess attachment importance.
        
        Args:
            attachment: Processed attachment info
            email_data: Parent email data
            
        Returns:
            Importance level (high, medium, low)
        """
        filename = attachment['filename'].lower()
        category = attachment['category']
        
        # High importance indicators
        high_importance_keywords = [
            'contract', 'agreement', 'invoice', 'receipt', 'report',
            'proposal', 'quote', 'budget', 'financial', 'legal',
            'confidential', 'urgent', 'important'
        ]
        
        # Check filename for important keywords
        for keyword in high_importance_keywords:
            if keyword in filename:
                return 'high'
        
        # Calendar events are usually important
        if category == 'calendar':
            return 'high'
        
        # Documents and spreadsheets from important senders
        if category in ['documents', 'spreadsheets']:
            # Check if from important sender (would need sender importance logic)
            return 'medium'
        
        # Code files might be important in technical contexts
        if category == 'code':
            return 'medium'
        
        # Images and other files are usually low importance
        return 'low'
    
    def _generate_summary(self, processed_attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate attachment summary statistics.
        
        Args:
            processed_attachments: List of processed attachments
            
        Returns:
            Summary statistics
        """
        summary = {
            'total_count': len(processed_attachments),
            'total_size_mb': sum(att.get('size_mb', 0) for att in processed_attachments),
            'by_category': {},
            'by_importance': {
                'high': 0,
                'medium': 0,
                'low': 0
            },
            'requires_processing': []
        }
        
        # Count by category
        for att in processed_attachments:
            category = att.get('category', 'other')
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
            
            # Count by importance
            importance = att.get('importance', 'low')
            summary['by_importance'][importance] += 1
            
            # Track files requiring processing
            if att.get('requires_parsing') or att.get('requires_extraction'):
                summary['requires_processing'].append({
                    'filename': att['filename'],
                    'type': 'parsing' if att.get('requires_parsing') else 'extraction'
                })
        
        return summary