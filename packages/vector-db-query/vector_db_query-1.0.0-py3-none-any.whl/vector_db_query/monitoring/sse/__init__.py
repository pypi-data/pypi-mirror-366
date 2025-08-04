"""
Server-Sent Events (SSE) Infrastructure for Real-Time Dashboard Updates

Provides enterprise-grade SSE streaming for real-time monitoring dashboard updates.

Components:
- SSEManager: Core SSE connection and event management
- EventStream: Individual SSE stream handler
- EventBroadcaster: Multi-client event broadcasting
- SSEMiddleware: FastAPI/Streamlit integration middleware

Usage:
    from vector_db_query.monitoring.sse import SSEManager, EventBroadcaster
    
    # Create SSE manager
    sse_manager = SSEManager()
    
    # Start broadcasting
    sse_manager.start()
    
    # Broadcast event to all clients
    sse_manager.broadcast_event({
        'type': 'task_completed',
        'data': {'task_id': '123', 'status': 'success'}
    })
"""

from .manager import SSEManager
from .stream import EventStream
from .broadcaster import EventBroadcaster
from .middleware import SSEMiddleware
from .models import SSEEvent, SSEConnection, SSEStats

__all__ = [
    'SSEManager',
    'EventStream',
    'EventBroadcaster', 
    'SSEMiddleware',
    'SSEEvent',
    'SSEConnection',
    'SSEStats'
]

__version__ = '1.0.0'