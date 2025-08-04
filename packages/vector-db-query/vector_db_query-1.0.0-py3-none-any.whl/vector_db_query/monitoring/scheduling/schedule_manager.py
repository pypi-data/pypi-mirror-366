"""
Schedule configuration management and persistence.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from threading import RLock

from .models import Schedule

logger = logging.getLogger(__name__)


class ScheduleManager:
    """
    Manages schedule configurations with persistence to disk.
    
    Handles CRUD operations for schedules and maintains consistency.
    """
    
    def __init__(self, storage_path: Path):
        """
        Initialize schedule manager.
        
        Args:
            storage_path: Path to store schedule files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.schedules_file = self.storage_path / "schedules.json"
        self.backup_file = self.storage_path / "schedules.backup.json"
        
        self._schedules: Dict[str, Schedule] = {}
        self._lock = RLock()
        
        logger.info(f"ScheduleManager initialized with storage: {self.storage_path}")
    
    def load_schedules(self) -> List[Schedule]:
        """
        Load schedules from disk.
        
        Returns:
            List of loaded schedules
        """
        with self._lock:
            if self.schedules_file.exists():
                try:
                    with self.schedules_file.open('r') as f:
                        data = json.load(f)
                    
                    schedules_data = data.get('schedules', [])
                    loaded_schedules = []
                    
                    for schedule_data in schedules_data:
                        try:
                            schedule = Schedule.from_dict(schedule_data)
                            self._schedules[schedule.id] = schedule
                            loaded_schedules.append(schedule)
                        except Exception as e:
                            logger.error(f"Failed to load schedule: {str(e)}")
                    
                    logger.info(f"Loaded {len(loaded_schedules)} schedules from disk")
                    return loaded_schedules
                
                except Exception as e:
                    logger.error(f"Failed to load schedules file: {str(e)}")
                    
                    # Try backup file
                    if self.backup_file.exists():
                        logger.info("Attempting to load from backup file")
                        try:
                            with self.backup_file.open('r') as f:
                                data = json.load(f)
                            
                            schedules_data = data.get('schedules', [])
                            for schedule_data in schedules_data:
                                schedule = Schedule.from_dict(schedule_data)
                                self._schedules[schedule.id] = schedule
                            
                            logger.info(f"Loaded {len(self._schedules)} schedules from backup")
                            
                        except Exception as backup_error:
                            logger.error(f"Failed to load backup file: {str(backup_error)}")
            
            return list(self._schedules.values())
    
    def save_schedules(self) -> bool:
        """
        Save schedules to disk.
        
        Returns:
            True if saved successfully
        """
        with self._lock:
            try:
                # Create backup of existing file
                if self.schedules_file.exists():
                    self.schedules_file.replace(self.backup_file)
                
                # Prepare data
                schedules_data = [
                    schedule.to_dict() 
                    for schedule in self._schedules.values()
                ]
                
                data = {
                    'schedules': schedules_data,
                    'metadata': {
                        'version': '1.0',
                        'saved_at': datetime.now().isoformat(),
                        'total_schedules': len(schedules_data)
                    }
                }
                
                # Write to file
                with self.schedules_file.open('w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                logger.info(f"Saved {len(schedules_data)} schedules to disk")
                return True
            
            except Exception as e:
                logger.error(f"Failed to save schedules: {str(e)}")
                return False
    
    def add_schedule(self, schedule: Schedule) -> None:
        """
        Add a new schedule.
        
        Args:
            schedule: Schedule to add
        """
        with self._lock:
            schedule.created_at = datetime.now()
            schedule.updated_at = datetime.now()
            self._schedules[schedule.id] = schedule
            
            # Auto-save
            self.save_schedules()
            
            logger.info(f"Added schedule: {schedule.name} ({schedule.id})")
    
    def update_schedule(self, schedule: Schedule) -> None:
        """
        Update an existing schedule.
        
        Args:
            schedule: Schedule to update
        """
        with self._lock:
            if schedule.id not in self._schedules:
                raise ValueError(f"Schedule not found: {schedule.id}")
            
            schedule.updated_at = datetime.now()
            self._schedules[schedule.id] = schedule
            
            # Auto-save
            self.save_schedules()
            
            logger.info(f"Updated schedule: {schedule.name} ({schedule.id})")
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a schedule.
        
        Args:
            schedule_id: ID of schedule to remove
            
        Returns:
            True if removed successfully
        """
        with self._lock:
            if schedule_id not in self._schedules:
                return False
            
            schedule = self._schedules[schedule_id]
            del self._schedules[schedule_id]
            
            # Auto-save
            self.save_schedules()
            
            logger.info(f"Removed schedule: {schedule.name} ({schedule_id})")
            return True
    
    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """
        Get a schedule by ID.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Schedule or None if not found
        """
        with self._lock:
            return self._schedules.get(schedule_id)
    
    def get_all_schedules(self) -> List[Schedule]:
        """
        Get all schedules.
        
        Returns:
            List of all schedules
        """
        with self._lock:
            return list(self._schedules.values())
    
    def get_schedules_by_type(self, schedule_type) -> List[Schedule]:
        """
        Get schedules by type.
        
        Args:
            schedule_type: Schedule type to filter by
            
        Returns:
            List of matching schedules
        """
        with self._lock:
            return [
                schedule for schedule in self._schedules.values()
                if schedule.schedule_type == schedule_type
            ]
    
    def get_schedules_by_status(self, status) -> List[Schedule]:
        """
        Get schedules by status.
        
        Args:
            status: Schedule status to filter by
            
        Returns:
            List of matching schedules
        """
        with self._lock:
            return [
                schedule for schedule in self._schedules.values()
                if schedule.status == status
            ]
    
    def get_schedules_by_task(self, task_name: str) -> List[Schedule]:
        """
        Get schedules by task name.
        
        Args:
            task_name: Task name to filter by
            
        Returns:
            List of matching schedules
        """
        with self._lock:
            return [
                schedule for schedule in self._schedules.values()
                if schedule.task_name == task_name
            ]
    
    def find_schedules(self, **criteria) -> List[Schedule]:
        """
        Find schedules matching criteria.
        
        Args:
            **criteria: Search criteria (name, status, task_name, etc.)
            
        Returns:
            List of matching schedules
        """
        with self._lock:
            results = []
            
            for schedule in self._schedules.values():
                match = True
                
                for key, value in criteria.items():
                    if not hasattr(schedule, key):
                        match = False
                        break
                    
                    schedule_value = getattr(schedule, key)
                    if schedule_value != value:
                        match = False
                        break
                
                if match:
                    results.append(schedule)
            
            return results
    
    def get_schedule_stats(self) -> Dict:
        """
        Get statistics about stored schedules.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            schedules = list(self._schedules.values())
            
            if not schedules:
                return {
                    'total': 0,
                    'by_status': {},
                    'by_type': {},
                    'execution_stats': {}
                }
            
            # Count by status
            status_counts = {}
            for schedule in schedules:
                status = schedule.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by type
            type_counts = {}
            for schedule in schedules:
                schedule_type = schedule.schedule_type.value
                type_counts[schedule_type] = type_counts.get(schedule_type, 0) + 1
            
            # Execution statistics
            total_runs = sum(schedule.run_count for schedule in schedules)
            total_successes = sum(schedule.success_count for schedule in schedules)
            total_failures = sum(schedule.failure_count for schedule in schedules)
            
            # Find most/least active schedules
            most_active = max(schedules, key=lambda s: s.run_count) if schedules else None
            least_active = min(schedules, key=lambda s: s.run_count) if schedules else None
            
            # Recent activity
            recent_schedules = [
                s for s in schedules 
                if s.last_run_at and (datetime.now() - s.last_run_at).days <= 7
            ]
            
            return {
                'total': len(schedules),
                'by_status': status_counts,
                'by_type': type_counts,
                'execution_stats': {
                    'total_runs': total_runs,
                    'total_successes': total_successes,
                    'total_failures': total_failures,
                    'success_rate': (total_successes / total_runs * 100) if total_runs > 0 else 0
                },
                'activity': {
                    'most_active': {
                        'name': most_active.name,
                        'runs': most_active.run_count
                    } if most_active else None,
                    'least_active': {
                        'name': least_active.name,
                        'runs': least_active.run_count
                    } if least_active else None,
                    'active_last_week': len(recent_schedules)
                }
            }
    
    def export_schedules(self, export_path: str) -> bool:
        """
        Export schedules to a file.
        
        Args:
            export_path: Path to export file
            
        Returns:
            True if exported successfully
        """
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with self._lock:
                schedules_data = [
                    schedule.to_dict() 
                    for schedule in self._schedules.values()
                ]
                
                data = {
                    'schedules': schedules_data,
                    'metadata': {
                        'exported_at': datetime.now().isoformat(),
                        'total_schedules': len(schedules_data),
                        'version': '1.0'
                    }
                }
                
                with export_file.open('w') as f:
                    json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Exported {len(schedules_data)} schedules to {export_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export schedules: {str(e)}")
            return False
    
    def import_schedules(self, import_path: str, overwrite: bool = False) -> int:
        """
        Import schedules from a file.
        
        Args:
            import_path: Path to import file
            overwrite: Whether to overwrite existing schedules
            
        Returns:
            Number of schedules imported
        """
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                raise FileNotFoundError(f"Import file not found: {import_path}")
            
            with import_file.open('r') as f:
                data = json.load(f)
            
            schedules_data = data.get('schedules', [])
            imported_count = 0
            
            with self._lock:
                for schedule_data in schedules_data:
                    try:
                        schedule = Schedule.from_dict(schedule_data)
                        
                        # Check if schedule already exists
                        if schedule.id in self._schedules and not overwrite:
                            logger.warning(f"Skipping existing schedule: {schedule.name}")
                            continue
                        
                        self._schedules[schedule.id] = schedule
                        imported_count += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to import schedule: {str(e)}")
                
                # Save after import
                self.save_schedules()
            
            logger.info(f"Imported {imported_count} schedules from {import_path}")
            return imported_count
        
        except Exception as e:
            logger.error(f"Failed to import schedules: {str(e)}")
            return 0
    
    @property
    def schedule_count(self) -> int:
        """Get the total number of schedules."""
        with self._lock:
            return len(self._schedules)