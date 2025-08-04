"""Tests for email reader functionality."""

import pytest
from pathlib import Path
import tempfile
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mailbox
from datetime import datetime

from vector_db_query.document_processor.email_reader import EmailReader
from vector_db_query.document_processor.exceptions import DocumentProcessingError


class TestEmailReader:
    """Test email reading functionality."""
    
    @pytest.fixture
    def reader(self):
        """Create EmailReader instance."""
        return EmailReader()
    
    @pytest.fixture
    def sample_eml(self):
        """Create a sample .eml file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.eml', mode='w', delete=False) as tmp:
            # Create a simple email
            msg = MIMEMultipart()
            msg['From'] = 'sender@example.com'
            msg['To'] = 'recipient@example.com'
            msg['Subject'] = 'Test Email'
            msg['Date'] = email.utils.formatdate()
            msg['Message-ID'] = '<test123@example.com>'
            
            # Add body
            body = MIMEText('This is a test email body.\n\nWith multiple paragraphs.')
            msg.attach(body)
            
            # Write to file
            tmp.write(msg.as_string())
            tmp.flush()
            
            yield tmp.name
        
        # Cleanup
        Path(tmp.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def html_eml(self):
        """Create an email with HTML content."""
        with tempfile.NamedTemporaryFile(suffix='.eml', mode='w', delete=False) as tmp:
            msg = MIMEMultipart('alternative')
            msg['From'] = 'sender@example.com'
            msg['To'] = 'recipient@example.com'
            msg['Subject'] = 'HTML Email Test'
            
            # Plain text part
            text_part = MIMEText('This is plain text version.', 'plain')
            msg.attach(text_part)
            
            # HTML part
            html_content = '''
            <html>
                <body>
                    <h1>HTML Email</h1>
                    <p>This is <b>HTML</b> content with <a href="http://example.com">links</a>.</p>
                    <ul>
                        <li>Item 1</li>
                        <li>Item 2</li>
                    </ul>
                </body>
            </html>
            '''
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            tmp.write(msg.as_string())
            tmp.flush()
            
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def email_with_attachments(self):
        """Create an email with attachments."""
        with tempfile.NamedTemporaryFile(suffix='.eml', mode='wb', delete=False) as tmp:
            msg = MIMEMultipart()
            msg['From'] = 'sender@example.com'
            msg['To'] = 'recipient@example.com'
            msg['Subject'] = 'Email with Attachments'
            
            # Body
            msg.attach(MIMEText('This email has attachments.'))
            
            # Text attachment
            text_attach = MIMEText('This is a text attachment content.')
            text_attach.add_header('Content-Disposition', 'attachment', filename='document.txt')
            msg.attach(text_attach)
            
            # Binary attachment (simulated)
            binary_attach = MIMEBase('application', 'octet-stream')
            binary_attach.set_payload(b'Binary data here')
            encoders.encode_base64(binary_attach)
            binary_attach.add_header('Content-Disposition', 'attachment', filename='file.pdf')
            msg.attach(binary_attach)
            
            tmp.write(msg.as_bytes())
            tmp.flush()
            
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def thread_email(self):
        """Create an email that's part of a thread."""
        with tempfile.NamedTemporaryFile(suffix='.eml', mode='w', delete=False) as tmp:
            msg = MIMEText('This is a reply in a thread.')
            msg['From'] = 'sender@example.com'
            msg['To'] = 'recipient@example.com'
            msg['Subject'] = 'Re: Re: Original Thread Topic'
            msg['In-Reply-To'] = '<original123@example.com>'
            msg['References'] = '<original123@example.com> <reply1@example.com>'
            
            tmp.write(msg.as_string())
            tmp.flush()
            
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def sample_mbox(self):
        """Create a sample .mbox file with multiple emails."""
        with tempfile.NamedTemporaryFile(suffix='.mbox', delete=False) as tmp:
            mbox = mailbox.mbox(tmp.name)
            
            # Add first email
            msg1 = email.message_from_string(
                'From: user1@example.com\n'
                'To: user2@example.com\n'
                'Subject: First Email\n\n'
                'This is the first email in the mbox.'
            )
            mbox.add(msg1)
            
            # Add second email
            msg2 = email.message_from_string(
                'From: user2@example.com\n'
                'To: user1@example.com\n'
                'Subject: Second Email\n\n'
                'This is the second email in the mbox.'
            )
            mbox.add(msg2)
            
            # Add third email with HTML
            msg3 = MIMEMultipart('alternative')
            msg3['From'] = 'user3@example.com'
            msg3['To'] = 'user1@example.com'
            msg3['Subject'] = 'Third Email with HTML'
            msg3.attach(MIMEText('Plain text version', 'plain'))
            msg3.attach(MIMEText('<p>HTML version</p>', 'html'))
            mbox.add(msg3)
            
            mbox.close()
            
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_simple_eml(self, reader, sample_eml):
        """Test reading a simple .eml file."""
        result = reader.read(sample_eml)
        
        assert len(result) > 0
        assert 'sender@example.com' in result
        assert 'recipient@example.com' in result
        assert 'Test Email' in result
        assert 'This is a test email body.' in result
        assert 'With multiple paragraphs.' in result
    
    def test_read_html_email(self, reader, html_eml):
        """Test reading an email with HTML content."""
        result = reader.read(html_eml)
        
        assert len(result) > 0
        # Should convert HTML to readable text
        assert 'HTML Email' in result
        # html2text converts <b>HTML</b> to **HTML**
        assert '**HTML**' in result
        assert 'Item 1' in result
        assert 'Item 2' in result
        # Links should be preserved
        assert 'http://example.com' in result
    
    def test_read_with_attachments(self, reader):
        """Test reading email with attachments."""
        reader.include_attachments = True
        
        with tempfile.NamedTemporaryFile(suffix='.eml', mode='wb', delete=False) as tmp:
            msg = MIMEMultipart()
            msg['From'] = 'sender@example.com'
            msg['To'] = 'recipient@example.com'
            msg['Subject'] = 'Test with Attachments'
            
            msg.attach(MIMEText('Email body'))
            
            # Add attachment
            attach = MIMEText('Attachment content')
            attach.add_header('Content-Disposition', 'attachment', filename='test.txt')
            msg.attach(attach)
            
            tmp.write(msg.as_bytes())
            tmp.flush()
            
            try:
                result = reader.read(tmp.name)
                assert len(result) > 0
                assert 'Attachments:' in result
                assert 'test.txt' in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_without_attachments(self, reader, email_with_attachments):
        """Test reading email without including attachment details."""
        reader.include_attachments = False
        
        result = reader.read(email_with_attachments)
        assert len(result) > 0
        assert 'This email has attachments.' in result
        assert 'Attachments:' not in result
    
    def test_thread_detection(self, reader, thread_email):
        """Test thread information detection."""
        reader.detect_threads = True
        
        result = reader.read(thread_email)
        assert len(result) > 0
        assert 'Thread Info:' in result
        assert 'In-Reply-To:' in result
        assert 'Thread References:' in result
        assert 'Original Thread Topic' in result
    
    def test_read_mbox(self, reader, sample_mbox):
        """Test reading .mbox file with multiple emails."""
        result = reader.read(sample_mbox)
        
        assert len(result) > 0
        # Should contain all three emails
        assert 'Email 1' in result
        assert 'Email 2' in result
        assert 'Email 3' in result
        assert 'First Email' in result
        assert 'Second Email' in result
        assert 'Third Email with HTML' in result
        # Check email separator is used
        assert reader.email_separator in result
    
    def test_header_inclusion(self, reader, sample_eml):
        """Test including/excluding headers."""
        # With headers
        reader.include_headers = True
        result_with = reader.read(sample_eml)
        assert 'From: sender@example.com' in result_with
        assert 'Subject: Test Email' in result_with
        
        # Without headers
        reader.include_headers = False
        result_without = reader.read(sample_eml)
        # Body should still be there
        assert 'This is a test email body.' in result_without
        # But not formatted headers
        assert 'From: sender@example.com' not in result_without
    
    def test_content_sanitization(self, reader):
        """Test content sanitization."""
        reader.sanitize_content = True
        
        with tempfile.NamedTemporaryFile(suffix='.eml', mode='w', delete=False) as tmp:
            msg = MIMEText(
                'Email with sensitive data: 1234-5678-9012-3456 and SSN: 123-45-6789'
            )
            msg['From'] = 'sender@example.com'
            msg['To'] = 'recipient@example.com'
            msg['Subject'] = 'Sensitive'
            
            tmp.write(msg.as_string())
            tmp.flush()
            
            try:
                result = reader.read(tmp.name)
                assert '[REDACTED-CC]' in result
                assert '[REDACTED-SSN]' in result
                assert '1234-5678-9012-3456' not in result
                assert '123-45-6789' not in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_malformed_email(self, reader):
        """Test handling of malformed emails."""
        with tempfile.NamedTemporaryFile(suffix='.eml', mode='w', delete=False) as tmp:
            # Write malformed email content
            tmp.write('This is not a valid email format\nJust some text')
            tmp.flush()
            
            try:
                # Should still try to extract what it can
                result = reader.read(tmp.name)
                assert len(result) > 0
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_empty_mbox(self, reader):
        """Test reading empty .mbox file."""
        with tempfile.NamedTemporaryFile(suffix='.mbox', delete=False) as tmp:
            # Create empty mbox
            mbox = mailbox.mbox(tmp.name)
            mbox.close()
            
            try:
                result = reader.read(tmp.name)
                assert 'No readable emails found' in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_nonexistent_file(self, reader):
        """Test reading a non-existent file."""
        with pytest.raises(DocumentProcessingError):
            reader.read("nonexistent.eml")
    
    def test_read_invalid_extension(self, reader):
        """Test reading file with invalid extension."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'Not an email')
            tmp.flush()
            
            try:
                with pytest.raises(DocumentProcessingError) as exc_info:
                    reader.read(tmp.name)
                assert 'Unsupported email format' in str(exc_info.value)
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_supports_extension(self, reader):
        """Test extension support checking."""
        assert reader.supports_extension('.eml')
        assert reader.supports_extension('.EML')
        assert reader.supports_extension('eml')
        assert reader.supports_extension('.mbox')
        assert reader.supports_extension('.MBOX')
        assert not reader.supports_extension('.msg')
        assert not reader.supports_extension('.txt')
    
    def test_multipart_mixed(self, reader):
        """Test reading multipart/mixed emails."""
        with tempfile.NamedTemporaryFile(suffix='.eml', mode='wb', delete=False) as tmp:
            msg = MIMEMultipart('mixed')
            msg['From'] = 'sender@example.com'
            msg['To'] = 'recipient@example.com'
            msg['Subject'] = 'Mixed Content'
            
            # Text part
            msg.attach(MIMEText('Main message'))
            
            # Another text part
            msg.attach(MIMEText('Additional info'))
            
            tmp.write(msg.as_bytes())
            tmp.flush()
            
            try:
                result = reader.read(tmp.name)
                assert 'Main message' in result
                assert 'Additional info' in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)