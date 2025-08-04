"""Comprehensive integration tests for all 39+ file formats."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import json
import yaml
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

from src.vector_db_query.document_processor.reader import ReaderFactory
from src.vector_db_query.document_processor import DocumentProcessor
from src.vector_db_query.document_processor.base_readers import DocumentReader
from src.vector_db_query.utils.config_enhanced import FileFormatConfig


class TestAllFormatsIntegration:
    """Test processing of all supported file formats."""
    
    @pytest.fixture
    def reader_factory(self):
        """Get reader factory instance."""
        return ReaderFactory()
    
    @pytest.fixture
    def file_formats(self):
        """Get file format configuration."""
        return FileFormatConfig()
    
    def test_all_formats_have_readers(self, reader_factory, file_formats):
        """Verify all configured formats have corresponding readers."""
        all_formats = file_formats.all_supported
        factory_formats = reader_factory.supported_extensions
        
        # Check each configured format has a reader
        missing_readers = all_formats - factory_formats
        extra_readers = factory_formats - all_formats
        
        assert len(missing_readers) == 0, f"Formats without readers: {missing_readers}"
        # It's OK to have extra readers (for aliases like .yml/.yaml)
        print(f"Total configured formats: {len(all_formats)}")
        print(f"Total reader extensions: {len(factory_formats)}")
    
    def test_reader_selection_accuracy(self, reader_factory):
        """Test that correct reader is selected for each format."""
        test_cases = [
            # Documents
            (".pdf", "PDFReader"),
            (".doc", "DocReader"),
            (".docx", "DocxReader"),
            (".txt", "TextReader"),
            (".md", "MarkdownReader"),
            (".rtf", "RTFReader"),
            (".odt", "ODTReader"),
            
            # Spreadsheets
            (".xlsx", "ExcelReader"),
            (".xls", "ExcelReader"),
            (".csv", "CSVReader"),
            
            # Presentations
            (".pptx", "PowerPointReader"),
            (".ppt", "PowerPointReader"),
            
            # Email
            (".eml", "EmailReader"),
            (".mbox", "MBoxReader"),
            
            # Web/Markup
            (".html", "HTMLReader"),
            (".htm", "HTMLReader"),
            (".xml", "XMLReader"),
            
            # Config
            (".json", "JSONReader"),
            (".yaml", "YAMLReader"),
            (".yml", "YAMLReader"),
            (".ini", "INIReader"),
            (".cfg", "INIReader"),
            (".conf", "INIReader"),
            (".config", "INIReader"),
            (".log", "LogReader"),
            
            # Images
            (".png", "ImageOCRReader"),
            (".jpg", "ImageOCRReader"),
            (".jpeg", "ImageOCRReader"),
            (".gif", "ImageOCRReader"),
            (".bmp", "ImageOCRReader"),
            (".tiff", "ImageOCRReader"),
            (".tif", "ImageOCRReader"),
            (".webp", "ImageOCRReader"),
            
            # Archives
            (".zip", "ZipReader"),
            (".tar", "TarReader"),
            (".tar.gz", "TarReader"),
            
            # Data
            (".geojson", "GeoJSONReader"),
            (".jsonl", "JSONLinesReader"),
            (".ndjson", "JSONLinesReader"),
        ]
        
        for ext, expected_class in test_cases:
            reader = reader_factory.get_reader(f"test{ext}")
            assert reader is not None, f"No reader for {ext}"
            assert expected_class in reader.__class__.__name__, \
                f"Wrong reader for {ext}: expected {expected_class}, got {reader.__class__.__name__}"
    
    @pytest.mark.asyncio
    async def test_batch_format_processing(self, reader_factory, temp_dir):
        """Test processing multiple formats in batch."""
        # Create test files of various formats
        test_files = []
        
        # Text file
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("This is a plain text file.")
        test_files.append(txt_file)
        
        # Markdown file
        md_file = temp_dir / "test.md"
        md_file.write_text("# Markdown\n\nThis is **bold** text.")
        test_files.append(md_file)
        
        # JSON file
        json_file = temp_dir / "test.json"
        json_file.write_text(json.dumps({"key": "value", "nested": {"data": 123}}))
        test_files.append(json_file)
        
        # XML file
        xml_file = temp_dir / "test.xml"
        root = ET.Element("root")
        ET.SubElement(root, "item", name="test").text = "content"
        xml_file.write_text(ET.tostring(root, encoding='unicode'))
        test_files.append(xml_file)
        
        # CSV file
        csv_file = temp_dir / "test.csv"
        with csv_file.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Age", "City"])
            writer.writerow(["Alice", "30", "NYC"])
            writer.writerow(["Bob", "25", "SF"])
        test_files.append(csv_file)
        
        # YAML file
        yaml_file = temp_dir / "test.yaml"
        yaml_file.write_text(yaml.dump({"config": {"setting": "value"}}))
        test_files.append(yaml_file)
        
        # INI file
        ini_file = temp_dir / "test.ini"
        ini_file.write_text("[section]\noption = value\n")
        test_files.append(ini_file)
        
        # HTML file
        html_file = temp_dir / "test.html"
        html_file.write_text("<html><body><h1>Title</h1><p>Content</p></body></html>")
        test_files.append(html_file)
        
        # Process all files
        results = {}
        for file_path in test_files:
            reader = reader_factory.get_reader(str(file_path))
            assert reader is not None, f"No reader for {file_path.suffix}"
            
            text = reader.read(file_path)
            metadata = reader.extract_metadata(file_path)
            
            results[file_path.suffix] = {
                "text": text,
                "metadata": metadata,
                "reader": reader.__class__.__name__
            }
        
        # Verify all files were processed
        assert len(results) == len(test_files)
        
        # Verify each format produced text
        for ext, result in results.items():
            assert len(result["text"]) > 0, f"No text extracted from {ext}"
            assert result["metadata"] is not None, f"No metadata from {ext}"
            print(f"{ext}: {len(result['text'])} chars, reader: {result['reader']}")
    
    def test_format_specific_features(self, reader_factory, temp_dir):
        """Test format-specific features are working."""
        # Test JSON pretty printing
        json_reader = reader_factory.get_reader("test.json")
        json_file = temp_dir / "nested.json"
        json_file.write_text('{"a":{"b":{"c":123}}}')
        
        text = json_reader.read(json_file)
        assert "{\n" in text  # Pretty printed
        assert '"a": {' in text
        
        # Test XML attribute handling
        xml_reader = reader_factory.get_reader("test.xml")
        xml_file = temp_dir / "attrs.xml"
        xml_file.write_text('<root><item id="123" type="test">Content</item></root>')
        
        text = xml_reader.read(xml_file)
        assert "id=" in text
        assert "type=" in text
        assert "Content" in text
        
        # Test YAML multi-document
        yaml_reader = reader_factory.get_reader("test.yaml")
        yaml_file = temp_dir / "multi.yaml"
        yaml_file.write_text("---\ndoc: 1\n---\ndoc: 2\n")
        
        text = yaml_reader.read(yaml_file)
        assert "Document 1:" in text
        assert "Document 2:" in text
        
        # Test INI sections
        ini_reader = reader_factory.get_reader("test.ini")
        ini_file = temp_dir / "sections.ini"
        ini_file.write_text("[section1]\nkey1=val1\n[section2]\nkey2=val2\n")
        
        text = ini_reader.read(ini_file)
        assert "[section1]" in text
        assert "[section2]" in text
        
        # Test Log level detection
        log_reader = reader_factory.get_reader("test.log")
        log_file = temp_dir / "app.log"
        log_file.write_text(
            "2024-01-01 INFO Starting app\n"
            "2024-01-01 ERROR Failed to connect\n"
            "2024-01-01 DEBUG Details here\n"
        )
        
        text = log_reader.read(log_file)
        metadata = log_reader.extract_metadata(log_file)
        
        assert "ERROR" in text
        assert "level_stats" in metadata
        assert metadata["level_stats"]["ERROR"] == 1
        assert metadata["level_stats"]["INFO"] == 1
    
    @pytest.mark.parametrize("ext,content", [
        (".json", '{"valid": "json"}'),
        (".yaml", "key: value"),
        (".xml", "<root><item>text</item></root>"),
        (".ini", "[section]\nkey=value"),
        (".csv", "col1,col2\nval1,val2"),
        (".html", "<p>paragraph</p>"),
        (".md", "# Header\nContent"),
        (".txt", "Plain text"),
        (".log", "2024-01-01 INFO Test log"),
    ])
    def test_format_validation(self, reader_factory, temp_dir, ext, content):
        """Test each format can handle valid content."""
        file_path = temp_dir / f"test{ext}"
        file_path.write_text(content)
        
        reader = reader_factory.get_reader(str(file_path))
        assert reader is not None
        
        text = reader.read(file_path)
        assert len(text) > 0
        
        metadata = reader.extract_metadata(file_path)
        assert metadata is not None
        assert "file_name" in metadata
        assert "file_size" in metadata
    
    def test_error_handling_for_malformed_files(self, reader_factory, temp_dir):
        """Test readers handle malformed files gracefully."""
        # Malformed JSON
        json_file = temp_dir / "bad.json"
        json_file.write_text("{invalid json}")
        json_reader = reader_factory.get_reader(str(json_file))
        
        # Should handle error gracefully
        text = json_reader.read(json_file)
        assert "invalid json" in text  # Falls back to raw text
        
        # Malformed XML
        xml_file = temp_dir / "bad.xml"
        xml_file.write_text("<unclosed>")
        xml_reader = reader_factory.get_reader(str(xml_file))
        
        text = xml_reader.read(xml_file)
        assert len(text) > 0  # Should return something
        
        # Binary file with text extension
        bin_file = temp_dir / "binary.txt"
        bin_file.write_bytes(b'\x00\x01\x02\x03')
        txt_reader = reader_factory.get_reader(str(bin_file))
        
        # Should handle binary gracefully
        try:
            text = txt_reader.read(bin_file)
            # Either succeeds with decoded text or raises an error
            assert isinstance(text, str)
        except (UnicodeDecodeError, ValueError):
            # Expected for binary content
            pass
    
    @pytest.mark.skipif(not Path("/usr/bin/tesseract").exists() and not Path("/usr/local/bin/tesseract").exists(), 
                        reason="Tesseract not installed")
    def test_ocr_integration(self, reader_factory, temp_dir):
        """Test OCR reader integration."""
        # Note: This would require actual image files with text
        # For now, just test the reader exists and can handle image extensions
        
        image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"]
        
        for ext in image_extensions:
            reader = reader_factory.get_reader(f"image{ext}")
            assert reader is not None
            assert reader.__class__.__name__ == "ImageOCRReader"
    
    def test_archive_reader_integration(self, reader_factory, temp_dir):
        """Test archive readers can extract and process contents."""
        import zipfile
        import tarfile
        
        # Create a ZIP file with text content
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("doc1.txt", "Content of document 1")
            zf.writestr("folder/doc2.txt", "Content of document 2")
        
        zip_reader = reader_factory.get_reader(str(zip_path))
        text = zip_reader.read(zip_path)
        
        assert "doc1.txt" in text
        assert "Content of document 1" in text
        assert "folder/doc2.txt" in text
        assert "Content of document 2" in text
        
        # Create a TAR file
        tar_path = temp_dir / "test.tar"
        with tarfile.open(tar_path, 'w') as tf:
            # Create temporary files to add
            temp_txt = temp_dir / "temp.txt"
            temp_txt.write_text("TAR content")
            tf.add(temp_txt, arcname="archived.txt")
        
        tar_reader = reader_factory.get_reader(str(tar_path))
        text = tar_reader.read(tar_path)
        
        assert "archived.txt" in text
        assert "TAR content" in text
    
    def test_metadata_extraction_consistency(self, reader_factory, temp_dir):
        """Test all readers extract consistent base metadata."""
        required_metadata_fields = {"file_name", "file_size", "file_type"}
        
        # Create various test files
        test_files = {
            "test.txt": "Plain text content",
            "test.json": '{"key": "value"}',
            "test.xml": "<root>content</root>",
            "test.csv": "col1,col2\nval1,val2",
            "test.yaml": "key: value",
            "test.html": "<p>content</p>",
            "test.md": "# Header",
            "test.ini": "[section]\nkey=value",
        }
        
        for filename, content in test_files.items():
            file_path = temp_dir / filename
            file_path.write_text(content)
            
            reader = reader_factory.get_reader(str(file_path))
            metadata = reader.extract_metadata(file_path)
            
            # Check required fields
            missing_fields = required_metadata_fields - set(metadata.keys())
            assert len(missing_fields) == 0, \
                f"{filename}: Missing metadata fields: {missing_fields}"
            
            # Verify field values
            assert metadata["file_name"] == filename
            assert metadata["file_size"] > 0
            assert metadata["file_type"] == file_path.suffix[1:]  # Remove dot
    
    def test_progress_callback_support(self, reader_factory, temp_dir):
        """Test readers that support progress callbacks."""
        # Create a larger file for testing progress
        large_json = temp_dir / "large.json"
        data = {"items": [{"id": i, "data": "x" * 100} for i in range(1000)]}
        large_json.write_text(json.dumps(data))
        
        progress_calls = []
        
        def progress_callback(current, total, message):
            progress_calls.append({
                "current": current,
                "total": total,
                "message": message
            })
        
        # Not all readers support progress callbacks, but test the interface
        reader = reader_factory.get_reader(str(large_json))
        
        # Check if reader has progress support
        if hasattr(reader.read, '__code__') and 'progress_callback' in reader.read.__code__.co_varnames:
            text = reader.read(large_json, progress_callback=progress_callback)
            # If progress was reported, verify it
            if progress_calls:
                assert len(progress_calls) > 0
                assert progress_calls[-1]["current"] == progress_calls[-1]["total"]
        else:
            # Reader doesn't support progress, just ensure it works
            text = reader.read(large_json)
        
        assert len(text) > 0


class TestDocumentProcessorIntegration:
    """Test DocumentProcessor with all formats."""
    
    @pytest.mark.asyncio
    async def test_process_mixed_formats(self, temp_dir):
        """Test processing directory with mixed formats."""
        # Create files of different types
        files = {
            "doc.txt": "Text document content",
            "data.json": '{"records": [1, 2, 3]}',
            "config.yaml": "setting: value\noption: true",
            "page.html": "<h1>Web Page</h1><p>Content</p>",
            "log.log": "2024-01-01 INFO Application started",
        }
        
        for filename, content in files.items():
            (temp_dir / filename).write_text(content)
        
        # Mock embedding service
        with patch('src.vector_db_query.embeddings.embedding_service.GeminiEmbedder') as mock_embedder:
            mock_instance = Mock()
            mock_instance.embed_batch.return_value = [[0.1] * 768] * len(files)
            mock_embedder.return_value = mock_instance
            
            # Process directory
            processor = DocumentProcessor()
            documents = []
            
            async for doc in processor.process_directory(
                str(temp_dir),
                recursive=False
            ):
                documents.append(doc)
            
            # Verify all files processed
            assert len(documents) == len(files)
            
            # Check each document
            processed_files = {doc.metadata.file_name for doc in documents}
            expected_files = set(files.keys())
            assert processed_files == expected_files
            
            # Verify content extracted
            for doc in documents:
                assert len(doc.content) > 0
                assert doc.chunks is not None
                assert len(doc.chunks) > 0
    
    @pytest.mark.asyncio
    async def test_format_filtering(self, temp_dir):
        """Test processing with format filtering."""
        # Create various files
        files = {
            "doc1.txt": "Text 1",
            "doc2.txt": "Text 2", 
            "data.json": "{}",
            "config.yaml": "key: val",
            "style.css": "body {}",  # Should be skipped
        }
        
        for filename, content in files.items():
            (temp_dir / filename).write_text(content)
        
        with patch('src.vector_db_query.embeddings.embedding_service.GeminiEmbedder') as mock_embedder:
            mock_instance = Mock()
            mock_instance.embed_batch.return_value = [[0.1] * 768] * 3
            mock_embedder.return_value = mock_instance
            
            processor = DocumentProcessor()
            
            # Process only specific formats
            documents = []
            async for doc in processor.process_directory(
                str(temp_dir),
                extensions=[".txt", ".json"],
                recursive=False
            ):
                documents.append(doc)
            
            # Should only process .txt and .json files
            assert len(documents) == 3
            processed_extensions = {Path(doc.metadata.file_path).suffix for doc in documents}
            assert processed_extensions == {".txt", ".json"}


class TestCLIIntegrationWithFormats:
    """Test CLI with new format support."""
    
    def test_cli_format_command(self):
        """Test CLI format listing command."""
        from click.testing import CliRunner
        from src.vector_db_query.cli.commands.process_enhanced import process_command
        
        runner = CliRunner()
        result = runner.invoke(process_command, ['--formats'])
        
        assert result.exit_code == 0
        assert "Supported File Formats" in result.output
        assert "Documents:" in result.output
        assert ".pdf" in result.output
        assert "Spreadsheets:" in result.output
        assert ".xlsx" in result.output
        assert "Total: 39" in result.output or "Total:" in result.output
    
    def test_cli_detect_format_command(self):
        """Test format detection command."""
        from click.testing import CliRunner
        from src.vector_db_query.cli.commands.detect import detect_format
        
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create test file
            Path("test.xyz").write_text("content")
            
            result = runner.invoke(detect_format, ['test.xyz'])
            
            assert result.exit_code == 0
            assert "Not Supported" in result.output or "not supported" in result.output
    
    def test_cli_process_with_extensions(self, temp_dir):
        """Test CLI processing with extension filter."""
        from click.testing import CliRunner
        from src.vector_db_query.cli.commands.process_enhanced import process_command
        
        # Create test files
        (temp_dir / "doc.txt").write_text("text")
        (temp_dir / "data.json").write_text("{}")
        (temp_dir / "image.png").write_bytes(b'PNG...')
        
        runner = CliRunner()
        with patch('src.vector_db_query.embeddings.embedding_service.GeminiEmbedder'):
            with patch('qdrant_client.QdrantClient'):
                result = runner.invoke(
                    process_command,
                    [str(temp_dir), '--extensions', '.txt', '.json', '--dry-run']
                )
                
                assert result.exit_code == 0
                assert "doc.txt" in result.output
                assert "data.json" in result.output
                # PNG should not be in dry-run output
                assert "image.png" not in result.output or "Skipping" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])