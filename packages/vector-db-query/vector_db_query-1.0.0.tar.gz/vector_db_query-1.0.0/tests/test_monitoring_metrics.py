"""
Unit tests for the Ansera monitoring metrics module.

Tests the SystemMonitor class and related functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import psutil

from src.vector_db_query.monitoring.metrics import SystemMonitor, SystemMetrics


class TestSystemMonitor(unittest.TestCase):
    """Test cases for SystemMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = SystemMonitor(cache_duration=1)
    
    def test_initialization(self):
        """Test SystemMonitor initialization."""
        self.assertEqual(self.monitor.cache_duration, 1)
        self.assertIsNone(self.monitor._last_metrics)
        self.assertIsNone(self.monitor._last_fetch)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_system_metrics(self, mock_disk, mock_memory, mock_cpu):
        """Test getting system metrics."""
        # Mock system values
        mock_cpu.return_value = 45.5
        mock_memory.return_value = Mock(
            total=17179869184,  # 16GB
            available=8589934592,  # 8GB
            percent=50.0
        )
        mock_disk.return_value = Mock(
            total=500000000000,  # 500GB
            used=250000000000,   # 250GB
            free=250000000000,   # 250GB
            percent=50.0
        )
        
        # Get metrics
        metrics = self.monitor.get_system_metrics()
        
        # Verify metrics
        self.assertIsInstance(metrics, SystemMetrics)
        self.assertEqual(metrics.cpu_percent, 45.5)
        self.assertEqual(metrics.memory_percent, 50.0)
        self.assertEqual(metrics.memory_used_gb, 8.0)
        self.assertEqual(metrics.memory_total_gb, 16.0)
        self.assertEqual(metrics.disk_percent, 50.0)
        self.assertEqual(metrics.disk_used_gb, 250.0)
        self.assertEqual(metrics.disk_total_gb, 500.0)
        
        # Verify system calls
        mock_cpu.assert_called_once_with(interval=1)
        mock_memory.assert_called_once()
        mock_disk.assert_called_once_with('/')
    
    def test_metrics_caching(self):
        """Test that metrics are cached properly."""
        with patch.object(self.monitor, '_fetch_metrics') as mock_fetch:
            mock_metrics = Mock()
            mock_fetch.return_value = mock_metrics
            
            # First call should fetch
            result1 = self.monitor.get_system_metrics()
            self.assertEqual(mock_fetch.call_count, 1)
            self.assertEqual(result1, mock_metrics)
            
            # Second call within cache duration should not fetch
            result2 = self.monitor.get_system_metrics()
            self.assertEqual(mock_fetch.call_count, 1)
            self.assertEqual(result2, mock_metrics)
            
            # Force cache expiration
            self.monitor._last_fetch = datetime.now() - timedelta(seconds=2)
            
            # Third call should fetch again
            result3 = self.monitor.get_system_metrics()
            self.assertEqual(mock_fetch.call_count, 2)
    
    @patch('psutil.process_iter')
    def test_get_ansera_processes(self, mock_process_iter):
        """Test getting Ansera-related processes."""
        # Create mock processes
        mock_procs = [
            Mock(
                info={'pid': 1234, 'name': 'python'},
                cmdline=lambda: ['python', '-m', 'vector_db_query.server'],
                cpu_percent=lambda: 10.5,
                memory_percent=lambda: 5.2,
                status=lambda: 'running'
            ),
            Mock(
                info={'pid': 5678, 'name': 'node'},
                cmdline=lambda: ['node', 'other_app.js'],
                cpu_percent=lambda: 5.0,
                memory_percent=lambda: 2.0,
                status=lambda: 'running'
            ),
            Mock(
                info={'pid': 9999, 'name': 'python'},
                cmdline=lambda: ['python', 'ansera_worker.py'],
                cpu_percent=lambda: 15.0,
                memory_percent=lambda: 8.0,
                status=lambda: 'sleeping'
            )
        ]
        
        mock_process_iter.return_value = mock_procs
        
        # Get Ansera processes
        processes = self.monitor.get_ansera_processes()
        
        # Should find 2 Ansera-related processes
        self.assertEqual(len(processes), 2)
        
        # Check first process
        self.assertEqual(processes[0]['pid'], 1234)
        self.assertEqual(processes[0]['name'], 'python')
        self.assertEqual(processes[0]['cpu_percent'], 10.5)
        self.assertEqual(processes[0]['memory_percent'], 5.2)
        self.assertEqual(processes[0]['status'], 'running')
        
        # Check second process
        self.assertEqual(processes[1]['pid'], 9999)
        self.assertEqual(processes[1]['name'], 'python')
    
    @patch('requests.get')
    def test_check_qdrant_health_success(self, mock_get):
        """Test successful Qdrant health check."""
        # Mock successful response
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                'status': 'ok',
                'version': '1.5.0'
            }
        )
        
        health = self.monitor.check_qdrant_health()
        
        self.assertEqual(health['status'], 'healthy')
        self.assertEqual(health['version'], '1.5.0')
        self.assertTrue(health['available'])
        
        # Verify API call
        mock_get.assert_called_with(
            'http://localhost:6333/health',
            timeout=5
        )
    
    @patch('requests.get')
    def test_check_qdrant_health_failure(self, mock_get):
        """Test failed Qdrant health check."""
        # Mock connection error
        mock_get.side_effect = Exception("Connection refused")
        
        health = self.monitor.check_qdrant_health()
        
        self.assertEqual(health['status'], 'unavailable')
        self.assertFalse(health['available'])
        self.assertIn('Connection refused', health['error'])
    
    @patch('docker.from_env')
    def test_get_docker_stats_success(self, mock_docker):
        """Test getting Docker container stats."""
        # Mock Docker client and container
        mock_container = Mock()
        mock_container.name = 'qdrant'
        mock_container.status = 'running'
        mock_container.stats.return_value = iter([{
            'cpu_stats': {
                'cpu_usage': {'total_usage': 1000000000},
                'system_cpu_usage': 10000000000
            },
            'memory_stats': {
                'usage': 536870912,  # 512MB
                'limit': 2147483648  # 2GB
            }
        }])
        
        mock_client = Mock()
        mock_client.containers.list.return_value = [mock_container]
        mock_docker.return_value = mock_client
        
        # Get stats
        stats = self.monitor.get_docker_stats()
        
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0]['name'], 'qdrant')
        self.assertEqual(stats[0]['status'], 'running')
        self.assertIn('cpu_percent', stats[0])
        self.assertIn('memory_mb', stats[0])
    
    @patch('docker.from_env')
    def test_get_docker_stats_no_docker(self, mock_docker):
        """Test Docker stats when Docker is not available."""
        mock_docker.side_effect = Exception("Docker not found")
        
        stats = self.monitor.get_docker_stats()
        
        self.assertEqual(stats, [])
    
    def test_get_quick_stats(self):
        """Test getting quick stats summary."""
        with patch.object(self.monitor, 'get_system_metrics') as mock_metrics:
            mock_metrics.return_value = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=45.5,
                memory_percent=50.0,
                memory_used_gb=8.0,
                memory_total_gb=16.0,
                disk_percent=25.0,
                disk_used_gb=125.0,
                disk_total_gb=500.0,
                process_count=150,
                qdrant_status='healthy',
                qdrant_collections=5,
                docker_containers=2
            )
            
            with patch.object(self.monitor, 'check_qdrant_health') as mock_qdrant:
                mock_qdrant.return_value = {
                    'status': 'healthy',
                    'available': True,
                    'documents': 10000
                }
                
                stats = self.monitor.get_quick_stats()
                
                self.assertEqual(stats['cpu'], 45.5)
                self.assertEqual(stats['memory']['percent'], 50.0)
                self.assertEqual(stats['memory']['used_gb'], 8.0)
                self.assertEqual(stats['memory']['total_gb'], 16.0)
                self.assertEqual(stats['disk']['percent'], 25.0)
                self.assertEqual(stats['qdrant']['status'], 'healthy')
                self.assertEqual(stats['qdrant']['documents'], 10000)


class TestSystemMetrics(unittest.TestCase):
    """Test cases for SystemMetrics dataclass."""
    
    def test_metrics_creation(self):
        """Test creating SystemMetrics instance."""
        now = datetime.now()
        metrics = SystemMetrics(
            timestamp=now,
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_used_gb=8.0,
            memory_total_gb=16.0,
            disk_percent=40.0,
            disk_used_gb=200.0,
            disk_total_gb=500.0,
            process_count=100,
            qdrant_status='healthy',
            qdrant_collections=3,
            docker_containers=2
        )
        
        self.assertEqual(metrics.timestamp, now)
        self.assertEqual(metrics.cpu_percent, 50.0)
        self.assertEqual(metrics.memory_percent, 60.0)
        self.assertEqual(metrics.qdrant_status, 'healthy')
    
    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_used_gb=8.0,
            memory_total_gb=16.0,
            disk_percent=40.0,
            disk_used_gb=200.0,
            disk_total_gb=500.0,
            process_count=100,
            qdrant_status='healthy',
            qdrant_collections=3,
            docker_containers=2
        )
        
        # Convert to dict using dataclasses.asdict
        from dataclasses import asdict
        metrics_dict = asdict(metrics)
        
        self.assertIsInstance(metrics_dict, dict)
        self.assertEqual(metrics_dict['cpu_percent'], 50.0)
        self.assertEqual(metrics_dict['qdrant_status'], 'healthy')


if __name__ == '__main__':
    unittest.main()