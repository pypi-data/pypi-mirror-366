"""
Notification channel implementations for multi-channel delivery.
"""

import asyncio
import logging
import smtplib
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from pathlib import Path

try:
    import aiosmtplib
    ASYNC_SMTP_AVAILABLE = True
except ImportError:
    ASYNC_SMTP_AVAILABLE = False

try:
    import firebase_admin
    from firebase_admin import messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

from .models import (
    Notification, NotificationChannel, NotificationResult, 
    NotificationStatus, ChannelConfig
)

logger = logging.getLogger(__name__)


class NotificationChannelBase(ABC):
    """Base class for notification channels."""
    
    def __init__(self, config: ChannelConfig):
        """
        Initialize notification channel.
        
        Args:
            config: Channel configuration
        """
        self.config = config
        self.channel_type = config.channel
        self._initialized = False
        
        logger.info(f"Initializing {self.channel_type.value} notification channel")
    
    async def initialize(self) -> bool:
        """Initialize the channel (async setup)."""
        try:
            await self._initialize()
            self._initialized = True
            logger.info(f"{self.channel_type.value} channel initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize {self.channel_type.value} channel: {str(e)}")
            return False
    
    @abstractmethod
    async def _initialize(self):
        """Channel-specific initialization."""
        pass
    
    @abstractmethod
    async def send(self, notification: Notification) -> NotificationResult:
        """
        Send notification through this channel.
        
        Args:
            notification: Notification to send
            
        Returns:
            NotificationResult
        """
        pass
    
    async def validate(self, notification: Notification) -> bool:
        """
        Validate notification before sending.
        
        Args:
            notification: Notification to validate
            
        Returns:
            True if valid
        """
        # Check if channel should deliver
        if not self.config.should_deliver(notification):
            return False
        
        # Check if initialized
        if not self._initialized:
            logger.warning(f"{self.channel_type.value} channel not initialized")
            return False
        
        # Channel-specific validation
        return await self._validate(notification)
    
    async def _validate(self, notification: Notification) -> bool:
        """Channel-specific validation."""
        return True
    
    def format_message(self, notification: Notification) -> Dict[str, Any]:
        """Format notification for this channel."""
        return {
            'title': notification.title,
            'message': notification.message,
            'data': notification.data,
            'severity': notification.severity.value,
            'timestamp': datetime.now().isoformat()
        }


class EmailNotifier(NotificationChannelBase):
    """Email notification channel using SMTP."""
    
    async def _initialize(self):
        """Initialize email channel."""
        # Validate required config
        required = ['smtp_host', 'smtp_port', 'from_email']
        missing = [field for field in required if field not in self.config.config]
        
        if missing:
            raise ValueError(f"Missing required email config: {missing}")
        
        # Test connection if possible
        if ASYNC_SMTP_AVAILABLE:
            self._async_smtp = True
        else:
            self._async_smtp = False
            logger.warning("aiosmtplib not available, using synchronous SMTP")
    
    async def send(self, notification: Notification) -> NotificationResult:
        """Send email notification."""
        start_time = datetime.now()
        
        try:
            # Validate notification
            if not await self.validate(notification):
                return NotificationResult(
                    notification_id=notification.id,
                    channel=NotificationChannel.EMAIL,
                    status=NotificationStatus.FAILED,
                    error_message="Validation failed"
                )
            
            # Format email
            email_data = self._format_email(notification)
            
            # Send email
            if self._async_smtp:
                success = await self._send_async(email_data, notification.recipients)
            else:
                success = await asyncio.to_thread(
                    self._send_sync, email_data, notification.recipients
                )
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            if success:
                return NotificationResult(
                    notification_id=notification.id,
                    channel=NotificationChannel.EMAIL,
                    status=NotificationStatus.SENT,
                    processing_time_ms=processing_time,
                    size_bytes=len(email_data['body'])
                )
            else:
                return NotificationResult(
                    notification_id=notification.id,
                    channel=NotificationChannel.EMAIL,
                    status=NotificationStatus.FAILED,
                    error_message="Failed to send email",
                    processing_time_ms=processing_time
                )
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return NotificationResult(
                notification_id=notification.id,
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )
    
    def _format_email(self, notification: Notification) -> Dict[str, Any]:
        """Format notification as email."""
        # Create subject
        subject = f"[{notification.severity.value.upper()}] {notification.title}"
        
        # Create body
        body_parts = [
            notification.message,
            "",
            "---",
            f"Source: {notification.source}",
            f"Time: {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        # Add data if present
        if notification.data:
            body_parts.extend([
                "",
                "Additional Information:",
                json.dumps(notification.data, indent=2)
            ])
        
        body = "\n".join(body_parts)
        
        # Create HTML version if template is available
        html_body = None
        if notification.template_name:
            # Would render template here
            pass
        
        return {
            'subject': subject,
            'body': body,
            'html_body': html_body,
            'from_email': self.config.config['from_email'],
            'from_name': self.config.config.get('from_name', 'Ansera Monitoring')
        }
    
    async def _send_async(self, email_data: Dict, recipients: List[str]) -> bool:
        """Send email using async SMTP."""
        try:
            smtp_config = self.config.config
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = email_data['subject']
            message['From'] = f"{email_data['from_name']} <{email_data['from_email']}>"
            message['To'] = ', '.join(recipients)
            
            # Add text part
            text_part = MIMEText(email_data['body'], 'plain')
            message.attach(text_part)
            
            # Add HTML part if available
            if email_data.get('html_body'):
                html_part = MIMEText(email_data['html_body'], 'html')
                message.attach(html_part)
            
            # Send via aiosmtplib
            await aiosmtplib.send(
                message,
                hostname=smtp_config['smtp_host'],
                port=smtp_config['smtp_port'],
                username=smtp_config.get('smtp_username'),
                password=smtp_config.get('smtp_password'),
                use_tls=smtp_config.get('use_tls', True)
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Async email send failed: {str(e)}")
            return False
    
    def _send_sync(self, email_data: Dict, recipients: List[str]) -> bool:
        """Send email using synchronous SMTP."""
        try:
            smtp_config = self.config.config
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = email_data['subject']
            msg['From'] = f"{email_data['from_name']} <{email_data['from_email']}>"
            msg['To'] = ', '.join(recipients)
            
            # Add text part
            text_part = MIMEText(email_data['body'], 'plain')
            msg.attach(text_part)
            
            # Connect and send
            with smtplib.SMTP(smtp_config['smtp_host'], smtp_config['smtp_port']) as server:
                if smtp_config.get('use_tls', True):
                    server.starttls()
                
                if smtp_config.get('smtp_username'):
                    server.login(
                        smtp_config['smtp_username'],
                        smtp_config['smtp_password']
                    )
                
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            logger.error(f"Sync email send failed: {str(e)}")
            return False
    
    async def _validate(self, notification: Notification) -> bool:
        """Validate email notification."""
        # Check for recipients
        if not notification.recipients:
            logger.warning("Email notification has no recipients")
            return False
        
        # Validate email addresses
        for recipient in notification.recipients:
            if '@' not in recipient:
                logger.warning(f"Invalid email address: {recipient}")
                return False
        
        return True


class PushNotifier(NotificationChannelBase):
    """Push notification channel using Firebase Cloud Messaging."""
    
    async def _initialize(self):
        """Initialize push notification channel."""
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin not available")
        
        # Get Firebase config
        firebase_config = self.config.config
        
        if 'credentials_path' not in firebase_config:
            raise ValueError("Firebase credentials_path required")
        
        # Initialize Firebase Admin SDK
        cred = firebase_admin.credentials.Certificate(firebase_config['credentials_path'])
        
        # Check if already initialized
        try:
            self._app = firebase_admin.get_app()
        except ValueError:
            self._app = firebase_admin.initialize_app(cred)
        
        logger.info("Firebase Admin SDK initialized")
    
    async def send(self, notification: Notification) -> NotificationResult:
        """Send push notification."""
        if not FIREBASE_AVAILABLE:
            return NotificationResult(
                notification_id=notification.id,
                channel=NotificationChannel.PUSH,
                status=NotificationStatus.FAILED,
                error_message="Firebase Admin SDK not available"
            )
            
        start_time = datetime.now()
        
        try:
            # Validate notification
            if not await self.validate(notification):
                return NotificationResult(
                    notification_id=notification.id,
                    channel=NotificationChannel.PUSH,
                    status=NotificationStatus.FAILED,
                    error_message="Validation failed"
                )
            
            # Format push message
            push_message = self._format_push_message(notification)
            
            # Send to each recipient (device token)
            success_count = 0
            failed_count = 0
            
            for device_token in notification.recipients:
                try:
                    # Send individual message
                    response = messaging.send(push_message, token=device_token)
                    success_count += 1
                    logger.debug(f"Push sent successfully: {response}")
                
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send push to {device_token}: {str(e)}")
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Determine overall status
            if success_count > 0 and failed_count == 0:
                status = NotificationStatus.SENT
                error_message = None
            elif success_count > 0 and failed_count > 0:
                status = NotificationStatus.SENT
                error_message = f"Partial failure: {failed_count} failed"
            else:
                status = NotificationStatus.FAILED
                error_message = f"All {failed_count} sends failed"
            
            return NotificationResult(
                notification_id=notification.id,
                channel=NotificationChannel.PUSH,
                status=status,
                error_message=error_message,
                processing_time_ms=processing_time
            )
        
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return NotificationResult(
                notification_id=notification.id,
                channel=NotificationChannel.PUSH,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )
    
    def _format_push_message(self, notification: Notification) -> Any:
        """Format notification as FCM message."""
        if not FIREBASE_AVAILABLE:
            raise RuntimeError("Firebase Admin SDK not available")
            
        # Create notification content
        fcm_notification = messaging.Notification(
            title=notification.title,
            body=notification.message
        )
        
        # Add data payload
        data_payload = {
            'notification_id': notification.id,
            'severity': notification.severity.value,
            'source': notification.source,
            'timestamp': notification.created_at.isoformat()
        }
        
        # Add custom data
        if notification.data:
            for key, value in notification.data.items():
                data_payload[key] = str(value)
        
        # Set Android-specific options
        android_config = messaging.AndroidConfig(
            priority='high' if notification.priority.value in ['high', 'urgent'] else 'normal',
            notification=messaging.AndroidNotification(
                icon='notification_icon',
                color='#f45342',
                sound='default'
            )
        )
        
        # Set iOS-specific options
        apns_config = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title=notification.title,
                        body=notification.message
                    ),
                    sound='default',
                    badge=1
                )
            )
        )
        
        # Build message (token will be set per recipient)
        return messaging.Message(
            notification=fcm_notification,
            data=data_payload,
            android=android_config,
            apns=apns_config
        )
    
    async def _validate(self, notification: Notification) -> bool:
        """Validate push notification."""
        # Check for recipients (device tokens)
        if not notification.recipients:
            logger.warning("Push notification has no recipients")
            return False
        
        # Validate message length
        if len(notification.title) > 200:
            logger.warning("Push notification title too long")
            return False
        
        if len(notification.message) > 4000:
            logger.warning("Push notification message too long")
            return False
        
        return True


class ToastNotifier(NotificationChannelBase):
    """In-dashboard toast notification channel."""
    
    def __init__(self, config: ChannelConfig, sse_manager=None):
        """
        Initialize toast notifier.
        
        Args:
            config: Channel configuration
            sse_manager: SSE manager for real-time delivery
        """
        super().__init__(config)
        self.sse_manager = sse_manager
        self._notification_queue = asyncio.Queue()
    
    async def _initialize(self):
        """Initialize toast notification channel."""
        # Check if SSE manager is available
        if not self.sse_manager:
            logger.warning("No SSE manager provided for toast notifications")
    
    async def send(self, notification: Notification) -> NotificationResult:
        """Send toast notification."""
        start_time = datetime.now()
        
        try:
            # Format toast data
            toast_data = {
                'id': notification.id,
                'type': 'toast',
                'title': notification.title,
                'message': notification.message,
                'severity': notification.severity.value,
                'duration': self.config.config.get('duration', 5000),  # ms
                'position': self.config.config.get('position', 'top-right'),
                'data': notification.data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send via SSE if available
            if self.sse_manager:
                sent_count = await self.sse_manager.broadcast_event(
                    event=toast_data,
                    event_type='dashboard_toast'
                )
                
                success = sent_count > 0
            else:
                # Queue for later delivery
                await self._notification_queue.put(toast_data)
                success = True
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return NotificationResult(
                notification_id=notification.id,
                channel=NotificationChannel.TOAST,
                status=NotificationStatus.SENT if success else NotificationStatus.FAILED,
                processing_time_ms=processing_time
            )
        
        except Exception as e:
            logger.error(f"Error sending toast notification: {str(e)}")
            return NotificationResult(
                notification_id=notification.id,
                channel=NotificationChannel.TOAST,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )
    
    async def get_queued_toasts(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get queued toast notifications."""
        toasts = []
        
        for _ in range(min(count, self._notification_queue.qsize())):
            try:
                toast = self._notification_queue.get_nowait()
                toasts.append(toast)
            except asyncio.QueueEmpty:
                break
        
        return toasts


class WebhookNotifier(NotificationChannelBase):
    """Webhook notification channel for external integrations."""
    
    async def _initialize(self):
        """Initialize webhook channel."""
        import aiohttp
        
        # Validate webhook URL
        if 'webhook_url' not in self.config.config:
            raise ValueError("webhook_url required in config")
        
        self.webhook_url = self.config.config['webhook_url']
        self.headers = self.config.config.get('headers', {})
        self.timeout = self.config.config.get('timeout', 30)
    
    async def send(self, notification: Notification) -> NotificationResult:
        """Send webhook notification."""
        import aiohttp
        
        start_time = datetime.now()
        
        try:
            # Format webhook payload
            payload = {
                'notification_id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'severity': notification.severity.value,
                'source': notification.source,
                'event_type': notification.event_type,
                'data': notification.data,
                'timestamp': notification.created_at.isoformat()
            }
            
            # Add custom fields if configured
            if 'custom_fields' in self.config.config:
                payload.update(self.config.config['custom_fields'])
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    success = response.status < 400
                    response_text = await response.text()
                    
                    # Calculate processing time
                    processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    
                    if success:
                        return NotificationResult(
                            notification_id=notification.id,
                            channel=NotificationChannel.WEBHOOK,
                            status=NotificationStatus.SENT,
                            delivery_id=response.headers.get('X-Request-ID'),
                            processing_time_ms=processing_time,
                            size_bytes=len(json.dumps(payload))
                        )
                    else:
                        return NotificationResult(
                            notification_id=notification.id,
                            channel=NotificationChannel.WEBHOOK,
                            status=NotificationStatus.FAILED,
                            error_code=str(response.status),
                            error_message=response_text[:500],
                            processing_time_ms=processing_time
                        )
        
        except Exception as e:
            logger.error(f"Error sending webhook: {str(e)}")
            return NotificationResult(
                notification_id=notification.id,
                channel=NotificationChannel.WEBHOOK,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )