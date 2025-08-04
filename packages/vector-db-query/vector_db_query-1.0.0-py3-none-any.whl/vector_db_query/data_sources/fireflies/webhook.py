"""Webhook handler for Fireflies.ai notifications."""

import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import asyncio
from pathlib import Path

from ...utils.logger import get_logger

logger = get_logger(__name__)


class FirefliesWebhookHandler:
    """Handles incoming webhooks from Fireflies.ai."""
    
    def __init__(self, webhook_secret: str, callback: Optional[Callable] = None):
        """Initialize webhook handler.
        
        Args:
            webhook_secret: Secret key for webhook signature validation
            callback: Optional async callback function to process webhook data
        """
        self.webhook_secret = webhook_secret
        self.callback = callback
        self.processed_events = set()  # Track processed event IDs
        
        # Create storage directory for webhook logs
        self.log_dir = Path(".vector-db-query/data_sources/webhooks/fireflies")
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature.
        
        Args:
            payload: Raw request body
            signature: Signature from X-Fireflies-Signature header
            
        Returns:
            True if signature is valid
        """
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    async def handle_webhook(self, 
                           headers: Dict[str, str],
                           body: bytes) -> Dict[str, Any]:
        """Handle incoming webhook.
        
        Args:
            headers: Request headers
            body: Raw request body
            
        Returns:
            Response data
        """
        # Log webhook receipt
        webhook_id = headers.get('X-Fireflies-Webhook-Id', 'unknown')
        logger.info(f"Received Fireflies webhook: {webhook_id}")
        
        # Verify signature
        signature = headers.get('X-Fireflies-Signature', '')
        if not self.verify_signature(body, signature):
            logger.error("Invalid webhook signature")
            return {
                'status': 'error',
                'message': 'Invalid signature'
            }
        
        # Parse payload
        try:
            payload = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse webhook payload: {e}")
            return {
                'status': 'error',
                'message': 'Invalid JSON payload'
            }
        
        # Check if already processed
        event_id = payload.get('event_id')
        if event_id and event_id in self.processed_events:
            logger.info(f"Webhook already processed: {event_id}")
            return {
                'status': 'success',
                'message': 'Already processed'
            }
        
        # Log webhook data
        await self._log_webhook(webhook_id, headers, payload)
        
        # Process webhook based on event type
        event_type = payload.get('event', {}).get('type')
        result = await self._process_event(event_type, payload)
        
        # Mark as processed
        if event_id:
            self.processed_events.add(event_id)
        
        # Call custom callback if provided
        if self.callback:
            try:
                await self.callback(event_type, payload)
            except Exception as e:
                logger.error(f"Callback error: {e}")
        
        return result
    
    async def _process_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook event.
        
        Args:
            event_type: Type of event
            payload: Webhook payload
            
        Returns:
            Processing result
        """
        logger.info(f"Processing event type: {event_type}")
        
        if event_type == 'transcription.completed':
            return await self._handle_transcription_completed(payload)
        
        elif event_type == 'meeting.ended':
            return await self._handle_meeting_ended(payload)
        
        elif event_type == 'summary.generated':
            return await self._handle_summary_generated(payload)
        
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return {
                'status': 'success',
                'message': f'Event type {event_type} acknowledged'
            }
    
    async def _handle_transcription_completed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transcription completed event.
        
        Args:
            payload: Webhook payload
            
        Returns:
            Processing result
        """
        data = payload.get('data', {})
        meeting_id = data.get('meeting_id')
        transcript_id = data.get('transcript_id')
        
        logger.info(f"Transcription completed for meeting {meeting_id}")
        
        # Extract key information
        meeting_info = {
            'meeting_id': meeting_id,
            'transcript_id': transcript_id,
            'title': data.get('title'),
            'date': data.get('date'),
            'duration': data.get('duration'),
            'participants': data.get('participants', []),
            'transcript_url': data.get('transcript_url'),
            'audio_url': data.get('audio_url'),
            'video_url': data.get('video_url'),
            'platform': data.get('meeting_platform'),
            'host': data.get('host'),
            'webhook_received': datetime.utcnow().isoformat()
        }
        
        # Save meeting info for processing
        info_file = self.log_dir / f"meeting_{meeting_id}_info.json"
        with open(info_file, 'w') as f:
            json.dump(meeting_info, f, indent=2)
        
        logger.info(f"Saved meeting info to {info_file}")
        
        return {
            'status': 'success',
            'message': 'Transcription completed event processed',
            'meeting_id': meeting_id
        }
    
    async def _handle_meeting_ended(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle meeting ended event.
        
        Args:
            payload: Webhook payload
            
        Returns:
            Processing result
        """
        data = payload.get('data', {})
        meeting_id = data.get('meeting_id')
        
        logger.info(f"Meeting ended: {meeting_id}")
        
        return {
            'status': 'success',
            'message': 'Meeting ended event processed',
            'meeting_id': meeting_id
        }
    
    async def _handle_summary_generated(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle summary generated event.
        
        Args:
            payload: Webhook payload
            
        Returns:
            Processing result
        """
        data = payload.get('data', {})
        meeting_id = data.get('meeting_id')
        summary = data.get('summary', {})
        
        logger.info(f"Summary generated for meeting {meeting_id}")
        
        # Save summary
        summary_file = self.log_dir / f"meeting_{meeting_id}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump({
                'meeting_id': meeting_id,
                'summary': summary,
                'generated_at': datetime.utcnow().isoformat()
            }, f, indent=2)
        
        return {
            'status': 'success',
            'message': 'Summary generated event processed',
            'meeting_id': meeting_id
        }
    
    async def _log_webhook(self, webhook_id: str, headers: Dict[str, str], payload: Dict[str, Any]):
        """Log webhook data for debugging and audit.
        
        Args:
            webhook_id: Webhook ID
            headers: Request headers
            payload: Webhook payload
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"webhook_{timestamp}_{webhook_id}.json"
        
        log_data = {
            'webhook_id': webhook_id,
            'timestamp': datetime.utcnow().isoformat(),
            'headers': {k: v for k, v in headers.items() if not k.lower().startswith('x-api')},
            'payload': payload
        }
        
        try:
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            logger.debug(f"Logged webhook to {log_file}")
        except Exception as e:
            logger.error(f"Failed to log webhook: {e}")
    
    def get_pending_transcripts(self) -> list:
        """Get list of pending transcript IDs.
        
        Returns:
            List of transcript info that need processing
        """
        pending = []
        
        # Find all meeting info files
        for info_file in self.log_dir.glob("meeting_*_info.json"):
            try:
                with open(info_file, 'r') as f:
                    info = json.load(f)
                
                # Check if transcript needs processing
                if info.get('transcript_id') and not self._is_transcript_processed(info['meeting_id']):
                    pending.append(info)
                    
            except Exception as e:
                logger.error(f"Failed to read {info_file}: {e}")
        
        return pending
    
    def _is_transcript_processed(self, meeting_id: str) -> bool:
        """Check if transcript has been processed.
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            True if already processed
        """
        # Check if processed file exists
        processed_file = self.log_dir / f"meeting_{meeting_id}_processed.json"
        return processed_file.exists()
    
    def mark_transcript_processed(self, meeting_id: str, result: Dict[str, Any]):
        """Mark transcript as processed.
        
        Args:
            meeting_id: Meeting ID
            result: Processing result
        """
        processed_file = self.log_dir / f"meeting_{meeting_id}_processed.json"
        
        with open(processed_file, 'w') as f:
            json.dump({
                'meeting_id': meeting_id,
                'processed_at': datetime.utcnow().isoformat(),
                'result': result
            }, f, indent=2)