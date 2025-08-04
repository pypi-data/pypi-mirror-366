"""
Notification templating system for consistent messaging.
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader, select_autoescape

from .models import NotificationTemplate, NotificationChannel

logger = logging.getLogger(__name__)


@dataclass
class EmailTemplate(NotificationTemplate):
    """Email-specific notification template."""
    channel: NotificationChannel = NotificationChannel.EMAIL
    html_template: Optional[str] = None
    
    # Email-specific settings
    include_footer: bool = True
    include_unsubscribe: bool = True
    reply_to: Optional[str] = None
    
    def render_html(self, data: Dict[str, Any]) -> Optional[str]:
        """Render HTML template with data."""
        if not self.html_template:
            return None
        
        template_data = {**self.default_data, **data}
        
        try:
            template = Template(self.html_template)
            return template.render(**template_data)
        except Exception as e:
            logger.error(f"Error rendering HTML template: {str(e)}")
            return None


@dataclass 
class PushTemplate(NotificationTemplate):
    """Push notification-specific template."""
    channel: NotificationChannel = NotificationChannel.PUSH
    
    # Push-specific settings
    icon: Optional[str] = None
    color: Optional[str] = None
    sound: Optional[str] = "default"
    badge_count: Optional[int] = None
    action_buttons: List[Dict[str, str]] = field(default_factory=list)
    
    def format_for_push(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format template for push notification."""
        return {
            'title': self.render_title(data),
            'body': self.render_message(data),
            'icon': self.icon,
            'color': self.color,
            'sound': self.sound,
            'badge': self.badge_count,
            'actions': self.action_buttons
        }


class NotificationTemplates:
    """
    Notification template manager.
    
    Handles template storage, rendering, and management.
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize template manager.
        
        Args:
            template_dir: Directory containing template files
        """
        self.template_dir = Path(template_dir) if template_dir else None
        self._templates: Dict[str, NotificationTemplate] = {}
        self._jinja_env = None
        
        # Initialize Jinja2 if template directory provided
        if self.template_dir and self.template_dir.exists():
            self._jinja_env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=select_autoescape(['html', 'xml'])
            )
        
        # Load built-in templates
        self._load_builtin_templates()
        
        logger.info(f"NotificationTemplates initialized with {len(self._templates)} templates")
    
    def _load_builtin_templates(self):
        """Load built-in notification templates."""
        
        # Task completion template
        self.add_template(NotificationTemplate(
            name="task_completed",
            title_template="Task Completed: {task_name}",
            message_template="Task '{task_name}' completed successfully in {duration}s",
            required_variables=["task_name", "duration"]
        ))
        
        # Task failed template
        self.add_template(NotificationTemplate(
            name="task_failed",
            title_template="Task Failed: {task_name}",
            message_template="Task '{task_name}' failed with error: {error_message}",
            required_variables=["task_name", "error_message"]
        ))
        
        # Schedule triggered template
        self.add_template(NotificationTemplate(
            name="schedule_triggered",
            title_template="Schedule Triggered: {schedule_name}",
            message_template="Schedule '{schedule_name}' was triggered by {trigger_source}",
            required_variables=["schedule_name", "trigger_source"]
        ))
        
        # System alert template
        self.add_template(NotificationTemplate(
            name="system_alert",
            title_template="System Alert: {alert_type}",
            message_template="{alert_message}\n\nSeverity: {severity}\nSource: {source}",
            required_variables=["alert_type", "alert_message", "severity", "source"]
        ))
        
        # Error threshold template
        self.add_template(NotificationTemplate(
            name="error_threshold",
            title_template="Error Threshold Exceeded",
            message_template="Error rate has exceeded threshold: {error_rate}% (threshold: {threshold}%)\n\nRecent errors: {error_count}",
            required_variables=["error_rate", "threshold", "error_count"]
        ))
        
        # Service status template
        self.add_template(NotificationTemplate(
            name="service_status",
            title_template="Service {service_name} is {status}",
            message_template="Service '{service_name}' status changed to {status} at {timestamp}",
            required_variables=["service_name", "status", "timestamp"]
        ))
        
        # Resource alert template
        self.add_template(NotificationTemplate(
            name="resource_alert",
            title_template="Resource Alert: {resource_type}",
            message_template="{resource_type} usage is at {usage_percent}% (threshold: {threshold}%)\n\nDetails: {details}",
            required_variables=["resource_type", "usage_percent", "threshold", "details"]
        ))
        
        # Email-specific templates
        self.add_template(EmailTemplate(
            name="email_task_report",
            title_template="Task Report: {report_date}",
            message_template="Daily task report for {report_date}\n\nCompleted: {completed_count}\nFailed: {failed_count}\nPending: {pending_count}",
            html_template="""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Task Report: {{ report_date }}</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 10px; background: #4CAF50; color: white;">Completed</td>
                        <td style="padding: 10px;">{{ completed_count }}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; background: #f44336; color: white;">Failed</td>
                        <td style="padding: 10px;">{{ failed_count }}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; background: #ff9800; color: white;">Pending</td>
                        <td style="padding: 10px;">{{ pending_count }}</td>
                    </tr>
                </table>
            </body>
            </html>
            """,
            required_variables=["report_date", "completed_count", "failed_count", "pending_count"]
        ))
        
        # Push-specific templates
        self.add_template(PushTemplate(
            name="push_task_alert",
            title_template="Task Alert",
            message_template="{task_name}: {status}",
            icon="task_icon",
            color="#4CAF50",
            action_buttons=[
                {"action": "view", "title": "View Details"},
                {"action": "dismiss", "title": "Dismiss"}
            ],
            required_variables=["task_name", "status"]
        ))
    
    def add_template(self, template: NotificationTemplate):
        """Add a notification template."""
        self._templates[template.name] = template
        logger.debug(f"Added template: {template.name}")
    
    def remove_template(self, template_name: str) -> bool:
        """Remove a notification template."""
        if template_name in self._templates:
            del self._templates[template_name]
            logger.debug(f"Removed template: {template_name}")
            return True
        return False
    
    def get_template(self, template_name: str) -> Optional[NotificationTemplate]:
        """Get a template by name."""
        return self._templates.get(template_name)
    
    def get_all_templates(self) -> List[NotificationTemplate]:
        """Get all templates."""
        return list(self._templates.values())
    
    def get_templates_for_channel(
        self, 
        channel: NotificationChannel
    ) -> List[NotificationTemplate]:
        """Get templates for a specific channel."""
        return [
            template for template in self._templates.values()
            if template.channel is None or template.channel == channel
        ]
    
    def render_notification(
        self,
        template_name: str,
        data: Dict[str, Any],
        channel: Optional[NotificationChannel] = None
    ) -> Dict[str, Any]:
        """
        Render a notification using a template.
        
        Args:
            template_name: Template name
            data: Template data
            channel: Target channel (for channel-specific rendering)
            
        Returns:
            Rendered notification data
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        # Validate required variables
        missing = template.validate_data(data)
        if missing:
            raise ValueError(f"Missing required template variables: {missing}")
        
        # Basic rendering
        result = {
            'title': template.render_title(data),
            'message': template.render_message(data),
            'template_name': template_name
        }
        
        # Channel-specific rendering
        if isinstance(template, EmailTemplate) and channel == NotificationChannel.EMAIL:
            html_content = template.render_html(data)
            if html_content:
                result['html_message'] = html_content
            result['reply_to'] = template.reply_to
            result['include_footer'] = template.include_footer
            result['include_unsubscribe'] = template.include_unsubscribe
        
        elif isinstance(template, PushTemplate) and channel == NotificationChannel.PUSH:
            push_data = template.format_for_push(data)
            result.update(push_data)
        
        return result
    
    def render_from_file(
        self,
        template_file: str,
        data: Dict[str, Any]
    ) -> str:
        """
        Render a template from file using Jinja2.
        
        Args:
            template_file: Template file name
            data: Template data
            
        Returns:
            Rendered content
        """
        if not self._jinja_env:
            raise ValueError("No template directory configured")
        
        try:
            template = self._jinja_env.get_template(template_file)
            return template.render(**data)
        except Exception as e:
            logger.error(f"Error rendering template file {template_file}: {str(e)}")
            raise
    
    def load_templates_from_file(self, config_file: str):
        """Load templates from configuration file."""
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Template config file not found: {config_file}")
        
        with config_path.open('r') as f:
            config = json.load(f)
        
        for template_config in config.get('templates', []):
            try:
                # Determine template type
                channel = template_config.get('channel')
                
                if channel == 'email':
                    template = EmailTemplate(
                        name=template_config['name'],
                        title_template=template_config['title_template'],
                        message_template=template_config['message_template'],
                        html_template=template_config.get('html_template'),
                        required_variables=template_config.get('required_variables', []),
                        default_data=template_config.get('default_data', {}),
                        include_footer=template_config.get('include_footer', True),
                        include_unsubscribe=template_config.get('include_unsubscribe', True),
                        reply_to=template_config.get('reply_to')
                    )
                
                elif channel == 'push':
                    template = PushTemplate(
                        name=template_config['name'],
                        title_template=template_config['title_template'],
                        message_template=template_config['message_template'],
                        required_variables=template_config.get('required_variables', []),
                        default_data=template_config.get('default_data', {}),
                        icon=template_config.get('icon'),
                        color=template_config.get('color'),
                        sound=template_config.get('sound', 'default'),
                        badge_count=template_config.get('badge_count'),
                        action_buttons=template_config.get('action_buttons', [])
                    )
                
                else:
                    template = NotificationTemplate(
                        name=template_config['name'],
                        title_template=template_config['title_template'],
                        message_template=template_config['message_template'],
                        required_variables=template_config.get('required_variables', []),
                        default_data=template_config.get('default_data', {})
                    )
                
                self.add_template(template)
                
            except Exception as e:
                logger.error(f"Error loading template {template_config.get('name', 'unknown')}: {str(e)}")
    
    def save_templates_to_file(self, output_file: str):
        """Save templates to configuration file."""
        templates_data = []
        
        for template in self._templates.values():
            template_dict = template.to_dict()
            
            # Add type-specific fields
            if isinstance(template, EmailTemplate):
                template_dict['html_template'] = template.html_template
                template_dict['include_footer'] = template.include_footer
                template_dict['include_unsubscribe'] = template.include_unsubscribe
                template_dict['reply_to'] = template.reply_to
            
            elif isinstance(template, PushTemplate):
                template_dict['icon'] = template.icon
                template_dict['color'] = template.color
                template_dict['sound'] = template.sound
                template_dict['badge_count'] = template.badge_count
                template_dict['action_buttons'] = template.action_buttons
            
            templates_data.append(template_dict)
        
        config = {
            'templates': templates_data,
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'total_templates': len(templates_data)
            }
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with output_path.open('w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved {len(templates_data)} templates to {output_file}")
    
    def validate_template_syntax(self, template_string: str) -> List[str]:
        """
        Validate template syntax and return list of variables.
        
        Args:
            template_string: Template string to validate
            
        Returns:
            List of variable names found in template
        """
        # Find all {variable} patterns
        pattern = r'\{(\w+)\}'
        variables = re.findall(pattern, template_string)
        
        # Validate balanced braces
        if template_string.count('{') != template_string.count('}'):
            raise ValueError("Unbalanced braces in template")
        
        return list(set(variables))
    
    def preview_template(
        self,
        template_name: str,
        sample_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Preview a template with sample data.
        
        Args:
            template_name: Template name
            sample_data: Sample data (uses defaults if not provided)
            
        Returns:
            Preview of rendered template
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        # Generate sample data if not provided
        if not sample_data:
            sample_data = {}
            for var in template.required_variables:
                sample_data[var] = f"[{var}]"
        
        # Merge with default data
        preview_data = {**template.default_data, **sample_data}
        
        try:
            return {
                'title': template.render_title(preview_data),
                'message': template.render_message(preview_data),
                'variables_used': list(preview_data.keys()),
                'missing_variables': template.validate_data(preview_data)
            }
        except Exception as e:
            return {
                'error': str(e),
                'template_name': template_name
            }
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get template statistics."""
        channel_counts = {}
        for template in self._templates.values():
            channel = template.channel.value if template.channel else 'generic'
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        return {
            'total_templates': len(self._templates),
            'by_channel': channel_counts,
            'template_names': list(self._templates.keys())
        }