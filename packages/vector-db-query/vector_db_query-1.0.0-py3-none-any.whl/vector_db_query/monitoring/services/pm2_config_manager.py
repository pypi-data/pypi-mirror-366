"""
PM2 configuration management for the monitoring dashboard.

This module provides PM2 ecosystem file management, process configuration,
and PM2 settings management through programmatic interfaces.
"""

import logging
import json
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from threading import RLock
import subprocess
import shutil
import tempfile

from ..history.change_tracker import get_change_tracker, ChangeType, ChangeCategory

logger = logging.getLogger(__name__)


@dataclass
class PM2ProcessConfig:
    """Configuration for a single PM2 process."""
    name: str
    script: str
    cwd: Optional[str] = None
    args: Optional[str] = None
    interpreter: Optional[str] = None
    instances: Union[int, str] = 1
    exec_mode: str = "fork"  # fork or cluster
    env: Optional[Dict[str, str]] = None
    env_production: Optional[Dict[str, str]] = None
    env_development: Optional[Dict[str, str]] = None
    log_file: Optional[str] = None
    out_file: Optional[str] = None
    error_file: Optional[str] = None
    pid_file: Optional[str] = None
    min_uptime: str = "10s"
    max_restarts: int = 10
    autorestart: bool = True
    cron_restart: Optional[str] = None
    watch: Union[bool, List[str]] = False
    ignore_watch: Optional[List[str]] = None
    max_memory_restart: Optional[str] = None
    node_args: Optional[str] = None
    merge_logs: bool = True
    log_type: str = "raw"
    log_date_format: str = "YYYY-MM-DD HH:mm:ss Z"
    
    def __post_init__(self):
        if self.env is None:
            self.env = {}


@dataclass 
class PM2EcosystemConfig:
    """Complete PM2 ecosystem configuration."""
    apps: List[PM2ProcessConfig]
    deploy: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON/YAML export."""
        config = {
            "apps": [asdict(app) for app in self.apps]
        }
        if self.deploy:
            config["deploy"] = self.deploy
        return config


class PM2ConfigValidationError(Exception):
    """Raised when PM2 configuration validation fails."""
    pass


class PM2ConfigManager:
    """
    Manages PM2 configurations and ecosystem files.
    
    Provides configuration editing, validation, backup/restore,
    and deployment management for PM2 processes.
    """
    
    def __init__(self, pm2_home: Optional[str] = None):
        """
        Initialize PM2 config manager.
        
        Args:
            pm2_home: PM2 home directory (default: ~/.pm2)
        """
        self._lock = RLock()
        self.change_tracker = get_change_tracker()
        
        # PM2 paths
        self.pm2_home = Path(pm2_home) if pm2_home else Path.home() / ".pm2"
        self.ecosystem_file = self.pm2_home / "ecosystem.config.js"
        self.config_backup_dir = self.pm2_home / "config_backups"
        
        # Create necessary directories
        self.pm2_home.mkdir(exist_ok=True)
        self.config_backup_dir.mkdir(exist_ok=True)
        
        # Current ecosystem configuration
        self._ecosystem_config: Optional[PM2EcosystemConfig] = None
        
        # Load existing configuration
        self._load_ecosystem_config()
        
        logger.info(f"PM2ConfigManager initialized with PM2_HOME: {self.pm2_home}")
    
    def get_ecosystem_config(self) -> Optional[PM2EcosystemConfig]:
        """
        Get current ecosystem configuration.
        
        Returns:
            Current ecosystem configuration or None if not loaded
        """
        with self._lock:
            return self._ecosystem_config
    
    def set_ecosystem_config(self, config: PM2EcosystemConfig, validate: bool = True) -> bool:
        """
        Set ecosystem configuration.
        
        Args:
            config: New ecosystem configuration
            validate: Whether to validate configuration
            
        Returns:
            True if set successfully
        """
        with self._lock:
            try:
                if validate:
                    self._validate_ecosystem_config(config)
                
                # Backup current configuration
                if self._ecosystem_config:
                    self._backup_current_config("before_update")
                
                old_config = self._ecosystem_config
                self._ecosystem_config = config
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description="PM2 ecosystem configuration updated",
                    details={
                        "apps_count": len(config.apps),
                        "app_names": [app.name for app in config.apps],
                        "has_deploy": config.deploy is not None,
                        "previous_apps": len(old_config.apps) if old_config else 0
                    }
                )
                
                logger.info(f"Ecosystem configuration updated with {len(config.apps)} apps")
                return True
                
            except Exception as e:
                logger.error(f"Failed to set ecosystem configuration: {e}")
                return False
    
    def add_process(self, process_config: PM2ProcessConfig, validate: bool = True) -> bool:
        """
        Add a new process to the ecosystem.
        
        Args:
            process_config: Process configuration to add
            validate: Whether to validate configuration
            
        Returns:
            True if added successfully
        """
        with self._lock:
            try:
                if validate:
                    self._validate_process_config(process_config)
                
                # Check for duplicate names
                if self._ecosystem_config:
                    existing_names = [app.name for app in self._ecosystem_config.apps]
                    if process_config.name in existing_names:
                        raise PM2ConfigValidationError(f"Process name '{process_config.name}' already exists")
                    
                    self._ecosystem_config.apps.append(process_config)
                else:
                    self._ecosystem_config = PM2EcosystemConfig([process_config])
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.CREATE,
                    description=f"PM2 process added: {process_config.name}",
                    details={
                        "process_name": process_config.name,
                        "script": process_config.script,
                        "instances": process_config.instances,
                        "exec_mode": process_config.exec_mode
                    }
                )
                
                logger.info(f"Process added: {process_config.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add process {process_config.name}: {e}")
                return False
    
    def remove_process(self, process_name: str) -> bool:
        """
        Remove a process from the ecosystem.
        
        Args:
            process_name: Name of process to remove
            
        Returns:
            True if removed successfully
        """
        with self._lock:
            try:
                if not self._ecosystem_config:
                    logger.warning("No ecosystem configuration loaded")
                    return False
                
                # Find and remove process
                original_count = len(self._ecosystem_config.apps)
                self._ecosystem_config.apps = [
                    app for app in self._ecosystem_config.apps 
                    if app.name != process_name
                ]
                
                if len(self._ecosystem_config.apps) == original_count:
                    logger.warning(f"Process not found: {process_name}")
                    return False
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.DELETE,
                    description=f"PM2 process removed: {process_name}",
                    details={
                        "process_name": process_name,
                        "remaining_processes": len(self._ecosystem_config.apps)
                    }
                )
                
                logger.info(f"Process removed: {process_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to remove process {process_name}: {e}")
                return False
    
    def update_process(self, process_config: PM2ProcessConfig, validate: bool = True) -> bool:
        """
        Update an existing process configuration.
        
        Args:
            process_config: Updated process configuration
            validate: Whether to validate configuration
            
        Returns:
            True if updated successfully
        """
        with self._lock:
            try:
                if not self._ecosystem_config:
                    logger.warning("No ecosystem configuration loaded")
                    return False
                
                if validate:
                    self._validate_process_config(process_config)
                
                # Find and update process
                updated = False
                for i, app in enumerate(self._ecosystem_config.apps):
                    if app.name == process_config.name:
                        old_config = app
                        self._ecosystem_config.apps[i] = process_config
                        updated = True
                        break
                
                if not updated:
                    logger.warning(f"Process not found for update: {process_config.name}")
                    return False
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description=f"PM2 process updated: {process_config.name}",
                    details={
                        "process_name": process_config.name,
                        "script": process_config.script,
                        "instances": process_config.instances,
                        "exec_mode": process_config.exec_mode
                    }
                )
                
                logger.info(f"Process updated: {process_config.name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to update process {process_config.name}: {e}")
                return False
    
    def get_process(self, process_name: str) -> Optional[PM2ProcessConfig]:
        """
        Get a specific process configuration.
        
        Args:
            process_name: Name of process to get
            
        Returns:
            Process configuration or None if not found
        """
        with self._lock:
            if not self._ecosystem_config:
                return None
            
            for app in self._ecosystem_config.apps:
                if app.name == process_name:
                    return app
            
            return None
    
    def list_processes(self) -> List[str]:
        """
        List all process names in the ecosystem.
        
        Returns:
            List of process names
        """
        with self._lock:
            if not self._ecosystem_config:
                return []
            
            return [app.name for app in self._ecosystem_config.apps]
    
    def save_ecosystem_file(self, format: str = "js", custom_path: Optional[str] = None) -> bool:
        """
        Save ecosystem configuration to file.
        
        Args:
            format: File format ('js', 'json', 'yaml')
            custom_path: Custom file path (default: PM2 home)
            
        Returns:
            True if saved successfully
        """
        with self._lock:
            try:
                if not self._ecosystem_config:
                    logger.warning("No ecosystem configuration to save")
                    return False
                
                # Determine file path
                if custom_path:
                    file_path = Path(custom_path)
                else:
                    if format == "js":
                        file_path = self.ecosystem_file
                    elif format == "json":
                        file_path = self.pm2_home / "ecosystem.config.json"
                    elif format == "yaml":
                        file_path = self.pm2_home / "ecosystem.config.yaml"
                    else:
                        raise ValueError(f"Unsupported format: {format}")
                
                # Backup existing file
                if file_path.exists():
                    backup_path = self.config_backup_dir / f"{file_path.name}.{int(datetime.now().timestamp())}"
                    shutil.copy2(file_path, backup_path)
                
                # Convert configuration
                config_dict = self._ecosystem_config.to_dict()
                
                # Save in requested format
                if format == "js":
                    self._save_js_config(file_path, config_dict)
                elif format == "json":
                    with open(file_path, 'w') as f:
                        json.dump(config_dict, f, indent=2)
                elif format == "yaml":
                    with open(file_path, 'w') as f:
                        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description=f"PM2 ecosystem file saved ({format})",
                    details={
                        "file_path": str(file_path),
                        "format": format,
                        "apps_count": len(self._ecosystem_config.apps)
                    }
                )
                
                logger.info(f"Ecosystem configuration saved to {file_path}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to save ecosystem file: {e}")
                return False
    
    def load_ecosystem_file(self, file_path: Optional[str] = None) -> bool:
        """
        Load ecosystem configuration from file.
        
        Args:
            file_path: Custom file path (default: PM2 home)
            
        Returns:
            True if loaded successfully
        """
        with self._lock:
            try:
                # Determine file path
                if file_path:
                    config_file = Path(file_path)
                else:
                    # Try different config file formats
                    possible_files = [
                        self.pm2_home / "ecosystem.config.js",
                        self.pm2_home / "ecosystem.config.json", 
                        self.pm2_home / "ecosystem.config.yaml",
                        Path.cwd() / "ecosystem.config.js",
                        Path.cwd() / "ecosystem.config.json"
                    ]
                    
                    config_file = None
                    for f in possible_files:
                        if f.exists():
                            config_file = f
                            break
                
                if not config_file or not config_file.exists():
                    logger.info("No ecosystem configuration file found")
                    return False
                
                # Load based on file extension
                if config_file.suffix == ".js":
                    config_dict = self._load_js_config(config_file)
                elif config_file.suffix == ".json":
                    with open(config_file, 'r') as f:
                        config_dict = json.load(f)
                elif config_file.suffix in [".yaml", ".yml"]:
                    with open(config_file, 'r') as f:
                        config_dict = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file format: {config_file.suffix}")
                
                # Parse configuration
                ecosystem_config = self._parse_ecosystem_dict(config_dict)
                self._ecosystem_config = ecosystem_config
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description="PM2 ecosystem configuration loaded",
                    details={
                        "file_path": str(config_file),
                        "apps_count": len(ecosystem_config.apps),
                        "app_names": [app.name for app in ecosystem_config.apps]
                    }
                )
                
                logger.info(f"Ecosystem configuration loaded from {config_file}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to load ecosystem file: {e}")
                return False
    
    def validate_configuration(self) -> tuple[bool, List[str]]:
        """
        Validate current ecosystem configuration.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        with self._lock:
            issues = []
            
            try:
                if not self._ecosystem_config:
                    return False, ["No ecosystem configuration loaded"]
                
                self._validate_ecosystem_config(self._ecosystem_config)
                return True, []
                
            except PM2ConfigValidationError as e:
                issues.append(str(e))
            except Exception as e:
                issues.append(f"Validation error: {e}")
            
            return False, issues
    
    def backup_configuration(self, backup_name: Optional[str] = None) -> str:
        """
        Create a backup of current configuration.
        
        Args:
            backup_name: Custom backup name
            
        Returns:
            Path to backup file
        """
        with self._lock:
            timestamp = int(datetime.now().timestamp())
            backup_name = backup_name or f"ecosystem_backup_{timestamp}"
            backup_path = self.config_backup_dir / f"{backup_name}.json"
            
            if self._ecosystem_config:
                with open(backup_path, 'w') as f:
                    json.dump(self._ecosystem_config.to_dict(), f, indent=2)
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.CREATE,
                    description=f"PM2 configuration backup created: {backup_name}",
                    details={
                        "backup_path": str(backup_path),
                        "apps_count": len(self._ecosystem_config.apps)
                    }
                )
                
                logger.info(f"Configuration backup created: {backup_path}")
            
            return str(backup_path)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all configuration backups.
        
        Returns:
            List of backup information
        """
        backups = []
        
        for backup_file in self.config_backup_dir.glob("*.json"):
            try:
                stat = backup_file.stat()
                backups.append({
                    'name': backup_file.stem,
                    'path': str(backup_file),
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_mtime),
                    'created_timestamp': stat.st_mtime
                })
            except Exception as e:
                logger.warning(f"Failed to get backup info for {backup_file}: {e}")
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created_timestamp'], reverse=True)
        return backups
    
    def restore_backup(self, backup_name: str) -> bool:
        """
        Restore configuration from backup.
        
        Args:
            backup_name: Name of backup to restore
            
        Returns:
            True if restored successfully
        """
        with self._lock:
            try:
                backup_path = self.config_backup_dir / f"{backup_name}.json"
                
                if not backup_path.exists():
                    logger.error(f"Backup not found: {backup_name}")
                    return False
                
                # Backup current configuration first
                current_backup = self.backup_configuration("before_restore")
                
                # Load backup
                with open(backup_path, 'r') as f:
                    config_dict = json.load(f)
                
                # Parse and set configuration
                ecosystem_config = self._parse_ecosystem_dict(config_dict)
                self._ecosystem_config = ecosystem_config
                
                # Track change
                self.change_tracker.track_change(
                    category=ChangeCategory.CONFIGURATION,
                    change_type=ChangeType.UPDATE,
                    description=f"PM2 configuration restored from backup: {backup_name}",
                    details={
                        "backup_name": backup_name,
                        "backup_path": str(backup_path),
                        "current_backup": current_backup,
                        "apps_count": len(ecosystem_config.apps)
                    }
                )
                
                logger.info(f"Configuration restored from backup: {backup_name}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to restore backup {backup_name}: {e}")
                return False
    
    def get_pm2_info(self) -> Dict[str, Any]:
        """
        Get PM2 system information.
        
        Returns:
            PM2 system information
        """
        try:
            # Get PM2 version
            result = subprocess.run(['pm2', '--version'], capture_output=True, text=True, timeout=10)
            pm2_version = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            # Get PM2 home
            pm2_home_env = subprocess.run(['pm2', 'info'], capture_output=True, text=True, timeout=10)
            
            # Get process list
            process_count = 0
            try:
                ps_result = subprocess.run(['pm2', 'jlist'], capture_output=True, text=True, timeout=10)
                if ps_result.returncode == 0:
                    processes = json.loads(ps_result.stdout)
                    process_count = len(processes)
            except:
                pass
            
            return {
                'version': pm2_version,
                'home': str(self.pm2_home),
                'ecosystem_file': str(self.ecosystem_file),
                'process_count': process_count,
                'config_loaded': self._ecosystem_config is not None,
                'backup_count': len(list(self.config_backup_dir.glob("*.json")))
            }
            
        except Exception as e:
            logger.error(f"Failed to get PM2 info: {e}")
            return {
                'version': 'unknown',
                'home': str(self.pm2_home),
                'ecosystem_file': str(self.ecosystem_file),
                'process_count': 0,
                'config_loaded': self._ecosystem_config is not None,
                'backup_count': 0,
                'error': str(e)
            }
    
    def _load_ecosystem_config(self):
        """Load ecosystem configuration from default location."""
        self.load_ecosystem_file()
    
    def _validate_ecosystem_config(self, config: PM2EcosystemConfig):
        """Validate ecosystem configuration."""
        if not config.apps:
            raise PM2ConfigValidationError("Ecosystem must have at least one app")
        
        # Check for duplicate names
        names = [app.name for app in config.apps]
        if len(names) != len(set(names)):
            raise PM2ConfigValidationError("Duplicate app names found")
        
        # Validate each app
        for app in config.apps:
            self._validate_process_config(app)
    
    def _validate_process_config(self, config: PM2ProcessConfig):
        """Validate process configuration."""
        if not config.name:
            raise PM2ConfigValidationError("Process name is required")
        
        if not config.script:
            raise PM2ConfigValidationError("Process script is required")
        
        # Validate exec_mode
        if config.exec_mode not in ["fork", "cluster"]:
            raise PM2ConfigValidationError(f"Invalid exec_mode: {config.exec_mode}")
        
        # Validate instances for cluster mode
        if config.exec_mode == "cluster" and isinstance(config.instances, int) and config.instances < 1:
            raise PM2ConfigValidationError("Cluster mode requires at least 1 instance")
        
        # Validate script path (if not a complex command)
        if config.cwd and not Path(config.cwd).exists():
            logger.warning(f"Working directory does not exist: {config.cwd}")
    
    def _parse_ecosystem_dict(self, config_dict: Dict[str, Any]) -> PM2EcosystemConfig:
        """Parse ecosystem configuration from dictionary."""
        apps = []
        
        for app_dict in config_dict.get("apps", []):
            # Convert dictionary to PM2ProcessConfig
            process_config = PM2ProcessConfig(
                name=app_dict["name"],
                script=app_dict["script"],
                cwd=app_dict.get("cwd"),
                args=app_dict.get("args"),
                interpreter=app_dict.get("interpreter"),
                instances=app_dict.get("instances", 1),
                exec_mode=app_dict.get("exec_mode", "fork"),
                env=app_dict.get("env", {}),
                env_production=app_dict.get("env_production"),
                env_development=app_dict.get("env_development"),
                log_file=app_dict.get("log_file"),
                out_file=app_dict.get("out_file"),
                error_file=app_dict.get("error_file"),
                pid_file=app_dict.get("pid_file"),
                min_uptime=app_dict.get("min_uptime", "10s"),
                max_restarts=app_dict.get("max_restarts", 10),
                autorestart=app_dict.get("autorestart", True),
                cron_restart=app_dict.get("cron_restart"),
                watch=app_dict.get("watch", False),
                ignore_watch=app_dict.get("ignore_watch"),
                max_memory_restart=app_dict.get("max_memory_restart"),
                node_args=app_dict.get("node_args"),
                merge_logs=app_dict.get("merge_logs", True),
                log_type=app_dict.get("log_type", "raw"),
                log_date_format=app_dict.get("log_date_format", "YYYY-MM-DD HH:mm:ss Z")
            )
            apps.append(process_config)
        
        return PM2EcosystemConfig(
            apps=apps,
            deploy=config_dict.get("deploy")
        )
    
    def _save_js_config(self, file_path: Path, config_dict: Dict[str, Any]):
        """Save configuration as JavaScript file."""
        js_content = f"module.exports = {json.dumps(config_dict, indent=2)};"
        
        with open(file_path, 'w') as f:
            f.write(js_content)
    
    def _load_js_config(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from JavaScript file."""
        # This is a simplified loader - in production you'd want a proper JS parser
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract JSON from module.exports
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start == -1 or end == 0:
            raise ValueError("Invalid JavaScript config file format")
        
        json_content = content[start:end]
        return json.loads(json_content)
    
    def _backup_current_config(self, reason: str):
        """Create backup of current configuration."""
        if self._ecosystem_config:
            backup_name = f"{reason}_{int(datetime.now().timestamp())}"
            self.backup_configuration(backup_name)


# Singleton instance
_pm2_config_manager: Optional[PM2ConfigManager] = None
_manager_lock = RLock()


def get_pm2_config_manager(pm2_home: Optional[str] = None) -> PM2ConfigManager:
    """
    Get singleton PM2 config manager instance.
    
    Args:
        pm2_home: PM2 home directory (only used on first call)
        
    Returns:
        PM2ConfigManager instance
    """
    global _pm2_config_manager
    
    with _manager_lock:
        if _pm2_config_manager is None:
            _pm2_config_manager = PM2ConfigManager(pm2_home)
        
        return _pm2_config_manager


def reset_pm2_config_manager():
    """Reset the singleton PM2 config manager (mainly for testing)."""
    global _pm2_config_manager
    
    with _manager_lock:
        _pm2_config_manager = None