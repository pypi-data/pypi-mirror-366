"""Tests for Gmail integration."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
from pathlib import Path

from vector_db_query.data_sources.gmail import (
    GmailDataSource, GmailConfig, EmailMessage, EmailFolder
)
from vector_db_query.data_sources.models import SourceType, ProcessedDocument
from vector_db_query.data_sources.exceptions import AuthenticationError
from vector_db_query.utils.crypto import encrypt_token, decrypt_token


class TestGmailConfig:
    """Test Gmail configuration."""
    
    def test_config_initialization(self):
        """Test GmailConfig initialization."""
        config = GmailConfig(
            email="test@gmail.com",
            oauth_credentials_file="creds.json",
            oauth_token_file="token.json",
            folders=["INBOX", "[Gmail]/Sent Mail"],
            initial_history_days=30
        )
        
        assert config.email == "test@gmail.com"
        assert config.oauth_credentials_file == "creds.json"
        assert config.oauth_token_file == "token.json"
        assert config.folders == ["INBOX", "[Gmail]/Sent Mail"]
        assert config.initial_history_days == 30
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "email": "test@gmail.com",
            "oauth_credentials_file": "creds.json",
            "folders": ["INBOX"],
            "knowledge_base_folder": "kb/emails"
        }
        
        config = GmailConfig.from_dict(config_dict)
        
        assert config.email == "test@gmail.com"
        assert config.oauth_credentials_file == "creds.json"
        assert config.folders == ["INBOX"]
        assert config.knowledge_base_folder == "kb/emails"
    
    def test_config_validation(self):
        """Test config validation."""
        # Test missing email
        with pytest.raises(ValueError):
            GmailConfig(
                email="",
                oauth_credentials_file="creds.json"
            )
        
        # Test invalid email format
        with pytest.raises(ValueError):
            GmailConfig(
                email="not-an-email",
                oauth_credentials_file="creds.json"
            )


class TestGmailDataSource:
    """Test Gmail data source functionality."""
    
    @pytest.fixture
    def gmail_config(self):
        """Create Gmail configuration."""
        return GmailConfig(
            email="test@gmail.com",
            oauth_credentials_file="test_creds.json",
            oauth_token_file="test_token.json",
            folders=["INBOX"],
            initial_history_days=7
        )
    
    @pytest.fixture
    def gmail_source(self, gmail_config):
        """Create Gmail data source."""
        return GmailDataSource(gmail_config)
    
    @pytest.fixture
    def mock_imap(self):
        """Create mock IMAP client."""
        with patch('imaplib.IMAP4_SSL') as mock:
            yield mock
    
    @pytest.fixture
    def mock_oauth(self):
        """Create mock OAuth flow."""
        with patch('google_auth_oauthlib.flow.InstalledAppFlow') as mock:
            yield mock
    
    @pytest.mark.asyncio
    async def test_authentication_with_existing_token(self, gmail_source):
        """Test authentication with existing token."""
        # Mock existing token
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                    'access_token': encrypt_token('test_token'),
                    'refresh_token': encrypt_token('refresh_token'),
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'client_id': 'test_client',
                    'client_secret': 'test_secret'
                })
                
                with patch('google.oauth2.credentials.Credentials') as mock_creds:
                    mock_creds.return_value.valid = True
                    
                    result = await gmail_source.authenticate()
                    assert result is True
    
    @pytest.mark.asyncio
    async def test_authentication_new_flow(self, gmail_source, mock_oauth):
        """Test authentication with new OAuth flow."""
        # Mock no existing token
        with patch('pathlib.Path.exists', return_value=False):
            # Mock OAuth flow
            mock_flow = Mock()
            mock_creds = Mock()
            mock_creds.to_json.return_value = json.dumps({
                'access_token': 'new_token',
                'refresh_token': 'new_refresh'
            })
            mock_flow.run_local_server.return_value = mock_creds
            mock_oauth.from_client_secrets_file.return_value = mock_flow
            
            with patch('builtins.open', create=True):
                result = await gmail_source.authenticate()
                assert result is True
    
    @pytest.mark.asyncio
    async def test_imap_connection(self, gmail_source, mock_imap):
        """Test IMAP connection."""
        # Setup mock IMAP
        mock_imap_instance = Mock()
        mock_imap.return_value = mock_imap_instance
        
        # Mock authentication
        gmail_source._oauth2_string = Mock(return_value="AUTH_STRING")
        
        # Test connection
        await gmail_source._connect_imap()
        
        mock_imap.assert_called_once_with('imap.gmail.com', 993)
        mock_imap_instance.authenticate.assert_called_once_with('XOAUTH2', gmail_source._oauth2_string)
    
    @pytest.mark.asyncio
    async def test_fetch_emails(self, gmail_source, mock_imap):
        """Test fetching emails."""
        # Setup mock IMAP
        mock_imap_instance = Mock()
        mock_imap.return_value = mock_imap_instance
        
        # Mock folder selection
        mock_imap_instance.select.return_value = ('OK', [b'10'])
        
        # Mock search results
        mock_imap_instance.search.return_value = ('OK', [b'1 2 3'])
        
        # Mock fetch results
        mock_imap_instance.fetch.side_effect = [
            ('OK', [(b'1', b'RFC822 {100}', b'email content 1')]),
            ('OK', [(b'2', b'RFC822 {100}', b'email content 2')]),
            ('OK', [(b'3', b'RFC822 {100}', b'email content 3')])
        ]
        
        gmail_source.imap = mock_imap_instance
        
        # Fetch emails
        emails = await gmail_source._fetch_emails_from_folder('INBOX', datetime.utcnow())
        
        assert len(emails) == 3
    
    @pytest.mark.asyncio
    async def test_process_email(self, gmail_source):
        """Test email processing."""
        # Create mock email
        email_data = {
            'message_id': 'test_123',
            'subject': 'Test Email',
            'from': 'sender@example.com',
            'to': ['recipient@example.com'],
            'date': datetime.utcnow().isoformat(),
            'body_text': 'This is a test email',
            'body_html': '<p>This is a test email</p>',
            'attachments': []
        }
        
        # Process email
        doc = await gmail_source.process_item(email_data)
        
        assert isinstance(doc, ProcessedDocument)
        assert doc.source_id == 'test_123'
        assert doc.title == 'Test Email'
        assert 'This is a test email' in doc.content
        assert doc.source_type == SourceType.GMAIL
        assert doc.metadata['sender_email'] == 'sender@example.com'
    
    @pytest.mark.asyncio
    async def test_sync_operation(self, gmail_source, mock_imap):
        """Test full sync operation."""
        # Mock authentication
        gmail_source.creds = Mock(valid=True)
        
        # Setup mock IMAP
        mock_imap_instance = Mock()
        mock_imap.return_value = mock_imap_instance
        mock_imap_instance.select.return_value = ('OK', [b'10'])
        mock_imap_instance.search.return_value = ('OK', [b'1'])
        
        # Mock email fetch
        email_content = b'''From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000
Message-ID: <test123@example.com>

This is a test email body.
'''
        mock_imap_instance.fetch.return_value = ('OK', [(b'1', b'RFC822 {100}', email_content)])
        
        # Mock email processing pipeline
        with patch.object(gmail_source, 'processing_pipeline') as mock_pipeline:
            mock_pipeline.process_email = AsyncMock(return_value={
                'message_id': 'test123@example.com',
                'subject': 'Test Email',
                'from': 'sender@example.com',
                'to': ['recipient@example.com'],
                'date': '2024-01-01T12:00:00',
                'body_text': 'This is a test email body.',
                'attachments': [],
                'entities': [],
                'sentiment': {'polarity': 0.0, 'subjectivity': 0.0}
            })
            
            # Perform sync
            result = await gmail_source.sync()
            
            assert result.items_processed == 1
            assert len(result.processed_documents) == 1
            assert result.processed_documents[0].title == 'Test Email'
    
    @pytest.mark.asyncio
    async def test_test_connection(self, gmail_source, mock_imap):
        """Test connection testing."""
        # Mock successful authentication
        gmail_source.creds = Mock(valid=True)
        
        # Setup mock IMAP
        mock_imap_instance = Mock()
        mock_imap.return_value = mock_imap_instance
        mock_imap_instance.select.return_value = ('OK', [b'10'])
        
        result = await gmail_source.test_connection()
        assert result is True
        
        # Test failed connection
        mock_imap_instance.select.side_effect = Exception("Connection failed")
        result = await gmail_source.test_connection()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, gmail_source):
        """Test metrics retrieval."""
        # Set some test values
        gmail_source._total_emails = 100
        gmail_source._processed_emails = 75
        gmail_source._failed_emails = 5
        gmail_source._last_sync_time = datetime.utcnow()
        
        metrics = await gmail_source.get_metrics()
        
        assert metrics['total_emails'] == 100
        assert metrics['processed_emails'] == 75
        assert metrics['failed_emails'] == 5
        assert metrics['success_rate'] == 0.75
        assert 'last_sync' in metrics
        assert metrics['status'] == 'Not Authenticated'
    
    @pytest.mark.asyncio
    async def test_email_filtering(self, gmail_source):
        """Test email filtering based on configuration."""
        # Set up filters
        gmail_source.config.sender_whitelist = ['allowed@example.com']
        gmail_source.config.sender_blacklist = ['blocked@example.com']
        
        # Test whitelisted sender
        email1 = {'from': 'allowed@example.com', 'subject': 'Test'}
        assert await gmail_source._should_process_email(email1) is True
        
        # Test blacklisted sender
        email2 = {'from': 'blocked@example.com', 'subject': 'Test'}
        assert await gmail_source._should_process_email(email2) is False
        
        # Test neutral sender (not in any list)
        email3 = {'from': 'neutral@example.com', 'subject': 'Test'}
        assert await gmail_source._should_process_email(email3) is True
    
    @pytest.mark.asyncio
    async def test_attachment_handling(self, gmail_source):
        """Test attachment handling."""
        email_data = {
            'message_id': 'test_123',
            'subject': 'Email with Attachments',
            'from': 'sender@example.com',
            'body_text': 'See attached files',
            'attachments': [
                {
                    'filename': 'document.pdf',
                    'size': 1024 * 500,  # 500KB
                    'content_type': 'application/pdf'
                },
                {
                    'filename': 'image.jpg',
                    'size': 1024 * 1024 * 2,  # 2MB
                    'content_type': 'image/jpeg'
                }
            ]
        }
        
        doc = await gmail_source.process_item(email_data)
        
        assert len(doc.metadata['attachments']) == 2
        assert doc.metadata['attachments'][0]['filename'] == 'document.pdf'
        assert doc.metadata['attachments'][1]['filename'] == 'image.jpg'
        assert doc.metadata['has_attachments'] is True
    
    @pytest.mark.asyncio
    async def test_meeting_link_extraction(self, gmail_source):
        """Test meeting link extraction."""
        email_data = {
            'message_id': 'test_123',
            'subject': 'Meeting Invitation',
            'from': 'organizer@example.com',
            'body_text': '''
            Please join our meeting:
            Zoom: https://zoom.us/j/123456789
            Teams: https://teams.microsoft.com/l/meetup-join/19%3ameeting_123
            ''',
            'body_html': '',
            'meeting_links': [
                'https://zoom.us/j/123456789',
                'https://teams.microsoft.com/l/meetup-join/19%3ameeting_123'
            ]
        }
        
        doc = await gmail_source.process_item(email_data)
        
        assert doc.metadata['has_meeting_links'] is True
        assert len(doc.metadata['meeting_links']) == 2
        assert 'zoom.us' in doc.metadata['meeting_links'][0]
        assert 'teams.microsoft.com' in doc.metadata['meeting_links'][1]


class TestEmailMessage:
    """Test EmailMessage model."""
    
    def test_email_message_creation(self):
        """Test creating EmailMessage."""
        msg = EmailMessage(
            message_id="test_123",
            subject="Test Subject",
            sender="sender@example.com",
            recipients=["recipient1@example.com", "recipient2@example.com"],
            date=datetime.utcnow(),
            body_text="Plain text body",
            body_html="<p>HTML body</p>",
            attachments=[],
            folder="INBOX"
        )
        
        assert msg.message_id == "test_123"
        assert msg.subject == "Test Subject"
        assert msg.sender == "sender@example.com"
        assert len(msg.recipients) == 2
        assert msg.body_text == "Plain text body"
        assert msg.body_html == "<p>HTML body</p>"
        assert msg.folder == "INBOX"
    
    def test_email_message_to_dict(self):
        """Test converting EmailMessage to dictionary."""
        msg = EmailMessage(
            message_id="test_123",
            subject="Test",
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            date=datetime(2024, 1, 1, 12, 0, 0),
            body_text="Test body",
            folder="INBOX"
        )
        
        msg_dict = msg.to_dict()
        
        assert msg_dict['message_id'] == "test_123"
        assert msg_dict['subject'] == "Test"
        assert msg_dict['from'] == "sender@example.com"
        assert msg_dict['to'] == ["recipient@example.com"]
        assert msg_dict['body_text'] == "Test body"
        assert isinstance(msg_dict['date'], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])