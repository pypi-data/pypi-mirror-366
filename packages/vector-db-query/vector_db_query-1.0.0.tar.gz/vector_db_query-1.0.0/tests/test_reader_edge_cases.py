"""Edge case tests for all document readers."""

import pytest
from pathlib import Path
import tempfile
import json
import yaml
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import zipfile
import tarfile

from src.vector_db_query.document_processor.reader import ReaderFactory
from src.vector_db_query.document_processor.base_readers import DocumentReader


class TestReaderEdgeCases:
    """Test edge cases for all readers."""
    
    @pytest.fixture
    def reader_factory(self):
        """Get reader factory instance."""
        return ReaderFactory()
    
    def test_empty_files(self, reader_factory, temp_dir):
        """Test readers handle empty files gracefully."""
        empty_files = {
            "empty.txt": "",
            "empty.json": "",
            "empty.yaml": "",
            "empty.xml": "",
            "empty.csv": "",
            "empty.html": "",
            "empty.md": "",
            "empty.ini": "",
            "empty.log": "",
        }
        
        for filename, content in empty_files.items():
            file_path = temp_dir / filename
            file_path.write_text(content)
            
            reader = reader_factory.get_reader(str(file_path))
            
            # Should not raise exception
            text = reader.read(file_path)
            metadata = reader.extract_metadata(file_path)
            
            # Should return valid but possibly empty results
            assert isinstance(text, str)
            assert isinstance(metadata, dict)
            assert metadata["file_size"] == 0
    
    def test_large_files(self, reader_factory, temp_dir):
        """Test readers handle large files efficiently."""
        # Create a large JSON file
        large_data = {"items": [{"id": i, "data": "x" * 1000} for i in range(100)]}
        large_json = temp_dir / "large.json"
        large_json.write_text(json.dumps(large_data))
        
        json_reader = reader_factory.get_reader(str(large_json))
        text = json_reader.read(large_json)
        
        assert len(text) > 100000  # Should be quite large
        assert "items" in text
        
        # Create a large CSV file
        large_csv = temp_dir / "large.csv"
        with large_csv.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["col1", "col2", "col3"])
            for i in range(1000):
                writer.writerow([f"val{i}_1", f"val{i}_2", f"val{i}_3"])
        
        csv_reader = reader_factory.get_reader(str(large_csv))
        text = csv_reader.read(large_csv)
        
        assert "col1" in text
        assert "val999_1" in text  # Last row
    
    def test_unicode_handling(self, reader_factory, temp_dir):
        """Test readers handle Unicode content correctly."""
        unicode_content = "Hello 世界 🌍 Привет مرحبا"
        
        unicode_files = {
            "unicode.txt": unicode_content,
            "unicode.json": json.dumps({"message": unicode_content}),
            "unicode.yaml": yaml.dump({"message": unicode_content}),
            "unicode.xml": f'<root><msg>{unicode_content}</msg></root>',
            "unicode.html": f'<p>{unicode_content}</p>',
            "unicode.md": f'# {unicode_content}',
        }
        
        for filename, content in unicode_files.items():
            file_path = temp_dir / filename
            file_path.write_text(content, encoding='utf-8')
            
            reader = reader_factory.get_reader(str(file_path))
            text = reader.read(file_path)
            
            # Should preserve Unicode characters
            assert "世界" in text
            assert "🌍" in text
            assert "Привет" in text
            assert "مرحبا" in text
    
    def test_special_characters_in_filenames(self, reader_factory, temp_dir):
        """Test readers handle special characters in filenames."""
        special_files = [
            "file with spaces.txt",
            "file-with-dashes.json",
            "file_with_underscores.yaml",
            "file.multiple.dots.xml",
            "file(with)parens.html",
            "file[with]brackets.md",
        ]
        
        for filename in special_files:
            file_path = temp_dir / filename
            file_path.write_text("test content")
            
            reader = reader_factory.get_reader(str(file_path))
            assert reader is not None
            
            text = reader.read(file_path)
            metadata = reader.extract_metadata(file_path)
            
            assert len(text) > 0
            assert metadata["file_name"] == filename
    
    def test_nested_structures(self, reader_factory, temp_dir):
        """Test readers handle deeply nested structures."""
        # Deeply nested JSON
        nested_json = {"level1": {"level2": {"level3": {"level4": {"level5": "deep value"}}}}}
        json_file = temp_dir / "nested.json"
        json_file.write_text(json.dumps(nested_json))
        
        json_reader = reader_factory.get_reader(str(json_file))
        text = json_reader.read(json_file)
        assert "level5" in text
        assert "deep value" in text
        
        # Deeply nested XML
        xml_file = temp_dir / "nested.xml"
        root = ET.Element("root")
        current = root
        for i in range(5):
            child = ET.SubElement(current, f"level{i}")
            current = child
        current.text = "deep content"
        xml_file.write_text(ET.tostring(root, encoding='unicode'))
        
        xml_reader = reader_factory.get_reader(str(xml_file))
        text = xml_reader.read(xml_file)
        assert "deep content" in text
        
        # Nested YAML
        yaml_file = temp_dir / "nested.yaml"
        nested_yaml = {"a": {"b": {"c": {"d": {"e": "nested"}}}}}
        yaml_file.write_text(yaml.dump(nested_yaml))
        
        yaml_reader = reader_factory.get_reader(str(yaml_file))
        text = yaml_reader.read(yaml_file)
        assert "nested" in text
    
    def test_malformed_but_recoverable(self, reader_factory, temp_dir):
        """Test readers can recover from minor format issues."""
        # JSON with trailing comma (common mistake)
        json_file = temp_dir / "trailing_comma.json"
        json_file.write_text('{"a": 1, "b": 2,}')  # Invalid JSON
        
        json_reader = reader_factory.get_reader(str(json_file))
        text = json_reader.read(json_file)
        # Should fall back to raw text
        assert '"a": 1' in text
        
        # XML without proper closing
        xml_file = temp_dir / "unclosed.xml"
        xml_file.write_text('<root><item>text</root>')  # Missing </item>
        
        xml_reader = reader_factory.get_reader(str(xml_file))
        text = xml_reader.read(xml_file)
        assert len(text) > 0
        
        # CSV with inconsistent columns
        csv_file = temp_dir / "inconsistent.csv"
        csv_file.write_text("col1,col2,col3\nval1,val2\nval3,val4,val5,val6")
        
        csv_reader = reader_factory.get_reader(str(csv_file))
        text = csv_reader.read(csv_file)
        assert "val1" in text
        assert "val6" in text
    
    def test_binary_content_handling(self, reader_factory, temp_dir):
        """Test readers handle files with binary content."""
        # Text file with some binary
        mixed_file = temp_dir / "mixed.txt"
        mixed_file.write_bytes(b'Text content\x00\x01\x02More text')
        
        txt_reader = reader_factory.get_reader(str(mixed_file))
        try:
            text = txt_reader.read(mixed_file)
            # Should either handle gracefully or raise clear error
            assert isinstance(text, str)
        except (UnicodeDecodeError, ValueError) as e:
            # Expected for binary content
            assert "decode" in str(e).lower() or "binary" in str(e).lower()
    
    def test_archive_edge_cases(self, reader_factory, temp_dir):
        """Test archive readers with edge cases."""
        # Empty ZIP file
        empty_zip = temp_dir / "empty.zip"
        with zipfile.ZipFile(empty_zip, 'w'):
            pass  # Create empty zip
        
        zip_reader = reader_factory.get_reader(str(empty_zip))
        text = zip_reader.read(empty_zip)
        metadata = zip_reader.extract_metadata(empty_zip)
        
        assert isinstance(text, str)
        assert metadata["file_count"] == 0
        
        # ZIP with nested directories
        nested_zip = temp_dir / "nested.zip"
        with zipfile.ZipFile(nested_zip, 'w') as zf:
            zf.writestr("dir1/file1.txt", "Content 1")
            zf.writestr("dir1/dir2/file2.txt", "Content 2")
            zf.writestr("dir1/dir2/dir3/file3.txt", "Content 3")
        
        text = zip_reader.read(nested_zip)
        assert "dir1/dir2/dir3/file3.txt" in text
        assert "Content 3" in text
        
        # TAR with special files
        special_tar = temp_dir / "special.tar"
        with tarfile.open(special_tar, 'w') as tf:
            # Add a text file
            info = tarfile.TarInfo(name="special/file.txt")
            info.size = len(b"Special content")
            tf.addfile(info, fileobj=tempfile.SpooledTemporaryFile())
            tf.getmember("special/file.txt").size = len(b"Special content")
        
        tar_reader = reader_factory.get_reader(str(special_tar))
        try:
            text = tar_reader.read(special_tar)
            assert isinstance(text, str)
        except Exception:
            # Some special tar features might not be fully supported
            pass
    
    def test_config_file_variations(self, reader_factory, temp_dir):
        """Test config file readers with various formats."""
        # INI with comments and special sections
        ini_file = temp_dir / "complex.ini"
        ini_file.write_text("""
; Comment line
[DEFAULT]
default_key = default_value

[Section One]
# Another comment
key1 = value1
key2 = value with spaces

[Section.With.Dots]
dotted.key = dotted.value
""")
        
        ini_reader = reader_factory.get_reader(str(ini_file))
        text = ini_reader.read(ini_file)
        assert "[DEFAULT]" in text
        assert "value with spaces" in text
        assert "[Section.With.Dots]" in text
        
        # YAML with anchors and aliases
        yaml_file = temp_dir / "anchors.yaml"
        yaml_file.write_text("""
defaults: &defaults
  setting1: value1
  setting2: value2

production:
  <<: *defaults
  setting2: override

development:
  <<: *defaults
  debug: true
""")
        
        yaml_reader = reader_factory.get_reader(str(yaml_file))
        text = yaml_reader.read(yaml_file)
        assert "defaults:" in text
        assert "production:" in text
        assert "override" in text
        
        # XML with namespaces
        xml_file = temp_dir / "namespaced.xml"
        xml_file.write_text("""
<root xmlns:custom="http://example.com/ns">
    <custom:element attr="value">
        Content with namespace
    </custom:element>
</root>
""")
        
        xml_reader = reader_factory.get_reader(str(xml_file))
        text = xml_reader.read(xml_file)
        assert "Content with namespace" in text
        assert "attr=" in text
    
    def test_log_file_patterns(self, reader_factory, temp_dir):
        """Test log reader with various log formats."""
        # Standard log format
        log_file = temp_dir / "app.log"
        log_file.write_text("""
2024-01-01 10:00:00 INFO Starting application
2024-01-01 10:00:01 DEBUG Loading configuration
2024-01-01 10:00:02 WARNING Config item missing
2024-01-01 10:00:03 ERROR Failed to connect to database
2024-01-01 10:00:04 CRITICAL System shutting down
[2024-01-01] Custom format log entry
Jan 01 10:00:05 syslog: System message
""")
        
        log_reader = reader_factory.get_reader(str(log_file))
        text = log_reader.read(log_file)
        metadata = log_reader.extract_metadata(log_file)
        
        assert "ERROR Failed to connect" in text
        assert "level_stats" in metadata
        assert metadata["level_stats"]["ERROR"] == 1
        assert metadata["level_stats"]["INFO"] == 1
        assert metadata["level_stats"]["CRITICAL"] == 1
        
        # Test with stack traces
        error_log = temp_dir / "error.log"
        error_log.write_text("""
2024-01-01 10:00:00 ERROR Exception occurred:
Traceback (most recent call last):
  File "app.py", line 123, in process
    result = divide(10, 0)
  File "app.py", line 45, in divide
    return a / b
ZeroDivisionError: division by zero
2024-01-01 10:00:01 INFO Recovery attempted
""")
        
        text = log_reader.read(error_log)
        assert "Traceback" in text
        assert "ZeroDivisionError" in text
        metadata = log_reader.extract_metadata(error_log)
        assert metadata["level_stats"]["ERROR"] == 1
    
    def test_data_format_edge_cases(self, reader_factory, temp_dir):
        """Test data format readers with edge cases."""
        # GeoJSON with complex geometries
        geojson_file = temp_dir / "complex.geojson"
        geojson_file.write_text(json.dumps({
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                    },
                    "properties": {"name": "Square", "area": 1}
                },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "MultiPoint",
                        "coordinates": [[0, 0], [1, 1], [2, 2]]
                    },
                    "properties": {"name": "Points", "count": 3}
                }
            ]
        }))
        
        geojson_reader = reader_factory.get_reader(str(geojson_file))
        text = geojson_reader.read(geojson_file)
        assert "FeatureCollection" in text
        assert "Square" in text
        assert "MultiPoint" in text
        
        # JSON Lines with various content types
        jsonl_file = temp_dir / "mixed.jsonl"
        jsonl_file.write_text('\n'.join([
            '{"type": "string", "value": "text"}',
            '{"type": "number", "value": 123}',
            '{"type": "boolean", "value": true}',
            '{"type": "null", "value": null}',
            '{"type": "array", "value": [1, 2, 3]}',
            '{"type": "object", "value": {"nested": "data"}}',
        ]))
        
        jsonl_reader = reader_factory.get_reader(str(jsonl_file))
        text = jsonl_reader.read(jsonl_file)
        assert "string" in text
        assert "123" in text
        assert "true" in text
        assert "nested" in text


class TestReaderPerformance:
    """Test reader performance characteristics."""
    
    @pytest.fixture
    def reader_factory(self):
        """Get reader factory instance."""
        return ReaderFactory()
    
    def test_streaming_large_csv(self, reader_factory, temp_dir):
        """Test CSV reader can stream large files."""
        import time
        
        # Create a moderately large CSV
        large_csv = temp_dir / "large.csv"
        with large_csv.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "value", "timestamp"])
            for i in range(10000):
                writer.writerow([i, f"name_{i}", i * 1.5, datetime.now().isoformat()])
        
        csv_reader = reader_factory.get_reader(str(large_csv))
        
        start_time = time.time()
        text = csv_reader.read(large_csv)
        read_time = time.time() - start_time
        
        # Should complete reasonably quickly
        assert read_time < 2.0  # Less than 2 seconds for 10k rows
        assert "name_9999" in text  # Last row present
        
        # Check memory efficiency (text should be reasonable size)
        text_size_mb = len(text) / (1024 * 1024)
        assert text_size_mb < 10  # Should be compressed/summarized if too large
    
    def test_concurrent_reader_access(self, reader_factory, temp_dir):
        """Test readers can be used concurrently."""
        import concurrent.futures
        
        # Create test files
        files = []
        for i in range(10):
            file_path = temp_dir / f"test_{i}.json"
            file_path.write_text(json.dumps({"id": i, "data": "x" * 100}))
            files.append(file_path)
        
        def read_file(file_path):
            reader = reader_factory.get_reader(str(file_path))
            return reader.read(file_path)
        
        # Read files concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(read_file, f) for f in files]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All files should be read successfully
        assert len(results) == 10
        for result in results:
            assert len(result) > 0
            assert "data" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])