"""Tests for Fireflies.ai integration."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import json
import aiohttp
from pathlib import Path

from vector_db_query.data_sources.fireflies import (
    FirefliesDataSource, FirefliesConfig, FirefliesTranscript
)
from vector_db_query.data_sources.models import SourceType, ProcessedDocument
from vector_db_query.data_sources.exceptions import AuthenticationError, DataSourceError


class TestFirefliesConfig:
    """Test Fireflies configuration."""
    
    def test_config_initialization(self):
        """Test FirefliesConfig initialization."""
        config = FirefliesConfig(
            api_key="test_api_key",
            webhook_secret="test_secret",
            webhook_enabled=True,
            initial_history_days=30,
            min_duration_seconds=300,
            max_duration_seconds=14400
        )
        
        assert config.api_key == "test_api_key"
        assert config.webhook_secret == "test_secret"
        assert config.webhook_enabled is True
        assert config.initial_history_days == 30
        assert config.min_duration_seconds == 300
        assert config.max_duration_seconds == 14400
    
    def test_config_validation(self):
        """Test config validation."""
        # Test missing API key
        with pytest.raises(ValueError):
            FirefliesConfig(api_key="")
        
        # Test invalid duration range
        with pytest.raises(ValueError):
            FirefliesConfig(
                api_key="test_key",
                min_duration_seconds=3600,
                max_duration_seconds=1800  # Max less than min
            )


class TestFirefliesDataSource:
    """Test Fireflies data source functionality."""
    
    @pytest.fixture
    def fireflies_config(self):
        """Create Fireflies configuration."""
        return FirefliesConfig(
            api_key="test_api_key",
            webhook_secret="test_secret",
            initial_history_days=7,
            output_dir="test_output"
        )
    
    @pytest.fixture
    def fireflies_source(self, fireflies_config):
        """Create Fireflies data source."""
        return FirefliesDataSource(fireflies_config)
    
    @pytest.fixture
    def mock_session(self):
        """Create mock aiohttp session."""
        with patch('aiohttp.ClientSession') as mock:
            yield mock
    
    @pytest.mark.asyncio
    async def test_authentication(self, fireflies_source):
        """Test authentication."""
        # Fireflies uses API key, so auth should always succeed if key is present
        result = await fireflies_source.authenticate()
        assert result is True
        
        # Test with no API key
        fireflies_source.config.api_key = ""
        result = await fireflies_source.authenticate()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_graphql_query(self, fireflies_source, mock_session):
        """Test GraphQL query execution."""
        # Mock response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'data': {
                'transcripts': [
                    {
                        'id': 'trans_123',
                        'title': 'Test Meeting',
                        'date': '2024-01-01T10:00:00Z'
                    }
                ]
            }
        })
        
        # Setup mock session
        mock_session_instance = Mock()
        mock_session_instance.post = AsyncMock(return_value=mock_response)
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        # Execute query
        query = """
        query {
            transcripts {
                id
                title
                date
            }
        }
        """
        
        result = await fireflies_source._execute_graphql_query(query)
        
        assert 'transcripts' in result
        assert len(result['transcripts']) == 1
        assert result['transcripts'][0]['id'] == 'trans_123'
    
    @pytest.mark.asyncio
    async def test_fetch_transcripts(self, fireflies_source, mock_session):
        """Test fetching transcripts."""
        # Mock GraphQL response
        mock_data = {
            'transcripts': [
                {
                    'id': 'trans_1',
                    'title': 'Meeting 1',
                    'date': '2024-01-01T10:00:00Z',
                    'duration': 1800,
                    'participants': [
                        {'name': 'John Doe', 'email': 'john@example.com'},
                        {'name': 'Jane Smith', 'email': 'jane@example.com'}
                    ],
                    'summary': 'Meeting summary',
                    'transcript_url': 'https://fireflies.ai/transcript/1'
                },
                {
                    'id': 'trans_2',
                    'title': 'Meeting 2',
                    'date': '2024-01-02T14:00:00Z',
                    'duration': 3600,
                    'participants': [
                        {'name': 'Alice', 'email': 'alice@example.com'}
                    ],
                    'summary': 'Another meeting',
                    'transcript_url': 'https://fireflies.ai/transcript/2'
                }
            ]
        }
        
        with patch.object(fireflies_source, '_execute_graphql_query', return_value=mock_data):
            transcripts = await fireflies_source._fetch_transcripts(datetime.utcnow())
            
            assert len(transcripts) == 2
            assert transcripts[0]['id'] == 'trans_1'
            assert transcripts[0]['title'] == 'Meeting 1'
            assert transcripts[1]['id'] == 'trans_2'
    
    @pytest.mark.asyncio
    async def test_process_transcript(self, fireflies_source):
        """Test transcript processing."""
        # Create mock transcript
        transcript_data = {
            'id': 'trans_123',
            'title': 'Product Planning Meeting',
            'date': '2024-01-01T10:00:00Z',
            'duration': 3600,
            'participants': [
                {'name': 'John Doe', 'email': 'john@example.com'},
                {'name': 'Jane Smith', 'email': 'jane@example.com'}
            ],
            'summary': 'Discussed Q1 product roadmap',
            'action_items': [
                'John to create design mockups',
                'Jane to prepare technical specification'
            ],
            'transcript_text': 'Full transcript text here...',
            'topics': ['product roadmap', 'Q1 planning', 'design review']
        }
        
        # Process transcript
        doc = await fireflies_source.process_item(transcript_data)
        
        assert isinstance(doc, ProcessedDocument)
        assert doc.source_id == 'trans_123'
        assert doc.title == 'Product Planning Meeting'
        assert doc.source_type == SourceType.FIREFLIES
        assert 'Discussed Q1 product roadmap' in doc.content
        assert 'Full transcript text here' in doc.content
        assert doc.metadata['duration'] == 3600
        assert len(doc.metadata['participants']) == 2
        assert len(doc.metadata['action_items']) == 2
        assert len(doc.metadata['topics']) == 3
    
    @pytest.mark.asyncio
    async def test_duration_filtering(self, fireflies_source):
        """Test filtering by meeting duration."""
        # Set duration filters
        fireflies_source.config.min_duration_seconds = 600  # 10 minutes
        fireflies_source.config.max_duration_seconds = 3600  # 1 hour
        
        # Test transcript within range
        transcript1 = {'duration': 1800}  # 30 minutes
        assert await fireflies_source._should_process_transcript(transcript1) is True
        
        # Test transcript too short
        transcript2 = {'duration': 300}  # 5 minutes
        assert await fireflies_source._should_process_transcript(transcript2) is False
        
        # Test transcript too long
        transcript3 = {'duration': 7200}  # 2 hours
        assert await fireflies_source._should_process_transcript(transcript3) is False
    
    @pytest.mark.asyncio
    async def test_platform_filtering(self, fireflies_source):
        """Test filtering by meeting platform."""
        # Set platform filters
        fireflies_source.config.platform_filters = ['zoom', 'teams']
        
        # Test allowed platform
        transcript1 = {'platform': 'zoom'}
        assert await fireflies_source._should_process_transcript(transcript1) is True
        
        # Test disallowed platform
        transcript2 = {'platform': 'webex'}
        assert await fireflies_source._should_process_transcript(transcript2) is False
        
        # Test with no platform filters (allow all)
        fireflies_source.config.platform_filters = []
        assert await fireflies_source._should_process_transcript(transcript2) is True
    
    @pytest.mark.asyncio
    async def test_user_filtering(self, fireflies_source):
        """Test filtering by participants."""
        # Set user filters
        fireflies_source.config.included_users = ['john@example.com']
        fireflies_source.config.excluded_users = ['spam@example.com']
        
        # Test included user
        transcript1 = {
            'participants': [
                {'email': 'john@example.com'},
                {'email': 'jane@example.com'}
            ]
        }
        assert await fireflies_source._should_process_transcript(transcript1) is True
        
        # Test excluded user
        transcript2 = {
            'participants': [
                {'email': 'spam@example.com'},
                {'email': 'jane@example.com'}
            ]
        }
        assert await fireflies_source._should_process_transcript(transcript2) is False
        
        # Test no included users
        transcript3 = {
            'participants': [
                {'email': 'alice@example.com'},
                {'email': 'bob@example.com'}
            ]
        }
        assert await fireflies_source._should_process_transcript(transcript3) is False
    
    @pytest.mark.asyncio
    async def test_sync_operation(self, fireflies_source, mock_session):
        """Test full sync operation."""
        # Mock transcript data
        mock_transcripts = [
            {
                'id': 'trans_1',
                'title': 'Meeting 1',
                'date': '2024-01-01T10:00:00Z',
                'duration': 1800,
                'participants': [{'name': 'John', 'email': 'john@example.com'}],
                'summary': 'Summary 1',
                'transcript_text': 'Transcript 1'
            }
        ]
        
        # Mock full transcript fetch
        with patch.object(fireflies_source, '_fetch_transcripts', return_value=mock_transcripts):
            with patch.object(fireflies_source, '_fetch_full_transcript', return_value={
                **mock_transcripts[0],
                'action_items': ['Task 1', 'Task 2'],
                'topics': ['Topic 1']
            }):
                result = await fireflies_source.sync()
                
                assert result.items_processed == 1
                assert len(result.processed_documents) == 1
                assert result.processed_documents[0].title == 'Meeting 1'
    
    @pytest.mark.asyncio
    async def test_webhook_processing(self, fireflies_source):
        """Test webhook event processing."""
        # Create webhook payload
        webhook_data = {
            'event': 'transcript.completed',
            'transcript': {
                'id': 'trans_webhook',
                'title': 'Webhook Meeting',
                'date': '2024-01-01T15:00:00Z',
                'duration': 2400,
                'participants': [{'name': 'User', 'email': 'user@example.com'}],
                'summary': 'Meeting from webhook',
                'transcript_text': 'Webhook transcript content'
            }
        }
        
        # Process webhook
        doc = await fireflies_source.process_webhook_event(webhook_data)
        
        assert isinstance(doc, ProcessedDocument)
        assert doc.source_id == 'trans_webhook'
        assert doc.title == 'Webhook Meeting'
        assert 'Meeting from webhook' in doc.content
    
    @pytest.mark.asyncio
    async def test_test_connection(self, fireflies_source, mock_session):
        """Test connection testing."""
        # Mock successful API call
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'data': {'user': {'email': 'test@example.com'}}
        })
        
        mock_session_instance = Mock()
        mock_session_instance.post = AsyncMock(return_value=mock_response)
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        result = await fireflies_source.test_connection()
        assert result is True
        
        # Test failed connection
        mock_response.status = 401
        result = await fireflies_source.test_connection()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, fireflies_source):
        """Test metrics retrieval."""
        # Set some test values
        fireflies_source._total_transcripts = 50
        fireflies_source._processed_transcripts = 45
        fireflies_source._failed_transcripts = 2
        fireflies_source._last_sync_time = datetime.utcnow()
        fireflies_source._filtered_transcripts = 3
        
        metrics = await fireflies_source.get_metrics()
        
        assert metrics['total_transcripts'] == 50
        assert metrics['processed_transcripts'] == 45
        assert metrics['failed_transcripts'] == 2
        assert metrics['filtered_transcripts'] == 3
        assert metrics['success_rate'] == 0.9
        assert 'last_sync' in metrics
        assert metrics['webhook_enabled'] is True
    
    @pytest.mark.asyncio
    async def test_error_handling(self, fireflies_source, mock_session):
        """Test error handling."""
        # Test API error
        mock_response = Mock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        
        mock_session_instance = Mock()
        mock_session_instance.post = AsyncMock(return_value=mock_response)
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        with pytest.raises(DataSourceError):
            await fireflies_source._execute_graphql_query("query { test }")
        
        # Test network error
        mock_session_instance.post = AsyncMock(side_effect=aiohttp.ClientError("Network error"))
        
        with pytest.raises(DataSourceError):
            await fireflies_source._execute_graphql_query("query { test }")


class TestFirefliesTranscript:
    """Test FirefliesTranscript model."""
    
    def test_transcript_creation(self):
        """Test creating FirefliesTranscript."""
        transcript = FirefliesTranscript(
            id="trans_123",
            title="Test Meeting",
            date=datetime(2024, 1, 1, 10, 0, 0),
            duration=3600,
            participants=["john@example.com", "jane@example.com"],
            summary="Meeting summary",
            transcript_text="Full transcript",
            action_items=["Task 1", "Task 2"],
            topics=["Topic 1", "Topic 2"],
            platform="zoom",
            meeting_url="https://zoom.us/j/123"
        )
        
        assert transcript.id == "trans_123"
        assert transcript.title == "Test Meeting"
        assert transcript.duration == 3600
        assert len(transcript.participants) == 2
        assert len(transcript.action_items) == 2
        assert len(transcript.topics) == 2
        assert transcript.platform == "zoom"
    
    def test_transcript_to_dict(self):
        """Test converting transcript to dictionary."""
        transcript = FirefliesTranscript(
            id="trans_123",
            title="Test",
            date=datetime(2024, 1, 1, 10, 0, 0),
            duration=1800,
            participants=["user@example.com"],
            summary="Summary",
            transcript_text="Text"
        )
        
        transcript_dict = transcript.to_dict()
        
        assert transcript_dict['id'] == "trans_123"
        assert transcript_dict['title'] == "Test"
        assert transcript_dict['duration'] == 1800
        assert isinstance(transcript_dict['date'], str)
        assert len(transcript_dict['participants']) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])