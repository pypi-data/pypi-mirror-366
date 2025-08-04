"""
HTML exporter for dashboard data with interactive features.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import base64

from .export_manager import ExportJob


class HTMLExporter:
    """
    Exports dashboard data to HTML format with interactive features and styling.
    """
    
    def export(self, data: Dict[str, Any], output_path: str, job: ExportJob) -> bool:
        """
        Export data to HTML format.
        
        Args:
            data: Data to export
            output_path: Output file path
            job: Export job configuration
            
        Returns:
            True if export successful
        """
        try:
            # Generate HTML content
            html_content = self._generate_html_content(data, job)
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            job.progress = 100.0
            return True
            
        except Exception as e:
            job.error_message = f"HTML export error: {str(e)}"
            return False
    
    def _generate_html_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate complete HTML content."""
        html_parts = []
        
        # HTML header with CSS and JavaScript
        html_parts.append(self._get_html_header(job.title))
        
        # Navigation
        html_parts.append(self._generate_navigation(data, job))
        
        # Main content container
        html_parts.append('<div class="main-content">')
        
        # Title section
        html_parts.append(self._generate_title_section(job, data.get('export_metadata', {})))
        
        # Content sections based on export type
        if job.export_type.value == 'system_metrics':
            html_parts.append(self._generate_system_metrics_content(data, job))
        elif job.export_type.value == 'performance_report':
            html_parts.append(self._generate_performance_content(data, job))
        elif job.export_type.value == 'dashboard_config':
            html_parts.append(self._generate_config_content(data, job))
        elif job.export_type.value == 'full_backup':
            html_parts.append(self._generate_backup_content(data, job))
        else:
            html_parts.append(self._generate_generic_content(data, job))
        
        # Close main content
        html_parts.append('</div>')
        
        # Footer and JavaScript
        html_parts.append(self._get_html_footer())
        
        return '\n'.join(html_parts)
    
    def _get_html_header(self, title: str) -> str:
        """Generate HTML header with modern CSS and JavaScript."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #2E86AB;
            --secondary-color: #A8E6CF;
            --accent-color: #4ECDC4;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --error-color: #dc3545;
            --background-color: #f8f9fa;
            --card-background: #ffffff;
            --text-color: #333333;
            --text-muted: #666666;
            --border-color: #dee2e6;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 300;
            margin-bottom: 0.5rem;
        }}
        
        .header .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .nav-tabs {{
            display: flex;
            background: white;
            border-radius: 8px;
            padding: 4px;
            margin: -1rem 0 2rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .nav-tab {{
            flex: 1;
            padding: 12px 20px;
            text-align: center;
            background: transparent;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        
        .nav-tab:hover {{
            background: var(--background-color);
        }}
        
        .nav-tab.active {{
            background: var(--primary-color);
            color: white;
        }}
        
        .main-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .section {{
            background: var(--card-background);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            color: var(--primary-color);
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--secondary-color);
        }}
        
        .grid {{
            display: grid;
            gap: 1.5rem;
        }}
        
        .grid-2 {{ grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }}
        .grid-3 {{ grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }}
        .grid-4 {{ grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }}
        
        .card {{
            background: var(--card-background);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .metric-card {{
            text-align: center;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border: none;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
        }}
        
        .status-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .status-healthy {{ background: #d4edda; color: #155724; }}
        .status-warning {{ background: #fff3cd; color: #856404; }}
        .status-error {{ background: #f8d7da; color: #721c24; }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .data-table th {{
            background: var(--primary-color);
            color: white;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .data-table tr:hover {{
            background: var(--background-color);
        }}
        
        .data-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .footer {{
            background: var(--text-color);
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
        }}
        
        .collapsible {{
            cursor: pointer;
            user-select: none;
        }}
        
        .collapsible:hover {{
            background: var(--background-color);
        }}
        
        .collapsible-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}
        
        .collapsible-content.active {{
            max-height: 1000px;
        }}
        
        .json-viewer {{
            background: #f8f9fa;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 1rem;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        
        .search-box {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid var(--border-color);
            border-radius: 6px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: var(--primary-color);
        }}
        
        @media (max-width: 768px) {{
            .grid-2, .grid-3, .grid-4 {{
                grid-template-columns: 1fr;
            }}
            
            .nav-tabs {{
                flex-direction: column;
            }}
            
            .main-content {{
                padding: 0 10px;
            }}
        }}
        
        .hidden {{ display: none; }}
        .fade-in {{ animation: fadeIn 0.5s ease-in; }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>'''
    
    def _generate_navigation(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate navigation tabs."""
        tabs = []
        
        if job.export_type.value == 'system_metrics':
            tabs = [
                ('overview', 'Overview'),
                ('metrics', 'System Metrics'),
                ('processes', 'Processes'),
                ('queue', 'Queue Status')
            ]
        elif job.export_type.value == 'performance_report':
            tabs = [
                ('overview', 'Overview'),
                ('metrics', 'Performance Metrics'),
                ('analysis', 'Analysis'),
                ('recommendations', 'Recommendations')
            ]
        elif job.export_type.value == 'dashboard_config':
            tabs = [
                ('overview', 'Overview'),
                ('layouts', 'Layouts'),
                ('templates', 'Templates')
            ]
        elif job.export_type.value == 'full_backup':
            tabs = [
                ('overview', 'Overview'),
                ('config', 'Configuration'),
                ('layouts', 'Layouts'),
                ('metrics', 'Metrics Snapshot')
            ]
        else:
            tabs = [('overview', 'Overview'), ('data', 'Data')]
        
        nav_html = '<div class="nav-tabs">'
        for i, (tab_id, tab_name) in enumerate(tabs):
            active_class = ' active' if i == 0 else ''
            nav_html += f'<button class="nav-tab{active_class}" onclick="showTab(\'{tab_id}\')">{tab_name}</button>'
        nav_html += '</div>'
        
        return nav_html
    
    def _generate_title_section(self, job: ExportJob, metadata: Dict[str, Any]) -> str:
        """Generate title section."""
        return f'''
<div class="header">
    <div class="container">
        <h1>{job.title}</h1>
        <p class="subtitle">{job.description or f"{job.export_type.value.replace('_', ' ').title()} Report"}</p>
        <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
    </div>
</div>'''
    
    def _generate_system_metrics_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate system metrics content."""
        content_parts = []
        
        # Overview tab
        content_parts.append('<div id="overview" class="tab-content">')
        content_parts.append('<div class="section fade-in">')
        content_parts.append('<h2 class="section-title">System Overview</h2>')
        
        if 'system_metrics' in data:
            metrics = data['system_metrics']
            content_parts.append('<div class="grid grid-4">')
            
            # CPU card
            if 'cpu' in metrics:
                status_class = 'status-healthy' if metrics['cpu'] < 80 else 'status-warning' if metrics['cpu'] < 95 else 'status-error'
                content_parts.append(f'''
                <div class="card metric-card">
                    <div class="metric-value">{metrics['cpu']}%</div>
                    <div class="metric-label">CPU Usage</div>
                    <div class="status-badge {status_class}">
                        {"Healthy" if metrics['cpu'] < 80 else "Warning" if metrics['cpu'] < 95 else "Critical"}
                    </div>
                </div>''')
            
            # Memory card
            if 'memory' in metrics:
                memory = metrics['memory']
                percent = memory.get('percent', 0)
                status_class = 'status-healthy' if percent < 80 else 'status-warning' if percent < 95 else 'status-error'
                content_parts.append(f'''
                <div class="card metric-card">
                    <div class="metric-value">{percent:.1f}%</div>
                    <div class="metric-label">Memory Usage</div>
                    <div class="status-badge {status_class}">
                        {"Healthy" if percent < 80 else "Warning" if percent < 95 else "Critical"}
                    </div>
                </div>''')
            
            # Disk card
            if 'disk' in metrics:
                disk = metrics['disk']
                percent = disk.get('percent', 0)
                status_class = 'status-healthy' if percent < 80 else 'status-warning' if percent < 95 else 'status-error'
                content_parts.append(f'''
                <div class="card metric-card">
                    <div class="metric-value">{percent:.1f}%</div>
                    <div class="metric-label">Disk Usage</div>
                    <div class="status-badge {status_class}">
                        {"Healthy" if percent < 80 else "Warning" if percent < 95 else "Critical"}
                    </div>
                </div>''')
            
            # Qdrant card
            if 'qdrant' in metrics:
                qdrant = metrics['qdrant']
                status = qdrant.get('status', 'unknown')
                status_class = 'status-healthy' if status == 'healthy' else 'status-error'
                content_parts.append(f'''
                <div class="card metric-card">
                    <div class="metric-value">{qdrant.get('documents', 0)}</div>
                    <div class="metric-label">Documents</div>
                    <div class="status-badge {status_class}">{status.title()}</div>
                </div>''')
            
            content_parts.append('</div>')
        
        content_parts.append('</div>')
        content_parts.append('</div>')
        
        # Metrics tab
        content_parts.append('<div id="metrics" class="tab-content hidden">')
        if 'system_metrics' in data:
            content_parts.append(self._create_metrics_table(data['system_metrics']))
        content_parts.append('</div>')
        
        # Processes tab
        content_parts.append('<div id="processes" class="tab-content hidden">')
        if 'processes' in data and data['processes']:
            content_parts.append(self._create_processes_table(data['processes']))
        else:
            content_parts.append('<div class="section"><p>No process data available</p></div>')
        content_parts.append('</div>')
        
        # Queue tab
        content_parts.append('<div id="queue" class="tab-content hidden">')
        if 'queue_metrics' in data:
            content_parts.append(self._create_queue_metrics(data['queue_metrics']))
        content_parts.append('</div>')
        
        return '\n'.join(content_parts)
    
    def _generate_performance_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate performance report content."""
        content_parts = []
        
        # Overview tab
        content_parts.append('<div id="overview" class="tab-content">')
        content_parts.append('<div class="section fade-in">')
        content_parts.append('<h2 class="section-title">Performance Overview</h2>')
        
        if 'performance_summary' in data:
            summary = data['performance_summary']
            if 'metrics' in summary:
                metrics = summary['metrics']
                content_parts.append('<div class="grid grid-4">')
                
                for metric_name, value in metrics.items():
                    display_name = metric_name.replace('_', ' ').title()
                    unit = self._get_performance_unit(metric_name)
                    status_class = self._get_performance_status_class(metric_name, value)
                    
                    content_parts.append(f'''
                    <div class="card metric-card">
                        <div class="metric-value">{value}{unit}</div>
                        <div class="metric-label">{display_name}</div>
                        <div class="status-badge {status_class}">
                            {self._get_performance_status_text(metric_name, value)}
                        </div>
                    </div>''')
                
                content_parts.append('</div>')
        
        content_parts.append('</div>')
        content_parts.append('</div>')
        
        return '\n'.join(content_parts)
    
    def _generate_config_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate dashboard configuration content."""
        content_parts = []
        
        # Overview tab
        content_parts.append('<div id="overview" class="tab-content">')
        content_parts.append('<div class="section fade-in">')
        content_parts.append('<h2 class="section-title">Configuration Overview</h2>')
        
        # Summary cards
        content_parts.append('<div class="grid grid-3">')
        
        if 'layouts' in data:
            layouts = data['layouts']
            active_count = len([l for l in layouts if l.get('properties', {}).get('is_active', False)])
            content_parts.append(f'''
            <div class="card metric-card">
                <div class="metric-value">{len(layouts)}</div>
                <div class="metric-label">Total Layouts</div>
                <div class="status-badge status-healthy">{active_count} Active</div>
            </div>''')
        
        if 'templates' in data:
            templates = data['templates']
            avg_rating = sum(t.get('usage', {}).get('rating', 0) for t in templates) / len(templates) if templates else 0
            content_parts.append(f'''
            <div class="card metric-card">
                <div class="metric-value">{len(templates)}</div>
                <div class="metric-label">Templates</div>
                <div class="status-badge status-healthy">{avg_rating:.1f}/5.0 Rating</div>
            </div>''')
        
        content_parts.append('</div>')
        content_parts.append('</div>')
        content_parts.append('</div>')
        
        return '\n'.join(content_parts)
    
    def _generate_backup_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate full backup content."""
        return self._generate_config_content(data, job)
    
    def _generate_generic_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate generic content."""
        content_parts = []
        
        content_parts.append('<div id="overview" class="tab-content">')
        content_parts.append('<div class="section fade-in">')
        content_parts.append('<h2 class="section-title">Export Data</h2>')
        
        # Create JSON viewer
        filtered_data = {k: v for k, v in data.items() if k not in ['job', 'export_metadata']}
        json_str = json.dumps(filtered_data, indent=2, default=str)
        
        content_parts.append('<div class="search-container">')
        content_parts.append('<input type="text" class="search-box" placeholder="Search data..." onkeyup="searchData(this.value)">')
        content_parts.append('</div>')
        content_parts.append(f'<div class="json-viewer" id="json-data">{json_str}</div>')
        
        content_parts.append('</div>')
        content_parts.append('</div>')
        
        return '\n'.join(content_parts)
    
    def _create_metrics_table(self, metrics: Dict[str, Any]) -> str:
        """Create metrics table."""
        table_html = '''
        <div class="section">
            <h2 class="section-title">Detailed System Metrics</h2>
            <table class="data-table">
                <thead>
                    <tr><th>Component</th><th>Metric</th><th>Value</th><th>Unit</th></tr>
                </thead>
                <tbody>'''
        
        for component, data in metrics.items():
            if isinstance(data, dict):
                for metric, value in data.items():
                    unit = self._get_metric_unit(metric)
                    table_html += f'<tr><td>{component.title()}</td><td>{metric.replace("_", " ").title()}</td><td>{value}</td><td>{unit}</td></tr>'
            else:
                unit = self._get_metric_unit(component)
                table_html += f'<tr><td>System</td><td>{component.replace("_", " ").title()}</td><td>{data}</td><td>{unit}</td></tr>'
        
        table_html += '</tbody></table></div>'
        return table_html
    
    def _create_processes_table(self, processes: List[Dict[str, Any]]) -> str:
        """Create processes table."""
        table_html = '''
        <div class="section">
            <h2 class="section-title">System Processes</h2>
            <table class="data-table">
                <thead>
                    <tr><th>PID</th><th>Name</th><th>CPU %</th><th>Memory %</th><th>Status</th></tr>
                </thead>
                <tbody>'''
        
        for proc in processes[:20]:  # Limit to first 20 processes
            table_html += f'''
            <tr>
                <td>{proc.get('pid', '')}</td>
                <td>{proc.get('name', '')}</td>
                <td>{proc.get('cpu_percent', 0):.1f}%</td>
                <td>{proc.get('memory_percent', 0):.1f}%</td>
                <td><span class="status-badge status-healthy">{proc.get('status', '')}</span></td>
            </tr>'''
        
        table_html += '</tbody></table>'
        if len(processes) > 20:
            table_html += f'<p><em>Showing 20 of {len(processes)} processes</em></p>'
        table_html += '</div>'
        return table_html
    
    def _create_queue_metrics(self, queue_metrics: Dict[str, Any]) -> str:
        """Create queue metrics section."""
        content = '''
        <div class="section">
            <h2 class="section-title">Queue Status</h2>
            <div class="grid grid-4">'''
        
        for metric, value in queue_metrics.items():
            if isinstance(value, (int, float)):
                content += f'''
                <div class="card metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{metric.replace("_", " ").title()}</div>
                </div>'''
        
        content += '</div></div>'
        return content
    
    def _get_performance_unit(self, metric_name: str) -> str:
        """Get unit for performance metric."""
        unit_map = {
            'avg_response_time': 'ms',
            'total_requests': '',
            'error_rate': '%',
            'uptime_percentage': '%'
        }
        return unit_map.get(metric_name, '')
    
    def _get_performance_status_class(self, metric_name: str, value: float) -> str:
        """Get CSS class for performance status."""
        if metric_name == 'avg_response_time':
            return 'status-healthy' if value < 500 else 'status-warning' if value < 1000 else 'status-error'
        elif metric_name == 'error_rate':
            return 'status-healthy' if value < 2 else 'status-warning' if value < 5 else 'status-error'
        elif metric_name == 'uptime_percentage':
            return 'status-healthy' if value >= 99.5 else 'status-warning' if value >= 99 else 'status-error'
        else:
            return 'status-healthy'
    
    def _get_performance_status_text(self, metric_name: str, value: float) -> str:
        """Get status text for performance metric."""
        if metric_name == 'avg_response_time':
            return 'Good' if value < 500 else 'Warning' if value < 1000 else 'Critical'
        elif metric_name == 'error_rate':
            return 'Good' if value < 2 else 'Warning' if value < 5 else 'Critical'
        elif metric_name == 'uptime_percentage':
            return 'Good' if value >= 99.5 else 'Warning' if value >= 99 else 'Critical'
        else:
            return 'Good'
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """Get unit for metric."""
        unit_map = {
            'cpu': '%',
            'percent': '%',
            'used_gb': 'GB',
            'total_gb': 'GB',
            'free_gb': 'GB',
            'documents': 'count',
            'status': ''
        }
        return unit_map.get(metric_name, '')
    
    def _get_html_footer(self) -> str:
        """Generate HTML footer with JavaScript."""
        return f'''
<div class="footer">
    <p>Generated by Ansera Monitoring Dashboard • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • Interactive HTML Report</p>
</div>

<script>
function showTab(tabId) {{
    // Hide all tab contents
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => {{
        content.classList.add('hidden');
    }});
    
    // Remove active class from all tabs
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {{
        tab.classList.remove('active');
    }});
    
    // Show selected tab content
    const selectedContent = document.getElementById(tabId);
    if (selectedContent) {{
        selectedContent.classList.remove('hidden');
        selectedContent.classList.add('fade-in');
    }}
    
    // Add active class to clicked tab
    event.target.classList.add('active');
}}

function searchData(query) {{
    const jsonViewer = document.getElementById('json-data');
    if (!jsonViewer) return;
    
    const originalData = jsonViewer.textContent;
    if (!query) {{
        return;
    }}
    
    // Simple highlight search
    const regex = new RegExp(`(${query})`, 'gi');
    const highlighted = originalData.replace(regex, '<mark>$1</mark>');
    jsonViewer.innerHTML = highlighted;
}}

// Collapsible functionality
document.addEventListener('DOMContentLoaded', function() {{
    const collapsibles = document.querySelectorAll('.collapsible');
    collapsibles.forEach(collapsible => {{
        collapsible.addEventListener('click', function() {{
            const content = this.nextElementSibling;
            if (content && content.classList.contains('collapsible-content')) {{
                content.classList.toggle('active');
            }}
        }});
    }});
}});

// Auto-refresh functionality for live data (placeholder)
function refreshData() {{
    console.log('Refreshing data...');
    // This would be implemented for live dashboards
}}

// Print functionality
function printReport() {{
    window.print();
}}

// Export current view
function exportCurrentView() {{
    console.log('Exporting current view...');
}}
</script>
</body>
</html>'''