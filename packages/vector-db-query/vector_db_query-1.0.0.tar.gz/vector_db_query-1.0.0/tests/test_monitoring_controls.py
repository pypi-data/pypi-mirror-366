"""
Unit tests for the Ansera monitoring controls module.

Tests the ProcessController class and process control functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import subprocess
import json
import os
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import psutil

from src.vector_db_query.monitoring.controls import ProcessController, get_controller


class TestProcessController(unittest.TestCase):
    """Test cases for ProcessController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = ProcessController()
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.controller.base_dir = Path(self.test_dir)
        self.controller.logs_dir = self.controller.base_dir / "logs"
        self.controller.scripts_dir = self.controller.base_dir / "scripts"
        self.controller.logs_dir.mkdir(parents=True, exist_ok=True)
        self.controller.scripts_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    @patch('psutil.process_iter')
    def test_find_mcp_processes(self, mock_process_iter):
        """Test finding MCP processes."""
        # Create mock processes
        mock_procs = [
            Mock(
                pid=1234,
                cmdline=lambda: ['python', '-m', 'vector_db_query.mcp_integration.server']
            ),
            Mock(
                pid=5678,
                cmdline=lambda: ['node', 'other_app.js']
            ),
            Mock(
                pid=9999,
                cmdline=lambda: ['python', 'mcp_server.py']
            )
        ]
        
        mock_process_iter.return_value = mock_procs
        
        # Find MCP processes
        mcp_processes = self.controller._find_mcp_processes()
        
        self.assertEqual(len(mcp_processes), 2)
        self.assertIn(mock_procs[0], mcp_processes)
        self.assertIn(mock_procs[2], mcp_processes)
    
    @patch.object(ProcessController, '_find_mcp_processes')
    @patch('subprocess.Popen')
    @patch('os.chmod')
    def test_restart_mcp_server_with_script(self, mock_chmod, mock_popen, mock_find):
        """Test restarting MCP server with script."""
        # Mock finding existing processes
        mock_proc = Mock()
        mock_proc.terminate = Mock()
        mock_proc.wait = Mock()
        mock_find.return_value = [mock_proc]
        
        # Create a fake start script
        start_script = self.controller.scripts_dir / "start-mcp.sh"
        start_script.write_text("#!/bin/bash\necho 'Starting MCP'")
        
        # Mock subprocess
        mock_process = Mock(pid=12345)
        mock_popen.return_value = mock_process
        
        # Restart MCP server
        result = self.controller.restart_mcp_server()
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        self.assertIn('12345', result['message'])
        
        # Verify process was terminated
        mock_proc.terminate.assert_called_once()
        
        # Verify script was made executable
        mock_chmod.assert_called_once()
        
        # Verify new process was started
        mock_popen.assert_called_once()
    
    @patch.object(ProcessController, '_find_mcp_processes')
    @patch('subprocess.Popen')
    def test_restart_mcp_server_python_fallback(self, mock_popen, mock_find):
        """Test restarting MCP server with Python module fallback."""
        # No existing processes
        mock_find.return_value = []
        
        # No start script exists
        
        # Create fake MCP module
        mcp_module = self.controller.base_dir / "src" / "vector_db_query" / "mcp_integration"
        mcp_module.mkdir(parents=True, exist_ok=True)
        (mcp_module / "server.py").write_text("# MCP server")
        
        # Mock subprocess
        mock_process = Mock(pid=54321)
        mock_popen.return_value = mock_process
        
        # Restart MCP server
        result = self.controller.restart_mcp_server()
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        self.assertIn('54321', result['message'])
        
        # Verify Python module was started
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        self.assertIn('python', call_args)
        self.assertIn('-m', call_args)
        self.assertIn('vector_db_query.mcp_integration.server', call_args)
    
    @patch.object(ProcessController, 'pm2')
    @patch.object(ProcessController, '_find_mcp_processes')
    def test_restart_mcp_server_with_pm2(self, mock_find, mock_pm2):
        """Test restarting MCP server when managed by PM2."""
        # Mock PM2 availability
        mock_pm2.check_pm2_status.return_value = True
        mock_pm2.list_processes.return_value = [
            {'name': 'ansera-mcp-server', 'status': 'online'}
        ]
        mock_pm2.restart_service.return_value = {
            'status': 'success',
            'message': 'Service restarted via PM2'
        }
        
        # Restart MCP server
        result = self.controller.restart_mcp_server()
        
        # Verify PM2 was used
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'Service restarted via PM2')
        mock_pm2.restart_service.assert_called_once_with('ansera-mcp-server')
        
        # Verify manual restart was not attempted
        mock_find.assert_not_called()
    
    def test_export_logs_success(self):
        """Test successful log export."""
        # Create some log files
        log_file1 = self.controller.logs_dir / "app.log"
        log_file1.write_text("Log entry 1\nLog entry 2")
        
        log_file2 = self.controller.logs_dir / "error.log"
        log_file2.write_text("Error 1\nError 2")
        
        # Create exports directory
        exports_dir = self.controller.base_dir / "exports"
        exports_dir.mkdir(exist_ok=True)
        
        # Export logs
        result = self.controller.export_logs()
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        self.assertIn('filename', result)
        self.assertIn('size', result)
        self.assertTrue(result['filename'].startswith('ansera_logs_'))
        self.assertTrue(result['filename'].endswith('.zip'))
        
        # Verify zip file exists
        export_path = Path(result['path'])
        self.assertTrue(export_path.exists())
    
    @patch('subprocess.run')
    def test_restart_qdrant_with_docker(self, mock_run):
        """Test restarting Qdrant container."""
        # Mock docker commands
        mock_run.side_effect = [
            Mock(returncode=0, stdout=""),  # docker --version
            Mock(returncode=0, stdout="qdrant-container\n"),  # docker ps
            Mock(returncode=0)  # docker restart
        ]
        
        # Restart Qdrant
        result = self.controller.restart_qdrant()
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        self.assertIn('Qdrant restarted successfully', result['message'])
        
        # Verify docker commands
        self.assertEqual(mock_run.call_count, 3)
        docker_restart_call = mock_run.call_args_list[2]
        self.assertEqual(docker_restart_call[0][0], ['docker', 'restart', 'qdrant-container'])
    
    @patch('subprocess.run')
    def test_restart_qdrant_no_docker(self, mock_run):
        """Test Qdrant restart when Docker not available."""
        # Mock docker not found
        mock_run.return_value = Mock(returncode=1)
        
        # Restart Qdrant
        result = self.controller.restart_qdrant()
        
        # Verify result
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'Docker not available')
    
    @patch('subprocess.run')
    @patch.object(ProcessController, '_find_mcp_processes')
    def test_get_service_status(self, mock_find, mock_run):
        """Test getting service status."""
        # Mock MCP processes
        mock_proc = Mock(pid=1234)
        mock_find.return_value = [mock_proc]
        
        # Mock docker command
        mock_run.return_value = Mock(
            returncode=0,
            stdout="qdrant:Up 2 hours\n"
        )
        
        # Get status
        status = self.controller.get_service_status()
        
        # Verify status
        self.assertEqual(status['mcp_server']['status'], 'running')
        self.assertEqual(status['mcp_server']['pid'], 1234)
        self.assertEqual(status['mcp_server']['count'], 1)
        self.assertEqual(status['qdrant']['status'], 'running')
        self.assertEqual(status['qdrant']['container'], 'qdrant')
        self.assertIn('timestamp', status)
    
    def test_cleanup_old_logs(self):
        """Test cleaning up old log files."""
        # Create log files with different ages
        now = datetime.now().timestamp()
        
        # Recent log (should keep)
        recent_log = self.controller.logs_dir / "recent.log"
        recent_log.write_text("Recent log")
        os.utime(recent_log, (now, now))
        
        # Old log (should delete)
        old_log = self.controller.logs_dir / "old.log"
        old_log.write_text("Old log")
        old_time = now - (8 * 24 * 60 * 60)  # 8 days old
        os.utime(old_log, (old_time, old_time))
        
        # Cleanup logs older than 7 days
        result = self.controller.cleanup_old_logs(days_to_keep=7)
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['files_deleted'], 1)
        
        # Verify files
        self.assertTrue(recent_log.exists())
        self.assertFalse(old_log.exists())
    
    @patch.object(ProcessController, 'pm2')
    def test_get_pm2_status(self, mock_pm2):
        """Test getting PM2 status."""
        # Mock PM2 available
        mock_pm2.check_pm2_status.return_value = True
        mock_pm2.list_processes.return_value = [
            {'name': 'ansera-mcp-server', 'status': 'online'},
            {'name': 'ansera-monitor', 'status': 'online'},
            {'name': 'other-service', 'status': 'stopped'}
        ]
        
        # Get PM2 status
        result = self.controller.get_pm2_status()
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['pm2_available'])
        self.assertEqual(result['total_count'], 2)  # Only ansera- services
        self.assertEqual(len(result['processes']), 2)
    
    @patch.object(ProcessController, 'pm2')
    def test_start_all_services(self, mock_pm2):
        """Test starting all services."""
        mock_pm2.check_pm2_status.return_value = True
        mock_pm2.start_all.return_value = {
            'status': 'success',
            'message': 'All services started'
        }
        
        result = self.controller.start_all_services()
        
        self.assertEqual(result['status'], 'success')
        mock_pm2.start_all.assert_called_once()
    
    @patch.object(ProcessController, 'pm2')
    def test_stop_all_services(self, mock_pm2):
        """Test stopping all services."""
        mock_pm2.check_pm2_status.return_value = True
        mock_pm2.stop_all.return_value = {
            'status': 'success',
            'message': 'All services stopped'
        }
        
        result = self.controller.stop_all_services()
        
        self.assertEqual(result['status'], 'success')
        mock_pm2.stop_all.assert_called_once()
    
    @patch.object(ProcessController, 'pm2')
    def test_get_service_logs_with_pm2(self, mock_pm2):
        """Test getting service logs via PM2."""
        mock_pm2.check_pm2_status.return_value = True
        mock_pm2.get_logs.return_value = {
            'status': 'success',
            'logs': 'Service log content...'
        }
        
        result = self.controller.get_service_logs('ansera-mcp-server', lines=100)
        
        self.assertEqual(result['status'], 'success')
        mock_pm2.get_logs.assert_called_once_with('ansera-mcp-server', 100)
    
    def test_get_file_logs_fallback(self):
        """Test getting logs from files when PM2 not available."""
        # Create a log file
        log_file = self.controller.logs_dir / "service.log"
        log_content = "\n".join([f"Log line {i}" for i in range(20)])
        log_file.write_text(log_content)
        
        # Get logs
        result = self.controller._get_file_logs(lines=10)
        
        # Verify result
        self.assertEqual(result['status'], 'success')
        self.assertIn('logs', result)
        
        # Should have last 10 lines
        log_lines = result['logs'].strip().split('\n')
        self.assertEqual(len(log_lines), 10)
        self.assertEqual(log_lines[-1], 'Log line 19')


class TestGetController(unittest.TestCase):
    """Test singleton controller instance."""
    
    def test_singleton_instance(self):
        """Test that get_controller returns singleton."""
        controller1 = get_controller()
        controller2 = get_controller()
        
        self.assertIs(controller1, controller2)


if __name__ == '__main__':
    unittest.main()