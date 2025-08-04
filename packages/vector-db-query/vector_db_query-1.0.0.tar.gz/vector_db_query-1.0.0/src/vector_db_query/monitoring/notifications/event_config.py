"""
Event configuration system for the monitoring dashboard.

This module provides comprehensive event configuration management,
allowing users to define when, how, and to whom notifications are sent.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict, field
from threading import RLock
from enum import Enum
from pathlib import Path
import uuid
import re

from .models import NotificationSeverity, NotificationChannel
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events that can trigger notifications."""
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"
    SERVICE_RESTART = "service_restart"
    SERVICE_FAILURE = "service_failure"
    QUEUE_FULL = "queue_full"
    QUEUE_EMPTY = "queue_empty"
    QUEUE_STALLED = "queue_stalled"
    PROCESSING_ERROR = "processing_error"
    HIGH_CPU_USAGE = "high_cpu_usage"
    HIGH_MEMORY_USAGE = "high_memory_usage"
    LOW_DISK_SPACE = "low_disk_space"
    CONNECTION_LOST = "connection_lost"
    CONNECTION_RESTORED = "connection_restored"
    SCHEDULE_EXECUTED = "schedule_executed"
    SCHEDULE_FAILED = "schedule_failed"
    BACKUP_COMPLETED = "backup_completed"
    BACKUP_FAILED = "backup_failed"
    MAINTENANCE_START = "maintenance_start"
    MAINTENANCE_END = "maintenance_end"
    CUSTOM_EVENT = "custom_event"


class TriggerCondition(Enum):
    """Conditions for triggering events."""
    ALWAYS = "always"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    VALUE_CHANGED = "value_changed"
    TIME_BASED = "time_based"
    COUNT_BASED = "count_based"
    PATTERN_MATCH = "pattern_match"


class EventPriority(Enum):
    """Priority levels for events."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EventCondition:
    """Condition that triggers an event."""
    id: str
    condition_type: TriggerCondition
    parameters: Dict[str, Any]
    description: str
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate if condition is met."""
        try:
            if not self.is_active:
                return False
            
            if self.condition_type == TriggerCondition.ALWAYS:
                return True
            
            elif self.condition_type == TriggerCondition.THRESHOLD_EXCEEDED:
                value = context.get(self.parameters.get('metric'))
                threshold = self.parameters.get('threshold')
                if value is not None and threshold is not None:
                    return float(value) > float(threshold)
            
            elif self.condition_type == TriggerCondition.VALUE_CHANGED:
                current = context.get(self.parameters.get('metric'))
                previous = context.get(f"{self.parameters.get('metric')}_previous")
                return current != previous
            
            elif self.condition_type == TriggerCondition.TIME_BASED:
                now = datetime.now()
                if 'schedule' in self.parameters:
                    # Simple time-based check (could be expanded with cron-like functionality)
                    schedule = self.parameters['schedule']
                    if schedule == 'hourly':
                        return now.minute == 0
                    elif schedule == 'daily':
                        return now.hour == 0 and now.minute == 0
            
            elif self.condition_type == TriggerCondition.COUNT_BASED:
                count = context.get(self.parameters.get('metric'), 0)
                target_count = self.parameters.get('count', 0)
                return int(count) >= int(target_count)
            
            elif self.condition_type == TriggerCondition.PATTERN_MATCH:
                text = str(context.get(self.parameters.get('field', ''), ''))
                pattern = self.parameters.get('pattern', '')
                if pattern:
                    return bool(re.search(pattern, text))
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating condition {self.id}: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'condition_type': self.condition_type.value,
            'parameters': self.parameters,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class NotificationRule:
    """Rule defining how notifications are sent for events."""
    id: str
    name: str
    description: str
    channels: List[NotificationChannel]
    severity: NotificationSeverity
    priority: EventPriority
    template_ids: Dict[str, str]  # channel_name -> template_id
    rate_limit: Optional[Dict[str, Any]] = None  # rate limiting config
    quiet_hours: Optional[Dict[str, Any]] = None  # quiet hours config
    escalation: Optional[Dict[str, Any]] = None  # escalation rules
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.template_ids is None:
            self.template_ids = {}
    
    def should_send_notification(self, last_sent: Optional[datetime] = None) -> bool:
        """Check if notification should be sent based on rate limiting."""
        if not self.is_active:
            return False
        
        # Check quiet hours
        if self.quiet_hours:
            now = datetime.now()
            start_hour = self.quiet_hours.get('start_hour', 0)
            end_hour = self.quiet_hours.get('end_hour', 0)
            
            if start_hour != end_hour:
                current_hour = now.hour
                if start_hour < end_hour:
                    if start_hour <= current_hour < end_hour:
                        return False
                else:  # Spans midnight
                    if current_hour >= start_hour or current_hour < end_hour:
                        return False
        
        # Check rate limiting
        if self.rate_limit and last_sent:
            limit_type = self.rate_limit.get('type', 'minutes')
            limit_value = self.rate_limit.get('value', 5)
            
            if limit_type == 'minutes':
                time_diff = datetime.now() - last_sent
                if time_diff < timedelta(minutes=limit_value):
                    return False
            elif limit_type == 'hours':
                time_diff = datetime.now() - last_sent
                if time_diff < timedelta(hours=limit_value):
                    return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'channels': [ch.value for ch in self.channels],
            'severity': self.severity.value,
            'priority': self.priority.value,
            'template_ids': self.template_ids,
            'rate_limit': self.rate_limit,
            'quiet_hours': self.quiet_hours,
            'escalation': self.escalation,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class EventConfiguration:
    """Complete event configuration linking events, conditions, and rules."""
    id: str
    name: str
    description: str
    event_type: EventType
    conditions: List[EventCondition]
    notification_rules: List[NotificationRule]
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        """Check if event should trigger based on conditions."""
        if not self.is_active:
            return False
        
        # All conditions must be met
        for condition in self.conditions:
            if not condition.evaluate(context):
                return False
        
        return True
    
    def get_applicable_rules(self, context: Dict[str, Any]) -> List[NotificationRule]:
        """Get notification rules that should be applied."""
        applicable_rules = []
        
        for rule in self.notification_rules:
            if rule.should_send_notification():
                applicable_rules.append(rule)
        
        return applicable_rules
    
    def record_trigger(self):
        """Record that this event was triggered."""
        self.last_triggered = datetime.now()
        self.trigger_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'event_type': self.event_type.value,
            'conditions': [c.to_dict() for c in self.conditions],
            'notification_rules': [r.to_dict() for r in self.notification_rules],
            'tags': self.tags,
            'metadata': self.metadata,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count
        }


class EventConfigurationService:
    """
    Service for managing event configurations.
    
    Provides comprehensive event configuration management including
    conditions, rules, templates, and notification routing.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize event configuration service.
        
        Args:
            storage_path: Path for configuration persistence
        """
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # Storage
        self.storage_path = Path(storage_path) if storage_path else Path.home() / ".ansera" / "events"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.configs_file = self.storage_path / "event_configurations.json"
        self.history_file = self.storage_path / "event_history.json"
        self.stats_file = self.storage_path / "event_statistics.json"
        
        # Data stores
        self._configurations: Dict[str, EventConfiguration] = {}
        self._event_history: List[Dict[str, Any]] = []
        self._statistics: Dict[str, Any] = {}
        
        # Load persisted data
        self._load_configurations()
        self._load_history()
        self._load_statistics()
        
        # Initialize default configurations if none exist
        if not self._configurations:
            self._create_default_configurations()
        
        logger.info(f"EventConfigurationService initialized with {len(self._configurations)} configurations")
    
    def add_configuration(self, config: EventConfiguration) -> bool:
        """
        Add event configuration.
        
        Args:
            config: Event configuration to add
            
        Returns:
            True if added successfully
        """
        with self._lock:
            try:
                self._configurations[config.id] = config
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.CREATE,
                    description=f"Event configuration added: {config.name}",
                    details={
                        'config_id': config.id,
                        'event_type': config.event_type.value,
                        'conditions_count': len(config.conditions),
                        'rules_count': len(config.notification_rules)
                    }
                )
                
                # Save configurations
                self._save_configurations()
                
                logger.info(f"Event configuration added: {config.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add event configuration: {e}")
                return False
    
    def update_configuration(self, config: EventConfiguration) -> bool:
        """
        Update event configuration.
        
        Args:
            config: Updated event configuration
            
        Returns:
            True if updated successfully
        """
        with self._lock:
            try:
                if config.id not in self._configurations:
                    logger.warning(f"Event configuration not found: {config.id}")
                    return False
                
                old_config = self._configurations[config.id]
                self._configurations[config.id] = config
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description=f"Event configuration updated: {config.name}",
                    details={
                        'config_id': config.id,
                        'old_active': old_config.is_active,
                        'new_active': config.is_active
                    }
                )
                
                # Save configurations
                self._save_configurations()
                
                logger.info(f"Event configuration updated: {config.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to update event configuration: {e}")
                return False
    
    def remove_configuration(self, config_id: str) -> bool:
        """
        Remove event configuration.
        
        Args:
            config_id: Configuration ID to remove
            
        Returns:
            True if removed successfully
        """
        with self._lock:
            try:
                if config_id not in self._configurations:
                    logger.warning(f"Event configuration not found: {config_id}")
                    return False
                
                config = self._configurations[config_id]
                del self._configurations[config_id]
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.DELETE,
                    description=f"Event configuration removed: {config.name}",
                    details={
                        'config_id': config_id,
                        'event_type': config.event_type.value
                    }
                )
                
                # Save configurations
                self._save_configurations()
                
                logger.info(f"Event configuration removed: {config.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to remove event configuration: {e}")
                return False
    
    def process_event(self, event_type: EventType, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process an event and return applicable notifications.
        
        Args:
            event_type: Type of event that occurred
            context: Event context data
            
        Returns:
            List of notification specifications
        """
        with self._lock:
            notifications = []
            
            try:
                # Find matching configurations
                matching_configs = [
                    config for config in self._configurations.values()
                    if config.event_type == event_type and config.should_trigger(context)
                ]
                
                for config in matching_configs:
                    # Record trigger
                    config.record_trigger()
                    
                    # Get applicable rules
                    applicable_rules = config.get_applicable_rules(context)
                    
                    for rule in applicable_rules:
                        notification_spec = {
                            'config_id': config.id,
                            'config_name': config.name,
                            'event_type': event_type.value,
                            'rule_id': rule.id,
                            'rule_name': rule.name,
                            'channels': [ch.value for ch in rule.channels],
                            'severity': rule.severity.value,
                            'priority': rule.priority.value,
                            'template_ids': rule.template_ids,
                            'context': context,
                            'timestamp': datetime.now().isoformat()
                        }
                        notifications.append(notification_spec)
                
                # Record event in history
                if matching_configs or notifications:
                    self._record_event_history(event_type, context, len(notifications))
                
                # Update statistics
                self._update_statistics(event_type, len(notifications))
                
                # Save data
                self._save_configurations()
                self._save_history()
                self._save_statistics()
                
                logger.info(f"Processed event {event_type.value}: {len(notifications)} notifications generated")
                return notifications
                
            except Exception as e:
                logger.error(f"Failed to process event {event_type.value}: {e}")
                return []
    
    def get_configurations(self, event_type: Optional[EventType] = None, 
                          active_only: bool = True) -> Dict[str, EventConfiguration]:
        """Get event configurations with optional filtering."""
        with self._lock:
            configs = {}
            for config_id, config in self._configurations.items():
                if active_only and not config.is_active:
                    continue
                if event_type and config.event_type != event_type:
                    continue
                configs[config_id] = config
            return configs
    
    def get_configuration(self, config_id: str) -> Optional[EventConfiguration]:
        """Get specific event configuration."""
        with self._lock:
            return self._configurations.get(config_id)
    
    def get_event_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent event history."""
        with self._lock:
            return self._event_history[-limit:] if self._event_history else []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event processing statistics."""
        with self._lock:
            return self._statistics.copy()
    
    def validate_configuration(self, config: EventConfiguration) -> List[str]:
        """
        Validate event configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            # Basic validation
            if not config.name.strip():
                errors.append("Configuration name is required")
            
            if not config.conditions:
                errors.append("At least one condition is required")
            
            if not config.notification_rules:
                errors.append("At least one notification rule is required")
            
            # Validate conditions
            for condition in config.conditions:
                if condition.condition_type == TriggerCondition.THRESHOLD_EXCEEDED:
                    if 'metric' not in condition.parameters or 'threshold' not in condition.parameters:
                        errors.append(f"Condition {condition.id}: threshold conditions require 'metric' and 'threshold' parameters")
                
                elif condition.condition_type == TriggerCondition.PATTERN_MATCH:
                    if 'field' not in condition.parameters or 'pattern' not in condition.parameters:
                        errors.append(f"Condition {condition.id}: pattern conditions require 'field' and 'pattern' parameters")
            
            # Validate notification rules
            for rule in config.notification_rules:
                if not rule.channels:
                    errors.append(f"Rule {rule.id}: at least one notification channel is required")
        
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors
    
    def _create_default_configurations(self):
        """Create default event configurations."""
        default_configs = [
            # Service failure configuration
            EventConfiguration(
                id=str(uuid.uuid4()),
                name="Service Failure Alert",
                description="Alert when any service fails or stops unexpectedly",
                event_type=EventType.SERVICE_FAILURE,
                conditions=[
                    EventCondition(
                        id=str(uuid.uuid4()),
                        condition_type=TriggerCondition.ALWAYS,
                        parameters={},
                        description="Always trigger on service failure"
                    )
                ],
                notification_rules=[
                    NotificationRule(
                        id=str(uuid.uuid4()),
                        name="Critical Service Failure",
                        description="Send critical notifications for service failures",
                        channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.TOAST],
                        severity=NotificationSeverity.CRITICAL,
                        priority=EventPriority.CRITICAL,
                        template_ids={
                            'email': 'service_failure_email',
                            'push': 'service_failure_push',
                            'toast': 'service_failure_toast'
                        },
                        rate_limit={'type': 'minutes', 'value': 5}
                    )
                ],
                tags=['critical', 'service', 'infrastructure']
            ),
            
            # High CPU usage configuration
            EventConfiguration(
                id=str(uuid.uuid4()),
                name="High CPU Usage Warning",
                description="Alert when CPU usage exceeds threshold",
                event_type=EventType.HIGH_CPU_USAGE,
                conditions=[
                    EventCondition(
                        id=str(uuid.uuid4()),
                        condition_type=TriggerCondition.THRESHOLD_EXCEEDED,
                        parameters={'metric': 'cpu_percent', 'threshold': 80},
                        description="CPU usage > 80%"
                    )
                ],
                notification_rules=[
                    NotificationRule(
                        id=str(uuid.uuid4()),
                        name="High CPU Warning",
                        description="Warning notification for high CPU usage",
                        channels=[NotificationChannel.EMAIL, NotificationChannel.TOAST],
                        severity=NotificationSeverity.WARNING,
                        priority=EventPriority.HIGH,
                        template_ids={
                            'email': 'high_cpu_email',
                            'toast': 'high_cpu_toast'
                        },
                        rate_limit={'type': 'minutes', 'value': 15}
                    )
                ],
                tags=['performance', 'cpu', 'monitoring']
            ),
            
            # Queue full configuration
            EventConfiguration(
                id=str(uuid.uuid4()),
                name="Queue Full Alert",
                description="Alert when processing queue is full",
                event_type=EventType.QUEUE_FULL,
                conditions=[
                    EventCondition(
                        id=str(uuid.uuid4()),
                        condition_type=TriggerCondition.THRESHOLD_EXCEEDED,
                        parameters={'metric': 'queue_size', 'threshold': 1000},
                        description="Queue size > 1000"
                    )
                ],
                notification_rules=[
                    NotificationRule(
                        id=str(uuid.uuid4()),
                        name="Queue Full Warning",
                        description="Warning when queue approaches capacity",
                        channels=[NotificationChannel.EMAIL, NotificationChannel.PUSH],
                        severity=NotificationSeverity.WARNING,
                        priority=EventPriority.HIGH,
                        template_ids={
                            'email': 'queue_full_email',
                            'push': 'queue_full_push'
                        },
                        rate_limit={'type': 'minutes', 'value': 10}
                    )
                ],
                tags=['queue', 'performance', 'capacity']
            ),
            
            # Daily summary configuration
            EventConfiguration(
                id=str(uuid.uuid4()),
                name="Daily System Summary",
                description="Daily summary of system status and metrics",
                event_type=EventType.CUSTOM_EVENT,
                conditions=[
                    EventCondition(
                        id=str(uuid.uuid4()),
                        condition_type=TriggerCondition.TIME_BASED,
                        parameters={'schedule': 'daily'},
                        description="Daily at midnight"
                    )
                ],
                notification_rules=[
                    NotificationRule(
                        id=str(uuid.uuid4()),
                        name="Daily Summary",
                        description="Daily system summary report",
                        channels=[NotificationChannel.EMAIL],
                        severity=NotificationSeverity.INFO,
                        priority=EventPriority.LOW,
                        template_ids={'email': 'daily_summary_email'},
                        quiet_hours={'start_hour': 22, 'end_hour': 8}
                    )
                ],
                tags=['summary', 'daily', 'report']
            )
        ]
        
        for config in default_configs:
            self._configurations[config.id] = config
        
        self._save_configurations()
        logger.info("Created default event configurations")
    
    def _record_event_history(self, event_type: EventType, context: Dict[str, Any], notification_count: int):
        """Record event in history."""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type.value,
            'context': context,
            'notification_count': notification_count
        }
        
        self._event_history.append(history_entry)
        
        # Keep only recent history (last 1000 entries)
        if len(self._event_history) > 1000:
            self._event_history = self._event_history[-1000:]
    
    def _update_statistics(self, event_type: EventType, notification_count: int):
        """Update event processing statistics."""
        if 'total_events' not in self._statistics:
            self._statistics['total_events'] = 0
        if 'total_notifications' not in self._statistics:
            self._statistics['total_notifications'] = 0
        if 'events_by_type' not in self._statistics:
            self._statistics['events_by_type'] = {}
        
        self._statistics['total_events'] += 1
        self._statistics['total_notifications'] += notification_count
        
        event_type_str = event_type.value
        if event_type_str not in self._statistics['events_by_type']:
            self._statistics['events_by_type'][event_type_str] = 0
        self._statistics['events_by_type'][event_type_str] += 1
        
        self._statistics['last_updated'] = datetime.now().isoformat()
    
    # Storage methods
    def _save_configurations(self):
        """Save configurations to storage."""
        try:
            data = {cid: config.to_dict() for cid, config in self._configurations.items()}
            with open(self.configs_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save event configurations: {e}")
    
    def _load_configurations(self):
        """Load configurations from storage."""
        try:
            if self.configs_file.exists():
                with open(self.configs_file, 'r') as f:
                    data = json.load(f)
                
                for cid, config_data in data.items():
                    # Reconstruct objects
                    config_data['event_type'] = EventType(config_data['event_type'])
                    config_data['created_at'] = datetime.fromisoformat(config_data['created_at'])
                    if config_data['last_triggered']:
                        config_data['last_triggered'] = datetime.fromisoformat(config_data['last_triggered'])
                    
                    # Reconstruct conditions
                    conditions = []
                    for cond_data in config_data['conditions']:
                        cond_data['condition_type'] = TriggerCondition(cond_data['condition_type'])
                        cond_data['created_at'] = datetime.fromisoformat(cond_data['created_at'])
                        conditions.append(EventCondition(**cond_data))
                    config_data['conditions'] = conditions
                    
                    # Reconstruct notification rules
                    rules = []
                    for rule_data in config_data['notification_rules']:
                        rule_data['channels'] = [NotificationChannel(ch) for ch in rule_data['channels']]
                        rule_data['severity'] = NotificationSeverity(rule_data['severity'])
                        rule_data['priority'] = EventPriority(rule_data['priority'])
                        rule_data['created_at'] = datetime.fromisoformat(rule_data['created_at'])
                        rules.append(NotificationRule(**rule_data))
                    config_data['notification_rules'] = rules
                    
                    config = EventConfiguration(**config_data)
                    self._configurations[cid] = config
                
                logger.info(f"Loaded {len(self._configurations)} event configurations")
        except Exception as e:
            logger.error(f"Failed to load event configurations: {e}")
    
    def _save_history(self):
        """Save event history to storage."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self._event_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save event history: {e}")
    
    def _load_history(self):
        """Load event history from storage."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self._event_history = json.load(f)
                logger.info(f"Loaded {len(self._event_history)} event history entries")
        except Exception as e:
            logger.error(f"Failed to load event history: {e}")
    
    def _save_statistics(self):
        """Save statistics to storage."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self._statistics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save event statistics: {e}")
    
    def _load_statistics(self):
        """Load statistics from storage."""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    self._statistics = json.load(f)
                logger.info("Loaded event statistics")
        except Exception as e:
            logger.error(f"Failed to load event statistics: {e}")


# Singleton instance
_event_config_service: Optional[EventConfigurationService] = None
_service_lock = RLock()


def get_event_config_service(storage_path: Optional[str] = None) -> EventConfigurationService:
    """
    Get singleton event configuration service instance.
    
    Args:
        storage_path: Storage path (only used on first call)
        
    Returns:
        EventConfigurationService instance
    """
    global _event_config_service
    
    with _service_lock:
        if _event_config_service is None:
            _event_config_service = EventConfigurationService(storage_path)
        
        return _event_config_service


def reset_event_config_service():
    """Reset the singleton event configuration service (mainly for testing)."""
    global _event_config_service
    
    with _service_lock:
        _event_config_service = None


# Convenience functions
def process_system_event(event_type: EventType, **context) -> List[Dict[str, Any]]:
    """Process a system event using the default service."""
    service = get_event_config_service()
    return service.process_event(event_type, context)


def trigger_service_failure_event(service_name: str, error_message: str, **extra_context):
    """Trigger a service failure event."""
    context = {
        'service_name': service_name,
        'error_message': error_message,
        'timestamp': datetime.now().isoformat(),
        **extra_context
    }
    return process_system_event(EventType.SERVICE_FAILURE, **context)


def trigger_high_cpu_event(cpu_percent: float, **extra_context):
    """Trigger a high CPU usage event."""
    context = {
        'cpu_percent': cpu_percent,
        'timestamp': datetime.now().isoformat(),
        **extra_context
    }
    return process_system_event(EventType.HIGH_CPU_USAGE, **context)


def trigger_queue_full_event(queue_size: int, **extra_context):
    """Trigger a queue full event."""
    context = {
        'queue_size': queue_size,
        'timestamp': datetime.now().isoformat(),
        **extra_context
    }
    return process_system_event(EventType.QUEUE_FULL, **context)