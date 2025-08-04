"""Fireflies webhook endpoint."""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
from typing import Dict, Any

from ...data_sources.fireflies.webhook import FirefliesWebhookHandler
from ...data_sources.orchestrator import DataSourceOrchestrator
from ...utils.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

# Initialize webhook handler
webhook_secret = os.getenv("FIREFLIES_WEBHOOK_SECRET", "")
if not webhook_secret:
    logger.warning("FIREFLIES_WEBHOOK_SECRET not set - webhook validation will fail")

webhook_handler = FirefliesWebhookHandler(webhook_secret)


async def process_transcript_in_background(event_type: str, payload: Dict[str, Any]):
    """Background task to process transcript.
    
    Args:
        event_type: Webhook event type
        payload: Webhook payload
    """
    try:
        if event_type == 'transcription.completed':
            # Get orchestrator
            orchestrator = DataSourceOrchestrator()
            
            # Trigger sync for Fireflies source
            logger.info("Triggering Fireflies sync from webhook")
            await orchestrator.sync_source('fireflies')
            
    except Exception as e:
        logger.error(f"Background transcript processing failed: {e}")


@router.post("/fireflies")
async def fireflies_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Fireflies webhook.
    
    This endpoint receives webhooks from Fireflies.ai when:
    - Transcription is completed
    - Meeting ends
    - Summary is generated
    
    Args:
        request: FastAPI request object
        background_tasks: FastAPI background tasks
        
    Returns:
        JSON response
    """
    try:
        # Get headers
        headers = dict(request.headers)
        
        # Get raw body
        body = await request.body()
        
        # Log webhook receipt
        logger.info(f"Received Fireflies webhook - Size: {len(body)} bytes")
        
        # Process webhook
        result = await webhook_handler.handle_webhook(headers, body)
        
        # Check if successful
        if result['status'] == 'error':
            raise HTTPException(status_code=400, detail=result['message'])
        
        # Add background task for transcript processing
        if webhook_handler.callback is None:
            webhook_handler.callback = process_transcript_in_background
        
        # Return success response
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/fireflies/status")
async def fireflies_webhook_status():
    """Get Fireflies webhook status.
    
    Returns:
        Webhook configuration and pending transcripts
    """
    try:
        # Get pending transcripts
        pending = webhook_handler.get_pending_transcripts()
        
        return {
            'status': 'active',
            'webhook_configured': bool(webhook_secret),
            'pending_transcripts': len(pending),
            'pending_details': [
                {
                    'meeting_id': t['meeting_id'],
                    'title': t.get('title', 'Unknown'),
                    'date': t.get('date'),
                    'duration': t.get('duration')
                }
                for t in pending[:10]  # Limit to 10
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get webhook status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")


@router.post("/fireflies/test")
async def test_fireflies_webhook():
    """Test webhook endpoint.
    
    Sends a test payload to verify webhook is working.
    
    Returns:
        Test result
    """
    # Create test payload
    test_payload = {
        'event_id': 'test_12345',
        'event': {
            'type': 'transcription.completed'
        },
        'data': {
            'meeting_id': 'test_meeting_123',
            'transcript_id': 'test_transcript_123',
            'title': 'Test Meeting',
            'date': '2025-08-03T12:00:00Z',
            'duration': 1800,
            'participants': ['Test User 1', 'Test User 2'],
            'transcript_url': 'https://example.com/transcript',
            'platform': 'zoom',
            'host': 'Test Host'
        }
    }
    
    # Create test headers
    import json
    import hmac
    import hashlib
    
    body = json.dumps(test_payload).encode()
    signature = hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'X-Fireflies-Webhook-Id': 'test_webhook_123',
        'X-Fireflies-Signature': signature,
        'Content-Type': 'application/json'
    }
    
    # Process test webhook
    result = await webhook_handler.handle_webhook(headers, body)
    
    return {
        'test_result': result,
        'webhook_secret_configured': bool(webhook_secret)
    }