"""
Notification rule engine for event-based routing.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from .models import (
    Notification, NotificationChannel, NotificationSeverity,
    DeliveryPriority
)

logger = logging.getLogger(__name__)


class RuleOperator(Enum):
    """Rule condition operators."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


class RuleAction(Enum):
    """Rule action types."""
    SEND = "send"
    SUPPRESS = "suppress"
    ESCALATE = "escalate"
    DELAY = "delay"
    TRANSFORM = "transform"
    ROUTE = "route"


@dataclass
class RuleCondition:
    """Individual rule condition."""
    field: str  # Field path (e.g., "event_type", "data.error_count")
    operator: RuleOperator
    value: Any
    case_sensitive: bool = True
    
    def evaluate(self, data: Dict[str, Any]) -> bool:
        """
        Evaluate condition against data.
        
        Args:
            data: Data to evaluate against
            
        Returns:
            True if condition matches
        """
        # Get field value using dot notation
        field_value = self._get_field_value(data, self.field)
        
        # Handle EXISTS/NOT_EXISTS operators
        if self.operator == RuleOperator.EXISTS:
            return field_value is not None
        elif self.operator == RuleOperator.NOT_EXISTS:
            return field_value is None
        
        # Return False if field doesn't exist for other operators
        if field_value is None:
            return False
        
        # Convert to string for string operations if needed
        if self.operator in [RuleOperator.CONTAINS, RuleOperator.NOT_CONTAINS,
                           RuleOperator.STARTS_WITH, RuleOperator.ENDS_WITH,
                           RuleOperator.REGEX]:
            field_value = str(field_value)
            compare_value = str(self.value)
            
            if not self.case_sensitive:
                field_value = field_value.lower()
                compare_value = compare_value.lower()
        else:
            compare_value = self.value
        
        # Evaluate based on operator
        try:
            if self.operator == RuleOperator.EQUALS:
                return field_value == compare_value
            
            elif self.operator == RuleOperator.NOT_EQUALS:
                return field_value != compare_value
            
            elif self.operator == RuleOperator.CONTAINS:
                return compare_value in field_value
            
            elif self.operator == RuleOperator.NOT_CONTAINS:
                return compare_value not in field_value
            
            elif self.operator == RuleOperator.STARTS_WITH:
                return field_value.startswith(compare_value)
            
            elif self.operator == RuleOperator.ENDS_WITH:
                return field_value.endswith(compare_value)
            
            elif self.operator == RuleOperator.GREATER_THAN:
                return float(field_value) > float(compare_value)
            
            elif self.operator == RuleOperator.LESS_THAN:
                return float(field_value) < float(compare_value)
            
            elif self.operator == RuleOperator.GREATER_EQUAL:
                return float(field_value) >= float(compare_value)
            
            elif self.operator == RuleOperator.LESS_EQUAL:
                return float(field_value) <= float(compare_value)
            
            elif self.operator == RuleOperator.IN:
                return field_value in compare_value
            
            elif self.operator == RuleOperator.NOT_IN:
                return field_value not in compare_value
            
            elif self.operator == RuleOperator.REGEX:
                pattern = re.compile(compare_value, re.IGNORECASE if not self.case_sensitive else 0)
                return bool(pattern.search(field_value))
            
            else:
                logger.warning(f"Unknown operator: {self.operator}")
                return False
        
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False
    
    def _get_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested dict using dot notation."""
        parts = field_path.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value


@dataclass
class NotificationRule:
    """Notification routing rule."""
    id: str
    name: str
    description: str = ""
    enabled: bool = True
    
    # Conditions (all must match)
    conditions: List[RuleCondition] = field(default_factory=list)
    
    # Actions to take
    action: RuleAction = RuleAction.SEND
    channels: List[NotificationChannel] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    
    # Modifications
    severity_override: Optional[NotificationSeverity] = None
    priority_override: Optional[DeliveryPriority] = None
    template_override: Optional[str] = None
    delay_seconds: int = 0
    
    # Rate limiting
    rate_limit_count: Optional[int] = None
    rate_limit_window: Optional[int] = None  # seconds
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_matched: Optional[datetime] = None
    match_count: int = 0
    
    # Internal state
    _rate_limit_tracker: Dict[str, List[datetime]] = field(default_factory=dict, init=False)
    
    def matches(self, event_data: Dict[str, Any]) -> bool:
        """
        Check if rule matches the event data.
        
        Args:
            event_data: Event data to match against
            
        Returns:
            True if all conditions match
        """
        if not self.enabled:
            return False
        
        # All conditions must match (AND logic)
        for condition in self.conditions:
            if not condition.evaluate(event_data):
                return False
        
        # Check rate limit
        if self.rate_limit_count and self.rate_limit_window:
            if not self._check_rate_limit():
                logger.info(f"Rule {self.name} rate limit exceeded")
                return False
        
        # Update match tracking
        self.last_matched = datetime.now()
        self.match_count += 1
        
        return True
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit allows this match."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.rate_limit_window)
        
        # Clean old entries
        key = "default"  # Could be per-source or per-recipient
        if key not in self._rate_limit_tracker:
            self._rate_limit_tracker[key] = []
        
        # Remove old timestamps
        self._rate_limit_tracker[key] = [
            ts for ts in self._rate_limit_tracker[key]
            if ts > window_start
        ]
        
        # Check count
        if len(self._rate_limit_tracker[key]) >= self.rate_limit_count:
            return False
        
        # Add current timestamp
        self._rate_limit_tracker[key].append(now)
        return True
    
    def apply_to_notification(self, notification: Notification) -> Notification:
        """
        Apply rule modifications to notification.
        
        Args:
            notification: Original notification
            
        Returns:
            Modified notification
        """
        # Apply severity override
        if self.severity_override:
            notification.severity = self.severity_override
        
        # Apply priority override
        if self.priority_override:
            notification.priority = self.priority_override
        
        # Apply template override
        if self.template_override:
            notification.template_name = self.template_override
        
        # Apply delay
        if self.delay_seconds > 0:
            notification.delay_seconds = self.delay_seconds
        
        # Add or override channels
        if self.channels:
            notification.channels = self.channels
        
        # Add recipients
        if self.recipients:
            notification.recipients.extend(self.recipients)
            # Remove duplicates
            notification.recipients = list(set(notification.recipients))
        
        return notification
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'enabled': self.enabled,
            'conditions': [
                {
                    'field': c.field,
                    'operator': c.operator.value,
                    'value': c.value,
                    'case_sensitive': c.case_sensitive
                }
                for c in self.conditions
            ],
            'action': self.action.value,
            'channels': [ch.value for ch in self.channels],
            'recipients': self.recipients,
            'severity_override': self.severity_override.value if self.severity_override else None,
            'priority_override': self.priority_override.value if self.priority_override else None,
            'template_override': self.template_override,
            'delay_seconds': self.delay_seconds,
            'rate_limit_count': self.rate_limit_count,
            'rate_limit_window': self.rate_limit_window,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_matched': self.last_matched.isoformat() if self.last_matched else None,
            'match_count': self.match_count
        }


class NotificationRules:
    """
    Notification rule engine for event-based routing.
    
    Manages rules and applies them to incoming events.
    """
    
    def __init__(self):
        """Initialize rule engine."""
        self._rules: Dict[str, NotificationRule] = {}
        self._rule_order: List[str] = []  # Ordered rule IDs
        self._stats = {
            'total_evaluations': 0,
            'total_matches': 0,
            'rules_matched': {}
        }
        
        logger.info("NotificationRules engine initialized")
    
    def add_rule(self, rule: NotificationRule, position: Optional[int] = None):
        """
        Add a notification rule.
        
        Args:
            rule: Rule to add
            position: Position in rule order (None for end)
        """
        self._rules[rule.id] = rule
        
        if position is not None:
            self._rule_order.insert(position, rule.id)
        else:
            self._rule_order.append(rule.id)
        
        logger.info(f"Added rule: {rule.name} (ID: {rule.id})")
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove a notification rule.
        
        Args:
            rule_id: Rule ID to remove
            
        Returns:
            True if removed
        """
        if rule_id in self._rules:
            del self._rules[rule_id]
            self._rule_order.remove(rule_id)
            logger.info(f"Removed rule: {rule_id}")
            return True
        
        return False
    
    def get_rule(self, rule_id: str) -> Optional[NotificationRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)
    
    def get_all_rules(self) -> List[NotificationRule]:
        """Get all rules in order."""
        return [self._rules[rule_id] for rule_id in self._rule_order if rule_id in self._rules]
    
    def evaluate_event(
        self,
        event_data: Dict[str, Any],
        stop_on_first_match: bool = False
    ) -> List[NotificationRule]:
        """
        Evaluate event against all rules.
        
        Args:
            event_data: Event data to evaluate
            stop_on_first_match: Stop after first matching rule
            
        Returns:
            List of matching rules
        """
        self._stats['total_evaluations'] += 1
        matching_rules = []
        
        for rule_id in self._rule_order:
            if rule_id not in self._rules:
                continue
            
            rule = self._rules[rule_id]
            
            try:
                if rule.matches(event_data):
                    matching_rules.append(rule)
                    self._stats['total_matches'] += 1
                    self._stats['rules_matched'][rule_id] = \
                        self._stats['rules_matched'].get(rule_id, 0) + 1
                    
                    logger.debug(f"Rule matched: {rule.name}")
                    
                    if stop_on_first_match:
                        break
            
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {str(e)}")
        
        return matching_rules
    
    def create_notifications_from_event(
        self,
        event_data: Dict[str, Any],
        base_notification: Optional[Notification] = None
    ) -> List[Notification]:
        """
        Create notifications based on matching rules.
        
        Args:
            event_data: Event data
            base_notification: Base notification to modify
            
        Returns:
            List of notifications to send
        """
        # Get matching rules
        matching_rules = self.evaluate_event(event_data)
        
        if not matching_rules:
            logger.debug("No rules matched for event")
            return []
        
        notifications = []
        suppressed = False
        
        for rule in matching_rules:
            # Check for suppress action
            if rule.action == RuleAction.SUPPRESS:
                logger.info(f"Notification suppressed by rule: {rule.name}")
                suppressed = True
                break
            
            # Create or modify notification
            if base_notification:
                notification = Notification(**base_notification.__dict__)
            else:
                # Create notification from event data
                notification = self._create_notification_from_event(event_data)
            
            # Apply rule modifications
            notification = rule.apply_to_notification(notification)
            
            # Handle different actions
            if rule.action == RuleAction.SEND:
                notifications.append(notification)
            
            elif rule.action == RuleAction.ESCALATE:
                # Escalate severity and priority
                notification.severity = NotificationSeverity.CRITICAL
                notification.priority = DeliveryPriority.URGENT
                notifications.append(notification)
            
            elif rule.action == RuleAction.DELAY:
                # Delay is already applied in apply_to_notification
                notifications.append(notification)
            
            elif rule.action == RuleAction.TRANSFORM:
                # Custom transformation would be applied here
                notifications.append(notification)
            
            elif rule.action == RuleAction.ROUTE:
                # Routing is handled by channel/recipient overrides
                notifications.append(notification)
        
        return [] if suppressed else notifications
    
    def _create_notification_from_event(self, event_data: Dict[str, Any]) -> Notification:
        """Create a notification from event data."""
        return Notification(
            title=event_data.get('title', 'System Event'),
            message=event_data.get('message', 'An event occurred'),
            severity=NotificationSeverity(event_data.get('severity', 'info')),
            source=event_data.get('source', 'system'),
            event_type=event_data.get('event_type'),
            data=event_data.get('data', {}),
            channels=[NotificationChannel.TOAST],  # Default channel
            recipients=[]
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rule engine statistics."""
        return {
            'total_rules': len(self._rules),
            'enabled_rules': sum(1 for r in self._rules.values() if r.enabled),
            'total_evaluations': self._stats['total_evaluations'],
            'total_matches': self._stats['total_matches'],
            'match_rate': (
                self._stats['total_matches'] / self._stats['total_evaluations']
                if self._stats['total_evaluations'] > 0 else 0
            ),
            'top_matched_rules': sorted(
                [
                    {
                        'rule_id': rule_id,
                        'rule_name': self._rules[rule_id].name if rule_id in self._rules else 'Unknown',
                        'matches': count
                    }
                    for rule_id, count in self._stats['rules_matched'].items()
                ],
                key=lambda x: x['matches'],
                reverse=True
            )[:10]
        }
    
    def load_rules_from_config(self, config: List[Dict[str, Any]]):
        """Load rules from configuration."""
        for rule_config in config:
            try:
                # Create conditions
                conditions = []
                for cond_config in rule_config.get('conditions', []):
                    condition = RuleCondition(
                        field=cond_config['field'],
                        operator=RuleOperator(cond_config['operator']),
                        value=cond_config['value'],
                        case_sensitive=cond_config.get('case_sensitive', True)
                    )
                    conditions.append(condition)
                
                # Create rule
                rule = NotificationRule(
                    id=rule_config['id'],
                    name=rule_config['name'],
                    description=rule_config.get('description', ''),
                    enabled=rule_config.get('enabled', True),
                    conditions=conditions,
                    action=RuleAction(rule_config.get('action', 'send')),
                    channels=[
                        NotificationChannel(ch) 
                        for ch in rule_config.get('channels', [])
                    ],
                    recipients=rule_config.get('recipients', []),
                    severity_override=NotificationSeverity(rule_config['severity_override'])
                        if 'severity_override' in rule_config else None,
                    priority_override=DeliveryPriority(rule_config['priority_override'])
                        if 'priority_override' in rule_config else None,
                    template_override=rule_config.get('template_override'),
                    delay_seconds=rule_config.get('delay_seconds', 0),
                    rate_limit_count=rule_config.get('rate_limit_count'),
                    rate_limit_window=rule_config.get('rate_limit_window')
                )
                
                self.add_rule(rule)
                
            except Exception as e:
                logger.error(f"Error loading rule {rule_config.get('id', 'unknown')}: {str(e)}")
    
    def export_rules(self) -> List[Dict[str, Any]]:
        """Export rules to configuration format."""
        return [rule.to_dict() for rule in self.get_all_rules()]