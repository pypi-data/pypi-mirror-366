"""
Analytics and metrics widgets for dashboard display.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .base_widget import BaseWidget, WidgetConfig
from ..layout.models import WidgetType, WidgetSize


class MetricsChartWidget(BaseWidget):
    """Widget for displaying customizable metrics charts."""
    
    widget_type = WidgetType.METRICS_CHART
    widget_name = "Metrics Chart"
    widget_description = "Customizable charts for displaying various metrics"
    widget_icon = "📊"
    widget_category = "Analytics"
    default_size = WidgetSize.LARGE
    
    config_schema = {
        'chart_type': {'type': 'select', 'options': ['line', 'bar', 'area', 'scatter'], 'default': 'line', 'description': 'Chart type'},
        'time_range': {'type': 'select', 'options': ['1h', '6h', '24h', '7d', '30d'], 'default': '24h', 'description': 'Time range'},
        'metrics': {'type': 'multiselect', 'options': ['cpu', 'memory', 'disk', 'network'], 'default': ['cpu', 'memory'], 'description': 'Metrics to display'},
        'show_trend': {'type': 'boolean', 'default': True, 'description': 'Show trend line'},
        'show_legend': {'type': 'boolean', 'default': True, 'description': 'Show chart legend'},
        'auto_scale': {'type': 'boolean', 'default': True, 'description': 'Auto-scale Y axis'}
    }
    
    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self._sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample time series data for demonstration."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Generate hourly data points
        time_points = pd.date_range(start=start_time, end=end_time, freq='H')
        
        data = []
        for timestamp in time_points:
            # Generate realistic sample data with some randomness
            base_cpu = 45 + 20 * np.sin(timestamp.hour * np.pi / 12) + np.random.normal(0, 5)
            base_memory = 60 + 15 * np.cos(timestamp.hour * np.pi / 8) + np.random.normal(0, 3)
            base_disk = 75 + 5 * np.sin(timestamp.hour * np.pi / 24) + np.random.normal(0, 2)
            base_network = 30 + 25 * np.random.random()
            
            data.append({
                'timestamp': timestamp,
                'cpu': max(0, min(100, base_cpu)),
                'memory': max(0, min(100, base_memory)),
                'disk': max(0, min(100, base_disk)),
                'network': max(0, min(100, base_network))
            })
        
        return pd.DataFrame(data)
    
    def _render_content(self) -> None:
        """Render metrics chart content."""
        try:
            chart_type = self.config.config.get('chart_type', 'line')
            time_range = self.config.config.get('time_range', '24h')
            metrics = self.config.config.get('metrics', ['cpu', 'memory'])
            show_trend = self.config.config.get('show_trend', True)
            show_legend = self.config.config.get('show_legend', True)
            auto_scale = self.config.config.get('auto_scale', True)
            
            # Filter data based on time range
            filtered_data = self._filter_data_by_time_range(time_range)
            
            if filtered_data.empty:
                st.info("No data available for the selected time range")
                return
            
            # Create chart based on type
            if chart_type == 'line':
                fig = self._create_line_chart(filtered_data, metrics, show_trend, show_legend, auto_scale)
            elif chart_type == 'bar':
                fig = self._create_bar_chart(filtered_data, metrics, show_legend)
            elif chart_type == 'area':
                fig = self._create_area_chart(filtered_data, metrics, show_legend, auto_scale)
            else:  # scatter
                fig = self._create_scatter_chart(filtered_data, metrics, show_legend, auto_scale)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show summary statistics
            self._render_summary_stats(filtered_data, metrics)
            
        except Exception as e:
            st.error(f"Failed to render metrics chart: {e}")
    
    def _filter_data_by_time_range(self, time_range: str) -> pd.DataFrame:
        """Filter data based on selected time range."""
        now = datetime.now()
        
        if time_range == '1h':
            start_time = now - timedelta(hours=1)
        elif time_range == '6h':
            start_time = now - timedelta(hours=6)
        elif time_range == '24h':
            start_time = now - timedelta(hours=24)
        elif time_range == '7d':
            start_time = now - timedelta(days=7)
        elif time_range == '30d':
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(hours=24)
        
        return self._sample_data[self._sample_data['timestamp'] >= start_time].copy()
    
    def _create_line_chart(self, data: pd.DataFrame, metrics: List[str], show_trend: bool, show_legend: bool, auto_scale: bool) -> go.Figure:
        """Create line chart."""
        fig = go.Figure()
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i, metric in enumerate(metrics):
            if metric in data.columns:
                color = colors[i % len(colors)]
                
                # Add main line
                fig.add_trace(go.Scatter(
                    x=data['timestamp'],
                    y=data[metric],
                    mode='lines+markers',
                    name=metric.upper(),
                    line=dict(color=color, width=2),
                    marker=dict(size=4)
                ))
                
                # Add trend line if requested
                if show_trend and len(data) > 1:
                    z = np.polyfit(range(len(data)), data[metric], 1)
                    trend_line = np.poly1d(z)(range(len(data)))
                    
                    fig.add_trace(go.Scatter(
                        x=data['timestamp'],
                        y=trend_line,
                        mode='lines',
                        name=f'{metric.upper()} Trend',
                        line=dict(color=color, width=1, dash='dash'),
                        opacity=0.7,
                        showlegend=show_legend
                    ))
        
        fig.update_layout(
            title="System Metrics Over Time",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            showlegend=show_legend,
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        if auto_scale:
            fig.update_yaxis(range=[0, 100])
        
        return fig
    
    def _create_bar_chart(self, data: pd.DataFrame, metrics: List[str], show_legend: bool) -> go.Figure:
        """Create bar chart showing latest values."""
        latest_data = data.iloc[-1] if not data.empty else {}
        
        fig = go.Figure()
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        values = []
        labels = []
        chart_colors = []
        
        for i, metric in enumerate(metrics):
            if metric in latest_data:
                values.append(latest_data[metric])
                labels.append(metric.upper())
                chart_colors.append(colors[i % len(colors)])
        
        fig.add_trace(go.Bar(
            x=labels,
            y=values,
            marker_color=chart_colors,
            showlegend=show_legend
        ))
        
        fig.update_layout(
            title="Current Metrics",
            xaxis_title="Metric",
            yaxis_title="Usage (%)",
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def _create_area_chart(self, data: pd.DataFrame, metrics: List[str], show_legend: bool, auto_scale: bool) -> go.Figure:
        """Create area chart."""
        fig = go.Figure()
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i, metric in enumerate(metrics):
            if metric in data.columns:
                fig.add_trace(go.Scatter(
                    x=data['timestamp'],
                    y=data[metric],
                    mode='lines',
                    name=metric.upper(),
                    fill='tonexty' if i > 0 else 'tozeroy',
                    fillcolor=colors[i % len(colors)],
                    line=dict(color=colors[i % len(colors)], width=2),
                    opacity=0.7
                ))
        
        fig.update_layout(
            title="System Metrics (Stacked)",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            showlegend=show_legend,
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        if auto_scale:
            fig.update_yaxis(range=[0, 100])
        
        return fig
    
    def _create_scatter_chart(self, data: pd.DataFrame, metrics: List[str], show_legend: bool, auto_scale: bool) -> go.Figure:
        """Create scatter chart showing correlation between metrics."""
        fig = go.Figure()
        
        if len(metrics) >= 2:
            metric_x = metrics[0]
            metric_y = metrics[1]
            
            if metric_x in data.columns and metric_y in data.columns:
                fig.add_trace(go.Scatter(
                    x=data[metric_x],
                    y=data[metric_y],
                    mode='markers',
                    name=f'{metric_x.upper()} vs {metric_y.upper()}',
                    marker=dict(
                        size=8,
                        color=data.index,
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Time Order")
                    ),
                    text=data['timestamp'].dt.strftime('%H:%M'),
                    hovertemplate=f'<b>{metric_x.upper()}</b>: %{{x}}<br><b>{metric_y.upper()}</b>: %{{y}}<br><b>Time</b>: %{{text}}<extra></extra>'
                ))
        
        fig.update_layout(
            title=f"Correlation: {metrics[0].upper()} vs {metrics[1].upper()}" if len(metrics) >= 2 else "Scatter Plot",
            xaxis_title=metrics[0].upper() if metrics else "X",
            yaxis_title=metrics[1].upper() if len(metrics) > 1 else "Y",
            showlegend=show_legend,
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        if auto_scale:
            fig.update_xaxis(range=[0, 100])
            fig.update_yaxis(range=[0, 100])
        
        return fig
    
    def _render_summary_stats(self, data: pd.DataFrame, metrics: List[str]) -> None:
        """Render summary statistics."""
        if data.empty or not metrics:
            return
        
        st.markdown("#### Summary Statistics")
        
        cols = st.columns(len(metrics))
        
        for i, metric in enumerate(metrics):
            if metric in data.columns:
                with cols[i]:
                    values = data[metric]
                    st.metric(
                        f"{metric.upper()} Avg",
                        f"{values.mean():.1f}%",
                        delta=f"±{values.std():.1f}%"
                    )
                    st.caption(f"Min: {values.min():.1f}% | Max: {values.max():.1f}%")
    
    def get_config_ui(self) -> Dict[str, Any]:
        """Get configuration UI for metrics chart widget."""
        config_values = super().get_config_ui()
        
        # Widget-specific configuration
        with st.expander("Metrics Chart Settings"):
            config_values['chart_type'] = st.selectbox(
                "Chart Type",
                options=['line', 'bar', 'area', 'scatter'],
                index=['line', 'bar', 'area', 'scatter'].index(self.config.config.get('chart_type', 'line')),
                key=f"config_chart_type_{self.config.widget_id}"
            )
            
            config_values['time_range'] = st.selectbox(
                "Time Range",
                options=['1h', '6h', '24h', '7d', '30d'],
                index=['1h', '6h', '24h', '7d', '30d'].index(self.config.config.get('time_range', '24h')),
                key=f"config_time_range_{self.config.widget_id}"
            )
            
            config_values['metrics'] = st.multiselect(
                "Metrics to Display",
                options=['cpu', 'memory', 'disk', 'network'],
                default=self.config.config.get('metrics', ['cpu', 'memory']),
                key=f"config_metrics_{self.config.widget_id}"
            )
            
            config_values['show_trend'] = st.checkbox(
                "Show Trend Lines",
                value=self.config.config.get('show_trend', True),
                key=f"config_show_trend_{self.config.widget_id}"
            )
            
            config_values['show_legend'] = st.checkbox(
                "Show Legend",
                value=self.config.config.get('show_legend', True),
                key=f"config_show_legend_{self.config.widget_id}"
            )
            
            config_values['auto_scale'] = st.checkbox(
                "Auto-scale Y Axis",
                value=self.config.config.get('auto_scale', True),
                key=f"config_auto_scale_{self.config.widget_id}"
            )
        
        return config_values


class PerformanceGraphWidget(BaseWidget):
    """Widget for displaying performance trends and analysis."""
    
    widget_type = WidgetType.PERFORMANCE_GRAPH
    widget_name = "Performance Graph"
    widget_description = "Performance trending and analysis charts"
    widget_icon = "⚡"
    widget_category = "Performance"
    default_size = WidgetSize.LARGE
    
    config_schema = {
        'graph_type': {'type': 'select', 'options': ['trends', 'distribution', 'heatmap'], 'default': 'trends', 'description': 'Graph type'},
        'performance_metric': {'type': 'select', 'options': ['response_time', 'throughput', 'error_rate', 'resource_usage'], 'default': 'response_time', 'description': 'Primary metric'},
        'aggregation': {'type': 'select', 'options': ['avg', 'p95', 'p99', 'max'], 'default': 'avg', 'description': 'Data aggregation method'},
        'show_thresholds': {'type': 'boolean', 'default': True, 'description': 'Show performance thresholds'},
        'anomaly_detection': {'type': 'boolean', 'default': True, 'description': 'Highlight anomalies'}
    }
    
    def __init__(self, config: WidgetConfig):
        super().__init__(config)
        self._performance_data = self._generate_performance_data()
    
    def _generate_performance_data(self) -> pd.DataFrame:
        """Generate sample performance data."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        time_points = pd.date_range(start=start_time, end=end_time, freq='5min')
        
        data = []
        for i, timestamp in enumerate(time_points):
            # Simulate performance patterns
            hour = timestamp.hour
            
            # Response time - higher during peak hours
            base_response = 100 + 50 * (1 if 9 <= hour <= 17 else 0.3)
            response_time = base_response + np.random.normal(0, 20)
            
            # Throughput - inverse correlation with response time
            throughput = max(10, 200 - response_time/2 + np.random.normal(0, 10))
            
            # Error rate - spikes occasionally
            error_rate = max(0, 0.5 + (2 if np.random.random() < 0.05 else 0) + np.random.normal(0, 0.2))
            
            # Resource usage
            resource_usage = min(100, max(0, 40 + response_time/5 + np.random.normal(0, 5)))
            
            data.append({
                'timestamp': timestamp,
                'response_time': max(0, response_time),
                'throughput': max(0, throughput),
                'error_rate': max(0, min(100, error_rate)),
                'resource_usage': resource_usage
            })
        
        return pd.DataFrame(data)
    
    def _render_content(self) -> None:
        """Render performance graph content."""
        try:
            graph_type = self.config.config.get('graph_type', 'trends')
            performance_metric = self.config.config.get('performance_metric', 'response_time')
            aggregation = self.config.config.get('aggregation', 'avg')
            show_thresholds = self.config.config.get('show_thresholds', True)
            anomaly_detection = self.config.config.get('anomaly_detection', True)
            
            if graph_type == 'trends':
                fig = self._create_trend_graph(performance_metric, aggregation, show_thresholds, anomaly_detection)
            elif graph_type == 'distribution':
                fig = self._create_distribution_graph(performance_metric)
            else:  # heatmap
                fig = self._create_heatmap_graph()
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show performance insights
            self._render_performance_insights(performance_metric)
            
        except Exception as e:
            st.error(f"Failed to render performance graph: {e}")
    
    def _create_trend_graph(self, metric: str, aggregation: str, show_thresholds: bool, anomaly_detection: bool) -> go.Figure:
        """Create performance trend graph."""
        fig = go.Figure()
        
        data = self._performance_data.copy()
        
        # Aggregate data if needed
        if aggregation != 'avg':
            # For demo, we'll just use the raw data
            pass
        
        # Main trend line
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data[metric],
            mode='lines+markers',
            name=f'{metric.replace("_", " ").title()} ({aggregation.upper()})',
            line=dict(color='#2E86AB', width=2),
            marker=dict(size=3)
        ))
        
        # Add threshold lines
        if show_thresholds:
            thresholds = self._get_performance_thresholds(metric)
            
            if 'warning' in thresholds:
                fig.add_hline(
                    y=thresholds['warning'],
                    line_dash="dash",
                    line_color="orange",
                    annotation_text="Warning Threshold"
                )
            
            if 'critical' in thresholds:
                fig.add_hline(
                    y=thresholds['critical'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Critical Threshold"
                )
        
        # Highlight anomalies
        if anomaly_detection:
            anomalies = self._detect_anomalies(data[metric])
            if len(anomalies) > 0:
                anomaly_data = data.iloc[anomalies]
                fig.add_trace(go.Scatter(
                    x=anomaly_data['timestamp'],
                    y=anomaly_data[metric],
                    mode='markers',
                    name='Anomalies',
                    marker=dict(
                        size=8,
                        color='red',
                        symbol='diamond'
                    ),
                    showlegend=True
                ))
        
        fig.update_layout(
            title=f'{metric.replace("_", " ").title()} Performance Trend',
            xaxis_title='Time',
            yaxis_title=self._get_metric_unit(metric),
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def _create_distribution_graph(self, metric: str) -> go.Figure:
        """Create performance distribution graph."""
        fig = go.Figure()
        
        values = self._performance_data[metric]
        
        # Histogram
        fig.add_trace(go.Histogram(
            x=values,
            nbinsx=30,
            name='Distribution',
            marker_color='#2E86AB',
            opacity=0.7
        ))
        
        # Add percentile lines
        percentiles = [50, 95, 99]
        colors = ['green', 'orange', 'red']
        
        for i, p in enumerate(percentiles):
            value = np.percentile(values, p)
            fig.add_vline(
                x=value,
                line_dash="dash",
                line_color=colors[i],
                annotation_text=f"P{p}: {value:.1f}"
            )
        
        fig.update_layout(
            title=f'{metric.replace("_", " ").title()} Distribution',
            xaxis_title=self._get_metric_unit(metric),
            yaxis_title='Frequency',
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def _create_heatmap_graph(self) -> go.Figure:
        """Create performance heatmap by hour and day."""
        data = self._performance_data.copy()
        data['hour'] = data['timestamp'].dt.hour
        data['day'] = data['timestamp'].dt.day_name()
        
        # Create pivot table for heatmap
        pivot_data = data.groupby(['day', 'hour'])['response_time'].mean().unstack()
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='RdYlBu_r',
            showscale=True,
            colorbar=dict(title="Avg Response Time (ms)")
        ))
        
        fig.update_layout(
            title='Performance Heatmap (Response Time by Hour)',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=400,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        return fig
    
    def _get_performance_thresholds(self, metric: str) -> Dict[str, float]:
        """Get performance thresholds for a metric."""
        thresholds = {
            'response_time': {'warning': 200, 'critical': 500},
            'throughput': {'warning': 50, 'critical': 20},
            'error_rate': {'warning': 2, 'critical': 5},
            'resource_usage': {'warning': 80, 'critical': 95}
        }
        return thresholds.get(metric, {})
    
    def _get_metric_unit(self, metric: str) -> str:
        """Get unit for a metric."""
        units = {
            'response_time': 'Response Time (ms)',
            'throughput': 'Requests/sec',
            'error_rate': 'Error Rate (%)',
            'resource_usage': 'Resource Usage (%)'
        }
        return units.get(metric, metric.replace('_', ' ').title())
    
    def _detect_anomalies(self, values: pd.Series) -> List[int]:
        """Simple anomaly detection using IQR method."""
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = values[(values < lower_bound) | (values > upper_bound)]
        return anomalies.index.tolist()
    
    def _render_performance_insights(self, metric: str) -> None:
        """Render performance insights."""
        st.markdown("#### Performance Insights")
        
        values = self._performance_data[metric]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Average",
                f"{values.mean():.1f}",
                delta=f"±{values.std():.1f}"
            )
        
        with col2:
            st.metric(
                "95th Percentile",
                f"{np.percentile(values, 95):.1f}",
                delta=f"vs P50: {np.percentile(values, 95) - np.percentile(values, 50):.1f}"
            )
        
        with col3:
            anomaly_count = len(self._detect_anomalies(values))
            st.metric(
                "Anomalies",
                anomaly_count,
                delta=f"{anomaly_count / len(values) * 100:.1f}% of data"
            )
    
    def get_config_ui(self) -> Dict[str, Any]:
        """Get configuration UI for performance graph widget."""
        config_values = super().get_config_ui()
        
        # Widget-specific configuration
        with st.expander("Performance Graph Settings"):
            config_values['graph_type'] = st.selectbox(
                "Graph Type",
                options=['trends', 'distribution', 'heatmap'],
                index=['trends', 'distribution', 'heatmap'].index(self.config.config.get('graph_type', 'trends')),
                key=f"config_graph_type_{self.config.widget_id}"
            )
            
            config_values['performance_metric'] = st.selectbox(
                "Primary Metric",
                options=['response_time', 'throughput', 'error_rate', 'resource_usage'],
                index=['response_time', 'throughput', 'error_rate', 'resource_usage'].index(
                    self.config.config.get('performance_metric', 'response_time')
                ),
                key=f"config_perf_metric_{self.config.widget_id}"
            )
            
            config_values['aggregation'] = st.selectbox(
                "Aggregation Method",
                options=['avg', 'p95', 'p99', 'max'],
                index=['avg', 'p95', 'p99', 'max'].index(self.config.config.get('aggregation', 'avg')),
                key=f"config_aggregation_{self.config.widget_id}"
            )
            
            config_values['show_thresholds'] = st.checkbox(
                "Show Performance Thresholds",
                value=self.config.config.get('show_thresholds', True),
                key=f"config_show_thresholds_{self.config.widget_id}"
            )
            
            config_values['anomaly_detection'] = st.checkbox(
                "Highlight Anomalies",
                value=self.config.config.get('anomaly_detection', True),
                key=f"config_anomaly_detection_{self.config.widget_id}"
            )
        
        return config_values