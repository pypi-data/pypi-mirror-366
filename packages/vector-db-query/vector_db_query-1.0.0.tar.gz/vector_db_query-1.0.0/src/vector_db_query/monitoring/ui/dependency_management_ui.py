"""
Dependency management UI components for the monitoring dashboard.

This module provides Streamlit UI components for managing
service dependencies, startup ordering, and dependency validation.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
from pathlib import Path

from ..services.dependency_manager import (
    DependencyManager, ServiceDefinition, ServiceDependency,
    DependencyType, ServiceStatus, get_dependency_manager
)
from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class DependencyManagementUI:
    """
    UI components for service dependency management.
    
    Provides interface for managing service definitions, dependencies,
    startup ordering, and dependency validation.
    """
    
    def __init__(self):
        """Initialize dependency management UI."""
        self.dependency_manager = get_dependency_manager()
        self.change_tracker = get_change_tracker()
    
    def render_dependency_tab(self):
        """Render the main dependency management tab."""
        st.header("🔗 Service Dependency Manager")
        
        # Tab selection
        dep_tabs = st.tabs([
            "Service Overview",
            "Manage Services", 
            "Manage Dependencies",
            "Startup Ordering",
            "Dependency Validation"
        ])
        
        with dep_tabs[0]:
            self._render_service_overview()
        
        with dep_tabs[1]:
            self._render_manage_services()
        
        with dep_tabs[2]:
            self._render_manage_dependencies()
        
        with dep_tabs[3]:
            self._render_startup_ordering()
        
        with dep_tabs[4]:
            self._render_dependency_validation()
    
    def _render_service_overview(self):
        """Render service overview with dependency graph."""
        st.subheader("Service Dependencies Overview")
        
        # Get all services
        all_services = self.dependency_manager.get_all_services()
        
        if not all_services:
            st.info("No services defined. Add services in the 'Manage Services' tab.")
            return
        
        # Service summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Services", len(all_services))
        
        with col2:
            running_count = sum(1 for s in all_services.values() if s['status'] == 'running')
            st.metric("Running Services", running_count, delta=f"{running_count}/{len(all_services)}")
        
        with col3:
            total_deps = sum(len(s['required_services']) for s in all_services.values())
            st.metric("Total Dependencies", total_deps)
        
        with col4:
            invalid_count = sum(1 for s in all_services.values() if not s['dependency_validation']['is_valid'])
            st.metric("Invalid Dependencies", invalid_count, delta="Issues" if invalid_count > 0 else None)
        
        # Service dependency graph
        st.subheader("Dependency Graph")
        
        if len(all_services) > 1:
            self._render_dependency_graph(all_services)
        else:
            st.info("Add more services to see dependency relationships.")
        
        # Service details table
        st.subheader("Service Details")
        
        service_data = []
        for name, info in all_services.items():
            service = info['service']
            status_emoji = {
                'running': '🟢',
                'stopped': '🔴',
                'starting': '🟡',
                'stopping': '🟠',
                'failed': '❌',
                'unknown': '⚪'
            }.get(info['status'], '⚪')
            
            service_data.append({
                'Service': f"{status_emoji} {service['display_name']}",
                'Name': name,
                'Status': info['status'].title(),
                'Priority': service['priority'],
                'Dependencies': len(info['required_services']),
                'Dependents': len(info['dependent_services']),
                'Valid': '✅' if info['dependency_validation']['is_valid'] else '❌',
                'Description': service['description'][:60] + '...' if len(service['description']) > 60 else service['description']
            })
        
        if service_data:
            df = pd.DataFrame(service_data)
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    'Service': st.column_config.TextColumn('Service', width='medium'),
                    'Status': st.column_config.TextColumn('Status', width='small'),
                    'Priority': st.column_config.NumberColumn('Priority', width='small'),
                    'Dependencies': st.column_config.NumberColumn('Deps', width='small'),
                    'Dependents': st.column_config.NumberColumn('Dependents', width='small'),
                    'Valid': st.column_config.TextColumn('Valid', width='small')
                }
            )
            
            # Service details expander
            selected_service = st.selectbox(
                "View Service Details",
                [''] + list(all_services.keys()),
                format_func=lambda x: f"{all_services[x]['service']['display_name']} ({x})" if x else "Select a service..."
            )
            
            if selected_service:
                self._render_service_details(selected_service, all_services[selected_service])
    
    def _render_dependency_graph(self, all_services: Dict[str, Dict[str, Any]]):
        """Render interactive dependency graph."""
        try:
            # Create networkx graph
            G = nx.DiGraph()
            
            # Add nodes
            for name, info in all_services.items():
                service = info['service']
                status = info['status']
                
                # Node color based on status
                color = {
                    'running': '#32CD32',
                    'stopped': '#FF6347', 
                    'starting': '#FFD700',
                    'stopping': '#FFA500',
                    'failed': '#DC143C',
                    'unknown': '#D3D3D3'
                }.get(status, '#D3D3D3')
                
                G.add_node(name, 
                          label=service['display_name'],
                          color=color,
                          status=status,
                          priority=service['priority'])
            
            # Add edges
            for name, info in all_services.items():
                for req in info['required_services']:
                    req_service = req['service']
                    dep_type = req['type']
                    
                    # Edge style based on dependency type
                    edge_color = {
                        'required': '#FF0000',
                        'optional': '#FFA500', 
                        'conflict': '#8B0000',
                        'sequence': '#0000FF'
                    }.get(dep_type, '#808080')
                    
                    G.add_edge(req_service, name, 
                              type=dep_type,
                              color=edge_color)
            
            if len(G.nodes()) == 0:
                st.info("No services to display in graph.")
                return
            
            # Generate layout
            try:
                pos = nx.spring_layout(G, k=3, iterations=50)
            except:
                pos = nx.random_layout(G)
            
            # Create plotly figure
            fig = go.Figure()
            
            # Add edges
            for edge in G.edges(data=True):
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                
                fig.add_trace(go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(
                        color=edge[2].get('color', '#808080'),
                        width=2
                    ),
                    hoverinfo='none',
                    showlegend=False
                ))
                
                # Add arrow
                fig.add_annotation(
                    x=x1, y=y1,
                    ax=x0, ay=y0,
                    xref='x', yref='y',
                    axref='x', ayref='y',
                    arrowhead=2,
                    arrowsize=1,
                    arrowcolor=edge[2].get('color', '#808080'),
                    arrowwidth=2
                )
            
            # Add nodes
            for node, data in G.nodes(data=True):
                x, y = pos[node]
                
                fig.add_trace(go.Scatter(
                    x=[x],
                    y=[y],
                    mode='markers+text',
                    marker=dict(
                        color=data.get('color', '#D3D3D3'),
                        size=20,
                        line=dict(color='black', width=2)
                    ),
                    text=data.get('label', node),
                    textposition='middle center',
                    textfont=dict(size=10, color='white' if data.get('status') != 'unknown' else 'black'),
                    hovertemplate=f"<b>{data.get('label', node)}</b><br>" +
                                 f"Status: {data.get('status', 'unknown').title()}<br>" +
                                 f"Priority: {data.get('priority', 0)}<extra></extra>",
                    showlegend=False
                ))
            
            fig.update_layout(
                title="Service Dependency Graph",
                showlegend=False,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Legend
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Node Colors (Status):**")
                st.write("🟢 Running | 🔴 Stopped | 🟡 Starting | 🟠 Stopping | ❌ Failed | ⚪ Unknown")
            
            with col2:
                st.write("**Edge Colors (Dependency Type):**")
                st.write("🔴 Required | 🟠 Optional | 🟤 Conflict | 🔵 Sequence")
                
        except Exception as e:
            st.error(f"Failed to render dependency graph: {e}")
            st.info("Try adding services and dependencies to see the graph.")
    
    def _render_service_details(self, service_name: str, service_info: Dict[str, Any]):
        """Render detailed service information."""
        with st.expander(f"Service Details: {service_info['service']['display_name']}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Information:**")
                service = service_info['service']
                st.json({
                    'name': service_name,
                    'display_name': service['display_name'],
                    'description': service['description'],
                    'status': service_info['status'],
                    'priority': service['priority'],
                    'startup_timeout': service['startup_timeout'],
                    'shutdown_timeout': service['shutdown_timeout']
                })
            
            with col2:
                st.write("**Dependencies:**")
                if service_info['required_services']:
                    for req in service_info['required_services']:
                        st.write(f"• **{req['service']}** ({req['type']})")
                else:
                    st.write("No dependencies")
                
                st.write("**Dependents:**")
                if service_info['dependent_services']:
                    for dep in service_info['dependent_services']:
                        st.write(f"• **{dep['service']}** ({dep['type']})")
                else:
                    st.write("No dependents")
            
            # Validation issues
            validation = service_info['dependency_validation']
            if not validation['is_valid']:
                st.write("**Validation Issues:**")
                for issue in validation['issues']:
                    st.error(f"⚠️ {issue}")
    
    def _render_manage_services(self):
        """Render service management interface."""
        st.subheader("Manage Services")
        
        # Add new service
        with st.expander("➕ Add New Service", expanded=False):
            with st.form("add_service_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    service_name = st.text_input(
                        "Service Name*",
                        help="Unique identifier for the service"
                    )
                    
                    display_name = st.text_input(
                        "Display Name*",
                        help="Human-readable name"
                    )
                    
                    description = st.text_area(
                        "Description",
                        help="Optional description of the service"
                    )
                    
                    priority = st.number_input(
                        "Priority",
                        min_value=0,
                        max_value=100,
                        value=50,
                        help="Higher priority services start first"
                    )
                
                with col2:
                    startup_timeout = st.number_input(
                        "Startup Timeout (seconds)",
                        min_value=1,
                        max_value=300,
                        value=30
                    )
                    
                    shutdown_timeout = st.number_input(
                        "Shutdown Timeout (seconds)",
                        min_value=1,
                        max_value=300,
                        value=15
                    )
                    
                    restart_policy = st.selectbox(
                        "Restart Policy",
                        ["always", "on_failure", "never"]
                    )
                    
                    health_endpoint = st.text_input(
                        "Health Check Endpoint",
                        placeholder="http://localhost:8080/health"
                    )
                
                # Tags
                tags_input = st.text_input(
                    "Tags (comma-separated)",
                    placeholder="web, api, critical"
                )
                
                submitted = st.form_submit_button("Add Service")
                
                if submitted and service_name and display_name:
                    # Parse tags
                    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else []
                    
                    service = ServiceDefinition(
                        name=service_name,
                        display_name=display_name,
                        description=description,
                        startup_timeout=startup_timeout,
                        shutdown_timeout=shutdown_timeout,
                        health_check_endpoint=health_endpoint if health_endpoint else None,
                        restart_policy=restart_policy,
                        priority=priority,
                        tags=tags
                    )
                    
                    if self.dependency_manager.add_service(service):
                        st.success(f"Service '{display_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add service. Check logs for details.")
        
        # Existing services
        all_services = self.dependency_manager.get_all_services()
        
        if all_services:
            st.write("### Existing Services")
            
            service_names = list(all_services.keys())
            selected_service = st.selectbox(
                "Select Service to Edit/Remove",
                [''] + service_names,
                format_func=lambda x: f"{all_services[x]['service']['display_name']} ({x})" if x else "Select a service..."
            )
            
            if selected_service:
                service_info = all_services[selected_service]
                service = service_info['service']
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Edit service form
                    with st.form(f"edit_service_{selected_service}"):
                        st.write(f"**Editing: {service['display_name']}**")
                        
                        edit_col1, edit_col2 = st.columns(2)
                        
                        with edit_col1:
                            new_display_name = st.text_input(
                                "Display Name",
                                value=service['display_name']
                            )
                            
                            new_description = st.text_area(
                                "Description",
                                value=service['description']
                            )
                            
                            new_priority = st.number_input(
                                "Priority",
                                min_value=0,
                                max_value=100,
                                value=service['priority']
                            )
                        
                        with edit_col2:
                            new_startup_timeout = st.number_input(
                                "Startup Timeout",
                                min_value=1,
                                max_value=300,
                                value=service['startup_timeout']
                            )
                            
                            new_shutdown_timeout = st.number_input(
                                "Shutdown Timeout",
                                min_value=1,
                                max_value=300,
                                value=service['shutdown_timeout']
                            )
                        
                        new_tags = st.text_input(
                            "Tags",
                            value=', '.join(service.get('tags', []))
                        )
                        
                        update_submitted = st.form_submit_button("Update Service")
                        
                        if update_submitted:
                            tags = [tag.strip() for tag in new_tags.split(',') if tag.strip()] if new_tags else []
                            
                            updated_service = ServiceDefinition(
                                name=selected_service,
                                display_name=new_display_name,
                                description=new_description,
                                startup_timeout=new_startup_timeout,
                                shutdown_timeout=new_shutdown_timeout,
                                health_check_endpoint=service.get('health_check_endpoint'),
                                restart_policy=service.get('restart_policy', 'on_failure'),
                                priority=new_priority,
                                tags=tags
                            )
                            
                            if self.dependency_manager.add_service(updated_service):
                                st.success("Service updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update service.")
                
                with col2:
                    # Service status control
                    st.write("**Status Control:**")
                    current_status = ServiceStatus(service_info['status'])
                    
                    new_status = st.selectbox(
                        "Status",
                        [status.value for status in ServiceStatus],
                        index=list(ServiceStatus).index(current_status),
                        key=f"status_{selected_service}"
                    )
                    
                    if st.button("Update Status", key=f"update_status_{selected_service}"):
                        if self.dependency_manager.update_service_status(selected_service, ServiceStatus(new_status)):
                            st.success(f"Status updated to {new_status}")
                            st.rerun()
                    
                    st.divider()
                    
                    # Remove service
                    if st.button("🗑 Remove Service", key=f"remove_{selected_service}", type="secondary"):
                        if st.session_state.get(f'confirm_remove_{selected_service}'):
                            if self.dependency_manager.remove_service(selected_service):
                                st.success("Service removed successfully!")
                                del st.session_state[f'confirm_remove_{selected_service}']
                                st.rerun()
                            else:
                                st.error("Failed to remove service. Check dependencies.")
                        else:
                            st.session_state[f'confirm_remove_{selected_service}'] = True
                            st.warning("Click again to confirm removal")
        else:
            st.info("No services defined. Add your first service above.")
    
    def _render_manage_dependencies(self):
        """Render dependency management interface."""
        st.subheader("Manage Dependencies")
        
        all_services = self.dependency_manager.get_all_services()
        
        if len(all_services) < 2:
            st.info("Add at least 2 services to create dependencies.")
            return
        
        service_names = list(all_services.keys())
        
        # Add new dependency
        with st.expander("➕ Add New Dependency", expanded=False):
            with st.form("add_dependency_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    dependent_service = st.selectbox(
                        "Dependent Service*",
                        service_names,
                        format_func=lambda x: f"{all_services[x]['service']['display_name']} ({x})"
                    )
                    
                    required_service = st.selectbox(
                        "Required Service*",
                        [s for s in service_names if s != dependent_service],
                        format_func=lambda x: f"{all_services[x]['service']['display_name']} ({x})"
                    )
                
                with col2:
                    dependency_type = st.selectbox(
                        "Dependency Type*",
                        [dt.value for dt in DependencyType],
                        format_func=lambda x: {
                            'required': 'Required - Must be running',
                            'optional': 'Optional - Should be running',
                            'conflict': 'Conflict - Cannot run together',
                            'sequence': 'Sequence - Ordered startup/shutdown'
                        }.get(x, x.title())
                    )
                    
                    timeout_seconds = st.number_input(
                        "Timeout (seconds)",
                        min_value=1,
                        max_value=300,
                        value=30
                    )
                
                description = st.text_area(
                    "Description",
                    placeholder="Optional description of this dependency relationship"
                )
                
                submitted = st.form_submit_button("Add Dependency")
                
                if submitted and dependent_service and required_service:
                    dependency = ServiceDependency(
                        dependent_service=dependent_service,
                        required_service=required_service,
                        dependency_type=DependencyType(dependency_type),
                        timeout_seconds=timeout_seconds,
                        description=description,
                        created_by="dashboard_user"
                    )
                    
                    if self.dependency_manager.add_dependency(dependency):
                        st.success("Dependency added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add dependency. Check for circular dependencies.")
        
        # Existing dependencies
        st.write("### Existing Dependencies")
        
        # Build dependency table
        dependency_data = []
        for service_name, service_info in all_services.items():
            for req in service_info['required_services']:
                dependency_data.append({
                    'Dependent Service': all_services[service_name]['service']['display_name'],
                    'Required Service': all_services[req['service']]['service']['display_name'],
                    'Type': req['type'].title(),
                    'Dependent ID': service_name,
                    'Required ID': req['service']
                })
        
        if dependency_data:
            df = pd.DataFrame(dependency_data)
            st.dataframe(
                df[['Dependent Service', 'Required Service', 'Type']],
                use_container_width=True
            )
            
            # Remove dependency
            st.write("### Remove Dependency")
            
            if dependency_data:
                dependency_options = [
                    f"{row['Dependent Service']} → {row['Required Service']} ({row['Type']})"
                    for _, row in df.iterrows()
                ]
                
                selected_dep = st.selectbox(
                    "Select Dependency to Remove",
                    [''] + dependency_options
                )
                
                if selected_dep:
                    # Find the corresponding row
                    selected_idx = dependency_options.index(selected_dep)
                    selected_row = df.iloc[selected_idx]
                    
                    if st.button("🗑 Remove Dependency", type="secondary"):
                        if st.session_state.get('confirm_remove_dep'):
                            if self.dependency_manager.remove_dependency(
                                selected_row['Dependent ID'],
                                selected_row['Required ID']
                            ):
                                st.success("Dependency removed successfully!")
                                del st.session_state['confirm_remove_dep']
                                st.rerun()
                            else:
                                st.error("Failed to remove dependency.")
                        else:
                            st.session_state['confirm_remove_dep'] = True
                            st.warning("Click again to confirm removal")
        else:
            st.info("No dependencies defined. Add dependencies above.")
    
    def _render_startup_ordering(self):
        """Render startup ordering interface."""
        st.subheader("Startup/Shutdown Ordering")
        
        all_services = self.dependency_manager.get_all_services()
        
        if not all_services:
            st.info("No services defined.")
            return
        
        # Service selection for ordering
        selected_services = st.multiselect(
            "Select Services for Ordering",
            list(all_services.keys()),
            default=list(all_services.keys()),
            format_func=lambda x: f"{all_services[x]['service']['display_name']} ({x})"
        )
        
        if not selected_services:
            st.warning("Please select at least one service.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Startup Order")
            
            try:
                startup_order = self.dependency_manager.get_startup_order(selected_services)
                
                for i, group in enumerate(startup_order):
                    st.write(f"**Phase {i+1}:**")
                    for service in group:
                        service_info = all_services[service]
                        priority = service_info['service']['priority']
                        st.write(f"• {service_info['service']['display_name']} (Priority: {priority})")
                    
                    if i < len(startup_order) - 1:
                        st.write("⬇️")
                
            except Exception as e:
                st.error(f"Failed to calculate startup order: {e}")
        
        with col2:
            st.write("### Shutdown Order")
            
            try:
                shutdown_order = self.dependency_manager.get_shutdown_order(selected_services)
                
                for i, group in enumerate(shutdown_order):
                    st.write(f"**Phase {i+1}:**")
                    for service in group:
                        service_info = all_services[service]
                        st.write(f"• {service_info['service']['display_name']}")
                    
                    if i < len(shutdown_order) - 1:
                        st.write("⬇️")
                
            except Exception as e:
                st.error(f"Failed to calculate shutdown order: {e}")
        
        # Export startup sequence
        if st.button("📋 Generate Startup Script"):
            try:
                startup_order = self.dependency_manager.get_startup_order(selected_services)
                
                script_lines = [
                    "#!/bin/bash",
                    "# Generated service startup script",
                    f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "",
                    "set -e",
                    ""
                ]
                
                for i, group in enumerate(startup_order):
                    script_lines.append(f"# Phase {i+1}")
                    
                    # Start services in parallel within the same phase
                    for service in group:
                        script_lines.append(f"echo 'Starting {service}...'")
                        script_lines.append(f"# pm2 start {service} &")
                    
                    # Wait for phase completion
                    if len(group) > 1:
                        script_lines.append("wait")
                    
                    script_lines.append("sleep 2")
                    script_lines.append("")
                
                script_lines.append("echo 'All services started successfully!'")
                
                script_content = '\n'.join(script_lines)
                
                st.code(script_content, language='bash')
                
                # Download button would be added here in a real implementation
                st.info("Copy the script above to use for automated service startup.")
                
            except Exception as e:
                st.error(f"Failed to generate startup script: {e}")
    
    def _render_dependency_validation(self):
        """Render dependency validation interface."""
        st.subheader("Dependency Validation")
        
        all_services = self.dependency_manager.get_all_services()
        
        if not all_services:
            st.info("No services defined.")
            return
        
        # Global validation summary
        valid_services = [name for name, info in all_services.items() if info['dependency_validation']['is_valid']]
        invalid_services = [name for name, info in all_services.items() if not info['dependency_validation']['is_valid']]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Services", len(all_services))
        
        with col2:
            st.metric("Valid Services", len(valid_services), delta="✅" if len(invalid_services) == 0 else None)
        
        with col3:
            st.metric("Invalid Services", len(invalid_services), delta="⚠️" if len(invalid_services) > 0 else None)
        
        # Validation details
        if invalid_services:
            st.write("### Validation Issues")
            
            for service_name in invalid_services:
                service_info = all_services[service_name]
                service = service_info['service']
                issues = service_info['dependency_validation']['issues']
                
                with st.expander(f"⚠️ {service['display_name']} ({service_name})", expanded=True):
                    st.write(f"**Status:** {service_info['status'].title()}")
                    
                    st.write("**Issues:**")
                    for issue in issues:
                        st.error(f"• {issue}")
                    
                    # Suggested actions
                    st.write("**Suggested Actions:**")
                    for issue in issues:
                        if "Required service" in issue and "is stopped" in issue:
                            st.info("• Start the required service")
                        elif "Required service" in issue and "is failed" in issue:
                            st.info("• Fix and restart the required service")
                        elif "Conflicting service" in issue:
                            st.info("• Stop the conflicting service before starting this one")
        else:
            st.success("🎉 All service dependencies are valid!")
        
        # Service validation table
        st.write("### Service Validation Details")
        
        validation_data = []
        for name, info in all_services.items():
            service = info['service']
            validation = info['dependency_validation']
            
            validation_data.append({
                'Service': service['display_name'],
                'Status': info['status'].title(),
                'Valid': '✅' if validation['is_valid'] else '❌',
                'Issues': len(validation['issues']),
                'Dependencies': len(info['required_services']),
                'Service ID': name
            })
        
        df = pd.DataFrame(validation_data)
        st.dataframe(
            df[['Service', 'Status', 'Valid', 'Issues', 'Dependencies']],
            use_container_width=True,
            column_config={
                'Valid': st.column_config.TextColumn('Valid', width='small'),
                'Issues': st.column_config.NumberColumn('Issues', width='small'),
                'Dependencies': st.column_config.NumberColumn('Deps', width='small')
            }
        )
        
        # Manual validation trigger
        st.write("### Manual Validation")
        
        selected_service = st.selectbox(
            "Validate Specific Service",
            [''] + list(all_services.keys()),
            format_func=lambda x: f"{all_services[x]['service']['display_name']} ({x})" if x else "Select a service..."
        )
        
        if selected_service and st.button("🔍 Validate Service"):
            is_valid, issues = self.dependency_manager.validate_dependencies(selected_service)
            
            if is_valid:
                st.success(f"✅ {all_services[selected_service]['service']['display_name']} dependencies are valid!")
            else:
                st.error(f"❌ {all_services[selected_service]['service']['display_name']} has dependency issues:")
                for issue in issues:
                    st.write(f"• {issue}")
        
        # Export/Import configuration
        st.write("### Configuration Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Export Configuration"):
                config = self.dependency_manager.export_configuration()
                
                # Display as downloadable JSON
                config_json = json.dumps(config, indent=2, default=str)
                st.code(config_json, language='json')
                
                st.info("Copy the configuration above to save or share.")
        
        with col2:
            st.write("**Import Configuration:**")
            uploaded_file = st.file_uploader(
                "Choose configuration file",
                type=['json'],
                help="Upload a previously exported configuration file"
            )
            
            if uploaded_file is not None:
                try:
                    config = json.load(uploaded_file)
                    
                    if st.button("📥 Import Configuration"):
                        if self.dependency_manager.import_configuration(config):
                            st.success("Configuration imported successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to import configuration. Check format and dependencies.")
                
                except json.JSONDecodeError:
                    st.error("Invalid JSON file format.")