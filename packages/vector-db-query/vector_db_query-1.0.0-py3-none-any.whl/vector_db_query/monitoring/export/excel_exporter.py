"""
Excel exporter for dashboard data with multiple sheets and formatting.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd

from .export_manager import ExportJob


class ExcelExporter:
    """
    Exports dashboard data to Excel format with multiple sheets and formatting.
    """
    
    def export(self, data: Dict[str, Any], output_path: str, job: ExportJob) -> bool:
        """
        Export data to Excel format.
        
        Args:
            data: Data to export
            output_path: Output file path
            job: Export job configuration
            
        Returns:
            True if export successful
        """
        try:
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Create sheets based on export type
                if job.export_type.value == 'system_metrics':
                    self._create_system_metrics_sheets(data, writer, job)
                elif job.export_type.value == 'performance_report':
                    self._create_performance_sheets(data, writer, job)
                elif job.export_type.value == 'dashboard_config':
                    self._create_config_sheets(data, writer, job)
                elif job.export_type.value == 'full_backup':
                    self._create_backup_sheets(data, writer, job)
                else:
                    self._create_generic_sheets(data, writer, job)
                
                # Always create summary sheet
                self._create_summary_sheet(data, writer, job)
            
            job.progress = 100.0
            return True
            
        except Exception as e:
            job.error_message = f"Excel export error: {str(e)}"
            return False
    
    def _create_system_metrics_sheets(self, data: Dict[str, Any], writer: pd.ExcelWriter, job: ExportJob) -> None:
        """Create sheets for system metrics export."""
        
        # System Metrics Sheet
        if 'system_metrics' in data:
            metrics_data = []
            timestamp = datetime.now().isoformat()
            
            # CPU metrics
            if 'cpu' in data['system_metrics']:
                metrics_data.append({
                    'Timestamp': timestamp,
                    'Component': 'CPU',
                    'Metric': 'Usage',
                    'Value': data['system_metrics']['cpu'],
                    'Unit': '%'
                })
            
            # Memory metrics
            if 'memory' in data['system_metrics']:
                memory = data['system_metrics']['memory']
                for metric, value in memory.items():
                    unit = 'GB' if 'gb' in metric.lower() else '%' if 'percent' in metric.lower() else 'bytes'
                    metrics_data.append({
                        'Timestamp': timestamp,
                        'Component': 'Memory',
                        'Metric': metric.replace('_', ' ').title(),
                        'Value': value,
                        'Unit': unit
                    })
            
            # Disk metrics
            if 'disk' in data['system_metrics']:
                disk = data['system_metrics']['disk']
                for metric, value in disk.items():
                    unit = 'GB' if 'gb' in metric.lower() else '%' if 'percent' in metric.lower() else 'bytes'
                    metrics_data.append({
                        'Timestamp': timestamp,
                        'Component': 'Disk',
                        'Metric': metric.replace('_', ' ').title(),
                        'Value': value,
                        'Unit': unit
                    })
            
            # Qdrant metrics
            if 'qdrant' in data['system_metrics']:
                qdrant = data['system_metrics']['qdrant']
                for metric, value in qdrant.items():
                    unit = 'count' if metric == 'documents' else 'status' if metric == 'status' else 'other'
                    metrics_data.append({
                        'Timestamp': timestamp,
                        'Component': 'Qdrant',
                        'Metric': metric.replace('_', ' ').title(),
                        'Value': value,
                        'Unit': unit
                    })
            
            if metrics_data:
                df_metrics = pd.DataFrame(metrics_data)
                df_metrics.to_excel(writer, sheet_name='System Metrics', index=False)
        
        # Processes Sheet
        if 'processes' in data and data['processes']:
            df_processes = pd.DataFrame(data['processes'])
            df_processes.to_excel(writer, sheet_name='Processes', index=False)
        
        # Queue Metrics Sheet
        if 'queue_metrics' in data:
            queue_data = []
            timestamp = datetime.now().isoformat()
            
            for metric, value in data['queue_metrics'].items():
                queue_data.append({
                    'Timestamp': timestamp,
                    'Metric': metric.replace('_', ' ').title(),
                    'Value': value,
                    'Type': 'Count' if metric in ['pending', 'processing', 'completed', 'failed'] else 'Status'
                })
            
            if queue_data:
                df_queue = pd.DataFrame(queue_data)
                df_queue.to_excel(writer, sheet_name='Queue Metrics', index=False)
        
        # Recent Jobs Sheet
        if 'recent_jobs' in data and data['recent_jobs']:
            jobs_data = []
            for job_data in data['recent_jobs']:
                jobs_data.append({
                    'Job ID': job_data.get('job_id', '')[:8] + '...' if job_data.get('job_id') else '',
                    'Document': job_data.get('document_path', '').split('/')[-1] if job_data.get('document_path') else 'Unknown',
                    'Status': job_data.get('status', '').title(),
                    'Started At': job_data.get('started_at', 'N/A'),
                    'Full Path': job_data.get('document_path', '')
                })
            
            if jobs_data:
                df_jobs = pd.DataFrame(jobs_data)
                df_jobs.to_excel(writer, sheet_name='Recent Jobs', index=False)
    
    def _create_performance_sheets(self, data: Dict[str, Any], writer: pd.ExcelWriter, job: ExportJob) -> None:
        """Create sheets for performance report export."""
        
        if 'performance_summary' in data:
            summary = data['performance_summary']
            
            # Performance Metrics Sheet
            if 'metrics' in summary:
                metrics_data = []
                for metric_name, value in summary['metrics'].items():
                    metrics_data.append({
                        'Metric': metric_name.replace('_', ' ').title(),
                        'Value': value,
                        'Unit': self._get_performance_unit(metric_name),
                        'Status': self._get_metric_status(metric_name, value)
                    })
                
                df_metrics = pd.DataFrame(metrics_data)
                df_metrics.to_excel(writer, sheet_name='Performance Metrics', index=False)
            
            # Report Details Sheet
            report_data = []
            if 'report_period' in summary:
                period = summary['report_period']
                report_data.append({
                    'Setting': 'Report Period Start',
                    'Value': period.get('start', 'N/A')
                })
                report_data.append({
                    'Setting': 'Report Period End',
                    'Value': period.get('end', 'N/A')
                })
            
            report_data.extend([
                {'Setting': 'Report Generated', 'Value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
                {'Setting': 'Report Type', 'Value': 'Performance Analysis'},
                {'Setting': 'Generated By', 'Value': job.created_by}
            ])
            
            df_report = pd.DataFrame(report_data)
            df_report.to_excel(writer, sheet_name='Report Details', index=False)
    
    def _create_config_sheets(self, data: Dict[str, Any], writer: pd.ExcelWriter, job: ExportJob) -> None:
        """Create sheets for dashboard configuration export."""
        
        # Layouts Sheet
        if 'layouts' in data and data['layouts']:
            layouts_data = []
            for layout in data['layouts']:
                tab_count = len(layout.get('tabs', []))
                widget_count = sum(len(tab.get('widgets', [])) for tab in layout.get('tabs', []))
                
                layouts_data.append({
                    'Layout ID': layout.get('layout_id', ''),
                    'Name': layout.get('name', ''),
                    'Type': layout.get('layout_type', '').title(),
                    'Active': layout.get('properties', {}).get('is_active', False),
                    'Default': layout.get('properties', {}).get('is_default', False),
                    'Tab Count': tab_count,
                    'Widget Count': widget_count,
                    'Created At': layout.get('metadata', {}).get('created_at', '')[:10],
                    'Owner': layout.get('access', {}).get('owner', '')
                })
            
            df_layouts = pd.DataFrame(layouts_data)
            df_layouts.to_excel(writer, sheet_name='Dashboard Layouts', index=False)
        
        # Templates Sheet
        if 'templates' in data and data['templates']:
            templates_data = []
            for template in data['templates']:
                templates_data.append({
                    'Template ID': template.get('template_id', ''),
                    'Name': template.get('name', ''),
                    'Description': template.get('description', ''),
                    'Category': template.get('category', '').title(),
                    'Layout Type': template.get('properties', {}).get('layout_type', '').title(),
                    'Usage Count': template.get('usage', {}).get('usage_count', 0),
                    'Rating': template.get('usage', {}).get('rating', 0),
                    'Tags': ', '.join(template.get('properties', {}).get('tags', [])),
                    'Created At': template.get('metadata', {}).get('created_at', '')[:10]
                })
            
            df_templates = pd.DataFrame(templates_data)
            df_templates.to_excel(writer, sheet_name='Layout Templates', index=False)
    
    def _create_backup_sheets(self, data: Dict[str, Any], writer: pd.ExcelWriter, job: ExportJob) -> None:
        """Create sheets for full backup export."""
        
        # System Configuration Sheet
        if 'system_config' in data:
            config_data = []
            for key, value in data['system_config'].items():
                config_data.append({
                    'Setting': key.replace('_', ' ').title(),
                    'Value': str(value)
                })
            
            df_config = pd.DataFrame(config_data)
            df_config.to_excel(writer, sheet_name='System Configuration', index=False)
        
        # Create dashboard config sheets
        self._create_config_sheets(data, writer, job)
        
        # Metrics Snapshot Sheet
        if 'metrics_snapshot' in data:
            snapshot = data['metrics_snapshot']
            snapshot_data = []
            timestamp = snapshot.get('timestamp', datetime.now().isoformat())
            
            # System metrics
            if 'system' in snapshot:
                for component, metrics in snapshot['system'].items():
                    if isinstance(metrics, dict):
                        for metric, value in metrics.items():
                            snapshot_data.append({
                                'Timestamp': timestamp,
                                'Component': component.title(),
                                'Metric': metric.replace('_', ' ').title(),
                                'Value': value,
                                'Type': 'System'
                            })
                    else:
                        snapshot_data.append({
                            'Timestamp': timestamp,
                            'Component': 'System',
                            'Metric': component.replace('_', ' ').title(),
                            'Value': metrics,
                            'Type': 'System'
                        })
            
            # Queue metrics
            if 'queue' in snapshot:
                for metric, value in snapshot['queue'].items():
                    snapshot_data.append({
                        'Timestamp': timestamp,
                        'Component': 'Queue',
                        'Metric': metric.replace('_', ' ').title(),
                        'Value': value,
                        'Type': 'Queue'
                    })
            
            if snapshot_data:
                df_snapshot = pd.DataFrame(snapshot_data)
                df_snapshot.to_excel(writer, sheet_name='Metrics Snapshot', index=False)
    
    def _create_generic_sheets(self, data: Dict[str, Any], writer: pd.ExcelWriter, job: ExportJob) -> None:
        """Create sheets for generic data export."""
        
        # Try to create sheets for each top-level data item
        for key, value in data.items():
            if key in ['job', 'export_metadata']:
                continue
                
            sheet_name = key.replace('_', ' ').title()[:31]  # Excel sheet name limit
            
            try:
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    # List of dictionaries - can be converted to DataFrame
                    df = pd.DataFrame(value)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                elif isinstance(value, dict):
                    # Dictionary - convert to key-value pairs
                    pairs = [{'Key': k, 'Value': str(v)} for k, v in value.items()]
                    df = pd.DataFrame(pairs)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    # Single value - create simple sheet
                    df = pd.DataFrame([{'Data': str(value)}])
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            except:
                # If conversion fails, skip this data
                continue
    
    def _create_summary_sheet(self, data: Dict[str, Any], writer: pd.ExcelWriter, job: ExportJob) -> None:
        """Create export summary sheet."""
        
        summary_data = [
            {'Property': 'Export Job ID', 'Value': job.job_id},
            {'Property': 'Export Type', 'Value': job.export_type.value.replace('_', ' ').title()},
            {'Property': 'Export Format', 'Value': job.export_format.value.upper()},
            {'Property': 'Title', 'Value': job.title},
            {'Property': 'Description', 'Value': job.description or 'N/A'},
            {'Property': 'Generated At', 'Value': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            {'Property': 'Generated By', 'Value': job.created_by},
            {'Property': 'Include Charts', 'Value': 'Yes' if job.include_charts else 'No'},
            {'Property': 'Include Metadata', 'Value': 'Yes' if job.include_metadata else 'No'}
        ]
        
        # Add date range if specified
        if job.date_range:
            summary_data.append({
                'Property': 'Date Range', 
                'Value': f"{job.date_range.get('start', 'N/A')} to {job.date_range.get('end', 'N/A')}"
            })
        
        # Add data sources if specified
        if job.data_sources:
            summary_data.append({
                'Property': 'Data Sources', 
                'Value': ', '.join(job.data_sources)
            })
        
        # Add export metadata
        if 'export_metadata' in data:
            metadata = data['export_metadata']
            for key, value in metadata.items():
                summary_data.append({
                    'Property': key.replace('_', ' ').title(),
                    'Value': str(value)
                })
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Export Summary', index=False)
    
    def _get_performance_unit(self, metric_name: str) -> str:
        """Get unit for performance metric."""
        unit_map = {
            'avg_response_time': 'ms',
            'total_requests': 'count',
            'error_rate': '%',
            'uptime_percentage': '%',
            'cpu_usage': '%',
            'memory_usage': '%'
        }
        return unit_map.get(metric_name, '')
    
    def _get_metric_status(self, metric_name: str, value: float) -> str:
        """Get status for performance metric."""
        if metric_name == 'avg_response_time':
            return 'Good' if value < 500 else 'Warning' if value < 1000 else 'Critical'
        elif metric_name == 'error_rate':
            return 'Good' if value < 2 else 'Warning' if value < 5 else 'Critical'
        elif metric_name == 'uptime_percentage':
            return 'Good' if value >= 99.5 else 'Warning' if value >= 99 else 'Critical'
        else:
            return 'N/A'