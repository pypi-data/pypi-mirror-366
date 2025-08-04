"""
Unit tests for the Ansera monitoring PM2 control module.

Tests the PM2Controller class and PM2 integration functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import subprocess
import json
from pathlib import Path
import tempfile

from src.vector_db_query.monitoring.pm2_control import PM2Controller, get_pm2_controller


class TestPM2Controller(unittest.TestCase):
    """Test cases for PM2Controller class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = PM2Controller()
        # Create temporary ecosystem file
        self.test_dir = tempfile.mkdtemp()
        self.controller.ecosystem_file = Path(self.test_dir) / "ecosystem.config.js"
        self.controller.ecosystem_file.write_text("module.exports = {}")
    
    @patch('subprocess.run')
    def test_run_pm2_command_success(self, mock_run):
        """Test successful PM2 command execution."""
        # Mock successful JSON response
        mock_run.return_value = Mock(
            returncode=0,
            stdout='[{"name": "test-app", "pm_id": 0}]'
        )
        
        result = self.controller._run_pm2_command(['list'])
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('data', result)
        self.assertEqual(result['data'][0]['name'], 'test-app')
        
        # Verify command
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args, ['pm2', 'list', '--json'])
    
    @patch('subprocess.run')
    def test_run_pm2_command_error(self, mock_run):
        """Test PM2 command error handling."""
        mock_run.return_value = Mock(
            returncode=1,
            stderr='PM2 error'
        )
        
        result = self.controller._run_pm2_command(['list'])
        
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['error'], 'PM2 error')
    
    @patch('subprocess.run')
    def test_run_pm2_command_timeout(self, mock_run):
        """Test PM2 command timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired('pm2', 10)
        
        result = self.controller._run_pm2_command(['list'])
        
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['error'], 'PM2 command timed out')
    
    @patch('subprocess.run')
    def test_run_pm2_command_not_found(self, mock_run):
        """Test PM2 not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        result = self.controller._run_pm2_command(['list'])
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('PM2 not found', result['error'])
    
    @patch.object(PM2Controller, '_run_pm2_command')
    def test_list_processes(self, mock_run):
        """Test listing PM2 processes."""
        mock_run.return_value = {
            'status': 'success',
            'data': [
                {
                    'name': 'ansera-mcp-server',
                    'pm_id': 0,
                    'pm2_env': {'status': 'online', 'pm_uptime': 3600000, 'restart_time': 2},
                    'monit': {'cpu': 15.5, 'memory': 104857600},  # 100MB
                    'pid': 12345
                },
                {
                    'name': 'ansera-monitor',
                    'pm_id': 1,
                    'pm2_env': {'status': 'stopped'},
                    'monit': {'cpu': 0, 'memory': 0},
                    'pid': None
                }
            ]
        }
        
        processes = self.controller.list_processes()
        
        self.assertEqual(len(processes), 2)
        
        # Check first process
        self.assertEqual(processes[0]['name'], 'ansera-mcp-server')
        self.assertEqual(processes[0]['pm_id'], 0)
        self.assertEqual(processes[0]['status'], 'online')
        self.assertEqual(processes[0]['cpu'], 15.5)
        self.assertEqual(processes[0]['memory'], 104857600)
        self.assertEqual(processes[0]['uptime'], 3600000)
        self.assertEqual(processes[0]['restarts'], 2)
        self.assertEqual(processes[0]['pid'], 12345)
        
        # Check second process
        self.assertEqual(processes[1]['name'], 'ansera-monitor')
        self.assertEqual(processes[1]['status'], 'stopped')
    
    @patch.object(PM2Controller, '_run_pm2_command')
    def test_start_all(self, mock_run):
        """Test starting all services."""
        mock_run.return_value = {'status': 'success'}
        
        result = self.controller.start_all()
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'All Ansera services started')
        
        mock_run.assert_called_once_with(['start', str(self.controller.ecosystem_file)])
    
    @patch.object(PM2Controller, '_run_pm2_command')
    def test_start_all_no_ecosystem(self, mock_run):
        """Test starting services without ecosystem file."""
        self.controller.ecosystem_file.unlink()
        
        result = self.controller.start_all()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Ecosystem file not found', result['message'])
        mock_run.assert_not_called()
    
    @patch.object(PM2Controller, '_run_pm2_command')
    def test_stop_all(self, mock_run):
        """Test stopping all services."""
        mock_run.return_value = {'status': 'success'}
        
        result = self.controller.stop_all()
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'All services stopped')
        
        mock_run.assert_called_once_with(['stop', 'all'])
    
    @patch.object(PM2Controller, '_run_pm2_command')
    def test_restart_service(self, mock_run):
        """Test restarting specific service."""
        mock_run.return_value = {'status': 'success'}
        
        result = self.controller.restart_service('ansera-mcp-server')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'Service ansera-mcp-server restarted')
        
        mock_run.assert_called_once_with(['restart', 'ansera-mcp-server'])
    
    @patch.object(PM2Controller, '_run_pm2_command')
    def test_stop_service(self, mock_run):
        """Test stopping specific service."""
        mock_run.return_value = {'status': 'success'}
        
        result = self.controller.stop_service('ansera-monitor')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'Service ansera-monitor stopped')
        
        mock_run.assert_called_once_with(['stop', 'ansera-monitor'])
    
    @patch.object(PM2Controller, '_run_pm2_command')
    def test_start_service(self, mock_run):
        """Test starting specific service."""
        mock_run.return_value = {'status': 'success'}
        
        result = self.controller.start_service('ansera-queue-processor')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'Service ansera-queue-processor started')
        
        mock_run.assert_called_once_with(['start', 'ansera-queue-processor'])
    
    @patch('subprocess.run')
    def test_get_logs(self, mock_run):
        """Test getting service logs."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='[2024-01-01] Service started\n[2024-01-01] Processing...'
        )
        
        result = self.controller.get_logs('ansera-mcp-server', lines=50)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('Service started', result['logs'])
        
        # Verify command
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args, ['pm2', 'logs', 'ansera-mcp-server', '--lines', '50', '--nostream'])
    
    @patch('subprocess.run')
    def test_get_logs_all_services(self, mock_run):
        """Test getting logs for all services."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='Combined logs output...'
        )
        
        result = self.controller.get_logs(lines=100)
        
        self.assertEqual(result['status'], 'success')
        
        # Verify command (no service name)
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args, ['pm2', 'logs', '--lines', '100', '--nostream'])
    
    @patch.object(PM2Controller, '_run_pm2_command')
    def test_get_process_info(self, mock_run):
        """Test getting detailed process info."""
        mock_run.return_value = {
            'status': 'success',
            'data': [{
                'name': 'ansera-mcp-server',
                'pm_id': 0,
                'pm2_env': {
                    'status': 'online',
                    'pm_uptime': 3600000,
                    'restart_time': 2,
                    'pm_exec_path': '/path/to/script.js',
                    'args': ['--port', '3000'],
                    'pm_err_log_path': '/logs/error.log',
                    'pm_out_log_path': '/logs/out.log',
                    'created_at': '2024-01-01T00:00:00Z'
                },
                'monit': {'cpu': 15.5, 'memory': 104857600},
                'pid': 12345
            }]
        }
        
        info = self.controller.get_process_info('ansera-mcp-server')
        
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'ansera-mcp-server')
        self.assertEqual(info['pm_id'], 0)
        self.assertEqual(info['status'], 'online')
        self.assertEqual(info['cpu'], 15.5)
        self.assertEqual(info['memory'], 100.0)  # Converted to MB
        self.assertEqual(info['restarts'], 2)
        self.assertEqual(info['script'], '/path/to/script.js')
        self.assertEqual(info['args'], ['--port', '3000'])
        
        mock_run.assert_called_once_with(['describe', 'ansera-mcp-server'])
    
    @patch.object(PM2Controller, '_run_pm2_command')
    def test_flush_logs(self, mock_run):
        """Test flushing PM2 logs."""
        mock_run.return_value = {'status': 'success'}
        
        result = self.controller.flush_logs()
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'Logs flushed successfully')
        
        mock_run.assert_called_once_with(['flush'])
    
    @patch.object(PM2Controller, '_run_pm2_command')
    def test_save_process_list(self, mock_run):
        """Test saving process list."""
        mock_run.return_value = {'status': 'success'}
        
        result = self.controller.save_process_list()
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], 'Process list saved')
        
        mock_run.assert_called_once_with(['save'])
    
    @patch('subprocess.run')
    def test_check_pm2_status_available(self, mock_run):
        """Test checking if PM2 is available."""
        mock_run.return_value = Mock(returncode=0)
        
        available = self.controller.check_pm2_status()
        
        self.assertTrue(available)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args, ['pm2', '--version'])
    
    @patch('subprocess.run')
    def test_check_pm2_status_not_available(self, mock_run):
        """Test PM2 not available."""
        mock_run.return_value = Mock(returncode=1)
        
        available = self.controller.check_pm2_status()
        
        self.assertFalse(available)
    
    @patch('subprocess.run')
    def test_check_pm2_status_exception(self, mock_run):
        """Test PM2 check with exception."""
        mock_run.side_effect = Exception("Not found")
        
        available = self.controller.check_pm2_status()
        
        self.assertFalse(available)


class TestGetPM2Controller(unittest.TestCase):
    """Test singleton PM2 controller instance."""
    
    def test_singleton_instance(self):
        """Test that get_pm2_controller returns singleton."""
        controller1 = get_pm2_controller()
        controller2 = get_pm2_controller()
        
        self.assertIs(controller1, controller2)


if __name__ == '__main__':
    unittest.main()