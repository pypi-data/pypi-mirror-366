"""
JSON exporter for dashboard data.
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from .export_manager import ExportJob


class JSONExporter:
    """
    Exports dashboard data to JSON format with proper formatting and metadata.
    """
    
    def export(self, data: Dict[str, Any], output_path: str, job: ExportJob) -> bool:
        """
        Export data to JSON format.
        
        Args:
            data: Data to export
            output_path: Output file path
            job: Export job configuration
            
        Returns:
            True if export successful
        """
        try:
            # Prepare JSON data with metadata
            json_data = self._prepare_json_data(data, job)
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    json_data, 
                    f, 
                    indent=2, 
                    ensure_ascii=False,
                    default=self._json_serializer
                )
            
            job.progress = 100.0
            return True
            
        except Exception as e:
            job.error_message = f"JSON export error: {str(e)}"
            return False
    
    def _prepare_json_data(self, data: Dict[str, Any], job: ExportJob) -> Dict[str, Any]:
        """Prepare data for JSON export with proper structure."""
        json_data = {
            "export_info": {
                "job_id": job.job_id,
                "export_type": job.export_type.value,
                "export_format": job.export_format.value,
                "title": job.title,
                "description": job.description,
                "generated_at": datetime.now().isoformat(),
                "generated_by": job.created_by,
                "include_charts": job.include_charts,
                "include_metadata": job.include_metadata
            }
        }
        
        # Add date range if specified
        if job.date_range:
            json_data["export_info"]["date_range"] = job.date_range
        
        # Add data sources if specified
        if job.data_sources:
            json_data["export_info"]["data_sources"] = job.data_sources
        
        # Add filters if specified
        if job.filters:
            json_data["export_info"]["filters"] = job.filters
        
        # Process data based on export type
        if job.export_type.value == 'system_metrics':
            json_data["data"] = self._process_system_metrics(data)
        elif job.export_type.value == 'performance_report':
            json_data["data"] = self._process_performance_report(data)
        elif job.export_type.value == 'dashboard_config':
            json_data["data"] = self._process_dashboard_config(data)
        elif job.export_type.value == 'full_backup':
            json_data["data"] = self._process_full_backup(data)
        else:
            # Generic processing
            json_data["data"] = self._process_generic_data(data)
        
        # Add metadata if requested
        if job.include_metadata and 'export_metadata' in data:
            json_data["metadata"] = data['export_metadata']
        
        return json_data
    
    def _process_system_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process system metrics data for JSON export."""
        processed_data = {}
        
        # System metrics
        if 'system_metrics' in data:
            processed_data['system_metrics'] = data['system_metrics']
        
        # Process information
        if 'processes' in data:
            processed_data['processes'] = {
                'count': len(data['processes']),
                'details': data['processes']
            }
        
        # Queue metrics
        if 'queue_metrics' in data:
            processed_data['queue_metrics'] = data['queue_metrics']
        
        # Recent jobs
        if 'recent_jobs' in data:
            processed_data['recent_jobs'] = {
                'count': len(data['recent_jobs']),
                'jobs': data['recent_jobs']
            }
        
        return processed_data
    
    def _process_performance_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process performance report data for JSON export."""
        processed_data = {}
        
        if 'performance_summary' in data:
            summary = data['performance_summary']
            processed_data['performance_summary'] = summary
            
            # Calculate additional metrics
            if 'metrics' in summary:
                metrics = summary['metrics']
                processed_data['calculated_metrics'] = {
                    'performance_score': self._calculate_performance_score(metrics),
                    'health_status': self._determine_health_status(metrics),
                    'recommendations': self._generate_recommendations(metrics)
                }
        
        return processed_data
    
    def _process_dashboard_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process dashboard configuration data for JSON export."""
        processed_data = {}
        
        # Layouts
        if 'layouts' in data:
            layouts = data['layouts']
            processed_data['layouts'] = {
                'count': len(layouts),
                'configurations': layouts,
                'summary': {
                    'active_layouts': len([l for l in layouts if l.get('properties', {}).get('is_active', False)]),
                    'total_widgets': sum(
                        sum(len(tab.get('widgets', [])) for tab in layout.get('tabs', []))
                        for layout in layouts
                    ),
                    'layout_types': list(set(l.get('layout_type', 'unknown') for l in layouts))
                }
            }
        
        # Templates
        if 'templates' in data:
            templates = data['templates']
            processed_data['templates'] = {
                'count': len(templates),
                'configurations': templates,
                'summary': {
                    'categories': list(set(t.get('category', 'unknown') for t in templates)),
                    'average_rating': sum(t.get('usage', {}).get('rating', 0) for t in templates) / len(templates) if templates else 0,
                    'most_used': max(templates, key=lambda t: t.get('usage', {}).get('usage_count', 0), default={}).get('name', 'None')
                }
            }
        
        return processed_data
    
    def _process_full_backup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process full backup data for JSON export."""
        processed_data = {}
        
        # System configuration
        if 'system_config' in data:
            processed_data['system_config'] = data['system_config']
        
        # Include dashboard config data
        config_data = self._process_dashboard_config(data)
        processed_data.update(config_data)
        
        # Metrics snapshot
        if 'metrics_snapshot' in data:
            processed_data['metrics_snapshot'] = data['metrics_snapshot']
        
        # Backup summary
        processed_data['backup_summary'] = {
            'created_at': datetime.now().isoformat(),
            'components_included': list(processed_data.keys()),
            'backup_size_estimate': self._estimate_backup_size(processed_data)
        }
        
        return processed_data
    
    def _process_generic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic data for JSON export."""
        # Remove job and export_metadata from generic data
        filtered_data = {k: v for k, v in data.items() if k not in ['job', 'export_metadata']}
        return filtered_data
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score."""
        score = 100.0
        
        # Penalize for high error rate
        error_rate = metrics.get('error_rate', 0)
        if error_rate > 5:
            score -= error_rate * 2
        
        # Penalize for slow response time
        response_time = metrics.get('avg_response_time', 0)
        if response_time > 1000:  # > 1 second
            score -= (response_time - 1000) / 100
        
        # Reward for high uptime
        uptime = metrics.get('uptime_percentage', 100)
        if uptime < 99:
            score -= (99 - uptime) * 5
        
        return max(0, min(100, score))
    
    def _determine_health_status(self, metrics: Dict[str, Any]) -> str:
        """Determine health status based on metrics."""
        score = self._calculate_performance_score(metrics)
        
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 50:
            return "fair"
        else:
            return "poor"
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        error_rate = metrics.get('error_rate', 0)
        response_time = metrics.get('avg_response_time', 0)
        uptime = metrics.get('uptime_percentage', 100)
        
        if error_rate > 2:
            recommendations.append("Consider investigating error sources and implementing better error handling")
        
        if response_time > 500:
            recommendations.append("Response time is elevated - consider performance optimization")
        
        if uptime < 99.5:
            recommendations.append("Uptime is below target - review system reliability")
        
        if not recommendations:
            recommendations.append("System is performing within acceptable parameters")
        
        return recommendations
    
    def _estimate_backup_size(self, data: Dict[str, Any]) -> str:
        """Estimate backup size in human-readable format."""
        try:
            # Rough estimation based on JSON string length
            json_str = json.dumps(data, default=str)
            size_bytes = len(json_str.encode('utf-8'))
            
            if size_bytes < 1024:
                return f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except:
            return "Unknown"
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for non-standard types."""
        if hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):  # custom objects
            return obj.__dict__
        elif isinstance(obj, set):
            return list(obj)
        else:
            return str(obj)