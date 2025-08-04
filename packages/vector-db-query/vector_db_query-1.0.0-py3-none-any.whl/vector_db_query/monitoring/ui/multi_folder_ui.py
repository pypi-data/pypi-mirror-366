"""
UI components for multi-folder schedule configuration.

This module provides Streamlit UI components for creating and managing
schedules that monitor multiple folders with different configurations.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json

from ..scheduling.multi_folder_watcher import (
    MultiFolderSchedule, FolderWatchConfig, MultiFolderWatcher
)
from ..scheduling.models import EventType, ScheduleType
from ..scheduling.schedule_manager import ScheduleManager


class MultiFolderUI:
    """
    UI for multi-folder schedule management.
    
    Provides interface for configuring schedules that monitor
    multiple folders with different patterns and settings.
    """
    
    def __init__(self, schedule_manager: ScheduleManager, multi_folder_watcher: MultiFolderWatcher):
        """
        Initialize multi-folder UI.
        
        Args:
            schedule_manager: Schedule manager instance
            multi_folder_watcher: Multi-folder watcher instance
        """
        self.schedule_manager = schedule_manager
        self.multi_folder_watcher = multi_folder_watcher
        
    def render_multi_folder_config(self):
        """Render multi-folder configuration interface."""
        st.header("📁 Multi-Folder Schedule Configuration")
        
        # Tabs for different operations
        tabs = st.tabs([
            "Create Multi-Folder Schedule",
            "Manage Existing",
            "Folder Templates",
            "Import/Export"
        ])
        
        with tabs[0]:
            self._render_create_multi_folder()
        
        with tabs[1]:
            self._render_manage_existing()
        
        with tabs[2]:
            self._render_folder_templates()
        
        with tabs[3]:
            self._render_import_export()
    
    def _render_create_multi_folder(self):
        """Render interface for creating multi-folder schedule."""
        st.subheader("Create Multi-Folder Schedule")
        
        # Basic information
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Schedule Name",
                placeholder="Multi-Site Document Monitor"
            )
            
            description = st.text_area(
                "Description",
                placeholder="Monitor documents across multiple project folders"
            )
        
        with col2:
            task_name = st.selectbox(
                "Task to Execute",
                ["incremental_index", "full_reindex", "generate_report", "backup_database"]
            )
            
            enabled = st.checkbox("Enable Schedule", value=True)
        
        # Advanced options
        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                cross_folder_dedup = st.checkbox(
                    "Cross-folder Deduplication",
                    value=True,
                    help="Prevent duplicate events when file appears in multiple folders"
                )
                
                aggregate_events = st.checkbox(
                    "Aggregate Events",
                    value=False,
                    help="Collect multiple events before triggering task"
                )
            
            with col2:
                if aggregate_events:
                    aggregation_window = st.number_input(
                        "Aggregation Window (seconds)",
                        min_value=1,
                        max_value=300,
                        value=5
                    )
                else:
                    aggregation_window = 5
        
        # Folder configurations
        st.subheader("Folder Configurations")
        
        # Initialize folder list in session state
        if 'multi_folder_configs' not in st.session_state:
            st.session_state.multi_folder_configs = []
        
        # Add folder button
        if st.button("➕ Add Folder", use_container_width=True):
            st.session_state.multi_folder_configs.append({
                'path': '',
                'patterns': ['*.*'],
                'recursive': True,
                'event_types': [EventType.CREATED, EventType.MODIFIED],
                'ignore_patterns': [],
                'min_file_size': None,
                'max_file_size': None
            })
        
        # Display folder configurations
        folders_to_remove = []
        
        for idx, config in enumerate(st.session_state.multi_folder_configs):
            with st.expander(f"Folder {idx + 1}: {config.get('path', 'Not configured')}", expanded=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Folder path
                    config['path'] = st.text_input(
                        "Folder Path",
                        value=config.get('path', ''),
                        key=f"path_{idx}",
                        placeholder="/path/to/folder"
                    )
                    
                    # Validate path
                    if config['path']:
                        path_obj = Path(config['path'])
                        if path_obj.exists() and path_obj.is_dir():
                            st.success("✓ Valid folder path")
                        else:
                            st.error("✗ Folder does not exist")
                
                with col2:
                    # Recursive option
                    config['recursive'] = st.checkbox(
                        "Recursive",
                        value=config.get('recursive', True),
                        key=f"recursive_{idx}"
                    )
                
                with col3:
                    # Remove button
                    if st.button("🗑️ Remove", key=f"remove_{idx}"):
                        folders_to_remove.append(idx)
                
                # File patterns
                patterns_str = st.text_input(
                    "File Patterns (comma-separated)",
                    value=", ".join(config.get('patterns', ['*.*'])),
                    key=f"patterns_{idx}",
                    help="e.g., *.pdf, *.docx, report_*.xlsx"
                )
                config['patterns'] = [p.strip() for p in patterns_str.split(',') if p.strip()]
                
                # Event types
                config['event_types'] = st.multiselect(
                    "Monitor Events",
                    options=[EventType.CREATED, EventType.MODIFIED, EventType.DELETED, EventType.MOVED],
                    default=config.get('event_types', [EventType.CREATED, EventType.MODIFIED]),
                    key=f"events_{idx}",
                    format_func=lambda x: x.value.capitalize()
                )
                
                # Advanced filters
                with st.expander("Advanced Filters"):
                    # Ignore patterns
                    ignore_str = st.text_input(
                        "Ignore Patterns (comma-separated)",
                        value=", ".join(config.get('ignore_patterns', [])),
                        key=f"ignore_{idx}",
                        placeholder="*.tmp, ~*, .DS_Store"
                    )
                    config['ignore_patterns'] = [p.strip() for p in ignore_str.split(',') if p.strip()]
                    
                    # File size filters
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        use_min_size = st.checkbox("Minimum file size", key=f"use_min_{idx}")
                        if use_min_size:
                            config['min_file_size'] = st.number_input(
                                "Min size (bytes)",
                                min_value=0,
                                value=config.get('min_file_size', 1024),
                                key=f"min_size_{idx}"
                            )
                        else:
                            config['min_file_size'] = None
                    
                    with col2:
                        use_max_size = st.checkbox("Maximum file size", key=f"use_max_{idx}")
                        if use_max_size:
                            config['max_file_size'] = st.number_input(
                                "Max size (bytes)",
                                min_value=1,
                                value=config.get('max_file_size', 104857600),  # 100MB
                                key=f"max_size_{idx}"
                            )
                        else:
                            config['max_file_size'] = None
        
        # Remove folders marked for deletion
        for idx in reversed(folders_to_remove):
            st.session_state.multi_folder_configs.pop(idx)
            st.rerun()
        
        # Quick stats
        if st.session_state.multi_folder_configs:
            st.info(f"Monitoring {len(st.session_state.multi_folder_configs)} folders")
        else:
            st.warning("No folders configured. Add at least one folder to monitor.")
        
        # Create button
        if st.button("✅ Create Multi-Folder Schedule", use_container_width=True, type="primary"):
            if not name:
                st.error("Please provide a schedule name")
            elif not st.session_state.multi_folder_configs:
                st.error("Please add at least one folder to monitor")
            else:
                # Validate all folders
                valid = True
                folder_configs = []
                
                for config in st.session_state.multi_folder_configs:
                    if not config['path']:
                        st.error("All folders must have a path specified")
                        valid = False
                        break
                    
                    folder_configs.append(FolderWatchConfig(
                        path=config['path'],
                        patterns=config['patterns'],
                        recursive=config['recursive'],
                        event_types=config['event_types'],
                        ignore_patterns=config['ignore_patterns'],
                        min_file_size=config['min_file_size'],
                        max_file_size=config['max_file_size']
                    ))
                
                if valid:
                    # Create schedule
                    schedule = MultiFolderSchedule(
                        name=name,
                        description=description,
                        schedule_type=ScheduleType.FILE_EVENT,
                        enabled=enabled,
                        task_name=task_name,
                        task_params={},
                        folder_configs=folder_configs,
                        cross_folder_dedup=cross_folder_dedup,
                        aggregate_events=aggregate_events,
                        aggregation_window=aggregation_window,
                        trigger=ScheduleTrigger.FILE_CHANGE
                    )
                    
                    try:
                        # Add to watcher
                        if self.multi_folder_watcher.add_multi_folder_schedule(schedule):
                            st.success(f"Created multi-folder schedule: {name}")
                            st.session_state.multi_folder_configs = []  # Clear form
                            st.rerun()
                        else:
                            st.error("Failed to add schedule to watcher")
                    except Exception as e:
                        st.error(f"Error creating schedule: {str(e)}")
    
    def _render_manage_existing(self):
        """Render interface for managing existing multi-folder schedules."""
        st.subheader("Manage Multi-Folder Schedules")
        
        # Get all multi-folder schedules
        all_schedules = self.schedule_manager.get_all_schedules()
        multi_folder_schedules = [
            s for s in all_schedules 
            if isinstance(s, MultiFolderSchedule) or (
                hasattr(s, 'folder_configs') and s.folder_configs
            )
        ]
        
        if not multi_folder_schedules:
            st.info("No multi-folder schedules configured yet.")
            return
        
        # Schedule selector
        selected_schedule_name = st.selectbox(
            "Select Schedule",
            [s.name for s in multi_folder_schedules]
        )
        
        selected_schedule = next(
            (s for s in multi_folder_schedules if s.name == selected_schedule_name),
            None
        )
        
        if selected_schedule:
            # Display schedule info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", "🟢 Active" if selected_schedule.enabled else "🔴 Inactive")
            
            with col2:
                folder_count = len(getattr(selected_schedule, 'folder_configs', []))
                st.metric("Monitored Folders", folder_count)
            
            with col3:
                if st.button("📊 View Statistics"):
                    stats = self.multi_folder_watcher.get_folder_statistics(selected_schedule.id)
                    st.json(stats)
            
            # Folder management
            st.write("### Monitored Folders")
            
            if hasattr(selected_schedule, 'folder_configs'):
                for idx, config in enumerate(selected_schedule.folder_configs):
                    with st.expander(f"📁 {config.path}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Patterns:** {', '.join(config.patterns)}")
                            st.write(f"**Recursive:** {'Yes' if config.recursive else 'No'}")
                            st.write(f"**Events:** {', '.join(e.value for e in config.event_types)}")
                            
                            if config.ignore_patterns:
                                st.write(f"**Ignore:** {', '.join(config.ignore_patterns)}")
                            
                            # Check folder status
                            if Path(config.path).exists():
                                file_count = sum(
                                    1 for _ in Path(config.path).rglob('*')
                                    if _.is_file()
                                )
                                st.success(f"✓ Folder exists ({file_count} files)")
                            else:
                                st.error("✗ Folder not found")
                        
                        with col2:
                            if st.button(f"Remove", key=f"remove_folder_{idx}"):
                                if self.multi_folder_watcher.remove_folder_from_schedule(
                                    selected_schedule.id, config.path
                                ):
                                    st.success("Folder removed")
                                    st.rerun()
                                else:
                                    st.error("Failed to remove folder")
            
            # Add new folder
            with st.expander("➕ Add New Folder"):
                new_path = st.text_input("Folder Path", key="new_folder_path")
                new_patterns = st.text_input(
                    "File Patterns",
                    value="*.*",
                    key="new_folder_patterns"
                )
                new_recursive = st.checkbox("Recursive", value=True, key="new_folder_recursive")
                
                if st.button("Add Folder", key="add_folder_btn"):
                    if new_path:
                        new_config = FolderWatchConfig(
                            path=new_path,
                            patterns=[p.strip() for p in new_patterns.split(',')],
                            recursive=new_recursive,
                            event_types=[EventType.CREATED, EventType.MODIFIED]
                        )
                        
                        if self.multi_folder_watcher.add_folder_to_schedule(
                            selected_schedule.id, new_config
                        ):
                            st.success("Folder added successfully")
                            st.rerun()
                        else:
                            st.error("Failed to add folder")
            
            # Schedule actions
            st.write("### Actions")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if selected_schedule.enabled:
                    if st.button("⏸️ Disable Schedule", use_container_width=True):
                        selected_schedule.enabled = False
                        self.schedule_manager.update_schedule(selected_schedule)
                        st.rerun()
                else:
                    if st.button("▶️ Enable Schedule", use_container_width=True):
                        selected_schedule.enabled = True
                        self.schedule_manager.update_schedule(selected_schedule)
                        st.rerun()
            
            with col2:
                if st.button("🔄 Restart Watchers", use_container_width=True):
                    # Remove and re-add schedule
                    self.multi_folder_watcher.remove_schedule(selected_schedule.id)
                    if self.multi_folder_watcher.add_multi_folder_schedule(selected_schedule):
                        st.success("Watchers restarted")
                    else:
                        st.error("Failed to restart watchers")
            
            with col3:
                if st.button("📋 Copy Configuration", use_container_width=True):
                    config_json = json.dumps(selected_schedule.to_dict(), indent=2)
                    st.code(config_json, language='json')
            
            with col4:
                if st.button("🗑️ Delete Schedule", use_container_width=True, type="secondary"):
                    if st.session_state.get(f'confirm_delete_{selected_schedule.id}'):
                        self.multi_folder_watcher.remove_schedule(selected_schedule.id)
                        self.schedule_manager.delete_schedule(selected_schedule.id)
                        st.success("Schedule deleted")
                        del st.session_state[f'confirm_delete_{selected_schedule.id}']
                        st.rerun()
                    else:
                        st.session_state[f'confirm_delete_{selected_schedule.id}'] = True
                        st.warning("Click again to confirm deletion")
    
    def _render_folder_templates(self):
        """Render folder configuration templates."""
        st.subheader("Folder Configuration Templates")
        
        templates = {
            "Project Documents": {
                "description": "Monitor all project documentation",
                "folders": [
                    {
                        "name": "Docs",
                        "patterns": ["*.pdf", "*.docx", "*.md"],
                        "recursive": True,
                        "ignore": ["~*", "*.tmp"]
                    },
                    {
                        "name": "Reports",
                        "patterns": ["*.xlsx", "*.csv", "report_*.pdf"],
                        "recursive": False
                    }
                ]
            },
            "Code Repository": {
                "description": "Monitor source code changes",
                "folders": [
                    {
                        "name": "Source",
                        "patterns": ["*.py", "*.js", "*.java"],
                        "recursive": True,
                        "ignore": ["__pycache__", "*.pyc", "node_modules"]
                    },
                    {
                        "name": "Tests",
                        "patterns": ["test_*.py", "*_test.py"],
                        "recursive": True
                    }
                ]
            },
            "Media Library": {
                "description": "Monitor media files across folders",
                "folders": [
                    {
                        "name": "Images",
                        "patterns": ["*.jpg", "*.png", "*.gif"],
                        "recursive": True,
                        "min_size": 1024  # 1KB minimum
                    },
                    {
                        "name": "Videos",
                        "patterns": ["*.mp4", "*.avi", "*.mov"],
                        "recursive": True,
                        "max_size": 5368709120  # 5GB maximum
                    }
                ]
            },
            "Data Pipeline": {
                "description": "Monitor data processing pipeline",
                "folders": [
                    {
                        "name": "Input",
                        "patterns": ["*.csv", "*.json", "*.xml"],
                        "recursive": False,
                        "events": ["created"]
                    },
                    {
                        "name": "Processing",
                        "patterns": ["*.tmp", "*.processing"],
                        "recursive": False,
                        "events": ["created", "deleted"]
                    },
                    {
                        "name": "Output",
                        "patterns": ["*.csv", "*.json", "*.parquet"],
                        "recursive": False,
                        "events": ["created", "modified"]
                    }
                ]
            }
        }
        
        # Template selector
        selected_template = st.selectbox(
            "Select Template",
            list(templates.keys())
        )
        
        if selected_template:
            template = templates[selected_template]
            
            st.info(template['description'])
            
            # Display template structure
            st.write("### Template Structure")
            
            for folder in template['folders']:
                with st.expander(f"📁 {folder['name']} Folder"):
                    st.write(f"**Patterns:** {', '.join(folder['patterns'])}")
                    st.write(f"**Recursive:** {folder.get('recursive', True)}")
                    
                    if 'ignore' in folder:
                        st.write(f"**Ignore:** {', '.join(folder['ignore'])}")
                    
                    if 'min_size' in folder:
                        st.write(f"**Min Size:** {folder['min_size']} bytes")
                    
                    if 'max_size' in folder:
                        st.write(f"**Max Size:** {folder['max_size']} bytes")
                    
                    if 'events' in folder:
                        st.write(f"**Events:** {', '.join(folder['events'])}")
            
            # Apply template button
            if st.button("📋 Use This Template", use_container_width=True):
                # Convert template to folder configs
                folder_configs = []
                
                for folder in template['folders']:
                    # Base path needs to be specified by user
                    base_path = st.text_input(
                        f"Base path for {folder['name']}",
                        placeholder=f"/path/to/{folder['name'].lower()}"
                    )
                    
                    if base_path:
                        folder_configs.append({
                            'path': base_path,
                            'patterns': folder['patterns'],
                            'recursive': folder.get('recursive', True),
                            'event_types': [
                                EventType(e) for e in folder.get('events', ['created', 'modified'])
                            ],
                            'ignore_patterns': folder.get('ignore', []),
                            'min_file_size': folder.get('min_size'),
                            'max_file_size': folder.get('max_size')
                        })
                
                if len(folder_configs) == len(template['folders']):
                    st.session_state.multi_folder_configs = folder_configs
                    st.success("Template applied! Go to 'Create Multi-Folder Schedule' to complete setup.")
                else:
                    st.warning("Please specify all base paths to use this template")
    
    def _render_import_export(self):
        """Render import/export interface for multi-folder schedules."""
        st.subheader("Import/Export Multi-Folder Configurations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Export Configuration")
            
            # Get multi-folder schedules
            all_schedules = self.schedule_manager.get_all_schedules()
            multi_folder_schedules = [
                s for s in all_schedules 
                if hasattr(s, 'folder_configs') and s.folder_configs
            ]
            
            if multi_folder_schedules:
                selected_export = st.multiselect(
                    "Select schedules to export",
                    [s.name for s in multi_folder_schedules]
                )
                
                if selected_export and st.button("📥 Export Selected", use_container_width=True):
                    export_data = []
                    
                    for schedule in multi_folder_schedules:
                        if schedule.name in selected_export:
                            export_data.append(schedule.to_dict())
                    
                    export_json = json.dumps(export_data, indent=2, default=str)
                    
                    st.download_button(
                        label="Download Configuration",
                        data=export_json,
                        file_name=f"multi_folder_schedules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            else:
                st.info("No multi-folder schedules to export")
        
        with col2:
            st.write("### Import Configuration")
            
            uploaded_file = st.file_uploader(
                "Choose configuration file",
                type=['json'],
                help="Upload multi-folder schedule configuration"
            )
            
            if uploaded_file is not None:
                try:
                    config_data = json.loads(uploaded_file.read())
                    
                    st.write(f"Found {len(config_data)} schedule(s) in file")
                    
                    if st.button("📤 Import All", use_container_width=True):
                        success_count = 0
                        
                        for schedule_data in config_data:
                            try:
                                schedule = MultiFolderSchedule.from_dict(schedule_data)
                                
                                if self.multi_folder_watcher.add_multi_folder_schedule(schedule):
                                    success_count += 1
                                else:
                                    st.warning(f"Failed to add schedule: {schedule.name}")
                            
                            except Exception as e:
                                st.error(f"Error importing schedule: {str(e)}")
                        
                        if success_count > 0:
                            st.success(f"Successfully imported {success_count} schedules")
                            st.rerun()
                
                except Exception as e:
                    st.error(f"Error reading configuration file: {str(e)}")