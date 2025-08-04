"""Data source monitoring widget for the dashboard."""

import streamlit as st
from typing import Dict, Any, Optional
import asyncio

from ..data_sources import DataSourceMetrics, DataSourceMonitoringUI, DataSourceControls
from ...data_sources.orchestrator import DataSourceOrchestrator
from ...utils.logger import get_logger

logger = get_logger(__name__)


class DataSourceWidget:
    """Widget for data source monitoring in the main dashboard."""
    
    def __init__(self, orchestrator: Optional[DataSourceOrchestrator] = None):
        """Initialize the widget.
        
        Args:
            orchestrator: Optional orchestrator instance
        """
        self.orchestrator = orchestrator
        self.metrics = DataSourceMetrics(orchestrator)
        self.controls = DataSourceControls(orchestrator)
        self.ui = DataSourceMonitoringUI(self.metrics, self.controls)
    
    def render_summary(self) -> Dict[str, Any]:
        """Render a summary card for the main dashboard.
        
        Returns:
            Summary statistics
        """
        # Get metrics
        metrics = asyncio.run(self.metrics.get_source_metrics())
        
        if not metrics or 'overall' not in metrics:
            st.info("Data sources not configured")
            return {}
        
        overall = metrics['overall']
        
        # Create summary card
        with st.container():
            st.markdown("### 📊 Data Sources")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Items",
                    f"{overall.get('total_items', 0):,}"
                )
            
            with col2:
                st.metric(
                    "Active Sources",
                    overall.get('active_sources', 0)
                )
            
            with col3:
                success_rate = overall.get('success_rate', 0)
                st.metric(
                    "Success Rate",
                    f"{success_rate:.1f}%"
                )
            
            # Quick status indicators
            source_statuses = []
            for source_type in ['gmail', 'fireflies', 'google_drive']:
                if source_type in metrics:
                    source_data = metrics[source_type]
                    sync_state = source_data.get('sync_state', {})
                    
                    if sync_state and sync_state.get('is_active'):
                        if sync_state.get('error_count', 0) > 0:
                            status = "⚠️"  # Warning
                        else:
                            status = "✅"  # OK
                    else:
                        status = "❌"  # Inactive
                    
                    source_statuses.append(f"{status} {source_type.title()}")
            
            if source_statuses:
                st.caption(" | ".join(source_statuses))
        
        return overall
    
    def render_full(self):
        """Render the full data source monitoring interface."""
        self.ui.render()
    
    @staticmethod
    def get_widget_info() -> Dict[str, Any]:
        """Get widget information for registration.
        
        Returns:
            Widget metadata
        """
        return {
            'id': 'data_sources',
            'name': 'Data Sources',
            'description': 'Monitor data source integrations',
            'category': 'monitoring',
            'icon': '📊',
            'default_size': 'medium',
            'min_refresh_interval': 30  # seconds
        }