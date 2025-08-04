"""
Individual SSE stream handler for client connections.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Optional, AsyncGenerator, Callable, Dict, Any
from contextlib import asynccontextmanager

from .models import SSEEvent, SSEConnection, ConnectionStatus, EventFilter

logger = logging.getLogger(__name__)


class EventStream:
    """
    Individual SSE stream for a client connection.
    
    Handles event streaming, connection management, and client-specific filtering.
    """
    
    def __init__(
        self,
        connection: SSEConnection,
        event_filter: Optional[EventFilter] = None,
        heartbeat_interval: int = 30,
        max_queue_size: int = 1000
    ):
        """
        Initialize event stream.
        
        Args:
            connection: SSE connection info
            event_filter: Event filter for this stream
            heartbeat_interval: Heartbeat interval in seconds
            max_queue_size: Maximum queued events
        """
        self.connection = connection
        self.event_filter = event_filter
        self.heartbeat_interval = heartbeat_interval
        self.max_queue_size = max_queue_size
        
        # Event queue
        self._event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        # Callbacks
        self.on_connect: Optional[Callable[[SSEConnection], None]] = None
        self.on_disconnect: Optional[Callable[[SSEConnection], None]] = None
        self.on_error: Optional[Callable[[SSEConnection, Exception], None]] = None
        
        logger.info(f"EventStream created for connection {connection.connection_id}")
    
    async def start(self):
        """Start the event stream."""
        if self._running:
            return
        
        self._running = True
        self.connection.status = ConnectionStatus.CONNECTED
        
        # Start heartbeat
        if self.heartbeat_interval > 0:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Call connect callback
        if self.on_connect:
            try:
                self.on_connect(self.connection)
            except Exception as e:
                logger.error(f"Error in connect callback: {str(e)}")
        
        logger.info(f"EventStream started for {self.connection.connection_id}")
    
    async def stop(self):
        """Stop the event stream."""
        if not self._running:
            return
        
        self._running = False
        self.connection.status = ConnectionStatus.DISCONNECTED
        
        # Cancel heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Clear event queue
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        # Call disconnect callback
        if self.on_disconnect:
            try:
                self.on_disconnect(self.connection)
            except Exception as e:
                logger.error(f"Error in disconnect callback: {str(e)}")
        
        logger.info(f"EventStream stopped for {self.connection.connection_id}")
    
    async def send_event(self, event: SSEEvent) -> bool:
        """
        Send an event to the stream.
        
        Args:
            event: Event to send
            
        Returns:
            True if event was queued successfully
        """
        if not self._running:
            return False
        
        # Apply event filter
        if self.event_filter and not self.event_filter.should_include(event):
            return True  # Filtered out, but not an error
        
        try:
            # Add to queue (non-blocking)
            self._event_queue.put_nowait(event)
            return True
        
        except asyncio.QueueFull:
            logger.warning(f"Event queue full for connection {self.connection.connection_id}")
            
            # Drop oldest events to make room
            try:
                while self._event_queue.qsize() >= self.max_queue_size * 0.8:
                    self._event_queue.get_nowait()
                
                self._event_queue.put_nowait(event)
                return True
            
            except asyncio.QueueEmpty:
                return False
    
    async def get_stream(self) -> AsyncGenerator[str, None]:
        """
        Get the SSE stream generator.
        
        Yields:
            SSE formatted event strings
        """
        try:
            # Send initial connection event
            connect_event = SSEEvent(
                event_type="connection_established",
                data={
                    'connection_id': self.connection.connection_id,
                    'server_time': datetime.now().isoformat(),
                    'heartbeat_interval': self.heartbeat_interval
                }
            )
            yield connect_event.to_sse_format()
            
            # Stream events
            while self._running:
                try:
                    # Wait for event with timeout
                    event = await asyncio.wait_for(
                        self._event_queue.get(),
                        timeout=1.0
                    )
                    
                    # Format and yield event
                    sse_data = event.to_sse_format()
                    
                    # Update connection stats
                    self.connection.events_sent += 1
                    self.connection.bytes_sent += len(sse_data.encode('utf-8'))
                    self.connection.update_activity()
                    
                    yield sse_data
                
                except asyncio.TimeoutError:
                    # No events, continue loop
                    continue
                
                except Exception as e:
                    logger.error(f"Error in stream for {self.connection.connection_id}: {str(e)}")
                    
                    # Update error count
                    self.connection.errors_count += 1
                    
                    # Call error callback
                    if self.on_error:
                        try:
                            self.on_error(self.connection, e)
                        except Exception as callback_error:
                            logger.error(f"Error in error callback: {str(callback_error)}")
                    
                    # Send error event to client
                    error_event = SSEEvent(
                        event_type="stream_error",
                        data={
                            'error': str(e),
                            'connection_id': self.connection.connection_id
                        }
                    )
                    yield error_event.to_sse_format()
        
        except Exception as e:
            logger.error(f"Fatal error in stream for {self.connection.connection_id}: {str(e)}")
            
            # Send final error event
            fatal_error_event = SSEEvent(
                event_type="stream_fatal_error",
                data={
                    'error': str(e),
                    'connection_id': self.connection.connection_id
                }
            )
            yield fatal_error_event.to_sse_format()
        
        finally:
            # Ensure stream is stopped
            await self.stop()
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat events."""
        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                if not self._running:
                    break
                
                # Create heartbeat event
                heartbeat_event = SSEEvent(
                    event_type="heartbeat",
                    data={
                        'timestamp': datetime.now().isoformat(),
                        'connection_id': self.connection.connection_id,
                        'events_sent': self.connection.events_sent,
                        'uptime': self.connection.duration
                    }
                )
                
                # Send heartbeat
                await self.send_event(heartbeat_event)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {str(e)}")
    
    def update_filter(self, event_filter: Optional[EventFilter]):
        """Update the event filter for this stream."""
        self.event_filter = event_filter
        logger.info(f"Updated event filter for connection {self.connection.connection_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get stream status information."""
        return {
            'connection_id': self.connection.connection_id,
            'status': self.connection.status.value,
            'running': self._running,
            'queue_size': self._event_queue.qsize(),
            'max_queue_size': self.max_queue_size,
            'events_sent': self.connection.events_sent,
            'bytes_sent': self.connection.bytes_sent,
            'errors_count': self.connection.errors_count,
            'uptime': self.connection.duration,
            'has_filter': self.event_filter is not None,
            'heartbeat_interval': self.heartbeat_interval
        }
    
    @property
    def is_running(self) -> bool:
        """Check if stream is running."""
        return self._running
    
    @property
    def queue_size(self) -> int:
        """Get current queue size."""
        return self._event_queue.qsize()


@asynccontextmanager
async def create_event_stream(
    connection: SSEConnection,
    event_filter: Optional[EventFilter] = None,
    **kwargs
):
    """
    Context manager for creating and managing an event stream.
    
    Args:
        connection: SSE connection info
        event_filter: Optional event filter
        **kwargs: Additional stream options
    
    Yields:
        EventStream instance
    """
    stream = EventStream(connection, event_filter, **kwargs)
    
    try:
        await stream.start()
        yield stream
    finally:
        await stream.stop()


class StreamManager:
    """
    Manages multiple event streams.
    
    Provides centralized control over SSE connections.
    """
    
    def __init__(self):
        """Initialize stream manager."""
        self._streams: Dict[str, EventStream] = {}
        self._lock = asyncio.Lock()
        
        logger.info("StreamManager initialized")
    
    async def add_stream(self, stream: EventStream) -> None:
        """Add a stream to management."""
        async with self._lock:
            self._streams[stream.connection.connection_id] = stream
            
            # Set up callbacks
            stream.on_disconnect = self._on_stream_disconnect
        
        logger.info(f"Added stream {stream.connection.connection_id}")
    
    async def remove_stream(self, connection_id: str) -> bool:
        """Remove a stream from management."""
        async with self._lock:
            if connection_id in self._streams:
                stream = self._streams[connection_id]
                await stream.stop()
                del self._streams[connection_id]
                
                logger.info(f"Removed stream {connection_id}")
                return True
        
        return False
    
    async def broadcast_event(self, event: SSEEvent) -> int:
        """
        Broadcast event to all streams.
        
        Args:
            event: Event to broadcast
            
        Returns:
            Number of streams that received the event
        """
        sent_count = 0
        
        async with self._lock:
            for stream in list(self._streams.values()):
                if await stream.send_event(event):
                    sent_count += 1
        
        return sent_count
    
    async def send_to_stream(self, connection_id: str, event: SSEEvent) -> bool:
        """
        Send event to a specific stream.
        
        Args:
            connection_id: Target connection ID
            event: Event to send
            
        Returns:
            True if sent successfully
        """
        async with self._lock:
            if connection_id in self._streams:
                return await self._streams[connection_id].send_event(event)
        
        return False
    
    async def get_stream_stats(self) -> Dict[str, Any]:
        """Get statistics for all streams."""
        async with self._lock:
            stats = {
                'total_streams': len(self._streams),
                'active_streams': sum(1 for s in self._streams.values() if s.is_running),
                'total_events_sent': sum(s.connection.events_sent for s in self._streams.values()),
                'total_bytes_sent': sum(s.connection.bytes_sent for s in self._streams.values()),
                'total_errors': sum(s.connection.errors_count for s in self._streams.values()),
                'streams': [s.get_status() for s in self._streams.values()]
            }
        
        return stats
    
    async def cleanup_inactive_streams(self, max_age_seconds: int = 300):
        """Remove inactive streams."""
        current_time = datetime.now()
        to_remove = []
        
        async with self._lock:
            for connection_id, stream in self._streams.items():
                if not stream.is_running:
                    to_remove.append(connection_id)
                elif (current_time - stream.connection.last_activity).total_seconds() > max_age_seconds:
                    to_remove.append(connection_id)
        
        for connection_id in to_remove:
            await self.remove_stream(connection_id)
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} inactive streams")
    
    async def _on_stream_disconnect(self, connection: SSEConnection):
        """Handle stream disconnect."""
        async with self._lock:
            if connection.connection_id in self._streams:
                del self._streams[connection.connection_id]
        
        logger.info(f"Stream disconnected: {connection.connection_id}")
    
    async def shutdown(self):
        """Shutdown all streams."""
        async with self._lock:
            for stream in list(self._streams.values()):
                await stream.stop()
            
            self._streams.clear()
        
        logger.info("All streams shut down")
    
    @property
    def active_stream_count(self) -> int:
        """Get number of active streams."""
        return len([s for s in self._streams.values() if s.is_running])