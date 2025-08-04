"""
Ansera Notification System

Provides multi-channel notification capabilities for enterprise monitoring.

Components:
- NotificationManager: Core notification coordination and routing
- EmailNotifier: SMTP email notifications with templates
- PushNotifier: Mobile push notifications (Firebase/OneSignal)  
- ToastNotifier: In-dashboard toast/alert notifications
- NotificationRules: Event-based notification rule engine
- NotificationTemplates: Message templating system

Usage:
    from vector_db_query.monitoring.notifications import NotificationManager, EmailNotifier
    
    # Create notification manager
    manager = NotificationManager()
    
    # Add notification channels
    manager.add_channel("email", EmailNotifier(smtp_config))
    manager.add_channel("push", PushNotifier(push_config))
    
    # Send notification
    await manager.send_notification(
        channels=["email", "push"],
        title="Task Completed",
        message="Document processing finished successfully",
        severity="info",
        data={"task_id": "123"}
    )
"""

from .manager import NotificationManager
from .channels import EmailNotifier, PushNotifier, ToastNotifier, WebhookNotifier
from .rules import NotificationRules, NotificationRule
from .templates import NotificationTemplates, EmailTemplate, PushTemplate
from .models import (
    Notification, NotificationChannel, NotificationSeverity, 
    NotificationResult, ChannelConfig
)
from .toast_manager import (
    ToastManager, ToastNotification, ToastType, ToastPosition, ToastSettings,
    get_toast_manager, reset_toast_manager,
    toast_success, toast_info, toast_warning, toast_error
)
from .email_service import (
    EmailService, SMTPConfig, EmailTemplate, EmailRecipientGroup, EmailSettings,
    EmailAuthType, EmailPriority, get_email_service, reset_email_service,
    send_email_notification, send_error_email, send_warning_email, send_info_email
)
from .push_service import (
    PushService, DeviceToken, PushTopic, PushTemplate, PushSettings,
    DevicePlatform, PushPriority, get_push_service, reset_push_service,
    send_push_notification, send_push_error, send_push_warning, send_push_info
)
from .event_config import (
    EventConfigurationService, EventConfiguration, EventCondition, NotificationRule,
    EventType, TriggerCondition, EventPriority, get_event_config_service, 
    reset_event_config_service, process_system_event, trigger_service_failure_event,
    trigger_high_cpu_event, trigger_queue_full_event
)

__all__ = [
    'NotificationManager',
    'EmailNotifier',
    'PushNotifier', 
    'ToastNotifier',
    'WebhookNotifier',
    'NotificationRules',
    'NotificationRule',
    'NotificationTemplates',
    'EmailTemplate',
    'PushTemplate',
    'Notification',
    'NotificationChannel',
    'NotificationSeverity',
    'NotificationResult',
    'ChannelConfig',
    'ToastManager',
    'ToastNotification',
    'ToastType',
    'ToastPosition',
    'ToastSettings',
    'get_toast_manager',
    'reset_toast_manager',
    'toast_success',
    'toast_info',
    'toast_warning',
    'toast_error',
    'EmailService',
    'SMTPConfig',
    'EmailTemplate',
    'EmailRecipientGroup',
    'EmailSettings',
    'EmailAuthType',
    'EmailPriority',
    'get_email_service',
    'reset_email_service',
    'send_email_notification',
    'send_error_email',
    'send_warning_email',
    'send_info_email',
    'PushService',
    'DeviceToken',
    'PushTopic',
    'PushTemplate',
    'PushSettings',
    'DevicePlatform',
    'PushPriority',
    'get_push_service',
    'reset_push_service',
    'send_push_notification',
    'send_push_error',
    'send_push_warning',
    'send_push_info',
    'EventConfigurationService',
    'EventConfiguration',
    'EventCondition',
    'NotificationRule',
    'EventType',
    'TriggerCondition',
    'EventPriority',
    'get_event_config_service',
    'reset_event_config_service',
    'process_system_event',
    'trigger_service_failure_event',
    'trigger_high_cpu_event',
    'trigger_queue_full_event'
]

__version__ = '1.0.0'