"""Gmail IMAP client for email fetching."""

import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any, Optional, Tuple, Generator
from datetime import datetime, timedelta
import re
import base64
from pathlib import Path
import mimetypes

from ...utils.logger import get_logger

logger = get_logger(__name__)


class GmailIMAPClient:
    """IMAP client for Gmail email access."""
    
    GMAIL_IMAP_HOST = "imap.gmail.com"
    GMAIL_IMAP_PORT = 993
    
    def __init__(self, email_address: str, access_token: str):
        """Initialize Gmail IMAP client.
        
        Args:
            email_address: User's email address
            access_token: OAuth2 access token
        """
        self.email_address = email_address
        self.access_token = access_token
        self.connection = None
        self._connected = False
    
    def connect(self) -> bool:
        """Connect to Gmail IMAP server using OAuth2.
        
        Returns:
            True if connection successful
        """
        try:
            # Create IMAP4_SSL connection
            self.connection = imaplib.IMAP4_SSL(
                self.GMAIL_IMAP_HOST,
                self.GMAIL_IMAP_PORT
            )
            
            # Build OAuth2 authentication string
            auth_string = f"user={self.email_address}\x01auth=Bearer {self.access_token}\x01\x01"
            
            # Authenticate using OAuth2
            self.connection.authenticate('XOAUTH2', lambda x: auth_string.encode())
            
            self._connected = True
            logger.info(f"Connected to Gmail IMAP for {self.email_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Gmail IMAP: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Gmail IMAP server."""
        if self.connection:
            try:
                self.connection.logout()
            except:
                pass
            finally:
                self.connection = None
                self._connected = False
    
    def list_folders(self) -> List[str]:
        """List all available folders/labels.
        
        Returns:
            List of folder names
        """
        if not self._connected:
            raise RuntimeError("Not connected to IMAP server")
        
        folders = []
        try:
            # List all folders
            status, folder_list = self.connection.list()
            
            if status == 'OK':
                for folder_data in folder_list:
                    # Parse folder name from response
                    # Format: (\\HasNoChildren) "/" "INBOX"
                    match = re.search(r'"([^"]+)"$', folder_data.decode())
                    if match:
                        folders.append(match.group(1))
            
            return folders
            
        except Exception as e:
            logger.error(f"Failed to list folders: {e}")
            return []
    
    def select_folder(self, folder: str = "INBOX") -> Tuple[bool, int]:
        """Select a folder/label for operations.
        
        Args:
            folder: Folder name (default: INBOX)
            
        Returns:
            Tuple of (success, message_count)
        """
        if not self._connected:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            # Select the folder
            status, data = self.connection.select(f'"{folder}"')
            
            if status == 'OK':
                # Get message count
                message_count = int(data[0]) if data and data[0] else 0
                logger.info(f"Selected folder '{folder}' with {message_count} messages")
                return True, message_count
            else:
                logger.error(f"Failed to select folder '{folder}': {status}")
                return False, 0
                
        except Exception as e:
            logger.error(f"Error selecting folder '{folder}': {e}")
            return False, 0
    
    def search_messages(self, 
                       criteria: str = "ALL",
                       since_date: Optional[datetime] = None,
                       limit: Optional[int] = None) -> List[str]:
        """Search for messages matching criteria.
        
        Args:
            criteria: IMAP search criteria (default: ALL)
            since_date: Only return messages since this date
            limit: Maximum number of messages to return
            
        Returns:
            List of message IDs
        """
        if not self._connected:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            # Build search criteria
            search_criteria = criteria
            
            if since_date:
                # Format date for IMAP search
                date_str = since_date.strftime("%d-%b-%Y")
                search_criteria = f'({criteria} SINCE {date_str})'
            
            # Search for messages
            status, data = self.connection.search(None, search_criteria)
            
            if status == 'OK':
                message_ids = data[0].split() if data[0] else []
                
                # Apply limit if specified
                if limit and len(message_ids) > limit:
                    # Return most recent messages (end of list)
                    message_ids = message_ids[-limit:]
                
                logger.info(f"Found {len(message_ids)} messages matching criteria")
                return [msg_id.decode() for msg_id in message_ids]
            else:
                logger.error(f"Search failed: {status}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []
    
    def fetch_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a complete message by ID.
        
        Args:
            message_id: IMAP message ID
            
        Returns:
            Dictionary with message data or None
        """
        if not self._connected:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            # Fetch the message
            status, data = self.connection.fetch(message_id, '(RFC822)')
            
            if status == 'OK' and data[0]:
                # Parse the email message
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Extract message data
                message_data = self._parse_message(msg, message_id)
                return message_data
            else:
                logger.error(f"Failed to fetch message {message_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching message {message_id}: {e}")
            return None
    
    def fetch_message_headers(self, message_id: str) -> Optional[Dict[str, str]]:
        """Fetch only message headers.
        
        Args:
            message_id: IMAP message ID
            
        Returns:
            Dictionary with headers or None
        """
        if not self._connected:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            # Fetch only headers
            status, data = self.connection.fetch(
                message_id, 
                '(BODY[HEADER.FIELDS (FROM TO CC SUBJECT DATE MESSAGE-ID)])'
            )
            
            if status == 'OK' and data[0]:
                # Parse headers
                headers_raw = data[0][1]
                msg = email.message_from_bytes(headers_raw)
                
                headers = {
                    'from': msg.get('From', ''),
                    'to': msg.get('To', ''),
                    'cc': msg.get('Cc', ''),
                    'subject': self._decode_header(msg.get('Subject', '')),
                    'date': msg.get('Date', ''),
                    'message_id': msg.get('Message-ID', '')
                }
                
                return headers
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error fetching headers for {message_id}: {e}")
            return None
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read.
        
        Args:
            message_id: IMAP message ID
            
        Returns:
            True if successful
        """
        if not self._connected:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            # Add SEEN flag
            status, data = self.connection.store(message_id, '+FLAGS', '\\Seen')
            return status == 'OK'
            
        except Exception as e:
            logger.error(f"Error marking message {message_id} as read: {e}")
            return False
    
    def add_label(self, message_id: str, label: str) -> bool:
        """Add a label to a message.
        
        Args:
            message_id: IMAP message ID
            label: Gmail label to add
            
        Returns:
            True if successful
        """
        if not self._connected:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            # Gmail uses X-GM-LABELS for labels
            status, data = self.connection.store(
                message_id, 
                '+X-GM-LABELS', 
                f'"{label}"'
            )
            return status == 'OK'
            
        except Exception as e:
            logger.error(f"Error adding label to message {message_id}: {e}")
            return False
    
    def _parse_message(self, msg: email.message.Message, message_id: str) -> Dict[str, Any]:
        """Parse email message into structured data.
        
        Args:
            msg: Email message object
            message_id: IMAP message ID
            
        Returns:
            Dictionary with parsed message data
        """
        # Extract headers
        headers = {
            'from': msg.get('From', ''),
            'to': msg.get('To', ''),
            'cc': msg.get('Cc', ''),
            'subject': self._decode_header(msg.get('Subject', '')),
            'date': msg.get('Date', ''),
            'message_id': msg.get('Message-ID', '')
        }
        
        # Parse date
        date_str = headers['date']
        try:
            # Try to parse the date
            from email.utils import parsedate_to_datetime
            parsed_date = parsedate_to_datetime(date_str)
        except:
            parsed_date = datetime.utcnow()
        
        # Extract body and attachments
        body_text = ""
        body_html = ""
        attachments = []
        
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Skip multipart containers
            if part.is_multipart():
                continue
            
            # Check if it's an attachment
            if "attachment" in content_disposition:
                # Extract attachment info
                filename = part.get_filename()
                if filename:
                    filename = self._decode_header(filename)
                    
                    attachment_info = {
                        'filename': filename,
                        'content_type': content_type,
                        'size': len(part.get_payload())
                    }
                    attachments.append(attachment_info)
            else:
                # Extract body content
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        text = payload.decode(charset, errors='replace')
                        
                        if content_type == "text/plain":
                            body_text += text
                        elif content_type == "text/html":
                            body_html += text
                except Exception as e:
                    logger.warning(f"Failed to decode message part: {e}")
        
        # Build message data
        message_data = {
            'id': message_id,
            'headers': headers,
            'date': parsed_date,
            'body_text': body_text.strip(),
            'body_html': body_html.strip(),
            'attachments': attachments,
            'has_attachments': len(attachments) > 0
        }
        
        # Extract additional metadata
        message_data['metadata'] = self._extract_metadata(message_data)
        
        return message_data
    
    def _decode_header(self, header_value: str) -> str:
        """Decode email header value.
        
        Args:
            header_value: Raw header value
            
        Returns:
            Decoded string
        """
        if not header_value:
            return ""
        
        # Decode header
        decoded_parts = decode_header(header_value)
        
        # Combine parts
        result = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                # Decode bytes
                if encoding:
                    try:
                        result += part.decode(encoding)
                    except:
                        result += part.decode('utf-8', errors='replace')
                else:
                    result += part.decode('utf-8', errors='replace')
            else:
                result += part
        
        return result.strip()
    
    def _extract_metadata(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional metadata from message.
        
        Args:
            message_data: Parsed message data
            
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        
        # Extract sender email
        from_header = message_data['headers']['from']
        email_match = re.search(r'<([^>]+)>', from_header)
        if email_match:
            metadata['sender_email'] = email_match.group(1)
        else:
            # Simple email without name
            metadata['sender_email'] = from_header.strip()
        
        # Extract sender name
        name_match = re.search(r'^([^<]+)<', from_header)
        if name_match:
            metadata['sender_name'] = name_match.group(1).strip().strip('"')
        
        # Check for meeting links
        body = message_data['body_text'] + " " + message_data['body_html']
        
        # Zoom links
        zoom_pattern = r'https?://[^\s]*zoom\.us/[^\s]+'
        zoom_links = re.findall(zoom_pattern, body)
        if zoom_links:
            metadata['meeting_links'] = {'zoom': zoom_links}
        
        # Google Meet links
        meet_pattern = r'https?://meet\.google\.com/[^\s]+'
        meet_links = re.findall(meet_pattern, body)
        if meet_links:
            metadata.setdefault('meeting_links', {})['google_meet'] = meet_links
        
        # Teams links
        teams_pattern = r'https?://teams\.microsoft\.com/[^\s]+'
        teams_links = re.findall(teams_pattern, body)
        if teams_links:
            metadata.setdefault('meeting_links', {})['teams'] = teams_links
        
        return metadata
    
    def download_attachment(self, 
                          message_id: str, 
                          attachment_name: str,
                          save_path: Path) -> bool:
        """Download an attachment from a message.
        
        Args:
            message_id: IMAP message ID
            attachment_name: Name of attachment to download
            save_path: Path to save the attachment
            
        Returns:
            True if successful
        """
        if not self._connected:
            raise RuntimeError("Not connected to IMAP server")
        
        try:
            # Fetch the full message
            status, data = self.connection.fetch(message_id, '(RFC822)')
            
            if status != 'OK' or not data[0]:
                return False
            
            # Parse the message
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Find and save the attachment
            for part in msg.walk():
                if part.get_filename() == attachment_name:
                    # Get attachment data
                    payload = part.get_payload(decode=True)
                    
                    # Save to file
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    save_path.write_bytes(payload)
                    
                    logger.info(f"Downloaded attachment '{attachment_name}' to {save_path}")
                    return True
            
            logger.warning(f"Attachment '{attachment_name}' not found in message {message_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error downloading attachment: {e}")
            return False