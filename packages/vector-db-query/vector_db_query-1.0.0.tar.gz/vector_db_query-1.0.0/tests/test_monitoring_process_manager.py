"""
Unit tests for the Ansera monitoring process manager module.

Tests the QueueMonitor class and queue management functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from src.vector_db_query.monitoring.process_manager import QueueMonitor, QueueMetrics, ProcessingJob


class TestProcessingJob(unittest.TestCase):
    """Test cases for ProcessingJob dataclass."""
    
    def test_job_creation(self):
        """Test creating ProcessingJob instance."""
        job = ProcessingJob(
            job_id="job_123",
            document_path="/path/to/doc.pdf",
            status="pending"
        )
        
        self.assertEqual(job.job_id, "job_123")
        self.assertEqual(job.document_path, "/path/to/doc.pdf")
        self.assertEqual(job.status, "pending")
        self.assertIsNone(job.started_at)
        self.assertIsNone(job.completed_at)
        self.assertIsNone(job.error_message)
    
    def test_processing_time_calculation(self):
        """Test calculating processing time."""
        start = datetime.now()
        end = start + timedelta(seconds=30)
        
        job = ProcessingJob(
            job_id="job_123",
            document_path="/path/to/doc.pdf",
            status="completed",
            started_at=start,
            completed_at=end
        )
        
        self.assertEqual(job.processing_time, 30.0)
    
    def test_processing_time_none(self):
        """Test processing time when not complete."""
        job = ProcessingJob(
            job_id="job_123",
            document_path="/path/to/doc.pdf",
            status="processing",
            started_at=datetime.now()
        )
        
        self.assertIsNone(job.processing_time)


class TestQueueMonitor(unittest.TestCase):
    """Test cases for QueueMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.queue_dir = Path(self.test_dir) / "queue"
        self.monitor = QueueMonitor(str(self.queue_dir))
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test QueueMonitor initialization."""
        self.assertTrue(self.queue_dir.exists())
        self.assertTrue(self.monitor.pending_file.exists())
        self.assertTrue(self.monitor.processing_file.exists())
        self.assertTrue(self.monitor.completed_file.exists())
        self.assertTrue(self.monitor.failed_file.exists())
        self.assertTrue(self.monitor.metrics_file.exists())
    
    def test_add_to_queue(self):
        """Test adding document to queue."""
        job_id = self.monitor.add_to_queue("/path/to/document.pdf")
        
        # Check job ID format
        self.assertTrue(job_id.startswith("job_"))
        
        # Check pending queue
        with open(self.monitor.pending_file, 'r') as f:
            pending = json.load(f)
        
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]['job_id'], job_id)
        self.assertEqual(pending[0]['document_path'], "/path/to/document.pdf")
        self.assertEqual(pending[0]['status'], "pending")
    
    def test_start_processing(self):
        """Test moving job to processing."""
        # Add a job first
        job_id = self.monitor.add_to_queue("/path/to/document.pdf")
        
        # Start processing
        success = self.monitor.start_processing(job_id)
        self.assertTrue(success)
        
        # Check queues
        with open(self.monitor.pending_file, 'r') as f:
            pending = json.load(f)
        with open(self.monitor.processing_file, 'r') as f:
            processing = json.load(f)
        
        self.assertEqual(len(pending), 0)
        self.assertEqual(len(processing), 1)
        self.assertEqual(processing[0]['job_id'], job_id)
        self.assertEqual(processing[0]['status'], 'processing')
        self.assertIn('started_at', processing[0])
    
    def test_start_processing_nonexistent_job(self):
        """Test starting processing for non-existent job."""
        success = self.monitor.start_processing("nonexistent_job")
        self.assertFalse(success)
    
    def test_complete_processing_success(self):
        """Test completing job successfully."""
        # Add and start a job
        job_id = self.monitor.add_to_queue("/path/to/document.pdf")
        self.monitor.start_processing(job_id)
        
        # Complete processing
        success = self.monitor.complete_processing(job_id, success=True)
        self.assertTrue(success)
        
        # Check queues
        with open(self.monitor.processing_file, 'r') as f:
            processing = json.load(f)
        with open(self.monitor.completed_file, 'r') as f:
            completed = json.load(f)
        
        self.assertEqual(len(processing), 0)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0]['job_id'], job_id)
        self.assertEqual(completed[0]['status'], 'completed')
        self.assertIn('completed_at', completed[0])
    
    def test_complete_processing_failure(self):
        """Test failing job processing."""
        # Add and start a job
        job_id = self.monitor.add_to_queue("/path/to/document.pdf")
        self.monitor.start_processing(job_id)
        
        # Fail processing
        success = self.monitor.complete_processing(
            job_id, 
            success=False, 
            error_message="Processing error"
        )
        self.assertTrue(success)
        
        # Check queues
        with open(self.monitor.failed_file, 'r') as f:
            failed = json.load(f)
        
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]['job_id'], job_id)
        self.assertEqual(failed[0]['status'], 'failed')
        self.assertEqual(failed[0]['error_message'], "Processing error")
    
    def test_get_queue_metrics(self):
        """Test getting queue metrics."""
        # Add some jobs
        job1 = self.monitor.add_to_queue("/path/to/doc1.pdf")
        job2 = self.monitor.add_to_queue("/path/to/doc2.pdf")
        job3 = self.monitor.add_to_queue("/path/to/doc3.pdf")
        
        # Process some
        self.monitor.start_processing(job1)
        self.monitor.complete_processing(job1, success=True)
        
        self.monitor.start_processing(job2)
        
        # Get metrics
        metrics = self.monitor.get_queue_metrics()
        
        self.assertEqual(metrics['pending'], 1)  # job3
        self.assertEqual(metrics['processing'], 1)  # job2
        self.assertEqual(metrics['completed'], 1)  # job1
        self.assertEqual(metrics['failed'], 0)
        self.assertIn('processing_rate', metrics)
        self.assertIn('average_processing_time', metrics)
        self.assertIn('queue_health', metrics)
    
    def test_get_recent_jobs(self):
        """Test getting recent jobs."""
        # Add multiple jobs
        jobs = []
        for i in range(5):
            job_id = self.monitor.add_to_queue(f"/path/to/doc{i}.pdf")
            jobs.append(job_id)
        
        # Get recent pending jobs
        recent = self.monitor.get_recent_jobs(status="pending", limit=3)
        
        self.assertEqual(len(recent), 3)
        for job in recent:
            self.assertEqual(job['status'], 'pending')
    
    def test_clear_completed(self):
        """Test clearing old completed jobs."""
        # Add and complete some jobs
        for i in range(3):
            job_id = self.monitor.add_to_queue(f"/path/to/doc{i}.pdf")
            self.monitor.start_processing(job_id)
            self.monitor.complete_processing(job_id, success=True)
        
        # Manually set old completion time for first job
        with open(self.monitor.completed_file, 'r') as f:
            completed = json.load(f)
        
        old_time = (datetime.now() - timedelta(hours=48)).isoformat()
        completed[0]['completed_at'] = old_time
        
        with open(self.monitor.completed_file, 'w') as f:
            json.dump(completed, f)
        
        # Clear old jobs
        self.monitor.clear_completed(older_than_hours=24)
        
        # Check remaining
        with open(self.monitor.completed_file, 'r') as f:
            completed = json.load(f)
        
        self.assertEqual(len(completed), 2)  # Only recent jobs remain
    
    def test_reset_queue(self):
        """Test resetting queue."""
        # Add jobs in different states
        job1 = self.monitor.add_to_queue("/path/to/doc1.pdf")
        job2 = self.monitor.add_to_queue("/path/to/doc2.pdf")
        
        self.monitor.start_processing(job1)
        
        # Reset queue
        self.monitor.reset_queue()
        
        # Check all jobs are pending
        with open(self.monitor.pending_file, 'r') as f:
            pending = json.load(f)
        with open(self.monitor.processing_file, 'r') as f:
            processing = json.load(f)
        
        self.assertEqual(len(pending), 2)
        self.assertEqual(len(processing), 0)
    
    def test_get_pending_jobs(self):
        """Test getting pending jobs for processing."""
        # Add multiple jobs
        for i in range(5):
            self.monitor.add_to_queue(f"/path/to/doc{i}.pdf")
        
        # Get limited pending jobs
        jobs = self.monitor.get_pending_jobs(limit=3)
        
        self.assertEqual(len(jobs), 3)
        for job in jobs:
            self.assertEqual(job['status'], 'pending')
        
        # Get all pending jobs
        all_jobs = self.monitor.get_pending_jobs()
        self.assertEqual(len(all_jobs), 5)
    
    def test_update_job_status(self):
        """Test updating job status."""
        # Add a job
        job_id = self.monitor.add_to_queue("/path/to/document.pdf")
        
        # Update to processing
        success = self.monitor.update_job_status(
            job_id, 
            'processing',
            {'worker_pid': 12345}
        )
        self.assertTrue(success)
        
        # Check job moved and updated
        with open(self.monitor.processing_file, 'r') as f:
            processing = json.load(f)
        
        self.assertEqual(len(processing), 1)
        self.assertEqual(processing[0]['status'], 'processing')
        self.assertEqual(processing[0]['worker_pid'], 12345)
        self.assertIn('started_at', processing[0])
    
    def test_determine_queue_health(self):
        """Test queue health determination."""
        # Test healthy state
        health = self.monitor._determine_queue_health(
            pending=10, processing=2, rate=5.0
        )
        self.assertEqual(health, "healthy")
        
        # Test warning state
        health = self.monitor._determine_queue_health(
            pending=60, processing=5, rate=2.0
        )
        self.assertEqual(health, "warning")
        
        # Test critical state
        health = self.monitor._determine_queue_health(
            pending=150, processing=5, rate=0.5
        )
        self.assertEqual(health, "critical")
    
    def test_calculate_processing_rate(self):
        """Test processing rate calculation."""
        # Create completed jobs with known times
        completed_jobs = []
        base_time = datetime.now() - timedelta(minutes=30)
        
        for i in range(6):
            completed_jobs.append({
                'job_id': f'job_{i}',
                'completed_at': (base_time + timedelta(minutes=i*5)).isoformat()
            })
        
        # Write to completed file
        with open(self.monitor.completed_file, 'w') as f:
            json.dump(completed_jobs, f)
        
        # Calculate rate (should be ~6 jobs in 30 minutes = 0.2/min)
        rate = self.monitor._calculate_processing_rate(completed_jobs)
        
        self.assertGreater(rate, 0)
        self.assertLess(rate, 1.0)  # Less than 1 per minute
    
    def test_cache_functionality(self):
        """Test metrics caching."""
        # Get metrics (should calculate)
        metrics1 = self.monitor.get_queue_metrics()
        
        # Get again immediately (should use cache)
        metrics2 = self.monitor.get_queue_metrics()
        
        self.assertEqual(metrics1, metrics2)
        
        # Force refresh
        metrics3 = self.monitor.get_queue_metrics(force_refresh=True)
        
        # Timestamp should be different
        self.assertNotEqual(metrics1['timestamp'], metrics3['timestamp'])


class TestQueueMetrics(unittest.TestCase):
    """Test cases for QueueMetrics dataclass."""
    
    def test_metrics_creation(self):
        """Test creating QueueMetrics instance."""
        now = datetime.now()
        metrics = QueueMetrics(
            timestamp=now,
            pending=10,
            processing=2,
            completed=100,
            failed=5,
            processing_rate=2.5,
            average_processing_time=30.0,
            queue_health="healthy"
        )
        
        self.assertEqual(metrics.timestamp, now)
        self.assertEqual(metrics.pending, 10)
        self.assertEqual(metrics.processing, 2)
        self.assertEqual(metrics.completed, 100)
        self.assertEqual(metrics.failed, 5)
        self.assertEqual(metrics.processing_rate, 2.5)
        self.assertEqual(metrics.average_processing_time, 30.0)
        self.assertEqual(metrics.queue_health, "healthy")


if __name__ == '__main__':
    unittest.main()