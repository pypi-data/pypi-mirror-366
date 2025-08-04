"""Fireflies.ai API client for transcript retrieval."""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime, timedelta
from dataclasses import dataclass

from .config import FirefliesConfig
from ...utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FirefliesTranscript:
    """Represents a Fireflies transcript."""
    id: str
    title: str
    date: datetime
    duration: int  # seconds
    participants: List[str]
    transcript_text: str
    summary: Optional[str] = None
    action_items: Optional[List[str]] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    meeting_url: Optional[str] = None
    platform: Optional[str] = None
    host_email: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'FirefliesTranscript':
        """Create from API response data."""
        return cls(
            id=data['id'],
            title=data.get('title', 'Untitled Meeting'),
            date=datetime.fromisoformat(data['date'].replace('Z', '+00:00')),
            duration=data.get('duration', 0),
            participants=data.get('participants', []),
            transcript_text=data.get('transcript', ''),
            summary=data.get('summary'),
            action_items=data.get('action_items', []),
            audio_url=data.get('audio_url'),
            video_url=data.get('video_url'),
            meeting_url=data.get('meeting_url'),
            platform=data.get('organizer_platform'),
            host_email=data.get('host_email')
        )


class FirefliesClient:
    """Client for Fireflies.ai API interactions."""
    
    # GraphQL queries
    QUERY_USER_INFO = """
    query {
        user {
            email
            name
            minutesConsumed
            minutesLimit
        }
    }
    """
    
    QUERY_LIST_TRANSCRIPTS = """
    query ListTranscripts($limit: Int!, $skip: Int!, $fromDate: String, $toDate: String) {
        transcripts(limit: $limit, skip: $skip, fromDate: $fromDate, toDate: $toDate) {
            id
            title
            date
            duration
            participants
            organizer_platform
            host_email
            meeting_url
        }
    }
    """
    
    QUERY_GET_TRANSCRIPT = """
    query GetTranscript($transcriptId: String!) {
        transcript(id: $transcriptId) {
            id
            title
            date
            duration
            participants
            transcript
            summary
            action_items
            audio_url
            video_url
            meeting_url
            organizer_platform
            host_email
            sentences {
                speaker_name
                speaker_id
                text
                start_time
                end_time
            }
        }
    }
    """
    
    def __init__(self, config: Optional[FirefliesConfig] = None):
        """Initialize Fireflies API client.
        
        Args:
            config: Fireflies configuration
        """
        self.config = config or FirefliesConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_reset = datetime.utcnow()
        self._rate_limit_remaining = 100  # Default rate limit
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self):
        """Create HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.config.api_key}',
                    'Content-Type': 'application/json'
                }
            )
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Query variables
            
        Returns:
            API response data
            
        Raises:
            Exception: If API request fails
        """
        if not self.session:
            await self.connect()
        
        # Check rate limit
        if datetime.utcnow() < self._rate_limit_reset and self._rate_limit_remaining <= 0:
            wait_time = (self._rate_limit_reset - datetime.utcnow()).total_seconds()
            logger.warning(f"Rate limit hit, waiting {wait_time:.1f} seconds")
            await asyncio.sleep(wait_time)
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            async with self.session.post(self.config.api_url, json=payload) as response:
                # Update rate limit info from headers
                if 'X-RateLimit-Remaining' in response.headers:
                    self._rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
                if 'X-RateLimit-Reset' in response.headers:
                    self._rate_limit_reset = datetime.fromtimestamp(
                        int(response.headers['X-RateLimit-Reset'])
                    )
                
                # Check response
                response.raise_for_status()
                data = await response.json()
                
                # Check for GraphQL errors
                if 'errors' in data:
                    error_msg = '; '.join(e.get('message', 'Unknown error') for e in data['errors'])
                    raise Exception(f"GraphQL error: {error_msg}")
                
                return data.get('data', {})
                
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            raise
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Get current user information.
        
        Returns:
            User information including usage limits
        """
        data = await self._execute_query(self.QUERY_USER_INFO)
        return data.get('user', {})
    
    async def list_transcripts(self,
                             since: Optional[datetime] = None,
                             until: Optional[datetime] = None,
                             limit: int = 50) -> List[Dict[str, Any]]:
        """List transcripts within date range.
        
        Args:
            since: Start date (default: 30 days ago)
            until: End date (default: now)
            limit: Maximum transcripts to return
            
        Returns:
            List of transcript metadata
        """
        # Default date range
        if not since:
            since = datetime.utcnow() - timedelta(days=self.config.initial_history_days)
        if not until:
            until = datetime.utcnow()
        
        variables = {
            'limit': min(limit, 100),  # API limit
            'skip': 0,
            'fromDate': since.isoformat(),
            'toDate': until.isoformat()
        }
        
        all_transcripts = []
        
        while len(all_transcripts) < limit:
            data = await self._execute_query(self.QUERY_LIST_TRANSCRIPTS, variables)
            transcripts = data.get('transcripts', [])
            
            if not transcripts:
                break
            
            all_transcripts.extend(transcripts)
            
            # Check if we have more pages
            if len(transcripts) < variables['limit']:
                break
            
            variables['skip'] += variables['limit']
        
        return all_transcripts[:limit]
    
    async def get_transcript(self, transcript_id: str) -> FirefliesTranscript:
        """Get full transcript details.
        
        Args:
            transcript_id: Transcript ID
            
        Returns:
            Full transcript object
        """
        variables = {'transcriptId': transcript_id}
        data = await self._execute_query(self.QUERY_GET_TRANSCRIPT, variables)
        
        transcript_data = data.get('transcript')
        if not transcript_data:
            raise Exception(f"Transcript not found: {transcript_id}")
        
        # Process sentences for full transcript
        sentences = transcript_data.get('sentences', [])
        if sentences:
            # Build transcript from sentences with speaker names
            transcript_lines = []
            current_speaker = None
            
            for sentence in sentences:
                speaker = sentence.get('speaker_name', 'Unknown')
                text = sentence.get('text', '')
                
                if speaker != current_speaker:
                    transcript_lines.append(f"\n{speaker}:")
                    current_speaker = speaker
                
                transcript_lines.append(text)
            
            transcript_data['transcript'] = ' '.join(transcript_lines)
        
        return FirefliesTranscript.from_api_response(transcript_data)
    
    async def fetch_transcripts(self,
                              since: Optional[datetime] = None,
                              limit: Optional[int] = None) -> AsyncIterator[FirefliesTranscript]:
        """Fetch transcripts as an async iterator.
        
        Args:
            since: Fetch transcripts since this date
            limit: Maximum number to fetch
            
        Yields:
            FirefliesTranscript objects
        """
        # Get transcript list
        transcript_list = await self.list_transcripts(since=since, limit=limit or 100)
        
        logger.info(f"Found {len(transcript_list)} transcripts to fetch")
        
        # Fetch each transcript
        for transcript_meta in transcript_list:
            try:
                # Apply filters
                duration = transcript_meta.get('duration', 0)
                if duration < self.config.min_duration_seconds:
                    logger.debug(f"Skipping short transcript: {duration}s")
                    continue
                
                if duration > self.config.max_duration_seconds:
                    logger.debug(f"Skipping long transcript: {duration}s")
                    continue
                
                # Platform filter
                platform = transcript_meta.get('organizer_platform', '').lower()
                if self.config.platform_filters and platform not in self.config.platform_filters:
                    logger.debug(f"Skipping platform: {platform}")
                    continue
                
                # User filters
                participants = transcript_meta.get('participants', [])
                if self.config.included_users:
                    if not any(user in ' '.join(participants) for user in self.config.included_users):
                        logger.debug("Skipping - no included users found")
                        continue
                
                if self.config.excluded_users:
                    if any(user in ' '.join(participants) for user in self.config.excluded_users):
                        logger.debug("Skipping - excluded user found")
                        continue
                
                # Fetch full transcript
                transcript = await self.get_transcript(transcript_meta['id'])
                yield transcript
                
                # Rate limit protection
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to fetch transcript {transcript_meta['id']}: {e}")
                continue
    
    async def test_connection(self) -> bool:
        """Test API connection and credentials.
        
        Returns:
            True if connection successful
        """
        try:
            user_info = await self.get_user_info()
            logger.info(f"Connected as: {user_info.get('email', 'Unknown')}")
            logger.info(f"Usage: {user_info.get('minutesConsumed', 0)}/{user_info.get('minutesLimit', 'Unlimited')} minutes")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False