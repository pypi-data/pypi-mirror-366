"""
Real-time event streaming integration.

This module integrates the SSE infrastructure with the event configuration system
to provide real-time streaming of monitoring events to dashboard clients.
"""

from .event_streamer import EventStreamer, get_event_streamer, reset_event_streamer
from .stream_manager import StreamManager, get_stream_manager, reset_stream_manager

__all__ = [
    'EventStreamer',
    'get_event_streamer',
    'reset_event_streamer',
    'StreamManager',
    'get_stream_manager',
    'reset_stream_manager'
]

__version__ = '1.0.0'