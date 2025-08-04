"""
Process and queue management module for Ansera monitoring.

This module provides queue monitoring for document processing,
tracking pending, processing, and completed documents.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import psutil

logger = logging.getLogger(__name__)


@dataclass
class QueueMetrics:
    """Container for document processing queue metrics."""
    timestamp: datetime
    pending: int
    processing: int
    completed: int
    failed: int
    processing_rate: float  # docs per minute
    average_processing_time: float  # seconds per doc
    queue_health: str  # healthy, warning, critical


@dataclass
class ProcessingJob:
    """Represents a document processing job."""
    job_id: str
    document_path: str
    status: str  # pending, processing, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    @property
    def processing_time(self) -> Optional[float]:
        """Calculate processing time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class QueueMonitor:
    """
    Monitor document processing queue and provide metrics.
    
    This class tracks document processing jobs, calculates metrics,
    and provides queue health status.
    """
    
    def __init__(self, queue_dir: Optional[str] = None):
        """
        Initialize the queue monitor.
        
        Args:
            queue_dir: Directory containing queue files (default: .vector_db_query/queue)
        """
        self.queue_dir = Path(queue_dir or os.path.expanduser("~/.vector_db_query/queue"))
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        
        # Queue state files
        self.pending_file = self.queue_dir / "pending.json"
        self.processing_file = self.queue_dir / "processing.json"
        self.completed_file = self.queue_dir / "completed.json"
        self.failed_file = self.queue_dir / "failed.json"
        self.metrics_file = self.queue_dir / "metrics.json"
        
        # Initialize queue files if they don't exist
        self._initialize_queue_files()
        
        # Cache for metrics
        self._metrics_cache: Optional[QueueMetrics] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(seconds=5)
    
    def _initialize_queue_files(self):
        """Create queue files if they don't exist."""
        for file_path in [self.pending_file, self.processing_file, 
                         self.completed_file, self.failed_file]:
            if not file_path.exists():
                self._write_json(file_path, [])
        
        if not self.metrics_file.exists():
            self._write_json(self.metrics_file, {
                "total_processed": 0,
                "total_failed": 0,
                "last_update": datetime.now().isoformat()
            })
    
    def _read_json(self, file_path: Path) -> Any:
        """Read JSON data from file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return [] if file_path != self.metrics_file else {}
    
    def _write_json(self, file_path: Path, data: Any):
        """Write JSON data to file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error writing {file_path}: {e}")
    
    def add_to_queue(self, document_path: str) -> str:
        """
        Add a document to the processing queue.
        
        Args:
            document_path: Path to the document to process
            
        Returns:
            Job ID for tracking
        """
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
        
        job = ProcessingJob(
            job_id=job_id,
            document_path=document_path,
            status="pending"
        )
        
        # Add to pending queue
        pending = self._read_json(self.pending_file)
        pending.append(asdict(job))
        self._write_json(self.pending_file, pending)
        
        logger.info(f"Added job {job_id} to queue: {document_path}")
        return job_id
    
    def start_processing(self, job_id: str) -> bool:
        """
        Move a job from pending to processing.
        
        Args:
            job_id: Job ID to start processing
            
        Returns:
            Success status
        """
        # Find job in pending queue
        pending = self._read_json(self.pending_file)
        job_data = None
        
        for i, job in enumerate(pending):
            if job['job_id'] == job_id:
                job_data = pending.pop(i)
                break
        
        if not job_data:
            logger.error(f"Job {job_id} not found in pending queue")
            return False
        
        # Update job status
        job_data['status'] = 'processing'
        job_data['started_at'] = datetime.now().isoformat()
        
        # Add to processing queue
        processing = self._read_json(self.processing_file)
        processing.append(job_data)
        
        # Save updated queues
        self._write_json(self.pending_file, pending)
        self._write_json(self.processing_file, processing)
        
        logger.info(f"Started processing job {job_id}")
        return True
    
    def complete_processing(self, job_id: str, success: bool = True, 
                          error_message: Optional[str] = None) -> bool:
        """
        Mark a job as completed or failed.
        
        Args:
            job_id: Job ID to complete
            success: Whether processing was successful
            error_message: Error message if failed
            
        Returns:
            Success status
        """
        # Find job in processing queue
        processing = self._read_json(self.processing_file)
        job_data = None
        
        for i, job in enumerate(processing):
            if job['job_id'] == job_id:
                job_data = processing.pop(i)
                break
        
        if not job_data:
            logger.error(f"Job {job_id} not found in processing queue")
            return False
        
        # Update job status
        job_data['completed_at'] = datetime.now().isoformat()
        job_data['status'] = 'completed' if success else 'failed'
        if error_message:
            job_data['error_message'] = error_message
        
        # Add to appropriate queue
        if success:
            completed = self._read_json(self.completed_file)
            completed.append(job_data)
            self._write_json(self.completed_file, completed)
        else:
            failed = self._read_json(self.failed_file)
            failed.append(job_data)
            self._write_json(self.failed_file, failed)
        
        # Save updated processing queue
        self._write_json(self.processing_file, processing)
        
        # Update metrics
        self._update_metrics(success)
        
        logger.info(f"Completed job {job_id}: {'success' if success else 'failed'}")
        return True
    
    def _update_metrics(self, success: bool):
        """Update processing metrics."""
        metrics = self._read_json(self.metrics_file)
        
        if success:
            metrics['total_processed'] = metrics.get('total_processed', 0) + 1
        else:
            metrics['total_failed'] = metrics.get('total_failed', 0) + 1
        
        metrics['last_update'] = datetime.now().isoformat()
        self._write_json(self.metrics_file, metrics)
    
    def get_queue_metrics(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get current queue metrics.
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            Dictionary containing queue metrics
        """
        # Check cache
        if not force_refresh and self._is_cache_valid():
            return asdict(self._metrics_cache)
        
        # Calculate fresh metrics
        pending = self._read_json(self.pending_file)
        processing = self._read_json(self.processing_file)
        completed = self._read_json(self.completed_file)
        failed = self._read_json(self.failed_file)
        
        # Calculate processing rate
        processing_rate = self._calculate_processing_rate(completed)
        avg_time = self._calculate_average_processing_time(completed)
        
        # Determine queue health
        queue_health = self._determine_queue_health(
            len(pending), len(processing), processing_rate
        )
        
        metrics = QueueMetrics(
            timestamp=datetime.now(),
            pending=len(pending),
            processing=len(processing),
            completed=len(completed),
            failed=len(failed),
            processing_rate=processing_rate,
            average_processing_time=avg_time,
            queue_health=queue_health
        )
        
        # Update cache
        self._metrics_cache = metrics
        self._cache_timestamp = datetime.now()
        
        return asdict(metrics)
    
    def _is_cache_valid(self) -> bool:
        """Check if metrics cache is still valid."""
        if not self._metrics_cache or not self._cache_timestamp:
            return False
        
        age = datetime.now() - self._cache_timestamp
        return age < self._cache_duration
    
    def _calculate_processing_rate(self, completed: List[Dict]) -> float:
        """Calculate documents processed per minute."""
        if not completed:
            return 0.0
        
        # Get completed jobs from last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_completed = []
        
        for job in completed:
            if 'completed_at' in job:
                completed_time = datetime.fromisoformat(job['completed_at'])
                if completed_time > one_hour_ago:
                    recent_completed.append(job)
        
        if not recent_completed:
            return 0.0
        
        # Calculate rate
        time_span = datetime.now() - datetime.fromisoformat(recent_completed[0]['completed_at'])
        minutes = max(time_span.total_seconds() / 60, 1)  # Avoid division by zero
        
        return len(recent_completed) / minutes
    
    def _calculate_average_processing_time(self, completed: List[Dict]) -> float:
        """Calculate average processing time in seconds."""
        if not completed:
            return 0.0
        
        processing_times = []
        
        for job in completed[-10:]:  # Last 10 jobs
            if 'started_at' in job and 'completed_at' in job:
                start = datetime.fromisoformat(job['started_at'])
                end = datetime.fromisoformat(job['completed_at'])
                processing_times.append((end - start).total_seconds())
        
        if not processing_times:
            return 0.0
        
        return sum(processing_times) / len(processing_times)
    
    def _determine_queue_health(self, pending: int, processing: int, 
                               rate: float) -> str:
        """Determine queue health status."""
        # Simple health rules
        if pending > 100 and rate < 1.0:
            return "critical"  # Large backlog with slow processing
        elif pending > 50 or processing > 10:
            return "warning"   # Moderate backlog
        else:
            return "healthy"   # Normal operation
    
    def get_recent_jobs(self, status: str = "all", limit: int = 10) -> List[Dict]:
        """
        Get recent jobs by status.
        
        Args:
            status: Job status filter (pending, processing, completed, failed, all)
            limit: Maximum number of jobs to return
            
        Returns:
            List of recent jobs
        """
        jobs = []
        
        if status in ["pending", "all"]:
            jobs.extend(self._read_json(self.pending_file)[-limit:])
        
        if status in ["processing", "all"]:
            jobs.extend(self._read_json(self.processing_file)[-limit:])
        
        if status in ["completed", "all"]:
            jobs.extend(self._read_json(self.completed_file)[-limit:])
        
        if status in ["failed", "all"]:
            jobs.extend(self._read_json(self.failed_file)[-limit:])
        
        # Sort by timestamp (most recent first)
        jobs.sort(key=lambda x: x.get('started_at', x.get('job_id', '')), reverse=True)
        
        return jobs[:limit]
    
    def clear_completed(self, older_than_hours: int = 24):
        """
        Clear completed jobs older than specified hours.
        
        Args:
            older_than_hours: Clear jobs older than this many hours
        """
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        # Clear old completed jobs
        completed = self._read_json(self.completed_file)
        recent_completed = []
        
        for job in completed:
            if 'completed_at' in job:
                completed_time = datetime.fromisoformat(job['completed_at'])
                if completed_time > cutoff_time:
                    recent_completed.append(job)
        
        self._write_json(self.completed_file, recent_completed)
        
        # Clear old failed jobs
        failed = self._read_json(self.failed_file)
        recent_failed = []
        
        for job in failed:
            if 'completed_at' in job:
                completed_time = datetime.fromisoformat(job['completed_at'])
                if completed_time > cutoff_time:
                    recent_failed.append(job)
        
        self._write_json(self.failed_file, recent_failed)
        
        logger.info(f"Cleared jobs older than {older_than_hours} hours")
    
    def reset_queue(self):
        """Reset all queues (USE WITH CAUTION)."""
        # Move all processing back to pending
        processing = self._read_json(self.processing_file)
        pending = self._read_json(self.pending_file)
        
        for job in processing:
            job['status'] = 'pending'
            job.pop('started_at', None)
            pending.append(job)
        
        self._write_json(self.pending_file, pending)
        self._write_json(self.processing_file, [])
        
        logger.warning("Queue reset - all processing jobs moved to pending")
    
    def get_pending_jobs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get pending jobs for processing.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of pending jobs
        """
        pending = self._read_json(self.pending_file)
        
        if limit:
            return pending[:limit]
        return pending
    
    def update_job_status(self, job_id: str, status: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update job status and metadata.
        
        Args:
            job_id: Job ID to update
            status: New status (pending, processing, completed, failed)
            metadata: Additional metadata to merge into job
            
        Returns:
            Success status
        """
        # Check current location of job
        all_queues = {
            'pending': self.pending_file,
            'processing': self.processing_file,
            'completed': self.completed_file,
            'failed': self.failed_file
        }
        
        job_data = None
        source_file = None
        source_queue = None
        
        # Find the job
        for queue_name, queue_file in all_queues.items():
            queue_data = self._read_json(queue_file)
            for i, job in enumerate(queue_data):
                if job['job_id'] == job_id:
                    job_data = queue_data.pop(i)
                    source_file = queue_file
                    source_queue = queue_data
                    break
            if job_data:
                break
        
        if not job_data:
            logger.error(f"Job {job_id} not found in any queue")
            return False
        
        # Update job data
        job_data['status'] = status
        if metadata:
            job_data.update(metadata)
        
        # Handle status transitions
        if status == 'processing' and 'started_at' not in job_data:
            job_data['started_at'] = datetime.now().isoformat()
        elif status in ['completed', 'failed'] and 'completed_at' not in job_data:
            job_data['completed_at'] = datetime.now().isoformat()
        
        # Save source queue without the job
        if source_file:
            self._write_json(source_file, source_queue)
        
        # Add to target queue
        target_file = all_queues.get(status)
        if target_file:
            target_queue = self._read_json(target_file)
            target_queue.append(job_data)
            self._write_json(target_file, target_queue)
            
            # Update metrics if completed or failed
            if status in ['completed', 'failed']:
                self._update_metrics(status == 'completed')
        
        logger.info(f"Updated job {job_id} status to {status}")
        return True


# Example usage for testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create monitor instance
    monitor = QueueMonitor()
    
    # Add some test jobs
    print("Adding test jobs to queue...")
    for i in range(5):
        job_id = monitor.add_to_queue(f"/path/to/document_{i}.pdf")
        print(f"Added job: {job_id}")
    
    # Get metrics
    print("\nQueue Metrics:")
    print("-" * 50)
    metrics = monitor.get_queue_metrics()
    print(f"Pending: {metrics['pending']}")
    print(f"Processing: {metrics['processing']}")
    print(f"Completed: {metrics['completed']}")
    print(f"Failed: {metrics['failed']}")
    print(f"Processing Rate: {metrics['processing_rate']:.2f} docs/min")
    print(f"Avg Processing Time: {metrics['average_processing_time']:.2f} seconds")
    print(f"Queue Health: {metrics['queue_health']}")
    
    # Show recent jobs
    print("\nRecent Jobs:")
    print("-" * 50)
    for job in monitor.get_recent_jobs(limit=5):
        print(f"[{job['status']}] {job['job_id']} - {job['document_path']}")