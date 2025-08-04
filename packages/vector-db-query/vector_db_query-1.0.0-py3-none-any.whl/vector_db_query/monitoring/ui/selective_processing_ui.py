"""Streamlit UI for selective processing configuration."""

import streamlit as st
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

from ...data_sources.filters import (
    SelectiveProcessor, FilterRule, FilterType, FilterAction,
    has_attachments_filter, is_automated_email_filter, meeting_duration_filter
)
from ...utils.logger import get_logger

logger = get_logger(__name__)


class SelectiveProcessingUI:
    """UI for managing selective processing filters."""
    
    def __init__(self):
        """Initialize UI component."""
        self.processor = self._init_processor()
        
        # Register custom filters
        self.processor.register_custom_filter('has_attachments', has_attachments_filter)
        self.processor.register_custom_filter('is_automated', is_automated_email_filter)
        self.processor.register_custom_filter('meeting_duration', meeting_duration_filter)
    
    def _init_processor(self) -> SelectiveProcessor:
        """Initialize selective processor with saved config."""
        # Load saved filters from session state
        if 'selective_filters' not in st.session_state:
            st.session_state.selective_filters = []
        
        if 'manual_exclusions' not in st.session_state:
            st.session_state.manual_exclusions = {
                'gmail': [],
                'fireflies': [],
                'google_drive': []
            }
        
        config = {
            'filter_rules': st.session_state.selective_filters,
            'manual_exclusions': st.session_state.manual_exclusions
        }
        
        return SelectiveProcessor(config)
    
    def render(self):
        """Render the selective processing UI."""
        st.header("🎯 Selective Processing")
        
        # Create tabs
        tabs = st.tabs(["Filter Rules", "Manual Exclusions", "Presets", "Import/Export"])
        
        with tabs[0]:
            self._render_filter_rules()
        
        with tabs[1]:
            self._render_manual_exclusions()
        
        with tabs[2]:
            self._render_presets()
        
        with tabs[3]:
            self._render_import_export()
    
    def _render_filter_rules(self):
        """Render filter rules management."""
        st.subheader("Filter Rules")
        
        # Add new rule section
        with st.expander("➕ Add New Rule", expanded=False):
            self._render_add_rule_form()
        
        # Display existing rules
        st.subheader("Active Rules")
        
        rules = self.processor.get_active_rules()
        if not rules:
            st.info("No filter rules defined. Add rules to control what gets processed.")
        else:
            # Show statistics
            stats = self.processor.get_exclusion_stats()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rules", stats['total_rules'])
            with col2:
                st.metric("Active Rules", stats['active_rules'])
            with col3:
                st.metric("Rule Types", len([t for t, c in stats['rule_types'].items() if c > 0]))
            
            # List rules
            for i, rule in enumerate(self.processor.rules):
                self._render_rule_card(rule, i)
    
    def _render_add_rule_form(self):
        """Render form to add a new rule."""
        col1, col2 = st.columns(2)
        
        with col1:
            rule_name = st.text_input("Rule Name", placeholder="e.g., Exclude Spam")
            rule_type = st.selectbox(
                "Filter Type",
                options=[t for t in FilterType],
                format_func=lambda x: x.value.replace('_', ' ').title()
            )
        
        with col2:
            rule_action = st.selectbox(
                "Action",
                options=[a for a in FilterAction],
                format_func=lambda x: x.value.title()
            )
            priority = st.number_input("Priority", min_value=0, max_value=100, value=0)
        
        # Type-specific configuration
        pattern = None
        value = None
        metadata = {}
        
        if rule_type == FilterType.PATTERN:
            pattern = st.text_input(
                "Pattern (glob format)",
                placeholder="e.g., *spam*, newsletter_*",
                help="Use * for wildcards, ? for single character"
            )
        
        elif rule_type == FilterType.DATE_RANGE:
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=None)
            with col2:
                end_date = st.date_input("End Date", value=None)
            
            value = {}
            if start_date:
                value['start'] = start_date.isoformat()
            if end_date:
                value['end'] = end_date.isoformat()
        
        elif rule_type == FilterType.SIZE:
            size_mode = st.radio("Size Filter Mode", ["Minimum", "Maximum", "Range"])
            
            if size_mode == "Minimum":
                min_size = st.number_input("Minimum Size (MB)", min_value=0.0, value=1.0)
                value = int(min_size * 1024 * 1024)
            elif size_mode == "Maximum":
                max_size = st.number_input("Maximum Size (MB)", min_value=0.0, value=10.0)
                value = {'min': 0, 'max': int(max_size * 1024 * 1024)}
            else:
                col1, col2 = st.columns(2)
                with col1:
                    min_size = st.number_input("Min Size (MB)", min_value=0.0, value=1.0)
                with col2:
                    max_size = st.number_input("Max Size (MB)", min_value=0.0, value=10.0)
                value = {
                    'min': int(min_size * 1024 * 1024),
                    'max': int(max_size * 1024 * 1024)
                }
        
        elif rule_type == FilterType.SENDER:
            pattern = st.text_input(
                "Sender Pattern",
                placeholder="e.g., *@spam.com, noreply@*",
                help="Email pattern to match"
            )
        
        elif rule_type == FilterType.SUBJECT:
            pattern = st.text_input(
                "Subject Pattern (regex)",
                placeholder="e.g., \\[SPAM\\], Newsletter.*",
                help="Regular expression to match subject"
            )
        
        elif rule_type == FilterType.CONTENT:
            pattern = st.text_area(
                "Content Pattern (regex)",
                placeholder="e.g., unsubscribe|opt.?out",
                help="Regular expression to match in content"
            )
        
        elif rule_type == FilterType.CUSTOM:
            custom_filter = st.selectbox(
                "Custom Filter",
                options=["has_attachments", "is_automated", "meeting_duration"]
            )
            metadata['filter_name'] = custom_filter
            
            if custom_filter == "meeting_duration":
                col1, col2 = st.columns(2)
                with col1:
                    min_dur = st.number_input("Min Duration (minutes)", min_value=0, value=5)
                with col2:
                    max_dur = st.number_input("Max Duration (minutes)", min_value=0, value=120)
                metadata['min_duration'] = min_dur * 60
                metadata['max_duration'] = max_dur * 60
        
        # Add rule button
        if st.button("Add Rule", type="primary", use_container_width=True):
            if not rule_name:
                st.error("Please provide a rule name")
            elif rule_type in [FilterType.PATTERN, FilterType.SENDER, FilterType.SUBJECT, FilterType.CONTENT] and not pattern:
                st.error("Please provide a pattern")
            else:
                new_rule = FilterRule(
                    name=rule_name,
                    type=rule_type,
                    action=rule_action,
                    pattern=pattern,
                    value=value,
                    metadata=metadata if metadata else None,
                    priority=priority
                )
                
                if self.processor.add_rule(new_rule):
                    # Save to session state
                    st.session_state.selective_filters = self.processor.export_rules()
                    st.success(f"Added rule: {rule_name}")
                    st.rerun()
                else:
                    st.error("Failed to add rule")
    
    def _render_rule_card(self, rule: FilterRule, index: int):
        """Render a single rule card."""
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            
            with col1:
                if rule.enabled:
                    st.markdown(f"**{rule.name}**")
                else:
                    st.markdown(f"~~{rule.name}~~ *(disabled)*")
                
                # Show pattern/value
                if rule.pattern:
                    st.caption(f"Pattern: `{rule.pattern}`")
                elif rule.value:
                    if isinstance(rule.value, dict):
                        st.caption(f"Value: {json.dumps(rule.value, default=str)}")
                    else:
                        st.caption(f"Value: {rule.value}")
            
            with col2:
                type_display = rule.type.value.replace('_', ' ').title()
                st.text(f"Type: {type_display}")
            
            with col3:
                action_color = {
                    FilterAction.EXCLUDE: "red",
                    FilterAction.INCLUDE: "green",
                    FilterAction.TAG: "blue"
                }.get(rule.action, "gray")
                st.markdown(f":{action_color}[{rule.action.value.upper()}]")
            
            with col4:
                st.text(f"Priority: {rule.priority}")
            
            with col5:
                # Action buttons
                if st.button("🗑️", key=f"delete_rule_{index}", help="Delete rule"):
                    if self.processor.remove_rule(rule.name):
                        st.session_state.selective_filters = self.processor.export_rules()
                        st.rerun()
                
                if rule.enabled:
                    if st.button("⏸️", key=f"disable_rule_{index}", help="Disable rule"):
                        self.processor.toggle_rule(rule.name, False)
                        st.session_state.selective_filters = self.processor.export_rules()
                        st.rerun()
                else:
                    if st.button("▶️", key=f"enable_rule_{index}", help="Enable rule"):
                        self.processor.toggle_rule(rule.name, True)
                        st.session_state.selective_filters = self.processor.export_rules()
                        st.rerun()
            
            st.divider()
    
    def _render_manual_exclusions(self):
        """Render manual exclusion lists."""
        st.subheader("Manual Exclusions")
        st.info("Manually exclude specific items from processing by their ID")
        
        # Source selector
        source_type = st.selectbox(
            "Data Source",
            options=['gmail', 'fireflies', 'google_drive'],
            format_func=lambda x: x.title()
        )
        
        # Add exclusion
        col1, col2 = st.columns([3, 1])
        with col1:
            item_id = st.text_input(
                "Item ID to Exclude",
                placeholder="e.g., message ID, transcript ID, file ID"
            )
        with col2:
            if st.button("Add Exclusion", use_container_width=True):
                if item_id:
                    if self.processor.add_manual_exclusion(source_type, item_id):
                        st.session_state.manual_exclusions = self.processor.manual_exclusions
                        st.success(f"Added {item_id} to exclusion list")
                        st.rerun()
                    else:
                        st.warning("Item already in exclusion list")
        
        # Display exclusions
        exclusions = self.processor.manual_exclusions[source_type]
        if exclusions:
            st.write(f"**Excluded {source_type.title()} Items ({len(exclusions)}):**")
            
            # Show in scrollable container
            container = st.container()
            with container:
                for item_id in exclusions:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.text(item_id)
                    with col2:
                        if st.button("Remove", key=f"remove_{source_type}_{item_id}"):
                            self.processor.remove_manual_exclusion(source_type, item_id)
                            st.session_state.manual_exclusions = self.processor.manual_exclusions
                            st.rerun()
        else:
            st.info(f"No manual exclusions for {source_type.title()}")
        
        # Bulk operations
        st.divider()
        st.subheader("Bulk Operations")
        
        uploaded_file = st.file_uploader(
            "Upload exclusion list (one ID per line)",
            type=['txt'],
            key=f"upload_{source_type}"
        )
        
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            ids = [line.strip() for line in content.split('\n') if line.strip()]
            
            if st.button(f"Add {len(ids)} items to exclusion list"):
                added = 0
                for item_id in ids:
                    if self.processor.add_manual_exclusion(source_type, item_id):
                        added += 1
                
                st.session_state.manual_exclusions = self.processor.manual_exclusions
                st.success(f"Added {added} items to exclusion list")
                st.rerun()
    
    def _render_presets(self):
        """Render filter presets."""
        st.subheader("Filter Presets")
        st.info("Quick templates for common filtering scenarios")
        
        presets = {
            "Exclude Automated Emails": [
                {
                    'name': 'Automated Senders',
                    'type': 'custom',
                    'action': 'exclude',
                    'metadata': {'filter_name': 'is_automated'},
                    'priority': 10
                },
                {
                    'name': 'Notification Subjects',
                    'type': 'subject',
                    'action': 'exclude',
                    'pattern': r'(notification|alert|automated|system)',
                    'priority': 9
                }
            ],
            "Focus on Recent Content": [
                {
                    'name': 'Last 30 Days Only',
                    'type': 'date_range',
                    'action': 'include',
                    'value': {
                        'start': (datetime.now() - timedelta(days=30)).isoformat()
                    },
                    'priority': 20
                }
            ],
            "Skip Large Files": [
                {
                    'name': 'Large Files',
                    'type': 'size',
                    'action': 'exclude',
                    'value': 50 * 1024 * 1024,  # 50MB
                    'priority': 15
                }
            ],
            "Important Meetings Only": [
                {
                    'name': 'Short Meetings',
                    'type': 'custom',
                    'action': 'exclude',
                    'metadata': {
                        'filter_name': 'meeting_duration',
                        'max_duration': 600  # 10 minutes
                    },
                    'priority': 10
                },
                {
                    'name': 'Executive Meetings',
                    'type': 'subject',
                    'action': 'include',
                    'pattern': r'(executive|board|strategic|quarterly)',
                    'priority': 25
                }
            ]
        }
        
        for preset_name, rules_data in presets.items():
            with st.expander(preset_name):
                st.write(f"**{len(rules_data)} rules**")
                
                for rule_data in rules_data:
                    st.write(f"- {rule_data['name']} ({rule_data['type']}) → {rule_data['action']}")
                
                if st.button(f"Apply {preset_name}", key=f"preset_{preset_name}"):
                    imported = self.processor.import_rules(rules_data, replace=False)
                    st.session_state.selective_filters = self.processor.export_rules()
                    st.success(f"Applied {imported} rules from preset")
                    st.rerun()
    
    def _render_import_export(self):
        """Render import/export functionality."""
        st.subheader("Import/Export Rules")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Export Current Rules**")
            
            rules_data = self.processor.export_rules()
            exclusions_data = st.session_state.manual_exclusions
            
            export_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'filter_rules': rules_data,
                'manual_exclusions': exclusions_data
            }
            
            export_json = json.dumps(export_data, indent=2)
            
            st.download_button(
                label="📥 Download Rules",
                data=export_json,
                file_name=f"selective_filters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            st.text(f"Total rules: {len(rules_data)}")
            st.text(f"Total exclusions: {sum(len(v) for v in exclusions_data.values())}")
        
        with col2:
            st.write("**Import Rules**")
            
            uploaded_file = st.file_uploader(
                "Upload rules file",
                type=['json'],
                key="import_rules"
            )
            
            if uploaded_file:
                try:
                    import_data = json.load(uploaded_file)
                    
                    st.write("File contains:")
                    st.text(f"- {len(import_data.get('filter_rules', []))} rules")
                    st.text(f"- {sum(len(v) for v in import_data.get('manual_exclusions', {}).values())} exclusions")
                    
                    replace = st.checkbox("Replace existing rules", value=False)
                    
                    if st.button("Import", type="primary"):
                        # Import rules
                        if 'filter_rules' in import_data:
                            imported = self.processor.import_rules(
                                import_data['filter_rules'],
                                replace=replace
                            )
                            st.session_state.selective_filters = self.processor.export_rules()
                        
                        # Import exclusions
                        if 'manual_exclusions' in import_data:
                            if replace:
                                st.session_state.manual_exclusions = import_data['manual_exclusions']
                            else:
                                for source, items in import_data['manual_exclusions'].items():
                                    if source in st.session_state.manual_exclusions:
                                        existing = set(st.session_state.manual_exclusions[source])
                                        existing.update(items)
                                        st.session_state.manual_exclusions[source] = list(existing)
                        
                        st.success("Import completed!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Failed to import: {e}")


def render_selective_processing():
    """Render the selective processing UI."""
    ui = SelectiveProcessingUI()
    ui.render()