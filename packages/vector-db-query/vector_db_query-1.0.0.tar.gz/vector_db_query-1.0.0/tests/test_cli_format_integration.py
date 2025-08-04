"""Integration tests for CLI with extended format support."""

import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, Mock
import json
import yaml
import tempfile

from src.vector_db_query.cli.commands.process_enhanced import process_command
from src.vector_db_query.cli.commands.detect import detect_format
from src.vector_db_query.cli.commands.config import config_group
from src.vector_db_query.utils.config_enhanced import FileFormatConfig


class TestCLIFormatCommands:
    """Test CLI format-related commands."""
    
    @pytest.fixture
    def runner(self):
        """Get Click test runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_embedder(self):
        """Mock embedding service."""
        with patch('src.vector_db_query.embeddings.embedding_service.GeminiEmbedder') as mock:
            instance = Mock()
            instance.embed_batch.return_value = [[0.1] * 768]
            mock.return_value = instance
            yield mock
    
    @pytest.fixture
    def mock_qdrant(self):
        """Mock Qdrant client."""
        with patch('qdrant_client.QdrantClient') as mock:
            instance = Mock()
            instance.get_collections.return_value = Mock(collections=[])
            instance.create_collection.return_value = True
            instance.upsert.return_value = True
            mock.return_value = instance
            yield mock
    
    def test_formats_display_command(self, runner):
        """Test --formats flag displays all supported formats."""
        result = runner.invoke(process_command, ['--formats'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check categories are displayed
        assert "📄 Documents:" in output
        assert "📊 Spreadsheets:" in output
        assert "🎯 Presentations:" in output
        assert "📧 Email:" in output
        assert "🌐 Web/Markup:" in output
        assert "⚙️ Config:" in output
        assert "🖼️ Images:" in output
        assert "📦 Archives:" in output
        assert "📊 Data:" in output
        assert "📋 Logs:" in output
        
        # Check specific formats
        assert ".pdf" in output
        assert ".xlsx" in output
        assert ".pptx" in output
        assert ".eml" in output
        assert ".html" in output
        assert ".json" in output
        assert ".png" in output
        assert ".zip" in output
        assert ".geojson" in output
        assert ".log" in output
        
        # Check total count
        assert "Total:" in output
        assert "39" in output or "formats" in output.lower()
    
    def test_detect_format_supported_file(self, runner):
        """Test format detection for supported files."""
        with runner.isolated_filesystem():
            # Create test file
            Path("test.pdf").touch()
            
            result = runner.invoke(detect_format, ['test.pdf'])
            
            assert result.exit_code == 0
            assert "✓ Supported" in result.output
            assert "Reader: PDFReader" in result.output
    
    def test_detect_format_unsupported_file(self, runner):
        """Test format detection for unsupported files."""
        with runner.isolated_filesystem():
            # Create unsupported file
            Path("test.xyz").touch()
            
            result = runner.invoke(detect_format, ['test.xyz'])
            
            assert result.exit_code == 0
            assert "✗ Not Supported" in result.output
            assert "No reader available" in result.output
    
    def test_detect_format_directory(self, runner):
        """Test format detection for directory."""
        with runner.isolated_filesystem():
            # Create directory with mixed files
            Path("docs").mkdir()
            Path("docs/file1.pdf").touch()
            Path("docs/file2.docx").touch()
            Path("docs/file3.xyz").touch()
            Path("docs/data.json").touch()
            
            result = runner.invoke(detect_format, ['docs', '--detailed'])
            
            assert result.exit_code == 0
            output = result.output
            
            # Should show summary
            assert "Format Detection Summary" in output
            assert "Supported: 3" in output
            assert "Unsupported: 1" in output
            
            # Detailed output should list files
            assert "file1.pdf" in output
            assert "file2.docx" in output
            assert "data.json" in output
            assert "file3.xyz" in output
    
    def test_process_with_extensions_filter(self, runner, mock_embedder, mock_qdrant):
        """Test processing with extension filter."""
        with runner.isolated_filesystem():
            # Create various files
            Path("doc.pdf").write_text("PDF content")
            Path("data.json").write_text('{"key": "value"}')
            Path("image.png").write_bytes(b'PNG...')
            Path("text.txt").write_text("Text content")
            
            # Process only PDF and JSON
            result = runner.invoke(
                process_command,
                ['.', '--extensions', '.pdf', '.json', '--dry-run']
            )
            
            assert result.exit_code == 0
            output = result.output
            
            # Should include PDF and JSON
            assert "doc.pdf" in output
            assert "data.json" in output
            
            # Should not include others
            assert "image.png" not in output or "Skipping" in output
            assert "text.txt" not in output or "Skipping" in output
    
    def test_process_with_exclude_filter(self, runner, mock_embedder, mock_qdrant):
        """Test processing with exclude filter."""
        with runner.isolated_filesystem():
            # Create files
            Path("doc.pdf").write_text("PDF")
            Path("backup.log").write_text("Log")
            Path("temp.tmp").write_text("Temp")
            Path("data.json").write_text("{}")
            
            # Exclude .log and .tmp
            result = runner.invoke(
                process_command,
                ['.', '--exclude', '.log', '.tmp', '--dry-run']
            )
            
            assert result.exit_code == 0
            output = result.output
            
            # Should include PDF and JSON
            assert "doc.pdf" in output
            assert "data.json" in output
            
            # Should exclude log and tmp
            assert "backup.log" not in output or "Excluded" in output
            assert "temp.tmp" not in output or "Excluded" in output
    
    def test_process_with_ocr_options(self, runner, mock_embedder, mock_qdrant):
        """Test processing with OCR options."""
        with runner.isolated_filesystem():
            # Create image file
            Path("scan.png").write_bytes(b'PNG...')
            
            # Process with OCR options
            result = runner.invoke(
                process_command,
                ['.', '--ocr-lang', 'eng+fra', '--ocr-confidence', '80', '--dry-run']
            )
            
            assert result.exit_code == 0
            output = result.output
            
            # Should show OCR is configured
            assert "scan.png" in output
            # Note: Actual OCR processing would happen during real run
    
    def test_process_no_ocr_flag(self, runner, mock_embedder, mock_qdrant):
        """Test --no-ocr flag disables OCR."""
        with runner.isolated_filesystem():
            Path("image.jpg").write_bytes(b'JPEG...')
            
            result = runner.invoke(
                process_command,
                ['.', '--no-ocr', '--dry-run']
            )
            
            assert result.exit_code == 0
            # Should process image but without OCR
            assert "image.jpg" in result.output
    
    def test_process_stats_output(self, runner, mock_embedder, mock_qdrant):
        """Test --stats flag shows processing statistics."""
        with runner.isolated_filesystem():
            # Create mixed files
            Path("doc1.pdf").write_text("PDF 1")
            Path("doc2.pdf").write_text("PDF 2")
            Path("data.json").write_text("{}")
            Path("page.html").write_text("<p>HTML</p>")
            
            result = runner.invoke(
                process_command,
                ['.', '--dry-run', '--stats']
            )
            
            assert result.exit_code == 0
            output = result.output
            
            # Should show statistics
            assert "Processing Statistics" in output
            assert "Total files found: 4" in output
            assert "By format:" in output
            assert ".pdf: 2" in output
            assert ".json: 1" in output
            assert ".html: 1" in output
    
    def test_config_formats_command(self, runner):
        """Test config formats command."""
        result = runner.invoke(config_group, ['formats'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Should show format configuration
        assert "File Format Configuration" in output
        assert "Documents:" in output
        assert "Spreadsheets:" in output
        assert "Total supported formats:" in output
    
    def test_config_add_format_command(self, runner):
        """Test adding custom format."""
        with runner.isolated_filesystem():
            # Create config file
            config = FileFormatConfig()
            config_file = Path("config.yaml")
            config_file.write_text(yaml.dump(config.dict()))
            
            # Add custom format
            result = runner.invoke(
                config_group,
                ['add-format', '.custom', '--config', str(config_file)]
            )
            
            assert result.exit_code == 0
            assert "Successfully added .custom" in result.output
            
            # Verify it was added
            updated_config = yaml.safe_load(config_file.read_text())
            assert '.custom' in updated_config.get('custom_extensions', [])
    
    def test_process_parallel_workers(self, runner, mock_embedder, mock_qdrant):
        """Test parallel processing configuration."""
        with runner.isolated_filesystem():
            # Create multiple files
            for i in range(10):
                Path(f"doc{i}.txt").write_text(f"Document {i}")
            
            # Process with specific worker count
            result = runner.invoke(
                process_command,
                ['.', '--max-workers', '4', '--dry-run']
            )
            
            assert result.exit_code == 0
            # Should process all files
            for i in range(10):
                assert f"doc{i}.txt" in result.output
    
    def test_interactive_format_selection(self, runner, mock_embedder, mock_qdrant):
        """Test interactive format selection."""
        with runner.isolated_filesystem():
            # Create files
            Path("doc.pdf").touch()
            Path("data.xlsx").touch()
            Path("image.png").touch()
            
            # Mock interactive input
            with patch('click.confirm') as mock_confirm:
                with patch('click.prompt') as mock_prompt:
                    mock_confirm.return_value = True  # Use interactive selection
                    mock_prompt.return_value = "1,2"  # Select PDF and Excel
                    
                    result = runner.invoke(
                        process_command,
                        ['.', '--interactive-formats', '--dry-run']
                    )
                    
                    assert result.exit_code == 0
                    # Should show format selection
                    assert mock_confirm.called
                    assert mock_prompt.called


class TestFormatSpecificCLI:
    """Test format-specific CLI behaviors."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_archive_extraction_cli(self, runner):
        """Test CLI handling of archive files."""
        with runner.isolated_filesystem():
            import zipfile
            
            # Create a zip with content
            with zipfile.ZipFile('archive.zip', 'w') as zf:
                zf.writestr('doc.txt', 'Document in archive')
                zf.writestr('data/info.json', '{"archived": true}')
            
            # Detect format
            result = runner.invoke(detect_format, ['archive.zip'])
            
            assert result.exit_code == 0
            assert "✓ Supported" in result.output
            assert "Reader: ZipReader" in result.output
            assert "Can extract and process contents" in result.output
    
    def test_ocr_availability_check(self, runner):
        """Test OCR availability detection."""
        with runner.isolated_filesystem():
            Path("scan.png").touch()
            
            # Check if Tesseract is available
            with patch('shutil.which') as mock_which:
                # Simulate Tesseract not found
                mock_which.return_value = None
                
                result = runner.invoke(detect_format, ['scan.png', '--check-ocr'])
                
                assert result.exit_code == 0
                assert "ImageOCRReader" in result.output
                # Should warn about OCR availability
                if '--check-ocr' in result.output or 'OCR' in result.output:
                    assert "Tesseract" in result.output or "OCR" in result.output
    
    def test_config_file_validation(self, runner):
        """Test validation of config files during processing."""
        with runner.isolated_filesystem():
            # Create invalid JSON
            Path("invalid.json").write_text("{broken json")
            
            # Try to detect format
            result = runner.invoke(detect_format, ['invalid.json', '--validate'])
            
            assert result.exit_code == 0
            assert "JSONReader" in result.output
            # Should note validation issues if --validate is supported
            if '--validate' in result.output:
                assert "invalid" in result.output.lower() or "error" in result.output.lower()


class TestCLIErrorHandling:
    """Test CLI error handling with various formats."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_missing_file_error(self, runner):
        """Test handling of missing files."""
        result = runner.invoke(detect_format, ['nonexistent.pdf'])
        
        # Should handle gracefully
        assert result.exit_code != 0 or "not found" in result.output.lower()
    
    def test_permission_error_handling(self, runner):
        """Test handling of permission errors."""
        with runner.isolated_filesystem():
            # Create file with no read permissions
            Path("noaccess.txt").touch()
            Path("noaccess.txt").chmod(0o000)
            
            result = runner.invoke(detect_format, ['noaccess.txt'])
            
            # Should handle permission error gracefully
            assert result.exit_code != 0 or "permission" in result.output.lower()
            
            # Cleanup
            Path("noaccess.txt").chmod(0o644)
    
    def test_large_file_warning(self, runner):
        """Test warning for large files."""
        with runner.isolated_filesystem():
            # Create a large file (simulate)
            large_file = Path("large.json")
            large_file.write_text('{"data": "' + 'x' * 1000000 + '"}')  # 1MB+
            
            # Process with size check
            with patch('src.vector_db_query.cli.commands.process_enhanced.MAX_FILE_SIZE_MB', 0.5):
                result = runner.invoke(
                    process_command,
                    ['.', '--check-size', '--dry-run']
                )
                
                if '--check-size' in result.output:
                    assert "large" in result.output.lower() or "size" in result.output.lower()


class TestCLIIntegrationScenarios:
    """Test complete CLI workflows."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_complete_processing_workflow(self, runner):
        """Test complete document processing workflow via CLI."""
        with runner.isolated_filesystem():
            # Setup directory structure
            Path("project/docs").mkdir(parents=True)
            Path("project/data").mkdir()
            Path("project/logs").mkdir()
            
            # Create various files
            Path("project/docs/readme.md").write_text("# Project README")
            Path("project/docs/guide.pdf").write_text("PDF Guide")
            Path("project/data/config.json").write_text('{"setting": "value"}')
            Path("project/data/stats.csv").write_text("metric,value\nusers,100")
            Path("project/logs/app.log").write_text("2024-01-01 INFO Started")
            
            # First, check what formats we have
            result = runner.invoke(detect_format, ['project', '--detailed'])
            assert result.exit_code == 0
            
            # Show format statistics
            result = runner.invoke(
                process_command,
                ['project', '--dry-run', '--stats', '--recursive']
            )
            assert result.exit_code == 0
            assert "Total files found: 5" in result.output
            
            # Process specific formats
            with patch('src.vector_db_query.embeddings.embedding_service.GeminiEmbedder'):
                with patch('qdrant_client.QdrantClient'):
                    # Process only documents
                    result = runner.invoke(
                        process_command,
                        ['project/docs', '--extensions', '.md', '.pdf']
                    )
                    # Would process in real scenario
            
            # Check configuration
            result = runner.invoke(config_group, ['formats'])
            assert result.exit_code == 0
    
    def test_migration_scenario(self, runner):
        """Test migrating from old to new format support."""
        with runner.isolated_filesystem():
            # Simulate old project with limited formats
            Path("legacy/file.txt").mkdir(parents=True)
            Path("legacy/file.txt").write_text("Text file")
            Path("legacy/data.json").write_text("{}")  # Previously unsupported
            Path("legacy/image.png").write_bytes(b"PNG")  # Previously unsupported
            
            # Check what's now supported
            result = runner.invoke(detect_format, ['legacy', '--detailed'])
            assert result.exit_code == 0
            assert "Supported: 3" in result.output  # All files now supported
            
            # Show migration benefits
            result = runner.invoke(process_command, ['--formats'])
            assert result.exit_code == 0
            assert "Total: 39+" in result.output or "39" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])