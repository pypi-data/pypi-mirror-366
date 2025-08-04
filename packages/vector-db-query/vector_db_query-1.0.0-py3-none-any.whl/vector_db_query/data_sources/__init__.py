"""Data Sources Module for Ansera Vector DB Query System.

This module provides integrations with various data sources including:
- Gmail (IMAP email integration)
- Fireflies.ai (meeting transcript webhooks)
- Google Drive (Gemini transcript detection)
"""

from .base import AbstractDataSource, DataSourceConfig, SyncResult
from .models import SourceType, SyncStatus, DataItem
from .exceptions import (
    DataSourceError,
    AuthenticationError,
    SyncError,
    ConfigurationError
)

__all__ = [
    'AbstractDataSource',
    'DataSourceConfig',
    'SyncResult',
    'SourceType',
    'SyncStatus',
    'DataItem',
    'DataSourceError',
    'AuthenticationError',
    'SyncError',
    'ConfigurationError'
]