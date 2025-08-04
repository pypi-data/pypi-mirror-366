"""
Export Manager for coordinating all export operations.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from threading import RLock
from pathlib import Path
import uuid
from dataclasses import dataclass, field
from enum import Enum

from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory


class ExportFormat(Enum):
    """Supported export formats."""
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    EXCEL = "xlsx"
    HTML = "html"


class ExportType(Enum):
    """Types of exports."""
    SYSTEM_METRICS = "system_metrics"
    DASHBOARD_CONFIG = "dashboard_config"
    WIDGET_DATA = "widget_data"
    PERFORMANCE_REPORT = "performance_report"
    LOG_EXPORT = "log_export"
    FULL_BACKUP = "full_backup"
    CUSTOM_REPORT = "custom_report"


@dataclass
class ExportJob:
    """Export job configuration."""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    export_type: ExportType = ExportType.SYSTEM_METRICS
    export_format: ExportFormat = ExportFormat.CSV
    
    # Export parameters
    title: str = "System Export"
    description: str = ""
    include_charts: bool = True
    include_metadata: bool = True
    date_range: Optional[Dict[str, str]] = None
    
    # Data sources
    data_sources: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Output settings
    output_filename: Optional[str] = None
    output_directory: Optional[str] = None
    compress_output: bool = False
    
    # Scheduling
    scheduled: bool = False
    schedule_cron: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    file_size: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'job_id': self.job_id,
            'export_type': self.export_type.value,
            'export_format': self.export_format.value,
            'title': self.title,
            'description': self.description,
            'include_charts': self.include_charts,
            'include_metadata': self.include_metadata,
            'date_range': self.date_range,
            'data_sources': self.data_sources,
            'filters': self.filters,
            'output_filename': self.output_filename,
            'output_directory': self.output_directory,
            'compress_output': self.compress_output,
            'scheduled': self.scheduled,
            'schedule_cron': self.schedule_cron,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'status': self.status,
            'progress': self.progress,
            'error_message': self.error_message,
            'output_path': self.output_path,
            'file_size': self.file_size
        }


class ExportManager:
    """
    Manages all export operations and coordinates between different exporters.
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize export manager."""
        self._lock = RLock()
        self.data_dir = data_dir or os.path.join(os.getcwd(), ".data", "monitoring")
        self.export_dir = os.path.join(self.data_dir, "exports")
        self.change_tracker = get_change_tracker()
        
        # Create directories
        os.makedirs(self.export_dir, exist_ok=True)
        os.makedirs(os.path.join(self.export_dir, "jobs"), exist_ok=True)
        os.makedirs(os.path.join(self.export_dir, "outputs"), exist_ok=True)
        
        # Job tracking
        self._active_jobs: Dict[str, ExportJob] = {}
        self._job_history: List[ExportJob] = []
        
        # Load existing jobs
        self._load_job_history()
    
    def _load_job_history(self) -> None:
        """Load job history from disk."""
        history_file = os.path.join(self.export_dir, "job_history.json")
        
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                
                for job_data in history_data.get('jobs', []):
                    job = self._dict_to_export_job(job_data)
                    self._job_history.append(job)
                    
            except Exception as e:
                print(f"Error loading job history: {e}")
    
    def _save_job_history(self) -> None:
        """Save job history to disk."""
        history_file = os.path.join(self.export_dir, "job_history.json")
        
        try:
            history_data = {
                'jobs': [job.to_dict() for job in self._job_history],
                'updated_at': datetime.now().isoformat()
            }
            
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving job history: {e}")
    
    def _dict_to_export_job(self, data: Dict[str, Any]) -> ExportJob:
        """Convert dictionary to ExportJob."""
        job = ExportJob(
            job_id=data.get('job_id', str(uuid.uuid4())),
            export_type=ExportType(data.get('export_type', 'system_metrics')),
            export_format=ExportFormat(data.get('export_format', 'csv')),
            title=data.get('title', 'System Export'),
            description=data.get('description', ''),
            include_charts=data.get('include_charts', True),
            include_metadata=data.get('include_metadata', True),
            date_range=data.get('date_range'),
            data_sources=data.get('data_sources', []),
            filters=data.get('filters', {}),
            output_filename=data.get('output_filename'),
            output_directory=data.get('output_directory'),
            compress_output=data.get('compress_output', False),
            scheduled=data.get('scheduled', False),
            schedule_cron=data.get('schedule_cron'),
            created_by=data.get('created_by', 'system'),
            status=data.get('status', 'pending'),
            progress=data.get('progress', 0.0),
            error_message=data.get('error_message'),
            output_path=data.get('output_path'),
            file_size=data.get('file_size')
        )
        
        # Parse datetime
        if 'created_at' in data:
            try:
                job.created_at = datetime.fromisoformat(data['created_at'])
            except:
                pass
        
        return job
    
    def create_export_job(self, 
                         export_type: ExportType,
                         export_format: ExportFormat,
                         title: str = None,
                         **kwargs) -> str:
        """
        Create a new export job.
        
        Args:
            export_type: Type of export
            export_format: Export format
            title: Job title
            **kwargs: Additional job parameters
            
        Returns:
            Job ID
        """
        with self._lock:
            job = ExportJob(
                export_type=export_type,
                export_format=export_format,
                title=title or f"{export_type.value.replace('_', ' ').title()} Export",
                **kwargs
            )
            
            # Generate filename if not provided
            if not job.output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                job.output_filename = f"{job.export_type.value}_{timestamp}.{job.export_format.value}"
            
            # Set output directory if not provided
            if not job.output_directory:
                job.output_directory = os.path.join(self.export_dir, "outputs")
            
            # Store job
            self._active_jobs[job.job_id] = job
            
            # Track change
            self.change_tracker.track_change(
                change_type=ChangeType.CREATE,
                category=ChangeCategory.EXPORT,
                entity_id=job.job_id,
                description=f"Created export job: {job.title}",
                metadata={'export_type': job.export_type.value, 'format': job.export_format.value}
            )
            
            return job.job_id
    
    def execute_export_job(self, job_id: str) -> bool:
        """
        Execute an export job.
        
        Args:
            job_id: Job ID to execute
            
        Returns:
            True if job started successfully
        """
        with self._lock:
            if job_id not in self._active_jobs:
                return False
            
            job = self._active_jobs[job_id]
            
            if job.status != 'pending':
                return False
            
            try:
                # Update job status
                job.status = 'running'
                job.progress = 0.0
                
                # Get appropriate exporter
                exporter = self._get_exporter(job.export_format)
                if not exporter:
                    job.status = 'failed'
                    job.error_message = f"No exporter available for format: {job.export_format.value}"
                    return False
                
                # Execute export
                success = self._execute_export_with_exporter(job, exporter)
                
                if success:
                    job.status = 'completed'
                    job.progress = 100.0
                    
                    # Move to history
                    self._job_history.append(job)
                    del self._active_jobs[job_id]
                    self._save_job_history()
                    
                    # Track completion
                    self.change_tracker.track_change(
                        change_type=ChangeType.UPDATE,
                        category=ChangeCategory.EXPORT,
                        entity_id=job.job_id,
                        description=f"Export job completed: {job.title}",
                        metadata={'output_path': job.output_path, 'file_size': job.file_size}
                    )
                else:
                    job.status = 'failed'
                
                return success
                
            except Exception as e:
                job.status = 'failed'
                job.error_message = str(e)
                return False
    
    def _get_exporter(self, export_format: ExportFormat):
        """Get exporter for format."""
        # Import here to avoid circular imports
        from .pdf_exporter import PDFExporter
        from .csv_exporter import CSVExporter
        from .json_exporter import JSONExporter
        from .excel_exporter import ExcelExporter
        from .html_exporter import HTMLExporter
        
        exporters = {
            ExportFormat.PDF: PDFExporter,
            ExportFormat.CSV: CSVExporter,
            ExportFormat.JSON: JSONExporter,
            ExportFormat.EXCEL: ExcelExporter,
            ExportFormat.HTML: HTMLExporter
        }
        
        exporter_class = exporters.get(export_format)
        return exporter_class() if exporter_class else None
    
    def _execute_export_with_exporter(self, job: ExportJob, exporter) -> bool:
        """Execute export using specific exporter."""
        try:
            # Collect data based on export type
            data = self._collect_export_data(job)
            
            # Update progress
            job.progress = 25.0
            
            # Generate output path
            output_path = os.path.join(job.output_directory, job.output_filename)
            
            # Execute export
            success = exporter.export(data, output_path, job)
            
            if success:
                job.output_path = output_path
                
                # Get file size
                if os.path.exists(output_path):
                    job.file_size = os.path.getsize(output_path)
                
                job.progress = 100.0
                return True
            else:
                job.error_message = "Export failed during generation"
                return False
                
        except Exception as e:
            job.error_message = f"Export execution error: {str(e)}"
            return False
    
    def _collect_export_data(self, job: ExportJob) -> Dict[str, Any]:
        """Collect data for export based on job type."""
        # Import monitoring components
        from ..metrics import SystemMonitor
        from ..process_manager import QueueMonitor
        from ..layout.layout_manager import get_layout_manager
        
        data = {
            'job': job.to_dict(),
            'export_metadata': {
                'generated_at': datetime.now().isoformat(),
                'system': 'Ansera Monitoring Dashboard',
                'version': '1.0.0'
            }
        }
        
        try:
            if job.export_type == ExportType.SYSTEM_METRICS:
                # Collect system metrics
                system_monitor = SystemMonitor()
                data['system_metrics'] = system_monitor.get_quick_stats()
                data['processes'] = system_monitor.get_ansera_processes()
                
                # Queue metrics
                queue_monitor = QueueMonitor()
                data['queue_metrics'] = queue_monitor.get_queue_metrics()
                data['recent_jobs'] = queue_monitor.get_recent_jobs(limit=50)
                
            elif job.export_type == ExportType.DASHBOARD_CONFIG:
                # Collect dashboard configuration
                layout_manager = get_layout_manager()
                layouts = layout_manager.get_layouts_by_owner("system")
                data['layouts'] = [layout.to_dict() for layout in layouts]
                data['templates'] = [template.to_dict() for template in layout_manager.get_templates()]
                
            elif job.export_type == ExportType.PERFORMANCE_REPORT:
                # Collect performance data (placeholder - would integrate with performance tracking)
                data['performance_summary'] = {
                    'report_period': job.date_range or {'start': '2025-01-01', 'end': datetime.now().isoformat()},
                    'metrics': {
                        'avg_response_time': 125.5,
                        'total_requests': 15420,
                        'error_rate': 0.8,
                        'uptime_percentage': 99.95
                    }
                }
                
            elif job.export_type == ExportType.FULL_BACKUP:
                # Collect full system backup data
                data.update(self._collect_full_backup_data())
                
            # Apply filters if specified
            if job.filters:
                data = self._apply_filters(data, job.filters)
                
        except Exception as e:
            data['collection_error'] = str(e)
        
        return data
    
    def _collect_full_backup_data(self) -> Dict[str, Any]:
        """Collect data for full system backup."""
        from ..layout.layout_manager import get_layout_manager
        from ..metrics import SystemMonitor
        from ..process_manager import QueueMonitor
        
        backup_data = {}
        
        try:
            # Layouts and templates
            layout_manager = get_layout_manager()
            backup_data['layouts'] = [l.to_dict() for l in layout_manager.get_layouts_by_owner("system")]
            backup_data['templates'] = [t.to_dict() for t in layout_manager.get_templates()]
            
            # System configuration
            backup_data['system_config'] = {
                'monitoring_enabled': True,
                'data_directory': self.data_dir,
                'export_directory': self.export_dir
            }
            
            # Recent metrics snapshot
            system_monitor = SystemMonitor()
            queue_monitor = QueueMonitor()
            
            backup_data['metrics_snapshot'] = {
                'system': system_monitor.get_quick_stats(),
                'queue': queue_monitor.get_queue_metrics(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            backup_data['backup_error'] = str(e)
        
        return backup_data
    
    def _apply_filters(self, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply filters to export data."""
        # Simple filtering implementation
        filtered_data = data.copy()
        
        # Date range filtering
        if 'date_range' in filters:
            # Would implement date filtering logic here
            pass
        
        # Source filtering
        if 'sources' in filters:
            # Would implement source filtering logic here
            pass
        
        return filtered_data
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an export job."""
        with self._lock:
            # Check active jobs
            if job_id in self._active_jobs:
                return self._active_jobs[job_id].to_dict()
            
            # Check history
            for job in self._job_history:
                if job.job_id == job_id:
                    return job.to_dict()
            
            return None
    
    def list_jobs(self, include_history: bool = True, limit: int = 50) -> List[Dict[str, Any]]:
        """List export jobs."""
        with self._lock:
            jobs = []
            
            # Add active jobs
            jobs.extend([job.to_dict() for job in self._active_jobs.values()])
            
            # Add history if requested
            if include_history:
                # Sort by created_at descending and limit
                history_jobs = sorted(self._job_history, key=lambda x: x.created_at, reverse=True)
                jobs.extend([job.to_dict() for job in history_jobs[:limit]])
            
            return jobs
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel an active export job."""
        with self._lock:
            if job_id in self._active_jobs:
                job = self._active_jobs[job_id]
                if job.status in ['pending', 'running']:
                    job.status = 'cancelled'
                    job.error_message = "Job cancelled by user"
                    
                    # Move to history
                    self._job_history.append(job)
                    del self._active_jobs[job_id]
                    self._save_job_history()
                    
                    return True
            return False
    
    def delete_job(self, job_id: str, delete_output: bool = False) -> bool:
        """Delete a job from history."""
        with self._lock:
            # Find and remove from history
            for i, job in enumerate(self._job_history):
                if job.job_id == job_id:
                    # Delete output file if requested
                    if delete_output and job.output_path and os.path.exists(job.output_path):
                        try:
                            os.remove(job.output_path)
                        except:
                            pass
                    
                    # Remove from history
                    self._job_history.pop(i)
                    self._save_job_history()
                    
                    # Track deletion
                    self.change_tracker.track_change(
                        change_type=ChangeType.DELETE,
                        category=ChangeCategory.EXPORT,
                        entity_id=job_id,
                        description=f"Deleted export job: {job.title}"
                    )
                    
                    return True
            
            return False
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get export statistics."""
        with self._lock:
            all_jobs = list(self._active_jobs.values()) + self._job_history
            
            stats = {
                'total_jobs': len(all_jobs),
                'active_jobs': len(self._active_jobs),
                'completed_jobs': len([j for j in all_jobs if j.status == 'completed']),
                'failed_jobs': len([j for j in all_jobs if j.status == 'failed']),
                'total_exported_size': sum(j.file_size or 0 for j in all_jobs if j.file_size),
                'export_types': {},
                'export_formats': {},
                'recent_activity': []
            }
            
            # Count by type and format
            for job in all_jobs:
                export_type = job.export_type.value
                export_format = job.export_format.value
                
                stats['export_types'][export_type] = stats['export_types'].get(export_type, 0) + 1
                stats['export_formats'][export_format] = stats['export_formats'].get(export_format, 0) + 1
            
            # Recent activity (last 10 jobs)
            recent_jobs = sorted(all_jobs, key=lambda x: x.created_at, reverse=True)[:10]
            stats['recent_activity'] = [
                {
                    'job_id': job.job_id,
                    'title': job.title,
                    'status': job.status,
                    'created_at': job.created_at.isoformat(),
                    'export_type': job.export_type.value,
                    'export_format': job.export_format.value
                }
                for job in recent_jobs
            ]
            
            return stats


# Global manager instance
_export_manager = None
_manager_lock = RLock()


def get_export_manager() -> ExportManager:
    """
    Get the global export manager instance (singleton).
    
    Returns:
        Global export manager instance
    """
    global _export_manager
    with _manager_lock:
        if _export_manager is None:
            _export_manager = ExportManager()
        return _export_manager


def reset_export_manager() -> None:
    """Reset the global export manager (mainly for testing)."""
    global _export_manager
    with _manager_lock:
        _export_manager = None