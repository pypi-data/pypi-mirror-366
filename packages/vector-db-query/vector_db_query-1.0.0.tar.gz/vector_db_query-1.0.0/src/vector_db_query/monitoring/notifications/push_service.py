"""
Mobile push notification service for the monitoring dashboard.

This module provides push notification management with Firebase Cloud Messaging (FCM),
device token management, and integration with the monitoring system.
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict, field
from threading import RLock
from enum import Enum
from pathlib import Path
import uuid
import hashlib

from .channels import PushNotifier
from .models import (
    Notification, NotificationChannel, NotificationSeverity, 
    NotificationResult, ChannelConfig
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class DevicePlatform(Enum):
    """Device platform types."""
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"


class PushPriority(Enum):
    """Push notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class DeviceToken:
    """Device token for push notifications."""
    id: str
    token: str
    platform: DevicePlatform
    user_id: str
    device_name: Optional[str] = None
    device_model: Optional[str] = None
    app_version: Optional[str] = None
    is_active: bool = True
    last_seen: datetime = None
    created_at: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'token': self.token,
            'platform': self.platform.value,
            'user_id': self.user_id,
            'device_name': self.device_name,
            'device_model': self.device_model,
            'app_version': self.app_version,
            'is_active': self.is_active,
            'last_seen': self.last_seen.isoformat(),
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class PushTopic:
    """Push notification topic for group messaging."""
    id: str
    name: str
    description: str
    subscriber_count: int = 0
    severity_filter: Optional[List[str]] = None
    category_filter: Optional[List[str]] = None
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subscriber_count': self.subscriber_count,
            'severity_filter': self.severity_filter,
            'category_filter': self.category_filter,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class PushTemplate:
    """Push notification template."""
    id: str
    name: str
    title_template: str
    body_template: str
    sound: Optional[str] = "default"
    badge_increment: bool = True
    android_channel_id: Optional[str] = None
    ios_category: Optional[str] = None
    action_buttons: Optional[List[Dict[str, str]]] = None
    severity_filter: Optional[List[str]] = None
    category_filter: Optional[List[str]] = None
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.action_buttons is None:
            self.action_buttons = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'title_template': self.title_template,
            'body_template': self.body_template,
            'sound': self.sound,
            'badge_increment': self.badge_increment,
            'android_channel_id': self.android_channel_id,
            'ios_category': self.ios_category,
            'action_buttons': self.action_buttons,
            'severity_filter': self.severity_filter,
            'category_filter': self.category_filter,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class PushSettings:
    """Push notification settings."""
    enabled: bool = True
    firebase_project_id: str = ""
    default_template_id: Optional[str] = None
    default_priority: PushPriority = PushPriority.NORMAL
    rate_limit_per_hour: int = 500
    batch_size: int = 100
    token_cleanup_days: int = 90
    retry_count: int = 3
    retry_delay_seconds: int = 30
    dry_run: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'firebase_project_id': self.firebase_project_id,
            'default_template_id': self.default_template_id,
            'default_priority': self.default_priority.value,
            'rate_limit_per_hour': self.rate_limit_per_hour,
            'batch_size': self.batch_size,
            'token_cleanup_days': self.token_cleanup_days,
            'retry_count': self.retry_count,
            'retry_delay_seconds': self.retry_delay_seconds,
            'dry_run': self.dry_run
        }


class PushService:
    """
    Mobile push notification service for the monitoring dashboard.
    
    Provides device token management, topic subscriptions, template management,
    and integration with Firebase Cloud Messaging.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize push service.
        
        Args:
            storage_path: Path for push configuration persistence
        """
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # Storage
        self.storage_path = Path(storage_path) if storage_path else Path.home() / ".ansera" / "push"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.firebase_config_file = self.storage_path / "firebase_config.json"
        self.tokens_file = self.storage_path / "device_tokens.json"
        self.topics_file = self.storage_path / "push_topics.json"
        self.templates_file = self.storage_path / "push_templates.json"
        self.settings_file = self.storage_path / "push_settings.json"
        self.topic_subscriptions_file = self.storage_path / "topic_subscriptions.json"
        
        # Configuration
        self._firebase_config: Optional[Dict[str, Any]] = None
        self._settings = PushSettings()
        
        # Data stores
        self._device_tokens: Dict[str, DeviceToken] = {}
        self._topics: Dict[str, PushTopic] = {}
        self._templates: Dict[str, PushTemplate] = {}
        self._topic_subscriptions: Dict[str, Set[str]] = {}  # topic_id -> set of device_token_ids
        
        # Push notifier instance
        self._push_notifier: Optional[PushNotifier] = None
        
        # Rate limiting
        self._sent_notifications_by_hour: Dict[str, int] = {}
        
        # Load persisted data
        self._load_firebase_config()
        self._load_settings()
        self._load_device_tokens()
        self._load_topics()
        self._load_templates()
        self._load_topic_subscriptions()
        
        # Initialize default templates if none exist
        if not self._templates:
            self._create_default_templates()
        
        # Initialize default topics if none exist
        if not self._topics:
            self._create_default_topics()
        
        logger.info(f"PushService initialized with {len(self._device_tokens)} tokens, {len(self._topics)} topics, {len(self._templates)} templates")
    
    def configure_firebase(self, credentials_path: str, project_id: str) -> bool:
        """
        Configure Firebase credentials.
        
        Args:
            credentials_path: Path to Firebase service account JSON file
            project_id: Firebase project ID
            
        Returns:
            True if configured successfully
        """
        with self._lock:
            try:
                # Validate credentials file exists
                cred_path = Path(credentials_path)
                if not cred_path.exists():
                    logger.error(f"Firebase credentials file not found: {credentials_path}")
                    return False
                
                # Read and validate credentials
                with open(cred_path, 'r') as f:
                    credentials_data = json.load(f)
                
                if 'project_id' not in credentials_data:
                    logger.error("Invalid Firebase credentials: missing project_id")
                    return False
                
                # Store configuration
                self._firebase_config = {
                    'credentials_path': str(cred_path.absolute()),
                    'project_id': project_id or credentials_data['project_id']
                }
                
                # Update settings
                self._settings.firebase_project_id = self._firebase_config['project_id']
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description="Firebase configuration updated",
                    details={
                        'project_id': self._firebase_config['project_id'],
                        'credentials_path': self._firebase_config['credentials_path']
                    }
                )
                
                # Save configuration
                self._save_firebase_config()
                self._save_settings()
                
                # Reset push notifier to pick up new config
                self._push_notifier = None
                
                logger.info(f"Firebase configured for project: {self._firebase_config['project_id']}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to configure Firebase: {e}")
                return False
    
    def register_device_token(self, token: str, platform: DevicePlatform, user_id: str,
                            device_name: Optional[str] = None, device_model: Optional[str] = None,
                            app_version: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Register a device token for push notifications.
        
        Args:
            token: FCM device token
            platform: Device platform
            user_id: User identifier
            device_name: Optional device name
            device_model: Optional device model
            app_version: Optional app version
            metadata: Optional additional metadata
            
        Returns:
            Device token ID if registered successfully
        """
        with self._lock:
            try:
                # Check if token already exists
                for existing_token in self._device_tokens.values():
                    if existing_token.token == token:
                        # Update existing token
                        existing_token.last_seen = datetime.now()
                        existing_token.is_active = True
                        if device_name:
                            existing_token.device_name = device_name
                        if device_model:
                            existing_token.device_model = device_model
                        if app_version:
                            existing_token.app_version = app_version
                        if metadata:
                            existing_token.metadata.update(metadata)
                        
                        self._save_device_tokens()
                        logger.info(f"Updated existing device token for user {user_id}")
                        return existing_token.id
                
                # Create new device token
                device_token = DeviceToken(
                    id=str(uuid.uuid4()),
                    token=token,
                    platform=platform,
                    user_id=user_id,
                    device_name=device_name,
                    device_model=device_model,
                    app_version=app_version,
                    metadata=metadata or {}
                )
                
                self._device_tokens[device_token.id] = device_token
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.CREATE,
                    description=f"Device token registered for user {user_id}",
                    details={
                        'token_id': device_token.id,
                        'platform': platform.value,
                        'user_id': user_id,
                        'device_name': device_name
                    }
                )
                
                # Save tokens
                self._save_device_tokens()
                
                logger.info(f"Registered new device token for user {user_id}")
                return device_token.id
                
            except Exception as e:
                logger.error(f"Failed to register device token: {e}")
                return None
    
    def unregister_device_token(self, token_id: str) -> bool:
        """
        Unregister a device token.
        
        Args:
            token_id: Device token ID
            
        Returns:
            True if unregistered successfully
        """
        with self._lock:
            try:
                if token_id not in self._device_tokens:
                    logger.warning(f"Device token not found: {token_id}")
                    return False
                
                token = self._device_tokens[token_id]
                token.is_active = False
                
                # Remove from topic subscriptions
                for topic_id, subscribers in self._topic_subscriptions.items():
                    if token_id in subscribers:
                        subscribers.remove(token_id)
                        topic = self._topics.get(topic_id)
                        if topic:
                            topic.subscriber_count = len(subscribers)
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description=f"Device token unregistered for user {token.user_id}",
                    details={
                        'token_id': token_id,
                        'platform': token.platform.value,
                        'user_id': token.user_id
                    }
                )
                
                # Save data
                self._save_device_tokens()
                self._save_topic_subscriptions()
                self._save_topics()
                
                logger.info(f"Unregistered device token for user {token.user_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to unregister device token: {e}")
                return False
    
    def subscribe_to_topic(self, token_id: str, topic_id: str) -> bool:
        """
        Subscribe a device to a topic.
        
        Args:
            token_id: Device token ID
            topic_id: Topic ID
            
        Returns:
            True if subscribed successfully
        """
        with self._lock:
            try:
                if token_id not in self._device_tokens:
                    logger.warning(f"Device token not found: {token_id}")
                    return False
                
                if topic_id not in self._topics:
                    logger.warning(f"Topic not found: {topic_id}")
                    return False
                
                # Add subscription
                if topic_id not in self._topic_subscriptions:
                    self._topic_subscriptions[topic_id] = set()
                
                self._topic_subscriptions[topic_id].add(token_id)
                
                # Update subscriber count
                topic = self._topics[topic_id]
                topic.subscriber_count = len(self._topic_subscriptions[topic_id])
                
                # Save data
                self._save_topic_subscriptions()
                self._save_topics()
                
                logger.info(f"Device {token_id} subscribed to topic {topic.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to subscribe to topic: {e}")
                return False
    
    def unsubscribe_from_topic(self, token_id: str, topic_id: str) -> bool:
        """
        Unsubscribe a device from a topic.
        
        Args:
            token_id: Device token ID
            topic_id: Topic ID
            
        Returns:
            True if unsubscribed successfully
        """
        with self._lock:
            try:
                if topic_id in self._topic_subscriptions and token_id in self._topic_subscriptions[topic_id]:
                    self._topic_subscriptions[topic_id].remove(token_id)
                    
                    # Update subscriber count
                    topic = self._topics.get(topic_id)
                    if topic:
                        topic.subscriber_count = len(self._topic_subscriptions[topic_id])
                    
                    # Save data
                    self._save_topic_subscriptions()
                    self._save_topics()
                    
                    logger.info(f"Device {token_id} unsubscribed from topic {topic.name if topic else topic_id}")
                    return True
                
                return False
                
            except Exception as e:
                logger.error(f"Failed to unsubscribe from topic: {e}")
                return False
    
    def add_topic(self, topic: PushTopic) -> bool:
        """
        Add a push notification topic.
        
        Args:
            topic: Push topic to add
            
        Returns:
            True if added successfully
        """
        with self._lock:
            try:
                self._topics[topic.id] = topic
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.CREATE,
                    description=f"Push topic added: {topic.name}",
                    details={
                        'topic_id': topic.id,
                        'topic_name': topic.name
                    }
                )
                
                # Save topics
                self._save_topics()
                
                logger.info(f"Push topic added: {topic.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add push topic: {e}")
                return False
    
    def add_template(self, template: PushTemplate) -> bool:
        """
        Add push notification template.
        
        Args:
            template: Push template to add
            
        Returns:
            True if added successfully
        """
        with self._lock:
            try:
                self._templates[template.id] = template
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.CREATE,
                    description=f"Push template added: {template.name}",
                    details={
                        'template_id': template.id,
                        'template_name': template.name
                    }
                )
                
                # Save templates
                self._save_templates()
                
                logger.info(f"Push template added: {template.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add push template: {e}")
                return False
    
    async def send_notification(self, title: str, message: str,
                              severity: NotificationSeverity = NotificationSeverity.INFO,
                              category: str = "general",
                              source: str = "system",
                              template_id: Optional[str] = None,
                              recipient_tokens: Optional[List[str]] = None,
                              topic_id: Optional[str] = None,
                              user_ids: Optional[List[str]] = None,
                              priority: Optional[PushPriority] = None,
                              data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send push notification.
        
        Args:
            title: Notification title
            message: Notification message
            severity: Notification severity
            category: Notification category
            source: Notification source
            template_id: Optional template ID
            recipient_tokens: Optional specific device token IDs
            topic_id: Optional topic ID for topic messaging
            user_ids: Optional user IDs to send to
            priority: Optional notification priority
            data: Optional additional data
            
        Returns:
            True if sent successfully
        """
        with self._lock:
            try:
                # Check if push service is enabled
                if not self._settings.enabled:
                    logger.info("Push service is disabled")
                    return False
                
                # Check if Firebase is configured
                if not self._firebase_config:
                    logger.warning("Firebase not configured")
                    return False
                
                # Check rate limiting
                current_hour = datetime.now().strftime('%Y-%m-%d-%H')
                if current_hour in self._sent_notifications_by_hour:
                    if self._sent_notifications_by_hour[current_hour] >= self._settings.rate_limit_per_hour:
                        logger.warning("Push notification rate limit exceeded")
                        return False
                
                # Determine recipients
                device_tokens = []
                
                if recipient_tokens:
                    # Use specific tokens
                    for token_id in recipient_tokens:
                        if token_id in self._device_tokens and self._device_tokens[token_id].is_active:
                            device_tokens.append(self._device_tokens[token_id].token)
                
                elif topic_id:
                    # Use topic subscribers
                    if topic_id in self._topic_subscriptions:
                        for token_id in self._topic_subscriptions[topic_id]:
                            if token_id in self._device_tokens and self._device_tokens[token_id].is_active:
                                device_tokens.append(self._device_tokens[token_id].token)
                
                elif user_ids:
                    # Find tokens for users
                    for token in self._device_tokens.values():
                        if token.user_id in user_ids and token.is_active:
                            device_tokens.append(token.token)
                
                if not device_tokens:
                    logger.warning("No device tokens found for push notification")
                    return False
                
                # Create notification
                notification = Notification(
                    id=str(uuid.uuid4()),
                    title=title,
                    message=message,
                    severity=severity,
                    source=source,
                    event_type=category,
                    recipients=device_tokens,
                    priority=priority or self._settings.default_priority,
                    data=data or {},
                    template_name=template_id,
                    created_at=datetime.now()
                )
                
                # Get push notifier
                push_notifier = await self._get_push_notifier()
                if not push_notifier:
                    logger.error("Failed to get push notifier")
                    return False
                
                # Send notification
                result = await push_notifier.send(notification)
                
                # Track sent notification for rate limiting
                if current_hour not in self._sent_notifications_by_hour:
                    self._sent_notifications_by_hour[current_hour] = 0
                self._sent_notifications_by_hour[current_hour] += len(device_tokens)
                
                # Clean up old hour counters
                self._cleanup_rate_limit_counters()
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.NOTIFICATION,
                    change_type=ChangeType.CREATE,
                    description=f"Push notification sent: {title}",
                    details={
                        'notification_id': notification.id,
                        'title': title,
                        'severity': severity.value,
                        'recipient_count': len(device_tokens),
                        'success': result.status.value == 'sent'
                    }
                )
                
                logger.info(f"Push notification sent: {title} (status: {result.status.value})")
                return result.status.value == 'sent'
                
            except Exception as e:
                logger.error(f"Failed to send push notification: {e}")
                return False
    
    async def test_push_notification(self, token_id: str) -> Dict[str, Any]:
        """
        Test push notification to specific device.
        
        Args:
            token_id: Device token ID
            
        Returns:
            Test result with status and details
        """
        try:
            if token_id not in self._device_tokens:
                return {
                    'success': False,
                    'error': 'Device token not found'
                }
            
            device_token = self._device_tokens[token_id]
            
            # Send test notification
            success = await self.send_notification(
                title="Test Notification",
                message="This is a test push notification from Ansera monitoring.",
                severity=NotificationSeverity.INFO,
                category="test",
                source="push_service_test",
                recipient_tokens=[token_id],
                data={
                    'test': True,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return {
                'success': success,
                'device_name': device_token.device_name,
                'platform': device_token.platform.value
            }
            
        except Exception as e:
            logger.error(f"Push notification test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_settings(self, settings: PushSettings) -> bool:
        """
        Update push settings.
        
        Args:
            settings: New push settings
            
        Returns:
            True if updated successfully
        """
        with self._lock:
            try:
                old_settings = self._settings.to_dict()
                self._settings = settings
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description="Push settings updated",
                    details={
                        'old_settings': old_settings,
                        'new_settings': settings.to_dict()
                    }
                )
                
                # Save settings
                self._save_settings()
                
                logger.info("Push settings updated")
                return True
                
            except Exception as e:
                logger.error(f"Failed to update push settings: {e}")
                return False
    
    def cleanup_inactive_tokens(self, days: Optional[int] = None) -> int:
        """
        Clean up inactive device tokens.
        
        Args:
            days: Days of inactivity (uses settings default if not specified)
            
        Returns:
            Number of tokens cleaned up
        """
        with self._lock:
            try:
                days = days or self._settings.token_cleanup_days
                cutoff_date = datetime.now() - timedelta(days=days)
                
                tokens_to_remove = []
                for token_id, token in self._device_tokens.items():
                    if not token.is_active or token.last_seen < cutoff_date:
                        tokens_to_remove.append(token_id)
                
                # Remove tokens
                for token_id in tokens_to_remove:
                    del self._device_tokens[token_id]
                    
                    # Remove from subscriptions
                    for subscribers in self._topic_subscriptions.values():
                        if token_id in subscribers:
                            subscribers.remove(token_id)
                
                # Update topic subscriber counts
                for topic_id, subscribers in self._topic_subscriptions.items():
                    topic = self._topics.get(topic_id)
                    if topic:
                        topic.subscriber_count = len(subscribers)
                
                # Save data
                self._save_device_tokens()
                self._save_topic_subscriptions()
                self._save_topics()
                
                logger.info(f"Cleaned up {len(tokens_to_remove)} inactive device tokens")
                return len(tokens_to_remove)
                
            except Exception as e:
                logger.error(f"Failed to cleanup inactive tokens: {e}")
                return 0
    
    def get_firebase_config(self) -> Optional[Dict[str, Any]]:
        """Get current Firebase configuration."""
        with self._lock:
            return self._firebase_config.copy() if self._firebase_config else None
    
    def get_settings(self) -> PushSettings:
        """Get current push settings."""
        with self._lock:
            return self._settings
    
    def get_device_tokens(self, user_id: Optional[str] = None, platform: Optional[DevicePlatform] = None,
                         active_only: bool = True) -> Dict[str, DeviceToken]:
        """Get device tokens with optional filtering."""
        with self._lock:
            tokens = {}
            for token_id, token in self._device_tokens.items():
                if active_only and not token.is_active:
                    continue
                if user_id and token.user_id != user_id:
                    continue
                if platform and token.platform != platform:
                    continue
                tokens[token_id] = token
            return tokens
    
    def get_topics(self) -> Dict[str, PushTopic]:
        """Get all push topics."""
        with self._lock:
            return self._topics.copy()
    
    def get_templates(self) -> Dict[str, PushTemplate]:
        """Get all push templates."""
        with self._lock:
            return self._templates.copy()
    
    def get_topic_subscribers(self, topic_id: str) -> List[str]:
        """Get device token IDs subscribed to a topic."""
        with self._lock:
            return list(self._topic_subscriptions.get(topic_id, set()))
    
    def get_user_subscriptions(self, user_id: str) -> List[str]:
        """Get topic IDs a user is subscribed to."""
        with self._lock:
            user_tokens = [tid for tid, token in self._device_tokens.items() 
                          if token.user_id == user_id and token.is_active]
            
            subscribed_topics = []
            for topic_id, subscribers in self._topic_subscriptions.items():
                if any(token_id in subscribers for token_id in user_tokens):
                    subscribed_topics.append(topic_id)
            
            return subscribed_topics
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get push service statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            current_hour = datetime.now().strftime('%Y-%m-%d-%H')
            notifications_this_hour = self._sent_notifications_by_hour.get(current_hour, 0)
            
            # Count by platform
            platform_counts = {}
            active_token_count = 0
            for token in self._device_tokens.values():
                if token.is_active:
                    active_token_count += 1
                    platform = token.platform.value
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            # Count users with tokens
            unique_users = len(set(token.user_id for token in self._device_tokens.values() if token.is_active))
            
            return {
                'firebase_configured': self._firebase_config is not None,
                'service_enabled': self._settings.enabled,
                'total_device_tokens': len(self._device_tokens),
                'active_device_tokens': active_token_count,
                'unique_users': unique_users,
                'topics_count': len(self._topics),
                'templates_count': len(self._templates),
                'notifications_sent_this_hour': notifications_this_hour,
                'rate_limit_per_hour': self._settings.rate_limit_per_hour,
                'rate_limit_remaining': max(0, self._settings.rate_limit_per_hour - notifications_this_hour),
                'platform_breakdown': platform_counts
            }
    
    async def _get_push_notifier(self) -> Optional[PushNotifier]:
        """Get configured push notifier."""
        if not self._push_notifier and self._firebase_config:
            try:
                # Create channel config
                channel_config = ChannelConfig(
                    channel=NotificationChannel.PUSH,
                    config={
                        'credentials_path': self._firebase_config['credentials_path']
                    }
                )
                
                # Create and initialize push notifier
                self._push_notifier = PushNotifier(channel_config)
                await self._push_notifier.initialize()
                
            except Exception as e:
                logger.error(f"Failed to create push notifier: {e}")
                return None
        
        return self._push_notifier
    
    def _create_default_templates(self):
        """Create default push templates."""
        templates = [
            PushTemplate(
                id="default_info",
                name="Default Info",
                title_template="{{title}}",
                body_template="{{message}}",
                severity_filter=["info"]
            ),
            PushTemplate(
                id="default_warning",
                name="Default Warning",
                title_template="⚠️ {{title}}",
                body_template="{{message}}",
                sound="warning.wav",
                severity_filter=["warning"]
            ),
            PushTemplate(
                id="default_error",
                name="Default Error",
                title_template="🚨 {{title}}",
                body_template="{{message}}",
                sound="alert.wav",
                android_channel_id="high_priority",
                severity_filter=["error", "critical"]
            ),
            PushTemplate(
                id="default_actionable",
                name="Default Actionable",
                title_template="{{title}}",
                body_template="{{message}}",
                action_buttons=[
                    {"id": "view", "title": "View Details"},
                    {"id": "dismiss", "title": "Dismiss"}
                ]
            )
        ]
        
        for template in templates:
            self._templates[template.id] = template
        
        self._save_templates()
        logger.info("Created default push templates")
    
    def _create_default_topics(self):
        """Create default push topics."""
        topics = [
            PushTopic(
                id="all_users",
                name="All Users",
                description="All registered users"
            ),
            PushTopic(
                id="critical_alerts",
                name="Critical Alerts",
                description="Critical system alerts only",
                severity_filter=["critical", "error"]
            ),
            PushTopic(
                id="maintenance",
                name="Maintenance Updates",
                description="System maintenance notifications",
                category_filter=["maintenance", "system"]
            ),
            PushTopic(
                id="daily_summary",
                name="Daily Summary",
                description="Daily system summary notifications",
                category_filter=["summary", "report"]
            )
        ]
        
        for topic in topics:
            self._topics[topic.id] = topic
        
        self._save_topics()
        logger.info("Created default push topics")
    
    def _cleanup_rate_limit_counters(self):
        """Clean up old rate limit counters."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=25)  # Keep 25 hours of data
        
        to_remove = []
        for hour_key in self._sent_notifications_by_hour:
            hour_time = datetime.strptime(hour_key, '%Y-%m-%d-%H')
            if hour_time < cutoff_time:
                to_remove.append(hour_key)
        
        for key in to_remove:
            del self._sent_notifications_by_hour[key]
    
    # Storage methods
    def _save_firebase_config(self):
        """Save Firebase configuration to storage."""
        try:
            if self._firebase_config:
                with open(self.firebase_config_file, 'w') as f:
                    json.dump(self._firebase_config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save Firebase config: {e}")
    
    def _load_firebase_config(self):
        """Load Firebase configuration from storage."""
        try:
            if self.firebase_config_file.exists():
                with open(self.firebase_config_file, 'r') as f:
                    self._firebase_config = json.load(f)
                logger.info("Loaded Firebase configuration")
        except Exception as e:
            logger.error(f"Failed to load Firebase config: {e}")
    
    def _save_settings(self):
        """Save push settings to storage."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self._settings.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save push settings: {e}")
    
    def _load_settings(self):
        """Load push settings from storage."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                
                if 'default_priority' in data:
                    data['default_priority'] = PushPriority(data['default_priority'])
                
                self._settings = PushSettings(**data)
                logger.info("Loaded push settings")
        except Exception as e:
            logger.error(f"Failed to load push settings: {e}")
    
    def _save_device_tokens(self):
        """Save device tokens to storage."""
        try:
            data = {tid: token.to_dict() for tid, token in self._device_tokens.items()}
            with open(self.tokens_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save device tokens: {e}")
    
    def _load_device_tokens(self):
        """Load device tokens from storage."""
        try:
            if self.tokens_file.exists():
                with open(self.tokens_file, 'r') as f:
                    data = json.load(f)
                
                for tid, token_data in data.items():
                    token_data['platform'] = DevicePlatform(token_data['platform'])
                    token_data['last_seen'] = datetime.fromisoformat(token_data['last_seen'])
                    token_data['created_at'] = datetime.fromisoformat(token_data['created_at'])
                    token = DeviceToken(**token_data)
                    self._device_tokens[tid] = token
                
                logger.info(f"Loaded {len(self._device_tokens)} device tokens")
        except Exception as e:
            logger.error(f"Failed to load device tokens: {e}")
    
    def _save_topics(self):
        """Save topics to storage."""
        try:
            data = {tid: topic.to_dict() for tid, topic in self._topics.items()}
            with open(self.topics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save topics: {e}")
    
    def _load_topics(self):
        """Load topics from storage."""
        try:
            if self.topics_file.exists():
                with open(self.topics_file, 'r') as f:
                    data = json.load(f)
                
                for tid, topic_data in data.items():
                    topic_data['created_at'] = datetime.fromisoformat(topic_data['created_at'])
                    topic = PushTopic(**topic_data)
                    self._topics[tid] = topic
                
                logger.info(f"Loaded {len(self._topics)} push topics")
        except Exception as e:
            logger.error(f"Failed to load topics: {e}")
    
    def _save_templates(self):
        """Save templates to storage."""
        try:
            data = {tid: template.to_dict() for tid, template in self._templates.items()}
            with open(self.templates_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save templates: {e}")
    
    def _load_templates(self):
        """Load templates from storage."""
        try:
            if self.templates_file.exists():
                with open(self.templates_file, 'r') as f:
                    data = json.load(f)
                
                for tid, template_data in data.items():
                    template_data['created_at'] = datetime.fromisoformat(template_data['created_at'])
                    template = PushTemplate(**template_data)
                    self._templates[tid] = template
                
                logger.info(f"Loaded {len(self._templates)} push templates")
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
    
    def _save_topic_subscriptions(self):
        """Save topic subscriptions to storage."""
        try:
            # Convert sets to lists for JSON serialization
            data = {topic_id: list(subscribers) for topic_id, subscribers in self._topic_subscriptions.items()}
            with open(self.topic_subscriptions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save topic subscriptions: {e}")
    
    def _load_topic_subscriptions(self):
        """Load topic subscriptions from storage."""
        try:
            if self.topic_subscriptions_file.exists():
                with open(self.topic_subscriptions_file, 'r') as f:
                    data = json.load(f)
                
                # Convert lists back to sets
                self._topic_subscriptions = {topic_id: set(subscribers) for topic_id, subscribers in data.items()}
                
                logger.info(f"Loaded subscriptions for {len(self._topic_subscriptions)} topics")
        except Exception as e:
            logger.error(f"Failed to load topic subscriptions: {e}")


# Singleton instance
_push_service: Optional[PushService] = None
_service_lock = RLock()


def get_push_service(storage_path: Optional[str] = None) -> PushService:
    """
    Get singleton push service instance.
    
    Args:
        storage_path: Storage path (only used on first call)
        
    Returns:
        PushService instance
    """
    global _push_service
    
    with _service_lock:
        if _push_service is None:
            _push_service = PushService(storage_path)
        
        return _push_service


def reset_push_service():
    """Reset the singleton push service (mainly for testing)."""
    global _push_service
    
    with _service_lock:
        _push_service = None


# Convenience functions
async def send_push_notification(title: str, message: str,
                               severity: NotificationSeverity = NotificationSeverity.INFO,
                               **kwargs) -> bool:
    """Send push notification using default service."""
    push_service = get_push_service()
    return await push_service.send_notification(title, message, severity, **kwargs)


async def send_push_error(title: str, message: str, **kwargs) -> bool:
    """Send error push notification."""
    return await send_push_notification(title, message, NotificationSeverity.ERROR, **kwargs)


async def send_push_warning(title: str, message: str, **kwargs) -> bool:
    """Send warning push notification."""
    return await send_push_notification(title, message, NotificationSeverity.WARNING, **kwargs)


async def send_push_info(title: str, message: str, **kwargs) -> bool:
    """Send info push notification."""
    return await send_push_notification(title, message, NotificationSeverity.INFO, **kwargs)