"""
Email notification service for the monitoring dashboard.

This module provides email notification management with SMTP configuration,
template support, and integration with the monitoring system.
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from threading import RLock
from enum import Enum
from pathlib import Path
import uuid

from .channels import EmailNotifier
from .models import (
    Notification, NotificationChannel, NotificationSeverity, 
    NotificationResult, ChannelConfig
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class EmailPriority(Enum):
    """Email priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailAuthType(Enum):
    """Email authentication types."""
    NONE = "none"
    PLAIN = "plain"
    LOGIN = "login"
    OAUTH2 = "oauth2"


@dataclass
class SMTPConfig:
    """SMTP server configuration."""
    smtp_host: str
    smtp_port: int = 587
    use_tls: bool = True
    use_ssl: bool = False
    auth_type: EmailAuthType = EmailAuthType.PLAIN
    username: Optional[str] = None
    password: Optional[str] = None
    timeout: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'smtp_host': self.smtp_host,
            'smtp_port': self.smtp_port,
            'use_tls': self.use_tls,
            'use_ssl': self.use_ssl,
            'auth_type': self.auth_type.value,
            'username': self.username,
            'password': self.password,  # Note: In production, encrypt this
            'timeout': self.timeout
        }


@dataclass
class EmailTemplate:
    """Email template configuration."""
    id: str
    name: str
    subject_template: str
    body_template: str
    html_template: Optional[str] = None
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
            'subject_template': self.subject_template,
            'body_template': self.body_template,
            'html_template': self.html_template,
            'severity_filter': self.severity_filter,
            'category_filter': self.category_filter,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class EmailRecipientGroup:
    """Email recipient group."""
    id: str
    name: str
    email_addresses: List[str]
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
            'email_addresses': self.email_addresses,
            'severity_filter': self.severity_filter,
            'category_filter': self.category_filter,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class EmailSettings:
    """Email notification settings."""
    enabled: bool = True
    from_email: str = ""
    from_name: str = "Ansera Monitoring"
    default_template_id: Optional[str] = None
    default_recipient_group_id: Optional[str] = None
    rate_limit_per_hour: int = 100
    batch_size: int = 10
    retry_count: int = 3
    retry_delay_seconds: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'from_email': self.from_email,
            'from_name': self.from_name,
            'default_template_id': self.default_template_id,
            'default_recipient_group_id': self.default_recipient_group_id,
            'rate_limit_per_hour': self.rate_limit_per_hour,
            'batch_size': self.batch_size,
            'retry_count': self.retry_count,
            'retry_delay_seconds': self.retry_delay_seconds
        }


class EmailService:
    """
    Email notification service for the monitoring dashboard.
    
    Provides email configuration, template management, recipient groups,
    and integration with the notification system.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize email service.
        
        Args:
            storage_path: Path for email configuration persistence
        """
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # Storage
        self.storage_path = Path(storage_path) if storage_path else Path.home() / ".ansera" / "email"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.config_file = self.storage_path / "email_config.json"
        self.templates_file = self.storage_path / "email_templates.json"
        self.recipients_file = self.storage_path / "email_recipients.json"
        self.settings_file = self.storage_path / "email_settings.json"
        
        # Configuration
        self._smtp_config: Optional[SMTPConfig] = None
        self._settings = EmailSettings()
        
        # Templates and recipients
        self._templates: Dict[str, EmailTemplate] = {}
        self._recipient_groups: Dict[str, EmailRecipientGroup] = {}
        
        # Email notifier instance
        self._email_notifier: Optional[EmailNotifier] = None
        
        # Rate limiting
        self._sent_emails_by_hour: Dict[str, int] = {}
        
        # Load persisted data
        self._load_smtp_config()
        self._load_settings()
        self._load_templates()
        self._load_recipient_groups()
        
        # Initialize default templates if none exist
        if not self._templates:
            self._create_default_templates()
        
        logger.info(f"EmailService initialized with {len(self._templates)} templates and {len(self._recipient_groups)} recipient groups")
    
    def configure_smtp(self, smtp_config: SMTPConfig) -> bool:
        """
        Configure SMTP settings.
        
        Args:
            smtp_config: SMTP configuration
            
        Returns:
            True if configured successfully
        """
        with self._lock:
            try:
                old_config = self._smtp_config.to_dict() if self._smtp_config else None
                self._smtp_config = smtp_config
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description="SMTP configuration updated",
                    details={
                        'old_config': old_config,
                        'new_config': smtp_config.to_dict()
                    }
                )
                
                # Save configuration
                self._save_smtp_config()
                
                # Reset email notifier to pick up new config
                self._email_notifier = None
                
                logger.info("SMTP configuration updated")
                return True
                
            except Exception as e:
                logger.error(f"Failed to configure SMTP: {e}")
                return False
    
    def update_settings(self, settings: EmailSettings) -> bool:
        """
        Update email settings.
        
        Args:
            settings: New email settings
            
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
                    description="Email settings updated",
                    details={
                        'old_settings': old_settings,
                        'new_settings': settings.to_dict()
                    }
                )
                
                # Save settings
                self._save_settings()
                
                logger.info("Email settings updated")
                return True
                
            except Exception as e:
                logger.error(f"Failed to update email settings: {e}")
                return False
    
    def add_template(self, template: EmailTemplate) -> bool:
        """
        Add email template.
        
        Args:
            template: Email template to add
            
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
                    description=f"Email template added: {template.name}",
                    details={
                        'template_id': template.id,
                        'template_name': template.name
                    }
                )
                
                # Save templates
                self._save_templates()
                
                logger.info(f"Email template added: {template.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add email template: {e}")
                return False
    
    def remove_template(self, template_id: str) -> bool:
        """
        Remove email template.
        
        Args:
            template_id: ID of template to remove
            
        Returns:
            True if removed successfully
        """
        with self._lock:
            try:
                if template_id not in self._templates:
                    logger.warning(f"Template not found: {template_id}")
                    return False
                
                template = self._templates.pop(template_id)
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.DELETE,
                    description=f"Email template removed: {template.name}",
                    details={
                        'template_id': template_id,
                        'template_name': template.name
                    }
                )
                
                # Save templates
                self._save_templates()
                
                logger.info(f"Email template removed: {template.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to remove email template: {e}")
                return False
    
    def add_recipient_group(self, group: EmailRecipientGroup) -> bool:
        """
        Add recipient group.
        
        Args:
            group: Recipient group to add
            
        Returns:
            True if added successfully
        """
        with self._lock:
            try:
                self._recipient_groups[group.id] = group
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.CREATE,
                    description=f"Email recipient group added: {group.name}",
                    details={
                        'group_id': group.id,
                        'group_name': group.name,
                        'recipient_count': len(group.email_addresses)
                    }
                )
                
                # Save recipient groups
                self._save_recipient_groups()
                
                logger.info(f"Email recipient group added: {group.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add recipient group: {e}")
                return False
    
    def remove_recipient_group(self, group_id: str) -> bool:
        """
        Remove recipient group.
        
        Args:
            group_id: ID of group to remove
            
        Returns:
            True if removed successfully
        """
        with self._lock:
            try:
                if group_id not in self._recipient_groups:
                    logger.warning(f"Recipient group not found: {group_id}")
                    return False
                
                group = self._recipient_groups.pop(group_id)
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.DELETE,
                    description=f"Email recipient group removed: {group.name}",
                    details={
                        'group_id': group_id,
                        'group_name': group.name
                    }
                )
                
                # Save recipient groups
                self._save_recipient_groups()
                
                logger.info(f"Email recipient group removed: {group.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to remove recipient group: {e}")
                return False
    
    async def send_notification(self, title: str, message: str, 
                              severity: NotificationSeverity = NotificationSeverity.INFO,
                              category: str = "general",
                              source: str = "system",
                              template_id: Optional[str] = None,
                              recipient_group_id: Optional[str] = None,
                              custom_recipients: Optional[List[str]] = None,
                              data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send email notification.
        
        Args:
            title: Notification title
            message: Notification message
            severity: Notification severity
            category: Notification category
            source: Notification source
            template_id: Optional template ID
            recipient_group_id: Optional recipient group ID
            custom_recipients: Optional custom recipient list
            data: Optional additional data
            
        Returns:
            True if sent successfully
        """
        with self._lock:
            try:
                # Check if email service is enabled
                if not self._settings.enabled:
                    logger.info("Email service is disabled")
                    return False
                
                # Check if SMTP is configured
                if not self._smtp_config:
                    logger.warning("SMTP not configured")
                    return False
                
                # Check rate limiting
                current_hour = datetime.now().strftime('%Y-%m-%d-%H')
                if current_hour in self._sent_emails_by_hour:
                    if self._sent_emails_by_hour[current_hour] >= self._settings.rate_limit_per_hour:
                        logger.warning("Email rate limit exceeded")
                        return False
                
                # Determine recipients
                recipients = []
                if custom_recipients:
                    recipients = custom_recipients
                elif recipient_group_id and recipient_group_id in self._recipient_groups:
                    group = self._recipient_groups[recipient_group_id]
                    if group.is_active:
                        recipients = group.email_addresses
                elif self._settings.default_recipient_group_id:
                    default_group = self._recipient_groups.get(self._settings.default_recipient_group_id)
                    if default_group and default_group.is_active:
                        recipients = default_group.email_addresses
                
                if not recipients:
                    logger.warning("No recipients found for email notification")
                    return False
                
                # Create notification
                notification = Notification(
                    id=str(uuid.uuid4()),
                    title=title,
                    message=message,
                    severity=severity,
                    source=source,
                    event_type=category,
                    recipients=recipients,
                    data=data or {},
                    template_name=template_id,
                    created_at=datetime.now()
                )
                
                # Get email notifier
                email_notifier = await self._get_email_notifier()
                if not email_notifier:
                    logger.error("Failed to get email notifier")
                    return False
                
                # Send notification
                result = await email_notifier.send(notification)
                
                # Track sent email for rate limiting
                if current_hour not in self._sent_emails_by_hour:
                    self._sent_emails_by_hour[current_hour] = 0
                self._sent_emails_by_hour[current_hour] += 1
                
                # Clean up old hour counters
                self._cleanup_rate_limit_counters()
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.NOTIFICATION,
                    change_type=ChangeType.CREATE,
                    description=f"Email notification sent: {title}",
                    details={
                        'notification_id': notification.id,
                        'title': title,
                        'severity': severity.value,
                        'recipient_count': len(recipients),
                        'success': result.status.value == 'sent'
                    }
                )
                
                logger.info(f"Email notification sent: {title} (status: {result.status.value})")
                return result.status.value == 'sent'
                
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")
                return False
    
    async def test_smtp_connection(self) -> Dict[str, Any]:
        """
        Test SMTP connection.
        
        Returns:
            Test result with status and details
        """
        try:
            if not self._smtp_config:
                return {
                    'success': False,
                    'error': 'SMTP not configured'
                }
            
            # Get email notifier
            email_notifier = await self._get_email_notifier()
            if not email_notifier:
                return {
                    'success': False,
                    'error': 'Failed to create email notifier'
                }
            
            # Create test notification
            test_notification = Notification(
                id=str(uuid.uuid4()),
                title="SMTP Test",
                message="This is a test email to verify SMTP configuration.",
                severity=NotificationSeverity.INFO,
                source="email_service_test",
                event_type="test",
                recipients=[self._settings.from_email],  # Send to self
                data={},
                created_at=datetime.now()
            )
            
            # Send test email
            result = await email_notifier.send(test_notification)
            
            return {
                'success': result.status.value == 'sent',
                'status': result.status.value,
                'processing_time_ms': result.processing_time_ms,
                'error': result.error_message
            }
            
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_smtp_config(self) -> Optional[SMTPConfig]:
        """Get current SMTP configuration."""
        with self._lock:
            return self._smtp_config
    
    def get_settings(self) -> EmailSettings:
        """Get current email settings."""
        with self._lock:
            return self._settings
    
    def get_templates(self) -> Dict[str, EmailTemplate]:
        """Get all email templates."""
        with self._lock:
            return self._templates.copy()
    
    def get_template(self, template_id: str) -> Optional[EmailTemplate]:
        """Get specific email template."""
        with self._lock:
            return self._templates.get(template_id)
    
    def get_recipient_groups(self) -> Dict[str, EmailRecipientGroup]:
        """Get all recipient groups."""
        with self._lock:
            return self._recipient_groups.copy()
    
    def get_recipient_group(self, group_id: str) -> Optional[EmailRecipientGroup]:
        """Get specific recipient group."""
        with self._lock:
            return self._recipient_groups.get(group_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get email service statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            current_hour = datetime.now().strftime('%Y-%m-%d-%H')
            emails_this_hour = self._sent_emails_by_hour.get(current_hour, 0)
            
            return {
                'smtp_configured': self._smtp_config is not None,
                'service_enabled': self._settings.enabled,
                'templates_count': len(self._templates),
                'recipient_groups_count': len(self._recipient_groups),
                'emails_sent_this_hour': emails_this_hour,
                'rate_limit_per_hour': self._settings.rate_limit_per_hour,
                'rate_limit_remaining': max(0, self._settings.rate_limit_per_hour - emails_this_hour)
            }
    
    async def _get_email_notifier(self) -> Optional[EmailNotifier]:
        """Get configured email notifier."""
        if not self._email_notifier and self._smtp_config:
            try:
                # Create channel config
                channel_config = ChannelConfig(
                    channel=NotificationChannel.EMAIL,
                    config={
                        'smtp_host': self._smtp_config.smtp_host,
                        'smtp_port': self._smtp_config.smtp_port,
                        'smtp_username': self._smtp_config.username,
                        'smtp_password': self._smtp_config.password,
                        'use_tls': self._smtp_config.use_tls,
                        'from_email': self._settings.from_email,
                        'from_name': self._settings.from_name
                    }
                )
                
                # Create and initialize email notifier
                self._email_notifier = EmailNotifier(channel_config)
                await self._email_notifier.initialize()
                
            except Exception as e:
                logger.error(f"Failed to create email notifier: {e}")
                return None
        
        return self._email_notifier
    
    def _create_default_templates(self):
        """Create default email templates."""
        templates = [
            EmailTemplate(
                id="default_info",
                name="Default Info",
                subject_template="[INFO] {{title}}",
                body_template="""{{message}}

Source: {{source}}
Time: {{timestamp}}
{% if data %}
Additional Details:
{% for key, value in data.items() %}
- {{key}}: {{value}}
{% endfor %}
{% endif %}

---
Ansera Monitoring System""",
                severity_filter=["info"]
            ),
            EmailTemplate(
                id="default_warning",
                name="Default Warning",
                subject_template="⚠️ [WARNING] {{title}}",
                body_template="""⚠️ Warning Alert

{{message}}

Source: {{source}}
Time: {{timestamp}}
Severity: {{severity}}

{% if data %}
Additional Details:
{% for key, value in data.items() %}
- {{key}}: {{value}}
{% endfor %}
{% endif %}

Please review this warning and take appropriate action.

---
Ansera Monitoring System""",
                severity_filter=["warning"]
            ),
            EmailTemplate(
                id="default_error",
                name="Default Error",
                subject_template="🚨 [ERROR] {{title}}",
                body_template="""🚨 ERROR ALERT

{{message}}

Source: {{source}}
Time: {{timestamp}}
Severity: {{severity}}

{% if data %}
Error Details:
{% for key, value in data.items() %}
- {{key}}: {{value}}
{% endfor %}
{% endif %}

IMMEDIATE ATTENTION REQUIRED

---
Ansera Monitoring System""",
                severity_filter=["error", "critical"]
            )
        ]
        
        for template in templates:
            self._templates[template.id] = template
        
        self._save_templates()
        logger.info("Created default email templates")
    
    def _cleanup_rate_limit_counters(self):
        """Clean up old rate limit counters."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=25)  # Keep 25 hours of data
        
        to_remove = []
        for hour_key in self._sent_emails_by_hour:
            hour_time = datetime.strptime(hour_key, '%Y-%m-%d-%H')
            if hour_time < cutoff_time:
                to_remove.append(hour_key)
        
        for key in to_remove:
            del self._sent_emails_by_hour[key]
    
    def _save_smtp_config(self):
        """Save SMTP configuration to storage."""
        try:
            if self._smtp_config:
                with open(self.config_file, 'w') as f:
                    json.dump(self._smtp_config.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save SMTP config: {e}")
    
    def _load_smtp_config(self):
        """Load SMTP configuration from storage."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                data['auth_type'] = EmailAuthType(data.get('auth_type', 'plain'))
                self._smtp_config = SMTPConfig(**data)
                logger.info("Loaded SMTP configuration")
        except Exception as e:
            logger.error(f"Failed to load SMTP config: {e}")
    
    def _save_settings(self):
        """Save email settings to storage."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self._settings.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save email settings: {e}")
    
    def _load_settings(self):
        """Load email settings from storage."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                
                self._settings = EmailSettings(**data)
                logger.info("Loaded email settings")
        except Exception as e:
            logger.error(f"Failed to load email settings: {e}")
    
    def _save_templates(self):
        """Save email templates to storage."""
        try:
            data = {tid: template.to_dict() for tid, template in self._templates.items()}
            with open(self.templates_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save email templates: {e}")
    
    def _load_templates(self):
        """Load email templates from storage."""
        try:
            if self.templates_file.exists():
                with open(self.templates_file, 'r') as f:
                    data = json.load(f)
                
                for tid, template_data in data.items():
                    template_data['created_at'] = datetime.fromisoformat(template_data['created_at'])
                    template = EmailTemplate(**template_data)
                    self._templates[tid] = template
                
                logger.info(f"Loaded {len(self._templates)} email templates")
        except Exception as e:
            logger.error(f"Failed to load email templates: {e}")
    
    def _save_recipient_groups(self):
        """Save recipient groups to storage."""
        try:
            data = {gid: group.to_dict() for gid, group in self._recipient_groups.items()}
            with open(self.recipients_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save recipient groups: {e}")
    
    def _load_recipient_groups(self):
        """Load recipient groups from storage."""
        try:
            if self.recipients_file.exists():
                with open(self.recipients_file, 'r') as f:
                    data = json.load(f)
                
                for gid, group_data in data.items():
                    group_data['created_at'] = datetime.fromisoformat(group_data['created_at'])
                    group = EmailRecipientGroup(**group_data)
                    self._recipient_groups[gid] = group
                
                logger.info(f"Loaded {len(self._recipient_groups)} recipient groups")
        except Exception as e:
            logger.error(f"Failed to load recipient groups: {e}")


# Singleton instance
_email_service: Optional[EmailService] = None
_service_lock = RLock()


def get_email_service(storage_path: Optional[str] = None) -> EmailService:
    """
    Get singleton email service instance.
    
    Args:
        storage_path: Storage path (only used on first call)
        
    Returns:
        EmailService instance
    """
    global _email_service
    
    with _service_lock:
        if _email_service is None:
            _email_service = EmailService(storage_path)
        
        return _email_service


def reset_email_service():
    """Reset the singleton email service (mainly for testing)."""
    global _email_service
    
    with _service_lock:
        _email_service = None


# Convenience functions
async def send_email_notification(title: str, message: str, 
                                severity: NotificationSeverity = NotificationSeverity.INFO,
                                **kwargs) -> bool:
    """Send email notification using default service."""
    email_service = get_email_service()
    return await email_service.send_notification(title, message, severity, **kwargs)


async def send_error_email(title: str, message: str, **kwargs) -> bool:
    """Send error email notification."""
    return await send_email_notification(title, message, NotificationSeverity.ERROR, **kwargs)


async def send_warning_email(title: str, message: str, **kwargs) -> bool:
    """Send warning email notification."""
    return await send_email_notification(title, message, NotificationSeverity.WARNING, **kwargs)


async def send_info_email(title: str, message: str, **kwargs) -> bool:
    """Send info email notification."""
    return await send_email_notification(title, message, NotificationSeverity.INFO, **kwargs)