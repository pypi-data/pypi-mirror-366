"""Tests for Google Drive integration."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
from pathlib import Path

from vector_db_query.data_sources.googledrive import (
    GoogleDriveDataSource, GoogleDriveConfig, DriveFile
)
from vector_db_query.data_sources.models import SourceType, ProcessedDocument
from vector_db_query.data_sources.exceptions import AuthenticationError, DataSourceError


class TestGoogleDriveConfig:
    """Test Google Drive configuration."""
    
    def test_config_initialization(self):
        """Test GoogleDriveConfig initialization."""
        config = GoogleDriveConfig(
            oauth_credentials_file="creds.json",
            oauth_token_file="token.json",
            search_patterns=["Notes by Gemini", "Meeting Notes"],
            folder_ids=["folder_123", "folder_456"],
            initial_history_days=30,
            knowledge_base_folder="kb/gdrive"
        )
        
        assert config.oauth_credentials_file == "creds.json"
        assert config.oauth_token_file == "token.json"
        assert config.search_patterns == ["Notes by Gemini", "Meeting Notes"]
        assert config.folder_ids == ["folder_123", "folder_456"]
        assert config.initial_history_days == 30
        assert config.knowledge_base_folder == "kb/gdrive"
    
    def test_config_from_config(self):
        """Test creating config from dictionary."""
        config_dict = {
            "oauth_credentials_file": "creds.json",
            "search_patterns": ["Notes by Gemini"],
            "folder_ids": [],
            "initial_history_days": 7
        }
        
        config = GoogleDriveConfig.from_config(config_dict)
        
        assert config.oauth_credentials_file == "creds.json"
        assert config.search_patterns == ["Notes by Gemini"]
        assert config.folder_ids == []
        assert config.initial_history_days == 7
    
    def test_config_validation(self):
        """Test config validation."""
        # Test missing credentials file
        with pytest.raises(ValueError):
            GoogleDriveConfig(oauth_credentials_file="")
        
        # Test empty search patterns
        with pytest.raises(ValueError):
            GoogleDriveConfig(
                oauth_credentials_file="creds.json",
                search_patterns=[]
            )


class TestGoogleDriveDataSource:
    """Test Google Drive data source functionality."""
    
    @pytest.fixture
    def drive_config(self):
        """Create Google Drive configuration."""
        return GoogleDriveConfig(
            oauth_credentials_file="test_creds.json",
            oauth_token_file="test_token.json",
            search_patterns=["Notes by Gemini"],
            initial_history_days=7,
            knowledge_base_folder="test_kb"
        )
    
    @pytest.fixture
    def drive_source(self, drive_config):
        """Create Google Drive data source."""
        return GoogleDriveDataSource(drive_config)
    
    @pytest.fixture
    def mock_oauth(self):
        """Create mock OAuth flow."""
        with patch('google_auth_oauthlib.flow.InstalledAppFlow') as mock:
            yield mock
    
    @pytest.fixture
    def mock_drive_service(self):
        """Create mock Google Drive service."""
        with patch('googleapiclient.discovery.build') as mock:
            yield mock
    
    @pytest.mark.asyncio
    async def test_authentication_with_existing_token(self, drive_source):
        """Test authentication with existing token."""
        # Mock existing token
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = json.dumps({
                    'access_token': 'test_token',
                    'refresh_token': 'refresh_token',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'client_id': 'test_client',
                    'client_secret': 'test_secret'
                })
                
                with patch('google.oauth2.credentials.Credentials') as mock_creds:
                    mock_creds.return_value.valid = True
                    
                    with patch('googleapiclient.discovery.build') as mock_build:
                        mock_build.return_value = Mock()
                        
                        result = await drive_source.authenticate()
                        assert result is True
    
    @pytest.mark.asyncio
    async def test_authentication_new_flow(self, drive_source, mock_oauth):
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
                with patch('googleapiclient.discovery.build') as mock_build:
                    mock_build.return_value = Mock()
                    
                    result = await drive_source.authenticate()
                    assert result is True
    
    @pytest.mark.asyncio
    async def test_search_files(self, drive_source, mock_drive_service):
        """Test searching files in Drive."""
        # Mock Drive service
        mock_service = Mock()
        mock_files = Mock()
        
        # Mock search results
        mock_files.list.return_value.execute.return_value = {
            'files': [
                {
                    'id': 'file_1',
                    'name': 'Notes by Gemini - Meeting 1',
                    'mimeType': 'application/vnd.google-apps.document',
                    'modifiedTime': '2024-01-01T10:00:00Z',
                    'size': '1024'
                },
                {
                    'id': 'file_2',
                    'name': 'Notes by Gemini - Meeting 2',
                    'mimeType': 'application/vnd.google-apps.document',
                    'modifiedTime': '2024-01-02T14:00:00Z',
                    'size': '2048'
                }
            ],
            'nextPageToken': None
        }
        
        mock_service.files.return_value = mock_files
        drive_source.service = mock_service
        
        # Search files
        files = await drive_source._search_files("Notes by Gemini", datetime.utcnow())
        
        assert len(files) == 2
        assert files[0]['id'] == 'file_1'
        assert files[0]['name'] == 'Notes by Gemini - Meeting 1'
        assert files[1]['id'] == 'file_2'
    
    @pytest.mark.asyncio
    async def test_download_file_content(self, drive_source, mock_drive_service):
        """Test downloading file content."""
        # Mock Drive service
        mock_service = Mock()
        mock_files = Mock()
        
        # Mock export for Google Docs
        mock_files.export.return_value.execute.return_value = b"# Meeting Notes\n\nContent of the meeting..."
        
        # Mock get_media for regular files
        mock_request = Mock()
        mock_request.execute.return_value = b"File content"
        mock_files.get_media.return_value = mock_request
        
        mock_service.files.return_value = mock_files
        drive_source.service = mock_service
        
        # Test Google Docs export
        content = await drive_source._download_file_content(
            'file_1',
            'application/vnd.google-apps.document'
        )
        assert content == "# Meeting Notes\n\nContent of the meeting..."
        
        # Test regular file download
        content = await drive_source._download_file_content(
            'file_2',
            'application/pdf'
        )
        assert content == "File content"
    
    @pytest.mark.asyncio
    async def test_process_file(self, drive_source):
        """Test file processing."""
        # Create mock file
        file_data = {
            'id': 'file_123',
            'name': 'Notes by Gemini - Product Meeting',
            'mimeType': 'application/vnd.google-apps.document',
            'modifiedTime': '2024-01-01T10:00:00Z',
            'size': '2048',
            'content': '''# Product Meeting Notes
            
            Date: January 1, 2024
            Participants: John, Jane, Alice
            
            ## Agenda
            1. Q1 Product Roadmap
            2. Feature Prioritization
            3. Timeline Discussion
            
            ## Action Items
            - John: Create feature specifications
            - Jane: Update project timeline
            - Alice: Schedule follow-up meetings
            '''
        }
        
        # Process file
        doc = await drive_source.process_item(file_data)
        
        assert isinstance(doc, ProcessedDocument)
        assert doc.source_id == 'file_123'
        assert doc.title == 'Notes by Gemini - Product Meeting'
        assert doc.source_type == SourceType.GOOGLE_DRIVE
        assert 'Product Meeting Notes' in doc.content
        assert 'Q1 Product Roadmap' in doc.content
        assert doc.metadata['mime_type'] == 'application/vnd.google-apps.document'
        assert doc.metadata['file_size'] == '2048'
    
    @pytest.mark.asyncio
    async def test_gemini_transcript_detection(self, drive_source):
        """Test Gemini transcript detection and parsing."""
        # Create Gemini transcript content
        gemini_content = '''# Notes by Gemini
        
        Meeting: Product Strategy Session
        Date: January 1, 2024
        Duration: 45 minutes
        
        ## Participants
        - John Doe (Product Manager)
        - Jane Smith (Engineering Lead)
        - Alice Johnson (Design Lead)
        
        ## Key Points Discussed
        
        ### Product Roadmap
        - Q1 focus on mobile app improvements
        - New feature rollout planned for February
        - User feedback integration process
        
        ### Technical Considerations
        - API performance optimization needed
        - Database migration scheduled for end of January
        - Security audit findings review
        
        ## Action Items
        1. John to finalize feature specifications by January 15
        2. Jane to create technical implementation plan
        3. Alice to prepare design mockups for review
        
        ## Next Steps
        - Follow-up meeting scheduled for January 8
        - Weekly progress updates via email
        '''
        
        file_data = {
            'id': 'gemini_123',
            'name': 'Notes by Gemini - Product Strategy',
            'content': gemini_content,
            'mimeType': 'application/vnd.google-apps.document',
            'modifiedTime': '2024-01-01T15:00:00Z'
        }
        
        doc = await drive_source.process_item(file_data)
        
        assert 'is_gemini_transcript' in doc.metadata
        assert doc.metadata['is_gemini_transcript'] is True
        assert 'meeting_date' in doc.metadata
        assert 'participants' in doc.metadata
        assert len(doc.metadata['participants']) == 3
        assert 'action_items' in doc.metadata
        assert len(doc.metadata['action_items']) == 3
    
    @pytest.mark.asyncio
    async def test_folder_filtering(self, drive_source, mock_drive_service):
        """Test filtering by folder IDs."""
        # Set folder filters
        drive_source.config.folder_ids = ['folder_123']
        
        # Mock Drive service
        mock_service = Mock()
        mock_files = Mock()
        
        # Mock search with folder filter
        mock_files.list.return_value.execute.return_value = {
            'files': [
                {
                    'id': 'file_1',
                    'name': 'Notes by Gemini',
                    'parents': ['folder_123']
                }
            ]
        }
        
        mock_service.files.return_value = mock_files
        drive_source.service = mock_service
        
        files = await drive_source._search_files("Notes by Gemini", None)
        
        # Verify folder filter was applied in query
        call_args = mock_files.list.call_args
        assert "'folder_123' in parents" in call_args[1]['q']
    
    @pytest.mark.asyncio
    async def test_sync_operation(self, drive_source, mock_drive_service):
        """Test full sync operation."""
        # Mock Drive service
        mock_service = Mock()
        mock_files = Mock()
        
        # Mock file list
        mock_files.list.return_value.execute.return_value = {
            'files': [
                {
                    'id': 'file_1',
                    'name': 'Notes by Gemini - Meeting',
                    'mimeType': 'application/vnd.google-apps.document',
                    'modifiedTime': '2024-01-01T10:00:00Z'
                }
            ]
        }
        
        # Mock file content
        mock_files.export.return_value.execute.return_value = b"Meeting content"
        
        mock_service.files.return_value = mock_files
        drive_source.service = mock_service
        
        # Perform sync
        result = await drive_source.sync()
        
        assert result.items_processed == 1
        assert len(result.processed_documents) == 1
        assert result.processed_documents[0].title == 'Notes by Gemini - Meeting'
    
    @pytest.mark.asyncio
    async def test_shared_drives(self, drive_source, mock_drive_service):
        """Test including shared drives in search."""
        drive_source.config.include_shared_drives = True
        
        # Mock Drive service
        mock_service = Mock()
        mock_files = Mock()
        
        mock_files.list.return_value.execute.return_value = {'files': []}
        mock_service.files.return_value = mock_files
        drive_source.service = mock_service
        
        await drive_source._search_files("test", None)
        
        # Verify shared drives parameters
        call_args = mock_files.list.call_args[1]
        assert call_args['supportsAllDrives'] is True
        assert call_args['includeItemsFromAllDrives'] is True
    
    @pytest.mark.asyncio
    async def test_test_connection(self, drive_source, mock_drive_service):
        """Test connection testing."""
        # Mock successful Drive service
        mock_service = Mock()
        mock_about = Mock()
        mock_about.get.return_value.execute.return_value = {
            'user': {'emailAddress': 'test@example.com'}
        }
        mock_service.about.return_value = mock_about
        drive_source.service = mock_service
        
        result = await drive_source.test_connection()
        assert result is True
        
        # Test failed connection
        mock_about.get.return_value.execute.side_effect = Exception("API Error")
        result = await drive_source.test_connection()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, drive_source):
        """Test metrics retrieval."""
        # Set test values
        drive_source._total_files = 100
        drive_source._processed_files = 90
        drive_source._failed_files = 5
        drive_source._gemini_transcripts = 50
        drive_source._last_sync_time = datetime.utcnow()
        
        metrics = await drive_source.get_metrics()
        
        assert metrics['total_files'] == 100
        assert metrics['processed_files'] == 90
        assert metrics['failed_files'] == 5
        assert metrics['gemini_transcripts'] == 50
        assert metrics['success_rate'] == 0.9
        assert 'last_sync' in metrics
        assert metrics['search_patterns'] == ["Notes by Gemini"]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, drive_source, mock_drive_service):
        """Test error handling."""
        # Mock Drive service with errors
        mock_service = Mock()
        mock_files = Mock()
        
        # Test API error
        mock_files.list.return_value.execute.side_effect = Exception("API Error")
        mock_service.files.return_value = mock_files
        drive_source.service = mock_service
        
        with pytest.raises(DataSourceError):
            await drive_source._search_files("test", None)
        
        # Test download error
        mock_files.list.return_value.execute.side_effect = None
        mock_files.list.return_value.execute.return_value = {'files': []}
        mock_files.export.return_value.execute.side_effect = Exception("Download failed")
        
        content = await drive_source._download_file_content('file_1', 'application/vnd.google-apps.document')
        assert content == ""  # Should return empty string on error


class TestDriveFile:
    """Test DriveFile model."""
    
    def test_drive_file_creation(self):
        """Test creating DriveFile."""
        file = DriveFile(
            id="file_123",
            name="Test Document",
            mime_type="application/vnd.google-apps.document",
            size=2048,
            modified_time=datetime(2024, 1, 1, 10, 0, 0),
            created_time=datetime(2023, 12, 1, 10, 0, 0),
            parents=["folder_123"],
            web_view_link="https://docs.google.com/document/d/file_123",
            is_gemini_transcript=True
        )
        
        assert file.id == "file_123"
        assert file.name == "Test Document"
        assert file.mime_type == "application/vnd.google-apps.document"
        assert file.size == 2048
        assert file.is_gemini_transcript is True
        assert len(file.parents) == 1
    
    def test_drive_file_to_dict(self):
        """Test converting DriveFile to dictionary."""
        file = DriveFile(
            id="file_123",
            name="Test",
            mime_type="text/plain",
            modified_time=datetime(2024, 1, 1, 10, 0, 0)
        )
        
        file_dict = file.to_dict()
        
        assert file_dict['id'] == "file_123"
        assert file_dict['name'] == "Test"
        assert file_dict['mimeType'] == "text/plain"
        assert isinstance(file_dict['modifiedTime'], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])