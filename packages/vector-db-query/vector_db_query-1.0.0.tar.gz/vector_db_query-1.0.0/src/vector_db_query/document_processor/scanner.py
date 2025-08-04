"""File scanner for document discovery."""

import os
from pathlib import Path
from typing import Iterator, List, Optional, Set

from vector_db_query.document_processor.exceptions import FileTooLargeError
from vector_db_query.document_processor.models import DocumentMetadata
from vector_db_query.utils.config import get_config
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class FileScanner:
    """Scans directories for processable documents."""
    
    def __init__(
        self,
        supported_extensions: Optional[Set[str]] = None,
        max_file_size_mb: Optional[float] = None,
        ignored_patterns: Optional[List[str]] = None,
        allowed_formats: Optional[List[str]] = None
    ):
        """Initialize the file scanner.
        
        Args:
            supported_extensions: Set of supported file extensions (e.g., {'.txt', '.pdf'})
            max_file_size_mb: Maximum file size in megabytes
            ignored_patterns: List of patterns to ignore (e.g., ['.*', '__pycache__'])
            allowed_formats: List of allowed file formats to filter (overrides supported_extensions)
        """
        config = get_config()
        
        # If allowed_formats is specified, use that to filter
        if allowed_formats:
            self.supported_extensions = set(f".{fmt}" if not fmt.startswith('.') else fmt 
                                           for fmt in allowed_formats)
        else:
            # Get all supported formats from ReaderFactory
            from vector_db_query.document_processor.reader import ReaderFactory
            all_formats = ReaderFactory.get_supported_extensions()
            self.supported_extensions = supported_extensions or set(f".{ext}" for ext in all_formats)
        
        self.max_file_size_mb = max_file_size_mb or config.get(
            "document_processing.scanner.max_file_size_mb", 100
        )
        self.max_file_size_bytes = int(self.max_file_size_mb * 1024 * 1024)
        self.ignored_patterns = set(ignored_patterns or config.get(
            "document_processing.scanner.ignored_patterns", [".*", "__pycache__"]
        ))
        
        logger.debug(
            f"FileScanner initialized - Extensions: {self.supported_extensions}, "
            f"Max size: {self.max_file_size_mb}MB"
        )
        
    def scan_directory(
        self,
        directory: Path,
        recursive: bool = True,
        follow_symlinks: bool = False
    ) -> Iterator[Path]:
        """Scan directory for supported files.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
            follow_symlinks: Whether to follow symbolic links
            
        Yields:
            Paths to supported files
        """
        directory = Path(directory).resolve()
        
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory}")
            return
            
        if not directory.is_dir():
            logger.error(f"Path is not a directory: {directory}")
            return
            
        logger.info(f"Scanning directory: {directory} (recursive={recursive})")
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
            
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                if self._should_process_file(file_path):
                    yield file_path
                    
    def scan_files(self, file_paths: List[Path]) -> Iterator[Path]:
        """Scan a list of files.
        
        Args:
            file_paths: List of file paths to scan
            
        Yields:
            Paths to supported files
        """
        for file_path in file_paths:
            file_path = Path(file_path).resolve()
            if file_path.exists() and file_path.is_file():
                if self._should_process_file(file_path):
                    yield file_path
                else:
                    logger.debug(f"Skipping file: {file_path}")
            else:
                logger.warning(f"File does not exist or is not a file: {file_path}")
                
    def validate_file_type(self, file_path: Path) -> bool:
        """Check if file type is supported.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file type is supported
        """
        return file_path.suffix.lower() in self.supported_extensions
        
    def validate_file_size(self, file_path: Path) -> bool:
        """Check if file size is within limits.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file size is acceptable
            
        Raises:
            FileTooLargeError: If file exceeds size limit
        """
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size_bytes:
            raise FileTooLargeError(
                f"File too large: {file_size / 1024 / 1024:.2f}MB "
                f"(max: {self.max_file_size_mb}MB)",
                file_path=str(file_path),
                file_size=file_size,
                max_size=self.max_file_size_bytes
            )
        return True
        
    def get_file_metadata(self, file_path: Path) -> DocumentMetadata:
        """Extract metadata from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Document metadata
        """
        return DocumentMetadata.from_path(file_path)
        
    def filter_by_size(self, files: List[Path], max_size_mb: Optional[float] = None) -> List[Path]:
        """Filter files by size.
        
        Args:
            files: List of file paths
            max_size_mb: Maximum file size in MB (uses default if None)
            
        Returns:
            List of files within size limit
        """
        max_size_bytes = int((max_size_mb or self.max_file_size_mb) * 1024 * 1024)
        filtered = []
        
        for file_path in files:
            try:
                if file_path.stat().st_size <= max_size_bytes:
                    filtered.append(file_path)
                else:
                    logger.warning(
                        f"File too large: {file_path} "
                        f"({file_path.stat().st_size / 1024 / 1024:.2f}MB)"
                    )
            except OSError as e:
                logger.error(f"Error accessing file {file_path}: {e}")
                
        return filtered
        
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be processed
        """
        # Check if file name matches ignored patterns
        file_name = file_path.name
        for pattern in self.ignored_patterns:
            if pattern.startswith(".") and file_name.startswith(pattern):
                logger.debug(f"Ignoring hidden file: {file_path}")
                return False
            elif pattern in file_name:
                logger.debug(f"Ignoring file matching pattern '{pattern}': {file_path}")
                return False
                
        # Check file type
        if not self.validate_file_type(file_path):
            logger.debug(f"Unsupported file type: {file_path}")
            return False
            
        # Check file size
        try:
            self.validate_file_size(file_path)
        except FileTooLargeError as e:
            logger.warning(str(e))
            return False
            
        return True
        
    def get_scan_summary(self, directory: Path, recursive: bool = True) -> dict:
        """Get a summary of files in a directory.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            Dictionary with scan summary
        """
        total_files = 0
        supported_files = 0
        total_size = 0
        files_by_type = {}
        
        for file_path in self.scan_directory(directory, recursive):
            total_files += 1
            supported_files += 1
            file_size = file_path.stat().st_size
            total_size += file_size
            
            ext = file_path.suffix.lower()
            if ext not in files_by_type:
                files_by_type[ext] = {"count": 0, "size": 0}
            files_by_type[ext]["count"] += 1
            files_by_type[ext]["size"] += file_size
            
        return {
            "directory": str(directory),
            "total_files": total_files,
            "supported_files": supported_files,
            "total_size_mb": total_size / 1024 / 1024,
            "files_by_type": files_by_type
        }