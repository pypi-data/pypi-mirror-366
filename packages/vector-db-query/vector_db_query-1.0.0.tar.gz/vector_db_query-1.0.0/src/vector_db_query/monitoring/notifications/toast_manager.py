"""
Toast notification manager for the monitoring dashboard.

This module provides toast notification management with support for
different notification types, persistence, and integration with Streamlit.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from threading import RLock
from enum import Enum
import uuid
from pathlib import Path

from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class ToastType(Enum):
    """Types of toast notifications."""
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ToastPosition(Enum):
    """Position of toast notifications."""
    TOP_RIGHT = "top-right"
    TOP_LEFT = "top-left"
    BOTTOM_RIGHT = "bottom-right"
    BOTTOM_LEFT = "bottom-left"
    CENTER = "center"


@dataclass
class ToastNotification:
    """Represents a toast notification."""
    id: str
    title: str
    message: str
    toast_type: ToastType
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_persistent: bool = False
    is_dismissible: bool = True
    action_text: Optional[str] = None
    action_callback: Optional[str] = None
    source: str = "system"
    category: str = "general"
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'toast_type': self.toast_type.value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_persistent': self.is_persistent,
            'is_dismissible': self.is_dismissible,
            'action_text': self.action_text,
            'action_callback': self.action_callback,
            'source': self.source,
            'category': self.category,
            'metadata': self.metadata
        }
    
    def is_expired(self) -> bool:
        """Check if notification has expired."""
        if self.is_persistent or not self.expires_at:
            return False
        return datetime.now() > self.expires_at


@dataclass
class ToastSettings:
    """Toast notification settings."""
    position: ToastPosition = ToastPosition.TOP_RIGHT
    default_duration: int = 5  # seconds
    max_notifications: int = 10
    auto_dismiss: bool = True
    show_timestamps: bool = True
    enable_sound: bool = False
    enable_animations: bool = True
    group_similar: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'position': self.position.value,
            'default_duration': self.default_duration,
            'max_notifications': self.max_notifications,
            'auto_dismiss': self.auto_dismiss,
            'show_timestamps': self.show_timestamps,
            'enable_sound': self.enable_sound,
            'enable_animations': self.enable_animations,
            'group_similar': self.group_similar
        }


class ToastManager:
    """
    Manages toast notifications for the dashboard.
    
    Provides notification creation, management, persistence,
    and integration with the existing notification system.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize toast manager.
        
        Args:
            storage_path: Path for notification persistence
        """
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # Storage
        self.storage_path = Path(storage_path) if storage_path else Path.home() / ".ansera" / "notifications"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.notifications_file = self.storage_path / "toast_notifications.json"
        self.settings_file = self.storage_path / "toast_settings.json"
        
        # Active notifications
        self._notifications: Dict[str, ToastNotification] = {}
        self._dismissed_notifications: Dict[str, ToastNotification] = {}
        
        # Settings
        self._settings = ToastSettings()
        
        # Action callbacks
        self._action_callbacks: Dict[str, Callable] = {}
        
        # Load persisted data
        self._load_notifications()
        self._load_settings()
        
        # Clean up expired notifications
        self._cleanup_expired()
        
        logger.info(f"ToastManager initialized with {len(self._notifications)} active notifications")
    
    def create_notification(self, title: str, message: str, toast_type: ToastType = ToastType.INFO,
                          duration: Optional[int] = None, is_persistent: bool = False,
                          action_text: Optional[str] = None, action_callback: Optional[str] = None,
                          source: str = "system", category: str = "general",
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new toast notification.
        
        Args:
            title: Notification title
            message: Notification message
            toast_type: Type of notification
            duration: Duration in seconds (None for default)
            is_persistent: Whether notification persists until dismissed
            action_text: Text for action button
            action_callback: Callback ID for action
            source: Source of notification
            category: Category for grouping
            metadata: Additional metadata
            
        Returns:
            Notification ID
        """
        with self._lock:
            try:
                # Generate unique ID
                notification_id = str(uuid.uuid4())
                
                # Calculate expiration
                expires_at = None
                if not is_persistent:
                    duration = duration or self._settings.default_duration
                    expires_at = datetime.now() + timedelta(seconds=duration)
                
                # Check for similar notifications if grouping is enabled
                if self._settings.group_similar:
                    similar_id = self._find_similar_notification(title, message, toast_type)
                    if similar_id:
                        # Update existing notification instead of creating new one
                        existing = self._notifications[similar_id]
                        existing.message = message
                        existing.created_at = datetime.now()
                        existing.expires_at = expires_at
                        
                        self._save_notifications()
                        return similar_id
                
                # Create notification
                notification = ToastNotification(
                    id=notification_id,
                    title=title,
                    message=message,
                    toast_type=toast_type,
                    created_at=datetime.now(),
                    expires_at=expires_at,
                    is_persistent=is_persistent,
                    action_text=action_text,
                    action_callback=action_callback,
                    source=source,
                    category=category,
                    metadata=metadata or {}
                )
                
                # Add to active notifications
                self._notifications[notification_id] = notification
                
                # Enforce max notifications limit
                self._enforce_max_notifications()
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.NOTIFICATION,
                    change_type=ChangeType.CREATE,
                    description=f"Toast notification created: {title}",
                    details={
                        'notification_id': notification_id,
                        'title': title,
                        'toast_type': toast_type.value,
                        'source': source,
                        'category': category,
                        'is_persistent': is_persistent
                    }
                )
                
                # Save notifications
                self._save_notifications()
                
                logger.info(f"Created toast notification: {title} ({toast_type.value})")
                return notification_id
                
            except Exception as e:
                logger.error(f"Failed to create toast notification: {e}")
                return ""
    
    def dismiss_notification(self, notification_id: str) -> bool:
        """
        Dismiss a notification.
        
        Args:
            notification_id: ID of notification to dismiss
            
        Returns:
            True if dismissed successfully
        """
        with self._lock:
            try:
                if notification_id not in self._notifications:
                    logger.warning(f"Notification not found: {notification_id}")
                    return False
                
                notification = self._notifications.pop(notification_id)
                
                # Move to dismissed notifications
                self._dismissed_notifications[notification_id] = notification
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.NOTIFICATION,
                    change_type=ChangeType.DELETE,
                    description=f"Toast notification dismissed: {notification.title}",
                    details={
                        'notification_id': notification_id,
                        'title': notification.title,
                        'toast_type': notification.toast_type.value
                    }
                )
                
                # Save state
                self._save_notifications()
                
                logger.info(f"Dismissed notification: {notification.title}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to dismiss notification {notification_id}: {e}")
                return False
    
    def dismiss_all(self, category: Optional[str] = None) -> int:
        """
        Dismiss all notifications or all in a category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            Number of notifications dismissed
        """
        with self._lock:
            try:
                notifications_to_dismiss = []
                
                for notification_id, notification in self._notifications.items():
                    if category is None or notification.category == category:
                        if notification.is_dismissible:
                            notifications_to_dismiss.append(notification_id)
                
                dismissed_count = 0
                for notification_id in notifications_to_dismiss:
                    if self.dismiss_notification(notification_id):
                        dismissed_count += 1
                
                logger.info(f"Dismissed {dismissed_count} notifications" + 
                           (f" in category '{category}'" if category else ""))
                
                return dismissed_count
                
            except Exception as e:
                logger.error(f"Failed to dismiss notifications: {e}")
                return 0
    
    def get_active_notifications(self, category: Optional[str] = None) -> List[ToastNotification]:
        """
        Get list of active notifications.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of active notifications
        """
        with self._lock:
            # Clean up expired notifications first
            self._cleanup_expired()
            
            notifications = list(self._notifications.values())
            
            # Filter by category if specified
            if category:
                notifications = [n for n in notifications if n.category == category]
            
            # Sort by creation time (newest first)
            notifications.sort(key=lambda x: x.created_at, reverse=True)
            
            return notifications
    
    def get_notification(self, notification_id: str) -> Optional[ToastNotification]:
        """
        Get a specific notification.
        
        Args:
            notification_id: ID of notification
            
        Returns:
            Notification if found, None otherwise
        """
        with self._lock:
            return self._notifications.get(notification_id)
    
    def update_settings(self, settings: ToastSettings) -> bool:
        """
        Update toast settings.
        
        Args:
            settings: New settings
            
        Returns:
            True if updated successfully
        """
        with self._lock:
            try:
                old_settings = self._settings
                self._settings = settings
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description="Toast notification settings updated",
                    details={
                        'old_settings': old_settings.to_dict(),
                        'new_settings': settings.to_dict()
                    }
                )
                
                # Save settings
                self._save_settings()
                
                logger.info("Toast notification settings updated")
                return True
                
            except Exception as e:
                logger.error(f"Failed to update toast settings: {e}")
                return False
    
    def get_settings(self) -> ToastSettings:
        """Get current toast settings."""
        with self._lock:
            return self._settings
    
    def register_action_callback(self, callback_id: str, callback: Callable) -> bool:
        """
        Register an action callback.
        
        Args:
            callback_id: Unique callback ID
            callback: Callback function
            
        Returns:
            True if registered successfully
        """
        with self._lock:
            try:
                self._action_callbacks[callback_id] = callback
                logger.info(f"Registered action callback: {callback_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to register callback {callback_id}: {e}")
                return False
    
    def execute_action(self, notification_id: str) -> bool:
        """
        Execute action for a notification.
        
        Args:
            notification_id: ID of notification
            
        Returns:
            True if action executed successfully
        """
        with self._lock:
            try:
                notification = self._notifications.get(notification_id)
                if not notification or not notification.action_callback:
                    return False
                
                callback = self._action_callbacks.get(notification.action_callback)
                if not callback:
                    logger.warning(f"Action callback not found: {notification.action_callback}")
                    return False
                
                # Execute callback
                callback(notification)
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.NOTIFICATION,
                    change_type=ChangeType.UPDATE,
                    description=f"Toast notification action executed: {notification.title}",
                    details={
                        'notification_id': notification_id,
                        'action_callback': notification.action_callback
                    }
                )
                
                logger.info(f"Executed action for notification: {notification.title}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to execute action for notification {notification_id}: {e}")
                return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get notification statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            # Clean up expired first
            self._cleanup_expired()
            
            # Count by type
            type_counts = {}
            for notification in self._notifications.values():
                toast_type = notification.toast_type.value
                type_counts[toast_type] = type_counts.get(toast_type, 0) + 1
            
            # Count by category
            category_counts = {}
            for notification in self._notifications.values():
                category = notification.category
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count by source
            source_counts = {}
            for notification in self._notifications.values():
                source = notification.source
                source_counts[source] = source_counts.get(source, 0) + 1
            
            return {
                'active_notifications': len(self._notifications),
                'dismissed_notifications': len(self._dismissed_notifications),
                'by_type': type_counts,
                'by_category': category_counts,
                'by_source': source_counts,
                'persistent_count': len([n for n in self._notifications.values() if n.is_persistent]),
                'settings': self._settings.to_dict()
            }
    
    def clear_dismissed(self, older_than_days: int = 7) -> int:
        """
        Clear old dismissed notifications.
        
        Args:
            older_than_days: Clear notifications older than this many days
            
        Returns:
            Number of notifications cleared
        """
        with self._lock:
            try:
                cutoff_date = datetime.now() - timedelta(days=older_than_days)
                
                # Find old dismissed notifications
                to_remove = []
                for notification_id, notification in self._dismissed_notifications.items():
                    if notification.created_at < cutoff_date:
                        to_remove.append(notification_id)
                
                # Remove them
                for notification_id in to_remove:
                    del self._dismissed_notifications[notification_id]
                
                # Save state
                self._save_notifications()
                
                logger.info(f"Cleared {len(to_remove)} old dismissed notifications")
                return len(to_remove)
                
            except Exception as e:
                logger.error(f"Failed to clear dismissed notifications: {e}")
                return 0
    
    def _find_similar_notification(self, title: str, message: str, toast_type: ToastType) -> Optional[str]:
        """Find similar notification for grouping."""
        for notification_id, notification in self._notifications.items():
            if (notification.title == title and 
                notification.toast_type == toast_type and
                notification.category == "general"):  # Only group general notifications
                return notification_id
        return None
    
    def _enforce_max_notifications(self):
        """Enforce maximum number of notifications."""
        if len(self._notifications) <= self._settings.max_notifications:
            return
        
        # Sort by creation time and dismiss oldest non-persistent notifications
        notifications = sorted(
            self._notifications.values(),
            key=lambda x: x.created_at
        )
        
        to_dismiss = []
        for notification in notifications:
            if len(self._notifications) - len(to_dismiss) <= self._settings.max_notifications:
                break
            
            if not notification.is_persistent and notification.is_dismissible:
                to_dismiss.append(notification.id)
        
        for notification_id in to_dismiss:
            self.dismiss_notification(notification_id)
    
    def _cleanup_expired(self):
        """Clean up expired notifications."""
        if not self._settings.auto_dismiss:
            return
        
        expired_ids = []
        for notification_id, notification in self._notifications.items():
            if notification.is_expired():
                expired_ids.append(notification_id)
        
        for notification_id in expired_ids:
            self.dismiss_notification(notification_id)
    
    def _save_notifications(self):
        """Save notifications to storage."""
        try:
            data = {
                'active': {nid: n.to_dict() for nid, n in self._notifications.items()},
                'dismissed': {nid: n.to_dict() for nid, n in self._dismissed_notifications.items()},
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.notifications_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save notifications: {e}")
    
    def _load_notifications(self):
        """Load notifications from storage."""
        try:
            if not self.notifications_file.exists():
                return
            
            with open(self.notifications_file, 'r') as f:
                data = json.load(f)
            
            # Load active notifications
            for nid, ndata in data.get('active', {}).items():
                try:
                    # Convert datetime strings back to datetime objects
                    ndata['created_at'] = datetime.fromisoformat(ndata['created_at'])
                    if ndata['expires_at']:
                        ndata['expires_at'] = datetime.fromisoformat(ndata['expires_at'])
                    ndata['toast_type'] = ToastType(ndata['toast_type'])
                    
                    notification = ToastNotification(**ndata)
                    self._notifications[nid] = notification
                    
                except Exception as e:
                    logger.warning(f"Failed to load notification {nid}: {e}")
            
            # Load dismissed notifications (recent ones only)
            cutoff_date = datetime.now() - timedelta(days=7)
            for nid, ndata in data.get('dismissed', {}).items():
                try:
                    ndata['created_at'] = datetime.fromisoformat(ndata['created_at'])
                    if ndata['expires_at']:
                        ndata['expires_at'] = datetime.fromisoformat(ndata['expires_at'])
                    ndata['toast_type'] = ToastType(ndata['toast_type'])
                    
                    notification = ToastNotification(**ndata)
                    
                    # Only keep recent dismissed notifications
                    if notification.created_at > cutoff_date:
                        self._dismissed_notifications[nid] = notification
                        
                except Exception as e:
                    logger.warning(f"Failed to load dismissed notification {nid}: {e}")
            
            logger.info(f"Loaded {len(self._notifications)} active and {len(self._dismissed_notifications)} dismissed notifications")
            
        except Exception as e:
            logger.error(f"Failed to load notifications: {e}")
    
    def _save_settings(self):
        """Save settings to storage."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self._settings.to_dict(), f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save toast settings: {e}")
    
    def _load_settings(self):
        """Load settings from storage."""
        try:
            if not self.settings_file.exists():
                return
            
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
            
            # Convert back to enums and objects
            if 'position' in data:
                data['position'] = ToastPosition(data['position'])
            
            self._settings = ToastSettings(**data)
            logger.info("Loaded toast notification settings")
            
        except Exception as e:
            logger.error(f"Failed to load toast settings: {e}")


# Singleton instance
_toast_manager: Optional[ToastManager] = None
_manager_lock = RLock()


def get_toast_manager(storage_path: Optional[str] = None) -> ToastManager:
    """
    Get singleton toast manager instance.
    
    Args:
        storage_path: Storage path (only used on first call)
        
    Returns:
        ToastManager instance
    """
    global _toast_manager
    
    with _manager_lock:
        if _toast_manager is None:
            _toast_manager = ToastManager(storage_path)
        
        return _toast_manager


def reset_toast_manager():
    """Reset the singleton toast manager (mainly for testing)."""
    global _toast_manager
    
    with _manager_lock:
        _toast_manager = None


# Convenience functions
def toast_success(title: str, message: str, **kwargs) -> str:
    """Create a success toast notification."""
    return get_toast_manager().create_notification(title, message, ToastType.SUCCESS, **kwargs)


def toast_info(title: str, message: str, **kwargs) -> str:
    """Create an info toast notification."""
    return get_toast_manager().create_notification(title, message, ToastType.INFO, **kwargs)


def toast_warning(title: str, message: str, **kwargs) -> str:
    """Create a warning toast notification."""
    return get_toast_manager().create_notification(title, message, ToastType.WARNING, **kwargs)


def toast_error(title: str, message: str, **kwargs) -> str:
    """Create an error toast notification."""
    return get_toast_manager().create_notification(title, message, ToastType.ERROR, **kwargs)