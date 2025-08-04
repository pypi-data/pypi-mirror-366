"""
System metrics collection module for Ansera monitoring dashboard.

This module provides real-time system metrics including CPU, memory,
disk usage, and process information.
"""

import psutil
import docker
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """Container for system metrics data."""
    timestamp: datetime
    cpu_percent: float
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    processes: List[Dict[str, Any]]


class SystemMonitor:
    """
    Monitor system resources and Ansera-specific processes.
    
    Provides real-time metrics for CPU, memory, disk usage,
    and tracks Ansera-related processes including Qdrant.
    """
    
    def __init__(self, cache_duration: int = 5):
        """
        Initialize the system monitor.
        
        Args:
            cache_duration: Seconds to cache metrics (default: 5)
        """
        self.cache_duration = cache_duration
        self._last_metrics: Optional[SystemMetrics] = None
        self._last_fetch: Optional[datetime] = None
        
        # Initialize Docker client for container monitoring
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}")
            self.docker_client = None
            
        # Initialize Qdrant client
        try:
            self.qdrant_client = QdrantClient(host="localhost", port=6333)
        except Exception as e:
            logger.warning(f"Qdrant client initialization failed: {e}")
            self.qdrant_client = None
    
    def get_system_metrics(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get current system metrics with caching.
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            Dictionary containing system metrics
        """
        # Check cache validity
        if not force_refresh and self._is_cache_valid():
            return asdict(self._last_metrics)
        
        # Collect fresh metrics
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=self._get_cpu_usage(),
            memory=self._get_memory_info(),
            disk=self._get_disk_info(),
            processes=self.get_ansera_processes()
        )
        
        # Update cache
        self._last_metrics = metrics
        self._last_fetch = datetime.now()
        
        return asdict(metrics)
    
    def _is_cache_valid(self) -> bool:
        """Check if cached metrics are still valid."""
        if self._last_metrics is None or self._last_fetch is None:
            return False
        
        age = datetime.now() - self._last_fetch
        return age < timedelta(seconds=self.cache_duration)
    
    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        # Use interval=1 for more accurate reading
        return psutil.cpu_percent(interval=1)
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage information."""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2)
        }
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk usage information."""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2)
        }
    
    def get_ansera_processes(self) -> List[Dict[str, Any]]:
        """
        Get list of Ansera-related processes.
        
        Returns:
            List of process information dictionaries
        """
        processes = []
        keywords = ['python', 'qdrant', 'vector', 'ansera', 'mcp']
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    pinfo = proc.info
                    # Check if process name contains any Ansera keywords
                    if any(keyword in pinfo['name'].lower() for keyword in keywords):
                        # Get additional info
                        cmdline = ' '.join(proc.cmdline())
                        
                        # Filter for actual Ansera processes
                        if any(term in cmdline.lower() for term in ['vector_db_query', 'qdrant', 'mcp_server', 'monitoring']):
                            processes.append({
                                'pid': pinfo['pid'],
                                'name': pinfo['name'],
                                'cpu_percent': pinfo['cpu_percent'] or 0.0,
                                'memory_percent': pinfo['memory_percent'] or 0.0,
                                'status': pinfo['status'],
                                'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting processes: {e}")
        
        # Check Docker containers
        if self.docker_client:
            processes.extend(self._get_docker_processes())
        
        return processes
    
    def _get_docker_processes(self) -> List[Dict[str, Any]]:
        """Get Docker container information for Qdrant."""
        containers = []
        
        try:
            for container in self.docker_client.containers.list():
                if 'qdrant' in container.name.lower() or 'qdrant' in container.image.tags[0].lower():
                    stats = container.stats(stream=False)
                    
                    # Calculate CPU percentage
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                               stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                                  stats['precpu_stats']['system_cpu_usage']
                    cpu_percent = 0.0
                    if system_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * 100.0
                    
                    # Calculate memory usage
                    memory_usage = stats['memory_stats'].get('usage', 0)
                    memory_limit = stats['memory_stats'].get('limit', 1)
                    memory_percent = (memory_usage / memory_limit) * 100.0
                    
                    containers.append({
                        'pid': f"docker-{container.short_id}",
                        'name': f"qdrant-container",
                        'cpu_percent': round(cpu_percent, 2),
                        'memory_percent': round(memory_percent, 2),
                        'status': container.status,
                        'cmdline': f"Docker: {container.image.tags[0]}"
                    })
        except Exception as e:
            logger.warning(f"Error getting Docker containers: {e}")
        
        return containers
    
    def get_qdrant_status(self) -> Dict[str, Any]:
        """
        Get Qdrant database status and statistics.
        
        Returns:
            Dictionary with Qdrant status information
        """
        if not self.qdrant_client:
            return {"status": "error", "error": "Qdrant client not initialized"}
        
        try:
            # Try to get collection info
            collections = self.qdrant_client.get_collections()
            
            # Get info about the main documents collection if it exists
            collection_stats = {}
            for collection in collections.collections:
                if collection.name == "documents":
                    info = self.qdrant_client.get_collection(collection.name)
                    collection_stats = {
                        "points_count": info.points_count,
                        "vectors_count": info.vectors_count,
                        "indexed_vectors": info.indexed_vectors_count
                    }
                    break
            
            return {
                "status": "healthy",
                "collections_count": len(collections.collections),
                "collection_names": [c.name for c in collections.collections],
                "documents_collection": collection_stats
            }
            
        except UnexpectedResponse as e:
            if "Service not ready" in str(e):
                return {"status": "starting", "error": "Qdrant is starting up"}
            return {"status": "error", "error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_quick_stats(self) -> Dict[str, Any]:
        """
        Get quick statistics for dashboard display.
        
        Returns:
            Simplified metrics for UI display
        """
        metrics = self.get_system_metrics()
        qdrant = self.get_qdrant_status()
        
        return {
            "cpu": metrics["cpu_percent"],
            "memory": {
                "percent": metrics["memory"]["percent"],
                "used_gb": metrics["memory"]["used_gb"],
                "total_gb": metrics["memory"]["total_gb"]
            },
            "disk": {
                "percent": metrics["disk"]["percent"],
                "used_gb": metrics["disk"]["used_gb"],
                "total_gb": metrics["disk"]["total_gb"]
            },
            "qdrant": {
                "status": qdrant["status"],
                "documents": qdrant.get("documents_collection", {}).get("points_count", 0)
            },
            "process_count": len(metrics["processes"])
        }


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create monitor instance
    monitor = SystemMonitor()
    
    # Get and display metrics
    print("System Metrics:")
    print("-" * 50)
    
    stats = monitor.get_quick_stats()
    print(f"CPU Usage: {stats['cpu']}%")
    print(f"Memory: {stats['memory']['used_gb']}GB / {stats['memory']['total_gb']}GB ({stats['memory']['percent']}%)")
    print(f"Disk: {stats['disk']['used_gb']}GB / {stats['disk']['total_gb']}GB ({stats['disk']['percent']}%)")
    print(f"Qdrant Status: {stats['qdrant']['status']} ({stats['qdrant']['documents']} documents)")
    print(f"Active Processes: {stats['process_count']}")
    
    print("\nDetailed Process List:")
    print("-" * 50)
    
    for proc in monitor.get_ansera_processes():
        print(f"[{proc['pid']}] {proc['name']} - CPU: {proc['cpu_percent']}%, Memory: {proc['memory_percent']}%")
        print(f"  Status: {proc['status']}, Command: {proc['cmdline']}")