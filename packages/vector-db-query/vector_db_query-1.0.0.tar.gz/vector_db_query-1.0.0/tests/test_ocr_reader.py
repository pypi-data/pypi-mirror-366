"""Tests for OCR reader functionality."""

import pytest
from pathlib import Path
import tempfile
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from vector_db_query.document_processor.image_ocr_reader import (
    ImageOCRReader, check_ocr_available, get_available_languages
)
from vector_db_query.document_processor.exceptions import DocumentProcessingError


# Skip all tests if OCR is not available
pytestmark = pytest.mark.skipif(
    not check_ocr_available(),
    reason="OCR dependencies not installed (Tesseract/pytesseract)"
)


class TestImageOCRReader:
    """Test OCR reading functionality."""
    
    @pytest.fixture
    def reader(self):
        """Create ImageOCRReader instance."""
        return ImageOCRReader()
    
    @pytest.fixture
    def simple_text_image(self):
        """Create a simple text image for testing."""
        # Create image with text
        width, height = 800, 200
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to use a basic font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        except:
            font = ImageFont.load_default()
        
        # Draw text
        text = "Hello World from OCR"
        draw.text((50, 50), text, fill='black', font=font)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            image.save(tmp.name)
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def multi_line_image(self):
        """Create a multi-line text image."""
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            font = ImageFont.load_default()
        
        # Draw multiple lines
        lines = [
            "Line 1: This is the first line",
            "Line 2: This is the second line",
            "Line 3: This is the third line",
            "",
            "Paragraph 2 starts here.",
            "It has multiple sentences."
        ]
        
        y_offset = 50
        for line in lines:
            draw.text((50, y_offset), line, fill='black', font=font)
            y_offset += 60
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            image.save(tmp.name)
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def low_quality_image(self):
        """Create a low quality image for preprocessing test."""
        # Create small, low contrast image
        width, height = 200, 100
        image = Image.new('RGB', (width, height), color='lightgray')
        draw = ImageDraw.Draw(image)
        
        # Draw text with low contrast
        text = "Low Quality Text"
        draw.text((10, 30), text, fill='gray')
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            image.save(tmp.name, quality=20)  # Low quality JPEG
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def multi_page_tiff(self):
        """Create a multi-page TIFF for testing."""
        images = []
        
        for i in range(3):
            image = Image.new('RGB', (600, 200), color='white')
            draw = ImageDraw.Draw(image)
            
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            except:
                font = ImageFont.load_default()
            
            text = f"Page {i + 1} of TIFF document"
            draw.text((50, 50), text, fill='black', font=font)
            images.append(image)
        
        with tempfile.NamedTemporaryFile(suffix='.tiff', delete=False) as tmp:
            # Save as multi-page TIFF
            images[0].save(
                tmp.name,
                save_all=True,
                append_images=images[1:],
                compression='tiff_lzw'
            )
            yield tmp.name
        
        Path(tmp.name).unlink(missing_ok=True)
    
    def test_read_simple_text(self, reader, simple_text_image):
        """Test reading simple text from image."""
        result = reader.read(simple_text_image)
        
        # OCR might not be perfect, so check for key words
        assert 'Hello' in result or 'hello' in result.lower()
        assert 'World' in result or 'world' in result.lower()
        
        # Check metadata
        metadata = reader._metadata
        assert metadata['format'] == 'PNG'
        assert metadata['width'] == 800
        assert metadata['height'] == 200
        assert 'ocr_confidence' in metadata
        assert metadata['word_count'] >= 3  # At least 3 words
    
    def test_read_multi_line(self, reader, multi_line_image):
        """Test reading multi-line text."""
        result = reader.read(multi_line_image)
        
        # Check that multiple lines are detected
        lines = result.strip().split('\n')
        assert len(lines) >= 4  # At least 4 non-empty lines
        
        # Check for content
        assert 'Line 1' in result or 'first line' in result
        assert 'Paragraph 2' in result or 'starts here' in result
    
    def test_preprocessing(self, reader, low_quality_image):
        """Test image preprocessing."""
        reader.preprocessing = True
        result = reader.read(low_quality_image)
        
        # With preprocessing, should still extract some text
        # (might not be perfect due to low quality)
        assert len(result.strip()) > 0
        
        # Check that preprocessing was triggered
        metadata = reader._metadata
        quality = metadata.get('quality', {})
        assert quality.get('needs_preprocessing', False)
    
    def test_multi_page_tiff(self, reader, multi_page_tiff):
        """Test reading multi-page TIFF."""
        result = reader.read(multi_page_tiff)
        
        # Check for page markers
        assert '--- Page 1 ---' in result
        assert '--- Page 2 ---' in result
        assert '--- Page 3 ---' in result
        
        # Check metadata
        metadata = reader._metadata
        assert metadata.get('page_count') == 3
        
        # Check content from each page
        assert 'Page 1' in result or 'TIFF' in result
    
    def test_confidence_threshold(self, reader, simple_text_image):
        """Test confidence threshold filtering."""
        # Set high confidence threshold
        reader.confidence_threshold = 90.0
        result_high = reader.read(simple_text_image)
        
        # Set low confidence threshold
        reader.confidence_threshold = 30.0
        result_low = reader.read(simple_text_image)
        
        # Low threshold might include more text (or noise)
        # This test might need adjustment based on OCR quality
        assert len(result_low) >= len(result_high)
    
    def test_language_support(self, reader):
        """Test language configuration."""
        # Check available languages
        languages = get_available_languages()
        assert 'eng' in languages
        
        # Test setting different language
        reader.language = 'eng+fra'  # English and French
        assert reader.language == 'eng+fra'
    
    def test_supported_formats(self, reader):
        """Test supported image formats."""
        assert reader.supports_extension('.png')
        assert reader.supports_extension('.jpg')
        assert reader.supports_extension('.jpeg')
        assert reader.supports_extension('.gif')
        assert reader.supports_extension('.bmp')
        assert reader.supports_extension('.tiff')
        assert reader.supports_extension('.tif')
        assert reader.supports_extension('.webp')
        assert not reader.supports_extension('.txt')
        assert not reader.supports_extension('.pdf')
    
    def test_metadata_extraction(self, reader, simple_text_image):
        """Test metadata extraction."""
        reader.read(simple_text_image)
        metadata = reader._metadata
        
        assert 'file_name' in metadata
        assert 'file_size' in metadata
        assert 'format' in metadata
        assert 'mode' in metadata
        assert 'width' in metadata
        assert 'height' in metadata
        assert 'language' in metadata
        assert metadata['language'] == 'eng'
    
    def test_quality_assessment(self, reader, simple_text_image):
        """Test image quality assessment."""
        reader.read(simple_text_image)
        metadata = reader._metadata
        
        quality = metadata.get('quality', {})
        assert 'suitable_for_ocr' in quality
        assert 'warnings' in quality
        assert isinstance(quality['warnings'], list)
    
    def test_error_handling(self, reader):
        """Test error handling for invalid files."""
        # Test with non-existent file
        with pytest.raises(DocumentProcessingError):
            reader.read("non_existent_image.png")
        
        # Test with non-image file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b"This is not an image")
            tmp.flush()
            
            try:
                with pytest.raises(DocumentProcessingError):
                    reader.read(tmp.name)
            finally:
                Path(tmp.name).unlink(missing_ok=True)
    
    def test_timeout_handling(self, reader, simple_text_image):
        """Test OCR timeout handling."""
        # Set very short timeout
        reader.timeout = 0.001
        
        # This might timeout on complex images
        # For simple images it might still succeed
        try:
            result = reader.read(simple_text_image)
            # If it succeeds, that's fine
            assert isinstance(result, str)
        except DocumentProcessingError as e:
            # If it fails due to timeout, that's expected
            assert 'timeout' in str(e).lower() or 'OCR failed' in str(e)
    
    def test_cleanup(self, reader, simple_text_image):
        """Test temporary file cleanup."""
        # Read image (which might create temp files)
        reader.read(simple_text_image)
        
        # Cleanup should remove temp directory
        reader.cleanup()
        assert reader._temp_dir is None