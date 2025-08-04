"""Google Drive integration module for Gemini transcripts."""

from .config import GoogleDriveConfig
from .auth import GoogleDriveOAuth2Provider
from .client import GoogleDriveClient
from .detector import GeminiTranscriptDetector
from .processor import GeminiTranscriptProcessor, GeminiProcessingPipeline
from .source import GoogleDriveDataSource

__all__ = [
    "GoogleDriveConfig",
    "GoogleDriveOAuth2Provider", 
    "GoogleDriveClient",
    "GeminiTranscriptDetector",
    "GeminiTranscriptProcessor",
    "GeminiProcessingPipeline",
    "GoogleDriveDataSource"
]