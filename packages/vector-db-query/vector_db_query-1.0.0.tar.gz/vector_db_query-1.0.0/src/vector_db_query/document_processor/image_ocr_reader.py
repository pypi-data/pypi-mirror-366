"""Image OCR reader implementation using Tesseract."""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import warnings

# Suppress PIL warnings
warnings.filterwarnings("ignore", category=UserWarning, module='PIL')

try:
    from PIL import Image, ImageEnhance, ImageFilter
    import pytesseract
    import numpy as np
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

from vector_db_query.document_processor.image_readers import ImageDocumentReader
from vector_db_query.document_processor.exceptions import (
    DocumentReadError,
    DocumentProcessingError
)
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class ImageOCRReader(ImageDocumentReader):
    """Reader for image files with OCR text extraction."""
    
    def __init__(self,
                 language: str = 'eng',
                 dpi: int = 300,
                 preprocessing: bool = True,
                 timeout: int = 30,
                 confidence_threshold: float = 60.0):
        """Initialize Image OCR reader.
        
        Args:
            language: OCR language(s) to use (e.g., 'eng', 'fra', 'eng+fra')
            dpi: DPI for image processing
            preprocessing: Whether to preprocess images for better OCR
            timeout: OCR timeout in seconds
            confidence_threshold: Minimum confidence for text extraction
        """
        if not HAS_OCR:
            raise ImportError(
                "OCR dependencies not installed. Install with: "
                "pip install pillow pytesseract numpy"
            )
            
        super().__init__(language, dpi, preprocessing, timeout)
        self.confidence_threshold = confidence_threshold
        self._metadata = {}
        
        # Check if Tesseract is installed
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            raise ImportError(
                "Tesseract OCR not found. Please install Tesseract: "
                "https://github.com/tesseract-ocr/tesseract"
            )
    
    def can_read(self, file_path: Path) -> bool:
        """Check if this reader can handle the file type."""
        return file_path.suffix.lower() in self.supported_extensions
        
    def read(self, file_path: Path) -> str:
        """Read image file and extract text using OCR."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        logger.info(f"Reading image file with OCR: {file_path.name}")
        
        try:
            # Open and validate image
            image = Image.open(file_path)
            
            # Extract metadata
            self._metadata = self._extract_metadata(image, file_path)
            
            # Handle multi-page TIFF
            if file_path.suffix.lower() in ['.tif', '.tiff']:
                return self._process_multipage_tiff(image, file_path)
            else:
                return self._process_single_image(image, file_path)
                
        except Exception as e:
            raise DocumentReadError(
                f"Failed to read image file: {e}",
                file_path=str(file_path)
            )
        finally:
            self.cleanup()
            
    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp']
        
    def supports_extension(self, extension: str) -> bool:
        """Check if a file extension is supported.
        
        Args:
            extension: File extension (with or without dot)
            
        Returns:
            True if the extension is supported
        """
        if not extension:
            return False
            
        # Normalize extension
        if not extension.startswith('.'):
            extension = f'.{extension}'
            
        return extension.lower() in self.supported_extensions
        
    def _process_single_image(self, image: Image.Image, file_path: Path) -> str:
        """Process a single image for OCR.
        
        Args:
            image: PIL Image object
            file_path: Path to original file
            
        Returns:
            Extracted text
        """
        # Assess image quality
        quality_info = self._assess_image_quality_pil(image)
        self._metadata.update({'quality': quality_info})
        
        # Preprocess if enabled and quality suggests it
        if self.preprocessing and quality_info.get('needs_preprocessing', False):
            image = self._preprocess_image_pil(image)
            
        # Extract text with OCR
        try:
            # Get detailed data including confidence scores
            ocr_data = pytesseract.image_to_data(
                image,
                lang=self.language,
                timeout=self.timeout,
                output_type=pytesseract.Output.DICT
            )
            
            # Filter by confidence and reconstruct text
            text_parts = []
            total_confidence = 0
            word_count = 0
            
            for i, conf in enumerate(ocr_data['conf']):
                if conf > -1:  # Valid confidence score
                    if conf >= self.confidence_threshold:
                        text = ocr_data['text'][i].strip()
                        if text:
                            text_parts.append(text)
                            total_confidence += conf
                            word_count += 1
                            
            # Calculate average confidence
            avg_confidence = total_confidence / word_count if word_count > 0 else 0
            self._metadata['ocr_confidence'] = avg_confidence
            self._metadata['word_count'] = word_count
            
            # Join text parts with appropriate spacing
            text = self._reconstruct_text(text_parts, ocr_data)
            
            if not text.strip():
                logger.warning(f"No text extracted from {file_path.name}")
                
            return text
            
        except pytesseract.TesseractError as e:
            raise DocumentProcessingError(
                f"OCR failed: {e}",
                file_path=str(file_path)
            )
            
    def _process_multipage_tiff(self, image: Image.Image, file_path: Path) -> str:
        """Process multi-page TIFF files.
        
        Args:
            image: PIL Image object (first page)
            file_path: Path to TIFF file
            
        Returns:
            Combined text from all pages
        """
        texts = []
        page_count = 0
        
        try:
            # Process each page
            while True:
                try:
                    image.seek(page_count)
                    page_text = self._process_single_image(image, file_path)
                    if page_text.strip():
                        texts.append(f"--- Page {page_count + 1} ---\n{page_text}")
                    page_count += 1
                except EOFError:
                    break
                    
            self._metadata['page_count'] = page_count
            logger.info(f"Processed {page_count} pages from TIFF file")
            
            return '\n\n'.join(texts)
            
        finally:
            # Reset to first page
            image.seek(0)
            
    def _preprocess_image_pil(self, image: Image.Image) -> Image.Image:
        """Preprocess image using PIL for better OCR results.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed image
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Resize if too small
        width, height = image.size
        if width < 300 or height < 300:
            scale = max(300 / width, 300 / height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # Convert to grayscale for better OCR
        image = image.convert('L')
        
        # Apply threshold to get black and white image
        # This helps with text recognition
        threshold = 180
        image = image.point(lambda x: 0 if x < threshold else 255, '1')
        
        return image
        
    def _assess_image_quality_pil(self, image: Image.Image) -> Dict[str, Any]:
        """Assess image quality using PIL.
        
        Args:
            image: PIL Image object
            
        Returns:
            Quality assessment dictionary
        """
        width, height = image.size
        
        quality_info = {
            'width': width,
            'height': height,
            'mode': image.mode,
            'suitable_for_ocr': True,
            'needs_preprocessing': False,
            'warnings': []
        }
        
        # Check resolution
        if width < 150 or height < 150:
            quality_info['warnings'].append('Low resolution - OCR quality may be poor')
            quality_info['needs_preprocessing'] = True
            
        # Check if too large (might cause memory issues)
        if width > 4000 or height > 4000:
            quality_info['warnings'].append('Very high resolution - processing may be slow')
            
        # Check color mode
        if image.mode not in ['L', '1', 'RGB']:
            quality_info['needs_preprocessing'] = True
            
        # Simple contrast check (for grayscale images)
        if image.mode == 'L':
            # Convert to numpy array for analysis
            img_array = np.array(image)
            std_dev = np.std(img_array)
            if std_dev < 30:
                quality_info['warnings'].append('Low contrast detected')
                quality_info['needs_preprocessing'] = True
                
        return quality_info
        
    def _reconstruct_text(self, text_parts: List[str], ocr_data: Dict) -> str:
        """Reconstruct text with proper spacing and line breaks.
        
        Args:
            text_parts: List of text fragments
            ocr_data: OCR data dictionary from Tesseract
            
        Returns:
            Reconstructed text
        """
        if not text_parts:
            return ""
            
        # Use block and paragraph information to add proper line breaks
        lines = []
        current_line = []
        last_block = -1
        last_par = -1
        last_line = -1
        
        word_index = 0
        for i in range(len(ocr_data['text'])):
            if ocr_data['conf'][i] >= self.confidence_threshold:
                text = ocr_data['text'][i].strip()
                if text:
                    block_num = ocr_data['block_num'][i]
                    par_num = ocr_data['par_num'][i]
                    line_num = ocr_data['line_num'][i]
                    
                    # New paragraph or block
                    if block_num != last_block or par_num != last_par:
                        if current_line:
                            lines.append(' '.join(current_line))
                            lines.append('')  # Empty line between paragraphs
                        current_line = [text]
                    # New line within same paragraph
                    elif line_num != last_line:
                        if current_line:
                            lines.append(' '.join(current_line))
                        current_line = [text]
                    # Same line
                    else:
                        current_line.append(text)
                        
                    last_block = block_num
                    last_par = par_num
                    last_line = line_num
                    word_index += 1
                    
        # Add last line
        if current_line:
            lines.append(' '.join(current_line))
            
        return '\n'.join(lines).strip()
        
    def _extract_metadata(self, image: Image.Image, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from image.
        
        Args:
            image: PIL Image object
            file_path: Path to image file
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size,
            'format': image.format,
            'mode': image.mode,
            'width': image.width,
            'height': image.height,
            'language': self.language
        }
        
        # Extract EXIF data if available
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            if exif:
                metadata['has_exif'] = True
                # Add selected EXIF tags
                from PIL.ExifTags import TAGS
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in ['Make', 'Model', 'DateTime', 'Software']:
                        metadata[f'exif_{tag.lower()}'] = str(value)
                        
        return metadata
        
    def _extract_text_from_image(self, image_path: Path) -> str:
        """Extract text from image using OCR.
        
        This method is required by the base class but we implement
        the logic in read() for better control.
        
        Args:
            image_path: Path to image
            
        Returns:
            Extracted text
        """
        # This is handled in the read() method
        return self.read(image_path)


# Convenience function to check OCR availability
def check_ocr_available() -> bool:
    """Check if OCR dependencies are available.
    
    Returns:
        True if OCR is available, False otherwise
    """
    if not HAS_OCR:
        return False
        
    try:
        pytesseract.get_tesseract_version()
        return True
    except:
        return False


# Convenience function to get available languages
def get_available_languages() -> List[str]:
    """Get list of available Tesseract languages.
    
    Returns:
        List of language codes
    """
    if not check_ocr_available():
        return []
        
    try:
        langs = pytesseract.get_languages()
        return [lang for lang in langs if not lang.startswith('osd')]
    except:
        return ['eng']  # Default to English