"""Custom exceptions for data source integrations."""


class DataSourceError(Exception):
    """Base exception for data source errors."""
    pass


class AuthenticationError(DataSourceError):
    """Raised when authentication fails."""
    pass


class SyncError(DataSourceError):
    """Raised when sync operation fails."""
    pass


class ConfigurationError(DataSourceError):
    """Raised when configuration is invalid."""
    pass


class RateLimitError(DataSourceError):
    """Raised when API rate limit is exceeded."""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class ConnectionError(DataSourceError):
    """Raised when connection to data source fails."""
    pass


class WebhookValidationError(DataSourceError):
    """Raised when webhook validation fails."""
    pass


class ItemProcessingError(DataSourceError):
    """Raised when processing a specific item fails."""
    def __init__(self, message: str, item_id: str = None):
        super().__init__(message)
        self.item_id = item_id