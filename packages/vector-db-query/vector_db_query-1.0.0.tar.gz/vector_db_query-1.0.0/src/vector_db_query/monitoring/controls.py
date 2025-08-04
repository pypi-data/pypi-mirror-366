"""
Process control functionality for Ansera monitoring dashboard.

This module provides the actual implementation for process control
operations like restarting services, clearing queues, and exporting logs.
"""

import os
import subprocess
import signal
import logging
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import psutil

from .pm2_control import get_pm2_controller

logger = logging.getLogger(__name__)


class ProcessController:
    """
    Handle process control operations for Ansera services.
    
    Provides methods to start, stop, restart services and
    manage system operations.
    """
    
    def __init__(self):
        """Initialize the process controller."""
        self.base_dir = Path(__file__).parent.parent.parent.parent.parent
        self.logs_dir = self.base_dir / "logs"
        self.scripts_dir = self.base_dir / "scripts"
        self.pm2 = get_pm2_controller()
        
    def restart_mcp_server(self) -> Dict[str, Any]:
        """
        Restart the MCP server process.
        
        Returns:
            Dict with status and message
        """
        try:
            logger.info("Attempting to restart MCP server...")
            
            # First check if PM2 is managing the process
            if self.pm2.check_pm2_status():
                pm2_processes = self.pm2.list_processes()
                mcp_in_pm2 = any(p['name'] == 'ansera-mcp-server' for p in pm2_processes)
                
                if mcp_in_pm2:
                    # Use PM2 to restart
                    result = self.pm2.restart_service('ansera-mcp-server')
                    return result
            
            # Fallback to manual process management
            # First, find and stop any running MCP server processes
            mcp_processes = self._find_mcp_processes()
            
            if mcp_processes:
                logger.info(f"Found {len(mcp_processes)} MCP processes to stop")
                for proc in mcp_processes:
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    except Exception as e:
                        logger.warning(f"Error stopping process {proc.pid}: {e}")
            
            # Start the MCP server
            # Check for different possible start scripts
            start_scripts = [
                self.base_dir / "run_mcp_server.sh",
                self.base_dir / "start_mcp.sh",
                self.scripts_dir / "start-mcp.sh"
            ]
            
            start_script = None
            for script in start_scripts:
                if script.exists() and script.is_file():
                    start_script = script
                    break
            
            if start_script:
                # Make script executable
                os.chmod(start_script, 0o755)
                
                # Start the server in background
                process = subprocess.Popen(
                    [str(start_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                    cwd=str(self.base_dir)
                )
                
                logger.info(f"Started MCP server with PID: {process.pid}")
                
                return {
                    "status": "success",
                    "message": f"MCP server restarted successfully (PID: {process.pid})",
                    "pid": process.pid
                }
            else:
                # Try direct Python execution
                mcp_module = self.base_dir / "src" / "vector_db_query" / "mcp_integration" / "server.py"
                
                if mcp_module.exists():
                    process = subprocess.Popen(
                        ["python", "-m", "vector_db_query.mcp_integration.server"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        start_new_session=True,
                        cwd=str(self.base_dir)
                    )
                    
                    logger.info(f"Started MCP server with PID: {process.pid}")
                    
                    return {
                        "status": "success",
                        "message": f"MCP server restarted successfully (PID: {process.pid})",
                        "pid": process.pid
                    }
                else:
                    return {
                        "status": "error",
                        "message": "MCP server start script not found"
                    }
                    
        except Exception as e:
            logger.error(f"Error restarting MCP server: {e}")
            return {
                "status": "error",
                "message": f"Failed to restart MCP server: {str(e)}"
            }
    
    def _find_mcp_processes(self) -> List[psutil.Process]:
        """Find running MCP server processes."""
        mcp_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.cmdline())
                    if 'mcp' in cmdline.lower() and ('server' in cmdline or 'vector_db_query' in cmdline):
                        mcp_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error finding MCP processes: {e}")
        
        return mcp_processes
    
    def export_logs(self, include_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export logs as a ZIP file.
        
        Args:
            include_types: List of log types to include (e.g., ['mcp', 'system', 'queue'])
                         If None, includes all logs
        
        Returns:
            Dict with status and file path if successful
        """
        try:
            if include_types is None:
                include_types = ['all']
            
            # Create exports directory
            exports_dir = self.base_dir / "exports"
            exports_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_filename = f"ansera_logs_{timestamp}.zip"
            export_path = exports_dir / export_filename
            
            # Create ZIP file
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add log files
                if self.logs_dir.exists():
                    for log_file in self.logs_dir.rglob('*.log'):
                        # Check if we should include this log type
                        if 'all' in include_types or any(t in log_file.name.lower() for t in include_types):
                            arcname = f"logs/{log_file.relative_to(self.logs_dir)}"
                            zipf.write(log_file, arcname)
                
                # Add queue state files
                queue_dir = Path.home() / ".vector_db_query" / "queue"
                if queue_dir.exists() and ('all' in include_types or 'queue' in include_types):
                    for queue_file in queue_dir.glob('*.json'):
                        arcname = f"queue/{queue_file.name}"
                        zipf.write(queue_file, arcname)
                
                # Add system info
                if 'all' in include_types or 'system' in include_types:
                    system_info = {
                        "timestamp": datetime.now().isoformat(),
                        "cpu_count": psutil.cpu_count(),
                        "memory_total": psutil.virtual_memory().total,
                        "disk_usage": psutil.disk_usage('/').percent,
                        "python_version": subprocess.check_output(['python', '--version'], 
                                                               text=True).strip()
                    }
                    
                    info_path = exports_dir / "system_info.json"
                    with open(info_path, 'w') as f:
                        json.dump(system_info, f, indent=2)
                    zipf.write(info_path, "system_info.json")
                    info_path.unlink()  # Clean up temp file
            
            logger.info(f"Logs exported successfully to {export_path}")
            
            return {
                "status": "success",
                "message": f"Logs exported successfully",
                "filename": export_filename,
                "path": str(export_path),
                "size": export_path.stat().st_size
            }
            
        except Exception as e:
            logger.error(f"Error exporting logs: {e}")
            return {
                "status": "error",
                "message": f"Failed to export logs: {str(e)}"
            }
    
    def restart_qdrant(self) -> Dict[str, Any]:
        """
        Restart Qdrant vector database container.
        
        Returns:
            Dict with status and message
        """
        try:
            # Check if Docker is available
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": "Docker not available"
                }
            
            # Find Qdrant container
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', 'name=qdrant', '--format', '{{.Names}}'],
                capture_output=True, text=True
            )
            
            containers = result.stdout.strip().split('\n')
            containers = [c for c in containers if c]
            
            if not containers:
                # Try to start Qdrant using docker-compose
                compose_file = self.base_dir / "docker-compose.yml"
                if compose_file.exists():
                    subprocess.run(
                        ['docker-compose', 'up', '-d', 'qdrant'],
                        cwd=str(self.base_dir)
                    )
                    return {
                        "status": "success",
                        "message": "Qdrant started successfully"
                    }
                else:
                    return {
                        "status": "error",
                        "message": "No Qdrant container found"
                    }
            
            # Restart the container
            for container in containers:
                subprocess.run(['docker', 'restart', container])
                logger.info(f"Restarted Qdrant container: {container}")
            
            return {
                "status": "success",
                "message": f"Qdrant restarted successfully ({len(containers)} container(s))"
            }
            
        except Exception as e:
            logger.error(f"Error restarting Qdrant: {e}")
            return {
                "status": "error",
                "message": f"Failed to restart Qdrant: {str(e)}"
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get status of all Ansera services.
        
        Returns:
            Dict with service statuses
        """
        status = {
            "mcp_server": {"status": "unknown", "pid": None},
            "qdrant": {"status": "unknown", "container": None},
            "timestamp": datetime.now().isoformat()
        }
        
        # Check MCP server
        mcp_processes = self._find_mcp_processes()
        if mcp_processes:
            status["mcp_server"]["status"] = "running"
            status["mcp_server"]["pid"] = mcp_processes[0].pid
            status["mcp_server"]["count"] = len(mcp_processes)
        else:
            status["mcp_server"]["status"] = "stopped"
        
        # Check Qdrant
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=qdrant', '--format', '{{.Names}}:{{.Status}}'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                containers = result.stdout.strip().split('\n')
                for container in containers:
                    if container:
                        name, container_status = container.split(':', 1)
                        if 'Up' in container_status:
                            status["qdrant"]["status"] = "running"
                            status["qdrant"]["container"] = name
                            break
            else:
                status["qdrant"]["status"] = "stopped"
                
        except Exception as e:
            logger.warning(f"Error checking Qdrant status: {e}")
            status["qdrant"]["error"] = str(e)
        
        return status
    
    def get_pm2_status(self) -> Dict[str, Any]:
        """
        Get status of all PM2-managed Ansera services.
        
        Returns:
            Dict with PM2 process information
        """
        if not self.pm2.check_pm2_status():
            return {
                "status": "error",
                "message": "PM2 not available",
                "processes": []
            }
        
        processes = self.pm2.list_processes()
        ansera_processes = [p for p in processes if p['name'].startswith('ansera-')]
        
        return {
            "status": "success",
            "pm2_available": True,
            "processes": ansera_processes,
            "total_count": len(ansera_processes)
        }
    
    def start_all_services(self) -> Dict[str, Any]:
        """Start all Ansera services using PM2."""
        if not self.pm2.check_pm2_status():
            return {
                "status": "error",
                "message": "PM2 not available. Install with: npm install -g pm2"
            }
        
        return self.pm2.start_all()
    
    def stop_all_services(self) -> Dict[str, Any]:
        """Stop all Ansera services using PM2."""
        if not self.pm2.check_pm2_status():
            return {
                "status": "error",
                "message": "PM2 not available"
            }
        
        return self.pm2.stop_all()
    
    def get_service_logs(self, service_name: str = None, lines: int = 50) -> Dict[str, Any]:
        """
        Get logs for a specific service or all services.
        
        Args:
            service_name: Service name (None for all)
            lines: Number of log lines to retrieve
            
        Returns:
            Dict with log content
        """
        if not self.pm2.check_pm2_status():
            # Fallback to file-based logs
            return self._get_file_logs(service_name, lines)
        
        return self.pm2.get_logs(service_name, lines)
    
    def _get_file_logs(self, service_name: str = None, lines: int = 50) -> Dict[str, Any]:
        """Get logs from file system when PM2 is not available."""
        try:
            log_files = []
            
            if self.logs_dir.exists():
                if service_name:
                    # Look for service-specific logs
                    pattern = f"*{service_name}*.log"
                    log_files = list(self.logs_dir.glob(pattern))
                else:
                    # Get all log files
                    log_files = list(self.logs_dir.glob("*.log"))
            
            if not log_files:
                return {
                    "status": "error",
                    "message": "No log files found"
                }
            
            # Read last N lines from most recent log file
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            most_recent = log_files[0]
            
            with open(most_recent, 'r') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
            return {
                "status": "success",
                "logs": ''.join(last_lines),
                "file": str(most_recent)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read logs: {str(e)}"
            }
    
    def cleanup_old_logs(self, days_to_keep: int = 7) -> Dict[str, Any]:
        """
        Clean up log files older than specified days.
        
        Args:
            days_to_keep: Number of days to keep logs
            
        Returns:
            Dict with cleanup results
        """
        try:
            if not self.logs_dir.exists():
                return {
                    "status": "success",
                    "message": "No logs directory found",
                    "files_deleted": 0
                }
            
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            files_deleted = 0
            space_freed = 0
            
            for log_file in self.logs_dir.rglob('*.log'):
                try:
                    if log_file.stat().st_mtime < cutoff_time:
                        space_freed += log_file.stat().st_size
                        log_file.unlink()
                        files_deleted += 1
                except Exception as e:
                    logger.warning(f"Error deleting {log_file}: {e}")
            
            return {
                "status": "success",
                "message": f"Cleaned up {files_deleted} log files",
                "files_deleted": files_deleted,
                "space_freed_mb": round(space_freed / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up logs: {e}")
            return {
                "status": "error",
                "message": f"Failed to clean up logs: {str(e)}"
            }


# Singleton instance
_controller = None

def get_controller() -> ProcessController:
    """Get singleton ProcessController instance."""
    global _controller
    if _controller is None:
        _controller = ProcessController()
    return _controller


# Example usage for testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Get controller
    controller = get_controller()
    
    # Test service status
    print("Service Status:")
    print("-" * 50)
    status = controller.get_service_status()
    print(f"MCP Server: {status['mcp_server']['status']}")
    print(f"Qdrant: {status['qdrant']['status']}")
    
    # Test log export
    print("\nExporting logs...")
    result = controller.export_logs()
    if result['status'] == 'success':
        print(f"Logs exported to: {result['filename']}")
        print(f"Size: {result['size'] / 1024:.2f} KB")