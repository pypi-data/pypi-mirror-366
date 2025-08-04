"""Tests for data source orchestrator."""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import tempfile
import json

from vector_db_query.data_sources.orchestrator import DataSourceOrchestrator
from vector_db_query.data_sources.models import (
    SourceType, SyncState, ProcessedDocument, SyncResult
)
from vector_db_query.data_sources.base import AbstractDataSource, DataSourceConfig
from vector_db_query.data_sources.exceptions import DataSourceError, ConfigurationError


class MockDataSource(AbstractDataSource):
    """Mock data source for testing."""
    
    def __init__(self, source_type: SourceType):
        self.source_type = source_type
        self.config = Mock(sync_interval=300)
        self.sync_called = False
        self.test_connection_result = True
        self.sync_result = SyncResult(source_type=source_type.value)
        self.metrics = {'test': 'metrics'}
    
    async def authenticate(self) -> bool:
        return True
    
    async def sync(self, since: datetime = None) -> SyncResult:
        self.sync_called = True
        return self.sync_result
    
    async def process_item(self, item):
        pass
    
    async def fetch_items(self, since: datetime = None):
        return []
    
    async def test_connection(self) -> bool:
        return self.test_connection_result
    
    async def get_metrics(self):
        return self.metrics
    
    async def cleanup(self):
        pass


class TestDataSourceOrchestrator:
    """Test orchestrator functionality."""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary configuration."""
        config = {
            'data_sources': {
                'gmail': {
                    'enabled': False,
                    'email': 'test@gmail.com'
                },
                'fireflies': {
                    'enabled': False,
                    'api_key': 'test_key'
                },
                'google_drive': {
                    'enabled': False,
                    'oauth_credentials_file': 'test.json'
                },
                'processing': {
                    'parallel_sources': True,
                    'max_concurrent_items': 10,
                    'retry_attempts': 3
                },
                'deduplication': {
                    'enabled': True,
                    'similarity_threshold': 0.95,
                    'cross_source_check': True,
                    'skip_duplicates': True
                },
                'selective_processing': {
                    'enabled': True,
                    'filter_rules': [],
                    'manual_exclusions': {
                        'gmail': [],
                        'fireflies': [],
                        'google_drive': []
                    }
                }
            }
        }
        return config
    
    @pytest.fixture
    def orchestrator(self, temp_config):
        """Create orchestrator instance."""
        with patch('vector_db_query.data_sources.orchestrator.get_config', return_value=temp_config):
            return DataSourceOrchestrator()
    
    @pytest.fixture
    def mock_sources(self):
        """Create mock data sources."""
        return {
            SourceType.GMAIL: MockDataSource(SourceType.GMAIL),
            SourceType.FIREFLIES: MockDataSource(SourceType.FIREFLIES),
            SourceType.GOOGLE_DRIVE: MockDataSource(SourceType.GOOGLE_DRIVE)
        }
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert isinstance(orchestrator.sources, dict)
        assert isinstance(orchestrator.sync_states, dict)
        assert orchestrator._running is False
        assert hasattr(orchestrator, 'deduplicator')
        assert hasattr(orchestrator, 'selective_processor')
    
    def test_register_source(self, orchestrator, mock_sources):
        """Test source registration."""
        # Register a source
        orchestrator.register_source(SourceType.GMAIL, mock_sources[SourceType.GMAIL])
        
        assert SourceType.GMAIL in orchestrator.sources
        assert orchestrator.sources[SourceType.GMAIL] == mock_sources[SourceType.GMAIL]
        
        # Check sync state initialization
        assert SourceType.GMAIL in orchestrator.sync_states
        assert isinstance(orchestrator.sync_states[SourceType.GMAIL], SyncState)
    
    @pytest.mark.asyncio
    async def test_initialize_sources_all_disabled(self, orchestrator):
        """Test source initialization when all are disabled."""
        await orchestrator.initialize_sources()
        
        # No sources should be registered when all are disabled
        assert len(orchestrator.sources) == 0
    
    @pytest.mark.asyncio
    async def test_initialize_sources_gmail_enabled(self, temp_config):
        """Test source initialization with Gmail enabled."""
        # Enable Gmail
        temp_config['data_sources']['gmail']['enabled'] = True
        
        with patch('vector_db_query.data_sources.orchestrator.get_config', return_value=temp_config):
            orchestrator = DataSourceOrchestrator()
            
            # Mock the Gmail source creation
            with patch('vector_db_query.data_sources.gmail.GmailDataSource') as mock_gmail:
                mock_instance = Mock()
                mock_gmail.return_value = mock_instance
                
                await orchestrator.initialize_sources()
                
                assert SourceType.GMAIL in orchestrator.sources
                assert orchestrator.sources[SourceType.GMAIL] == mock_instance
    
    @pytest.mark.asyncio
    async def test_sync_source(self, orchestrator, mock_sources):
        """Test syncing a single source."""
        # Register source
        source = mock_sources[SourceType.GMAIL]
        orchestrator.register_source(SourceType.GMAIL, source)
        
        # Add test documents to sync result
        source.sync_result.processed_documents = [
            ProcessedDocument(
                id="doc1",
                source_type=SourceType.GMAIL,
                source_id="gmail1",
                title="Test Email",
                content="Test content",
                processed_at=datetime.utcnow()
            )
        ]
        source.sync_result.items_processed = 1
        
        # Perform sync
        result = await orchestrator.sync_source(SourceType.GMAIL)
        
        assert source.sync_called is True
        assert result.items_processed == 1
        assert len(result.processed_documents) == 1
    
    @pytest.mark.asyncio
    async def test_sync_source_not_registered(self, orchestrator):
        """Test syncing unregistered source."""
        with pytest.raises(DataSourceError):
            await orchestrator.sync_source(SourceType.GMAIL)
    
    @pytest.mark.asyncio
    async def test_sync_source_inactive(self, orchestrator, mock_sources):
        """Test syncing inactive source."""
        # Register source and mark as inactive
        source = mock_sources[SourceType.GMAIL]
        orchestrator.register_source(SourceType.GMAIL, source)
        orchestrator.sync_states[SourceType.GMAIL].is_active = False
        
        result = await orchestrator.sync_source(SourceType.GMAIL)
        
        assert source.sync_called is False
        assert result.items_processed == 0
    
    @pytest.mark.asyncio
    async def test_sync_source_with_errors(self, orchestrator, mock_sources):
        """Test sync error handling."""
        # Register source that will fail
        source = mock_sources[SourceType.GMAIL]
        source.sync = AsyncMock(side_effect=Exception("Sync failed"))
        orchestrator.register_source(SourceType.GMAIL, source)
        
        # First few errors should not disable the source
        for i in range(4):
            with pytest.raises(Exception):
                await orchestrator.sync_source(SourceType.GMAIL)
            assert orchestrator.sync_states[SourceType.GMAIL].error_count == i + 1
            assert orchestrator.sync_states[SourceType.GMAIL].is_active is True
        
        # Fifth error should disable the source
        with pytest.raises(Exception):
            await orchestrator.sync_source(SourceType.GMAIL)
        assert orchestrator.sync_states[SourceType.GMAIL].error_count == 5
        assert orchestrator.sync_states[SourceType.GMAIL].is_active is False
    
    @pytest.mark.asyncio
    async def test_sync_all_parallel(self, orchestrator, mock_sources):
        """Test syncing all sources in parallel."""
        # Register all sources
        for source_type, source in mock_sources.items():
            orchestrator.register_source(source_type, source)
        
        # Perform sync
        results = await orchestrator.sync_all()
        
        assert len(results) == 3
        for source_type, source in mock_sources.items():
            assert source.sync_called is True
            assert source_type in results
    
    @pytest.mark.asyncio
    async def test_sync_all_sequential(self, temp_config):
        """Test syncing all sources sequentially."""
        # Disable parallel processing
        temp_config['data_sources']['processing']['parallel_sources'] = False
        
        with patch('vector_db_query.data_sources.orchestrator.get_config', return_value=temp_config):
            orchestrator = DataSourceOrchestrator()
            
            # Register mock sources
            sources = {
                SourceType.GMAIL: MockDataSource(SourceType.GMAIL),
                SourceType.FIREFLIES: MockDataSource(SourceType.FIREFLIES)
            }
            
            for source_type, source in sources.items():
                orchestrator.register_source(source_type, source)
            
            # Perform sync
            results = await orchestrator.sync_all()
            
            assert len(results) == 2
            for source in sources.values():
                assert source.sync_called is True
    
    @pytest.mark.asyncio
    async def test_deduplication_integration(self, orchestrator, mock_sources):
        """Test deduplication during sync."""
        # Register source
        source = mock_sources[SourceType.GMAIL]
        orchestrator.register_source(SourceType.GMAIL, source)
        
        # Create duplicate documents
        doc1 = ProcessedDocument(
            id="doc1",
            source_type=SourceType.GMAIL,
            source_id="gmail1",
            title="Test Email",
            content="This is test content",
            processed_at=datetime.utcnow()
        )
        
        doc2 = ProcessedDocument(
            id="doc2",
            source_type=SourceType.GMAIL,
            source_id="gmail2",
            title="Test Email",
            content="This is test content",  # Same content
            processed_at=datetime.utcnow()
        )
        
        # First sync with one document
        source.sync_result.processed_documents = [doc1]
        source.sync_result.items_processed = 1
        
        result1 = await orchestrator.sync_source(SourceType.GMAIL)
        assert result1.items_processed == 1
        
        # Second sync with duplicate
        source.sync_result.processed_documents = [doc2]
        source.sync_result.items_processed = 1
        
        result2 = await orchestrator.sync_source(SourceType.GMAIL)
        
        # Duplicate should be detected and skipped
        assert result2.items_processed == 0  # Skipped due to deduplication
        assert 'deduplication' in result2.metadata
        assert result2.metadata['deduplication']['duplicates_found'] == 1
    
    @pytest.mark.asyncio
    async def test_selective_processing_integration(self, orchestrator, mock_sources):
        """Test selective processing during sync."""
        # Add a filter rule
        orchestrator.selective_processor.add_rule({
            'name': 'Exclude Test',
            'type': 'pattern',
            'action': 'exclude',
            'pattern': '*spam*'
        })
        
        # Register source
        source = mock_sources[SourceType.GMAIL]
        orchestrator.register_source(SourceType.GMAIL, source)
        
        # Create documents
        doc1 = ProcessedDocument(
            id="doc1",
            source_type=SourceType.GMAIL,
            source_id="gmail1",
            title="Important Email",
            content="Important content",
            processed_at=datetime.utcnow()
        )
        
        doc2 = ProcessedDocument(
            id="doc2",
            source_type=SourceType.GMAIL,
            source_id="gmail2",
            title="Spam Email",
            content="This is spam content",
            processed_at=datetime.utcnow()
        )
        
        source.sync_result.processed_documents = [doc1, doc2]
        source.sync_result.items_processed = 2
        
        result = await orchestrator.sync_source(SourceType.GMAIL)
        
        # Only non-spam document should be kept
        assert result.items_processed == 1
        assert len(result.processed_documents) == 1
        assert result.processed_documents[0].id == "doc1"
        assert 'selective_processing' in result.metadata
        assert result.metadata['selective_processing']['excluded_count'] == 1
    
    @pytest.mark.asyncio
    async def test_scheduled_sync(self, orchestrator, mock_sources):
        """Test scheduled sync functionality."""
        # Register sources with short interval
        for source_type, source in mock_sources.items():
            source.config.sync_interval = 0.1  # 100ms for testing
            orchestrator.register_source(source_type, source)
        
        # Start scheduled sync
        await orchestrator.start_scheduled_sync()
        assert orchestrator._running is True
        assert len(orchestrator._sync_tasks) == 3
        
        # Wait for at least one sync cycle
        await asyncio.sleep(0.2)
        
        # Stop scheduled sync
        await orchestrator.stop_scheduled_sync()
        assert orchestrator._running is False
        assert len(orchestrator._sync_tasks) == 0
        
        # Verify syncs occurred
        for source in mock_sources.values():
            assert source.sync_called is True
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, orchestrator, mock_sources):
        """Test metrics retrieval."""
        # Register sources
        for source_type, source in mock_sources.items():
            orchestrator.register_source(source_type, source)
            # Set some sync state
            orchestrator.sync_states[source_type].last_sync_timestamp = datetime.utcnow()
        
        metrics = await orchestrator.get_metrics()
        
        assert len(metrics) == 3
        for source_type in mock_sources:
            assert source_type.value in metrics
            source_metrics = metrics[source_type.value]
            assert 'metrics' in source_metrics
            assert 'sync_state' in source_metrics
            assert source_metrics['metrics'] == {'test': 'metrics'}
    
    @pytest.mark.asyncio
    async def test_cleanup(self, orchestrator, mock_sources):
        """Test cleanup functionality."""
        # Register sources
        for source_type, source in mock_sources.items():
            source.cleanup = AsyncMock()
            orchestrator.register_source(source_type, source)
        
        # Start and stop scheduled sync
        await orchestrator.start_scheduled_sync()
        await orchestrator.cleanup()
        
        # Verify cleanup was called on all sources
        for source in mock_sources.values():
            source.cleanup.assert_called_once()
        
        # Verify scheduled sync was stopped
        assert orchestrator._running is False
    
    def test_get_deduplication_stats(self, orchestrator):
        """Test deduplication statistics."""
        stats = orchestrator.get_deduplication_stats()
        
        assert 'total_documents' in stats
        assert 'unique_documents' in stats
        assert isinstance(stats['total_documents'], int)
    
    def test_cleanup_old_duplicates(self, orchestrator):
        """Test cleaning old duplicate entries."""
        removed = orchestrator.cleanup_old_duplicates(90)
        
        assert isinstance(removed, int)
        assert removed >= 0
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, orchestrator, mock_sources):
        """Test error recovery in sync loop."""
        # Register source that fails then succeeds
        source = mock_sources[SourceType.GMAIL]
        call_count = 0
        
        async def mock_sync(since=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary error")
            return source.sync_result
        
        source.sync = mock_sync
        source.config.sync_interval = 0.1
        orchestrator.register_source(SourceType.GMAIL, source)
        
        # Start scheduled sync
        await orchestrator.start_scheduled_sync()
        
        # Wait for recovery
        await asyncio.sleep(0.3)
        
        # Stop sync
        await orchestrator.stop_scheduled_sync()
        
        # Should have attempted multiple times
        assert call_count >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])