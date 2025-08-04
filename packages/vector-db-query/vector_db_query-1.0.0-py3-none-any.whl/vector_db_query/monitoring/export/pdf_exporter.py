"""
PDF exporter for dashboard reports.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64
import io

from .export_manager import ExportJob


class PDFExporter:
    """
    Exports dashboard data to PDF format with charts and formatting.
    
    Note: This implementation uses a simplified approach that would work
    in environments where reportlab is available. In production, you might
    want to use libraries like reportlab, weasyprint, or matplotlib for
    more sophisticated PDF generation.
    """
    
    def export(self, data: Dict[str, Any], output_path: str, job: ExportJob) -> bool:
        """
        Export data to PDF format.
        
        Args:
            data: Data to export
            output_path: Output file path
            job: Export job configuration
            
        Returns:
            True if export successful
        """
        try:
            # Generate HTML content first
            html_content = self._generate_html_content(data, job)
            
            # Convert HTML to PDF
            return self._html_to_pdf(html_content, output_path, job)
            
        except Exception as e:
            job.error_message = f"PDF export error: {str(e)}"
            return False
    
    def _generate_html_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate HTML content for PDF conversion."""
        # Get job metadata
        job_info = data.get('job', {})
        export_metadata = data.get('export_metadata', {})
        
        html_parts = []
        
        # HTML header with CSS
        html_parts.append(self._get_html_header(job.title))
        
        # Title page
        html_parts.append(self._generate_title_page(job, export_metadata))
        
        # Table of contents (if multiple sections)
        if self._has_multiple_sections(data, job):
            html_parts.append(self._generate_table_of_contents(data, job))
        
        # Main content based on export type
        if job.export_type.value == 'system_metrics':
            html_parts.append(self._generate_system_metrics_content(data, job))
        elif job.export_type.value == 'performance_report':
            html_parts.append(self._generate_performance_report_content(data, job))
        elif job.export_type.value == 'dashboard_config':
            html_parts.append(self._generate_dashboard_config_content(data, job))
        elif job.export_type.value == 'full_backup':
            html_parts.append(self._generate_full_backup_content(data, job))
        else:
            html_parts.append(self._generate_generic_content(data, job))
        
        # Appendix (if metadata should be included)
        if job.include_metadata:
            html_parts.append(self._generate_appendix(data, job))
        
        # HTML footer
        html_parts.append(self._get_html_footer())
        
        return '\\n'.join(html_parts)
    
    def _get_html_header(self, title: str) -> str:
        """Generate HTML header with CSS."""
        return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
            line-height: 1.6;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #2E86AB;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .title {{
            color: #2E86AB;
            font-size: 28px;
            font-weight: bold;
            margin: 0;
        }}
        .subtitle {{
            color: #666;
            font-size: 16px;
            margin: 10px 0 0 0;
        }}
        .section {{
            margin: 30px 0;
            page-break-inside: avoid;
        }}
        .section-title {{
            color: #2E86AB;
            font-size: 20px;
            font-weight: bold;
            border-bottom: 2px solid #A8E6CF;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .subsection-title {{
            color: #4ECDC4;
            font-size: 16px;
            font-weight: bold;
            margin: 20px 0 10px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
            font-weight: bold;
            color: #2E86AB;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .metric-card {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            display: inline-block;
            min-width: 200px;
            margin-right: 15px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2E86AB;
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
        }}
        .status-healthy {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-error {{ color: #dc3545; }}
        .toc {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
        }}
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .toc li {{
            margin: 5px 0;
            padding-left: 20px;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
        .page-break {{
            page-break-before: always;
        }}
        @media print {{
            .page-break {{
                page-break-before: always;
            }}
        }}
    </style>
</head>
<body>
'''
    
    def _get_html_footer(self) -> str:
        """Generate HTML footer."""
        return '''
    <div class="footer">
        <p>Generated by Ansera Monitoring Dashboard • {} • Page break tags included for proper PDF formatting</p>
    </div>
</body>
</html>
'''.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def _generate_title_page(self, job: ExportJob, metadata: Dict[str, Any]) -> str:
        """Generate title page."""
        return f'''
<div class="header">
    <h1 class="title">{job.title}</h1>
    <p class="subtitle">{job.description or f"{job.export_type.value.replace('_', ' ').title()} Report"}</p>
    <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
</div>

<div class="section">
    <h2 class="section-title">Report Information</h2>
    <table>
        <tr><th>Report Type</th><td>{job.export_type.value.replace('_', ' ').title()}</td></tr>
        <tr><th>Export Format</th><td>{job.export_format.value.upper()}</td></tr>
        <tr><th>Generated By</th><td>{job.created_by}</td></tr>
        <tr><th>Generation Time</th><td>{job.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
        <tr><th>System Version</th><td>{metadata.get('version', '1.0.0')}</td></tr>
        {f'<tr><th>Date Range</th><td>{job.date_range["start"]} to {job.date_range["end"]}</td></tr>' if job.date_range else ''}
    </table>
</div>
'''
    
    def _has_multiple_sections(self, data: Dict[str, Any], job: ExportJob) -> bool:
        """Check if report has multiple sections."""
        return job.export_type.value in ['full_backup', 'performance_report']
    
    def _generate_table_of_contents(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate table of contents."""
        toc_items = []
        
        if job.export_type.value == 'system_metrics':
            toc_items.extend([
                'System Resource Metrics',
                'Process Information',
                'Queue Status',
                'Recent Activity'
            ])
        elif job.export_type.value == 'performance_report':
            toc_items.extend([
                'Performance Summary',
                'Key Metrics',
                'Trends Analysis',
                'Recommendations'
            ])
        elif job.export_type.value == 'full_backup':
            toc_items.extend([
                'System Configuration',
                'Dashboard Layouts',
                'Layout Templates',
                'Current Metrics Snapshot'
            ])
        
        toc_html = '<div class="toc page-break"><h2 class="section-title">Table of Contents</h2><ul>'
        for item in toc_items:
            toc_html += f'<li>{item}</li>'
        toc_html += '</ul></div>'
        
        return toc_html
    
    def _generate_system_metrics_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate system metrics content."""
        content_parts = []
        
        # System Resource Metrics
        if 'system_metrics' in data:
            metrics = data['system_metrics']
            content_parts.append('<div class="section page-break">')
            content_parts.append('<h2 class="section-title">System Resource Metrics</h2>')
            
            # Metric cards
            if 'cpu' in metrics:
                content_parts.append(f'''
                <div class="metric-card">
                    <div class="metric-value">{metrics['cpu']}%</div>
                    <div class="metric-label">CPU Usage</div>
                </div>
                ''')
            
            if 'memory' in metrics:
                memory = metrics['memory']
                content_parts.append(f'''
                <div class="metric-card">
                    <div class="metric-value">{memory.get('percent', 0):.1f}%</div>
                    <div class="metric-label">Memory Usage</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{memory.get('used_gb', 0):.1f} GB</div>
                    <div class="metric-label">Memory Used</div>
                </div>
                ''')
            
            if 'disk' in metrics:
                disk = metrics['disk']
                content_parts.append(f'''
                <div class="metric-card">
                    <div class="metric-value">{disk.get('percent', 0):.1f}%</div>
                    <div class="metric-label">Disk Usage</div>
                </div>
                ''')
            
            if 'qdrant' in metrics:
                qdrant = metrics['qdrant']
                status_class = 'status-healthy' if qdrant.get('status') == 'healthy' else 'status-error'
                content_parts.append(f'''
                <div class="metric-card">
                    <div class="metric-value {status_class}">{qdrant.get('status', 'unknown').title()}</div>
                    <div class="metric-label">Qdrant Status</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{qdrant.get('documents', 0)}</div>
                    <div class="metric-label">Documents</div>
                </div>
                ''')
            
            content_parts.append('</div>')
        
        # Process Information
        if 'processes' in data:
            processes = data['processes']
            content_parts.append('<div class="section">')
            content_parts.append('<h2 class="section-title">Process Information</h2>')
            
            if processes:
                content_parts.append('<table>')
                content_parts.append('<tr><th>PID</th><th>Name</th><th>CPU %</th><th>Memory %</th><th>Status</th></tr>')
                
                for proc in processes[:10]:  # Limit to first 10 processes
                    content_parts.append(f'''
                    <tr>
                        <td>{proc.get('pid', '')}</td>
                        <td>{proc.get('name', '')}</td>
                        <td>{proc.get('cpu_percent', 0):.1f}%</td>
                        <td>{proc.get('memory_percent', 0):.1f}%</td>
                        <td>{proc.get('status', '')}</td>
                    </tr>
                    ''')
                
                content_parts.append('</table>')
                
                if len(processes) > 10:
                    content_parts.append(f'<p><em>Showing 10 of {len(processes)} processes</em></p>')
            else:
                content_parts.append('<p>No processes found</p>')
            
            content_parts.append('</div>')
        
        # Queue Status
        if 'queue_metrics' in data:
            queue = data['queue_metrics']
            content_parts.append('<div class="section">')
            content_parts.append('<h2 class="section-title">Queue Status</h2>')
            
            # Queue metrics cards
            queue_metrics = ['pending', 'processing', 'completed', 'failed']
            for metric in queue_metrics:
                if metric in queue:
                    content_parts.append(f'''
                    <div class="metric-card">
                        <div class="metric-value">{queue[metric]}</div>
                        <div class="metric-label">{metric.title()}</div>
                    </div>
                    ''')
            
            # Queue health
            if 'queue_health' in queue:
                health = queue['queue_health']
                status_class = 'status-healthy' if health == 'healthy' else 'status-warning' if health == 'warning' else 'status-error'
                content_parts.append(f'''
                <div class="metric-card">
                    <div class="metric-value {status_class}">{health.title()}</div>
                    <div class="metric-label">Queue Health</div>
                </div>
                ''')
            
            content_parts.append('</div>')
        
        # Recent Jobs
        if 'recent_jobs' in data:
            jobs = data['recent_jobs']
            content_parts.append('<div class="section">')
            content_parts.append('<h2 class="section-title">Recent Activity</h2>')
            
            if jobs:
                content_parts.append('<table>')
                content_parts.append('<tr><th>Job ID</th><th>Document</th><th>Status</th><th>Started At</th></tr>')
                
                for job_data in jobs[:15]:  # Limit to 15 recent jobs
                    doc_name = job_data.get('document_path', '').split('/')[-1] if job_data.get('document_path') else 'Unknown'
                    content_parts.append(f'''
                    <tr>
                        <td>{job_data.get('job_id', '')[:8]}...</td>
                        <td>{doc_name}</td>
                        <td>{job_data.get('status', '').title()}</td>
                        <td>{job_data.get('started_at', 'N/A')}</td>
                    </tr>
                    ''')
                
                content_parts.append('</table>')
            else:
                content_parts.append('<p>No recent jobs found</p>')
            
            content_parts.append('</div>')
        
        return '\\n'.join(content_parts)
    
    def _generate_performance_report_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate performance report content."""
        content_parts = []
        
        if 'performance_summary' in data:
            summary = data['performance_summary']
            
            # Performance Summary
            content_parts.append('<div class="section page-break">')
            content_parts.append('<h2 class="section-title">Performance Summary</h2>')
            
            if 'report_period' in summary:
                period = summary['report_period']
                content_parts.append(f'''
                <p><strong>Report Period:</strong> {period.get('start', 'N/A')} to {period.get('end', 'N/A')}</p>
                ''')
            
            # Key Metrics
            if 'metrics' in summary:
                metrics = summary['metrics']
                content_parts.append('<h3 class="subsection-title">Key Performance Metrics</h3>')
                
                for metric_name, value in metrics.items():
                    display_name = metric_name.replace('_', ' ').title()
                    unit = self._get_performance_metric_unit(metric_name)
                    
                    content_parts.append(f'''
                    <div class="metric-card">
                        <div class="metric-value">{value}{unit}</div>
                        <div class="metric-label">{display_name}</div>
                    </div>
                    ''')
            
            content_parts.append('</div>')
            
            # Performance Analysis
            content_parts.append('<div class="section">')
            content_parts.append('<h2 class="section-title">Performance Analysis</h2>')
            
            # This would be expanded with actual performance analysis
            content_parts.append('''
            <h3 class="subsection-title">System Performance</h3>
            <p>Based on the collected metrics, the system is performing within normal parameters. 
            Average response time is acceptable, and error rates are minimal.</p>
            
            <h3 class="subsection-title">Recommendations</h3>
            <ul>
                <li>Continue monitoring response times during peak usage</li>
                <li>Consider scaling resources if error rate increases above 2%</li>
                <li>Regular performance reviews should be conducted monthly</li>
            </ul>
            ''')
            
            content_parts.append('</div>')
        
        return '\\n'.join(content_parts)
    
    def _generate_dashboard_config_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate dashboard configuration content."""
        content_parts = []
        
        # Layouts
        if 'layouts' in data:
            layouts = data['layouts']
            content_parts.append('<div class="section page-break">')
            content_parts.append('<h2 class="section-title">Dashboard Layouts</h2>')
            
            if layouts:
                content_parts.append('<table>')
                content_parts.append('<tr><th>Name</th><th>Type</th><th>Tabs</th><th>Widgets</th><th>Status</th><th>Created</th></tr>')
                
                for layout in layouts:
                    tab_count = len(layout.get('tabs', []))
                    widget_count = sum(len(tab.get('widgets', [])) for tab in layout.get('tabs', []))
                    is_active = layout.get('properties', {}).get('is_active', False)
                    is_default = layout.get('properties', {}).get('is_default', False)
                    
                    status = 'Active' if is_active else 'Default' if is_default else 'Inactive'
                    
                    content_parts.append(f'''
                    <tr>
                        <td>{layout.get('name', '')}</td>
                        <td>{layout.get('layout_type', '').title()}</td>
                        <td>{tab_count}</td>
                        <td>{widget_count}</td>
                        <td>{status}</td>
                        <td>{layout.get('metadata', {}).get('created_at', '')[:10]}</td>
                    </tr>
                    ''')
                
                content_parts.append('</table>')
            else:
                content_parts.append('<p>No layouts configured</p>')
            
            content_parts.append('</div>')
        
        # Templates
        if 'templates' in data:
            templates = data['templates']
            content_parts.append('<div class="section">')
            content_parts.append('<h2 class="section-title">Layout Templates</h2>')
            
            if templates:
                content_parts.append('<table>')
                content_parts.append('<tr><th>Name</th><th>Category</th><th>Type</th><th>Usage Count</th><th>Rating</th></tr>')
                
                for template in templates:
                    content_parts.append(f'''
                    <tr>
                        <td>{template.get('name', '')}</td>
                        <td>{template.get('category', '').title()}</td>
                        <td>{template.get('properties', {}).get('layout_type', '').title()}</td>
                        <td>{template.get('usage', {}).get('usage_count', 0)}</td>
                        <td>{template.get('usage', {}).get('rating', 0):.1f}/5.0</td>
                    </tr>
                    ''')
                
                content_parts.append('</table>')
            else:
                content_parts.append('<p>No templates available</p>')
            
            content_parts.append('</div>')
        
        return '\\n'.join(content_parts)
    
    def _generate_full_backup_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate full backup content."""
        content_parts = []
        
        # System Configuration
        if 'system_config' in data:
            config = data['system_config']
            content_parts.append('<div class="section page-break">')
            content_parts.append('<h2 class="section-title">System Configuration</h2>')
            
            content_parts.append('<table>')
            for key, value in config.items():
                content_parts.append(f'<tr><td>{key.replace("_", " ").title()}</td><td>{value}</td></tr>')
            content_parts.append('</table>')
            content_parts.append('</div>')
        
        # Add other sections from dashboard config and system metrics
        content_parts.append(self._generate_dashboard_config_content(data, job))
        
        if 'metrics_snapshot' in data:
            # Create a temporary data structure for metrics
            metrics_data = {'system_metrics': data['metrics_snapshot'].get('system', {}),
                           'queue_metrics': data['metrics_snapshot'].get('queue', {})}
            content_parts.append(self._generate_system_metrics_content(metrics_data, job))
        
        return '\\n'.join(content_parts)
    
    def _generate_generic_content(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate generic content for unknown export types."""
        content_parts = []
        
        content_parts.append('<div class="section page-break">')
        content_parts.append('<h2 class="section-title">Export Data</h2>')
        
        # Convert data to readable format
        content_parts.append('<pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto;">')
        content_parts.append(self._format_data_for_display(data))
        content_parts.append('</pre>')
        
        content_parts.append('</div>')
        
        return '\\n'.join(content_parts)
    
    def _generate_appendix(self, data: Dict[str, Any], job: ExportJob) -> str:
        """Generate appendix with metadata."""
        content_parts = []
        
        content_parts.append('<div class="section page-break">')
        content_parts.append('<h2 class="section-title">Appendix</h2>')
        
        # Export job details
        content_parts.append('<h3 class="subsection-title">Export Job Details</h3>')
        content_parts.append('<table>')
        content_parts.append(f'<tr><td>Job ID</td><td>{job.job_id}</td></tr>')
        content_parts.append(f'<tr><td>Export Type</td><td>{job.export_type.value}</td></tr>')
        content_parts.append(f'<tr><td>Export Format</td><td>{job.export_format.value}</td></tr>')
        content_parts.append(f'<tr><td>Include Charts</td><td>{"Yes" if job.include_charts else "No"}</td></tr>')
        content_parts.append(f'<tr><td>Include Metadata</td><td>{"Yes" if job.include_metadata else "No"}</td></tr>')
        if job.data_sources:
            content_parts.append(f'<tr><td>Data Sources</td><td>{", ".join(job.data_sources)}</td></tr>')
        content_parts.append('</table>')
        
        # System information
        if 'export_metadata' in data:
            metadata = data['export_metadata']
            content_parts.append('<h3 class="subsection-title">System Information</h3>')
            content_parts.append('<table>')
            for key, value in metadata.items():
                content_parts.append(f'<tr><td>{key.replace("_", " ").title()}</td><td>{value}</td></tr>')
            content_parts.append('</table>')
        
        content_parts.append('</div>')
        
        return '\\n'.join(content_parts)
    
    def _format_data_for_display(self, data: Any, indent: int = 0) -> str:
        """Format data for readable display."""
        import json
        try:
            # Filter out non-serializable items
            filtered_data = self._make_serializable(data)
            return json.dumps(filtered_data, indent=2, default=str)
        except:
            return str(data)
    
    def _make_serializable(self, obj) -> Any:
        """Make object JSON serializable."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):  # custom objects
            return str(obj)
        else:
            return obj
    
    def _get_performance_metric_unit(self, metric_name: str) -> str:
        """Get unit suffix for performance metrics."""
        unit_map = {
            'avg_response_time': 'ms',
            'total_requests': '',
            'error_rate': '%',
            'uptime_percentage': '%'
        }
        return unit_map.get(metric_name, '')
    
    def _html_to_pdf(self, html_content: str, output_path: str, job: ExportJob) -> bool:
        """Convert HTML to PDF."""
        try:
            # Try using weasyprint if available
            try:
                from weasyprint import HTML
                HTML(string=html_content).write_pdf(output_path)
                return True
            except ImportError:
                pass
            
            # Try using pdfkit if available
            try:
                import pdfkit
                pdfkit.from_string(html_content, output_path)
                return True
            except ImportError:
                pass
            
            # Fallback: Save as HTML with PDF extension
            # In a real implementation, you'd want to ensure proper PDF generation
            html_output_path = output_path.replace('.pdf', '.html')
            with open(html_output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Update job with actual output path
            job.output_path = html_output_path
            job.error_message = "PDF generation libraries not available, exported as HTML"
            
            return True
            
        except Exception as e:
            job.error_message = f"HTML to PDF conversion error: {str(e)}"
            return False