"""
CSV exporter for dashboard data.
"""

import csv
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd

from .export_manager import ExportJob


class CSVExporter:
    """
    Exports dashboard data to CSV format.
    """
    
    def export(self, data: Dict[str, Any], output_path: str, job: ExportJob) -> bool:
        """
        Export data to CSV format.
        
        Args:
            data: Data to export
            output_path: Output file path
            job: Export job configuration
            
        Returns:
            True if export successful
        """
        try:
            # Determine if we need multiple CSV files (ZIP) or single file
            if self._needs_multiple_files(data, job):
                return self._export_multiple_csv(data, output_path, job)
            else:
                return self._export_single_csv(data, output_path, job)
                
        except Exception as e:
            job.error_message = f"CSV export error: {str(e)}"
            return False
    
    def _needs_multiple_files(self, data: Dict[str, Any], job: ExportJob) -> bool:
        """Check if export needs multiple CSV files."""
        # Multiple files needed for complex exports like full backup
        complex_types = ['full_backup', 'dashboard_config']
        return job.export_type.value in complex_types
    
    def _export_single_csv(self, data: Dict[str, Any], output_path: str, job: ExportJob) -> bool:
        """Export to single CSV file."""
        try:
            # Extract tabular data based on export type
            csv_data = self._extract_csv_data(data, job)
            
            if not csv_data:
                job.error_message = "No tabular data found for CSV export"
                return False
            
            # Write CSV file
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                if isinstance(csv_data, list) and csv_data:
                    # List of dictionaries
                    fieldnames = csv_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(csv_data)
                    
                elif isinstance(csv_data, dict):
                    # Simple key-value pairs
                    writer = csv.writer(csvfile)
                    writer.writerow(['Key', 'Value'])
                    for key, value in csv_data.items():
                        writer.writerow([key, str(value)])
                
                else:
                    job.error_message = "Unsupported data format for CSV export"
                    return False
            
            job.progress = 100.0
            return True
            
        except Exception as e:
            job.error_message = f"Single CSV export error: {str(e)}"
            return False
    
    def _export_multiple_csv(self, data: Dict[str, Any], output_path: str, job: ExportJob) -> bool:
        """Export to multiple CSV files in a ZIP archive."""
        import zipfile
        import tempfile
        
        try:
            # Create temporary directory for CSV files
            with tempfile.TemporaryDirectory() as temp_dir:
                csv_files = []
                
                # Generate CSV files for different data sections
                if job.export_type.value == 'full_backup':
                    csv_files.extend(self._create_backup_csv_files(data, temp_dir, job))
                elif job.export_type.value == 'dashboard_config':
                    csv_files.extend(self._create_config_csv_files(data, temp_dir, job))
                else:
                    # Fallback to single file
                    return self._export_single_csv(data, output_path, job)
                
                # Create ZIP archive
                zip_path = output_path.replace('.csv', '.zip')
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for csv_file in csv_files:
                        if os.path.exists(csv_file):
                            zipf.write(csv_file, os.path.basename(csv_file))
                
                # Update job with actual output path
                job.output_path = zip_path
                job.progress = 100.0
                return True
                
        except Exception as e:
            job.error_message = f"Multiple CSV export error: {str(e)}"
            return False
    
    def _create_backup_csv_files(self, data: Dict[str, Any], temp_dir: str, job: ExportJob) -> List[str]:
        """Create CSV files for full backup export."""
        csv_files = []
        
        try:
            # System metrics
            if 'metrics_snapshot' in data:
                metrics_file = os.path.join(temp_dir, 'system_metrics.csv')
                self._write_metrics_csv(data['metrics_snapshot'], metrics_file)
                csv_files.append(metrics_file)
            
            # Layouts
            if 'layouts' in data:
                layouts_file = os.path.join(temp_dir, 'layouts.csv')
                self._write_layouts_csv(data['layouts'], layouts_file)
                csv_files.append(layouts_file)
            
            # Templates
            if 'templates' in data:
                templates_file = os.path.join(temp_dir, 'templates.csv')
                self._write_templates_csv(data['templates'], templates_file)
                csv_files.append(templates_file)
            
            # System configuration
            if 'system_config' in data:
                config_file = os.path.join(temp_dir, 'system_config.csv')
                self._write_config_csv(data['system_config'], config_file)
                csv_files.append(config_file)
                
        except Exception as e:
            job.error_message = f"Backup CSV creation error: {str(e)}"
        
        return csv_files
    
    def _create_config_csv_files(self, data: Dict[str, Any], temp_dir: str, job: ExportJob) -> List[str]:
        """Create CSV files for dashboard configuration export."""
        csv_files = []
        
        try:
            # Layouts
            if 'layouts' in data:
                layouts_file = os.path.join(temp_dir, 'dashboard_layouts.csv')
                self._write_layouts_csv(data['layouts'], layouts_file)
                csv_files.append(layouts_file)
            
            # Templates
            if 'templates' in data:
                templates_file = os.path.join(temp_dir, 'layout_templates.csv')
                self._write_templates_csv(data['templates'], templates_file)
                csv_files.append(templates_file)
                
        except Exception as e:
            job.error_message = f"Config CSV creation error: {str(e)}"
        
        return csv_files
    
    def _extract_csv_data(self, data: Dict[str, Any], job: ExportJob) -> Any:
        """Extract CSV-appropriate data based on export type."""
        if job.export_type.value == 'system_metrics':
            return self._extract_system_metrics_csv(data)
        elif job.export_type.value == 'performance_report':
            return self._extract_performance_csv(data)
        else:
            # Generic extraction
            return self._extract_generic_csv(data)
    
    def _extract_system_metrics_csv(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract system metrics for CSV."""
        csv_rows = []
        
        # System metrics
        if 'system_metrics' in data:
            metrics = data['system_metrics']
            timestamp = datetime.now().isoformat()
            
            csv_rows.append({
                'timestamp': timestamp,
                'metric_type': 'cpu',
                'value': metrics.get('cpu', 0),
                'unit': 'percent'
            })
            
            if 'memory' in metrics:
                memory = metrics['memory']
                csv_rows.append({
                    'timestamp': timestamp,
                    'metric_type': 'memory_used',
                    'value': memory.get('used_gb', 0),
                    'unit': 'GB'
                })
                csv_rows.append({
                    'timestamp': timestamp,
                    'metric_type': 'memory_percent',
                    'value': memory.get('percent', 0),
                    'unit': 'percent'
                })
            
            if 'disk' in metrics:
                disk = metrics['disk']
                csv_rows.append({
                    'timestamp': timestamp,
                    'metric_type': 'disk_used',
                    'value': disk.get('used_gb', 0),
                    'unit': 'GB'
                })
                csv_rows.append({
                    'timestamp': timestamp,
                    'metric_type': 'disk_percent',
                    'value': disk.get('percent', 0),
                    'unit': 'percent'
                })
        
        # Queue metrics
        if 'queue_metrics' in data:
            queue = data['queue_metrics']
            timestamp = datetime.now().isoformat()
            
            for metric_name, value in queue.items():
                if isinstance(value, (int, float)):
                    csv_rows.append({
                        'timestamp': timestamp,
                        'metric_type': f'queue_{metric_name}',
                        'value': value,
                        'unit': 'count' if metric_name in ['pending', 'processing', 'completed', 'failed'] else 'other'
                    })
        
        # Recent jobs
        if 'recent_jobs' in data:
            for job_data in data['recent_jobs']:
                csv_rows.append({
                    'timestamp': job_data.get('started_at', datetime.now().isoformat()),
                    'metric_type': 'job_status',
                    'value': job_data.get('status', 'unknown'),
                    'unit': 'status',
                    'job_id': job_data.get('job_id', ''),
                    'document': job_data.get('document_path', '')
                })
        
        return csv_rows
    
    def _extract_performance_csv(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract performance data for CSV."""
        csv_rows = []
        
        if 'performance_summary' in data:
            summary = data['performance_summary']
            timestamp = datetime.now().isoformat()
            
            if 'metrics' in summary:
                metrics = summary['metrics']
                for metric_name, value in metrics.items():
                    csv_rows.append({
                        'timestamp': timestamp,
                        'metric_name': metric_name,
                        'value': value,
                        'period': f"{summary.get('report_period', {}).get('start', '')} to {summary.get('report_period', {}).get('end', '')}"
                    })
        
        return csv_rows
    
    def _extract_generic_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic CSV data extraction."""
        # Flatten nested dictionaries for CSV
        flattened = {}
        
        def flatten_dict(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list):
                    # Convert lists to comma-separated strings
                    items.append((new_key, ', '.join(map(str, v))))
                else:
                    items.append((new_key, v))
            return dict(items)
        
        return flatten_dict(data)
    
    def _write_metrics_csv(self, metrics_data: Dict[str, Any], file_path: str) -> None:
        """Write metrics data to CSV file."""
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Component', 'Metric', 'Value', 'Unit', 'Timestamp'])
            
            timestamp = metrics_data.get('timestamp', datetime.now().isoformat())
            
            for component, data in metrics_data.items():
                if component == 'timestamp':
                    continue
                    
                if isinstance(data, dict):
                    for metric, value in data.items():
                        unit = self._get_metric_unit(metric)
                        writer.writerow([component, metric, value, unit, timestamp])
                else:
                    unit = self._get_metric_unit(component)
                    writer.writerow(['system', component, data, unit, timestamp])
    
    def _write_layouts_csv(self, layouts_data: List[Dict[str, Any]], file_path: str) -> None:
        """Write layouts data to CSV file."""
        if not layouts_data:
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['layout_id', 'name', 'layout_type', 'is_active', 'is_default', 
                         'tab_count', 'widget_count', 'created_at', 'owner']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for layout in layouts_data:
                row = {
                    'layout_id': layout.get('layout_id', ''),
                    'name': layout.get('name', ''),
                    'layout_type': layout.get('layout_type', ''),
                    'is_active': layout.get('properties', {}).get('is_active', False),
                    'is_default': layout.get('properties', {}).get('is_default', False),
                    'tab_count': len(layout.get('tabs', [])),
                    'widget_count': sum(len(tab.get('widgets', [])) for tab in layout.get('tabs', [])),
                    'created_at': layout.get('metadata', {}).get('created_at', ''),
                    'owner': layout.get('access', {}).get('owner', '')
                }
                writer.writerow(row)
    
    def _write_templates_csv(self, templates_data: List[Dict[str, Any]], file_path: str) -> None:
        """Write templates data to CSV file."""
        if not templates_data:
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['template_id', 'name', 'description', 'category', 'layout_type', 
                         'usage_count', 'rating', 'tags', 'created_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for template in templates_data:
                row = {
                    'template_id': template.get('template_id', ''),
                    'name': template.get('name', ''),
                    'description': template.get('description', ''),
                    'category': template.get('category', ''),
                    'layout_type': template.get('properties', {}).get('layout_type', ''),
                    'usage_count': template.get('usage', {}).get('usage_count', 0),
                    'rating': template.get('usage', {}).get('rating', 0),
                    'tags': ', '.join(template.get('properties', {}).get('tags', [])),
                    'created_at': template.get('metadata', {}).get('created_at', '')
                }
                writer.writerow(row)
    
    def _write_config_csv(self, config_data: Dict[str, Any], file_path: str) -> None:
        """Write configuration data to CSV file."""
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Setting', 'Value'])
            
            for key, value in config_data.items():
                writer.writerow([key, str(value)])
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """Get unit for metric name."""
        unit_map = {
            'cpu': 'percent',
            'percent': 'percent',
            'used_gb': 'GB',
            'total_gb': 'GB',
            'free_gb': 'GB',
            'documents': 'count',
            'pending': 'count',
            'processing': 'count',
            'completed': 'count',
            'failed': 'count',
            'processing_rate': 'docs/min',
            'average_processing_time': 'seconds'
        }
        
        return unit_map.get(metric_name, 'unknown')