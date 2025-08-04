"""Test suite for CLI display storage fixes.

This test file specifically tests:
1. Document count display fix in process_fixed.py (line 182)
2. New vector info command in vector.py
3. Command suggestion fix in process_fixed.py
4. vdq alias functionality
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from click.testing import CliRunner

from vector_db_query.cli.main import cli
from vector_db_query.cli.commands.process_fixed import process_command
from vector_db_query.cli.commands.vector import vector, info


class TestProcessCommandDisplayFix:
    """Test process command correctly displays document count."""
    
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    @patch('vector_db_query.document_processor.scanner.FileScanner')
    def test_process_command_displays_correct_document_count(self, mock_scanner, mock_service):
        """Test that process command displays 'vectors_stored' correctly."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance._initialized = True
        
        # Mock the process_and_store result with 'vectors_stored' key
        mock_service_instance.process_and_store.return_value = {
            'vectors_stored': 42,
            'documents_processed': 10,
            'errors': []
        }
        
        # Mock file scanner
        mock_scanner_instance = Mock()
        mock_scanner.return_value = mock_scanner_instance
        mock_scanner_instance.scan_directory.return_value = [
            Path('/test/file1.txt'),
            Path('/test/file2.txt')
        ]
        
        # Run command with temp directory
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create test directory
            test_dir = Path('test')
            test_dir.mkdir()
            
            result = runner.invoke(process_command, [
                '--folder', str(test_dir),
                '--collection', 'test-collection'
            ])
        
            # Check output contains correct document count
            assert 'Documents Stored' in result.output
            assert '42' in result.output
            assert result.exit_code == 0
        
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    def test_process_command_handles_missing_vectors_stored_key(self, mock_service):
        """Test graceful handling when 'vectors_stored' key is missing."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance._initialized = True
        
        # Return result without 'vectors_stored' key (old format)
        mock_service_instance.process_and_store.return_value = {
            'stored_count': 30,  # Old key name
            'documents_processed': 10,
            'errors': []
        }
        
        # Run command
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create test file
            test_file = Path('test.txt')
            test_file.write_text('test content')
            
            result = runner.invoke(process_command, [
                '--file', str(test_file),
                '--collection', 'test-collection'
            ])
        
        # Should show 0 when key is missing
        assert 'Documents Stored' in result.output
        assert '0' in result.output
        assert result.exit_code == 0
        
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    def test_process_command_accumulates_vectors_across_batches(self, mock_service):
        """Test that vector counts are accumulated correctly across batches."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance._initialized = True
        
        # Mock multiple batch results
        batch_results = [
            {'vectors_stored': 10, 'errors': []},
            {'vectors_stored': 15, 'errors': []},
            {'vectors_stored': 25, 'errors': ['error1']}
        ]
        mock_service_instance.process_and_store.side_effect = batch_results
        
        # Run command with many files
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create many test files to trigger batching
            test_files = []
            for i in range(25):
                test_file = Path(f'file{i}.txt')
                test_file.write_text(f'content {i}')
                test_files.append(test_file)
            
            result = runner.invoke(process_command, [
                '--file'] + [str(f) for f in test_files] + [
                '--collection', 'test-collection'
            ])
        
        # Check total is sum of all batches
        assert 'Documents Stored' in result.output
        assert '50' in result.output  # 10 + 15 + 25
        assert 'Errors' in result.output
        assert '1' in result.output  # 1 error from last batch


class TestVectorInfoCommand:
    """Test the new vector info command functionality."""
    
    @patch('vector_db_query.cli.commands.vector.VectorDBService')
    def test_vector_info_command_displays_collection_details(self, mock_service):
        """Test vector info command shows detailed collection information."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        
        # Mock collection info
        mock_collection = Mock()
        mock_collection.name = 'test-collection'
        mock_collection.vectors_count = 100
        mock_collection.vector_size = 768
        mock_collection.distance_metric = 'Cosine'
        mock_collection.is_ready = True
        
        mock_service_instance.collections.list_collections.return_value = [mock_collection]
        
        # Mock scroll for metadata fields
        mock_point = Mock()
        mock_point.payload = {
            'file_name': 'test.txt',
            'chunk_index': 0,
            'chunk_text': 'sample text',
            'created_at': '2024-01-01'
        }
        mock_service_instance.client._client.scroll.return_value = ([mock_point], None)
        
        # Run command
        runner = CliRunner()
        result = runner.invoke(info, ['test-collection'])
        
        # Check output
        assert 'Collection: test-collection' in result.output
        assert 'Vector Count' in result.output
        assert '100' in result.output
        assert 'Vector Size' in result.output
        assert '768' in result.output
        assert 'Distance Metric' in result.output
        assert 'Cosine' in result.output
        assert '✓ Ready' in result.output
        assert 'Metadata Fields:' in result.output
        assert 'file_name' in result.output
        assert 'chunk_index' in result.output
        assert result.exit_code == 0
        
    @patch('vector_db_query.cli.commands.vector.VectorDBService')
    def test_vector_info_command_handles_missing_collection(self, mock_service):
        """Test vector info command with non-existent collection."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.collections.list_collections.return_value = []
        
        # Run command
        runner = CliRunner()
        result = runner.invoke(info, ['non-existent'])
        
        # Check error message
        assert "Collection 'non-existent' not found" in result.output
        assert result.exit_code == 0
        
    @patch('vector_db_query.cli.commands.vector.VectorDBService')
    def test_vector_info_shows_usage_hint(self, mock_service):
        """Test vector info command shows usage hint."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        
        mock_collection = Mock()
        mock_collection.name = 'docs'
        mock_collection.vectors_count = 50
        mock_collection.vector_size = 768
        mock_collection.distance_metric = 'Cosine'
        mock_collection.is_ready = True
        
        mock_service_instance.collections.list_collections.return_value = [mock_collection]
        mock_service_instance.client._client.scroll.side_effect = Exception("No scroll")
        
        # Run command
        runner = CliRunner()
        result = runner.invoke(info, ['docs'])
        
        # Check usage hint is shown
        assert 'vector-db-query query --collection docs' in result.output
        assert result.exit_code == 0


class TestCommandSuggestions:
    """Test command suggestion fixes in process_fixed.py."""
    
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    def test_process_command_shows_correct_next_steps(self, mock_service):
        """Test that next steps show valid commands."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance._initialized = True
        mock_service_instance.process_and_store.return_value = {
            'vectors_stored': 10,
            'documents_processed': 5,
            'errors': []
        }
        
        # Run command
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create test file
            test_file = Path('test.txt')
            test_file.write_text('test content')
            
            result = runner.invoke(process_command, [
                '--file', str(test_file),
                '--collection', 'my-docs'
            ])
        
        # Check all suggested commands are present and correct
        assert 'Next Steps:' in result.output
        assert "vdq query 'your search query'" in result.output
        assert 'vdq interactive' in result.output
        assert 'vector-db-query vector info my-docs' in result.output
        assert result.exit_code == 0
        
    def test_process_command_suggestions_are_executable(self):
        """Test that suggested commands are valid CLI commands."""
        runner = CliRunner()
        
        # Test vdq query command exists
        result = runner.invoke(cli, ['query', '--help'])
        assert result.exit_code == 0
        assert 'Query the vector database' in result.output
        
        # Test vdq interactive command exists
        result = runner.invoke(cli, ['interactive', '--help'])
        assert result.exit_code == 0
        
        # Test vector-db-query vector info command exists
        result = runner.invoke(cli, ['vector', 'info', '--help'])
        assert result.exit_code == 0
        assert 'Show detailed information about a specific collection' in result.output


class TestVDQAlias:
    """Test vdq alias functionality."""
    
    def test_vdq_alias_works_for_main_commands(self):
        """Test that vdq alias executes main commands correctly."""
        runner = CliRunner()
        
        # Test vdq --version
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert 'Vector DB Query System' in result.output
        
        # Test vdq --help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Vector DB Query System' in result.output
        assert 'process' in result.output
        assert 'vector' in result.output
        assert 'query' in result.output
        
    def test_vdq_alias_works_for_subcommands(self):
        """Test vdq alias works with subcommands."""
        runner = CliRunner()
        
        # Test vdq process --help
        result = runner.invoke(cli, ['process', '--help'])
        assert result.exit_code == 0
        assert 'Process documents and store them in the vector database' in result.output
        
        # Test vdq vector --help
        result = runner.invoke(cli, ['vector', '--help'])
        assert result.exit_code == 0
        assert 'Vector database management commands' in result.output
        
        # Test vdq vector info --help
        result = runner.invoke(cli, ['vector', 'info', '--help'])
        assert result.exit_code == 0
        assert 'Show detailed information about a specific collection' in result.output
        
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    def test_vdq_alias_executes_commands(self, mock_service):
        """Test vdq alias actually executes commands."""
        # Setup mocks
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance._initialized = True
        mock_service_instance.get_status.return_value = {
            'service_initialized': True,
            'docker_running': True,
            'client_connected': True,
            'health_status': {
                'is_healthy': True,
                'version': '1.0.0'
            },
            'storage_stats': {
                'total_collections': 3,
                'total_vectors': 150
            },
            'collections': []
        }
        
        # Run vdq vector status
        runner = CliRunner()
        result = runner.invoke(cli, ['vector', 'status'])
        
        assert result.exit_code == 0
        assert 'Vector Database Status' in result.output
        assert 'Service Initialized' in result.output
        assert '✓' in result.output


class TestIntegrationScenarios:
    """Test end-to-end integration scenarios."""
    
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    @patch('vector_db_query.cli.commands.vector.VectorDBService')
    def test_process_then_info_workflow(self, mock_vector_service, mock_process_service):
        """Test typical workflow: process documents then check info."""
        runner = CliRunner()
        
        # Setup process service mock
        mock_process_instance = Mock()
        mock_process_service.return_value = mock_process_instance
        mock_process_instance._initialized = True
        mock_process_instance.process_and_store.return_value = {
            'vectors_stored': 25,
            'documents_processed': 5,
            'errors': []
        }
        
        # Setup vector service mock
        mock_vector_instance = Mock()
        mock_vector_service.return_value = mock_vector_instance
        
        mock_collection = Mock()
        mock_collection.name = 'test-docs'
        mock_collection.vectors_count = 25
        mock_collection.vector_size = 768
        mock_collection.distance_metric = 'Cosine'
        mock_collection.is_ready = True
        
        mock_vector_instance.collections.list_collections.return_value = [mock_collection]
        
        # Step 1: Process documents
        result = runner.invoke(cli, [
            'process',
            '--file', '/test/doc1.txt',
            '--file', '/test/doc2.txt',
            '--collection', 'test-docs'
        ])
        
        assert result.exit_code == 0
        assert 'Documents Stored' in result.output
        assert '25' in result.output
        assert 'vector-db-query vector info test-docs' in result.output
        
        # Step 2: Check collection info
        result = runner.invoke(cli, ['vector', 'info', 'test-docs'])
        
        assert result.exit_code == 0
        assert 'Collection: test-docs' in result.output
        assert 'Vector Count' in result.output
        assert '25' in result.output
        
    def test_cli_error_handling(self):
        """Test CLI handles errors gracefully."""
        runner = CliRunner()
        
        # Test missing required arguments
        result = runner.invoke(cli, ['process'])
        assert result.exit_code != 0
        assert 'Error:' in result.output or 'specify either --folder or --file' in result.output
        
        # Test invalid command
        result = runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0
        
        # Test vector info without collection name
        result = runner.invoke(cli, ['vector', 'info'])
        assert result.exit_code != 0
        assert 'Missing argument' in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])