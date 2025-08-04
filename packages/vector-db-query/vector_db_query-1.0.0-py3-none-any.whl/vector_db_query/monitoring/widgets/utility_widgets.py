"""
Utility widgets for dashboard display.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re

from .base_widget import BaseWidget, WidgetConfig
from ..layout.models import WidgetType, WidgetSize


class LogViewerWidget(BaseWidget):
    """Widget for viewing and filtering log files."""
    
    widget_type = WidgetType.LOG_VIEWER
    widget_name = "Log Viewer"
    widget_description = "Log viewing and filtering interface"
    widget_icon = "📋"
    widget_category = "Logs"
    default_size = WidgetSize.WIDE
    
    config_schema = {
        'log_sources': {'type': 'multiselect', 'options': ['system', 'application', 'error', 'access'], 'default': ['system', 'application'], 'description': 'Log sources to display'},
        'log_levels': {'type': 'multiselect', 'options': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 'default': ['INFO', 'WARNING', 'ERROR'], 'description': 'Log levels to show'},
        'max_lines': {'type': 'number', 'min': 10, 'max': 1000, 'default': 100, 'description': 'Maximum log lines to display'},
        'auto_refresh': {'type': 'boolean', 'default': True, 'description': 'Auto-refresh log content'},
        'search_enabled': {'type': 'boolean', 'default': True, 'description': 'Enable log search'},
        'word_wrap': {'type': 'boolean', 'default': True, 'description': 'Enable word wrapping'},
        'show_timestamps': {'type': 'boolean', 'default': True, 'description': 'Show log timestamps'}
    }
    
    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self._sample_logs = self._generate_sample_logs()
        self._search_term = ""
    
    def _generate_sample_logs(self) -> List[Dict[str, Any]]:
        """Generate sample log entries for demonstration."""
        logs = []
        now = datetime.now()
        
        log_templates = [
            {'level': 'INFO', 'source': 'system', 'message': 'System startup completed successfully'},
            {'level': 'INFO', 'source': 'application', 'message': 'MCP server started on port 8080'},
            {'level': 'WARNING', 'source': 'system', 'message': 'High CPU usage detected: 85%'},
            {'level': 'ERROR', 'source': 'application', 'message': 'Failed to connect to database: connection timeout'},
            {'level': 'INFO', 'source': 'access', 'message': 'User dashboard access from 192.168.1.100'},
            {'level': 'ERROR', 'source': 'error', 'message': 'Unhandled exception in process_document: IndexError'},
            {'level': 'INFO', 'source': 'system', 'message': 'Scheduled backup started'},
            {'level': 'WARNING', 'source': 'application', 'message': 'Queue processing rate below threshold: 5 docs/min'},
            {'level': 'DEBUG', 'source': 'application', 'message': 'Processing document: example.pdf (size: 2.5MB)'},
            {'level': 'CRITICAL', 'source': 'system', 'message': 'Disk space critical: only 500MB remaining'},
            {'level': 'INFO', 'source': 'application', 'message': 'Document vectorization completed in 1.2s'},
            {'level': 'WARNING', 'source': 'system', 'message': 'Memory usage above 80%: 85.2%'},
            {'level': 'ERROR', 'source': 'application', 'message': 'Qdrant connection failed: server unreachable'},
            {'level': 'INFO', 'source': 'access', 'message': 'API request: GET /api/documents/search'},
            {'level': 'DEBUG', 'source': 'application', 'message': 'Cache hit for query: "machine learning"'}
        ]
        
        for i in range(50):  # Generate 50 log entries
            template = log_templates[i % len(log_templates)]
            log_time = now - timedelta(minutes=i * 2)
            
            logs.append({
                'timestamp': log_time,
                'level': template['level'],
                'source': template['source'],
                'message': template['message'],
                'line_number': i + 1
            })
        
        return sorted(logs, key=lambda x: x['timestamp'], reverse=True)
    
    def _render_content(self) -> None:
        """Render log viewer content."""
        try:
            log_sources = self.config.config.get('log_sources', ['system', 'application'])
            log_levels = self.config.config.get('log_levels', ['INFO', 'WARNING', 'ERROR'])
            max_lines = self.config.config.get('max_lines', 100)
            auto_refresh = self.config.config.get('auto_refresh', True)
            search_enabled = self.config.config.get('search_enabled', True)
            word_wrap = self.config.config.get('word_wrap', True)
            show_timestamps = self.config.config.get('show_timestamps', True)
            
            # Log controls
            self._render_log_controls(search_enabled, auto_refresh)
            
            # Filter logs
            filtered_logs = self._filter_logs(log_sources, log_levels, max_lines)
            
            if not filtered_logs:
                st.info("No logs match the current filter criteria")
                return
            
            # Log display
            self._render_log_display(filtered_logs, show_timestamps, word_wrap)
            
            # Log statistics
            self._render_log_statistics(filtered_logs)
            
        except Exception as e:
            st.error(f"Failed to render log viewer: {e}")
    
    def _render_log_controls(self, search_enabled: bool, auto_refresh: bool) -> None:
        """Render log viewer controls."""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if search_enabled:
                self._search_term = st.text_input(
                    "Search logs",
                    value=self._search_term,
                    placeholder="Enter search term...",
                    key=f"log_search_{self.config.widget_id}"
                )
        
        with col2:
            if st.button("🔄 Refresh", key=f"refresh_logs_{self.config.widget_id}"):
                self._sample_logs = self._generate_sample_logs()
                st.rerun()
        
        with col3:
            if st.button("📥 Export", key=f"export_logs_{self.config.widget_id}"):
                st.info("Log export functionality would be implemented here")
    
    def _filter_logs(self, log_sources: List[str], log_levels: List[str], max_lines: int) -> List[Dict[str, Any]]:
        """Filter logs based on criteria."""
        filtered = []
        
        for log in self._sample_logs:
            # Filter by source
            if log['source'] not in log_sources:
                continue
            
            # Filter by level
            if log['level'] not in log_levels:
                continue
            
            # Filter by search term
            if self._search_term and self._search_term.lower() not in log['message'].lower():
                continue
            
            filtered.append(log)
            
            # Limit results
            if len(filtered) >= max_lines:
                break
        
        return filtered
    
    def _render_log_display(self, logs: List[Dict[str, Any]], show_timestamps: bool, word_wrap: bool) -> None:
        """Render the log display area."""
        st.markdown("#### Log Entries")
        
        # Create container for logs with fixed height
        with st.container():
            for log in logs:
                level_colors = {
                    'DEBUG': '#6C757D',
                    'INFO': '#17A2B8',
                    'WARNING': '#FFC107',
                    'ERROR': '#DC3545',
                    'CRITICAL': '#6F42C1'
                }
                
                level_bg_colors = {
                    'DEBUG': '#F8F9FA',
                    'INFO': '#D1ECF1',
                    'WARNING': '#FFF3CD',
                    'ERROR': '#F8D7DA',
                    'CRITICAL': '#E2E3F1'
                }
                
                level_color = level_colors.get(log['level'], '#6C757D')
                bg_color = level_bg_colors.get(log['level'], '#F8F9FA')
                
                timestamp_str = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if show_timestamps else ''
                wrap_style = "word-wrap: break-word;" if word_wrap else "white-space: nowrap; overflow-x: auto;"
                
                # Highlight search terms
                message = log['message']
                if self._search_term:
                    message = re.sub(
                        f'({re.escape(self._search_term)})',
                        r'<mark>\1</mark>',
                        message,
                        flags=re.IGNORECASE
                    )
                
                st.markdown(
                    f"""
                    <div style="
                        background-color: {bg_color}; 
                        border-left: 4px solid {level_color};
                        padding: 8px 12px; 
                        margin-bottom: 4px;
                        font-family: 'Courier New', monospace;
                        font-size: 0.85em;
                        {wrap_style}
                    ">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="color: {level_color}; font-weight: bold;">[{log['level']}]</span>
                            <span style="color: #6C757D; font-size: 0.8em;">
                                {timestamp_str} | {log['source']} | Line {log['line_number']}
                            </span>
                        </div>
                        <div style="color: #333;">
                            {message}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    def _render_log_statistics(self, logs: List[Dict[str, Any]]) -> None:
        """Render log statistics."""
        if not logs:
            return
        
        st.markdown("#### Log Statistics")
        
        # Count by level
        level_counts = {}
        source_counts = {}
        
        for log in logs:
            level = log['level']
            source = log['source']
            
            level_counts[level] = level_counts.get(level, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**By Level:**")
            for level, count in sorted(level_counts.items()):
                st.write(f"• {level}: {count}")
        
        with col2:
            st.markdown("**By Source:**")
            for source, count in sorted(source_counts.items()):
                st.write(f"• {source}: {count}")
    
    def get_config_ui(self) -> Dict[str, Any]:
        """Get configuration UI for log viewer widget."""
        config_values = super().get_config_ui()
        
        # Widget-specific configuration
        with st.expander("Log Viewer Settings"):
            config_values['log_sources'] = st.multiselect(
                "Log Sources",
                options=['system', 'application', 'error', 'access'],
                default=self.config.config.get('log_sources', ['system', 'application']),
                key=f"config_log_sources_{self.config.widget_id}"
            )
            
            config_values['log_levels'] = st.multiselect(
                "Log Levels",
                options=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                default=self.config.config.get('log_levels', ['INFO', 'WARNING', 'ERROR']),
                key=f"config_log_levels_{self.config.widget_id}"
            )
            
            config_values['max_lines'] = st.slider(
                "Maximum Lines",
                min_value=10,
                max_value=1000,
                value=self.config.config.get('max_lines', 100),
                key=f"config_max_lines_{self.config.widget_id}"
            )
            
            config_values['auto_refresh'] = st.checkbox(
                "Auto-refresh",
                value=self.config.config.get('auto_refresh', True),
                key=f"config_auto_refresh_{self.config.widget_id}"
            )
            
            config_values['search_enabled'] = st.checkbox(
                "Enable Search",
                value=self.config.config.get('search_enabled', True),
                key=f"config_search_enabled_{self.config.widget_id}"
            )
            
            config_values['word_wrap'] = st.checkbox(
                "Word Wrap",
                value=self.config.config.get('word_wrap', True),
                key=f"config_word_wrap_{self.config.widget_id}"
            )
            
            config_values['show_timestamps'] = st.checkbox(
                "Show Timestamps",
                value=self.config.config.get('show_timestamps', True),
                key=f"config_show_timestamps_{self.config.widget_id}"
            )
        
        return config_values


class CustomHTMLWidget(BaseWidget):
    """Widget for displaying custom HTML content."""
    
    widget_type = WidgetType.CUSTOM_HTML
    widget_name = "Custom HTML"
    widget_description = "Custom HTML content widget for flexible display"
    widget_icon = "🌐"
    widget_category = "Custom"
    default_size = WidgetSize.MEDIUM
    
    config_schema = {
        'html_content': {'type': 'textarea', 'default': '<h3>Custom HTML Widget</h3><p>Add your custom HTML content here.</p>', 'description': 'HTML content to display'},
        'allow_javascript': {'type': 'boolean', 'default': False, 'description': 'Allow JavaScript execution (security risk)'},
        'auto_height': {'type': 'boolean', 'default': True, 'description': 'Auto-adjust widget height'},
        'css_styles': {'type': 'textarea', 'default': '', 'description': 'Custom CSS styles'},
        'sandbox': {'type': 'boolean', 'default': True, 'description': 'Sandbox HTML content for security'}
    }
    
    def __init__(self, config: WidgetConfig):
        super().__init__(config)
    
    def _render_content(self) -> None:
        """Render custom HTML content."""
        try:
            html_content = self.config.config.get('html_content', '<h3>Custom HTML Widget</h3><p>Add your custom HTML content here.</p>')
            allow_javascript = self.config.config.get('allow_javascript', False)
            auto_height = self.config.config.get('auto_height', True)
            css_styles = self.config.config.get('css_styles', '')
            sandbox = self.config.config.get('sandbox', True)
            
            # Render CSS styles if provided
            if css_styles:
                st.markdown(f"<style>{css_styles}</style>", unsafe_allow_html=True)
            
            # Render HTML content
            if sandbox and not allow_javascript:
                # Basic sanitization - remove script tags
                sanitized_html = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
                sanitized_html = re.sub(r'javascript:', '', sanitized_html, flags=re.IGNORECASE)
                html_content = sanitized_html
            
            # Wrap content in a container
            if auto_height:
                container_html = f"""
                <div style="width: 100%; overflow: auto;">
                    {html_content}
                </div>
                """
            else:
                container_html = f"""
                <div style="width: 100%; height: 400px; overflow: auto;">
                    {html_content}
                </div>
                """
            
            st.markdown(container_html, unsafe_allow_html=True)
            
            # Show editor if in config mode
            if st.session_state.get(f'edit_html_{self.config.widget_id}', False):
                self._render_html_editor()
                
        except Exception as e:
            st.error(f"Failed to render custom HTML: {e}")
    
    def _render_html_editor(self) -> None:
        """Render HTML content editor."""
        st.markdown("#### HTML Editor")
        
        current_html = self.config.config.get('html_content', '')
        
        new_html = st.text_area(
            "HTML Content",
            value=current_html,
            height=200,
            key=f"html_editor_{self.config.widget_id}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save HTML", key=f"save_html_{self.config.widget_id}"):
                self.config.config['html_content'] = new_html
                st.success("HTML content saved!")
                st.session_state[f'edit_html_{self.config.widget_id}'] = False
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", key=f"cancel_html_{self.config.widget_id}"):
                st.session_state[f'edit_html_{self.config.widget_id}'] = False
                st.rerun()
        
        # HTML preview
        st.markdown("#### Preview")
        st.markdown(new_html, unsafe_allow_html=True)
    
    def _render_header(self) -> None:
        """Override header to add edit button."""
        col1, col2 = st.columns([4, 1])
        
        with col1:
            if self.config.collapsible:
                with st.expander(f"{self.widget_icon} {self.config.title}", expanded=not self.config.collapsed):
                    self._render_content()
            else:
                st.markdown(f"### {self.widget_icon} {self.config.title}")
                self._render_content()
        
        with col2:
            col2a, col2b = st.columns(2)
            
            with col2a:
                if st.button("✏️", key=f"edit_html_btn_{self.config.widget_id}", help="Edit HTML"):
                    st.session_state[f'edit_html_{self.config.widget_id}'] = True
                    st.rerun()
            
            with col2b:
                if self.config.refreshable:
                    if st.button("🔄", key=f"refresh_{self.config.widget_id}", help="Refresh widget"):
                        self.refresh()
                        st.rerun()
    
    def get_config_ui(self) -> Dict[str, Any]:
        """Get configuration UI for custom HTML widget."""
        config_values = super().get_config_ui()
        
        # Widget-specific configuration
        with st.expander("Custom HTML Settings"):
            config_values['html_content'] = st.text_area(
                "HTML Content",
                value=self.config.config.get('html_content', '<h3>Custom HTML Widget</h3><p>Add your custom HTML content here.</p>'),
                height=150,
                key=f"config_html_content_{self.config.widget_id}"
            )
            
            config_values['css_styles'] = st.text_area(
                "Custom CSS Styles",
                value=self.config.config.get('css_styles', ''),
                height=100,
                key=f"config_css_styles_{self.config.widget_id}",
                help="Add custom CSS styles for your HTML content"
            )
            
            config_values['allow_javascript'] = st.checkbox(
                "Allow JavaScript (Security Risk)",
                value=self.config.config.get('allow_javascript', False),
                key=f"config_allow_js_{self.config.widget_id}",
                help="⚠️ Enabling this can pose security risks"
            )
            
            config_values['auto_height'] = st.checkbox(
                "Auto-adjust Height",
                value=self.config.config.get('auto_height', True),
                key=f"config_auto_height_{self.config.widget_id}"
            )
            
            config_values['sandbox'] = st.checkbox(
                "Sandbox Content",
                value=self.config.config.get('sandbox', True),
                key=f"config_sandbox_{self.config.widget_id}",
                help="Enable sandboxing for security"
            )
            
            # HTML templates
            st.markdown("#### HTML Templates")
            
            templates = {
                "Basic Card": """
                <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px; background: #f9f9f9;">
                    <h4>Card Title</h4>
                    <p>Card content goes here...</p>
                </div>
                """,
                "Status Dashboard": """
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; text-align: center;">
                        <h5 style="margin: 0; color: #28a745;">✅ Healthy</h5>
                        <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold;">12</p>
                    </div>
                    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; text-align: center;">
                        <h5 style="margin: 0; color: #ffc107;">⚠️ Warning</h5>
                        <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold;">3</p>
                    </div>
                    <div style="background: #f8d7da; padding: 15px; border-radius: 5px; text-align: center;">
                        <h5 style="margin: 0; color: #dc3545;">❌ Critical</h5>
                        <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold;">1</p>
                    </div>
                </div>
                """,
                "Progress Bar": """
                <div style="margin: 20px 0;">
                    <h4>Task Progress</h4>
                    <div style="background: #e9ecef; border-radius: 10px; overflow: hidden;">
                        <div style="background: #007bff; height: 20px; width: 75%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;">
                            75% Complete
                        </div>
                    </div>
                </div>
                """
            }
            
            template_choice = st.selectbox(
                "Choose Template",
                options=[""] + list(templates.keys()),
                key=f"config_template_{self.config.widget_id}"
            )
            
            if template_choice and st.button("📝 Use Template", key=f"use_template_{self.config.widget_id}"):
                config_values['html_content'] = templates[template_choice]
                st.success(f"Applied template: {template_choice}")
        
        return config_values