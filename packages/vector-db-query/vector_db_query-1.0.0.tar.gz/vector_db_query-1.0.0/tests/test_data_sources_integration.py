"""Integration tests for data sources."""

import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json
import os

from vector_db_query.data_sources.orchestrator import DataSourceOrchestrator
from vector_db_query.data_sources.models import SourceType
from vector_db_query.data_sources.gmail import GmailDataSource, GmailConfig
from vector_db_query.data_sources.fireflies import FirefliesDataSource, FirefliesConfig
from vector_db_query.data_sources.googledrive import GoogleDriveDataSource, GoogleDriveConfig
from vector_db_query.utils.config import get_config


@pytest.mark.integration
class TestDataSourcesIntegration:
    """Integration tests for data sources.
    
    Note: These tests require proper credentials and configuration to run.
    They are marked with @pytest.mark.integration and can be skipped in CI.
    """
    
    @pytest.fixture
    def integration_config(self):
        """Load integration test configuration."""
        # Check if integration config exists
        config_path = Path("tests/integration_config.json")
        if not config_path.exists():
            pytest.skip("Integration config not found. Create tests/integration_config.json to run integration tests.")
        
        with open(config_path) as f:
            return json.load(f)
    
    @pytest.fixture
    async def orchestrator(self, integration_config):
        """Create orchestrator with test configuration."""
        # Create temporary config
        test_config = {
            'data_sources': integration_config.get('data_sources', {})
        }
        
        # Create orchestrator
        orchestrator = DataSourceOrchestrator()
        
        # Manually configure sources based on test config
        if test_config['data_sources'].get('gmail', {}).get('enabled'):
            gmail_config = GmailConfig.from_dict(test_config['data_sources']['gmail'])
            gmail_source = GmailDataSource(gmail_config)
            orchestrator.register_source(SourceType.GMAIL, gmail_source)
        
        if test_config['data_sources'].get('fireflies', {}).get('enabled'):
            fireflies_config = FirefliesConfig(**test_config['data_sources']['fireflies'])
            fireflies_source = FirefliesDataSource(fireflies_config)
            orchestrator.register_source(SourceType.FIREFLIES, fireflies_source)
        
        if test_config['data_sources'].get('google_drive', {}).get('enabled'):
            drive_config = GoogleDriveConfig.from_config(test_config['data_sources']['google_drive'])
            drive_source = GoogleDriveDataSource(drive_config)
            orchestrator.register_source(SourceType.GOOGLE_DRIVE, drive_source)
        
        yield orchestrator
        
        # Cleanup
        await orchestrator.cleanup()
    
    @pytest.mark.asyncio
    async def test_gmail_authentication(self, orchestrator):
        """Test Gmail OAuth authentication flow."""
        if SourceType.GMAIL not in orchestrator.sources:
            pytest.skip("Gmail not enabled in integration config")
        
        gmail_source = orchestrator.sources[SourceType.GMAIL]
        
        # Test authentication
        auth_result = await gmail_source.authenticate()
        assert auth_result is True
        
        # Test connection
        connection_result = await gmail_source.test_connection()
        assert connection_result is True
    
    @pytest.mark.asyncio
    async def test_gmail_sync_recent(self, orchestrator):
        """Test syncing recent Gmail messages."""
        if SourceType.GMAIL not in orchestrator.sources:
            pytest.skip("Gmail not enabled in integration config")
        
        # Sync last 7 days
        since = datetime.utcnow() - timedelta(days=7)
        result = await orchestrator.sync_source(SourceType.GMAIL)
        
        assert result.items_processed >= 0
        assert isinstance(result.processed_documents, list)
        
        # Check processed documents
        for doc in result.processed_documents[:5]:  # Check first 5
            assert doc.source_type == SourceType.GMAIL
            assert doc.title  # Has subject
            assert doc.content  # Has body
            assert doc.metadata.get('sender_email')  # Has sender
    
    @pytest.mark.asyncio
    async def test_fireflies_authentication(self, orchestrator):
        """Test Fireflies API authentication."""
        if SourceType.FIREFLIES not in orchestrator.sources:
            pytest.skip("Fireflies not enabled in integration config")
        
        fireflies_source = orchestrator.sources[SourceType.FIREFLIES]
        
        # Test authentication
        auth_result = await fireflies_source.authenticate()
        assert auth_result is True
        
        # Test connection
        connection_result = await fireflies_source.test_connection()
        assert connection_result is True
    
    @pytest.mark.asyncio
    async def test_fireflies_sync_transcripts(self, orchestrator):
        """Test syncing Fireflies transcripts."""
        if SourceType.FIREFLIES not in orchestrator.sources:
            pytest.skip("Fireflies not enabled in integration config")
        
        # Sync recent transcripts
        result = await orchestrator.sync_source(SourceType.FIREFLIES)
        
        assert result.items_processed >= 0
        
        # Check processed transcripts
        for doc in result.processed_documents[:3]:  # Check first 3
            assert doc.source_type == SourceType.FIREFLIES
            assert doc.title  # Has meeting title
            assert doc.content  # Has transcript
            assert 'duration' in doc.metadata  # Has duration
            assert 'participants' in doc.metadata  # Has participants
    
    @pytest.mark.asyncio
    async def test_google_drive_authentication(self, orchestrator):
        """Test Google Drive OAuth authentication."""
        if SourceType.GOOGLE_DRIVE not in orchestrator.sources:
            pytest.skip("Google Drive not enabled in integration config")
        
        drive_source = orchestrator.sources[SourceType.GOOGLE_DRIVE]
        
        # Test authentication
        auth_result = await drive_source.authenticate()
        assert auth_result is True
        
        # Test connection
        connection_result = await drive_source.test_connection()
        assert connection_result is True
    
    @pytest.mark.asyncio
    async def test_google_drive_sync_gemini(self, orchestrator):
        """Test syncing Gemini transcripts from Google Drive."""
        if SourceType.GOOGLE_DRIVE not in orchestrator.sources:
            pytest.skip("Google Drive not enabled in integration config")
        
        # Sync Gemini transcripts
        result = await orchestrator.sync_source(SourceType.GOOGLE_DRIVE)
        
        assert result.items_processed >= 0
        
        # Check for Gemini transcripts
        gemini_docs = [
            doc for doc in result.processed_documents
            if doc.metadata.get('is_gemini_transcript')
        ]
        
        for doc in gemini_docs[:2]:  # Check first 2
            assert "Gemini" in doc.title or "gemini" in doc.title.lower()
            assert doc.content  # Has content
            assert doc.source_type == SourceType.GOOGLE_DRIVE
    
    @pytest.mark.asyncio
    async def test_cross_source_deduplication(self, orchestrator):
        """Test deduplication across multiple sources."""
        if len(orchestrator.sources) < 2:
            pytest.skip("Need at least 2 sources for cross-source deduplication test")
        
        # Sync all sources
        results = await orchestrator.sync_all()
        
        # Get deduplication stats
        stats = orchestrator.get_deduplication_stats()
        
        assert stats['total_documents'] >= 0
        assert stats['unique_documents'] <= stats['total_documents']
        
        # Check for any duplicates found
        total_duplicates = sum(
            result.metadata.get('deduplication', {}).get('duplicates_found', 0)
            for result in results.values()
        )
        
        if total_duplicates > 0:
            print(f"Found {total_duplicates} duplicates across sources")
    
    @pytest.mark.asyncio
    async def test_selective_processing_filters(self, orchestrator):
        """Test selective processing with filters."""
        if SourceType.GMAIL not in orchestrator.sources:
            pytest.skip("Gmail not enabled for selective processing test")
        
        # Add test filter
        orchestrator.selective_processor.add_rule({
            'name': 'Test Filter',
            'type': 'subject',
            'action': 'exclude',
            'pattern': r'newsletter|notification',
            'priority': 10
        })
        
        # Sync with filter
        result = await orchestrator.sync_source(SourceType.GMAIL)
        
        # Check filtering stats
        if 'selective_processing' in result.metadata:
            excluded = result.metadata['selective_processing']['excluded_count']
            included = result.metadata['selective_processing']['included_count']
            
            print(f"Selective processing: {excluded} excluded, {included} included")
            assert excluded + included > 0
    
    @pytest.mark.asyncio
    async def test_nlp_extraction(self, orchestrator):
        """Test NLP extraction on real documents."""
        if not orchestrator.sources:
            pytest.skip("No sources enabled for NLP test")
        
        # Sync one source
        source_type = list(orchestrator.sources.keys())[0]
        result = await orchestrator.sync_source(source_type)
        
        # Check NLP extraction in documents
        docs_with_nlp = [
            doc for doc in result.processed_documents
            if doc.metadata and ('entities' in doc.metadata or 'sentiment' in doc.metadata)
        ]
        
        if docs_with_nlp:
            # Check first document with NLP
            doc = docs_with_nlp[0]
            
            if 'entities' in doc.metadata:
                assert isinstance(doc.metadata['entities'], list)
                print(f"Found {len(doc.metadata['entities'])} entities")
            
            if 'sentiment' in doc.metadata:
                sentiment = doc.metadata['sentiment']
                assert 'polarity' in sentiment
                assert 'label' in sentiment
                print(f"Sentiment: {sentiment['label']} ({sentiment['polarity']:.2f})")
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, orchestrator):
        """Test metrics collection from all sources."""
        if not orchestrator.sources:
            pytest.skip("No sources enabled for metrics test")
        
        # Get initial metrics
        initial_metrics = await orchestrator.get_metrics()
        
        # Perform sync
        await orchestrator.sync_all()
        
        # Get updated metrics
        final_metrics = await orchestrator.get_metrics()
        
        # Verify metrics structure
        for source_type, metrics in final_metrics.items():
            assert 'metrics' in metrics or 'error' in metrics
            assert 'sync_state' in metrics
            
            if 'metrics' in metrics:
                source_metrics = metrics['metrics']
                print(f"\n{source_type} metrics:")
                for key, value in source_metrics.items():
                    print(f"  {key}: {value}")
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, orchestrator):
        """Test error handling and recovery mechanisms."""
        if not orchestrator.sources:
            pytest.skip("No sources enabled for error handling test")
        
        # Temporarily break a source
        source_type = list(orchestrator.sources.keys())[0]
        original_source = orchestrator.sources[source_type]
        
        # Replace with broken source
        broken_source = type(original_source)(original_source.config)
        broken_source.sync = asyncio.coroutine(lambda since=None: 1/0)  # Will raise ZeroDivisionError
        orchestrator.sources[source_type] = broken_source
        
        # Try to sync - should handle error
        results = await orchestrator.sync_all()
        
        assert source_type in results
        assert len(results[source_type].errors) > 0
        assert "division by zero" in str(results[source_type].errors[0])
        
        # Restore original source
        orchestrator.sources[source_type] = original_source
        
        # Verify recovery
        results = await orchestrator.sync_all()
        assert source_type in results
        # Should work now (unless there are other issues)
    
    @pytest.mark.asyncio
    async def test_performance_benchmark(self, orchestrator):
        """Benchmark sync performance."""
        if not orchestrator.sources:
            pytest.skip("No sources enabled for performance test")
        
        # Time full sync
        start_time = datetime.utcnow()
        results = await orchestrator.sync_all()
        end_time = datetime.utcnow()
        
        total_time = (end_time - start_time).total_seconds()
        total_items = sum(r.items_processed for r in results.values())
        
        print(f"\nPerformance benchmark:")
        print(f"  Total time: {total_time:.2f} seconds")
        print(f"  Total items: {total_items}")
        if total_items > 0:
            print(f"  Items/second: {total_items/total_time:.2f}")
        
        # Performance assertions (adjust based on requirements)
        assert total_time < 300  # Should complete within 5 minutes
        if total_items > 0:
            assert total_items / total_time > 0.1  # At least 0.1 items/second


@pytest.mark.integration
class TestEndToEndScenarios:
    """End-to-end integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_daily_sync_workflow(self, orchestrator):
        """Test a typical daily sync workflow."""
        if not orchestrator.sources:
            pytest.skip("No sources enabled for workflow test")
        
        print("\n=== Daily Sync Workflow Test ===")
        
        # 1. Check connections
        print("\n1. Testing connections...")
        for source_type, source in orchestrator.sources.items():
            result = await source.test_connection()
            print(f"   {source_type.value}: {'✓' if result else '✗'}")
        
        # 2. Sync all sources
        print("\n2. Syncing all sources...")
        results = await orchestrator.sync_all()
        
        for source_type, result in results.items():
            print(f"   {source_type.value}: {result.items_processed} processed, {len(result.errors)} errors")
        
        # 3. Check deduplication
        print("\n3. Deduplication stats:")
        dedup_stats = orchestrator.get_deduplication_stats()
        print(f"   Total documents: {dedup_stats['total_documents']}")
        print(f"   Unique documents: {dedup_stats['unique_documents']}")
        
        # 4. Get metrics
        print("\n4. Final metrics:")
        metrics = await orchestrator.get_metrics()
        for source_type, source_metrics in metrics.items():
            if 'sync_state' in source_metrics:
                last_sync = source_metrics['sync_state'].get('last_sync', 'Never')
                print(f"   {source_type}: Last sync: {last_sync}")
    
    @pytest.mark.asyncio
    async def test_knowledge_base_creation(self, orchestrator, tmp_path):
        """Test creating a knowledge base from all sources."""
        if not orchestrator.sources:
            pytest.skip("No sources enabled for knowledge base test")
        
        print("\n=== Knowledge Base Creation Test ===")
        
        # Set knowledge base paths
        kb_path = tmp_path / "knowledge_base"
        kb_path.mkdir()
        
        # Sync and save documents
        results = await orchestrator.sync_all()
        
        total_saved = 0
        for source_type, result in results.items():
            source_path = kb_path / source_type.value
            source_path.mkdir()
            
            for doc in result.processed_documents[:10]:  # Save first 10
                doc_path = source_path / f"{doc.id}.json"
                doc_data = {
                    'id': doc.id,
                    'title': doc.title,
                    'content': doc.content[:1000],  # First 1000 chars
                    'metadata': doc.metadata,
                    'processed_at': doc.processed_at.isoformat()
                }
                
                with open(doc_path, 'w') as f:
                    json.dump(doc_data, f, indent=2)
                
                total_saved += 1
        
        print(f"\nSaved {total_saved} documents to {kb_path}")
        
        # Verify structure
        assert kb_path.exists()
        assert total_saved > 0


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"])