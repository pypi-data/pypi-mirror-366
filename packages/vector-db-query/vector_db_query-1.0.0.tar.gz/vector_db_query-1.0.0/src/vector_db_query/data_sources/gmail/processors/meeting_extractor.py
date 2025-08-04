"""Extract meeting information from emails."""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dateutil import parser as date_parser
import pytz

from .base import EmailProcessor
from ....utils.logger import get_logger

logger = get_logger(__name__)


class MeetingExtractor(EmailProcessor):
    """Extract meeting details from email content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize meeting extractor.
        
        Config options:
            extract_zoom: Extract Zoom meeting info (default: True)
            extract_teams: Extract Teams meeting info (default: True)
            extract_meet: Extract Google Meet info (default: True)
            extract_calendar: Extract calendar events (default: True)
            timezone: Default timezone (default: UTC)
        """
        super().__init__(config)
        
        self.default_timezone = self.config.get('timezone', 'UTC')
        
        # Meeting platform patterns
        self.meeting_patterns = {
            'zoom': {
                'url': re.compile(r'https?://[^\s]*zoom\.us/j/(\d+)(?:\?pwd=([^\s&]+))?', re.IGNORECASE),
                'meeting_id': re.compile(r'Meeting ID:\s*(\d{3}\s*\d{3,4}\s*\d{3,4})', re.IGNORECASE),
                'passcode': re.compile(r'Pass(?:code|word):\s*([^\s\n]+)', re.IGNORECASE)
            },
            'teams': {
                'url': re.compile(r'https?://teams\.microsoft\.com/l/meetup-join/[^\s]+', re.IGNORECASE),
                'phone': re.compile(r'Conference ID:\s*(\d+)', re.IGNORECASE)
            },
            'meet': {
                'url': re.compile(r'https?://meet\.google\.com/[a-z]{3}-[a-z]{4}-[a-z]{3}', re.IGNORECASE),
                'phone': re.compile(r'PIN:\s*(\d+\s*#)', re.IGNORECASE)
            }
        }
        
        # Date/time patterns
        self.datetime_patterns = [
            # "Monday, January 1, 2024 at 2:00 PM PST"
            re.compile(r'(\w+,\s+\w+\s+\d{1,2},\s+\d{4})\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM))\s*(\w+)?', re.IGNORECASE),
            # "Jan 1, 2024 2:00 PM"
            re.compile(r'(\w+\s+\d{1,2},\s+\d{4})\s+(\d{1,2}:\d{2}\s*(?:AM|PM))', re.IGNORECASE),
            # "2024-01-01 14:00"
            re.compile(r'(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})'),
            # "tomorrow at 3pm"
            re.compile(r'(tomorrow|today|next\s+\w+)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', re.IGNORECASE)
        ]
        
        # Calendar event patterns
        self.calendar_patterns = {
            'ics_attachment': re.compile(r'\.ics$', re.IGNORECASE),
            'when': re.compile(r'When:\s*(.+?)(?:\n|$)', re.IGNORECASE),
            'where': re.compile(r'Where:\s*(.+?)(?:\n|$)', re.IGNORECASE),
            'organizer': re.compile(r'Organizer:\s*(.+?)(?:\n|$)', re.IGNORECASE)
        }
    
    async def process(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meeting information from email.
        
        Args:
            email_data: Email data with content
            
        Returns:
            Email data with extracted meeting info
        """
        # Get content to analyze
        content = email_data.get('body_text', '') + ' ' + email_data.get('body_html', '')
        subject = email_data.get('headers', {}).get('subject', '')
        
        # Initialize meeting data
        meeting_data = {
            'has_meeting': False,
            'meetings': []
        }
        
        # Extract meeting links
        if self.config.get('extract_zoom', True):
            zoom_meetings = self._extract_zoom_meetings(content)
            meeting_data['meetings'].extend(zoom_meetings)
        
        if self.config.get('extract_teams', True):
            teams_meetings = self._extract_teams_meetings(content)
            meeting_data['meetings'].extend(teams_meetings)
        
        if self.config.get('extract_meet', True):
            meet_meetings = self._extract_meet_meetings(content)
            meeting_data['meetings'].extend(meet_meetings)
        
        # Extract meeting times
        for meeting in meeting_data['meetings']:
            meeting_time = self._extract_meeting_time(content, subject)
            if meeting_time:
                meeting['datetime'] = meeting_time
        
        # Check for calendar attachments
        if self.config.get('extract_calendar', True):
            calendar_events = self._extract_calendar_events(email_data, content)
            meeting_data['meetings'].extend(calendar_events)
        
        # Update has_meeting flag
        if meeting_data['meetings']:
            meeting_data['has_meeting'] = True
        
        # Add meeting data to email
        email_data['meeting_info'] = meeting_data
        
        return email_data
    
    def _extract_zoom_meetings(self, content: str) -> List[Dict[str, Any]]:
        """Extract Zoom meeting information.
        
        Args:
            content: Email content
            
        Returns:
            List of Zoom meeting details
        """
        meetings = []
        
        # Find Zoom URLs
        zoom_urls = self.meeting_patterns['zoom']['url'].findall(content)
        
        for match in zoom_urls:
            meeting_id = match[0] if isinstance(match, tuple) else match
            password = match[1] if isinstance(match, tuple) and len(match) > 1 else None
            
            meeting = {
                'platform': 'zoom',
                'meeting_id': meeting_id,
                'url': f'https://zoom.us/j/{meeting_id}'
            }
            
            if password:
                meeting['password'] = password
            
            # Look for additional passcode
            passcode_match = self.meeting_patterns['zoom']['passcode'].search(content)
            if passcode_match and not password:
                meeting['password'] = passcode_match.group(1)
            
            meetings.append(meeting)
        
        # Also look for meeting ID without URL
        meeting_ids = self.meeting_patterns['zoom']['meeting_id'].findall(content)
        for meeting_id in meeting_ids:
            # Clean up meeting ID
            clean_id = re.sub(r'\s+', '', meeting_id)
            
            # Check if we already have this meeting
            if not any(m.get('meeting_id') == clean_id for m in meetings):
                meeting = {
                    'platform': 'zoom',
                    'meeting_id': clean_id,
                    'url': f'https://zoom.us/j/{clean_id}'
                }
                
                # Look for passcode
                passcode_match = self.meeting_patterns['zoom']['passcode'].search(content)
                if passcode_match:
                    meeting['password'] = passcode_match.group(1)
                
                meetings.append(meeting)
        
        return meetings
    
    def _extract_teams_meetings(self, content: str) -> List[Dict[str, Any]]:
        """Extract Microsoft Teams meeting information.
        
        Args:
            content: Email content
            
        Returns:
            List of Teams meeting details
        """
        meetings = []
        
        # Find Teams URLs
        teams_urls = self.meeting_patterns['teams']['url'].findall(content)
        
        for url in teams_urls:
            meeting = {
                'platform': 'teams',
                'url': url
            }
            
            # Look for conference ID
            conf_id_match = self.meeting_patterns['teams']['phone'].search(content)
            if conf_id_match:
                meeting['conference_id'] = conf_id_match.group(1)
            
            meetings.append(meeting)
        
        return meetings
    
    def _extract_meet_meetings(self, content: str) -> List[Dict[str, Any]]:
        """Extract Google Meet meeting information.
        
        Args:
            content: Email content
            
        Returns:
            List of Meet meeting details
        """
        meetings = []
        
        # Find Meet URLs
        meet_urls = self.meeting_patterns['meet']['url'].findall(content)
        
        for url in meet_urls:
            meeting = {
                'platform': 'google_meet',
                'url': url,
                'meeting_code': url.split('/')[-1]
            }
            
            # Look for PIN
            pin_match = self.meeting_patterns['meet']['phone'].search(content)
            if pin_match:
                meeting['phone_pin'] = pin_match.group(1)
            
            meetings.append(meeting)
        
        return meetings
    
    def _extract_meeting_time(self, content: str, subject: str) -> Optional[Dict[str, Any]]:
        """Extract meeting date and time.
        
        Args:
            content: Email content
            subject: Email subject
            
        Returns:
            Dictionary with datetime info or None
        """
        # Check both subject and content
        text_to_check = f"{subject}\n{content}"
        
        for pattern in self.datetime_patterns:
            match = pattern.search(text_to_check)
            if match:
                try:
                    # Extract components
                    date_part = match.group(1)
                    time_part = match.group(2)
                    timezone_part = match.group(3) if len(match.groups()) > 2 else None
                    
                    # Handle relative dates
                    if date_part.lower() == 'today':
                        date_part = datetime.now().strftime('%Y-%m-%d')
                    elif date_part.lower() == 'tomorrow':
                        date_part = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                    
                    # Parse datetime
                    datetime_str = f"{date_part} {time_part}"
                    parsed_dt = date_parser.parse(datetime_str)
                    
                    # Apply timezone
                    if timezone_part:
                        try:
                            tz = pytz.timezone(timezone_part)
                            parsed_dt = tz.localize(parsed_dt)
                        except:
                            # Use default timezone
                            tz = pytz.timezone(self.default_timezone)
                            parsed_dt = tz.localize(parsed_dt)
                    else:
                        tz = pytz.timezone(self.default_timezone)
                        parsed_dt = tz.localize(parsed_dt)
                    
                    return {
                        'datetime': parsed_dt.isoformat(),
                        'timezone': str(parsed_dt.tzinfo),
                        'original_text': match.group(0)
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to parse datetime: {e}")
                    continue
        
        # Try calendar patterns
        when_match = self.calendar_patterns['when'].search(content)
        if when_match:
            try:
                parsed_dt = date_parser.parse(when_match.group(1))
                return {
                    'datetime': parsed_dt.isoformat(),
                    'timezone': self.default_timezone,
                    'original_text': when_match.group(1)
                }
            except:
                pass
        
        return None
    
    def _extract_calendar_events(self, email_data: Dict[str, Any], content: str) -> List[Dict[str, Any]]:
        """Extract calendar event information.
        
        Args:
            email_data: Full email data
            content: Email content
            
        Returns:
            List of calendar events
        """
        events = []
        
        # Check for .ics attachments
        attachments = email_data.get('attachments', [])
        for attachment in attachments:
            if self.calendar_patterns['ics_attachment'].search(attachment.get('filename', '')):
                event = {
                    'platform': 'calendar',
                    'type': 'ics_attachment',
                    'filename': attachment['filename']
                }
                
                # Extract meeting details from content
                where_match = self.calendar_patterns['where'].search(content)
                if where_match:
                    event['location'] = where_match.group(1).strip()
                
                when_match = self.calendar_patterns['when'].search(content)
                if when_match:
                    event['when_text'] = when_match.group(1).strip()
                
                organizer_match = self.calendar_patterns['organizer'].search(content)
                if organizer_match:
                    event['organizer'] = organizer_match.group(1).strip()
                
                events.append(event)
        
        # Check for calendar event text patterns
        if 'calendar invitation' in content.lower() or 'meeting invitation' in content.lower():
            event = {
                'platform': 'calendar',
                'type': 'text_invitation'
            }
            
            # Extract details
            where_match = self.calendar_patterns['where'].search(content)
            if where_match:
                event['location'] = where_match.group(1).strip()
            
            when_match = self.calendar_patterns['when'].search(content)
            if when_match:
                event['when_text'] = when_match.group(1).strip()
                # Try to parse the time
                meeting_time = self._extract_meeting_time(when_match.group(1), '')
                if meeting_time:
                    event['datetime'] = meeting_time
            
            if event.get('location') or event.get('when_text'):
                events.append(event)
        
        return events