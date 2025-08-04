"""
Stream management for dashboard event streaming.

This module provides high-level stream management for dashboard clients,
handling stream lifecycle, reconnection, and client-specific features.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from threading import RLock
import json
from collections import defaultdict

from .event_streamer import EventStreamer, get_event_streamer
from ..notifications.event_config import EventType
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class StreamClient:
    """Represents a dashboard client stream."""
    
    def __init__(self, client_id: str, name: str, event_filter: Optional[Dict[str, Any]] = None):
        """
        Initialize stream client.
        
        Args:
            client_id: Unique client identifier
            name: Client name/description
            event_filter: Optional event filter
        """
        self.client_id = client_id
        self.name = name
        self.event_filter = event_filter or {}
        self.connected_at = datetime.now()
        self.last_seen = datetime.now()
        self.reconnect_count = 0
        self.events_received = 0
        self.connection_task: Optional[asyncio.Task] = None
        self.is_active = False
        
        # Client preferences
        self.preferences = {
            'auto_reconnect': True,
            'reconnect_delay': 5,  # seconds
            'max_reconnect_attempts': 10,
            'event_buffer_size': 100,
            'heartbeat_timeout': 60  # seconds
        }
        
        # Event buffer for offline periods
        self.event_buffer: List[Dict[str, Any]] = []
        
        # Callbacks
        self.on_event: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_connect: Optional[Callable[[], None]] = None
        self.on_disconnect: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
    
    def update_activity(self):
        """Update last seen timestamp."""
        self.last_seen = datetime.now()
    
    def add_buffered_event(self, event: Dict[str, Any]):
        """Add event to buffer for later delivery."""
        self.event_buffer.append(event)
        if len(self.event_buffer) > self.preferences['event_buffer_size']:
            self.event_buffer.pop(0)
    
    def get_buffered_events(self) -> List[Dict[str, Any]]:
        """Get and clear buffered events."""
        events = self.event_buffer.copy()
        self.event_buffer.clear()
        return events
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'client_id': self.client_id,
            'name': self.name,
            'connected_at': self.connected_at.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'is_active': self.is_active,
            'reconnect_count': self.reconnect_count,
            'events_received': self.events_received,
            'event_filter': self.event_filter,
            'preferences': self.preferences,
            'buffered_events': len(self.event_buffer)
        }


class StreamManager:
    """
    High-level stream manager for dashboard event streaming.
    
    Provides client management, automatic reconnection, and stream orchestration.
    """
    
    def __init__(self):
        """Initialize stream manager."""
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # Event streamer
        self.event_streamer = get_event_streamer()
        
        # Client management
        self._clients: Dict[str, StreamClient] = {}
        self._client_groups: Dict[str, Set[str]] = defaultdict(set)
        
        # Manager state
        self._is_running = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Statistics
        self._stats = {
            'total_clients': 0,
            'active_streams': 0,
            'total_events_delivered': 0,
            'total_reconnects': 0,
            'start_time': None
        }
        
        # Configuration
        self.config = {
            'max_clients': 100,
            'monitor_interval': 10,  # seconds
            'inactive_timeout': 300,  # 5 minutes
            'enable_auto_cleanup': True
        }
        
        logger.info("StreamManager initialized")
    
    async def start(self):
        """Start the stream manager."""
        with self._lock:
            if self._is_running:
                logger.warning("Stream manager is already running")
                return
            
            self._is_running = True
            self._stats['start_time'] = datetime.now()
        
        # Start event streamer if not running
        if not self.event_streamer.is_running:
            await self.event_streamer.start()
        
        # Start monitoring task
        self._monitor_task = asyncio.create_task(self._monitor_clients())
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.CONFIGURATION,
            change_type=ChangeType.UPDATE,
            description="Stream manager started",
            details={'start_time': self._stats['start_time'].isoformat()}
        )
        
        logger.info("Stream manager started")
    
    async def stop(self):
        """Stop the stream manager."""
        with self._lock:
            if not self._is_running:
                return
            
            self._is_running = False
        
        # Stop monitor task
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect all clients
        client_ids = list(self._clients.keys())
        for client_id in client_ids:
            await self.disconnect_client(client_id)
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.CONFIGURATION,
            change_type=ChangeType.UPDATE,
            description="Stream manager stopped",
            details={'stop_time': datetime.now().isoformat()}
        )
        
        logger.info("Stream manager stopped")
    
    async def register_client(self, client_id: str, name: str, 
                            event_filter: Optional[Dict[str, Any]] = None,
                            group: Optional[str] = None) -> StreamClient:
        """
        Register a new stream client.
        
        Args:
            client_id: Unique client identifier
            name: Client name/description
            event_filter: Optional event filter
            group: Optional client group
            
        Returns:
            StreamClient instance
        """
        with self._lock:
            if len(self._clients) >= self.config['max_clients']:
                raise Exception(f"Maximum clients ({self.config['max_clients']}) reached")
            
            if client_id in self._clients:
                raise ValueError(f"Client {client_id} already registered")
            
            # Create client
            client = StreamClient(client_id, name, event_filter)
            self._clients[client_id] = client
            
            # Add to group if specified
            if group:
                self._client_groups[group].add(client_id)
            
            # Update stats
            self._stats['total_clients'] = len(self._clients)
        
        logger.info(f"Registered stream client {client_id} ({name})")
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.SYSTEM,
            change_type=ChangeType.CREATE,
            description=f"Stream client registered: {name}",
            details={'client_id': client_id, 'group': group}
        )
        
        return client
    
    async def connect_client(self, client_id: str, auto_reconnect: bool = True) -> bool:
        """
        Connect a client stream.
        
        Args:
            client_id: Client identifier
            auto_reconnect: Enable auto-reconnection
            
        Returns:
            True if connected successfully
        """
        with self._lock:
            if client_id not in self._clients:
                raise ValueError(f"Client {client_id} not registered")
            
            client = self._clients[client_id]
            
            if client.is_active:
                logger.warning(f"Client {client_id} already connected")
                return True
            
            client.preferences['auto_reconnect'] = auto_reconnect
        
        # Create connection task
        client.connection_task = asyncio.create_task(
            self._handle_client_stream(client)
        )
        
        # Wait for initial connection
        await asyncio.sleep(0.1)
        
        return client.is_active
    
    async def _handle_client_stream(self, client: StreamClient):
        """Handle client stream connection and events."""
        attempt = 0
        
        while attempt < client.preferences['max_reconnect_attempts']:
            try:
                # Update connection attempt
                if attempt > 0:
                    client.reconnect_count += 1
                    self._stats['total_reconnects'] += 1
                    logger.info(f"Reconnecting client {client.client_id} (attempt {attempt + 1})")
                
                # Mark as active
                client.is_active = True
                client.update_activity()
                
                # Update stats
                with self._lock:
                    self._stats['active_streams'] = sum(
                        1 for c in self._clients.values() if c.is_active
                    )
                
                # Trigger connect callback
                if client.on_connect:
                    try:
                        client.on_connect()
                    except Exception as e:
                        logger.error(f"Error in connect callback: {e}")
                
                # Send buffered events if any
                buffered = client.get_buffered_events()
                for event in buffered:
                    if client.on_event:
                        try:
                            client.on_event(event)
                        except Exception as e:
                            logger.error(f"Error delivering buffered event: {e}")
                
                # Stream events
                async for event_data in self.event_streamer.create_client_stream(
                    client.client_id, 
                    client.event_filter
                ):
                    # Update activity
                    client.update_activity()
                    client.events_received += 1
                    self._stats['total_events_delivered'] += 1
                    
                    # Deliver event
                    if client.on_event:
                        try:
                            client.on_event(event_data)
                        except Exception as e:
                            logger.error(f"Error in event callback: {e}")
                            if client.on_error:
                                client.on_error(e)
                
                # Stream ended normally
                break
                
            except asyncio.CancelledError:
                logger.info(f"Client {client.client_id} stream cancelled")
                break
                
            except Exception as e:
                logger.error(f"Error in client {client.client_id} stream: {e}")
                
                # Trigger error callback
                if client.on_error:
                    try:
                        client.on_error(e)
                    except Exception:
                        pass
                
                # Check if should reconnect
                if not client.preferences['auto_reconnect']:
                    break
                
                # Wait before reconnecting
                attempt += 1
                if attempt < client.preferences['max_reconnect_attempts']:
                    await asyncio.sleep(client.preferences['reconnect_delay'])
            
            finally:
                # Mark as inactive
                client.is_active = False
                
                # Update stats
                with self._lock:
                    self._stats['active_streams'] = sum(
                        1 for c in self._clients.values() if c.is_active
                    )
        
        # Trigger disconnect callback
        if client.on_disconnect:
            try:
                client.on_disconnect()
            except Exception as e:
                logger.error(f"Error in disconnect callback: {e}")
        
        logger.info(f"Client {client.client_id} disconnected")
    
    async def disconnect_client(self, client_id: str) -> bool:
        """
        Disconnect a client stream.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if disconnected successfully
        """
        with self._lock:
            if client_id not in self._clients:
                return False
            
            client = self._clients[client_id]
        
        # Cancel connection task
        if client.connection_task and not client.connection_task.done():
            client.connection_task.cancel()
            try:
                await client.connection_task
            except asyncio.CancelledError:
                pass
        
        client.is_active = False
        
        logger.info(f"Disconnected client {client.client_id}")
        return True
    
    async def unregister_client(self, client_id: str) -> bool:
        """
        Unregister a client completely.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if unregistered successfully
        """
        # Disconnect first
        await self.disconnect_client(client_id)
        
        with self._lock:
            if client_id not in self._clients:
                return False
            
            # Remove from clients
            client = self._clients.pop(client_id)
            
            # Remove from groups
            for group_clients in self._client_groups.values():
                group_clients.discard(client_id)
            
            # Update stats
            self._stats['total_clients'] = len(self._clients)
        
        # Track change
        self.change_tracker.track_change(
            category=ChangeCategory.SYSTEM,
            change_type=ChangeType.DELETE,
            description=f"Stream client unregistered: {client.name}",
            details={'client_id': client_id}
        )
        
        logger.info(f"Unregistered client {client_id}")
        return True
    
    async def broadcast_to_group(self, group: str, event_type: str, data: Dict[str, Any]):
        """
        Broadcast event to all clients in a group.
        
        Args:
            group: Group name
            event_type: Event type
            data: Event data
        """
        with self._lock:
            client_ids = list(self._client_groups.get(group, []))
        
        if not client_ids:
            logger.warning(f"No clients in group {group}")
            return
        
        # Create event
        event = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'group_broadcast': True,
            'group': group
        }
        
        # Send to each client
        delivered = 0
        for client_id in client_ids:
            with self._lock:
                client = self._clients.get(client_id)
            
            if client:
                if client.is_active and client.on_event:
                    try:
                        client.on_event(event)
                        delivered += 1
                    except Exception as e:
                        logger.error(f"Error broadcasting to client {client_id}: {e}")
                else:
                    # Buffer for offline clients
                    client.add_buffered_event(event)
        
        logger.info(f"Broadcast to group {group}: {delivered}/{len(client_ids)} delivered")
    
    async def send_to_client(self, client_id: str, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Send event to specific client.
        
        Args:
            client_id: Client identifier
            event_type: Event type
            data: Event data
            
        Returns:
            True if sent successfully
        """
        with self._lock:
            client = self._clients.get(client_id)
        
        if not client:
            logger.warning(f"Client {client_id} not found")
            return False
        
        # Create event
        event = {
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'direct_message': True
        }
        
        if client.is_active and client.on_event:
            try:
                client.on_event(event)
                return True
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
                return False
        else:
            # Buffer for offline client
            client.add_buffered_event(event)
            return True
    
    async def update_client_filter(self, client_id: str, event_filter: Dict[str, Any]):
        """
        Update client's event filter.
        
        Args:
            client_id: Client identifier
            event_filter: New event filter
        """
        with self._lock:
            if client_id not in self._clients:
                raise ValueError(f"Client {client_id} not found")
            
            client = self._clients[client_id]
            client.event_filter = event_filter
        
        # Reconnect if active to apply new filter
        if client.is_active:
            await self.disconnect_client(client_id)
            await self.connect_client(client_id, client.preferences['auto_reconnect'])
        
        logger.info(f"Updated filter for client {client_id}")
    
    async def _monitor_clients(self):
        """Monitor client health and cleanup inactive clients."""
        while self._is_running:
            try:
                await asyncio.sleep(self.config['monitor_interval'])
                
                now = datetime.now()
                inactive_clients = []
                
                with self._lock:
                    for client_id, client in self._clients.items():
                        # Check for inactive clients
                        if self.config['enable_auto_cleanup']:
                            inactive_duration = (now - client.last_seen).total_seconds()
                            if (not client.is_active and 
                                inactive_duration > self.config['inactive_timeout']):
                                inactive_clients.append(client_id)
                
                # Cleanup inactive clients
                for client_id in inactive_clients:
                    logger.info(f"Removing inactive client {client_id}")
                    await self.unregister_client(client_id)
                
            except Exception as e:
                logger.error(f"Error in client monitor: {e}")
    
    def get_client(self, client_id: str) -> Optional[StreamClient]:
        """Get client by ID."""
        with self._lock:
            return self._clients.get(client_id)
    
    def get_all_clients(self) -> List[StreamClient]:
        """Get all registered clients."""
        with self._lock:
            return list(self._clients.values())
    
    def get_group_clients(self, group: str) -> List[StreamClient]:
        """Get all clients in a group."""
        with self._lock:
            client_ids = self._client_groups.get(group, set())
            return [self._clients[cid] for cid in client_ids if cid in self._clients]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get stream manager statistics."""
        with self._lock:
            active_clients = sum(1 for c in self._clients.values() if c.is_active)
            
            uptime = None
            if self._stats['start_time']:
                uptime = (datetime.now() - self._stats['start_time']).total_seconds()
            
            return {
                'manager': {
                    'is_running': self._is_running,
                    'total_clients': self._stats['total_clients'],
                    'active_clients': active_clients,
                    'total_events_delivered': self._stats['total_events_delivered'],
                    'total_reconnects': self._stats['total_reconnects'],
                    'uptime_seconds': uptime
                },
                'clients': [client.to_dict() for client in self._clients.values()],
                'groups': {
                    group: len(clients) for group, clients in self._client_groups.items()
                },
                'config': self.config
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        health_status = "healthy"
        issues = []
        
        # Check if running
        if not self._is_running:
            health_status = "stopped"
            issues.append("Stream manager is not running")
        
        # Check client load
        with self._lock:
            client_count = len(self._clients)
            if client_count >= self.config['max_clients'] * 0.9:
                health_status = "warning"
                issues.append("High client count")
        
        # Check event streamer
        streamer_health = await self.event_streamer.health_check()
        if streamer_health['streaming']['status'] != 'healthy':
            health_status = "degraded"
            issues.extend(streamer_health['streaming']['issues'])
        
        return {
            'status': health_status,
            'issues': issues,
            'is_running': self._is_running,
            'client_count': client_count,
            'max_clients': self.config['max_clients']
        }
    
    @property
    def is_running(self) -> bool:
        """Check if manager is running."""
        return self._is_running
    
    @property
    def client_count(self) -> int:
        """Get total client count."""
        with self._lock:
            return len(self._clients)
    
    @property
    def active_client_count(self) -> int:
        """Get active client count."""
        with self._lock:
            return sum(1 for c in self._clients.values() if c.is_active)


# Singleton instance
_stream_manager: Optional[StreamManager] = None
_manager_lock = RLock()


def get_stream_manager() -> StreamManager:
    """Get singleton stream manager instance."""
    global _stream_manager
    
    with _manager_lock:
        if _stream_manager is None:
            _stream_manager = StreamManager()
        
        return _stream_manager


def reset_stream_manager():
    """Reset the singleton stream manager (mainly for testing)."""
    global _stream_manager
    
    with _manager_lock:
        if _stream_manager and _stream_manager.is_running:
            asyncio.create_task(_stream_manager.stop())
        
        _stream_manager = None


# High-level integration functions
async def register_dashboard_client(name: str, event_filter: Optional[Dict[str, Any]] = None) -> str:
    """
    Register a new dashboard client.
    
    Args:
        name: Client name
        event_filter: Optional event filter
        
    Returns:
        Client ID
    """
    manager = get_stream_manager()
    
    # Ensure manager is running
    if not manager.is_running:
        await manager.start()
    
    # Generate client ID
    import uuid
    client_id = str(uuid.uuid4())
    
    # Register client
    client = await manager.register_client(client_id, name, event_filter, group="dashboard")
    
    return client_id


async def connect_dashboard_client(client_id: str, 
                                 on_event: Callable[[Dict[str, Any]], None],
                                 on_connect: Optional[Callable[[], None]] = None,
                                 on_disconnect: Optional[Callable[[], None]] = None) -> bool:
    """
    Connect a dashboard client with callbacks.
    
    Args:
        client_id: Client ID
        on_event: Event callback
        on_connect: Connect callback
        on_disconnect: Disconnect callback
        
    Returns:
        True if connected successfully
    """
    manager = get_stream_manager()
    
    # Get client
    client = manager.get_client(client_id)
    if not client:
        raise ValueError(f"Client {client_id} not found")
    
    # Set callbacks
    client.on_event = on_event
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    # Connect
    return await manager.connect_client(client_id)


async def disconnect_dashboard_client(client_id: str):
    """Disconnect a dashboard client."""
    manager = get_stream_manager()
    await manager.disconnect_client(client_id)


async def broadcast_dashboard_update(update_type: str, data: Dict[str, Any]):
    """Broadcast update to all dashboard clients."""
    manager = get_stream_manager()
    await manager.broadcast_to_group("dashboard", f"dashboard.{update_type}", data)