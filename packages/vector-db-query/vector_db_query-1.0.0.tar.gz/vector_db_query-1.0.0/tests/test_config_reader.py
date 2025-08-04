"""Tests for configuration file readers."""

import pytest
import json
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile
import configparser

from vector_db_query.document_processor.config_reader import (
    JSONReader, XMLReader, YAMLReader, INIReader, LogReader
)
from vector_db_query.document_processor.exceptions import DocumentProcessingError


class TestJSONReader:
    """Test JSON reading functionality."""
    
    @pytest.fixture
    def reader(self):
        """Create JSONReader instance."""
        return JSONReader()
    
    @pytest.fixture
    def simple_json(self):
        """Create a simple JSON file for testing."""
        data = {
            "name": "Test Document",
            "version": "1.0",
            "features": ["feature1", "feature2", "feature3"],
            "metadata": {
                "author": "Test Author",
                "date": "2025-01-30"
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as tmp:
            json.dump(data, tmp, indent=2)
            tmp.flush()
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def json_array(self):
        """Create a JSON array file."""
        data = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as tmp:
            json.dump(data, tmp)
            tmp.flush()
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_simple_json(self, reader, simple_json):
        """Test reading a simple JSON file."""
        result = reader.read(simple_json)
        
        assert '"name": "Test Document"' in result
        assert '"version": "1.0"' in result
        assert '"features"' in result
        assert '"metadata"' in result
        
        # Check metadata
        metadata = reader._metadata
        assert metadata['type'] == 'json'
        assert metadata['key_count'] == 6  # Total keys including nested
    
    def test_read_json_array(self, reader, json_array):
        """Test reading a JSON array."""
        result = reader.read(json_array)
        
        assert '"id": 1' in result
        assert '"name": "Item 1"' in result
        
        # Check metadata
        metadata = reader._metadata
        assert metadata['array_length'] == 3
    
    def test_pretty_print(self, reader, simple_json):
        """Test pretty printing."""
        reader.pretty_print = True
        result = reader.read(simple_json)
        # Should have indentation
        assert '\n  "' in result
        
        reader.pretty_print = False
        result = reader.read(simple_json)
        # Should be compact
        assert '\n  "' not in result
    
    def test_invalid_json(self, reader):
        """Test handling of invalid JSON."""
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as tmp:
            tmp.write('{"invalid": json""}')
            tmp.flush()
            
            try:
                with pytest.raises(DocumentProcessingError):
                    reader.read(tmp.name)
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_supports_extension(self, reader):
        """Test extension support checking."""
        assert reader.supports_extension('.json')
        assert reader.supports_extension('.jsonl')
        assert reader.supports_extension('.geojson')
        assert not reader.supports_extension('.txt')


class TestXMLReader:
    """Test XML reading functionality."""
    
    @pytest.fixture
    def reader(self):
        """Create XMLReader instance."""
        return XMLReader()
    
    @pytest.fixture
    def simple_xml(self):
        """Create a simple XML file for testing."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<document>
    <title>Test Document</title>
    <author>Test Author</author>
    <sections>
        <section id="1">
            <heading>Introduction</heading>
            <content>This is the introduction.</content>
        </section>
        <section id="2">
            <heading>Main Content</heading>
            <content>This is the main content.</content>
        </section>
    </sections>
</document>"""
        
        with tempfile.NamedTemporaryFile(suffix='.xml', mode='w', delete=False) as tmp:
            tmp.write(xml_content)
            tmp.flush()
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_simple_xml(self, reader, simple_xml):
        """Test reading a simple XML file."""
        result = reader.read(simple_xml)
        
        assert 'document:' in result
        assert 'title: Test Document' in result
        assert 'author: Test Author' in result
        assert 'sections:' in result
        
        # Check metadata
        metadata = reader._metadata
        assert metadata['type'] == 'xml'
        assert metadata['root_tag'] == 'document'
        assert metadata['element_count'] > 0
    
    def test_xml_attributes(self, reader):
        """Test handling of XML attributes."""
        xml_content = """<?xml version="1.0"?>
<root>
    <element id="123" type="test">Content</element>
</root>"""
        
        with tempfile.NamedTemporaryFile(suffix='.xml', mode='w', delete=False) as tmp:
            tmp.write(xml_content)
            tmp.flush()
            
            try:
                result = reader.read(tmp.name)
                assert '@id: 123' in result
                assert '@type: test' in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_preserve_structure(self, reader, simple_xml):
        """Test structure preservation."""
        reader.preserve_structure = True
        result = reader.read(simple_xml)
        # Should have indentation
        assert '  section:' in result
        
        reader.preserve_structure = False
        result = reader.read(simple_xml)
        # Should just extract text
        assert 'Test Document' in result
        assert 'This is the introduction.' in result
    
    def test_invalid_xml(self, reader):
        """Test handling of invalid XML."""
        with tempfile.NamedTemporaryFile(suffix='.xml', mode='w', delete=False) as tmp:
            tmp.write('<root><unclosed>')
            tmp.flush()
            
            try:
                with pytest.raises(DocumentProcessingError):
                    reader.read(tmp.name)
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_supports_extension(self, reader):
        """Test extension support checking."""
        assert reader.supports_extension('.xml')
        assert reader.supports_extension('.xsd')
        assert reader.supports_extension('.xsl')
        assert reader.supports_extension('.svg')
        assert not reader.supports_extension('.html')


class TestYAMLReader:
    """Test YAML reading functionality."""
    
    @pytest.fixture
    def reader(self):
        """Create YAMLReader instance."""
        return YAMLReader()
    
    @pytest.fixture
    def simple_yaml(self):
        """Create a simple YAML file for testing."""
        yaml_content = """
name: Test Document
version: 1.0
features:
  - feature1
  - feature2
  - feature3
metadata:
  author: Test Author
  date: 2025-01-30
  tags:
    - test
    - sample
"""
        
        with tempfile.NamedTemporaryFile(suffix='.yaml', mode='w', delete=False) as tmp:
            tmp.write(yaml_content)
            tmp.flush()
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def multi_doc_yaml(self):
        """Create a multi-document YAML file."""
        yaml_content = """---
document: 1
type: test
---
document: 2
type: sample
"""
        
        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            tmp.write(yaml_content)
            tmp.flush()
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_simple_yaml(self, reader, simple_yaml):
        """Test reading a simple YAML file."""
        result = reader.read(simple_yaml)
        
        assert 'name: Test Document' in result
        assert 'version: 1.0' in result
        assert 'features:' in result
        assert '- feature1' in result
        
        # Check metadata
        metadata = reader._metadata
        assert metadata['type'] == 'yaml'
        assert metadata['document_count'] == 1
        assert metadata['key_count'] > 0
    
    def test_read_multi_doc_yaml(self, reader, multi_doc_yaml):
        """Test reading multi-document YAML."""
        result = reader.read(multi_doc_yaml)
        
        assert 'document: 1' in result
        assert 'document: 2' in result
        assert '---' in result  # Document separator
        
        # Check metadata
        metadata = reader._metadata
        assert metadata['document_count'] == 2
    
    def test_pretty_print(self, reader, simple_yaml):
        """Test pretty printing."""
        reader.pretty_print = True
        result = reader.read(simple_yaml)
        # Should have proper YAML formatting
        assert 'features:\n' in result
        
    def test_invalid_yaml(self, reader):
        """Test handling of invalid YAML."""
        with tempfile.NamedTemporaryFile(suffix='.yaml', mode='w', delete=False) as tmp:
            tmp.write('invalid:\n  - item\n bad indentation')
            tmp.flush()
            
            try:
                with pytest.raises(DocumentProcessingError):
                    reader.read(tmp.name)
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_supports_extension(self, reader):
        """Test extension support checking."""
        assert reader.supports_extension('.yaml')
        assert reader.supports_extension('.yml')
        assert not reader.supports_extension('.xml')


class TestINIReader:
    """Test INI/CFG reading functionality."""
    
    @pytest.fixture
    def reader(self):
        """Create INIReader instance."""
        return INIReader()
    
    @pytest.fixture
    def simple_ini(self):
        """Create a simple INI file for testing."""
        ini_content = """[DEFAULT]
app_name = TestApp
version = 1.0

[database]
host = localhost
port = 5432
name = testdb
user = testuser

[logging]
level = INFO
file = app.log
format = %(asctime)s - %(levelname)s - %(message)s
"""
        
        with tempfile.NamedTemporaryFile(suffix='.ini', mode='w', delete=False) as tmp:
            tmp.write(ini_content)
            tmp.flush()
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_simple_ini(self, reader, simple_ini):
        """Test reading a simple INI file."""
        result = reader.read(simple_ini)
        
        assert '[DEFAULT]' in result
        assert 'app_name = TestApp' in result
        assert '[database]' in result
        assert 'host = localhost' in result
        assert '[logging]' in result
        
        # Check metadata
        metadata = reader._metadata
        assert metadata['type'] == 'ini'
        assert metadata['section_count'] == 2  # DEFAULT not counted as section
        assert metadata['total_keys'] > 0
    
    def test_cfg_extension(self, reader):
        """Test reading .cfg files."""
        with tempfile.NamedTemporaryFile(suffix='.cfg', mode='w', delete=False) as tmp:
            tmp.write('[section]\nkey = value')
            tmp.flush()
            
            try:
                result = reader.read(tmp.name)
                assert '[section]' in result
                assert 'key = value' in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_invalid_ini(self, reader):
        """Test handling of invalid INI."""
        with tempfile.NamedTemporaryFile(suffix='.ini', mode='w', delete=False) as tmp:
            tmp.write('[section\nno closing bracket')
            tmp.flush()
            
            try:
                with pytest.raises(DocumentProcessingError):
                    reader.read(tmp.name)
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_supports_extension(self, reader):
        """Test extension support checking."""
        assert reader.supports_extension('.ini')
        assert reader.supports_extension('.cfg')
        assert reader.supports_extension('.conf')
        assert reader.supports_extension('.config')
        assert not reader.supports_extension('.txt')


class TestLogReader:
    """Test log file reading functionality."""
    
    @pytest.fixture
    def reader(self):
        """Create LogReader instance."""
        return LogReader()
    
    @pytest.fixture
    def simple_log(self):
        """Create a simple log file for testing."""
        log_content = """[2025-01-30 10:00:00] INFO Starting application
[2025-01-30 10:00:01] DEBUG Loading configuration
[2025-01-30 10:00:02] INFO Connected to database
[2025-01-30 10:00:03] WARNING Connection timeout, retrying
[2025-01-30 10:00:04] INFO Retry successful
[2025-01-30 10:00:05] ERROR Failed to load user data
[2025-01-30 10:00:06] CRITICAL System shutdown required
[2025-01-30 10:00:07] INFO Shutting down gracefully
"""
        
        with tempfile.NamedTemporaryFile(suffix='.log', mode='w', delete=False) as tmp:
            tmp.write(log_content)
            tmp.flush()
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_simple_log(self, reader, simple_log):
        """Test reading a simple log file."""
        result = reader.read(simple_log)
        
        assert 'Starting application' in result
        assert 'Failed to load user data' in result
        
        # Check metadata
        metadata = reader._metadata
        assert metadata['type'] == 'log'
        assert metadata['line_count'] == 8
        assert metadata['error_count'] == 1
        assert metadata['warning_count'] == 1
        assert metadata['info_count'] == 4  # INFO appears 4 times in the log
        assert metadata['debug_count'] == 1
    
    def test_summarize_mode(self, reader, simple_log):
        """Test log summarization."""
        reader.summarize = True
        result = reader.read(simple_log)
        
        assert 'Log File Summary' in result
        assert 'Total Lines: 8' in result
        assert 'ERROR: 1' in result
        assert 'Recent Errors' in result
    
    def test_structure_markers(self, reader, simple_log):
        """Test adding structure markers."""
        reader.preserve_structure = True
        reader.summarize = False
        result = reader.read(simple_log)
        
        assert '[ERROR]' in result
        assert '[WARN]' in result
    
    def test_timestamp_extraction(self, reader, simple_log):
        """Test timestamp extraction."""
        reader.read(simple_log)
        metadata = reader._metadata
        
        assert 'timestamp_range' in metadata
        assert '2025-01-30 10:00:00' in metadata['timestamp_range']
        assert '2025-01-30 10:00:07' in metadata['timestamp_range']
    
    def test_different_log_formats(self, reader):
        """Test different log formats."""
        # Syslog format
        log_content = """Jan 30 10:00:00 server kernel: Boot complete
Jan 30 10:00:01 server systemd: Started service"""
        
        with tempfile.NamedTemporaryFile(suffix='.log', mode='w', delete=False) as tmp:
            tmp.write(log_content)
            tmp.flush()
            
            try:
                result = reader.read(tmp.name)
                assert 'Boot complete' in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_supports_extension(self, reader):
        """Test extension support checking."""
        assert reader.supports_extension('.log')
        assert reader.supports_extension('.txt')
        assert not reader.supports_extension('.json')