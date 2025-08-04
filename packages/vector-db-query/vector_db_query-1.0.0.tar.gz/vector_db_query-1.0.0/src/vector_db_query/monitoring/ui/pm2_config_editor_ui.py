"""
PM2 configuration editor UI components for the monitoring dashboard.

This module provides Streamlit UI components for editing PM2 ecosystem files,
managing process configurations, and handling PM2 settings.
"""

import streamlit as st
import json
import yaml
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
from pathlib import Path

from ..services.pm2_config_manager import (
    PM2ConfigManager, PM2ProcessConfig, PM2EcosystemConfig,
    get_pm2_config_manager
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class PM2ConfigEditorUI:
    """
    UI components for PM2 configuration management.
    
    Provides interface for editing ecosystem files, managing processes,
    and handling PM2 configuration validation and deployment.
    """
    
    def __init__(self):
        """Initialize PM2 config editor UI."""
        self.config_manager = get_pm2_config_manager()
        self.change_tracker = get_change_tracker()
    
    def render_pm2_config_tab(self):
        """Render the main PM2 configuration tab."""
        st.header("⚙️ PM2 Configuration Editor")
        
        # Tab selection
        pm2_tabs = st.tabs([
            "Ecosystem Overview",
            "Process Editor", 
            "Configuration Files",
            "Backup & Restore",
            "Validation & Deploy"
        ])
        
        with pm2_tabs[0]:
            self._render_ecosystem_overview()
        
        with pm2_tabs[1]:
            self._render_process_editor()
        
        with pm2_tabs[2]:
            self._render_config_files()
        
        with pm2_tabs[3]:
            self._render_backup_restore()
        
        with pm2_tabs[4]:
            self._render_validation_deploy()
    
    def _render_ecosystem_overview(self):
        """Render ecosystem overview with process list."""
        st.subheader("PM2 Ecosystem Overview")
        
        # PM2 system information
        pm2_info = self.config_manager.get_pm2_info()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PM2 Version", pm2_info.get('version', 'unknown'))
        
        with col2:
            st.metric("Running Processes", pm2_info.get('process_count', 0))
        
        with col3:
            config_status = "✅ Loaded" if pm2_info.get('config_loaded') else "❌ Not Loaded"
            st.metric("Config Status", config_status)
        
        with col4:
            st.metric("Backups Available", pm2_info.get('backup_count', 0))
        
        # Current ecosystem configuration
        ecosystem_config = self.config_manager.get_ecosystem_config()
        
        if ecosystem_config:
            st.write("### Current Ecosystem Configuration")
            
            if ecosystem_config.apps:
                # Process summary table
                process_data = []
                for app in ecosystem_config.apps:
                    process_data.append({
                        'Name': app.name,
                        'Script': app.script,
                        'Mode': app.exec_mode,
                        'Instances': str(app.instances),
                        'Auto Restart': '✅' if app.autorestart else '❌',
                        'Watch': '✅' if app.watch else '❌',
                        'Cwd': app.cwd or 'default'
                    })
                
                df = pd.DataFrame(process_data)
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        'Name': st.column_config.TextColumn('Name', width='medium'),
                        'Script': st.column_config.TextColumn('Script', width='large'),
                        'Mode': st.column_config.TextColumn('Mode', width='small'),
                        'Instances': st.column_config.TextColumn('Instances', width='small'),
                        'Auto Restart': st.column_config.TextColumn('Auto Restart', width='small'),
                        'Watch': st.column_config.TextColumn('Watch', width='small')
                    }
                )
                
                # Process details
                st.write("### Process Details")
                
                selected_process = st.selectbox(
                    "Select Process for Details",
                    [''] + [app.name for app in ecosystem_config.apps],
                    format_func=lambda x: x if x else "Select a process..."
                )
                
                if selected_process:
                    process_config = self.config_manager.get_process(selected_process)
                    if process_config:
                        self._render_process_details(process_config)
            else:
                st.info("No processes defined in ecosystem configuration.")
        else:
            st.warning("No ecosystem configuration loaded. Load or create one in the 'Configuration Files' tab.")
            
            # Quick actions
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Load Existing Config"):
                    if self.config_manager.load_ecosystem_file():
                        st.success("Configuration loaded successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to load configuration. Check if ecosystem file exists.")
            
            with col2:
                if st.button("➕ Create New Config"):
                    # Create empty ecosystem
                    empty_config = PM2EcosystemConfig([])
                    if self.config_manager.set_ecosystem_config(empty_config, validate=False):
                        st.success("Empty ecosystem configuration created!")
                        st.rerun()
    
    def _render_process_details(self, process_config: PM2ProcessConfig):
        """Render detailed process information."""
        with st.expander(f"Process Details: {process_config.name}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Configuration:**")
                st.write(f"**Name:** {process_config.name}")
                st.write(f"**Script:** {process_config.script}")
                st.write(f"**Working Directory:** {process_config.cwd or 'default'}")
                st.write(f"**Arguments:** {process_config.args or 'none'}")
                st.write(f"**Interpreter:** {process_config.interpreter or 'default'}")
                
                st.write("**Execution:**")
                st.write(f"**Mode:** {process_config.exec_mode}")
                st.write(f"**Instances:** {process_config.instances}")
                st.write(f"**Auto Restart:** {'Yes' if process_config.autorestart else 'No'}")
                st.write(f"**Max Restarts:** {process_config.max_restarts}")
                st.write(f"**Min Uptime:** {process_config.min_uptime}")
            
            with col2:
                st.write("**Monitoring:**")
                st.write(f"**Watch:** {'Yes' if process_config.watch else 'No'}")
                st.write(f"**Memory Restart:** {process_config.max_memory_restart or 'none'}")
                st.write(f"**Cron Restart:** {process_config.cron_restart or 'none'}")
                
                st.write("**Logging:**")
                st.write(f"**Log File:** {process_config.log_file or 'default'}")
                st.write(f"**Out File:** {process_config.out_file or 'default'}")
                st.write(f"**Error File:** {process_config.error_file or 'default'}")
                st.write(f"**Merge Logs:** {'Yes' if process_config.merge_logs else 'No'}")
                
                # Environment variables
                if process_config.env:
                    st.write("**Environment Variables:**")
                    for key, value in process_config.env.items():
                        st.write(f"  • {key}: {value}")
    
    def _render_process_editor(self):
        """Render process editor interface."""
        st.subheader("Process Configuration Editor")
        
        ecosystem_config = self.config_manager.get_ecosystem_config()
        
        # Process selection for editing
        process_names = self.config_manager.list_processes()
        
        # Action selector
        action = st.radio(
            "Action",
            ["Add New Process", "Edit Existing Process", "Remove Process"],
            horizontal=True
        )
        
        if action == "Add New Process":
            self._render_add_process_form()
        
        elif action == "Edit Existing Process":
            if not process_names:
                st.info("No processes available to edit. Add a process first.")
            else:
                selected_process = st.selectbox(
                    "Select Process to Edit",
                    process_names
                )
                
                if selected_process:
                    process_config = self.config_manager.get_process(selected_process)
                    if process_config:
                        self._render_edit_process_form(process_config)
        
        elif action == "Remove Process":
            if not process_names:
                st.info("No processes available to remove.")
            else:
                selected_process = st.selectbox(
                    "Select Process to Remove",
                    process_names
                )
                
                if selected_process:
                    st.warning(f"⚠️ This will permanently remove the process '{selected_process}' from the ecosystem configuration.")
                    
                    if st.button(f"🗑 Remove {selected_process}", type="secondary"):
                        if st.session_state.get(f'confirm_remove_{selected_process}'):
                            if self.config_manager.remove_process(selected_process):
                                st.success(f"Process '{selected_process}' removed successfully!")
                                del st.session_state[f'confirm_remove_{selected_process}']
                                st.rerun()
                            else:
                                st.error("Failed to remove process.")
                        else:
                            st.session_state[f'confirm_remove_{selected_process}'] = True
                            st.error("Click again to confirm removal")
    
    def _render_add_process_form(self):
        """Render form for adding new process."""
        st.write("### Add New Process")
        
        with st.form("add_process_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Settings:**")
                name = st.text_input("Process Name*", help="Unique name for this process")
                script = st.text_input("Script Path*", help="Path to the script to execute")
                cwd = st.text_input("Working Directory", help="Directory to run the script from")
                args = st.text_input("Arguments", help="Command line arguments")
                interpreter = st.text_input("Interpreter", help="e.g., python3, node, etc.")
                
                st.write("**Execution:**")
                exec_mode = st.selectbox("Execution Mode", ["fork", "cluster"])
                instances = st.number_input("Instances", min_value=1, value=1)
                if exec_mode == "cluster":
                    st.info("Cluster mode: Use multiple instances for load balancing")
            
            with col2:
                st.write("**Restart Policy:**")
                autorestart = st.checkbox("Auto Restart", value=True)
                max_restarts = st.number_input("Max Restarts", min_value=0, value=10)
                min_uptime = st.text_input("Min Uptime", value="10s", help="Minimum uptime before restart")
                max_memory_restart = st.text_input("Max Memory Restart", help="e.g., 1G, 500M")
                cron_restart = st.text_input("Cron Restart", help="Cron pattern for scheduled restarts")
                
                st.write("**Monitoring:**")
                watch = st.checkbox("Watch Files", value=False)
                if watch:
                    ignore_watch = st.text_input("Ignore Watch", help="Comma-separated patterns to ignore")
            
            # Environment variables
            st.write("**Environment Variables:**")
            env_text = st.text_area(
                "Environment (JSON format)",
                value='{}',
                help="JSON object with environment variables"
            )
            
            # Logging
            st.write("**Logging:**")
            col3, col4 = st.columns(2)
            
            with col3:
                log_file = st.text_input("Log File", help="Path to log file")
                out_file = st.text_input("Out File", help="Path to stdout file")
            
            with col4:
                error_file = st.text_input("Error File", help="Path to stderr file")
                merge_logs = st.checkbox("Merge Logs", value=True)
            
            submitted = st.form_submit_button("Add Process")
            
            if submitted and name and script:
                try:
                    # Parse environment variables
                    env_vars = json.loads(env_text) if env_text.strip() else {}
                    
                    # Parse ignore watch patterns
                    ignore_patterns = None
                    if watch and ignore_watch:
                        ignore_patterns = [p.strip() for p in ignore_watch.split(',') if p.strip()]
                    
                    # Create process configuration
                    process_config = PM2ProcessConfig(
                        name=name,
                        script=script,
                        cwd=cwd if cwd else None,
                        args=args if args else None,
                        interpreter=interpreter if interpreter else None,
                        instances=instances,
                        exec_mode=exec_mode,
                        env=env_vars,
                        log_file=log_file if log_file else None,
                        out_file=out_file if out_file else None,
                        error_file=error_file if error_file else None,
                        min_uptime=min_uptime,
                        max_restarts=max_restarts,  
                        autorestart=autorestart,
                        cron_restart=cron_restart if cron_restart else None,
                        watch=watch,
                        ignore_watch=ignore_patterns,
                        max_memory_restart=max_memory_restart if max_memory_restart else None,
                        merge_logs=merge_logs
                    )
                    
                    if self.config_manager.add_process(process_config):
                        st.success(f"Process '{name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add process. Check the logs for details.")
                
                except json.JSONDecodeError:
                    st.error("Invalid JSON format in environment variables.")
                except Exception as e:
                    st.error(f"Error creating process: {e}")
    
    def _render_edit_process_form(self, current_config: PM2ProcessConfig):
        """Render form for editing existing process."""
        st.write(f"### Edit Process: {current_config.name}")
        
        with st.form("edit_process_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Settings:**")
                script = st.text_input("Script Path*", value=current_config.script)
                cwd = st.text_input("Working Directory", value=current_config.cwd or "")
                args = st.text_input("Arguments", value=current_config.args or "")
                interpreter = st.text_input("Interpreter", value=current_config.interpreter or "")
                
                st.write("**Execution:**")
                exec_mode = st.selectbox(
                    "Execution Mode", 
                    ["fork", "cluster"],
                    index=0 if current_config.exec_mode == "fork" else 1
                )
                instances = st.number_input(
                    "Instances", 
                    min_value=1, 
                    value=int(current_config.instances) if isinstance(current_config.instances, int) else 1
                )
            
            with col2:
                st.write("**Restart Policy:**")
                autorestart = st.checkbox("Auto Restart", value=current_config.autorestart)
                max_restarts = st.number_input("Max Restarts", min_value=0, value=current_config.max_restarts)
                min_uptime = st.text_input("Min Uptime", value=current_config.min_uptime)
                max_memory_restart = st.text_input(
                    "Max Memory Restart", 
                    value=current_config.max_memory_restart or ""
                )
                cron_restart = st.text_input("Cron Restart", value=current_config.cron_restart or "")
                
                st.write("**Monitoring:**")
                watch = st.checkbox("Watch Files", value=bool(current_config.watch))
                if watch:
                    ignore_patterns = ', '.join(current_config.ignore_watch) if current_config.ignore_watch else ""
                    ignore_watch = st.text_input("Ignore Watch", value=ignore_patterns)
            
            # Environment variables
            st.write("**Environment Variables:**")
            env_json = json.dumps(current_config.env or {}, indent=2)
            env_text = st.text_area("Environment (JSON format)", value=env_json)
            
            # Logging
            st.write("**Logging:**")
            col3, col4 = st.columns(2)
            
            with col3:
                log_file = st.text_input("Log File", value=current_config.log_file or "")
                out_file = st.text_input("Out File", value=current_config.out_file or "")
            
            with col4:
                error_file = st.text_input("Error File", value=current_config.error_file or "")
                merge_logs = st.checkbox("Merge Logs", value=current_config.merge_logs)
            
            submitted = st.form_submit_button("Update Process")
            
            if submitted and script:
                try:
                    # Parse environment variables
                    env_vars = json.loads(env_text) if env_text.strip() else {}
                    
                    # Parse ignore watch patterns
                    ignore_patterns = None
                    if watch and ignore_watch:
                        ignore_patterns = [p.strip() for p in ignore_watch.split(',') if p.strip()]
                    
                    # Create updated process configuration
                    updated_config = PM2ProcessConfig(
                        name=current_config.name,  # Name cannot be changed
                        script=script,
                        cwd=cwd if cwd else None,
                        args=args if args else None,
                        interpreter=interpreter if interpreter else None,
                        instances=instances,
                        exec_mode=exec_mode,
                        env=env_vars,
                        log_file=log_file if log_file else None,
                        out_file=out_file if out_file else None,
                        error_file=error_file if error_file else None,
                        min_uptime=min_uptime,
                        max_restarts=max_restarts,
                        autorestart=autorestart,
                        cron_restart=cron_restart if cron_restart else None,
                        watch=watch,
                        ignore_watch=ignore_patterns,
                        max_memory_restart=max_memory_restart if max_memory_restart else None,
                        merge_logs=merge_logs
                    )
                    
                    if self.config_manager.update_process(updated_config):
                        st.success(f"Process '{current_config.name}' updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update process. Check the logs for details.")
                
                except json.JSONDecodeError:
                    st.error("Invalid JSON format in environment variables.")
                except Exception as e:
                    st.error(f"Error updating process: {e}")
    
    def _render_config_files(self):
        """Render configuration file management interface."""
        st.subheader("Configuration File Management")
        
        # Current file information
        pm2_info = self.config_manager.get_pm2_info()
        
        st.write("### Current Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**PM2 Home:** {pm2_info['home']}")
            st.write(f"**Ecosystem File:** {pm2_info['ecosystem_file']}")
            st.write(f"**Configuration Loaded:** {'Yes' if pm2_info['config_loaded'] else 'No'}")
        
        with col2:
            # File operations
            if st.button("🔄 Reload Configuration"):
                if self.config_manager.load_ecosystem_file():
                    st.success("Configuration reloaded successfully!")
                    st.rerun()
                else:
                    st.error("Failed to reload configuration.")
        
        # Save configuration
        st.write("### Save Configuration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save as JavaScript (.js)"):
                if self.config_manager.save_ecosystem_file("js"):
                    st.success("Configuration saved as JavaScript!")
                else:
                    st.error("Failed to save configuration.")
        
        with col2:
            if st.button("💾 Save as JSON (.json)"):
                if self.config_manager.save_ecosystem_file("json"):
                    st.success("Configuration saved as JSON!")
                else:
                    st.error("Failed to save configuration.")
        
        with col3:
            if st.button("💾 Save as YAML (.yaml)"):
                if self.config_manager.save_ecosystem_file("yaml"):
                    st.success("Configuration saved as YAML!")
                else:
                    st.error("Failed to save configuration.")
        
        # Custom save location
        st.write("### Export to Custom Location")
        
        custom_path = st.text_input(
            "Custom File Path",
            placeholder="/path/to/my-ecosystem.config.js"
        )
        
        if custom_path:
            file_format = "js"
            if custom_path.endswith('.json'):
                file_format = "json"
            elif custom_path.endswith(('.yaml', '.yml')):
                file_format = "yaml"
            
            if st.button(f"📤 Export as {file_format.upper()}"):
                if self.config_manager.save_ecosystem_file(file_format, custom_path):
                    st.success(f"Configuration exported to {custom_path}")
                else:
                    st.error("Failed to export configuration.")
        
        # Load from custom location
        st.write("### Load from Custom Location")
        
        uploaded_file = st.file_uploader(
            "Upload Configuration File",
            type=['js', 'json', 'yaml', 'yml'],
            help="Upload an existing PM2 ecosystem configuration file"
        )
        
        if uploaded_file is not None:
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix=f'.{uploaded_file.name.split(".")[-1]}',
                    delete=False
                ) as temp_file:
                    temp_file.write(uploaded_file.getvalue().decode())
                    temp_file_path = temp_file.name
                
                if st.button("📥 Load Uploaded Configuration"):
                    if self.config_manager.load_ecosystem_file(temp_file_path):
                        st.success("Configuration loaded from uploaded file!")
                        st.rerun()
                    else:
                        st.error("Failed to load configuration from uploaded file.")
                
                # Clean up temp file
                Path(temp_file_path).unlink(missing_ok=True)
                
            except Exception as e:
                st.error(f"Error processing uploaded file: {e}")
        
        # Current configuration preview
        ecosystem_config = self.config_manager.get_ecosystem_config()
        
        if ecosystem_config:
            st.write("### Current Configuration Preview")
            
            format_option = st.selectbox("Preview Format", ["JSON", "YAML"])
            
            config_dict = ecosystem_config.to_dict()
            
            if format_option == "JSON":
                config_text = json.dumps(config_dict, indent=2)
                st.code(config_text, language='json')
            else:
                config_text = yaml.dump(config_dict, default_flow_style=False, indent=2)
                st.code(config_text, language='yaml')
    
    def _render_backup_restore(self):
        """Render backup and restore interface."""
        st.subheader("Backup & Restore")
        
        # Create backup
        st.write("### Create Backup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            backup_name = st.text_input(
                "Backup Name (optional)",
                placeholder="my_backup_name"
            )
        
        with col2:
            if st.button("💾 Create Backup"):
                backup_path = self.config_manager.backup_configuration(backup_name)
                st.success(f"Backup created: {backup_path}")
        
        # List backups
        st.write("### Available Backups")
        
        backups = self.config_manager.list_backups()
        
        if backups:
            backup_data = []
            for backup in backups:
                backup_data.append({
                    'Name': backup['name'],
                    'Created': backup['created'].strftime('%Y-%m-%d %H:%M:%S'),
                    'Size': f"{backup['size'] / 1024:.1f} KB",
                    'Path': backup['path']
                })
            
            df = pd.DataFrame(backup_data)
            st.dataframe(
                df[['Name', 'Created', 'Size']],
                use_container_width=True
            )
            
            # Restore backup
            st.write("### Restore Backup")
            
            selected_backup = st.selectbox(
                "Select Backup to Restore",
                [''] + [backup['name'] for backup in backups],
                format_func=lambda x: x if x else "Select a backup..."
            )
            
            if selected_backup:
                selected_backup_info = next(b for b in backups if b['name'] == selected_backup)
                
                st.info(f"**Backup:** {selected_backup}")
                st.info(f"**Created:** {selected_backup_info['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.info(f"**Size:** {selected_backup_info['size'] / 1024:.1f} KB")
                
                st.warning("⚠️ Restoring will replace the current configuration. A backup of the current state will be created automatically.")
                
                if st.button("🔄 Restore Backup"):
                    if st.session_state.get('confirm_restore'):
                        if self.config_manager.restore_backup(selected_backup):
                            st.success(f"Configuration restored from backup: {selected_backup}")
                            del st.session_state['confirm_restore']
                            st.rerun()
                        else:
                            st.error("Failed to restore backup.")
                    else:
                        st.session_state['confirm_restore'] = True
                        st.error("Click again to confirm restore operation")
        else:
            st.info("No backups available. Create a backup first.")
    
    def _render_validation_deploy(self):
        """Render validation and deployment interface."""
        st.subheader("Configuration Validation & Deployment")
        
        # Validation
        st.write("### Configuration Validation")
        
        if st.button("🔍 Validate Configuration"):
            is_valid, issues = self.config_manager.validate_configuration()
            
            if is_valid:
                st.success("✅ Configuration is valid!")
            else:
                st.error("❌ Configuration has issues:")
                for issue in issues:
                    st.write(f"• {issue}")
        
        # PM2 deployment commands
        st.write("### PM2 Deployment")
        
        ecosystem_config = self.config_manager.get_ecosystem_config()
        
        if ecosystem_config and ecosystem_config.apps:
            st.info("Use these commands to deploy your configuration:")
            
            # Generate PM2 commands
            pm2_info = self.config_manager.get_pm2_info()
            ecosystem_path = pm2_info['ecosystem_file']
            
            commands = [
                "# Stop all processes",
                "pm2 delete all",
                "",
                "# Start from ecosystem file",
                f"pm2 start {ecosystem_path}",
                "",
                "# Save PM2 process list",
                "pm2 save",
                "",
                "# Setup PM2 startup script",
                "pm2 startup",
                "",
                "# Monitor processes",
                "pm2 monit"
            ]
            
            st.code('\n'.join(commands), language='bash')
            
            # Individual process commands
            st.write("### Individual Process Commands")
            
            selected_process = st.selectbox(
                "Select Process for Commands",
                [app.name for app in ecosystem_config.apps]
            )
            
            if selected_process:
                process_commands = [
                    f"# Start {selected_process}",
                    f"pm2 start {ecosystem_path} --only {selected_process}",
                    "",
                    f"# Stop {selected_process}",
                    f"pm2 stop {selected_process}",
                    "",
                    f"# Restart {selected_process}",
                    f"pm2 restart {selected_process}",
                    "",
                    f"# Delete {selected_process}",
                    f"pm2 delete {selected_process}",
                    "",
                    f"# View logs for {selected_process}",
                    f"pm2 logs {selected_process}"
                ]
                
                st.code('\n'.join(process_commands), language='bash')
        else:
            st.warning("No processes configured. Add processes to generate deployment commands.")
        
        # Deployment validation
        st.write("### Pre-deployment Checks")
        
        if st.button("🔧 Run Pre-deployment Checks"):
            checks_passed = 0
            total_checks = 0
            
            # Check 1: Configuration validity
            total_checks += 1
            is_valid, issues = self.config_manager.validate_configuration()
            if is_valid:
                st.success("✅ Configuration is valid")
                checks_passed += 1
            else:
                st.error("❌ Configuration validation failed")
                for issue in issues:
                    st.write(f"  • {issue}")
            
            # Check 2: PM2 availability
            total_checks += 1
            pm2_info = self.config_manager.get_pm2_info()
            if pm2_info.get('version') != 'unknown':
                st.success(f"✅ PM2 is available (version {pm2_info['version']})")
                checks_passed += 1
            else:
                st.error("❌ PM2 is not available or not installed")
            
            # Check 3: Script paths
            if ecosystem_config and ecosystem_config.apps:
                total_checks += 1
                script_issues = []
                
                for app in ecosystem_config.apps:
                    if app.cwd:
                        cwd_path = Path(app.cwd)
                        if not cwd_path.exists():
                            script_issues.append(f"Working directory does not exist: {app.cwd} (for {app.name})")
                
                if not script_issues:
                    st.success("✅ All working directories exist")
                    checks_passed += 1
                else:
                    st.warning("⚠️ Some working directories may not exist:")
                    for issue in script_issues:
                        st.write(f"  • {issue}")
            
            # Summary
            st.write(f"### Check Summary: {checks_passed}/{total_checks} passed")
            
            if checks_passed == total_checks:
                st.success("🎉 All checks passed! Configuration is ready for deployment.")
            else:
                st.warning("⚠️ Some checks failed. Please review and fix issues before deployment.")