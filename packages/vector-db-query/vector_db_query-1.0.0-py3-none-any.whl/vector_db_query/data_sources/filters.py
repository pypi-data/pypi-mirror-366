"""Selective processing filters for data sources."""

import re
import fnmatch
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import get_logger

logger = get_logger(__name__)


class FilterType(Enum):
    """Types of filters available."""
    PATTERN = "pattern"
    DATE_RANGE = "date_range"
    SIZE = "size"
    SENDER = "sender"
    SUBJECT = "subject"
    CONTENT = "content"
    CUSTOM = "custom"
    MANUAL_EXCLUDE = "manual_exclude"


class FilterAction(Enum):
    """Actions to take when filter matches."""
    EXCLUDE = "exclude"
    INCLUDE = "include"
    TAG = "tag"


@dataclass
class FilterRule:
    """Represents a single filter rule."""
    name: str
    type: FilterType
    action: FilterAction
    pattern: Optional[str] = None
    value: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
    enabled: bool = True
    priority: int = 0  # Higher priority rules are evaluated first


class SelectiveProcessor:
    """Manages selective processing filters for data sources."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize selective processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.rules: List[FilterRule] = []
        self.manual_exclusions: Dict[str, List[str]] = {
            'gmail': [],
            'fireflies': [],
            'google_drive': []
        }
        self._load_rules()
        self._custom_filters: Dict[str, Callable] = {}
    
    def _load_rules(self):
        """Load filter rules from configuration."""
        rules_config = self.config.get('filter_rules', [])
        
        for rule_data in rules_config:
            try:
                rule = FilterRule(
                    name=rule_data['name'],
                    type=FilterType(rule_data['type']),
                    action=FilterAction(rule_data.get('action', 'exclude')),
                    pattern=rule_data.get('pattern'),
                    value=rule_data.get('value'),
                    metadata=rule_data.get('metadata', {}),
                    enabled=rule_data.get('enabled', True),
                    priority=rule_data.get('priority', 0)
                )
                self.rules.append(rule)
            except Exception as e:
                logger.error(f"Failed to load rule {rule_data.get('name', 'unknown')}: {e}")
        
        # Sort rules by priority (descending)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        
        # Load manual exclusions
        exclusions = self.config.get('manual_exclusions', {})
        for source, items in exclusions.items():
            if source in self.manual_exclusions:
                self.manual_exclusions[source] = items
    
    def add_rule(self, rule: FilterRule) -> bool:
        """Add a new filter rule.
        
        Args:
            rule: Filter rule to add
            
        Returns:
            True if added successfully
        """
        try:
            # Check for duplicate names
            if any(r.name == rule.name for r in self.rules):
                logger.warning(f"Rule with name '{rule.name}' already exists")
                return False
            
            self.rules.append(rule)
            self.rules.sort(key=lambda r: r.priority, reverse=True)
            logger.info(f"Added filter rule: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add rule: {e}")
            return False
    
    def remove_rule(self, name: str) -> bool:
        """Remove a filter rule by name.
        
        Args:
            name: Name of rule to remove
            
        Returns:
            True if removed successfully
        """
        initial_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != name]
        removed = len(self.rules) < initial_count
        
        if removed:
            logger.info(f"Removed filter rule: {name}")
        else:
            logger.warning(f"Rule '{name}' not found")
        
        return removed
    
    def toggle_rule(self, name: str, enabled: Optional[bool] = None) -> bool:
        """Toggle or set rule enabled state.
        
        Args:
            name: Name of rule
            enabled: Specific state to set (None to toggle)
            
        Returns:
            True if state changed
        """
        for rule in self.rules:
            if rule.name == name:
                if enabled is None:
                    rule.enabled = not rule.enabled
                else:
                    rule.enabled = enabled
                logger.info(f"Rule '{name}' is now {'enabled' if rule.enabled else 'disabled'}")
                return True
        
        logger.warning(f"Rule '{name}' not found")
        return False
    
    def should_process(self, 
                      item: Dict[str, Any], 
                      source_type: str,
                      default_action: FilterAction = FilterAction.INCLUDE) -> bool:
        """Check if an item should be processed based on filters.
        
        Args:
            item: Item to check
            source_type: Type of data source
            default_action: Default action if no rules match
            
        Returns:
            True if item should be processed
        """
        # Check manual exclusions first
        item_id = self._get_item_id(item, source_type)
        if item_id and item_id in self.manual_exclusions.get(source_type, []):
            logger.debug(f"Item {item_id} is manually excluded")
            return False
        
        # Evaluate rules in priority order
        matched_action = None
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._evaluate_rule(rule, item, source_type):
                matched_action = rule.action
                logger.debug(f"Item matched rule '{rule.name}' with action {rule.action.value}")
                
                # For include/exclude actions, we can stop here
                if rule.action in [FilterAction.INCLUDE, FilterAction.EXCLUDE]:
                    break
                # For tag action, continue to check other rules
        
        # Determine final action
        if matched_action is None:
            matched_action = default_action
        
        return matched_action != FilterAction.EXCLUDE
    
    def _evaluate_rule(self, rule: FilterRule, item: Dict[str, Any], source_type: str) -> bool:
        """Evaluate if a rule matches an item.
        
        Args:
            rule: Filter rule
            item: Item to check
            source_type: Type of data source
            
        Returns:
            True if rule matches
        """
        try:
            if rule.type == FilterType.PATTERN:
                return self._match_pattern(rule, item, source_type)
            elif rule.type == FilterType.DATE_RANGE:
                return self._match_date_range(rule, item, source_type)
            elif rule.type == FilterType.SIZE:
                return self._match_size(rule, item, source_type)
            elif rule.type == FilterType.SENDER:
                return self._match_sender(rule, item, source_type)
            elif rule.type == FilterType.SUBJECT:
                return self._match_subject(rule, item, source_type)
            elif rule.type == FilterType.CONTENT:
                return self._match_content(rule, item, source_type)
            elif rule.type == FilterType.CUSTOM:
                return self._match_custom(rule, item, source_type)
            
        except Exception as e:
            logger.error(f"Error evaluating rule '{rule.name}': {e}")
        
        return False
    
    def _match_pattern(self, rule: FilterRule, item: Dict[str, Any], source_type: str) -> bool:
        """Match using file name or title pattern."""
        if not rule.pattern:
            return False
        
        # Get item name/title based on source type
        if source_type == 'gmail':
            target = item.get('headers', {}).get('subject', '')
        elif source_type == 'fireflies':
            target = item.get('title', '')
        elif source_type == 'google_drive':
            target = item.get('name', '')
        else:
            target = ''
        
        # Use fnmatch for glob-style patterns
        return fnmatch.fnmatch(target.lower(), rule.pattern.lower())
    
    def _match_date_range(self, rule: FilterRule, item: Dict[str, Any], source_type: str) -> bool:
        """Match based on date range."""
        if not rule.value or not isinstance(rule.value, dict):
            return False
        
        # Get item date based on source type
        item_date = None
        if source_type == 'gmail':
            date_str = item.get('date')
            if date_str:
                item_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        elif source_type == 'fireflies':
            date_str = item.get('date')
            if date_str:
                item_date = datetime.fromisoformat(date_str)
        elif source_type == 'google_drive':
            date_str = item.get('modifiedTime')
            if date_str:
                item_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        if not item_date:
            return False
        
        # Check date range
        start_date = rule.value.get('start')
        end_date = rule.value.get('end')
        
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date)
            if item_date < start_date:
                return False
        
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date)
            if item_date > end_date:
                return False
        
        return True
    
    def _match_size(self, rule: FilterRule, item: Dict[str, Any], source_type: str) -> bool:
        """Match based on file size."""
        if not rule.value:
            return False
        
        # Get item size
        item_size = 0
        if source_type == 'gmail':
            # Estimate email size from content
            item_size = len(item.get('body_text', '')) + len(item.get('body_html', ''))
            # Add attachment sizes
            for attachment in item.get('attachments', []):
                item_size += attachment.get('size', 0)
        elif source_type == 'google_drive':
            item_size = int(item.get('size', 0))
        
        # Check size condition
        if isinstance(rule.value, dict):
            min_size = rule.value.get('min', 0)
            max_size = rule.value.get('max', float('inf'))
            return min_size <= item_size <= max_size
        else:
            # Simple threshold
            return item_size >= rule.value
    
    def _match_sender(self, rule: FilterRule, item: Dict[str, Any], source_type: str) -> bool:
        """Match based on sender (email only)."""
        if source_type != 'gmail' or not rule.pattern:
            return False
        
        sender = item.get('metadata', {}).get('sender_email', '')
        return fnmatch.fnmatch(sender.lower(), rule.pattern.lower())
    
    def _match_subject(self, rule: FilterRule, item: Dict[str, Any], source_type: str) -> bool:
        """Match based on subject/title."""
        if not rule.pattern:
            return False
        
        # Get subject/title
        if source_type == 'gmail':
            subject = item.get('headers', {}).get('subject', '')
        elif source_type == 'fireflies':
            subject = item.get('title', '')
        elif source_type == 'google_drive':
            subject = item.get('name', '')
        else:
            return False
        
        # Use regex for more complex matching
        try:
            return bool(re.search(rule.pattern, subject, re.IGNORECASE))
        except re.error:
            # Fall back to simple substring match
            return rule.pattern.lower() in subject.lower()
    
    def _match_content(self, rule: FilterRule, item: Dict[str, Any], source_type: str) -> bool:
        """Match based on content."""
        if not rule.pattern:
            return False
        
        # Get content
        content = ''
        if source_type == 'gmail':
            content = item.get('body_text', '')
        elif source_type == 'fireflies':
            content = item.get('transcript', '')
        elif source_type == 'google_drive':
            content = item.get('content', '')
        
        if not content:
            return False
        
        # Use regex for content matching
        try:
            return bool(re.search(rule.pattern, content, re.IGNORECASE))
        except re.error:
            # Fall back to simple substring match
            return rule.pattern.lower() in content.lower()
    
    def _match_custom(self, rule: FilterRule, item: Dict[str, Any], source_type: str) -> bool:
        """Match using custom filter function."""
        filter_name = rule.metadata.get('filter_name') if rule.metadata else None
        if not filter_name or filter_name not in self._custom_filters:
            return False
        
        try:
            return self._custom_filters[filter_name](item, source_type, rule)
        except Exception as e:
            logger.error(f"Custom filter '{filter_name}' failed: {e}")
            return False
    
    def register_custom_filter(self, name: str, filter_func: Callable) -> bool:
        """Register a custom filter function.
        
        Args:
            name: Name of the filter
            filter_func: Function that takes (item, source_type, rule) and returns bool
            
        Returns:
            True if registered successfully
        """
        if not callable(filter_func):
            logger.error(f"Filter function '{name}' is not callable")
            return False
        
        self._custom_filters[name] = filter_func
        logger.info(f"Registered custom filter: {name}")
        return True
    
    def add_manual_exclusion(self, source_type: str, item_id: str) -> bool:
        """Add an item to manual exclusion list.
        
        Args:
            source_type: Type of data source
            item_id: ID of item to exclude
            
        Returns:
            True if added successfully
        """
        if source_type not in self.manual_exclusions:
            logger.error(f"Invalid source type: {source_type}")
            return False
        
        if item_id not in self.manual_exclusions[source_type]:
            self.manual_exclusions[source_type].append(item_id)
            logger.info(f"Added {item_id} to {source_type} exclusion list")
            return True
        
        return False
    
    def remove_manual_exclusion(self, source_type: str, item_id: str) -> bool:
        """Remove an item from manual exclusion list.
        
        Args:
            source_type: Type of data source
            item_id: ID of item to remove
            
        Returns:
            True if removed successfully
        """
        if source_type not in self.manual_exclusions:
            return False
        
        try:
            self.manual_exclusions[source_type].remove(item_id)
            logger.info(f"Removed {item_id} from {source_type} exclusion list")
            return True
        except ValueError:
            return False
    
    def _get_item_id(self, item: Dict[str, Any], source_type: str) -> Optional[str]:
        """Get unique ID for an item based on source type."""
        if source_type == 'gmail':
            return item.get('id') or item.get('headers', {}).get('message_id')
        elif source_type == 'fireflies':
            return item.get('id')
        elif source_type == 'google_drive':
            return item.get('id')
        return None
    
    def get_active_rules(self, source_type: Optional[str] = None) -> List[FilterRule]:
        """Get list of active rules.
        
        Args:
            source_type: Filter by source type (optional)
            
        Returns:
            List of active rules
        """
        rules = [r for r in self.rules if r.enabled]
        
        # TODO: Filter by source type if needed
        
        return rules
    
    def get_exclusion_stats(self) -> Dict[str, Any]:
        """Get statistics about exclusions.
        
        Returns:
            Dictionary with exclusion statistics
        """
        return {
            'total_rules': len(self.rules),
            'active_rules': len([r for r in self.rules if r.enabled]),
            'manual_exclusions': {
                source: len(items) 
                for source, items in self.manual_exclusions.items()
            },
            'rule_types': {
                rule_type.value: len([r for r in self.rules if r.type == rule_type])
                for rule_type in FilterType
            }
        }
    
    def export_rules(self) -> List[Dict[str, Any]]:
        """Export all rules as dictionary list.
        
        Returns:
            List of rule dictionaries
        """
        return [
            {
                'name': rule.name,
                'type': rule.type.value,
                'action': rule.action.value,
                'pattern': rule.pattern,
                'value': rule.value,
                'metadata': rule.metadata,
                'enabled': rule.enabled,
                'priority': rule.priority
            }
            for rule in self.rules
        ]
    
    def import_rules(self, rules_data: List[Dict[str, Any]], replace: bool = False) -> int:
        """Import rules from dictionary list.
        
        Args:
            rules_data: List of rule dictionaries
            replace: Whether to replace existing rules
            
        Returns:
            Number of rules imported
        """
        if replace:
            self.rules.clear()
        
        imported = 0
        for rule_data in rules_data:
            try:
                rule = FilterRule(
                    name=rule_data['name'],
                    type=FilterType(rule_data['type']),
                    action=FilterAction(rule_data.get('action', 'exclude')),
                    pattern=rule_data.get('pattern'),
                    value=rule_data.get('value'),
                    metadata=rule_data.get('metadata'),
                    enabled=rule_data.get('enabled', True),
                    priority=rule_data.get('priority', 0)
                )
                if self.add_rule(rule):
                    imported += 1
            except Exception as e:
                logger.error(f"Failed to import rule: {e}")
        
        return imported


# Example custom filter functions
def has_attachments_filter(item: Dict[str, Any], source_type: str, rule: FilterRule) -> bool:
    """Filter items that have attachments."""
    if source_type == 'gmail':
        return len(item.get('attachments', [])) > 0
    return False


def is_automated_email_filter(item: Dict[str, Any], source_type: str, rule: FilterRule) -> bool:
    """Filter automated emails (noreply, notifications, etc.)."""
    if source_type != 'gmail':
        return False
    
    sender = item.get('metadata', {}).get('sender_email', '').lower()
    automated_patterns = [
        'noreply@', 'no-reply@', 'notification@', 'notifications@',
        'automated@', 'system@', 'mailer-daemon@', 'postmaster@'
    ]
    
    return any(pattern in sender for pattern in automated_patterns)


def meeting_duration_filter(item: Dict[str, Any], source_type: str, rule: FilterRule) -> bool:
    """Filter meetings based on duration."""
    if source_type != 'fireflies':
        return False
    
    duration = item.get('duration', 0)
    min_duration = rule.metadata.get('min_duration', 0) if rule.metadata else 0
    max_duration = rule.metadata.get('max_duration', float('inf')) if rule.metadata else float('inf')
    
    return min_duration <= duration <= max_duration