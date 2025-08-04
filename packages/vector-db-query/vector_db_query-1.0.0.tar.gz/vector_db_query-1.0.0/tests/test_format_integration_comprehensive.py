"""Comprehensive integration tests for all file format processing."""

import pytest
import tempfile
import shutil
from pathlib import Path
import json
import yaml
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import psutil
import os

from vector_db_query.document_processor import DocumentProcessor
from vector_db_query.document_processor.reader import ReaderFactory
from vector_db_query.document_processor.scanner import FileScanner
from vector_db_query.utils.config import get_config
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class TestFormatIntegration:
    """Integration tests for file format processing."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path, ignore_errors=True)
        
    @pytest.fixture
    def processor(self):
        """Create document processor instance."""
        from vector_db_query.document_processor.chunker import SlidingWindowChunker
        processor = DocumentProcessor(
            chunk_size=500,  # Smaller chunks for testing
            chunk_overlap=50,
            enable_ocr=False  # Disable OCR for base tests
        )
        # Set min_chunk_size to 10 for testing small files
        if hasattr(processor.chunker, 'min_chunk_size'):
            processor.chunker.min_chunk_size = 10
        return processor
        
    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files of various formats."""
        files = {}
        
        # Text documents
        files['text'] = temp_dir / "sample.txt"
        files['text'].write_text("This is a sample text document for testing. " * 10 + 
                                "It contains multiple sentences to ensure proper chunking. " * 5)
        
        files['markdown'] = temp_dir / "sample.md"
        files['markdown'].write_text("# Sample Markdown\n\n" + 
                                   "This is **bold** and _italic_ text. " * 5 +
                                   "\n\n## Section 2\n\n" + 
                                   "More content to ensure sufficient length for chunking. " * 10)
        
        # Configuration files
        files['json'] = temp_dir / "config.json"
        json_data = {
            "name": "test",
            "version": "1.0",
            "description": "This is a test configuration file with more content for testing purposes.",
            "settings": {
                "debug": True,
                "verbose": False,
                "log_level": "INFO",
                "max_connections": 100,
                "timeout": 30
            },
            "features": ["feature1", "feature2", "feature3"],
            "metadata": {
                "created": "2025-07-31",
                "author": "Test Suite",
                "tags": ["test", "integration", "json"]
            }
        }
        files['json'].write_text(json.dumps(json_data, indent=2))
        
        files['yaml'] = temp_dir / "config.yaml"
        yaml_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "testdb",
                "user": "testuser",
                "pool_size": 10,
                "ssl_mode": "require"
            },
            "application": {
                "name": "Test App",
                "version": "2.0.0",
                "environment": "testing",
                "features": ["logging", "caching", "monitoring"]
            },
            "services": {
                "redis": {"host": "localhost", "port": 6379},
                "elasticsearch": {"host": "localhost", "port": 9200}
            }
        }
        files['yaml'].write_text(yaml.dump(yaml_data))
        
        files['ini'] = temp_dir / "settings.ini"
        files['ini'].write_text("""[General]
name = Test Application
version = 1.0
description = This is a test INI configuration file with additional content for proper testing
debug = true
log_level = INFO

[Database]
host = localhost
port = 5432
database = testdb
username = testuser
password = testpass
pool_size = 20
timeout = 30

[Features]
enable_caching = true
enable_logging = true
enable_monitoring = false
max_retries = 3

[Paths]
data_dir = /var/data
log_dir = /var/log
temp_dir = /tmp
""")
        
        # Data files
        files['csv'] = temp_dir / "data.csv"
        with files['csv'].open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Age', 'City', 'Department', 'Salary', 'Start_Date', 'Email'])
            for i in range(20):
                writer.writerow([
                    f'{1000+i}', 
                    f'Person_{i}', 
                    f'{25+i}', 
                    ['New York', 'London', 'Paris', 'Tokyo', 'Sydney'][i % 5],
                    ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance'][i % 5],
                    f'{50000 + i * 1000}',
                    f'2020-{(i % 12) + 1:02d}-01',
                    f'person{i}@example.com'
                ])
        
        files['xml'] = temp_dir / "data.xml"
        root = ET.Element("data")
        for i in range(10):
            item = ET.SubElement(root, "item", id=str(i+1))
            ET.SubElement(item, "name").text = f"Test Item {i+1}"
            ET.SubElement(item, "description").text = f"This is a test item with ID {i+1} for integration testing"
            ET.SubElement(item, "value").text = str(100 + i * 10)
            ET.SubElement(item, "category").text = ["A", "B", "C"][i % 3]
            ET.SubElement(item, "active").text = "true" if i % 2 == 0 else "false"
        files['xml'].write_text(ET.tostring(root, encoding='unicode'))
        
        # Log file
        files['log'] = temp_dir / "app.log"
        log_content = []
        for i in range(30):
            timestamp = f"2025-07-31 10:{i//60:02d}:{i%60:02d}"
            level = ["INFO", "DEBUG", "WARNING", "ERROR"][i % 4]
            messages = [
                "Application started successfully",
                "Loading configuration from config.yaml",
                "Database connection established to localhost:5432",
                "User authentication successful for user_123",
                "Processing request ID: REQ-" + str(1000 + i),
                "Cache hit ratio: 85%",
                "Memory usage: 512MB",
                "Failed to connect to external service: timeout",
                "Retrying connection attempt 1 of 3",
                "Successfully processed 1000 records"
            ]
            log_content.append(f"{timestamp} {level} {messages[i % len(messages)]}")
        files['log'].write_text("\n".join(log_content))
        
        # HTML file
        files['html'] = temp_dir / "page.html"
        files['html'].write_text("""<!DOCTYPE html>
<html>
<head>
    <title>Test Page - Integration Testing</title>
    <meta charset="UTF-8">
    <meta name="description" content="Test page for document processing integration tests">
    <script>console.log('test'); function doSomething() { return 42; }</script>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
        .content { max-width: 800px; margin: 0 auto; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <header>
        <h1>Test Page for Integration Testing</h1>
        <nav>
            <a href="#section1">Section 1</a> | 
            <a href="#section2">Section 2</a> | 
            <a href="#section3">Section 3</a>
        </nav>
    </header>
    
    <main class="content">
        <section id="section1">
            <h2>Introduction</h2>
            <p>This is a test HTML page designed for testing the document processing system. It contains various HTML elements to ensure proper text extraction.</p>
            <p>Here's another paragraph with <strong>bold text</strong>, <em>italic text</em>, and a <a href="https://example.com">link to example.com</a>.</p>
        </section>
        
        <section id="section2">
            <h2>Features</h2>
            <ul>
                <li>List item 1: Text extraction</li>
                <li>List item 2: Script and style removal</li>
                <li>List item 3: Structure preservation</li>
                <li>List item 4: Link handling</li>
            </ul>
            <p>The document processor should handle all these elements correctly.</p>
        </section>
        
        <section id="section3">
            <h2>Data Table</h2>
            <table>
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th>Status</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Text Extraction</td>
                        <td>Supported</td>
                        <td>Extracts all visible text</td>
                    </tr>
                    <tr>
                        <td>Script Removal</td>
                        <td>Supported</td>
                        <td>JavaScript code is removed</td>
                    </tr>
                    <tr>
                        <td>Style Removal</td>
                        <td>Supported</td>
                        <td>CSS styles are removed</td>
                    </tr>
                </tbody>
            </table>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2025 Test Suite. All rights reserved.</p>
    </footer>
</body>
</html>""")
        
        return files
        
    def test_mixed_format_processing(self, processor, sample_files):
        """Test processing multiple file formats in one batch."""
        # Process all sample files
        start_time = time.time()
        
        documents = list(processor.process_files(list(sample_files.values())))
        
        processing_time = time.time() - start_time
        
        # Verify all files were processed
        assert len(documents) == len(sample_files)
        
        # Check each document
        for doc in documents:
            assert doc.file_path.exists()
            assert len(doc.chunks) > 0
            assert doc.metadata is not None
            assert doc.processing_time > 0
            
            # Verify metadata
            assert doc.metadata.file_size > 0
            assert doc.metadata.file_type in ['.txt', '.md', '.json', '.yaml', '.ini', '.csv', '.xml', '.log', '.html']
            
        # Performance check
        assert processing_time < 10.0, f"Processing took too long: {processing_time:.2f}s"
        
        logger.info(f"Processed {len(documents)} files in {processing_time:.2f}s")
        
    def test_format_specific_extraction(self, processor, sample_files):
        """Test format-specific feature extraction."""
        # Process specific formats with custom settings
        processor_with_settings = DocumentProcessor(
            chunk_size=500,
            chunk_overlap=50
        )
        
        # Test JSON structure preservation
        json_doc = processor_with_settings.process_file(sample_files['json'])
        json_text = ' '.join(chunk.text for chunk in json_doc.chunks)
        assert '"name": "test"' in json_text
        assert '"version": "1.0"' in json_text
        
        # Test YAML processing
        yaml_doc = processor_with_settings.process_file(sample_files['yaml'])
        yaml_text = ' '.join(chunk.text for chunk in yaml_doc.chunks)
        assert 'database:' in yaml_text or 'host: localhost' in yaml_text
        
        # Test CSV table extraction
        csv_doc = processor_with_settings.process_file(sample_files['csv'])
        csv_text = ' '.join(chunk.text for chunk in csv_doc.chunks)
        assert 'Person_0' in csv_text
        assert 'Engineering' in csv_text
        assert 'New York' in csv_text
        
        # Test HTML with script/style removal
        html_doc = processor_with_settings.process_file(sample_files['html'])
        html_text = ' '.join(chunk.text for chunk in html_doc.chunks)
        assert 'Test Page' in html_text
        assert 'console.log' not in html_text  # Script removed
        assert 'margin: 0' not in html_text  # Style removed
        
        # Test log file processing
        log_doc = processor_with_settings.process_file(sample_files['log'])
        log_text = ' '.join(chunk.text for chunk in log_doc.chunks)
        assert 'ERROR Failed to load user data' in log_text
        assert 'WARNING High memory usage' in log_text
        
    def test_batch_processing_performance(self, processor, temp_dir):
        """Test performance with large batch of files."""
        # Create 100 test files of various formats
        test_files = []
        formats = ['.txt', '.json', '.csv', '.xml', '.log']
        
        for i in range(100):
            fmt = formats[i % len(formats)]
            file_path = temp_dir / f"test_{i}{fmt}"
            
            if fmt == '.txt':
                file_path.write_text(f"Test document {i}\n" * 10)
            elif fmt == '.json':
                file_path.write_text(json.dumps({"id": i, "data": f"test_{i}"}))
            elif fmt == '.csv':
                with file_path.open('w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['id', 'value'])
                    writer.writerow([i, f'test_{i}'])
            elif fmt == '.xml':
                file_path.write_text(f'<root><item id="{i}">test_{i}</item></root>')
            elif fmt == '.log':
                file_path.write_text(f"2025-07-31 10:00:{i:02d} INFO Test log entry {i}")
                
            test_files.append(file_path)
            
        # Measure performance
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        documents = list(processor.process_files(test_files))
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        processing_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        # Verify results
        assert len(documents) == 100
        assert all(doc.chunks for doc in documents)
        
        # Performance benchmarks
        files_per_second = 100 / processing_time
        assert files_per_second > 5, f"Too slow: {files_per_second:.2f} files/sec"
        assert memory_used < 500, f"Too much memory used: {memory_used:.2f} MB"
        
        logger.info(f"Performance: {files_per_second:.2f} files/sec, Memory: {memory_used:.2f} MB")
        
    def test_error_handling(self, processor, temp_dir):
        """Test error handling for various scenarios."""
        errors = []
        
        # Non-existent file
        try:
            processor.process_file(temp_dir / "nonexistent.txt")
        except Exception as e:
            errors.append(("nonexistent", type(e).__name__))
            
        # Corrupted file
        corrupted = temp_dir / "corrupted.json"
        corrupted.write_text("{invalid json")
        doc = processor.process_file(corrupted)
        if doc.errors:
            errors.append(("corrupted_json", doc.errors[0].error_type))
            
        # Empty file
        empty = temp_dir / "empty.txt"
        empty.write_text("")
        doc = processor.process_file(empty)
        # Empty files should still process without errors
        assert len(doc.errors) == 0 or doc.errors[0].recoverable
        
        # Unsupported format (if any)
        unsupported = temp_dir / "test.xyz"
        unsupported.write_text("unsupported format")
        try:
            processor.process_file(unsupported)
        except Exception as e:
            errors.append(("unsupported", type(e).__name__))
            
        # Verify error handling
        assert len(errors) >= 2  # At least nonexistent and unsupported
        logger.info(f"Handled errors: {errors}")
        
    def test_memory_usage_large_files(self, processor, temp_dir):
        """Test memory usage with large files."""
        # Create a large text file (10 MB)
        large_file = temp_dir / "large.txt"
        chunk = "This is a test line that will be repeated many times.\n" * 100
        
        with large_file.open('w') as f:
            for _ in range(2000):  # ~10 MB
                f.write(chunk)
                
        # Monitor memory during processing
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        doc = processor.process_file(large_file)
        
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = peak_memory - start_memory
        
        # Verify processing
        assert len(doc.chunks) > 0
        assert doc.metadata.file_size > 10 * 1024 * 1024  # > 10 MB
        
        # Memory should not increase by more than 2x file size
        assert memory_increase < 20, f"Memory increase too high: {memory_increase:.2f} MB"
        
        logger.info(f"Large file processing - Memory increase: {memory_increase:.2f} MB")
        
    def test_concurrent_processing(self, processor, sample_files):
        """Test concurrent processing of multiple files."""
        import concurrent.futures
        
        # Process files concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for file_path in sample_files.values():
                future = executor.submit(processor.process_file, file_path)
                futures.append(future)
                
            # Wait for all to complete
            documents = [f.result() for f in concurrent.futures.as_completed(futures)]
            
        # Verify all processed successfully
        assert len(documents) == len(sample_files)
        assert all(len(doc.chunks) > 0 for doc in documents)
        
    def test_format_filtering(self, temp_dir):
        """Test processing with format filtering."""
        # Create files of different formats
        files = []
        files.append(temp_dir / "doc1.txt")
        files[-1].write_text("Text document")
        files.append(temp_dir / "doc2.pdf")
        files[-1].write_text("PDF content")  # Mock PDF
        files.append(temp_dir / "doc3.json")
        files[-1].write_text('{"key": "value"}')
        files.append(temp_dir / "doc4.xml")
        files[-1].write_text('<root>XML content</root>')
        
        # Process only text and JSON
        processor = DocumentProcessor(allowed_formats=['txt', 'json'])
        
        # Scan directory with filter
        scanner = FileScanner(allowed_formats=['.txt', '.json'])
        found_files = list(scanner.scan_directory(temp_dir))
        
        assert len(found_files) == 2
        assert all(f.suffix in ['.txt', '.json'] for f in found_files)
        
        # Process filtered files
        documents = list(processor.process_files(found_files))
        assert len(documents) == 2
        
    @pytest.mark.skipif(not os.environ.get('TEST_OCR'), reason="OCR tests require TEST_OCR=1")
    def test_ocr_integration(self, temp_dir):
        """Test OCR integration if available."""
        try:
            from vector_db_query.document_processor.image_ocr_reader import check_ocr_available
            if not check_ocr_available():
                pytest.skip("OCR not available")
        except ImportError:
            pytest.skip("OCR module not available")
            
        # Create processor with OCR enabled
        processor = DocumentProcessor(
            enable_ocr=True,
            ocr_language="eng"
        )
        
        # Create a simple image file (would need PIL for real image)
        # For now, just verify OCR configuration
        assert processor.enable_ocr
        assert processor.ocr_language == "eng"
        
    def test_configuration_integration(self):
        """Test integration with configuration system."""
        # Test with custom config
        config = get_config()
        
        # Update config for testing
        original_chunk_size = config.get("document_processing.chunk_size")
        config.set("document_processing.chunk_size", 1000)
        
        try:
            # Create processor with config
            processor = DocumentProcessor()
            assert processor.chunk_size == 1000
        finally:
            # Restore original config
            if original_chunk_size:
                config.set("document_processing.chunk_size", original_chunk_size)


class TestCLIIntegration:
    """Test CLI command integration."""
    
    def test_formats_command(self):
        """Test the formats CLI command."""
        from click.testing import CliRunner
        from vector_db_query.cli.main import cli
        
        runner = CliRunner()
        result = runner.invoke(cli, ['formats'])
        
        assert result.exit_code == 0
        assert 'File Format Information' in result.output
        assert 'Documents' in result.output
        assert 'Spreadsheets' in result.output
        assert 'Total supported extensions:' in result.output
        
    def test_process_with_formats(self, temp_dir):
        """Test process command with format filtering."""
        from click.testing import CliRunner
        from vector_db_query.cli.main import cli
        
        # Create test files
        (temp_dir / "test.txt").write_text("Text file")
        (temp_dir / "test.json").write_text('{"key": "value"}')
        (temp_dir / "test.xml").write_text('<root>XML</root>')
        
        runner = CliRunner()
        
        # Test dry run with format filter
        result = runner.invoke(cli, [
            'process',
            '--folder', str(temp_dir),
            '--formats', 'txt,json',
            '--dry-run'
        ])
        
        assert result.exit_code == 0
        assert 'Would process' in result.output
        # Should only mention txt and json files
        assert 'test.txt' in result.output or 'txt' in result.output
        assert 'test.json' in result.output or 'json' in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])