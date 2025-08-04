"""
Event configuration UI components for the monitoring dashboard.

This module provides Streamlit UI components for managing event configurations,
conditions, notification rules, and monitoring event processing.
"""

import streamlit as st
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

from ..notifications.event_config import (
    EventConfigurationService, get_event_config_service, 
    EventConfiguration, EventCondition, NotificationRule,
    EventType, TriggerCondition, EventPriority, process_system_event,
    trigger_service_failure_event, trigger_high_cpu_event, trigger_queue_full_event
)
from ..notifications.models import NotificationSeverity, NotificationChannel
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class EventConfigurationUI:
    """
    UI components for event configuration management.
    
    Provides interface for creating, editing, and monitoring event configurations,
    conditions, rules, and notification processing.
    """
    
    def __init__(self):
        """Initialize event configuration UI."""
        self.event_service = get_event_config_service()
        self.change_tracker = get_change_tracker()
        
        # Initialize session state
        if 'event_config_mode' not in st.session_state:
            st.session_state.event_config_mode = 'list'
        
        if 'selected_config_id' not in st.session_state:
            st.session_state.selected_config_id = None
        
        if 'last_event_test' not in st.session_state:
            st.session_state.last_event_test = None
    
    def render_event_configuration_tab(self):
        """
        Render the main event configuration tab.
        """
        st.header("⚙️ Event Configuration")
        
        # Event configuration tabs
        config_tabs = st.tabs(["Configurations", "Create Config", "Event History", "Statistics", "Test Events"])
        
        with config_tabs[0]:
            self._render_configurations_list()
        
        with config_tabs[1]:
            self._render_configuration_creator()
        
        with config_tabs[2]:
            self._render_event_history()
        
        with config_tabs[3]:
            self._render_statistics()
        
        with config_tabs[4]:
            self._render_event_testing()
    
    def _render_configurations_list(self):
        """Render configurations list and management."""
        st.subheader("📋 Event Configurations")
        
        # Get configurations
        configurations = self.event_service.get_configurations(active_only=False)
        
        if configurations:
            # Filter controls
            col1, col2, col3 = st.columns(3)
            
            with col1:
                event_type_filter = st.selectbox(
                    "Filter by Event Type",
                    options=['All'] + [et.value for et in EventType],
                    key="config_event_type_filter"
                )
            
            with col2:
                status_filter = st.selectbox(
                    "Filter by Status",
                    options=['All', 'Active', 'Inactive'],
                    key="config_status_filter"
                )
            
            with col3:
                sort_by = st.selectbox(
                    "Sort by",
                    options=['Name', 'Created', 'Last Triggered', 'Trigger Count'],
                    key="config_sort_by"
                )
            
            # Apply filters
            filtered_configs = []
            for config in configurations.values():
                if event_type_filter != 'All' and config.event_type.value != event_type_filter:
                    continue
                if status_filter == 'Active' and not config.is_active:
                    continue
                if status_filter == 'Inactive' and config.is_active:
                    continue
                filtered_configs.append(config)
            
            # Sort configurations
            if sort_by == 'Name':
                filtered_configs.sort(key=lambda x: x.name)
            elif sort_by == 'Created':
                filtered_configs.sort(key=lambda x: x.created_at, reverse=True)
            elif sort_by == 'Last Triggered':
                filtered_configs.sort(key=lambda x: x.last_triggered or datetime.min, reverse=True)
            elif sort_by == 'Trigger Count':
                filtered_configs.sort(key=lambda x: x.trigger_count, reverse=True)
            
            # Display configurations
            if filtered_configs:
                config_data = []
                for config in filtered_configs:
                    config_data.append({
                        'ID': config.id[:8] + '...',
                        'Name': config.name,
                        'Event Type': config.event_type.value.replace('_', ' ').title(),
                        'Conditions': len(config.conditions),
                        'Rules': len(config.notification_rules),
                        'Triggers': config.trigger_count,
                        'Last Triggered': config.last_triggered.strftime('%Y-%m-%d %H:%M') if config.last_triggered else 'Never',
                        'Status': '✅ Active' if config.is_active else '❌ Inactive',
                        'Tags': ', '.join(config.tags[:3]) + ('...' if len(config.tags) > 3 else '')
                    })
                
                # Display with selection
                selected_indices = st.dataframe(
                    config_data,
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row"
                )
                
                # Configuration actions
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("✏️ Edit Selected", type="secondary"):
                        if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                            selected_idx = selected_indices.selection['rows'][0]
                            selected_config = filtered_configs[selected_idx]
                            st.session_state.selected_config_id = selected_config.id
                            st.session_state.event_config_mode = 'edit'
                            st.rerun()
                
                with col2:
                    if st.button("📋 Clone Selected", type="secondary"):
                        if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                            selected_idx = selected_indices.selection['rows'][0]
                            selected_config = filtered_configs[selected_idx]
                            # Store config for cloning
                            st.session_state.clone_config_id = selected_config.id
                            st.session_state.event_config_mode = 'clone'
                            st.rerun()
                
                with col3:
                    if st.button("🔄 Toggle Status", type="secondary"):
                        if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                            selected_idx = selected_indices.selection['rows'][0]
                            selected_config = filtered_configs[selected_idx]
                            selected_config.is_active = not selected_config.is_active
                            if self.event_service.update_configuration(selected_config):
                                st.success(f"Configuration {'activated' if selected_config.is_active else 'deactivated'}")
                                st.rerun()
                            else:
                                st.error("Failed to update configuration")
                
                with col4:
                    if st.button("🗑️ Delete Selected", type="secondary"):
                        if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                            selected_idx = selected_indices.selection['rows'][0]
                            selected_config = filtered_configs[selected_idx]
                            
                            if st.session_state.get('confirm_delete_config') == selected_config.id:
                                if self.event_service.remove_configuration(selected_config.id):
                                    st.success("Configuration deleted successfully!")
                                    st.session_state.confirm_delete_config = None
                                    st.rerun()
                                else:
                                    st.error("Failed to delete configuration")
                            else:
                                st.session_state.confirm_delete_config = selected_config.id
                                st.warning("Click again to confirm deletion")
                
                # Configuration details
                if hasattr(selected_indices, 'selection') and selected_indices.selection['rows']:
                    selected_idx = selected_indices.selection['rows'][0]
                    selected_config = filtered_configs[selected_idx]
                    
                    st.write("### Configuration Details")
                    
                    with st.expander(f"⚙️ {selected_config.name}", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Basic Information:**")
                            st.write(f"Name: {selected_config.name}")
                            st.write(f"Event Type: {selected_config.event_type.value.replace('_', ' ').title()}")
                            st.write(f"Description: {selected_config.description}")
                            st.write(f"Status: {'✅ Active' if selected_config.is_active else '❌ Inactive'}")
                            st.write(f"Created: {selected_config.created_at.strftime('%Y-%m-%d %H:%M')}")
                            
                            if selected_config.tags:
                                st.write("**Tags:**")
                                for tag in selected_config.tags:
                                    st.write(f"• {tag}")
                        
                        with col2:
                            st.write("**Activity:**")
                            st.write(f"Triggers: {selected_config.trigger_count}")
                            st.write(f"Last Triggered: {selected_config.last_triggered.strftime('%Y-%m-%d %H:%M') if selected_config.last_triggered else 'Never'}")
                            st.write(f"Conditions: {len(selected_config.conditions)}")
                            st.write(f"Notification Rules: {len(selected_config.notification_rules)}")
                        
                        # Conditions
                        if selected_config.conditions:
                            st.write("**Conditions:**")
                            for condition in selected_config.conditions:
                                status_icon = "✅" if condition.is_active else "❌"
                                st.write(f"{status_icon} {condition.description}")
                                if condition.parameters:
                                    st.write(f"   Parameters: {condition.parameters}")
                        
                        # Notification Rules
                        if selected_config.notification_rules:
                            st.write("**Notification Rules:**")
                            for rule in selected_config.notification_rules:
                                status_icon = "✅" if rule.is_active else "❌"
                                channels = ", ".join([ch.value for ch in rule.channels])
                                st.write(f"{status_icon} {rule.name} → {channels}")
                                st.write(f"   Severity: {rule.severity.value.title()} | Priority: {rule.priority.value.title()}")
                        
                        # Metadata
                        if selected_config.metadata:
                            st.write("**Metadata:**")
                            st.json(selected_config.metadata)
            else:
                st.info("No configurations match the current filters.")
        else:
            st.info("No event configurations found. Create your first configuration to start monitoring events.")
    
    def _render_configuration_creator(self):
        """Render configuration creator/editor."""
        st.subheader("✨ Create Event Configuration")
        
        # Determine mode
        mode = st.session_state.get('event_config_mode', 'create')
        config_to_edit = None
        
        if mode == 'edit' and st.session_state.get('selected_config_id'):
            config_to_edit = self.event_service.get_configuration(st.session_state.selected_config_id)
            if config_to_edit:
                st.info(f"Editing configuration: {config_to_edit.name}")
            else:
                st.error("Configuration not found")
                st.session_state.event_config_mode = 'create'
                st.session_state.selected_config_id = None
                st.rerun()
        
        elif mode == 'clone' and st.session_state.get('clone_config_id'):
            config_to_edit = self.event_service.get_configuration(st.session_state.clone_config_id)
            if config_to_edit:
                st.info(f"Cloning configuration: {config_to_edit.name}")
            else:
                st.error("Configuration not found")
                st.session_state.event_config_mode = 'create'
                st.session_state.clone_config_id = None
                st.rerun()
        
        # Configuration form
        with st.form("create_config_form", clear_on_submit=(mode == 'create')):
            # Basic information
            st.write("### Basic Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "Configuration Name *",
                    value=config_to_edit.name + " (Copy)" if (mode == 'clone' and config_to_edit) 
                          else config_to_edit.name if config_to_edit else "",
                    help="Descriptive name for this event configuration"
                )
                
                event_type = st.selectbox(
                    "Event Type *",
                    options=[et.value for et in EventType],
                    index=list(EventType).index(config_to_edit.event_type) if config_to_edit else 0,
                    help="Type of event that triggers this configuration"
                )
            
            with col2:
                description = st.text_area(
                    "Description *",
                    value=config_to_edit.description if config_to_edit else "",
                    height=100,
                    help="Detailed description of what this configuration monitors"
                )
                
                tags = st.text_input(
                    "Tags (comma-separated)",
                    value=", ".join(config_to_edit.tags) if config_to_edit else "",
                    help="Tags for categorizing and filtering configurations"
                )
            
            is_active = st.checkbox(
                "Configuration Active",
                value=config_to_edit.is_active if config_to_edit else True
            )
            
            # Conditions section
            st.write("### Trigger Conditions")
            st.write("Define when this event should trigger notifications.")
            
            # Initialize conditions in session state
            if f'conditions_{mode}' not in st.session_state:
                if config_to_edit and config_to_edit.conditions:
                    st.session_state[f'conditions_{mode}'] = [
                        {
                            'condition_type': cond.condition_type.value,
                            'parameters': cond.parameters.copy(),
                            'description': cond.description,
                            'is_active': cond.is_active
                        }
                        for cond in config_to_edit.conditions
                    ]
                else:
                    st.session_state[f'conditions_{mode}'] = []
            
            # Condition management
            conditions = st.session_state[f'conditions_{mode}']
            
            if st.button("➕ Add Condition"):
                conditions.append({
                    'condition_type': 'always',
                    'parameters': {},
                    'description': '',
                    'is_active': True
                })
                st.session_state[f'conditions_{mode}'] = conditions
                st.rerun()
            
            # Display conditions
            for i, condition in enumerate(conditions):
                with st.container():
                    st.write(f"**Condition {i+1}:**")
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        condition_type = st.selectbox(
                            "Type",
                            options=[tc.value for tc in TriggerCondition],
                            index=list(TriggerCondition).index(TriggerCondition(condition['condition_type'])),
                            key=f"condition_type_{mode}_{i}"
                        )
                        condition['condition_type'] = condition_type
                    
                    with col2:
                        description = st.text_input(
                            "Description",
                            value=condition['description'],
                            key=f"condition_desc_{mode}_{i}"
                        )
                        condition['description'] = description
                    
                    with col3:
                        condition['is_active'] = st.checkbox(
                            "Active",
                            value=condition['is_active'],
                            key=f"condition_active_{mode}_{i}"
                        )
                    
                    # Parameters based on condition type
                    if condition_type == 'threshold_exceeded':
                        col1, col2 = st.columns(2)
                        with col1:
                            metric = st.text_input(
                                "Metric Name",
                                value=condition['parameters'].get('metric', ''),
                                key=f"condition_metric_{mode}_{i}",
                                help="e.g., cpu_percent, memory_usage, queue_size"
                            )
                            condition['parameters']['metric'] = metric
                        with col2:
                            threshold = st.number_input(
                                "Threshold Value",
                                value=float(condition['parameters'].get('threshold', 0)),
                                key=f"condition_threshold_{mode}_{i}"
                            )
                            condition['parameters']['threshold'] = threshold
                    
                    elif condition_type == 'pattern_match':
                        col1, col2 = st.columns(2)
                        with col1:
                            field = st.text_input(
                                "Field Name",
                                value=condition['parameters'].get('field', ''),
                                key=f"condition_field_{mode}_{i}",
                                help="Field in event context to match against"
                            )
                            condition['parameters']['field'] = field
                        with col2:
                            pattern = st.text_input(
                                "Pattern (regex)",
                                value=condition['parameters'].get('pattern', ''),
                                key=f"condition_pattern_{mode}_{i}",
                                help="Regular expression pattern to match"
                            )
                            condition['parameters']['pattern'] = pattern
                    
                    elif condition_type == 'time_based':
                        schedule = st.selectbox(
                            "Schedule",
                            options=['hourly', 'daily', 'custom'],
                            index=['hourly', 'daily', 'custom'].index(condition['parameters'].get('schedule', 'daily')),
                            key=f"condition_schedule_{mode}_{i}"
                        )
                        condition['parameters']['schedule'] = schedule
                    
                    elif condition_type == 'count_based':
                        count = st.number_input(
                            "Count Threshold",
                            value=int(condition['parameters'].get('count', 1)),
                            min_value=1,
                            key=f"condition_count_{mode}_{i}"
                        )
                        condition['parameters']['count'] = count
                    
                    # Remove condition button
                    if st.button(f"🗑️ Remove Condition {i+1}", key=f"remove_condition_{mode}_{i}"):
                        conditions.pop(i)
                        st.session_state[f'conditions_{mode}'] = conditions
                        st.rerun()
                    
                    st.divider()
            
            if not conditions:
                st.info("Add at least one condition to define when this event should trigger.")
            
            # Notification Rules section
            st.write("### Notification Rules")
            st.write("Define how notifications are sent when conditions are met.")
            
            # Initialize rules in session state
            if f'rules_{mode}' not in st.session_state:
                if config_to_edit and config_to_edit.notification_rules:
                    st.session_state[f'rules_{mode}'] = [
                        {
                            'name': rule.name,
                            'description': rule.description,
                            'channels': [ch.value for ch in rule.channels],
                            'severity': rule.severity.value,
                            'priority': rule.priority.value,
                            'template_ids': rule.template_ids.copy(),
                            'rate_limit': rule.rate_limit.copy() if rule.rate_limit else None,
                            'quiet_hours': rule.quiet_hours.copy() if rule.quiet_hours else None,
                            'is_active': rule.is_active
                        }
                        for rule in config_to_edit.notification_rules
                    ]
                else:
                    st.session_state[f'rules_{mode}'] = []
            
            # Rule management
            rules = st.session_state[f'rules_{mode}']
            
            if st.button("➕ Add Notification Rule"):
                rules.append({
                    'name': '',
                    'description': '',
                    'channels': ['toast'],
                    'severity': 'info',
                    'priority': 'normal',
                    'template_ids': {},
                    'rate_limit': None,
                    'quiet_hours': None,
                    'is_active': True
                })
                st.session_state[f'rules_{mode}'] = rules
                st.rerun()
            
            # Display rules
            for i, rule in enumerate(rules):
                with st.container():
                    st.write(f"**Notification Rule {i+1}:**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        rule['name'] = st.text_input(
                            "Rule Name",
                            value=rule['name'],
                            key=f"rule_name_{mode}_{i}"
                        )
                        
                        rule['channels'] = st.multiselect(
                            "Notification Channels",
                            options=[ch.value for ch in NotificationChannel],
                            default=rule['channels'],
                            key=f"rule_channels_{mode}_{i}"
                        )
                    
                    with col2:
                        rule['description'] = st.text_input(
                            "Rule Description",
                            value=rule['description'],
                            key=f"rule_desc_{mode}_{i}"
                        )
                        
                        col2a, col2b = st.columns(2)
                        with col2a:
                            rule['severity'] = st.selectbox(
                                "Severity",
                                options=[s.value for s in NotificationSeverity],
                                index=list(NotificationSeverity).index(NotificationSeverity(rule['severity'])),
                                key=f"rule_severity_{mode}_{i}"
                            )
                        with col2b:
                            rule['priority'] = st.selectbox(
                                "Priority",
                                options=[p.value for p in EventPriority],
                                index=list(EventPriority).index(EventPriority(rule['priority'])),
                                key=f"rule_priority_{mode}_{i}"
                            )
                    
                    # Advanced settings
                    with st.expander(f"Advanced Settings - Rule {i+1}"):
                        # Rate limiting
                        enable_rate_limit = st.checkbox(
                            "Enable Rate Limiting",
                            value=rule['rate_limit'] is not None,
                            key=f"rule_rate_limit_enable_{mode}_{i}"
                        )
                        
                        if enable_rate_limit:
                            col1, col2 = st.columns(2)
                            with col1:
                                rate_type = st.selectbox(
                                    "Rate Limit Type",
                                    options=['minutes', 'hours'],
                                    index=['minutes', 'hours'].index(rule['rate_limit']['type']) if rule['rate_limit'] else 0,
                                    key=f"rule_rate_type_{mode}_{i}"
                                )
                            with col2:
                                rate_value = st.number_input(
                                    "Rate Limit Value",
                                    value=rule['rate_limit']['value'] if rule['rate_limit'] else 5,
                                    min_value=1,
                                    key=f"rule_rate_value_{mode}_{i}"
                                )
                            
                            rule['rate_limit'] = {'type': rate_type, 'value': rate_value}
                        else:
                            rule['rate_limit'] = None
                        
                        # Quiet hours
                        enable_quiet_hours = st.checkbox(
                            "Enable Quiet Hours",
                            value=rule['quiet_hours'] is not None,
                            key=f"rule_quiet_hours_enable_{mode}_{i}"
                        )
                        
                        if enable_quiet_hours:
                            col1, col2 = st.columns(2)
                            with col1:
                                start_hour = st.number_input(
                                    "Quiet Start Hour (24h)",
                                    value=rule['quiet_hours']['start_hour'] if rule['quiet_hours'] else 22,
                                    min_value=0,
                                    max_value=23,
                                    key=f"rule_quiet_start_{mode}_{i}"
                                )
                            with col2:
                                end_hour = st.number_input(
                                    "Quiet End Hour (24h)",
                                    value=rule['quiet_hours']['end_hour'] if rule['quiet_hours'] else 8,
                                    min_value=0,
                                    max_value=23,
                                    key=f"rule_quiet_end_{mode}_{i}"
                                )
                            
                            rule['quiet_hours'] = {'start_hour': start_hour, 'end_hour': end_hour}
                        else:
                            rule['quiet_hours'] = None
                    
                    rule['is_active'] = st.checkbox(
                        "Rule Active",
                        value=rule['is_active'],
                        key=f"rule_active_{mode}_{i}"
                    )
                    
                    # Remove rule button
                    if st.button(f"🗑️ Remove Rule {i+1}", key=f"remove_rule_{mode}_{i}"):
                        rules.pop(i)
                        st.session_state[f'rules_{mode}'] = rules
                        st.rerun()
                    
                    st.divider()
            
            if not rules:
                st.info("Add at least one notification rule to define how notifications are sent.")
            
            # Form submission
            col1, col2, col3 = st.columns(3)
            
            with col1:
                submitted = st.form_submit_button(
                    f"💾 {'Update' if mode == 'edit' else 'Create'} Configuration", 
                    type="primary"
                )
            
            with col2:
                if st.form_submit_button("🧪 Validate Configuration"):
                    # Perform validation without saving
                    if self._validate_form_data(name, description, conditions, rules):
                        st.success("✅ Configuration is valid!")
                    # Validation errors shown by _validate_form_data
            
            with col3:
                if st.form_submit_button("❌ Cancel"):
                    # Reset session state
                    st.session_state.event_config_mode = 'create'
                    st.session_state.selected_config_id = None
                    st.session_state.clone_config_id = None
                    if f'conditions_{mode}' in st.session_state:
                        del st.session_state[f'conditions_{mode}']
                    if f'rules_{mode}' in st.session_state:
                        del st.session_state[f'rules_{mode}']
                    st.rerun()
            
            if submitted:
                if self._save_configuration(name, description, event_type, tags, conditions, rules, is_active, mode, config_to_edit):
                    st.success(f"✅ Configuration {'updated' if mode == 'edit' else 'created'} successfully!")
                    
                    # Reset session state
                    st.session_state.event_config_mode = 'create'
                    st.session_state.selected_config_id = None
                    st.session_state.clone_config_id = None
                    if f'conditions_{mode}' in st.session_state:
                        del st.session_state[f'conditions_{mode}']
                    if f'rules_{mode}' in st.session_state:
                        del st.session_state[f'rules_{mode}']
                    
                    st.rerun()
    
    def _validate_form_data(self, name: str, description: str, conditions: List, rules: List) -> bool:
        """Validate form data."""
        errors = []
        
        if not name.strip():
            errors.append("Configuration name is required")
        
        if not description.strip():
            errors.append("Description is required")
        
        if not conditions:
            errors.append("At least one condition is required")
        
        if not rules:
            errors.append("At least one notification rule is required")
        
        # Validate conditions
        for i, condition in enumerate(conditions):
            if not condition['description'].strip():
                errors.append(f"Condition {i+1}: description is required")
            
            if condition['condition_type'] == 'threshold_exceeded':
                if not condition['parameters'].get('metric'):
                    errors.append(f"Condition {i+1}: metric name is required for threshold conditions")
                if condition['parameters'].get('threshold') is None:
                    errors.append(f"Condition {i+1}: threshold value is required")
            
            elif condition['condition_type'] == 'pattern_match':
                if not condition['parameters'].get('field'):
                    errors.append(f"Condition {i+1}: field name is required for pattern conditions")
                if not condition['parameters'].get('pattern'):
                    errors.append(f"Condition {i+1}: pattern is required")
        
        # Validate rules
        for i, rule in enumerate(rules):
            if not rule['name'].strip():
                errors.append(f"Rule {i+1}: name is required")
            
            if not rule['channels']:
                errors.append(f"Rule {i+1}: at least one notification channel is required")
        
        # Display errors
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
            return False
        
        return True
    
    def _save_configuration(self, name: str, description: str, event_type: str, tags: str,
                           conditions: List, rules: List, is_active: bool, mode: str, 
                           existing_config: Optional[EventConfiguration]) -> bool:
        """Save event configuration."""
        try:
            # Validate first
            if not self._validate_form_data(name, description, conditions, rules):
                return False
            
            # Create condition objects
            condition_objects = []
            for condition_data in conditions:
                condition = EventCondition(
                    id=str(uuid.uuid4()),
                    condition_type=TriggerCondition(condition_data['condition_type']),
                    parameters=condition_data['parameters'],
                    description=condition_data['description'],
                    is_active=condition_data['is_active']
                )
                condition_objects.append(condition)
            
            # Create rule objects
            rule_objects = []
            for rule_data in rules:
                rule = NotificationRule(
                    id=str(uuid.uuid4()),
                    name=rule_data['name'],
                    description=rule_data['description'],
                    channels=[NotificationChannel(ch) for ch in rule_data['channels']],
                    severity=NotificationSeverity(rule_data['severity']),
                    priority=EventPriority(rule_data['priority']),
                    template_ids=rule_data['template_ids'],
                    rate_limit=rule_data['rate_limit'],
                    quiet_hours=rule_data['quiet_hours'],
                    is_active=rule_data['is_active']
                )
                rule_objects.append(rule)
            
            # Create or update configuration
            if mode == 'edit' and existing_config:
                # Update existing
                existing_config.name = name.strip()
                existing_config.description = description.strip()
                existing_config.event_type = EventType(event_type)
                existing_config.conditions = condition_objects
                existing_config.notification_rules = rule_objects
                existing_config.tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
                existing_config.is_active = is_active
                
                return self.event_service.update_configuration(existing_config)
            else:
                # Create new
                config = EventConfiguration(
                    id=str(uuid.uuid4()),
                    name=name.strip(),
                    description=description.strip(),
                    event_type=EventType(event_type),
                    conditions=condition_objects,
                    notification_rules=rule_objects,
                    tags=[tag.strip() for tag in tags.split(',') if tag.strip()],
                    is_active=is_active
                )
                
                return self.event_service.add_configuration(config)
        
        except Exception as e:
            st.error(f"❌ Error saving configuration: {str(e)}")
            return False
    
    def _render_event_history(self):
        """Render event processing history."""
        st.subheader("📜 Event Processing History")
        
        # Get event history
        history = self.event_service.get_event_history(limit=200)
        
        if history:
            # Filter controls
            col1, col2, col3 = st.columns(3)
            
            with col1:
                event_types = list(set(entry['event_type'] for entry in history))
                event_type_filter = st.selectbox(
                    "Filter by Event Type",
                    options=['All'] + event_types,
                    key="history_event_type_filter"
                )
            
            with col2:
                hours_back = st.selectbox(
                    "Time Range",
                    options=[1, 6, 12, 24, 48, 72, 168],  # hours
                    index=3,  # 24 hours default
                    format_func=lambda x: f"Last {x} hour{'s' if x > 1 else ''}",
                    key="history_time_range"
                )
            
            with col3:
                show_details = st.checkbox("Show Context Details", value=False)
            
            # Filter history
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            filtered_history = []
            
            for entry in history:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if entry_time < cutoff_time:
                    continue
                if event_type_filter != 'All' and entry['event_type'] != event_type_filter:
                    continue
                filtered_history.append(entry)
            
            # Sort by timestamp (newest first)
            filtered_history.sort(key=lambda x: x['timestamp'], reverse=True)
            
            if filtered_history:
                # Display history
                for entry in filtered_history:
                    timestamp = datetime.fromisoformat(entry['timestamp'])
                    
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**{entry['event_type'].replace('_', ' ').title()}**")
                            st.caption(f"🕒 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        with col2:
                            st.metric("Notifications", entry['notification_count'])
                        
                        with col3:
                            if show_details and st.button("📋 Details", key=f"history_details_{entry['timestamp']}"):
                                st.json(entry['context'])
                        
                        if show_details:
                            with st.expander(f"Event Context - {timestamp.strftime('%H:%M:%S')}"):
                                st.json(entry['context'])
                        
                        st.divider()
            else:
                st.info("No events match the current filters.")
        else:
            st.info("No event history available. Events will appear here as they are processed.")
    
    def _render_statistics(self):
        """Render event processing statistics."""
        st.subheader("📊 Event Processing Statistics")
        
        # Get statistics
        stats = self.event_service.get_statistics()
        
        if stats:
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Events", stats.get('total_events', 0))
            
            with col2:
                st.metric("Total Notifications", stats.get('total_notifications', 0))
            
            with col3:
                avg_notifications = (stats.get('total_notifications', 0) / max(stats.get('total_events', 1), 1))
                st.metric("Avg Notifications/Event", f"{avg_notifications:.1f}")
            
            with col4:
                last_updated = stats.get('last_updated')
                if last_updated:
                    last_time = datetime.fromisoformat(last_updated)
                    st.metric("Last Activity", last_time.strftime('%H:%M:%S'))
                else:
                    st.metric("Last Activity", "Never")
            
            # Event type breakdown
            if 'events_by_type' in stats and stats['events_by_type']:
                st.write("### Event Type Breakdown")
                
                event_data = []
                for event_type, count in stats['events_by_type'].items():
                    percentage = (count / stats['total_events']) * 100 if stats['total_events'] > 0 else 0
                    event_data.append({
                        'Event Type': event_type.replace('_', ' ').title(),
                        'Count': count,
                        'Percentage': f"{percentage:.1f}%"
                    })
                
                # Sort by count
                event_data.sort(key=lambda x: x['Count'], reverse=True)
                
                st.dataframe(event_data, use_container_width=True, hide_index=True)
            
            # Configuration status
            configurations = self.event_service.get_configurations(active_only=False)
            
            if configurations:
                st.write("### Configuration Status")
                
                active_configs = sum(1 for config in configurations.values() if config.is_active)
                total_configs = len(configurations)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Configurations", total_configs)
                
                with col2:
                    st.metric("Active Configurations", active_configs)
                
                with col3:
                    st.metric("Inactive Configurations", total_configs - active_configs)
                
                # Most triggered configurations
                triggered_configs = [
                    (config.name, config.trigger_count)
                    for config in configurations.values()
                    if config.trigger_count > 0
                ]
                
                if triggered_configs:
                    triggered_configs.sort(key=lambda x: x[1], reverse=True)
                    
                    st.write("### Most Triggered Configurations")
                    top_configs = triggered_configs[:10]
                    
                    config_data = []
                    for name, count in top_configs:
                        config_data.append({
                            'Configuration': name,
                            'Triggers': count
                        })
                    
                    st.dataframe(config_data, use_container_width=True, hide_index=True)
        else:
            st.info("No statistics available yet. Statistics will be generated as events are processed.")
    
    def _render_event_testing(self):
        """Render event testing interface."""
        st.subheader("🧪 Event Testing")
        
        st.write("Test event configurations by triggering sample events.")
        
        # Test tabs
        test_tabs = st.tabs(["Quick Tests", "Custom Event", "Bulk Test"])
        
        with test_tabs[0]:
            self._render_quick_tests()
        
        with test_tabs[1]:
            self._render_custom_event_test()
        
        with test_tabs[2]:
            self._render_bulk_test()
    
    def _render_quick_tests(self):
        """Render quick test buttons."""
        st.write("### Quick Event Tests")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚨 Service Failure", use_container_width=True):
                notifications = trigger_service_failure_event(
                    service_name="test-service",
                    error_message="Simulated service failure for testing"
                )
                st.success(f"Service failure event triggered! Generated {len(notifications)} notifications.")
                st.session_state.last_event_test = {
                    'type': 'service_failure',
                    'count': len(notifications),
                    'timestamp': datetime.now().isoformat()
                }
        
        with col2:
            if st.button("🔥 High CPU", use_container_width=True):
                notifications = trigger_high_cpu_event(
                    cpu_percent=85.5,
                    source="test-system"
                )
                st.success(f"High CPU event triggered! Generated {len(notifications)} notifications.")
                st.session_state.last_event_test = {
                    'type': 'high_cpu',
                    'count': len(notifications),
                    'timestamp': datetime.now().isoformat()
                }
        
        with col3:
            if st.button("📦 Queue Full", use_container_width=True):
                notifications = trigger_queue_full_event(
                    queue_size=1200,
                    max_size=1000
                )
                st.success(f"Queue full event triggered! Generated {len(notifications)} notifications.")
                st.session_state.last_event_test = {
                    'type': 'queue_full',
                    'count': len(notifications),
                    'timestamp': datetime.now().isoformat()
                }
        
        with col4:
            if st.button("🔄 System Restart", use_container_width=True):
                notifications = process_system_event(
                    EventType.SYSTEM_STARTUP,
                    restart_reason="manual",
                    uptime_before="24h 15m"
                )
                st.success(f"System restart event triggered! Generated {len(notifications)} notifications.")
                st.session_state.last_event_test = {
                    'type': 'system_startup',
                    'count': len(notifications),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Display last test result
        if st.session_state.last_event_test:
            last_test = st.session_state.last_event_test
            test_time = datetime.fromisoformat(last_test['timestamp'])
            st.info(f"Last test: {last_test['type']} at {test_time.strftime('%H:%M:%S')} → {last_test['count']} notifications")
    
    def _render_custom_event_test(self):
        """Render custom event testing."""
        st.write("### Custom Event Test")
        
        with st.form("custom_event_test"):
            event_type = st.selectbox(
                "Event Type",
                options=[et.value for et in EventType]
            )
            
            context_json = st.text_area(
                "Event Context (JSON)",
                value='{\n  "test": true,\n  "value": 100,\n  "message": "Custom test event"\n}',
                height=150,
                help="JSON object containing event context data"
            )
            
            submitted = st.form_submit_button("🚀 Trigger Custom Event", type="primary")
            
            if submitted:
                try:
                    context = json.loads(context_json)
                    notifications = process_system_event(EventType(event_type), **context)
                    
                    st.success(f"Custom event triggered! Generated {len(notifications)} notifications.")
                    
                    if notifications:
                        st.write("**Generated Notifications:**")
                        for i, notification in enumerate(notifications):
                            with st.expander(f"Notification {i+1} - {notification['rule_name']}"):
                                st.json(notification)
                    
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {str(e)}")
                except Exception as e:
                    st.error(f"Error triggering event: {str(e)}")
    
    def _render_bulk_test(self):
        """Render bulk testing interface."""
        st.write("### Bulk Event Testing")
        
        st.info("Test multiple events in sequence to evaluate system performance and notification behavior.")
        
        with st.form("bulk_test_form"):
            test_count = st.number_input(
                "Number of Events",
                min_value=1,
                max_value=100,
                value=10
            )
            
            test_event_type = st.selectbox(
                "Event Type for Bulk Test",
                options=[et.value for et in EventType]
            )
            
            delay_seconds = st.number_input(
                "Delay Between Events (seconds)",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1
            )
            
            submitted = st.form_submit_button("🔄 Run Bulk Test", type="primary")
            
            if submitted:
                progress_bar = st.progress(0)
                status_text = st.empty()
                results = []
                
                import time
                
                for i in range(test_count):
                    progress = (i + 1) / test_count
                    progress_bar.progress(progress)
                    status_text.text(f"Processing event {i+1}/{test_count}...")
                    
                    # Trigger event
                    context = {
                        'bulk_test': True,
                        'sequence_number': i + 1,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    notifications = process_system_event(EventType(test_event_type), **context)
                    results.append(len(notifications))
                    
                    # Delay if not last event
                    if i < test_count - 1:
                        time.sleep(delay_seconds)
                
                # Show results
                total_notifications = sum(results)
                avg_notifications = total_notifications / test_count if test_count > 0 else 0
                
                status_text.success(f"Bulk test completed! {test_count} events triggered, {total_notifications} total notifications ({avg_notifications:.1f} avg per event)")
                
                # Results summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Events Triggered", test_count)
                with col2:
                    st.metric("Total Notifications", total_notifications)
                with col3:
                    st.metric("Avg Notifications/Event", f"{avg_notifications:.1f}")


# Global UI instance
_event_config_ui: Optional[EventConfigurationUI] = None


def get_event_configuration_ui() -> EventConfigurationUI:
    """Get singleton event configuration UI instance."""
    global _event_config_ui
    
    if _event_config_ui is None:
        _event_config_ui = EventConfigurationUI()
    
    return _event_config_ui