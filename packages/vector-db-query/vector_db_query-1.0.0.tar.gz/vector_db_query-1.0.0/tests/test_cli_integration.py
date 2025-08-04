"""Integration tests for CLI commands and workflows.

This file tests real command execution scenarios and integration between components.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from vector_db_query.cli.main import cli
from vector_db_query.vector_db.models import CollectionInfo


class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test files
            (tmpdir / "doc1.txt").write_text("This is the first test document.")
            (tmpdir / "doc2.txt").write_text("This is the second test document.")
            (tmpdir / "doc3.md").write_text("# Test Markdown\n\nThis is a test markdown file.")
            
            # Create subdirectory with files
            subdir = tmpdir / "subdir"
            subdir.mkdir()
            (subdir / "doc4.txt").write_text("Document in subdirectory.")
            
            yield tmpdir
            
    @pytest.fixture
    def mock_vector_service(self):
        """Mock VectorDBService for testing."""
        with patch('vector_db_query.cli.commands.process_fixed.VectorDBService') as mock_service_class:
            mock_instance = Mock()
            mock_service_class.return_value = mock_instance
            
            # Setup default behavior
            mock_instance._initialized = True
            mock_instance.initialize.return_value = True
            mock_instance.get_status.return_value = {
                'service_initialized': True,
                'docker_running': True,
                'client_connected': True,
                'health_status': {'is_healthy': True, 'version': '1.7.0'},
                'storage_stats': {'total_collections': 0, 'total_vectors': 0},
                'collections': [],
                'docker_info': {'status': 'running', 'id': 'abc123'}
            }
            
            yield mock_instance
            
    def test_process_folder_recursive(self, temp_dir, mock_vector_service):
        """Test processing a folder recursively."""
        # Setup mock response
        mock_vector_service.process_and_store.return_value = {
            'vectors_stored': 4,
            'documents_processed': 4,
            'errors': []
        }
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'process',
            '--folder', str(temp_dir),
            '--recursive',
            '--collection', 'test-collection'
        ])
        
        assert result.exit_code == 0
        assert 'Found 4 files to process' in result.output
        assert 'Documents Stored' in result.output
        assert '4' in result.output
        
        # Verify process_and_store was called
        mock_vector_service.process_and_store.assert_called()
        call_args = mock_vector_service.process_and_store.call_args
        assert call_args[1]['collection_name'] == 'test-collection'
        
    def test_process_individual_files(self, temp_dir, mock_vector_service):
        """Test processing individual files."""
        # Setup mock response
        mock_vector_service.process_and_store.return_value = {
            'vectors_stored': 2,
            'documents_processed': 2,
            'errors': []
        }
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'process',
            '--file', str(temp_dir / "doc1.txt"),
            '--file', str(temp_dir / "doc2.txt"),
            '--collection', 'my-docs'
        ])
        
        assert result.exit_code == 0
        assert 'Found 2 files to process' in result.output
        assert 'Documents Stored' in result.output
        assert '2' in result.output
        assert 'Next Steps:' in result.output
        assert "vdq query 'your search query'" in result.output
        
    def test_process_with_custom_options(self, temp_dir, mock_vector_service):
        """Test processing with custom chunking options."""
        mock_vector_service.process_and_store.return_value = {
            'vectors_stored': 10,
            'documents_processed': 2,
            'errors': []
        }
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'process',
            '--folder', str(temp_dir),
            '--collection', 'custom-chunks',
            '--chunk-size', '500',
            '--chunk-overlap', '100',
            '--strategy', 'sliding_window',
            '--verbose'
        ])
        
        assert result.exit_code == 0
        assert 'Documents Stored' in result.output
        assert '10' in result.output
        
    def test_process_dry_run(self, temp_dir, mock_vector_service):
        """Test dry run mode."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'process',
            '--folder', str(temp_dir),
            '--dry-run'
        ])
        
        assert result.exit_code == 0
        assert 'DRY RUN - Would process:' in result.output
        assert 'doc1.txt' in result.output
        assert 'doc2.txt' in result.output
        
        # Ensure process_and_store was NOT called
        mock_vector_service.process_and_store.assert_not_called()
        
    def test_process_error_handling(self, temp_dir, mock_vector_service):
        """Test error handling during processing."""
        # Simulate processing errors
        mock_vector_service.process_and_store.return_value = {
            'vectors_stored': 2,
            'documents_processed': 4,
            'errors': ['Failed to process doc3.md: Invalid format', 'Network timeout']
        }
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'process',
            '--folder', str(temp_dir),
            '--collection', 'test',
            '--verbose'
        ])
        
        assert result.exit_code == 0
        assert 'Errors' in result.output
        assert '2' in result.output  # 2 errors
        assert 'Errors encountered:' in result.output
        assert 'Failed to process doc3.md' in result.output
        
    def test_vector_status_command(self, mock_vector_service):
        """Test vector status command."""
        # Add mock collections
        mock_vector_service.get_status.return_value['collections'] = [
            {
                'name': 'documents',
                'vectors': 100,
                'vector_size': 768,
                'status': 'green'
            },
            {
                'name': 'test-data',
                'vectors': 50,
                'vector_size': 384,
                'status': 'green'
            }
        ]
        mock_vector_service.get_status.return_value['storage_stats'] = {
            'total_collections': 2,
            'total_vectors': 150
        }
        
        with patch('vector_db_query.cli.commands.vector.VectorDBService', return_value=mock_vector_service):
            runner = CliRunner()
            result = runner.invoke(cli, ['vector', 'status'])
        
        assert result.exit_code == 0
        assert 'Vector Database Status' in result.output
        assert 'Service Initialized' in result.output
        assert 'Docker Running' in result.output
        assert 'Collections:' in result.output
        assert 'documents' in result.output
        assert '100' in result.output
        assert 'test-data' in result.output
        assert '50' in result.output
        assert 'Total Collections: 2' in result.output
        assert 'Total Vectors: 150' in result.output
        
    def test_vector_list_collections(self):
        """Test listing collections."""
        mock_collections = [
            Mock(
                name='docs',
                vectors_count=100,
                vector_size=768,
                distance_metric='Cosine',
                is_ready=True
            ),
            Mock(
                name='embeddings',
                vectors_count=500,
                vector_size=384,
                distance_metric='Euclidean',
                is_ready=True
            )
        ]
        
        with patch('vector_db_query.cli.commands.vector.VectorDBService') as mock_service_class:
            mock_instance = Mock()
            mock_service_class.return_value = mock_instance
            mock_instance.collections.list_collections.return_value = mock_collections
            
            runner = CliRunner()
            result = runner.invoke(cli, ['vector', 'list-collections'])
        
        assert result.exit_code == 0
        assert 'Vector Collections' in result.output
        assert 'docs' in result.output
        assert '100' in result.output
        assert '768' in result.output
        assert 'Cosine' in result.output
        assert 'embeddings' in result.output
        assert '500' in result.output
        assert '384' in result.output
        assert 'Euclidean' in result.output
        
    def test_vector_create_collection(self):
        """Test creating a new collection."""
        with patch('vector_db_query.cli.commands.vector.VectorDBService') as mock_service_class:
            mock_instance = Mock()
            mock_service_class.return_value = mock_instance
            mock_instance.collections.create_collection.return_value = True
            
            runner = CliRunner()
            result = runner.invoke(cli, [
                'vector',
                'create-collection',
                'new-collection',
                '--vector-size', '768',
                '--distance', 'cosine'
            ])
        
        assert result.exit_code == 0
        assert "Collection 'new-collection' created successfully" in result.output
        
        # Verify create_collection was called correctly
        mock_instance.collections.create_collection.assert_called_once_with(
            name='new-collection',
            vector_size=768,
            distance='Cosine'
        )
        
    def test_vector_info_integration(self):
        """Test vector info command integration."""
        mock_collection = Mock(
            name='my-docs',
            vectors_count=250,
            vector_size=768,
            distance_metric='Cosine',
            is_ready=True
        )
        
        mock_point = Mock()
        mock_point.payload = {
            'file_name': 'document.txt',
            'chunk_index': 0,
            'chunk_text': 'Sample content',
            'created_at': '2024-01-15T10:30:00',
            'file_type': 'text'
        }
        
        with patch('vector_db_query.cli.commands.vector.VectorDBService') as mock_service_class:
            mock_instance = Mock()
            mock_service_class.return_value = mock_instance
            mock_instance.collections.list_collections.return_value = [mock_collection]
            mock_instance.client._client.scroll.return_value = ([mock_point], None)
            
            runner = CliRunner()
            result = runner.invoke(cli, ['vector', 'info', 'my-docs'])
        
        assert result.exit_code == 0
        assert 'Collection: my-docs' in result.output
        assert 'Vector Count' in result.output
        assert '250' in result.output
        assert 'Storage Statistics:' in result.output
        assert 'Total vectors: 250' in result.output
        assert 'Metadata Fields:' in result.output
        assert 'file_name' in result.output
        assert 'chunk_index' in result.output
        assert 'created_at' in result.output
        assert 'file_type' in result.output
        
    def test_workflow_process_then_query_info(self, temp_dir):
        """Test complete workflow: process -> check info -> query."""
        runner = CliRunner()
        
        # Mock for process command
        with patch('vector_db_query.cli.commands.process_fixed.VectorDBService') as mock_process:
            mock_process_instance = Mock()
            mock_process.return_value = mock_process_instance
            mock_process_instance._initialized = True
            mock_process_instance.process_and_store.return_value = {
                'vectors_stored': 3,
                'documents_processed': 3,
                'errors': []
            }
            
            # Step 1: Process documents
            result = runner.invoke(cli, [
                'process',
                '--folder', str(temp_dir),
                '--collection', 'test-workflow',
                '--recursive', 'false'
            ])
            
            assert result.exit_code == 0
            assert '3' in result.output  # 3 documents stored
            
        # Mock for vector info command
        with patch('vector_db_query.cli.commands.vector.VectorDBService') as mock_vector:
            mock_vector_instance = Mock()
            mock_vector.return_value = mock_vector_instance
            
            mock_collection = Mock(
                name='test-workflow',
                vectors_count=3,
                vector_size=768,
                distance_metric='Cosine',
                is_ready=True
            )
            mock_vector_instance.collections.list_collections.return_value = [mock_collection]
            
            # Step 2: Check collection info
            result = runner.invoke(cli, ['vector', 'info', 'test-workflow'])
            
            assert result.exit_code == 0
            assert 'test-workflow' in result.output
            assert '3' in result.output  # 3 vectors
            
    def test_command_help_system(self):
        """Test help commands work properly."""
        runner = CliRunner()
        
        # Main help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Vector DB Query System' in result.output
        assert 'process' in result.output
        assert 'vector' in result.output
        assert 'query' in result.output
        
        # Process help
        result = runner.invoke(cli, ['process', '--help'])
        assert result.exit_code == 0
        assert 'Process documents and store them' in result.output
        assert '--folder' in result.output
        assert '--file' in result.output
        assert '--collection' in result.output
        
        # Vector help
        result = runner.invoke(cli, ['vector', '--help'])
        assert result.exit_code == 0
        assert 'Vector database management commands' in result.output
        assert 'init' in result.output
        assert 'status' in result.output
        assert 'info' in result.output
        
        # Vector info help
        result = runner.invoke(cli, ['vector', 'info', '--help'])
        assert result.exit_code == 0
        assert 'Show detailed information about a specific collection' in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])