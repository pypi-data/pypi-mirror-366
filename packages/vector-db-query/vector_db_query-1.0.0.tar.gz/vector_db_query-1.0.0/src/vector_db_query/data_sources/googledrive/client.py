"""Google Drive API client for file operations."""

import asyncio
import io
from typing import List, Dict, Any, Optional, AsyncIterator
from datetime import datetime, timedelta
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

from .config import GoogleDriveConfig
from .auth import GoogleDriveOAuth2Provider
from .detector import GeminiTranscriptDetector
from ..auth import AuthToken
from ...utils.logger import get_logger

logger = get_logger(__name__)


class GoogleDriveClient:
    """Client for Google Drive API interactions."""
    
    def __init__(self, config: GoogleDriveConfig):
        """Initialize Google Drive client.
        
        Args:
            config: Google Drive configuration
        """
        self.config = config
        self.auth_provider = GoogleDriveOAuth2Provider(config)
        self.detector = GeminiTranscriptDetector()
        self._service = None
        self._token: Optional[AuthToken] = None
        self._rate_limiter = asyncio.Semaphore(int(config.api_calls_per_second))
    
    async def connect(self) -> bool:
        """Connect to Google Drive API.
        
        Returns:
            True if connection successful
        """
        try:
            # Authenticate
            self._token = await self.auth_provider.authenticate()
            
            # Create service
            creds = Credentials(
                token=self._token.access_token,
                refresh_token=self._token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.auth_provider.client_id,
                client_secret=self.auth_provider.client_secret
            )
            
            self._service = build('drive', 'v3', credentials=creds)
            
            # Test connection
            return await self.auth_provider.test_connection(self._token)
            
        except Exception as e:
            logger.error(f"Failed to connect to Google Drive: {e}")
            return False
    
    async def search_files(self,
                          query: str,
                          folder_ids: Optional[List[str]] = None,
                          since: Optional[datetime] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Search for files in Google Drive.
        
        Args:
            query: Search query (Drive API query syntax)
            folder_ids: Optional list of folder IDs to search in
            since: Only return files modified after this date
            limit: Maximum number of results
            
        Returns:
            List of file metadata dictionaries
        """
        if not self._service:
            raise RuntimeError("Not connected to Google Drive")
        
        # Build query parts
        query_parts = [query]
        
        # Add folder filter
        if folder_ids:
            folder_query = " or ".join(f"'{fid}' in parents" for fid in folder_ids)
            query_parts.append(f"({folder_query})")
        
        # Add date filter
        if since:
            date_str = since.strftime("%Y-%m-%d")
            query_parts.append(f"modifiedTime > '{date_str}'")
        
        # Combine query parts
        full_query = " and ".join(f"({part})" for part in query_parts)
        
        logger.info(f"Searching Google Drive with query: {full_query}")
        
        files = []
        page_token = None
        
        async with self._rate_limiter:
            while len(files) < limit:
                try:
                    # Execute search
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self._service.files().list(
                            q=full_query,
                            pageSize=min(100, limit - len(files)),
                            pageToken=page_token,
                            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, parents, webViewLink)",
                            orderBy="modifiedTime desc"
                        ).execute()
                    )
                    
                    files.extend(result.get('files', []))
                    page_token = result.get('nextPageToken')
                    
                    if not page_token:
                        break
                        
                except HttpError as e:
                    logger.error(f"Search failed: {e}")
                    break
        
        logger.info(f"Found {len(files)} files matching search criteria")
        return files[:limit]
    
    async def search_gemini_transcripts(self,
                                      since: Optional[datetime] = None,
                                      limit: int = 100) -> List[Dict[str, Any]]:
        """Search specifically for Gemini transcripts.
        
        Args:
            since: Only return files modified after this date
            limit: Maximum number of results
            
        Returns:
            List of file metadata for Gemini transcripts
        """
        # Build search queries for each pattern
        all_results = []
        
        for pattern in self.config.search_patterns:
            # Search for pattern in file name and content
            query = f"(name contains '{pattern}' or fullText contains '{pattern}')"
            
            # Add Google Docs filter (Gemini creates Docs)
            query += " and mimeType = 'application/vnd.google-apps.document'"
            
            results = await self.search_files(
                query=query,
                folder_ids=self.config.folder_ids if self.config.folder_ids else None,
                since=since,
                limit=limit - len(all_results)
            )
            
            all_results.extend(results)
            
            if len(all_results) >= limit:
                break
        
        # Remove duplicates
        seen_ids = set()
        unique_results = []
        for file_info in all_results:
            if file_info['id'] not in seen_ids:
                seen_ids.add(file_info['id'])
                unique_results.append(file_info)
        
        return unique_results[:limit]
    
    async def get_file_content(self, file_id: str, mime_type: str) -> str:
        """Get content of a file.
        
        Args:
            file_id: Google Drive file ID
            mime_type: MIME type of the file
            
        Returns:
            File content as string
        """
        if not self._service:
            raise RuntimeError("Not connected to Google Drive")
        
        async with self._rate_limiter:
            try:
                # Handle Google Docs differently
                if mime_type == 'application/vnd.google-apps.document':
                    # Export as plain text
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self._service.files().export(
                            fileId=file_id,
                            mimeType='text/plain'
                        ).execute()
                    )
                    return result.decode('utf-8') if isinstance(result, bytes) else result
                
                else:
                    # Download regular files
                    request = self._service.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    
                    done = False
                    while not done:
                        _, done = await asyncio.get_event_loop().run_in_executor(
                            None,
                            downloader.next_chunk
                        )
                    
                    fh.seek(0)
                    return fh.read().decode('utf-8')
                    
            except HttpError as e:
                logger.error(f"Failed to get file content: {e}")
                raise
    
    async def fetch_transcripts(self,
                              since: Optional[datetime] = None,
                              limit: Optional[int] = None) -> AsyncIterator[Dict[str, Any]]:
        """Fetch Gemini transcripts as an async iterator.
        
        Args:
            since: Fetch transcripts modified after this date
            limit: Maximum number to fetch
            
        Yields:
            Transcript data with content
        """
        # Search for transcripts
        files = await self.search_gemini_transcripts(
            since=since,
            limit=limit or 100
        )
        
        logger.info(f"Found {len(files)} Gemini transcripts to fetch")
        
        # Fetch content for each file
        for file_info in files:
            try:
                # Apply size filters
                file_size = int(file_info.get('size', 0))
                if file_size < self.config.min_file_size_bytes:
                    logger.debug(f"Skipping small file: {file_info['name']} ({file_size} bytes)")
                    continue
                
                if file_size > self.config.max_file_size_bytes:
                    logger.debug(f"Skipping large file: {file_info['name']} ({file_size} bytes)")
                    continue
                
                # Get file content
                content = await self.get_file_content(
                    file_info['id'],
                    file_info['mimeType']
                )
                
                # Validate it's a Gemini transcript
                is_transcript, confidence = self.detector.is_gemini_transcript(
                    content,
                    file_info['name']
                )
                
                if not is_transcript:
                    logger.debug(f"Skipping non-Gemini file: {file_info['name']} (confidence: {confidence:.2f})")
                    continue
                
                # Add content and validation info to file info
                file_info['content'] = content
                file_info['is_gemini_transcript'] = True
                file_info['confidence'] = confidence
                
                yield file_info
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to fetch transcript {file_info['name']}: {e}")
                continue
    
    async def test_connection(self) -> bool:
        """Test Google Drive connection.
        
        Returns:
            True if connection successful
        """
        if not self._token:
            return False
        
        return await self.auth_provider.test_connection(self._token)
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get information about the authenticated user.
        
        Returns:
            User information dictionary
        """
        if not self._service:
            raise RuntimeError("Not connected to Google Drive")
        
        async with self._rate_limiter:
            try:
                about = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._service.about().get(
                        fields="user(displayName, emailAddress), storageQuota"
                    ).execute()
                )
                
                return {
                    'user': about.get('user', {}),
                    'storage': about.get('storageQuota', {})
                }
                
            except HttpError as e:
                logger.error(f"Failed to get user info: {e}")
                return {}
    
    async def analyze_transcript(self, file_id: str) -> Dict[str, Any]:
        """Analyze a potential Gemini transcript.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            Analysis results including validation and extracted data
        """
        if not self._service:
            raise RuntimeError("Not connected to Google Drive")
        
        try:
            # Get file metadata
            files = await self.search_files(f"'{file_id}' in id", limit=1)
            if not files:
                return {'error': 'File not found'}
            
            file_info = files[0]
            
            # Get content
            content = await self.get_file_content(file_id, file_info['mimeType'])
            
            # Validate and analyze
            validation = self.detector.validate_transcript(content)
            
            # Add file info
            validation['file_info'] = {
                'id': file_info['id'],
                'name': file_info['name'],
                'modified_time': file_info['modifiedTime'],
                'size': int(file_info.get('size', 0))
            }
            
            return validation
            
        except Exception as e:
            logger.error(f"Failed to analyze transcript: {e}")
            return {'error': str(e)}