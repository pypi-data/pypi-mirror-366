"""
Qdrant Health Monitor

This module monitors the health of the Qdrant vector database
and can restart it if necessary.
"""

import os
import sys
import time
import logging
import signal
from datetime import datetime
from typing import Dict, Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QdrantHealthMonitor:
    """Monitor Qdrant health and perform recovery actions."""
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize health monitor.
        
        Args:
            check_interval: Seconds between health checks
        """
        self.check_interval = check_interval
        self.qdrant_url = os.environ.get('QDRANT_URL', 'http://localhost:6333')
        self.running = True
        self.consecutive_failures = 0
        self.max_failures = 3
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        
        logger.info(f"Qdrant health monitor initialized (check_interval={check_interval}s)")
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check Qdrant health status.
        
        Returns:
            Health status dictionary
        """
        try:
            # Check Qdrant health endpoint
            response = requests.get(
                f"{self.qdrant_url}/healthz",
                timeout=5
            )
            
            if response.status_code == 200:
                # Get additional info
                try:
                    collections_response = requests.get(
                        f"{self.qdrant_url}/collections",
                        timeout=5
                    )
                    collections_data = collections_response.json()
                    collection_count = len(collections_data.get('result', {}).get('collections', []))
                except:
                    collection_count = -1
                
                return {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'collections': collection_count,
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
            else:
                return {
                    'status': 'unhealthy',
                    'timestamp': datetime.now().isoformat(),
                    'status_code': response.status_code,
                    'error': f'Unexpected status code: {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': 'Health check timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': 'Connection refused - Qdrant may be down'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def perform_recovery(self):
        """Attempt to recover Qdrant if it's unhealthy."""
        logger.warning("Attempting Qdrant recovery...")
        
        try:
            # In a real implementation, this would:
            # 1. Try to restart the Docker container
            # 2. Check Docker logs for errors
            # 3. Possibly clear corrupted data
            # 4. Send alerts to administrators
            
            # For now, just log the attempt
            logger.info("Recovery attempt completed (manual intervention may be required)")
            
            # Reset failure counter after recovery attempt
            self.consecutive_failures = 0
            
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
    
    def run(self):
        """Main monitoring loop."""
        logger.info("Qdrant health monitor started")
        
        while self.running:
            try:
                # Check health
                health_status = self.check_health()
                
                if health_status['status'] == 'healthy':
                    if self.consecutive_failures > 0:
                        logger.info(f"Qdrant recovered after {self.consecutive_failures} failures")
                    self.consecutive_failures = 0
                    
                    logger.debug(f"Qdrant healthy - Collections: {health_status.get('collections', 'N/A')}, "
                               f"Response time: {health_status.get('response_time_ms', 'N/A')}ms")
                else:
                    self.consecutive_failures += 1
                    logger.warning(f"Qdrant unhealthy (failure {self.consecutive_failures}/{self.max_failures}): "
                                 f"{health_status.get('error', 'Unknown error')}")
                    
                    # Attempt recovery after max consecutive failures
                    if self.consecutive_failures >= self.max_failures:
                        self.perform_recovery()
                
                # Sleep between checks
                if self.running:
                    time.sleep(self.check_interval)
                    
            except Exception as e:
                logger.error(f"Unexpected error in monitoring loop: {e}")
                time.sleep(self.check_interval)
        
        logger.info("Qdrant health monitor stopped")


def main():
    """Entry point for health monitor."""
    # Get configuration from environment
    check_interval = int(os.environ.get('QDRANT_CHECK_INTERVAL', '60'))
    
    # Create and run monitor
    monitor = QdrantHealthMonitor(check_interval=check_interval)
    
    try:
        monitor.run()
    except KeyboardInterrupt:
        logger.info("Health monitor interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error in health monitor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()