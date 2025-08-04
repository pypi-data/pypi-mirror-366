"""
Main notification manager that coordinates all notification components.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set
from collections import defaultdict, deque

from .models import (
    Notification, NotificationChannel, NotificationResult,
    NotificationStatus, ChannelConfig, NotificationStats,
    RateLimitBucket, NotificationSeverity, DeliveryPriority
)
from .channels import (
    NotificationChannelBase, EmailNotifier, PushNotifier,
    ToastNotifier, WebhookNotifier
)
from .rules import NotificationRules, NotificationRule
from .templates import NotificationTemplates

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Main notification manager that coordinates channels, rules, and templates.
    
    Provides the primary interface for sending notifications across multiple channels.
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        sse_manager=None,
        max_queue_size: int = 10000,
        retry_interval: int = 60
    ):
        """
        Initialize notification manager.
        
        Args:
            config_path: Path to configuration file
            sse_manager: SSE manager for real-time notifications
            max_queue_size: Maximum notification queue size
            retry_interval: Retry interval in seconds
        """
        self.config_path = Path(config_path) if config_path else None
        self.sse_manager = sse_manager
        self.max_queue_size = max_queue_size
        self.retry_interval = retry_interval
        
        # Core components
        self._channels: Dict[str, NotificationChannelBase] = {}
        self._channel_configs: Dict[str, ChannelConfig] = {}
        self.rules = NotificationRules()
        self.templates = NotificationTemplates()
        
        # Notification queues
        self._pending_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._retry_queue: deque = deque()
        self._notification_store: Dict[str, Notification] = {}
        
        # Rate limiting
        self._rate_limiters: Dict[str, RateLimitBucket] = {}
        
        # Statistics
        self._stats = NotificationStats()
        self._channel_stats: Dict[str, NotificationStats] = defaultdict(NotificationStats)
        
        # Background tasks
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._retry_task: Optional[asyncio.Task] = None
        
        # Load configuration if provided
        if self.config_path and self.config_path.exists():
            self.load_configuration(str(self.config_path))
        
        logger.info("NotificationManager initialized")
    
    async def start(self):
        """Start the notification manager."""
        if self._running:
            logger.warning("NotificationManager is already running")
            return
        
        self._running = True
        
        # Initialize channels
        for channel_name, channel in self._channels.items():
            await channel.initialize()
        
        # Start background tasks
        self._processor_task = asyncio.create_task(self._process_notifications())
        self._retry_task = asyncio.create_task(self._retry_notifications())
        
        logger.info("NotificationManager started")
    
    async def stop(self):
        """Stop the notification manager."""
        if not self._running:
            logger.warning("NotificationManager is not running")
            return
        
        self._running = False
        
        # Cancel background tasks
        if self._processor_task:
            self._processor_task.cancel()
        if self._retry_task:
            self._retry_task.cancel()
        
        # Process remaining notifications
        remaining = self._pending_queue.qsize()
        if remaining > 0:
            logger.info(f"Processing {remaining} remaining notifications...")
            await self._flush_queue()
        
        logger.info("NotificationManager stopped")
    
    def add_channel(
        self,
        channel_name: str,
        channel: Union[NotificationChannelBase, ChannelConfig]
    ):
        """
        Add a notification channel.
        
        Args:
            channel_name: Channel identifier
            channel: Channel instance or configuration
        """
        if isinstance(channel, ChannelConfig):
            # Create channel from config
            config = channel
            channel_instance = self._create_channel_from_config(config)
            if channel_instance:
                self._channels[channel_name] = channel_instance
                self._channel_configs[channel_name] = config
        else:
            # Direct channel instance
            self._channels[channel_name] = channel
            self._channel_configs[channel_name] = channel.config
        
        logger.info(f"Added notification channel: {channel_name}")
    
    def remove_channel(self, channel_name: str) -> bool:
        """Remove a notification channel."""
        if channel_name in self._channels:
            del self._channels[channel_name]
            del self._channel_configs[channel_name]
            logger.info(f"Removed notification channel: {channel_name}")
            return True
        return False
    
    async def send_notification(
        self,
        title: str,
        message: str,
        severity: Union[NotificationSeverity, str] = NotificationSeverity.INFO,
        channels: Optional[List[Union[NotificationChannel, str]]] = None,
        recipients: Optional[List[str]] = None,
        data: Optional[Dict[str, Any]] = None,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        priority: Union[DeliveryPriority, str] = DeliveryPriority.NORMAL,
        source: str = "system",
        event_type: Optional[str] = None,
        delay_seconds: int = 0
    ) -> str:
        """
        Send a notification through configured channels.
        
        Args:
            title: Notification title
            message: Notification message
            severity: Notification severity
            channels: Target channels (None for default)
            recipients: Recipients list
            data: Additional data
            template_name: Template to use
            template_data: Template data
            priority: Delivery priority
            source: Notification source
            event_type: Event type for rule matching
            delay_seconds: Delay before sending
            
        Returns:
            Notification ID
        """
        # Convert string enums if needed
        if isinstance(severity, str):
            severity = NotificationSeverity(severity)
        if isinstance(priority, str):
            priority = DeliveryPriority(priority)
        
        # Convert channel strings to enums
        if channels:
            channel_enums = []
            for ch in channels:
                if isinstance(ch, str):
                    channel_enums.append(NotificationChannel(ch))
                else:
                    channel_enums.append(ch)
            channels = channel_enums
        
        # Create notification
        notification = Notification(
            title=title,
            message=message,
            severity=severity,
            channels=channels or [],
            recipients=recipients or [],
            data=data or {},
            template_name=template_name,
            template_data=template_data or {},
            priority=priority,
            source=source,
            event_type=event_type,
            delay_seconds=delay_seconds
        )
        
        # Apply template if specified
        if template_name:
            try:
                rendered = self.templates.render_notification(
                    template_name,
                    template_data or {}
                )
                notification.title = rendered['title']
                notification.message = rendered['message']
            except Exception as e:
                logger.error(f"Error applying template {template_name}: {str(e)}")
        
        # Apply rules if event type specified
        if event_type:
            event_data = {
                'event_type': event_type,
                'severity': severity.value,
                'source': source,
                'data': data or {}
            }
            
            # Get notifications from rules
            rule_notifications = self.rules.create_notifications_from_event(
                event_data,
                base_notification=notification
            )
            
            # Send all rule-generated notifications
            for rule_notification in rule_notifications:
                await self._queue_notification(rule_notification)
        else:
            # Queue the original notification
            await self._queue_notification(notification)
        
        return notification.id
    
    async def send_alert(
        self,
        alert_type: str,
        title: str,
        message: str,
        severity: Union[NotificationSeverity, str] = NotificationSeverity.WARNING,
        **kwargs
    ) -> str:
        """Send an alert notification."""
        return await self.send_notification(
            title=title,
            message=message,
            severity=severity,
            event_type=f"alert_{alert_type}",
            **kwargs
        )
    
    async def send_from_event(
        self,
        event_data: Dict[str, Any],
        default_channels: Optional[List[NotificationChannel]] = None
    ) -> List[str]:
        """
        Send notifications based on event data and rules.
        
        Args:
            event_data: Event data dictionary
            default_channels: Default channels if no rules match
            
        Returns:
            List of notification IDs
        """
        # Create notifications from rules
        notifications = self.rules.create_notifications_from_event(event_data)
        
        # If no rules matched, create default notification
        if not notifications and default_channels:
            notification = Notification(
                title=event_data.get('title', 'System Event'),
                message=event_data.get('message', 'An event occurred'),
                severity=NotificationSeverity(event_data.get('severity', 'info')),
                channels=default_channels,
                source=event_data.get('source', 'system'),
                event_type=event_data.get('event_type'),
                data=event_data.get('data', {})
            )
            notifications = [notification]
        
        # Queue all notifications
        notification_ids = []
        for notification in notifications:
            await self._queue_notification(notification)
            notification_ids.append(notification.id)
        
        return notification_ids
    
    async def _queue_notification(self, notification: Notification):
        """Queue a notification for processing."""
        # Store notification
        self._notification_store[notification.id] = notification
        
        # Apply delay if specified
        if notification.delay_seconds > 0:
            asyncio.create_task(self._delayed_queue(notification))
        else:
            try:
                await self._pending_queue.put(notification)
            except asyncio.QueueFull:
                logger.error(f"Notification queue full, dropping notification {notification.id}")
                self._stats.total_failed += 1
    
    async def _delayed_queue(self, notification: Notification):
        """Queue a notification after delay."""
        await asyncio.sleep(notification.delay_seconds)
        try:
            await self._pending_queue.put(notification)
        except asyncio.QueueFull:
            logger.error(f"Notification queue full after delay, dropping notification {notification.id}")
    
    async def _process_notifications(self):
        """Background task to process notification queue."""
        while self._running:
            try:
                # Get notification from queue
                notification = await asyncio.wait_for(
                    self._pending_queue.get(),
                    timeout=1.0
                )
                
                # Process notification
                await self._send_notification(notification)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing notifications: {str(e)}")
    
    async def _send_notification(self, notification: Notification):
        """Send a notification through its channels."""
        notification.sent_at = datetime.now()
        notification.attempts += 1
        
        # Get channels to use
        if not notification.channels:
            # Use all enabled channels
            channels_to_use = [
                ch for ch_name, ch in self._channel_configs.items()
                if ch.enabled and ch.should_deliver(notification)
            ]
        else:
            # Use specified channels
            channels_to_use = [
                self._channel_configs.get(ch.value)
                for ch in notification.channels
                if ch.value in self._channel_configs
            ]
        
        # Send through each channel
        any_success = False
        results = []
        
        for channel_config in channels_to_use:
            if not channel_config:
                continue
            
            channel_name = channel_config.channel.value
            
            # Check rate limit
            if not self._check_channel_rate_limit(channel_name, channel_config):
                logger.warning(f"Rate limit exceeded for channel {channel_name}")
                continue
            
            # Get channel instance
            channel = self._channels.get(channel_name)
            if not channel:
                logger.warning(f"Channel not found: {channel_name}")
                continue
            
            try:
                # Send notification
                result = await channel.send(notification)
                results.append(result)
                
                # Update statistics
                self._update_stats(result, channel_name)
                
                if result.success:
                    any_success = True
                
            except Exception as e:
                logger.error(f"Error sending through {channel_name}: {str(e)}")
                result = NotificationResult(
                    notification_id=notification.id,
                    channel=channel_config.channel,
                    status=NotificationStatus.FAILED,
                    error_message=str(e)
                )
                results.append(result)
        
        # Update notification status
        if any_success:
            notification.status = NotificationStatus.SENT
            notification.delivered_at = datetime.now()
        else:
            notification.status = NotificationStatus.FAILED
            notification.failed_at = datetime.now()
            
            # Add to retry queue if retryable
            if notification.can_retry():
                self._retry_queue.append(notification)
    
    async def _retry_notifications(self):
        """Background task to retry failed notifications."""
        while self._running:
            try:
                await asyncio.sleep(self.retry_interval)
                
                # Process retry queue
                retry_count = len(self._retry_queue)
                if retry_count > 0:
                    logger.info(f"Retrying {retry_count} failed notifications")
                    
                    for _ in range(retry_count):
                        try:
                            notification = self._retry_queue.popleft()
                            
                            # Check if still retryable
                            if notification.can_retry():
                                notification.status = NotificationStatus.RETRYING
                                await self._queue_notification(notification)
                            
                        except IndexError:
                            break
                
            except Exception as e:
                logger.error(f"Error in retry task: {str(e)}")
    
    async def _flush_queue(self):
        """Process all remaining notifications in queue."""
        while not self._pending_queue.empty():
            try:
                notification = self._pending_queue.get_nowait()
                await self._send_notification(notification)
            except asyncio.QueueEmpty:
                break
    
    def _check_channel_rate_limit(
        self,
        channel_name: str,
        config: ChannelConfig
    ) -> bool:
        """Check if channel rate limit allows sending."""
        # No rate limit configured
        if not config.rate_limit_per_minute and not config.rate_limit_per_hour:
            return True
        
        now = datetime.now()
        
        # Check per-minute limit
        if config.rate_limit_per_minute:
            bucket_key = f"{channel_name}_minute"
            if bucket_key not in self._rate_limiters:
                self._rate_limiters[bucket_key] = RateLimitBucket(
                    window_start=now,
                    window_duration=timedelta(minutes=1),
                    max_count=config.rate_limit_per_minute
                )
            
            if not self._rate_limiters[bucket_key].increment():
                return False
        
        # Check per-hour limit
        if config.rate_limit_per_hour:
            bucket_key = f"{channel_name}_hour"
            if bucket_key not in self._rate_limiters:
                self._rate_limiters[bucket_key] = RateLimitBucket(
                    window_start=now,
                    window_duration=timedelta(hours=1),
                    max_count=config.rate_limit_per_hour
                )
            
            if not self._rate_limiters[bucket_key].increment():
                return False
        
        return True
    
    def _update_stats(self, result: NotificationResult, channel_name: str):
        """Update statistics from notification result."""
        # Global stats
        self._stats.total_sent += 1
        
        if result.success:
            self._stats.total_delivered += 1
        else:
            self._stats.total_failed += 1
            if result.error_code:
                self._stats.common_errors[result.error_code] = \
                    self._stats.common_errors.get(result.error_code, 0) + 1
        
        # Channel stats
        channel_stats = self._channel_stats[channel_name]
        channel_stats.total_sent += 1
        
        if result.success:
            channel_stats.total_delivered += 1
        else:
            channel_stats.total_failed += 1
        
        # Update channel in global stats
        if channel_name not in self._stats.by_channel:
            self._stats.by_channel[channel_name] = {
                'sent': 0,
                'delivered': 0,
                'failed': 0
            }
        
        self._stats.by_channel[channel_name]['sent'] += 1
        if result.success:
            self._stats.by_channel[channel_name]['delivered'] += 1
        else:
            self._stats.by_channel[channel_name]['failed'] += 1
        
        # Update timing stats
        if result.processing_time_ms:
            if result.processing_time_ms > self._stats.max_delivery_time_ms:
                self._stats.max_delivery_time_ms = result.processing_time_ms
        
        # Calculate error rate
        if self._stats.total_sent > 0:
            self._stats.error_rate = self._stats.total_failed / self._stats.total_sent
    
    def _create_channel_from_config(
        self,
        config: ChannelConfig
    ) -> Optional[NotificationChannelBase]:
        """Create channel instance from configuration."""
        try:
            if config.channel == NotificationChannel.EMAIL:
                return EmailNotifier(config)
            
            elif config.channel == NotificationChannel.PUSH:
                return PushNotifier(config)
            
            elif config.channel == NotificationChannel.TOAST:
                return ToastNotifier(config, self.sse_manager)
            
            elif config.channel == NotificationChannel.WEBHOOK:
                return WebhookNotifier(config)
            
            else:
                logger.warning(f"Unknown channel type: {config.channel}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating channel {config.channel}: {str(e)}")
            return None
    
    def get_stats(self, period_hours: Optional[int] = None) -> NotificationStats:
        """Get notification statistics."""
        if period_hours:
            # Calculate stats for specific period
            period_start = datetime.now() - timedelta(hours=period_hours)
            # Would filter stats by period
        
        return self._stats
    
    def get_channel_stats(self, channel_name: str) -> Optional[NotificationStats]:
        """Get statistics for a specific channel."""
        return self._channel_stats.get(channel_name)
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID."""
        return self._notification_store.get(notification_id)
    
    def get_pending_count(self) -> int:
        """Get number of pending notifications."""
        return self._pending_queue.qsize()
    
    def get_retry_count(self) -> int:
        """Get number of notifications in retry queue."""
        return len(self._retry_queue)
    
    def load_configuration(self, config_file: str):
        """Load configuration from file."""
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Load channels
        for channel_config in config.get('channels', []):
            try:
                channel_type = NotificationChannel(channel_config['type'])
                channel_cfg = ChannelConfig(
                    channel=channel_type,
                    enabled=channel_config.get('enabled', True),
                    config=channel_config.get('config', {}),
                    rate_limit_per_minute=channel_config.get('rate_limit_per_minute'),
                    rate_limit_per_hour=channel_config.get('rate_limit_per_hour'),
                    max_retries=channel_config.get('max_retries', 3),
                    retry_delay_seconds=channel_config.get('retry_delay_seconds', 60),
                    min_severity=NotificationSeverity(
                        channel_config.get('min_severity', 'info')
                    )
                )
                
                self.add_channel(channel_type.value, channel_cfg)
                
            except Exception as e:
                logger.error(f"Error loading channel config: {str(e)}")
        
        # Load rules
        if 'rules' in config:
            self.rules.load_rules_from_config(config['rules'])
        
        # Load templates
        if 'template_file' in config:
            self.templates.load_templates_from_file(config['template_file'])
        
        logger.info(f"Loaded configuration from {config_file}")
    
    def save_configuration(self, output_file: str):
        """Save current configuration to file."""
        config = {
            'channels': [
                {
                    'type': cfg.channel.value,
                    'enabled': cfg.enabled,
                    'config': cfg.config,
                    'rate_limit_per_minute': cfg.rate_limit_per_minute,
                    'rate_limit_per_hour': cfg.rate_limit_per_hour,
                    'max_retries': cfg.max_retries,
                    'retry_delay_seconds': cfg.retry_delay_seconds,
                    'min_severity': cfg.min_severity.value
                }
                for cfg in self._channel_configs.values()
            ],
            'rules': self.rules.export_rules()
        }
        
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved configuration to {output_file}")
    
    @property
    def is_running(self) -> bool:
        """Check if manager is running."""
        return self._running