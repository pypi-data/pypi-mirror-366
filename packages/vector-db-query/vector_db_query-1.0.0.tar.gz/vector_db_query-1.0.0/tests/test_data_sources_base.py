"""Tests for data sources base classes and models."""

import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from vector_db_query.data_sources.base import (
    AbstractDataSource, DataSourceConfig, SyncResult
)
from vector_db_query.data_sources.models import (
    SourceType, SyncState, ProcessedDocument
)
from vector_db_query.data_sources.exceptions import (
    DataSourceError, AuthenticationError, ConfigurationError
)


class MockDataSourceConfig(DataSourceConfig):
    """Mock configuration for testing."""
    
    def __init__(self, **kwargs):
        super().__init__()
        self.enabled = kwargs.get('enabled', True)
        self.sync_interval = kwargs.get('sync_interval', 300)
        self.knowledge_base_folder = kwargs.get('knowledge_base_folder', 'test_kb')
        self.test_option = kwargs.get('test_option', 'default')


class MockDataSource(AbstractDataSource):
    """Mock data source for testing."""
    
    def __init__(self, config: MockDataSourceConfig):
        self.config = config
        self.authenticated = False
        self.test_connection_result = True
        self.metrics = {
            'total_items': 100,
            'processed_items': 50,
            'failed_items': 5
        }
        self.sync_items = []
    
    async def authenticate(self) -> bool:
        """Mock authentication."""
        self.authenticated = True
        return True
    
    async def sync(self, since: datetime = None) -> SyncResult:
        """Mock sync operation."""
        if not self.authenticated:
            raise AuthenticationError("Not authenticated")
        
        result = SyncResult(source_type=SourceType.GMAIL.value)
        
        for i, item in enumerate(self.sync_items):
            doc = ProcessedDocument(
                id=f"doc_{i}",
                source_type=SourceType.GMAIL,
                source_id=f"source_{i}",
                title=item.get('title', f"Document {i}"),
                content=item.get('content', f"Content {i}"),
                processed_at=datetime.utcnow(),
                metadata=item.get('metadata', {})
            )
            result.processed_documents.append(doc)
            result.items_processed += 1
        
        return result
    
    async def process_item(self, item: Any) -> ProcessedDocument:
        """Mock item processing."""
        return ProcessedDocument(
            id="test_doc",
            source_type=SourceType.GMAIL,
            source_id="test_source",
            title="Test Document",
            content="Test content",
            processed_at=datetime.utcnow()
        )
    
    async def fetch_items(self, since: datetime = None) -> List[Any]:
        """Mock item fetching."""
        return self.sync_items
    
    async def test_connection(self) -> bool:
        """Mock connection test."""
        return self.test_connection_result
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Mock metrics retrieval."""
        return self.metrics
    
    async def cleanup(self):
        """Mock cleanup."""
        self.authenticated = False


class TestDataSourceModels:
    """Test data source models."""
    
    def test_source_type_enum(self):
        """Test SourceType enum."""
        assert SourceType.GMAIL.value == "gmail"
        assert SourceType.FIREFLIES.value == "fireflies"
        assert SourceType.GOOGLE_DRIVE.value == "google_drive"
    
    def test_sync_state_initialization(self):
        """Test SyncState initialization."""
        state = SyncState(source_type=SourceType.GMAIL)
        
        assert state.source_type == SourceType.GMAIL
        assert state.last_sync_timestamp is None
        assert state.is_active is True
        assert state.error_count == 0
        assert state.last_error is None
        assert state.metadata == {}
    
    def test_sync_state_error_handling(self):
        """Test SyncState error handling."""
        state = SyncState(source_type=SourceType.GMAIL)
        
        # Record errors
        state.record_error("First error")
        assert state.error_count == 1
        assert state.last_error == "First error"
        
        state.record_error("Second error")
        assert state.error_count == 2
        assert state.last_error == "Second error"
        
        # Clear errors
        state.clear_errors()
        assert state.error_count == 0
        assert state.last_error is None
    
    def test_processed_document(self):
        """Test ProcessedDocument model."""
        doc = ProcessedDocument(
            id="test_123",
            source_type=SourceType.FIREFLIES,
            source_id="fireflies_456",
            title="Test Meeting",
            content="Meeting transcript content",
            processed_at=datetime.utcnow(),
            metadata={
                "duration": 3600,
                "participants": ["user1", "user2"]
            }
        )
        
        assert doc.id == "test_123"
        assert doc.source_type == SourceType.FIREFLIES
        assert doc.source_id == "fireflies_456"
        assert doc.title == "Test Meeting"
        assert doc.content == "Meeting transcript content"
        assert doc.metadata["duration"] == 3600
        assert len(doc.metadata["participants"]) == 2
    
    def test_sync_result(self):
        """Test SyncResult model."""
        result = SyncResult(source_type="gmail")
        
        assert result.source_type == "gmail"
        assert result.items_processed == 0
        assert result.items_failed == 0
        assert result.errors == []
        assert result.processed_documents == []
        
        # Add processed document
        doc = ProcessedDocument(
            id="doc1",
            source_type=SourceType.GMAIL,
            source_id="gmail1",
            title="Email 1",
            content="Email content",
            processed_at=datetime.utcnow()
        )
        result.processed_documents.append(doc)
        result.items_processed += 1
        
        assert len(result.processed_documents) == 1
        assert result.items_processed == 1
        
        # Add error
        result.errors.append("Failed to process item")
        result.items_failed += 1
        
        assert len(result.errors) == 1
        assert result.items_failed == 1


class TestAbstractDataSource:
    """Test AbstractDataSource functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration."""
        return MockDataSourceConfig(
            enabled=True,
            sync_interval=300,
            test_option="test_value"
        )
    
    @pytest.fixture
    def mock_source(self, mock_config):
        """Create mock data source."""
        return MockDataSource(mock_config)
    
    @pytest.mark.asyncio
    async def test_authentication(self, mock_source):
        """Test authentication."""
        assert mock_source.authenticated is False
        
        result = await mock_source.authenticate()
        assert result is True
        assert mock_source.authenticated is True
    
    @pytest.mark.asyncio
    async def test_sync_without_auth(self, mock_source):
        """Test sync without authentication."""
        with pytest.raises(AuthenticationError):
            await mock_source.sync()
    
    @pytest.mark.asyncio
    async def test_sync_with_items(self, mock_source):
        """Test sync with items."""
        # Authenticate first
        await mock_source.authenticate()
        
        # Add test items
        mock_source.sync_items = [
            {"title": "Item 1", "content": "Content 1"},
            {"title": "Item 2", "content": "Content 2"},
            {"title": "Item 3", "content": "Content 3"}
        ]
        
        # Perform sync
        result = await mock_source.sync()
        
        assert result.items_processed == 3
        assert len(result.processed_documents) == 3
        assert result.processed_documents[0].title == "Item 1"
        assert result.processed_documents[1].title == "Item 2"
        assert result.processed_documents[2].title == "Item 3"
    
    @pytest.mark.asyncio
    async def test_sync_with_since_parameter(self, mock_source):
        """Test sync with since parameter."""
        await mock_source.authenticate()
        
        since_date = datetime.utcnow()
        result = await mock_source.sync(since=since_date)
        
        assert isinstance(result, SyncResult)
    
    @pytest.mark.asyncio
    async def test_test_connection(self, mock_source):
        """Test connection testing."""
        # Test successful connection
        result = await mock_source.test_connection()
        assert result is True
        
        # Test failed connection
        mock_source.test_connection_result = False
        result = await mock_source.test_connection()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, mock_source):
        """Test metrics retrieval."""
        metrics = await mock_source.get_metrics()
        
        assert metrics['total_items'] == 100
        assert metrics['processed_items'] == 50
        assert metrics['failed_items'] == 5
    
    @pytest.mark.asyncio
    async def test_cleanup(self, mock_source):
        """Test cleanup."""
        # Authenticate first
        await mock_source.authenticate()
        assert mock_source.authenticated is True
        
        # Cleanup
        await mock_source.cleanup()
        assert mock_source.authenticated is False


class TestDataSourceConfig:
    """Test DataSourceConfig functionality."""
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        config = MockDataSourceConfig(
            enabled=True,
            sync_interval=600,
            test_option="custom_value"
        )
        
        assert config.enabled is True
        assert config.sync_interval == 600
        assert config.test_option == "custom_value"
    
    def test_config_defaults(self):
        """Test configuration defaults."""
        config = MockDataSourceConfig()
        
        assert config.enabled is True
        assert config.sync_interval == 300
        assert config.test_option == "default"


class TestDataSourceExceptions:
    """Test data source exceptions."""
    
    def test_data_source_error(self):
        """Test DataSourceError."""
        error = DataSourceError("Test error")
        assert str(error) == "Test error"
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Auth failed")
        assert str(error) == "Auth failed"
        assert isinstance(error, DataSourceError)
    
    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Config invalid")
        assert str(error) == "Config invalid"
        assert isinstance(error, DataSourceError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])