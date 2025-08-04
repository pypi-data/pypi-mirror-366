"""Base classes for image and OCR readers."""

from abc import abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any
import tempfile

from vector_db_query.document_processor.base import DocumentReader
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class ImageDocumentReader(DocumentReader):
    """Base class for image readers with OCR capabilities."""
    
    def __init__(self,
                 language: str = 'eng',
                 dpi: int = 300,
                 preprocessing: bool = True,
                 timeout: int = 30):
        """Initialize image reader.
        
        Args:
            language: OCR language(s) to use
            dpi: DPI for image processing
            preprocessing: Whether to preprocess images
            timeout: OCR timeout in seconds
        """
        super().__init__()
        self.language = language
        self.dpi = dpi
        self.preprocessing = preprocessing
        self.timeout = timeout
        self._temp_dir = None
        
    def _get_temp_dir(self) -> Path:
        """Get or create temporary directory for image processing.
        
        Returns:
            Path to temporary directory
        """
        if self._temp_dir is None:
            self._temp_dir = tempfile.mkdtemp(prefix='vdq_ocr_')
            logger.debug(f"Created temporary directory: {self._temp_dir}")
        return Path(self._temp_dir)
        
    def _preprocess_image(self, image_path: Path) -> Path:
        """Preprocess image for better OCR results.
        
        Args:
            image_path: Path to original image
            
        Returns:
            Path to preprocessed image
        """
        # Default implementation returns original path
        # Subclasses can override for actual preprocessing
        return image_path
        
    def _assess_image_quality(self, image_path: Path) -> Dict[str, Any]:
        """Assess image quality for OCR suitability.
        
        Args:
            image_path: Path to image
            
        Returns:
            Dictionary with quality metrics
        """
        return {
            'suitable_for_ocr': True,
            'warnings': []
        }
        
    @abstractmethod
    def _extract_text_from_image(self, image_path: Path) -> str:
        """Extract text from image using OCR.
        
        Args:
            image_path: Path to image
            
        Returns:
            Extracted text
        """
        pass
        
    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self._temp_dir:
            import shutil
            try:
                shutil.rmtree(self._temp_dir)
                logger.debug(f"Cleaned up temporary directory: {self._temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")
            finally:
                self._temp_dir = None