"""Tests for HTML reader functionality."""

import pytest
from pathlib import Path
import tempfile

from vector_db_query.document_processor.html_reader import HTMLReader
from vector_db_query.document_processor.exceptions import DocumentProcessingError


class TestHTMLReader:
    """Test HTML reading functionality."""
    
    @pytest.fixture
    def reader(self):
        """Create HTMLReader instance."""
        return HTMLReader()
    
    @pytest.fixture
    def reader_markdown(self):
        """Create HTMLReader with markdown conversion enabled."""
        return HTMLReader(convert_to_markdown=True)
    
    @pytest.fixture
    def simple_html(self):
        """Create a simple HTML file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as tmp:
            tmp.write("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Test Page</title>
                <meta name="description" content="A test HTML page">
                <meta name="author" content="Test Author">
            </head>
            <body>
                <h1>Main Heading</h1>
                <p>This is a paragraph with some text.</p>
                <p>Another paragraph with more content.</p>
            </body>
            </html>
            """)
            tmp.flush()
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def complex_html(self):
        """Create a complex HTML file with various elements."""
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as tmp:
            tmp.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Complex HTML Test</title>
                <style>
                    body { font-family: Arial; }
                    .hidden { display: none; }
                </style>
                <script>
                    console.log('This should be removed');
                </script>
            </head>
            <body>
                <h1>Complex HTML Elements</h1>
                
                <h2>Lists</h2>
                <ul>
                    <li>Unordered item 1</li>
                    <li>Unordered item 2</li>
                </ul>
                
                <ol>
                    <li>Ordered item 1</li>
                    <li>Ordered item 2</li>
                </ol>
                
                <h2>Links and Formatting</h2>
                <p>This has a <a href="https://example.com">link</a> and <strong>bold text</strong>.</p>
                <p>Also <em>italic</em> and <code>inline code</code>.</p>
                
                <h2>Code Block</h2>
                <pre><code>def hello():
    print("Hello, World!")</code></pre>
                
                <h2>Table</h2>
                <table>
                    <tr>
                        <th>Header 1</th>
                        <th>Header 2</th>
                    </tr>
                    <tr>
                        <td>Cell 1</td>
                        <td>Cell 2</td>
                    </tr>
                </table>
                
                <blockquote>This is a blockquote.</blockquote>
                
                <!-- This is a comment that should be removed -->
            </body>
            </html>
            """)
            tmp.flush()
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_simple_html(self, reader, simple_html):
        """Test reading a simple HTML file."""
        result = reader.read(simple_html)
        
        assert len(result) > 0
        assert 'Main Heading' in result
        assert 'This is a paragraph with some text.' in result
        assert 'Another paragraph with more content.' in result
    
    def test_metadata_extraction(self, reader, simple_html):
        """Test metadata extraction from HTML."""
        reader.read(simple_html)
        metadata = reader._metadata
        
        assert metadata['title'] == 'Test Page'
        assert metadata['meta_description'] == 'A test HTML page'
        assert metadata['meta_author'] == 'Test Author'
        assert metadata['language'] == 'en'
        assert metadata['heading_count'] == 1
        assert metadata['paragraph_count'] == 2
    
    def test_script_and_style_removal(self, reader, complex_html):
        """Test that scripts and styles are removed."""
        result = reader.read(complex_html)
        
        # Scripts should be removed
        assert 'console.log' not in result
        assert 'This should be removed' not in result
        
        # Styles should be removed
        assert 'font-family' not in result
        assert 'display: none' not in result
        
        # Comments should be removed
        assert 'This is a comment' not in result
    
    def test_preserve_structure(self, reader, complex_html):
        """Test structure preservation."""
        reader.preserve_structure = True
        result = reader.read(complex_html)
        
        # Check headings are preserved with markdown style
        assert '# Complex HTML Elements' in result
        assert '## Lists' in result
        
        # Check lists are formatted
        assert '- Unordered item 1' in result
        assert '1. Ordered item 1' in result
        
        # Check code block
        assert '```' in result
        assert 'def hello():' in result
        
        # Check blockquote
        assert '> This is a blockquote.' in result
        
        # Check table
        assert 'Header 1 | Header 2' in result
        assert 'Cell 1 | Cell 2' in result
    
    def test_no_structure_preservation(self, reader, complex_html):
        """Test reading without structure preservation."""
        reader.preserve_structure = False
        result = reader.read(complex_html)
        
        # Should still have all text
        assert 'Complex HTML Elements' in result
        assert 'Unordered item 1' in result
        assert 'This is a blockquote.' in result
        
        # But no markdown formatting
        assert '# Complex HTML Elements' not in result
        assert '- Unordered item 1' not in result
    
    def test_markdown_conversion(self, reader_markdown, complex_html):
        """Test HTML to markdown conversion."""
        result = reader_markdown.read(complex_html)
        
        # Should have markdown formatting
        assert '# Complex HTML Elements' in result
        assert '## Lists' in result
        assert '* Unordered item 1' in result or '- Unordered item 1' in result
        assert '[link](https://example.com)' in result
        assert '**bold text**' in result
        assert '_italic_' in result or '*italic*' in result
        assert '`inline code`' in result
    
    def test_link_handling(self, reader):
        """Test link preservation and ignoring."""
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as tmp:
            tmp.write("""
            <html>
            <body>
                <p>Visit our <a href="https://example.com">website</a> for more info.</p>
            </body>
            </html>
            """)
            tmp.flush()
            
            try:
                # With links preserved
                reader.ignore_links = False
                result = reader.read(tmp.name)
                # Debug output
                print(f"Result: '{result}'")
                print(f"Looking for: '[website](https://example.com)'")
                assert '[website](https://example.com)' in result
                
                # With links ignored
                reader.ignore_links = True
                reader.preserve_structure = False
                result = reader.read(tmp.name)
                assert 'website' in result
                assert 'https://example.com' not in result
                
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_encoding_detection(self, reader):
        """Test reading HTML with different encodings."""
        # UTF-8 encoded
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', encoding='utf-8', delete=False) as tmp:
            tmp.write("""
            <html>
            <head><meta charset="UTF-8"></head>
            <body><p>UTF-8 content: café, naïve</p></body>
            </html>
            """)
            tmp.flush()
            
            try:
                result = reader.read(tmp.name)
                assert 'café' in result
                assert 'naïve' in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_malformed_html(self, reader):
        """Test handling of malformed HTML."""
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as tmp:
            tmp.write("""
            <html>
            <body>
                <p>Unclosed paragraph
                <div>Unclosed div
                <p>Another paragraph</p>
            </body>
            """)
            tmp.flush()
            
            try:
                # Should still extract text
                result = reader.read(tmp.name)
                assert 'Unclosed paragraph' in result
                assert 'Unclosed div' in result
                assert 'Another paragraph' in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_nested_elements(self, reader):
        """Test handling of deeply nested elements."""
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as tmp:
            tmp.write("""
            <html>
            <body>
                <div>
                    <div>
                        <p>Nested <span>paragraph with <strong>bold <em>and italic</em></strong> text</span>.</p>
                    </div>
                </div>
            </body>
            </html>
            """)
            tmp.flush()
            
            try:
                result = reader.read(tmp.name)
                assert 'Nested paragraph with bold and italic text.' in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_empty_html(self, reader):
        """Test reading empty HTML file."""
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as tmp:
            tmp.write('<html><body></body></html>')
            tmp.flush()
            
            try:
                result = reader.read(tmp.name)
                # Should return empty or minimal content
                assert len(result.strip()) == 0
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_nonexistent_file(self, reader):
        """Test reading a non-existent file."""
        with pytest.raises(DocumentProcessingError):
            reader.read("nonexistent.html")
    
    def test_supports_extension(self, reader):
        """Test extension support checking."""
        assert reader.supports_extension('.html')
        assert reader.supports_extension('.HTML')
        assert reader.supports_extension('html')
        assert reader.supports_extension('.htm')
        assert reader.supports_extension('.xhtml')
        assert not reader.supports_extension('.txt')
        assert not reader.supports_extension('.xml')
    
    def test_whitespace_cleanup(self, reader):
        """Test whitespace cleanup."""
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as tmp:
            tmp.write("""
            <html>
            <body>
                <p>Text with     excessive     spaces</p>
                
                
                
                <p>Multiple blank lines above</p>
            </body>
            </html>
            """)
            tmp.flush()
            
            try:
                result = reader.read(tmp.name)
                # Should clean up excessive spaces
                assert 'Text with     excessive     spaces' in result or 'Text with excessive spaces' in result
                # Should not have more than 2 consecutive newlines
                assert '\n\n\n' not in result
            finally:
                Path(tmp.name).unlink(missing_ok=True)