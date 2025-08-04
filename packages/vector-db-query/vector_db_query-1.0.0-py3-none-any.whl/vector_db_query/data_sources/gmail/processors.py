"""Email processing pipeline with NLP extraction."""

import re
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import hashlib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from ..nlp_extraction import get_nlp_extractor, EmailNLPExtractor
from ...utils.logger import get_logger

logger = get_logger(__name__)


class EmailContentProcessor:
    """Processes email content, extracting text and structure."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize content processor."""
        self.config = config or {}
        self.extract_urls = self.config.get('extract_urls', True)
        self.extract_emails = self.config.get('extract_emails', True)
        self.remove_signatures = self.config.get('remove_signatures', True)
        
    async def process(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email content.
        
        Args:
            email_data: Raw email data
            
        Returns:
            Processed content
        """
        result = {
            'cleaned_text': '',
            'urls': [],
            'email_addresses': [],
            'signature': None,
            'quoted_text': []
        }
        
        # Extract text content
        text_content = email_data.get('body_text', '')
        
        if text_content:
            # Clean and extract from text
            result['cleaned_text'] = self._clean_text(text_content)
            
            if self.extract_urls:
                result['urls'] = self._extract_urls(text_content)
            
            if self.extract_emails:
                result['email_addresses'] = self._extract_emails(text_content)
            
            if self.remove_signatures:
                text_parts = self._split_signature(text_content)
                result['cleaned_text'] = text_parts['body']
                result['signature'] = text_parts['signature']
            
            # Extract quoted text
            result['quoted_text'] = self._extract_quoted_text(text_content)
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean email text."""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        return text.strip()
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return list(set(re.findall(url_pattern, text)))
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(email_pattern, text)))
    
    def _split_signature(self, text: str) -> Dict[str, str]:
        """Split email body from signature."""
        # Common signature indicators
        sig_patterns = [
            r'^--\s*$',
            r'^Best regards,?$',
            r'^Regards,?$',
            r'^Sincerely,?$',
            r'^Thanks,?$',
            r'^Thank you,?$',
            r'^Sent from my',
        ]
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            for pattern in sig_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    return {
                        'body': '\n'.join(lines[:i]).strip(),
                        'signature': '\n'.join(lines[i:]).strip()
                    }
        
        return {'body': text, 'signature': None}
    
    def _extract_quoted_text(self, text: str) -> List[str]:
        """Extract quoted/replied text."""
        quoted_sections = []
        
        # Look for common quote patterns
        quote_patterns = [
            r'^>.*$',  # > quoted lines
            r'^On .* wrote:$',  # Gmail style
            r'^-----Original Message-----$',  # Outlook style
        ]
        
        lines = text.split('\n')
        in_quote = False
        current_quote = []
        
        for line in lines:
            if any(re.match(pattern, line.strip()) for pattern in quote_patterns):
                in_quote = True
            
            if in_quote:
                current_quote.append(line)
            elif current_quote:
                quoted_sections.append('\n'.join(current_quote))
                current_quote = []
                in_quote = False
        
        if current_quote:
            quoted_sections.append('\n'.join(current_quote))
        
        return quoted_sections


class MeetingInfoProcessor:
    """Extracts meeting information from emails."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize meeting processor."""
        self.config = config or {}
        self.extract_zoom = self.config.get('extract_zoom', True)
        self.extract_teams = self.config.get('extract_teams', True)
        self.extract_meet = self.config.get('extract_meet', True)
        self.extract_calendar = self.config.get('extract_calendar', True)
    
    async def process(self, email_data: Dict[str, Any], content_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meeting information.
        
        Args:
            email_data: Raw email data
            content_result: Result from content processor
            
        Returns:
            Meeting information
        """
        result = {
            'has_meeting': False,
            'meeting_links': [],
            'meeting_type': None,
            'meeting_id': None,
            'meeting_password': None,
            'calendar_event': None
        }
        
        text = content_result.get('cleaned_text', '') + '\n' + email_data.get('body_text', '')
        
        # Extract Zoom meetings
        if self.extract_zoom:
            zoom_info = self._extract_zoom_info(text)
            if zoom_info:
                result['has_meeting'] = True
                result['meeting_type'] = 'zoom'
                result['meeting_links'].extend(zoom_info.get('links', []))
                result['meeting_id'] = zoom_info.get('meeting_id')
                result['meeting_password'] = zoom_info.get('password')
        
        # Extract Teams meetings
        if self.extract_teams:
            teams_links = self._extract_teams_links(text)
            if teams_links:
                result['has_meeting'] = True
                result['meeting_type'] = result['meeting_type'] or 'teams'
                result['meeting_links'].extend(teams_links)
        
        # Extract Google Meet
        if self.extract_meet:
            meet_links = self._extract_meet_links(text)
            if meet_links:
                result['has_meeting'] = True
                result['meeting_type'] = result['meeting_type'] or 'meet'
                result['meeting_links'].extend(meet_links)
        
        # Extract calendar information
        if self.extract_calendar:
            result['calendar_event'] = self._extract_calendar_info(email_data)
        
        return result
    
    def _extract_zoom_info(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract Zoom meeting information."""
        zoom_url_pattern = r'https://[a-zA-Z0-9.-]*zoom\.us/[j/]*(\d+)'
        zoom_id_pattern = r'Meeting ID:\s*(\d+[-\s]*\d+[-\s]*\d+)'
        zoom_pwd_pattern = r'Password:\s*(\S+)'
        
        result = {'links': [], 'meeting_id': None, 'password': None}
        
        # Find Zoom URLs
        zoom_urls = re.findall(zoom_url_pattern, text)
        if zoom_urls:
            result['links'] = [url for url in re.findall(r'https://[a-zA-Z0-9.-]*zoom\.us/\S+', text)]
            result['meeting_id'] = zoom_urls[0]
        
        # Find meeting ID
        id_match = re.search(zoom_id_pattern, text)
        if id_match:
            result['meeting_id'] = re.sub(r'[-\s]', '', id_match.group(1))
        
        # Find password
        pwd_match = re.search(zoom_pwd_pattern, text)
        if pwd_match:
            result['password'] = pwd_match.group(1)
        
        return result if result['links'] or result['meeting_id'] else None
    
    def _extract_teams_links(self, text: str) -> List[str]:
        """Extract Microsoft Teams meeting links."""
        teams_pattern = r'https://teams\.microsoft\.com/l/meetup-join/[^\s<"]+'
        return list(set(re.findall(teams_pattern, text)))
    
    def _extract_meet_links(self, text: str) -> List[str]:
        """Extract Google Meet links."""
        meet_pattern = r'https://meet\.google\.com/[a-z]{3}-[a-z]{4}-[a-z]{3}'
        return list(set(re.findall(meet_pattern, text)))
    
    def _extract_calendar_info(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract calendar event information from email."""
        # Check for calendar attachments (ics files)
        attachments = email_data.get('attachments', [])
        for attachment in attachments:
            if attachment.get('filename', '').endswith('.ics'):
                # TODO: Parse ICS file content
                return {'has_calendar_attachment': True, 'filename': attachment['filename']}
        
        return None


class EmailProcessingPipeline:
    """Main email processing pipeline with NLP extraction."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize pipeline."""
        self.config = config or {}
        
        # Initialize processors
        self.content_processor = EmailContentProcessor(self.config.get('content_config', {}))
        self.meeting_processor = MeetingInfoProcessor(self.config.get('meeting_config', {}))
        
        # Initialize NLP extractor
        self.nlp_extractor = get_nlp_extractor('email')
        
    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email through all pipeline stages.
        
        Args:
            email_data: Raw email data
            
        Returns:
            Fully processed email data
        """
        # Start with original data
        result = email_data.copy()
        
        try:
            # Process content
            content_result = await self.content_processor.process(email_data)
            result['content'] = content_result
            
            # Extract meeting information
            meeting_result = await self.meeting_processor.process(email_data, content_result)
            result['meeting_info'] = meeting_result
            
            # Perform NLP extraction
            nlp_result = await self._perform_nlp_extraction(email_data, content_result)
            result['nlp_extraction'] = nlp_result
            
            # Generate summary
            result['summary'] = self._generate_summary(result)
            
            # Add processing metadata
            result['processing'] = {
                'processed_at': datetime.utcnow().isoformat(),
                'pipeline_version': '1.0',
                'processors_used': ['content', 'meeting', 'nlp']
            }
            
        except Exception as e:
            logger.error(f"Error processing email: {e}")
            result['processing_error'] = str(e)
        
        return result
    
    async def _perform_nlp_extraction(self, 
                                    email_data: Dict[str, Any], 
                                    content_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform NLP extraction on email.
        
        Args:
            email_data: Original email data
            content_result: Processed content
            
        Returns:
            NLP extraction results
        """
        try:
            # Get email components
            subject = email_data.get('headers', {}).get('subject', '')
            body = content_result.get('cleaned_text', '') or email_data.get('body_text', '')
            sender = email_data.get('metadata', {}).get('sender_email', '')
            
            # Use specialized email extractor
            if isinstance(self.nlp_extractor, EmailNLPExtractor):
                nlp_metadata = self.nlp_extractor.extract_email_metadata(
                    subject=subject,
                    body=body,
                    sender=sender
                )
            else:
                # Fallback to general extraction
                full_text = f"{subject}\n\n{body}"
                nlp_metadata = self.nlp_extractor.extract_summary_metadata(full_text)
            
            return nlp_metadata.get('nlp_extraction', {})
            
        except Exception as e:
            logger.error(f"NLP extraction failed: {e}")
            return {
                'error': str(e),
                'entities': {},
                'sentiment': {'polarity': 'neutral', 'score': 0.0}
            }
    
    def _generate_summary(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of processed email.
        
        Args:
            processed_data: Fully processed email data
            
        Returns:
            Summary information
        """
        summary = {
            'has_meeting': processed_data.get('meeting_info', {}).get('has_meeting', False),
            'has_attachments': len(processed_data.get('attachments', [])) > 0,
            'has_action_items': processed_data.get('nlp_extraction', {}).get('has_action_items', False),
            'sentiment': processed_data.get('nlp_extraction', {}).get('sentiment', {}).get('polarity', 'neutral'),
            'urgency_score': processed_data.get('nlp_extraction', {}).get('urgency_score', 0.0),
            'key_entities': {
                'people': processed_data.get('nlp_extraction', {}).get('entities', {}).get('person', [])[:3],
                'organizations': processed_data.get('nlp_extraction', {}).get('entities', {}).get('organization', [])[:3]
            },
            'extracted_urls': len(processed_data.get('content', {}).get('urls', [])),
            'word_count': processed_data.get('nlp_extraction', {}).get('statistics', {}).get('word_count', 0)
        }
        
        return summary