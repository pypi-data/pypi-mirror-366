"""Regression tests for CLI fixes.

This file contains tests to ensure no regressions occur in related functionality
after the CLI display storage fixes.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from click.testing import CliRunner
import json

from vector_db_query.cli.main import cli
from vector_db_query.cli.commands.process_fixed import process_command
from vector_db_query.cli.commands.vector import vector


class TestRegressionVectorOperations:
    """Regression tests for vector database operations."""
    
    @patch('vector_db_query.cli.commands.vector.VectorDBService')
    def test_vector_search_still_works(self, mock_service):
        """Ensure vector search functionality is not affected."""
        mock_instance = Mock()
        mock_service.return_value = mock_instance
        
        # Mock search results
        mock_result1 = Mock()
        mock_result1.score = 0.95
        mock_result1.payload = {
            'file_name': 'test.txt',
            'chunk_index': 0,
            'chunk_text': 'This is a test document with relevant content.'
        }
        
        mock_result2 = Mock()
        mock_result2.score = 0.87
        mock_result2.payload = {
            'file_name': 'other.txt',
            'chunk_index': 2,
            'chunk_text': 'Another document with matching terms.'
        }
        
        mock_instance.search_similar.return_value = [mock_result1, mock_result2]
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'vector',
            'search',
            'test query',
            '--collection', 'documents',
            '--limit', '5'
        ])
        
        assert result.exit_code == 0
        assert 'Searching for:' in result.output
        assert 'test query' in result.output
        assert 'Found 2 results' in result.output
        assert 'Score: 0.9500' in result.output
        assert 'test.txt' in result.output
        assert 'Score: 0.8700' in result.output
        assert 'other.txt' in result.output
        
    @patch('vector_db_query.cli.commands.vector.VectorDBService')
    def test_vector_store_functionality(self, mock_service):
        """Ensure vector store command still works correctly."""
        mock_instance = Mock()
        mock_service.return_value = mock_instance
        
        mock_instance.process_and_store.return_value = {
            'documents_processed': 3,
            'vectors_stored': 15,  # Multiple chunks per document
            'errors': []
        }
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'vector',
            'store',
            '/path/to/file1.txt',
            '/path/to/file2.txt',
            '/path/to/file3.txt',
            '--collection', 'test-store'
        ])
        
        assert result.exit_code == 0
        assert 'Processing 3 files' in result.output
        assert 'Storage Complete!' in result.output
        assert 'Documents processed: 3' in result.output
        assert 'Vectors stored: 15' in result.output
        
    @patch('vector_db_query.cli.commands.vector.VectorDBService')
    def test_vector_init_stop_commands(self, mock_service):
        """Test vector init and stop commands still work."""
        mock_instance = Mock()
        mock_service.return_value = mock_instance
        mock_instance.initialize.return_value = True
        
        # Test init
        runner = CliRunner()
        result = runner.invoke(cli, ['vector', 'init', '--timeout', '30'])
        
        assert result.exit_code == 0
        assert 'Vector database initialized successfully!' in result.output
        
        # Test stop
        result = runner.invoke(cli, ['vector', 'stop', '--stop-docker'])
        
        assert result.exit_code == 0
        assert 'Vector database and container stopped' in result.output
        mock_instance.shutdown.assert_called_once_with(stop_container=True)


class TestRegressionProcessCommand:
    """Regression tests for process command functionality."""
    
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    @patch('vector_db_query.document_processor.scanner.FileScanner')
    def test_file_scanning_still_works(self, mock_scanner, mock_service):
        """Ensure file scanning functionality is not broken."""
        # Setup mocks
        mock_scanner_instance = Mock()
        mock_scanner.return_value = mock_scanner_instance
        
        # Mock various file types
        test_files = [
            Path('/docs/readme.md'),
            Path('/docs/report.pdf'),
            Path('/docs/data.xlsx'),
            Path('/docs/notes.txt'),
            Path('/docs/presentation.pptx')
        ]
        mock_scanner_instance.scan_directory.return_value = test_files
        
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        mock_service_instance._initialized = True
        mock_service_instance.process_and_store.return_value = {
            'vectors_stored': 50,
            'documents_processed': 5,
            'errors': []
        }
        
        runner = CliRunner()
        result = runner.invoke(process_command, [
            '--folder', '/docs',
            '--recursive'
        ])
        
        assert result.exit_code == 0
        assert 'Found 5 files to process' in result.output
        assert 'Documents Stored' in result.output
        assert '50' in result.output
        
        # Verify scanner was called correctly
        mock_scanner_instance.scan_directory.assert_called_once_with(
            Path('/docs'),
            recursive=True
        )
        
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    def test_chunking_options_still_work(self, mock_service):
        """Ensure chunking options are still passed correctly."""
        mock_instance = Mock()
        mock_service.return_value = mock_instance
        mock_instance._initialized = True
        mock_instance.process_and_store.return_value = {
            'vectors_stored': 20,
            'documents_processed': 1,
            'errors': []
        }
        
        runner = CliRunner()
        result = runner.invoke(process_command, [
            '--file', '/test.txt',
            '--chunk-size', '1000',
            '--chunk-overlap', '200',
            '--strategy', 'semantic'
        ])
        
        assert result.exit_code == 0
        
        # The service is mocked, but we ensure the command accepts these options
        assert 'Documents Stored' in result.output
        assert '20' in result.output
        
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    def test_error_reporting_still_works(self, mock_service):
        """Ensure error reporting is not affected."""
        mock_instance = Mock()
        mock_service.return_value = mock_instance
        mock_instance._initialized = True
        
        # Simulate partial failure
        mock_instance.process_and_store.side_effect = [
            {'vectors_stored': 10, 'errors': ['Error in file1.pdf: Corrupted PDF']},
            {'vectors_stored': 5, 'errors': []},
            {'vectors_stored': 0, 'errors': ['Error in file3.docx: Unsupported format', 'Network timeout']}
        ]
        
        runner = CliRunner()
        # Create many files to trigger multiple batches
        files = ['--file'] + [f'/test{i}.txt' for i in range(25)]
        result = runner.invoke(process_command, files + ['--verbose'])
        
        assert result.exit_code == 0
        assert 'Errors' in result.output
        assert '3' in result.output  # Total errors
        assert 'Errors encountered:' in result.output
        assert 'Error in file1.pdf' in result.output


class TestRegressionCLIBehavior:
    """Test overall CLI behavior hasn't regressed."""
    
    def test_cli_version_flag(self):
        """Test --version flag still works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert 'Vector DB Query System v' in result.output
        
    def test_cli_help_completeness(self):
        """Ensure all commands are listed in help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        # Check all main commands are present
        assert 'process' in result.output
        assert 'vector' in result.output
        assert 'query' in result.output
        assert 'mcp' in result.output
        assert 'interactive' in result.output
        assert 'read' in result.output
        assert 'config' in result.output
        assert 'status' in result.output
        
    @patch('vector_db_query.cli.main.InteractiveApp')
    def test_interactive_mode_fallback(self, mock_app):
        """Test interactive mode still launches correctly."""
        # Simulate interactive app
        mock_app_instance = Mock()
        mock_app.return_value = mock_app_instance
        mock_app_instance.run = MagicMock(return_value=None)
        
        runner = CliRunner()
        # Invoke without subcommand should start interactive mode
        result = runner.invoke(cli, [])
        
        # Check that interactive app was attempted
        mock_app.assert_called()
        
    def test_config_command_regression(self):
        """Test config command still works."""
        with patch('vector_db_query.utils.config.get_config') as mock_config:
            mock_config.return_value = {
                'embedding.model': 'text-embedding-ada-002',
                'embedding.dimensions': 1536,
                'vector_db.host': 'localhost',
                'vector_db.port': 6333,
                'vector_db.collection_name': 'documents',
                'document_processing.chunk_size': 1000,
                'app.log_level': 'INFO'
            }
            
            runner = CliRunner()
            result = runner.invoke(cli, ['config'])
            
            assert result.exit_code == 0
            assert 'Current Configuration' in result.output
            assert 'text-embedding-ada-002' in result.output
            assert '1536' in result.output
            assert 'localhost:6333' in result.output
            
    def test_logging_options_work(self):
        """Test logging options are not broken."""
        runner = CliRunner()
        
        # Test with different log levels
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            result = runner.invoke(cli, ['--log-level', level, '--help'])
            assert result.exit_code == 0
            
    @patch('vector_db_query.cli.commands.read.UniversalVDBReader')
    def test_read_command_regression(self, mock_reader):
        """Test read command functionality."""
        mock_reader_instance = Mock()
        mock_reader.return_value = mock_reader_instance
        
        # Mock statistics
        mock_reader_instance.get_statistics.return_value = {
            'collection1': {
                'points_count': 100,
                'dimension': 768,
                'status': 'ready'
            },
            'collection2': {
                'points_count': 50,
                'dimension': 384,
                'status': 'ready'
            }
        }
        
        runner = CliRunner()
        result = runner.invoke(cli, ['read', '--stats'])
        
        assert result.exit_code == 0
        assert 'Vector Database Collections' in result.output
        assert 'collection1' in result.output
        assert '100' in result.output
        assert 'collection2' in result.output
        assert '50' in result.output
        assert 'Total documents: 150' in result.output


class TestRegressionEdgeCases:
    """Test edge cases to ensure robustness."""
    
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    def test_empty_folder_handling(self, mock_service):
        """Test processing empty folder doesn't crash."""
        mock_instance = Mock()
        mock_service.return_value = mock_instance
        mock_instance._initialized = True
        
        with patch('vector_db_query.document_processor.scanner.FileScanner') as mock_scanner:
            mock_scanner_instance = Mock()
            mock_scanner.return_value = mock_scanner_instance
            mock_scanner_instance.scan_directory.return_value = []  # Empty folder
            
            runner = CliRunner()
            result = runner.invoke(process_command, [
                '--folder', '/empty/folder'
            ])
            
            assert result.exit_code == 0
            assert 'No files found to process' in result.output
            
    @patch('vector_db_query.cli.commands.process_fixed.VectorDBService')
    def test_service_initialization_failure(self, mock_service):
        """Test graceful handling of service initialization failure."""
        mock_service.side_effect = Exception("Failed to connect to Qdrant")
        
        runner = CliRunner()
        result = runner.invoke(process_command, [
            '--file', '/test.txt'
        ])
        
        assert result.exit_code != 0
        assert 'Error initializing vector service' in result.output
        assert 'Failed to connect to Qdrant' in result.output
        
    @patch('vector_db_query.cli.commands.vector.VectorDBService')
    def test_collection_not_found_handling(self, mock_service):
        """Test handling of non-existent collection."""
        mock_instance = Mock()
        mock_service.return_value = mock_instance
        mock_instance.collections.list_collections.return_value = []
        
        runner = CliRunner()
        result = runner.invoke(cli, ['vector', 'info', 'non-existent'])
        
        assert result.exit_code == 0
        assert "Collection 'non-existent' not found" in result.output
        
    def test_invalid_command_handling(self):
        """Test invalid commands are handled properly."""
        runner = CliRunner()
        
        # Invalid main command
        result = runner.invoke(cli, ['invalid-command'])
        assert result.exit_code != 0
        assert 'Error' in result.output or 'No such command' in result.output
        
        # Invalid subcommand
        result = runner.invoke(cli, ['vector', 'invalid-subcommand'])
        assert result.exit_code != 0
        
        # Missing required arguments
        result = runner.invoke(cli, ['vector', 'create-collection'])
        assert result.exit_code != 0
        assert 'Missing' in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])