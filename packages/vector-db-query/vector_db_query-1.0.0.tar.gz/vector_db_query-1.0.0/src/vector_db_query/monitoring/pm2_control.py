"""
PM2 Control Interface for Ansera Monitoring

This module provides Python interface to control PM2-managed processes
from the monitoring dashboard.
"""

import subprocess
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PM2Controller:
    """
    Interface to control PM2-managed Ansera processes.
    
    Provides methods to start, stop, restart, and monitor
    processes managed by PM2.
    """
    
    def __init__(self):
        """Initialize PM2 controller."""
        self.ecosystem_file = Path(__file__).parent.parent.parent.parent.parent / "ecosystem.config.js"
        
    def _run_pm2_command(self, args: List[str], use_json: bool = True) -> Dict[str, Any]:
        """
        Run a PM2 command and return the result.
        
        Args:
            args: PM2 command arguments
            use_json: Whether to add --json flag (default True)
            
        Returns:
            Dict with status and output/error
        """
        try:
            # Build command
            cmd = ["pm2"] + args
            
            # Only add --json for commands that support it
            if use_json and len(args) > 0:
                command = args[0]
                # Commands that support --json
                json_commands = ["list", "jlist", "describe", "show", "info"]
                if command in json_commands:
                    cmd.append("--json")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Try to parse as JSON if we used --json flag
                if "--json" in cmd:
                    try:
                        output = json.loads(result.stdout)
                        return {
                            "status": "success",
                            "data": output
                        }
                    except json.JSONDecodeError:
                        # Fallback for non-JSON output
                        return {
                            "status": "success",
                            "output": result.stdout
                        }
                else:
                    # Return raw output for non-JSON commands
                    return {
                        "status": "success",
                        "output": result.stdout
                    }
            else:
                return {
                    "status": "error",
                    "error": result.stderr or "PM2 command failed"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "PM2 command timed out"
            }
        except FileNotFoundError:
            return {
                "status": "error",
                "error": "PM2 not found. Please install PM2 globally: npm install -g pm2"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def list_processes(self) -> List[Dict[str, Any]]:
        """
        List all PM2 processes with their status.
        
        Returns:
            List of process information
        """
        result = self._run_pm2_command(["list"])
        
        if result["status"] == "success" and "data" in result:
            processes = []
            for proc in result["data"]:
                # Extract relevant fields
                processes.append({
                    "name": proc.get("name", "unknown"),
                    "pm_id": proc.get("pm_id", -1),
                    "status": proc.get("pm2_env", {}).get("status", "unknown"),
                    "cpu": proc.get("monit", {}).get("cpu", 0),
                    "memory": proc.get("monit", {}).get("memory", 0),
                    "uptime": proc.get("pm2_env", {}).get("pm_uptime", 0),
                    "restarts": proc.get("pm2_env", {}).get("restart_time", 0),
                    "pid": proc.get("pid", None)
                })
            return processes
        
        return []
    
    def start_all(self) -> Dict[str, Any]:
        """Start all Ansera services using ecosystem file."""
        if not self.ecosystem_file.exists():
            return {
                "status": "error",
                "message": f"Ecosystem file not found: {self.ecosystem_file}"
            }
        
        # Don't use JSON for start command with ecosystem file
        result = self._run_pm2_command(["start", str(self.ecosystem_file)], use_json=False)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "All Ansera services started"
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", "Failed to start services")
            }
    
    def stop_all(self) -> Dict[str, Any]:
        """Stop all Ansera services."""
        # Don't use JSON for stop command
        result = self._run_pm2_command(["stop", "all"], use_json=False)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "All services stopped"
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", "Failed to stop services")
            }
    
    def restart_service(self, service_name: str) -> Dict[str, Any]:
        """
        Restart a specific service.
        
        Args:
            service_name: Name of the service (e.g., 'ansera-mcp-server')
            
        Returns:
            Operation result
        """
        # Don't use JSON for restart command
        result = self._run_pm2_command(["restart", service_name], use_json=False)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Service {service_name} restarted"
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", f"Failed to restart {service_name}")
            }
    
    def stop_service(self, service_name: str) -> Dict[str, Any]:
        """Stop a specific service."""
        # Don't use JSON for stop command
        result = self._run_pm2_command(["stop", service_name], use_json=False)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Service {service_name} stopped"
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", f"Failed to stop {service_name}")
            }
    
    def start_service(self, service_name: str) -> Dict[str, Any]:
        """Start a specific service."""
        # Don't use JSON for start command
        result = self._run_pm2_command(["start", service_name], use_json=False)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Service {service_name} started"
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", f"Failed to start {service_name}")
            }
    
    def get_logs(self, service_name: Optional[str] = None, lines: int = 50) -> Dict[str, Any]:
        """
        Get logs for a service.
        
        Args:
            service_name: Service name (None for all services)
            lines: Number of lines to retrieve
            
        Returns:
            Log content
        """
        cmd_args = ["logs"]
        if service_name:
            cmd_args.append(service_name)
        cmd_args.extend(["--lines", str(lines), "--nostream"])
        
        # Run without --json flag for logs
        try:
            cmd = ["pm2"] + cmd_args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "logs": result.stdout
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to retrieve logs"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_process_info(self, service_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific process.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Detailed process information
        """
        # Use describe command for detailed info
        result = self._run_pm2_command(["describe", service_name])
        
        if result["status"] == "success" and "data" in result:
            # PM2 describe returns an array with one element
            if isinstance(result["data"], list) and len(result["data"]) > 0:
                proc = result["data"][0]
                env = proc.get("pm2_env", {})
                
                return {
                    "name": proc.get("name"),
                    "pm_id": proc.get("pm_id"),
                    "status": env.get("status"),
                    "cpu": proc.get("monit", {}).get("cpu", 0),
                    "memory": proc.get("monit", {}).get("memory", 0) / (1024 * 1024),  # Convert to MB
                    "uptime": env.get("pm_uptime"),
                    "restarts": env.get("restart_time", 0),
                    "pid": proc.get("pid"),
                    "script": env.get("pm_exec_path"),
                    "args": env.get("args"),
                    "error_file": env.get("pm_err_log_path"),
                    "out_file": env.get("pm_out_log_path"),
                    "created_at": env.get("created_at")
                }
        
        return None
    
    def flush_logs(self) -> Dict[str, Any]:
        """Flush all PM2 logs."""
        # Don't use JSON for flush command
        result = self._run_pm2_command(["flush"], use_json=False)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Logs flushed successfully"
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", "Failed to flush logs")
            }
    
    def save_process_list(self) -> Dict[str, Any]:
        """Save current process list for resurrection."""
        # Don't use JSON for save command
        result = self._run_pm2_command(["save"], use_json=False)
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Process list saved"
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", "Failed to save process list")
            }
    
    def check_pm2_status(self) -> bool:
        """
        Check if PM2 is installed and accessible.
        
        Returns:
            True if PM2 is available
        """
        try:
            result = subprocess.run(
                ["pm2", "--version"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False


# Singleton instance
_pm2_controller = None

def get_pm2_controller() -> PM2Controller:
    """Get singleton PM2Controller instance."""
    global _pm2_controller
    if _pm2_controller is None:
        _pm2_controller = PM2Controller()
    return _pm2_controller


# Test functionality
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Get controller
    controller = get_pm2_controller()
    
    # Check PM2 status
    if not controller.check_pm2_status():
        print("PM2 is not installed. Please install with: npm install -g pm2")
        exit(1)
    
    print("PM2 is available")
    
    # List processes
    print("\nAnsera Processes:")
    print("-" * 60)
    processes = controller.list_processes()
    
    for proc in processes:
        if proc["name"].startswith("ansera-"):
            print(f"{proc['name']}: {proc['status']} (PID: {proc['pid']}, CPU: {proc['cpu']}%, Memory: {proc['memory']/1024/1024:.1f}MB)")
    
    if not any(p["name"].startswith("ansera-") for p in processes):
        print("No Ansera processes found. Start with: pm2 start ecosystem.config.js")