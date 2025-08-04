"""Docker manager for Qdrant container."""

import subprocess
import time
from pathlib import Path
from typing import Dict, Optional

import docker
from docker.errors import NotFound, APIError

from vector_db_query.vector_db.exceptions import (
    DockerError,
    ContainerNotFoundError,
    ContainerNotRunningError
)
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class QdrantDockerManager:
    """Manages Qdrant Docker container lifecycle."""
    
    CONTAINER_NAME = "vector-db-qdrant"
    IMAGE_NAME = "qdrant/qdrant:latest"
    DEFAULT_HTTP_PORT = 6333
    DEFAULT_GRPC_PORT = 6334
    
    def __init__(self, docker_compose_path: Optional[Path] = None):
        """Initialize Docker manager.
        
        Args:
            docker_compose_path: Path to docker-compose.yml file
        """
        try:
            self.client = docker.from_env()
        except Exception as e:
            raise DockerError(f"Failed to connect to Docker: {e}")
            
        # Set docker-compose path
        if docker_compose_path is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
            docker_compose_path = project_root / "docker" / "docker-compose.yml"
            
        self.docker_compose_path = docker_compose_path
        
    def start_container(self) -> bool:
        """Start Qdrant container using docker-compose.
        
        Returns:
            True if container started successfully
        """
        try:
            # Check if container already exists
            container = self._get_container()
            if container:
                if container.status == "running":
                    logger.info("Qdrant container is already running")
                    return True
                else:
                    logger.info("Starting existing Qdrant container")
                    container.start()
                    return self._wait_for_container()
                    
            # Start using docker-compose
            logger.info("Starting Qdrant container with docker-compose")
            return self._start_with_compose()
            
        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            raise DockerError(f"Failed to start Qdrant container: {e}")
            
    def stop_container(self) -> bool:
        """Stop Qdrant container.
        
        Returns:
            True if container stopped successfully
        """
        try:
            if self.docker_compose_path.exists():
                # Stop using docker-compose
                return self._stop_with_compose()
            else:
                # Stop using Docker API
                container = self._get_container()
                if container and container.status == "running":
                    logger.info("Stopping Qdrant container")
                    container.stop()
                    return True
                else:
                    logger.info("Container is not running")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to stop container: {e}")
            raise DockerError(f"Failed to stop Qdrant container: {e}")
            
    def restart_container(self) -> bool:
        """Restart Qdrant container.
        
        Returns:
            True if container restarted successfully
        """
        logger.info("Restarting Qdrant container")
        self.stop_container()
        time.sleep(2)  # Brief pause
        return self.start_container()
        
    def is_running(self) -> bool:
        """Check if Qdrant container is running.
        
        Returns:
            True if container is running
        """
        try:
            # First check if any Qdrant is accessible
            import requests
            response = requests.get(f"http://localhost:{self.DEFAULT_HTTP_PORT}", timeout=2)
            if response.status_code == 200:
                logger.info("Qdrant is accessible on port 6333")
                return True
        except Exception:
            pass
            
        # Check for our specific container
        try:
            container = self._get_container()
            return container is not None and container.status == "running"
        except Exception:
            return False
            
    def get_container_info(self) -> Dict[str, any]:
        """Get information about the Qdrant container.
        
        Returns:
            Dictionary with container information
        """
        try:
            container = self._get_container()
            if not container:
                return {"status": "not_found"}
                
            return {
                "id": container.short_id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "ports": container.ports,
                "created": container.attrs["Created"],
                "started": container.attrs.get("State", {}).get("StartedAt", "")
            }
            
        except Exception as e:
            logger.error(f"Failed to get container info: {e}")
            return {"status": "error", "error": str(e)}
            
    def wait_for_health(self, timeout: int = 60) -> bool:
        """Wait for Qdrant to be healthy.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if healthy within timeout
        """
        import requests
        
        start_time = time.time()
        health_url = f"http://localhost:{self.DEFAULT_HTTP_PORT}/health"
        
        logger.info("Waiting for Qdrant to be healthy...")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    logger.info("Qdrant is healthy")
                    return True
            except Exception:
                pass  # Expected while starting up
                
            time.sleep(1)
            
        logger.error("Qdrant health check timeout")
        return False
        
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.client.close()
        except Exception:
            pass
            
    def _get_container(self) -> Optional[docker.models.containers.Container]:
        """Get Qdrant container if it exists.
        
        Returns:
            Container object or None
        """
        try:
            return self.client.containers.get(self.CONTAINER_NAME)
        except NotFound:
            return None
        except Exception as e:
            logger.error(f"Error getting container: {e}")
            return None
            
    def _start_with_compose(self) -> bool:
        """Start container using docker-compose.
        
        Returns:
            True if successful
        """
        if not self.docker_compose_path.exists():
            raise DockerError(f"docker-compose.yml not found at {self.docker_compose_path}")
            
        try:
            # Change to docker directory
            docker_dir = self.docker_compose_path.parent
            
            # Run docker-compose up
            result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                cwd=docker_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Try legacy docker-compose command
                result = subprocess.run(
                    ["docker-compose", "up", "-d"],
                    cwd=docker_dir,
                    capture_output=True,
                    text=True
                )
                
            if result.returncode != 0:
                raise DockerError(f"docker-compose failed: {result.stderr}")
                
            return self._wait_for_container()
            
        except Exception as e:
            logger.error(f"Failed to start with docker-compose: {e}")
            raise DockerError(f"Failed to start with docker-compose: {e}")
            
    def _stop_with_compose(self) -> bool:
        """Stop container using docker-compose.
        
        Returns:
            True if successful
        """
        try:
            docker_dir = self.docker_compose_path.parent
            
            # Run docker-compose down
            result = subprocess.run(
                ["docker", "compose", "down"],
                cwd=docker_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Try legacy docker-compose command
                result = subprocess.run(
                    ["docker-compose", "down"],
                    cwd=docker_dir,
                    capture_output=True,
                    text=True
                )
                
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to stop with docker-compose: {e}")
            return False
            
    def _wait_for_container(self, timeout: int = 30) -> bool:
        """Wait for container to be running.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if container is running within timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_running():
                # Give it a moment to fully start
                time.sleep(2)
                return True
            time.sleep(0.5)
            
        return False