"""
Integration tests for the Ansera monitoring system.

These tests verify that all components work together correctly
in realistic scenarios.
"""

import unittest
import tempfile
import shutil
import time
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, Mock
import threading

from src.vector_db_query.monitoring.metrics import SystemMonitor
from src.vector_db_query.monitoring.process_manager import QueueMonitor
from src.vector_db_query.monitoring.controls import ProcessController
from src.vector_db_query.monitoring.pm2_control import PM2Controller


class TestMonitoringIntegration(unittest.TestCase):
    """Integration tests for monitoring system components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories
        self.test_dir = tempfile.mkdtemp()
        self.queue_dir = Path(self.test_dir) / "queue"
        self.logs_dir = Path(self.test_dir) / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.system_monitor = SystemMonitor(cache_duration=1)
        self.queue_monitor = QueueMonitor(str(self.queue_dir))
        self.process_controller = ProcessController()
        self.process_controller.base_dir = Path(self.test_dir)
        self.process_controller.logs_dir = self.logs_dir
        
        # Mock PM2 controller
        self.process_controller.pm2 = Mock(spec=PM2Controller)
        self.process_controller.pm2.check_pm2_status.return_value = False
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_system_monitoring_flow(self):
        """Test complete system monitoring flow."""
        # Get system metrics
        metrics = self.system_monitor.get_quick_stats()
        
        # Verify metrics structure
        self.assertIn('cpu', metrics)
        self.assertIn('memory', metrics)
        self.assertIn('disk', metrics)
        self.assertIn('qdrant', metrics)
        
        # Memory should have sub-fields
        self.assertIn('percent', metrics['memory'])
        self.assertIn('used_gb', metrics['memory'])
        self.assertIn('total_gb', metrics['memory'])
    
    def test_queue_processing_workflow(self):
        """Test complete queue processing workflow."""
        # Add multiple documents to queue
        job_ids = []
        for i in range(5):
            job_id = self.queue_monitor.add_to_queue(f"/test/document_{i}.pdf")
            job_ids.append(job_id)
        
        # Verify initial metrics
        metrics = self.queue_monitor.get_queue_metrics()
        self.assertEqual(metrics['pending'], 5)
        self.assertEqual(metrics['processing'], 0)
        self.assertEqual(metrics['completed'], 0)
        
        # Simulate processing first 2 documents
        for job_id in job_ids[:2]:
            self.queue_monitor.start_processing(job_id)
        
        metrics = self.queue_monitor.get_queue_metrics()
        self.assertEqual(metrics['pending'], 3)
        self.assertEqual(metrics['processing'], 2)
        
        # Complete one, fail one
        self.queue_monitor.complete_processing(job_ids[0], success=True)
        self.queue_monitor.complete_processing(job_ids[1], success=False, error_message="Test error")
        
        # Final metrics
        metrics = self.queue_monitor.get_queue_metrics()
        self.assertEqual(metrics['pending'], 3)
        self.assertEqual(metrics['processing'], 0)
        self.assertEqual(metrics['completed'], 1)
        self.assertEqual(metrics['failed'], 1)
        
        # Verify queue health
        self.assertEqual(metrics['queue_health'], 'healthy')
    
    def test_process_control_with_logs(self):
        """Test process control with log management."""
        # Create some log files
        log_files = []
        for i in range(3):
            log_file = self.logs_dir / f"service_{i}.log"
            log_file.write_text(f"Service {i} log entries\n" * 50)
            log_files.append(log_file)
        
        # Export logs
        result = self.process_controller.export_logs()
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('filename', result)
        self.assertTrue(result['filename'].startswith('ansera_logs_'))
        
        # Verify export file exists
        export_path = Path(result['path'])
        self.assertTrue(export_path.exists())
        self.assertGreater(result['size'], 0)
    
    @patch('psutil.process_iter')
    def test_process_monitoring_integration(self, mock_process_iter):
        """Test integration of process monitoring."""
        # Mock some processes
        mock_processes = [
            Mock(
                info={'pid': 1001, 'name': 'python'},
                cmdline=lambda: ['python', '-m', 'vector_db_query.server'],
                cpu_percent=lambda: 15.0,
                memory_percent=lambda: 5.0,
                status=lambda: 'running'
            ),
            Mock(
                info={'pid': 1002, 'name': 'python'},
                cmdline=lambda: ['python', 'ansera_monitor.py'],
                cpu_percent=lambda: 8.0,
                memory_percent=lambda: 3.0,
                status=lambda: 'sleeping'
            )
        ]
        mock_process_iter.return_value = mock_processes
        
        # Get Ansera processes
        processes = self.system_monitor.get_ansera_processes()
        
        # Get service status
        status = self.process_controller.get_service_status()
        
        # Verify integration
        self.assertEqual(len(processes), 2)
        self.assertEqual(status['mcp_server']['status'], 'running')
        self.assertEqual(status['mcp_server']['count'], 2)
    
    def test_queue_monitor_with_worker_simulation(self):
        """Test queue monitor with simulated worker processing."""
        processed_jobs = []
        
        def worker_simulation():
            """Simulate a queue worker."""
            while True:
                # Get pending jobs
                jobs = self.queue_monitor.get_pending_jobs(limit=1)
                if not jobs:
                    break
                
                job = jobs[0]
                # Start processing
                self.queue_monitor.update_job_status(job['job_id'], 'processing')
                
                # Simulate processing time
                time.sleep(0.1)
                
                # Complete processing
                self.queue_monitor.update_job_status(job['job_id'], 'completed')
                processed_jobs.append(job['job_id'])
        
        # Add jobs to queue
        job_ids = []
        for i in range(3):
            job_id = self.queue_monitor.add_to_queue(f"/test/doc_{i}.pdf")
            job_ids.append(job_id)
        
        # Run worker simulation
        worker_thread = threading.Thread(target=worker_simulation)
        worker_thread.start()
        worker_thread.join(timeout=2)
        
        # Verify all jobs processed
        self.assertEqual(len(processed_jobs), 3)
        self.assertEqual(set(processed_jobs), set(job_ids))
        
        # Check final metrics
        metrics = self.queue_monitor.get_queue_metrics()
        self.assertEqual(metrics['pending'], 0)
        self.assertEqual(metrics['completed'], 3)
    
    def test_monitoring_data_persistence(self):
        """Test that monitoring data persists correctly."""
        # Add and process some jobs
        job1 = self.queue_monitor.add_to_queue("/test/persist1.pdf")
        job2 = self.queue_monitor.add_to_queue("/test/persist2.pdf")
        
        self.queue_monitor.start_processing(job1)
        self.queue_monitor.complete_processing(job1, success=True)
        
        # Create new monitor instance with same directory
        new_monitor = QueueMonitor(str(self.queue_dir))
        
        # Verify data persisted
        metrics = new_monitor.get_queue_metrics()
        self.assertEqual(metrics['pending'], 1)  # job2
        self.assertEqual(metrics['completed'], 1)  # job1
        
        # Verify job details persisted
        recent_jobs = new_monitor.get_recent_jobs(status='completed')
        self.assertEqual(len(recent_jobs), 1)
        self.assertEqual(recent_jobs[0]['job_id'], job1)
    
    @patch.object(ProcessController, 'pm2')
    def test_pm2_integration_flow(self, mock_pm2):
        """Test PM2 integration in process control."""
        # Setup PM2 mock
        mock_pm2.check_pm2_status.return_value = True
        mock_pm2.list_processes.return_value = [
            {
                'name': 'ansera-mcp-server',
                'status': 'online',
                'cpu': 12.5,
                'memory': 104857600,
                'uptime': 7200000,
                'restarts': 1
            },
            {
                'name': 'ansera-monitor',
                'status': 'online',
                'cpu': 5.0,
                'memory': 52428800,
                'uptime': 3600000,
                'restarts': 0
            }
        ]
        
        # Reinitialize controller with mocked PM2
        self.process_controller.pm2 = mock_pm2
        
        # Get PM2 status
        pm2_status = self.process_controller.get_pm2_status()
        
        self.assertEqual(pm2_status['status'], 'success')
        self.assertTrue(pm2_status['pm2_available'])
        self.assertEqual(pm2_status['total_count'], 2)
        self.assertEqual(len(pm2_status['processes']), 2)
        
        # Test service restart through PM2
        mock_pm2.restart_service.return_value = {
            'status': 'success',
            'message': 'Service restarted'
        }
        
        result = self.process_controller.restart_mcp_server()
        
        self.assertEqual(result['status'], 'success')
        mock_pm2.restart_service.assert_called_once_with('ansera-mcp-server')
    
    def test_metrics_caching_behavior(self):
        """Test metrics caching across components."""
        # Get initial metrics
        system_metrics1 = self.system_monitor.get_system_metrics()
        queue_metrics1 = self.queue_monitor.get_queue_metrics()
        
        # Immediate second call should use cache
        system_metrics2 = self.system_monitor.get_system_metrics()
        queue_metrics2 = self.queue_monitor.get_queue_metrics()
        
        # Timestamps should be the same (cached)
        self.assertEqual(system_metrics1.timestamp, system_metrics2.timestamp)
        self.assertEqual(queue_metrics1['timestamp'], queue_metrics2['timestamp'])
        
        # Wait for cache expiration
        time.sleep(1.1)
        
        # Next call should fetch fresh data
        system_metrics3 = self.system_monitor.get_system_metrics()
        
        # Timestamp should be different
        self.assertNotEqual(system_metrics1.timestamp, system_metrics3.timestamp)
    
    def test_error_recovery_flow(self):
        """Test system behavior during error conditions."""
        # Test queue recovery after failed jobs
        job_ids = []
        for i in range(3):
            job_id = self.queue_monitor.add_to_queue(f"/test/error_{i}.pdf")
            job_ids.append(job_id)
            self.queue_monitor.start_processing(job_id)
            self.queue_monitor.complete_processing(job_id, success=False, error_message="Simulated error")
        
        # Reset queue (move failed back to pending)
        self.queue_monitor.reset_queue()
        
        # Verify recovery
        metrics = self.queue_monitor.get_queue_metrics()
        self.assertEqual(metrics['pending'], 0)  # Reset doesn't affect failed
        self.assertEqual(metrics['failed'], 3)
        
        # Test log cleanup after errors
        old_log = self.logs_dir / "old_error.log"
        old_log.write_text("Old error logs")
        
        # Set old timestamp
        import os
        old_time = time.time() - (8 * 24 * 60 * 60)  # 8 days old
        os.utime(old_log, (old_time, old_time))
        
        # Cleanup old logs
        result = self.process_controller.cleanup_old_logs(days_to_keep=7)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['files_deleted'], 1)
        self.assertFalse(old_log.exists())


class TestMonitoringEndToEnd(unittest.TestCase):
    """End-to-end tests for monitoring system."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    @patch('requests.get')
    @patch('docker.from_env')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_complete_monitoring_scenario(self, mock_disk, mock_memory, mock_cpu, mock_docker, mock_requests):
        """Test complete monitoring scenario from start to finish."""
        # Setup mocks
        mock_cpu.return_value = 35.0
        mock_memory.return_value = Mock(
            total=17179869184,
            available=10737418240,
            percent=37.5
        )
        mock_disk.return_value = Mock(
            total=500000000000,
            used=150000000000,
            percent=30.0
        )
        
        # Mock Qdrant health
        mock_requests.return_value = Mock(
            status_code=200,
            json=lambda: {'status': 'ok', 'version': '1.5.0'}
        )
        
        # Mock Docker
        mock_docker.return_value = Mock(
            containers=Mock(list=lambda: [])
        )
        
        # Initialize monitoring system
        monitor = SystemMonitor()
        queue = QueueMonitor(str(Path(self.test_dir) / "queue"))
        
        # Simulate document processing workflow
        print("\n=== Starting End-to-End Monitoring Test ===")
        
        # 1. Check system health
        print("1. Checking system health...")
        stats = monitor.get_quick_stats()
        self.assertEqual(stats['cpu'], 35.0)
        self.assertEqual(stats['memory']['percent'], 37.5)
        print(f"   CPU: {stats['cpu']}%, Memory: {stats['memory']['percent']}%")
        
        # 2. Add documents to queue
        print("2. Adding documents to processing queue...")
        docs = [
            "/data/report_2024.pdf",
            "/data/analysis.docx",
            "/data/presentation.pptx"
        ]
        job_ids = []
        for doc in docs:
            job_id = queue.add_to_queue(doc)
            job_ids.append(job_id)
            print(f"   Added: {doc} -> {job_id}")
        
        # 3. Process documents
        print("3. Processing documents...")
        for i, job_id in enumerate(job_ids):
            queue.start_processing(job_id)
            time.sleep(0.1)  # Simulate processing
            success = i != 1  # Fail the second job
            queue.complete_processing(job_id, success=success,
                                    error_message="Parse error" if not success else None)
            print(f"   Processed: {job_id} -> {'Success' if success else 'Failed'}")
        
        # 4. Check final metrics
        print("4. Final metrics:")
        final_metrics = queue.get_queue_metrics()
        print(f"   Completed: {final_metrics['completed']}")
        print(f"   Failed: {final_metrics['failed']}")
        print(f"   Queue Health: {final_metrics['queue_health']}")
        
        # Verify results
        self.assertEqual(final_metrics['completed'], 2)
        self.assertEqual(final_metrics['failed'], 1)
        self.assertEqual(final_metrics['queue_health'], 'healthy')
        
        print("=== End-to-End Test Complete ===\n")


if __name__ == '__main__':
    unittest.main(verbosity=2)