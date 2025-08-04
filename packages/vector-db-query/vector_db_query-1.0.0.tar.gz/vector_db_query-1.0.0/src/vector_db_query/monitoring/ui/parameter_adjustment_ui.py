"""
Parameter adjustment UI components for the monitoring dashboard.

This module provides Streamlit UI components for viewing and
adjusting service parameters at runtime.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import pandas as pd
import plotly.express as px
from pathlib import Path

from ..services.parameter_manager import (
    ParameterManager, ParameterDefinition, ParameterType,
    ParameterScope, ParameterChange, get_parameter_manager
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class ParameterAdjustmentUI:
    """
    UI components for service parameter adjustment.
    
    Provides interface for viewing and modifying service
    parameters without requiring restarts.
    """
    
    def __init__(self, parameter_manager: Optional[ParameterManager] = None):
        """
        Initialize parameter adjustment UI.
        
        Args:
            parameter_manager: Parameter manager instance
        """
        self.parameter_manager = parameter_manager or get_parameter_manager()
        self.change_tracker = get_change_tracker()
        
    def render_parameter_tab(self):
        """Render the main parameter adjustment tab."""
        st.header("🎛️ Service Parameter Adjustment")
        
        # Tab selection
        param_tabs = st.tabs([
            "Service Parameters",
            "Global Settings",
            "Bulk Operations",
            "Change History",
            "Import/Export"
        ])
        
        with param_tabs[0]:
            self._render_service_parameters()
        
        with param_tabs[1]:
            self._render_global_settings()
        
        with param_tabs[2]:
            self._render_bulk_operations()
        
        with param_tabs[3]:
            self._render_change_history()
        
        with param_tabs[4]:
            self._render_import_export()
    
    def _render_service_parameters(self):
        """Render service-specific parameter adjustments."""
        st.subheader("Service Parameters")
        
        # Get all registered services
        all_parameters = self.parameter_manager.get_all_parameters()
        service_ids = [sid for sid in all_parameters.keys() if sid != "global"]
        
        if not service_ids:
            st.info("No services with configurable parameters found.")
            return
        
        # Service selector
        selected_service = st.selectbox(
            "Select Service",
            service_ids,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if selected_service:
            # Get service parameters
            service_params = self.parameter_manager.get_service_parameters(selected_service)
            
            if not service_params:
                st.warning(f"No parameters configured for {selected_service}")
                return
            
            # Group by category
            categories = self.parameter_manager.get_parameter_categories(selected_service)
            
            # Display service info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Parameters", len(service_params))
            
            with col2:
                st.metric("Categories", len(categories))
            
            with col3:
                requires_restart = sum(
                    1 for p in service_params.values() 
                    if p.requires_restart
                )
                st.metric("Require Restart", requires_restart)
            
            # Filter controls
            col1, col2 = st.columns(2)
            
            with col1:
                category_filter = st.selectbox(
                    "Filter by Category",
                    ["All"] + categories
                )
            
            with col2:
                show_advanced = st.checkbox("Show Advanced Parameters", value=False)
            
            # Display parameters by category
            for category in categories:
                if category_filter != "All" and category != category_filter:
                    continue
                
                # Get parameters in this category
                cat_params = [
                    (name, param) for name, param in service_params.items()
                    if param.category == category
                ]
                
                if not cat_params:
                    continue
                
                # Skip advanced categories if not showing
                if not show_advanced and category in ['advanced', 'debug', 'experimental']:
                    continue
                
                with st.expander(f"📁 {category.title()} ({len(cat_params)} parameters)", expanded=True):
                    for param_name, param_def in cat_params:
                        self._render_parameter_control(
                            selected_service,
                            param_name,
                            param_def
                        )
    
    def _render_parameter_control(
        self,
        service_id: str,
        param_name: str,
        param_def: ParameterDefinition
    ):
        """Render control for a single parameter."""
        # Create unique key for this parameter
        param_key = f"{service_id}_{param_name}"
        
        # Parameter container
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                # Parameter info
                st.write(f"**{param_name}**")
                st.caption(param_def.description)
                
                # Show constraints
                constraints = []
                if param_def.min_value is not None:
                    constraints.append(f"Min: {param_def.min_value}")
                if param_def.max_value is not None:
                    constraints.append(f"Max: {param_def.max_value}")
                if param_def.allowed_values:
                    constraints.append(f"Allowed: {', '.join(map(str, param_def.allowed_values))}")
                
                if constraints:
                    st.caption(" | ".join(constraints))
            
            with col2:
                # Parameter control based on type
                current_value = param_def.current_value
                new_value = None
                
                if param_def.type == ParameterType.BOOLEAN:
                    new_value = st.checkbox(
                        "Enabled",
                        value=current_value,
                        key=f"{param_key}_value"
                    )
                
                elif param_def.type == ParameterType.INTEGER:
                    if param_def.min_value is not None and param_def.max_value is not None:
                        new_value = st.slider(
                            "Value",
                            min_value=param_def.min_value,
                            max_value=param_def.max_value,
                            value=current_value,
                            key=f"{param_key}_value"
                        )
                    else:
                        new_value = st.number_input(
                            "Value",
                            value=current_value,
                            min_value=param_def.min_value,
                            max_value=param_def.max_value,
                            step=1,
                            key=f"{param_key}_value"
                        )
                
                elif param_def.type == ParameterType.FLOAT:
                    if param_def.min_value is not None and param_def.max_value is not None:
                        new_value = st.slider(
                            "Value",
                            min_value=float(param_def.min_value),
                            max_value=float(param_def.max_value),
                            value=float(current_value),
                            key=f"{param_key}_value"
                        )
                    else:
                        new_value = st.number_input(
                            "Value",
                            value=float(current_value),
                            min_value=float(param_def.min_value) if param_def.min_value else None,
                            max_value=float(param_def.max_value) if param_def.max_value else None,
                            step=0.1,
                            key=f"{param_key}_value"
                        )
                
                elif param_def.type == ParameterType.STRING:
                    if param_def.sensitive:
                        new_value = st.text_input(
                            "Value",
                            value="*" * len(str(current_value)),
                            type="password",
                            key=f"{param_key}_value"
                        )
                    else:
                        new_value = st.text_input(
                            "Value",
                            value=current_value,
                            key=f"{param_key}_value"
                        )
                
                elif param_def.type == ParameterType.ENUM:
                    if param_def.allowed_values:
                        new_value = st.selectbox(
                            "Value",
                            param_def.allowed_values,
                            index=param_def.allowed_values.index(current_value)
                            if current_value in param_def.allowed_values else 0,
                            key=f"{param_key}_value"
                        )
                
                elif param_def.type == ParameterType.LIST:
                    # Simple text area for list input
                    list_text = st.text_area(
                        "Value (one per line)",
                        value="\n".join(map(str, current_value)),
                        key=f"{param_key}_value"
                    )
                    new_value = [line.strip() for line in list_text.split('\n') if line.strip()]
                
                elif param_def.type == ParameterType.JSON:
                    json_text = st.text_area(
                        "Value (JSON)",
                        value=json.dumps(current_value, indent=2),
                        key=f"{param_key}_value"
                    )
                    try:
                        new_value = json.loads(json_text)
                    except:
                        st.error("Invalid JSON")
                        new_value = current_value
                
                # Show current vs new
                if new_value != current_value:
                    st.caption(f"Current: {current_value} → New: {new_value}")
            
            with col3:
                # Action buttons
                if new_value != current_value:
                    if st.button("💾 Apply", key=f"{param_key}_apply"):
                        # Get reason for change
                        reason = st.session_state.get(f"{param_key}_reason", "Manual adjustment")
                        
                        # Apply the change
                        success = self.parameter_manager.set_value(
                            service_id=service_id,
                            parameter_name=param_name,
                            new_value=new_value,
                            changed_by=st.session_state.get('username', 'user'),
                            reason=reason
                        )
                        
                        if success:
                            st.success(f"Updated {param_name}")
                            
                            # Show restart warning if needed
                            if param_def.requires_restart:
                                st.warning(
                                    f"⚠️ {param_name} requires service restart to take effect"
                                )
                            
                            st.rerun()
                        else:
                            st.error(f"Failed to update {param_name}")
                
                # Reset button
                if current_value != param_def.default_value:
                    if st.button("🔄 Reset", key=f"{param_key}_reset"):
                        success = self.parameter_manager.set_value(
                            service_id=service_id,
                            parameter_name=param_name,
                            new_value=param_def.default_value,
                            changed_by=st.session_state.get('username', 'user'),
                            reason="Reset to default"
                        )
                        
                        if success:
                            st.success(f"Reset {param_name} to default")
                            st.rerun()
            
            # Reason input (shown when value changed)
            if new_value != current_value:
                st.text_input(
                    "Reason for change",
                    key=f"{param_key}_reason",
                    placeholder="Why are you making this change?"
                )
            
            st.divider()
    
    def _render_global_settings(self):
        """Render global parameter settings."""
        st.subheader("Global Settings")
        
        st.info(
            "Global settings affect all services. Changes here may have "
            "system-wide impact. Use with caution."
        )
        
        # Get global parameters
        global_params = self.parameter_manager.get_service_parameters("global")
        
        if not global_params:
            st.warning("No global parameters configured")
            return
        
        # Display global parameters
        for param_name, param_def in global_params.items():
            # Skip if it's a service-specific parameter
            if param_def.scope != ParameterScope.GLOBAL:
                continue
            
            self._render_parameter_control("global", param_name, param_def)
    
    def _render_bulk_operations(self):
        """Render bulk parameter operations."""
        st.subheader("Bulk Operations")
        
        operation_type = st.selectbox(
            "Operation Type",
            ["Reset to Defaults", "Apply Profile", "Copy Settings"]
        )
        
        if operation_type == "Reset to Defaults":
            st.write("### Reset Parameters to Default Values")
            
            # Service selection
            all_parameters = self.parameter_manager.get_all_parameters()
            service_ids = list(all_parameters.keys())
            
            selected_services = st.multiselect(
                "Select Services",
                service_ids,
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            if selected_services:
                # Show what will be reset
                total_params = 0
                for service_id in selected_services:
                    params = all_parameters.get(service_id, {})
                    non_default = sum(
                        1 for p in params.values()
                        if p.current_value != p.default_value
                    )
                    if non_default > 0:
                        st.write(f"- **{service_id}**: {non_default} parameters")
                        total_params += non_default
                
                if total_params > 0:
                    if st.button(f"🔄 Reset {total_params} Parameters", type="primary"):
                        if st.session_state.get('confirm_bulk_reset'):
                            # Perform reset
                            reset_count = 0
                            
                            for service_id in selected_services:
                                params = all_parameters.get(service_id, {})
                                
                                for param_name, param_def in params.items():
                                    if param_def.current_value != param_def.default_value:
                                        success = self.parameter_manager.set_value(
                                            service_id=service_id,
                                            parameter_name=param_name,
                                            new_value=param_def.default_value,
                                            changed_by=st.session_state.get('username', 'user'),
                                            reason="Bulk reset to defaults"
                                        )
                                        if success:
                                            reset_count += 1
                            
                            st.success(f"Reset {reset_count} parameters to defaults")
                            del st.session_state['confirm_bulk_reset']
                            st.rerun()
                        else:
                            st.session_state['confirm_bulk_reset'] = True
                            st.warning("Click again to confirm bulk reset")
                else:
                    st.info("All selected services are already at default values")
        
        elif operation_type == "Apply Profile":
            st.write("### Apply Parameter Profile")
            
            # Predefined profiles
            profiles = {
                "Performance": {
                    "description": "Optimize for high performance",
                    "settings": {
                        "queue_processor": {
                            "batch_size": 50,
                            "processing_interval": 1.0
                        },
                        "mcp_server": {
                            "max_connections": 500
                        }
                    }
                },
                "Conservative": {
                    "description": "Conservative resource usage",
                    "settings": {
                        "queue_processor": {
                            "batch_size": 5,
                            "processing_interval": 10.0
                        },
                        "mcp_server": {
                            "max_connections": 50
                        }
                    }
                },
                "Debug": {
                    "description": "Enable debug logging and verbose output",
                    "settings": {
                        "global": {
                            "log_level": "DEBUG",
                            "enable_metrics": True
                        }
                    }
                }
            }
            
            selected_profile = st.selectbox(
                "Select Profile",
                list(profiles.keys())
            )
            
            if selected_profile:
                profile = profiles[selected_profile]
                st.info(profile['description'])
                
                # Show what will change
                st.write("**Changes to apply:**")
                
                changes = []
                for service_id, settings in profile['settings'].items():
                    for param_name, new_value in settings.items():
                        param = self.parameter_manager.get_parameter(service_id, param_name)
                        if param and param.current_value != new_value:
                            changes.append({
                                'Service': service_id,
                                'Parameter': param_name,
                                'Current': param.current_value,
                                'New': new_value
                            })
                
                if changes:
                    df = pd.DataFrame(changes)
                    st.dataframe(df, use_container_width=True)
                    
                    if st.button(f"🎯 Apply {selected_profile} Profile"):
                        # Apply profile
                        applied = 0
                        
                        for service_id, settings in profile['settings'].items():
                            for param_name, new_value in settings.items():
                                success = self.parameter_manager.set_value(
                                    service_id=service_id,
                                    parameter_name=param_name,
                                    new_value=new_value,
                                    changed_by=st.session_state.get('username', 'user'),
                                    reason=f"Applied {selected_profile} profile"
                                )
                                if success:
                                    applied += 1
                        
                        st.success(f"Applied {applied} parameter changes")
                        st.rerun()
                else:
                    st.info("Profile settings already match current configuration")
        
        elif operation_type == "Copy Settings":
            st.write("### Copy Settings Between Services")
            
            all_parameters = self.parameter_manager.get_all_parameters()
            service_ids = [sid for sid in all_parameters.keys() if sid != "global"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                source_service = st.selectbox(
                    "Source Service",
                    service_ids,
                    format_func=lambda x: x.replace('_', ' ').title()
                )
            
            with col2:
                if source_service:
                    target_services = [s for s in service_ids if s != source_service]
                    target_service = st.selectbox(
                        "Target Service",
                        target_services,
                        format_func=lambda x: x.replace('_', ' ').title()
                    )
            
            if source_service and target_service:
                # Find common parameters
                source_params = all_parameters.get(source_service, {})
                target_params = all_parameters.get(target_service, {})
                
                common_params = set(source_params.keys()) & set(target_params.keys())
                
                if common_params:
                    st.write(f"**{len(common_params)} common parameters found:**")
                    
                    # Show parameters to copy
                    copy_params = []
                    for param_name in common_params:
                        source_val = source_params[param_name].current_value
                        target_val = target_params[param_name].current_value
                        
                        if source_val != target_val:
                            copy_params.append({
                                'Parameter': param_name,
                                'Source Value': source_val,
                                'Target Value': target_val
                            })
                    
                    if copy_params:
                        df = pd.DataFrame(copy_params)
                        st.dataframe(df, use_container_width=True)
                        
                        if st.button(f"📋 Copy {len(copy_params)} Parameters"):
                            # Copy parameters
                            copied = 0
                            
                            for param_name in common_params:
                                source_val = source_params[param_name].current_value
                                target_val = target_params[param_name].current_value
                                
                                if source_val != target_val:
                                    success = self.parameter_manager.set_value(
                                        service_id=target_service,
                                        parameter_name=param_name,
                                        new_value=source_val,
                                        changed_by=st.session_state.get('username', 'user'),
                                        reason=f"Copied from {source_service}"
                                    )
                                    if success:
                                        copied += 1
                            
                            st.success(f"Copied {copied} parameters")
                            st.rerun()
                    else:
                        st.info("All common parameters already have matching values")
                else:
                    st.warning("No common parameters between selected services")
    
    def _render_change_history(self):
        """Render parameter change history."""
        st.subheader("Parameter Change History")
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            all_parameters = self.parameter_manager.get_all_parameters()
            service_filter = st.selectbox(
                "Filter by Service",
                ["All"] + list(all_parameters.keys()),
                format_func=lambda x: x if x == "All" else x.replace('_', ' ').title()
            )
        
        with col2:
            limit = st.selectbox(
                "Show last",
                [25, 50, 100, 200],
                index=0
            )
        
        with col3:
            if st.button("🔄 Refresh History"):
                st.rerun()
        
        # Get change history
        history = self.parameter_manager.get_change_history(
            service_id=service_filter if service_filter != "All" else None,
            limit=limit
        )
        
        if not history:
            st.info("No parameter changes recorded yet")
            return
        
        # Display history
        for change in history:
            with st.expander(
                f"{change.parameter_name} - {change.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                expanded=False
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Service:** {change.service_id}")
                    st.write(f"**Changed by:** {change.changed_by}")
                    
                    if change.reason:
                        st.write(f"**Reason:** {change.reason}")
                    
                    # Value change
                    st.write("**Value Change:**")
                    col_old, col_new = st.columns(2)
                    
                    with col_old:
                        st.write("Old Value:")
                        if isinstance(change.old_value, (dict, list)):
                            st.json(change.old_value)
                        else:
                            st.code(str(change.old_value))
                    
                    with col_new:
                        st.write("New Value:")
                        if isinstance(change.new_value, (dict, list)):
                            st.json(change.new_value)
                        else:
                            st.code(str(change.new_value))
                
                with col2:
                    if change.applied:
                        st.success("✓ Applied")
                    else:
                        st.error("✗ Failed")
                        if change.error:
                            st.error(change.error)
                    
                    # Revert option
                    if change.applied:
                        if st.button("↩️ Revert", key=f"revert_{id(change)}"):
                            success = self.parameter_manager.set_value(
                                service_id=change.service_id,
                                parameter_name=change.parameter_name,
                                new_value=change.old_value,
                                changed_by=st.session_state.get('username', 'user'),
                                reason=f"Reverted change from {change.timestamp}"
                            )
                            
                            if success:
                                st.success("Reverted parameter change")
                                st.rerun()
                            else:
                                st.error("Failed to revert change")
    
    def _render_import_export(self):
        """Render import/export functionality."""
        st.subheader("Import/Export Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Export Parameters")
            
            if st.button("📥 Export All Parameters", use_container_width=True):
                # Generate export
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"parameters_export_{timestamp}.json"
                
                # Create temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
                    self.parameter_manager.export_parameters(tmp.name)
                    
                    # Read back for download
                    with open(tmp.name, 'r') as f:
                        export_data = f.read()
                
                # Provide download
                st.download_button(
                    label="📥 Download Export",
                    data=export_data,
                    file_name=filename,
                    mime="application/json"
                )
                
                st.success("Export generated successfully")
            
            st.info(
                "Exports include all parameter definitions and current values "
                "(excluding sensitive parameters)."
            )
        
        with col2:
            st.write("### Import Parameters")
            
            uploaded_file = st.file_uploader(
                "Choose parameter file",
                type=['json'],
                help="Upload exported parameter configuration"
            )
            
            if uploaded_file:
                # Parse uploaded file
                try:
                    import_data = json.loads(uploaded_file.read())
                    
                    # Show preview
                    st.write(f"**Version:** {import_data.get('version', 'Unknown')}")
                    st.write(f"**Exported:** {import_data.get('exported_at', 'Unknown')}")
                    
                    # Count parameters
                    total_params = sum(
                        len(params) 
                        for params in import_data.get('parameters', {}).values()
                    )
                    st.write(f"**Total Parameters:** {total_params}")
                    
                    # Import options
                    merge_mode = st.checkbox(
                        "Merge with existing",
                        value=True,
                        help="If unchecked, will replace all parameters"
                    )
                    
                    if st.button("📤 Import Parameters", type="primary"):
                        # Save uploaded file temporarily
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
                            json.dump(import_data, tmp)
                            tmp_path = tmp.name
                        
                        # Import parameters
                        try:
                            self.parameter_manager.import_parameters(
                                tmp_path,
                                merge=merge_mode
                            )
                            
                            st.success(f"Successfully imported {total_params} parameters")
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"Import failed: {str(e)}")
                
                except Exception as e:
                    st.error(f"Invalid file format: {str(e)}")
