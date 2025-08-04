"""
Ansera Queue Worker - Document Processing Pipeline

This module runs as a background service managed by PM2 to process
documents in the queue asynchronously.
"""

import os
import sys
import time
import json
import logging
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from vector_db_query.monitoring.process_manager import QueueMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class QueueWorker:
    """Background worker for processing document queue."""
    
    def __init__(self, batch_size: int = 10, poll_interval: int = 5):
        """
        Initialize queue worker.
        
        Args:
            batch_size: Number of documents to process in batch
            poll_interval: Seconds between queue checks
        """
        self.batch_size = batch_size
        self.poll_interval = poll_interval
        self.queue_monitor = QueueMonitor()
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        
        logger.info(f"Queue worker initialized (batch_size={batch_size}, poll_interval={poll_interval}s)")
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def process_document(self, job_data: Dict[str, Any]) -> bool:
        """
        Process a single document.
        
        Args:
            job_data: Job information from queue
            
        Returns:
            True if successful, False otherwise
        """
        try:
            job_id = job_data.get('job_id')
            document_path = job_data.get('document_path')
            
            logger.info(f"Processing document: {document_path} (job_id: {job_id})")
            
            # Simulate document processing
            # In real implementation, this would:
            # 1. Read the document
            # 2. Extract text/content
            # 3. Generate embeddings
            # 4. Store in Qdrant
            # 5. Update metadata
            
            # For now, simulate processing time
            processing_time = 2 + (hash(job_id) % 3)  # 2-5 seconds
            time.sleep(processing_time)
            
            # Random success (90% success rate for demo)
            import random
            if random.random() < 0.9:
                logger.info(f"Successfully processed: {document_path}")
                return True
            else:
                raise Exception("Simulated processing error")
                
        except Exception as e:
            logger.error(f"Error processing document {job_data.get('document_path')}: {e}")
            return False
    
    def process_batch(self):
        """Process a batch of queued documents."""
        try:
            # Get pending jobs
            pending_jobs = self.queue_monitor.get_pending_jobs(limit=self.batch_size)
            
            if not pending_jobs:
                return
            
            logger.info(f"Processing batch of {len(pending_jobs)} documents")
            
            for job in pending_jobs:
                if not self.running:
                    logger.info("Shutdown requested, stopping batch processing")
                    break
                
                # Mark as processing
                self.queue_monitor.update_job_status(
                    job['job_id'], 
                    'processing',
                    {'worker_pid': os.getpid()}
                )
                
                # Process the document
                success = self.process_document(job)
                
                # Update status based on result
                if success:
                    self.queue_monitor.update_job_status(
                        job['job_id'],
                        'completed',
                        {
                            'completed_at': datetime.now().isoformat()
                        }
                    )
                else:
                    self.queue_monitor.update_job_status(
                        job['job_id'],
                        'failed',
                        {
                            'failed_at': datetime.now().isoformat(),
                            'error': 'Processing failed'
                        }
                    )
            
            logger.info(f"Batch processing completed")
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
    
    def run(self):
        """Main worker loop."""
        logger.info("Queue worker started")
        
        while self.running:
            try:
                # Process batch
                self.process_batch()
                
                # Sleep between batches
                if self.running:
                    time.sleep(self.poll_interval)
                    
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {e}")
                time.sleep(self.poll_interval)
        
        logger.info("Queue worker stopped")


def main():
    """Entry point for queue worker."""
    # Get configuration from environment
    batch_size = int(os.environ.get('QUEUE_BATCH_SIZE', '10'))
    poll_interval = int(os.environ.get('QUEUE_POLL_INTERVAL', '5'))
    
    # Create and run worker
    worker = QueueWorker(batch_size=batch_size, poll_interval=poll_interval)
    
    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("Queue worker interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error in queue worker: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()