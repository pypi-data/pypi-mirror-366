"""Custom exceptions for document processing."""


class DocumentProcessingError(Exception):
    """Base exception for document processing errors."""
    
    def __init__(self, message: str, file_path: str = None, **kwargs):
        """Initialize the error.
        
        Args:
            message: Error message
            file_path: Path to the file that caused the error
            **kwargs: Additional context
        """
        super().__init__(message)
        self.file_path = file_path
        self.context = kwargs


class DocumentReadError(DocumentProcessingError):
    """Raised when a document cannot be read."""
    pass


class UnsupportedFileTypeError(DocumentProcessingError):
    """Raised when attempting to process an unsupported file type."""
    pass


class FileTooLargeError(DocumentProcessingError):
    """Raised when a file exceeds the maximum size limit."""
    
    def __init__(self, message: str, file_size: int, max_size: int, **kwargs):
        """Initialize the error.
        
        Args:
            message: Error message
            file_size: Size of the file in bytes
            max_size: Maximum allowed size in bytes
            **kwargs: Additional context
        """
        super().__init__(message, **kwargs)
        self.file_size = file_size
        self.max_size = max_size


class ChunkingError(DocumentProcessingError):
    """Raised when text chunking fails."""
    pass


class EmbeddingError(DocumentProcessingError):
    """Base exception for embedding-related errors."""
    pass


class EmbeddingAPIError(EmbeddingError):
    """Raised when the embedding API returns an error."""
    
    def __init__(self, message: str, status_code: int = None, **kwargs):
        """Initialize the error.
        
        Args:
            message: Error message
            status_code: HTTP status code if applicable
            **kwargs: Additional context
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code


class RateLimitError(EmbeddingAPIError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: float = None, **kwargs):
        """Initialize the error.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            **kwargs: Additional context
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class AuthenticationError(EmbeddingAPIError):
    """Raised when API authentication fails."""
    pass


class InvalidDimensionsError(EmbeddingError):
    """Raised when invalid embedding dimensions are specified."""
    
    def __init__(self, dimensions: int, valid_dimensions: list):
        """Initialize the error.
        
        Args:
            dimensions: The invalid dimensions specified
            valid_dimensions: List of valid dimension values
        """
        message = (
            f"Invalid embedding dimensions: {dimensions}. "
            f"Valid options are: {', '.join(map(str, valid_dimensions))}"
        )
        super().__init__(message)
        self.dimensions = dimensions
        self.valid_dimensions = valid_dimensions