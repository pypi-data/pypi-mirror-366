"""
Batch processing system for improved performance.
"""

import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union, TypeVar, Generic
from threading import RLock, Thread, Event
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
from collections import defaultdict
import logging
from concurrent.futures import ThreadPoolExecutor, Future


T = TypeVar('T')
R = TypeVar('R')


class BatchStrategy(Enum):
    """Batch processing strategies."""
    SIZE_BASED = "size_based"        # Process when batch reaches size
    TIME_BASED = "time_based"        # Process at intervals
    HYBRID = "hybrid"                # Combine size and time
    ADAPTIVE = "adaptive"            # Adjust based on load


class ProcessingStatus(Enum):
    """Batch processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class BatchItem(Generic[T]):
    """Individual item in a batch."""
    item_id: str
    data: T
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    retries: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        """Compare by priority for priority queue."""
        return self.priority > other.priority  # Higher priority first


@dataclass
class BatchResult(Generic[R]):
    """Result of batch processing."""
    batch_id: str
    status: ProcessingStatus
    items_processed: int
    items_failed: int
    results: List[R] = field(default_factory=list)
    errors: Dict[str, str] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    
    def complete(self) -> None:
        """Mark batch as complete."""
        self.end_time = datetime.now()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        
        if self.items_failed == 0:
            self.status = ProcessingStatus.COMPLETED
        elif self.items_processed > 0:
            self.status = ProcessingStatus.PARTIAL
        else:
            self.status = ProcessingStatus.FAILED


@dataclass
class BatchConfig:
    """Batch processing configuration."""
    max_batch_size: int = 100
    max_wait_time_ms: int = 1000
    strategy: BatchStrategy = BatchStrategy.HYBRID
    max_concurrent_batches: int = 5
    retry_delay_ms: int = 1000
    exponential_backoff: bool = True
    
    # Adaptive strategy parameters
    target_latency_ms: float = 100.0
    min_batch_size: int = 10
    adjustment_factor: float = 0.1


class BatchProcessor(Generic[T, R]):
    """
    High-performance batch processing system.
    """
    
    def __init__(self,
                 processor_func: Callable[[List[T]], List[R]],
                 config: BatchConfig = None,
                 name: str = "BatchProcessor"):
        """Initialize batch processor."""
        self._lock = RLock()
        self.processor_func = processor_func
        self.config = config or BatchConfig()
        self.name = name
        
        # Batch queue
        self.pending_items: Queue[BatchItem[T]] = Queue()
        self.current_batch: List[BatchItem[T]] = []
        
        # Processing state
        self.processing_active = False
        self.processor_thread: Optional[Thread] = None
        self.stop_event = Event()
        
        # Thread pool for concurrent batch processing
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.max_concurrent_batches,
            thread_name_prefix=f"{name}_worker"
        )
        
        # Statistics
        self.total_items_processed = 0
        self.total_items_failed = 0
        self.total_batches = 0
        self.average_batch_size = 0.0
        self.average_latency_ms = 0.0
        
        # Adaptive parameters
        self.current_batch_size = self.config.max_batch_size
        self.current_wait_time = self.config.max_wait_time_ms
        
        # Result callbacks
        self.result_callbacks: List[Callable[[BatchResult[R]], None]] = []
        
        # Error callbacks
        self.error_callbacks: List[Callable[[str, Exception], None]] = []
        
        # Logger
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def start(self) -> None:
        """Start batch processing."""
        with self._lock:
            if not self.processing_active:
                self.processing_active = True
                self.stop_event.clear()
                self.processor_thread = Thread(
                    target=self._process_loop,
                    daemon=True,
                    name=f"{self.name}_processor"
                )
                self.processor_thread.start()
                self.logger.info(f"Batch processor '{self.name}' started")
    
    def stop(self, timeout: float = 5.0) -> None:
        """Stop batch processing."""
        with self._lock:
            if self.processing_active:
                self.processing_active = False
                self.stop_event.set()
                
                # Process any remaining items
                if self.current_batch:
                    self._process_batch(self.current_batch)
                
                if self.processor_thread:
                    self.processor_thread.join(timeout=timeout)
                
                # Shutdown executor
                self.executor.shutdown(wait=True)
                
                self.logger.info(f"Batch processor '{self.name}' stopped")
    
    def add_item(self, item_id: str, data: T, priority: int = 0, metadata: Dict[str, Any] = None) -> None:
        """Add item to batch queue."""
        if not self.processing_active:
            raise RuntimeError("Batch processor is not running")
        
        batch_item = BatchItem(
            item_id=item_id,
            data=data,
            priority=priority,
            metadata=metadata or {}
        )
        
        self.pending_items.put(batch_item)
    
    def add_items(self, items: List[Tuple[str, T]], priority: int = 0) -> None:
        """Add multiple items to batch queue."""
        for item_id, data in items:
            self.add_item(item_id, data, priority)
    
    def _process_loop(self) -> None:
        """Main processing loop."""
        last_batch_time = datetime.now()
        
        while self.processing_active and not self.stop_event.is_set():
            try:
                # Calculate wait time based on strategy
                wait_time = self._calculate_wait_time()
                
                # Collect items for batch
                deadline = datetime.now() + timedelta(milliseconds=wait_time)
                
                while datetime.now() < deadline and len(self.current_batch) < self.current_batch_size:
                    try:
                        remaining_time = (deadline - datetime.now()).total_seconds()
                        if remaining_time <= 0:
                            break
                        
                        # Get item with timeout
                        item = self.pending_items.get(timeout=min(remaining_time, 0.1))
                        self.current_batch.append(item)
                        
                    except Empty:
                        # Check if we should process what we have
                        if self._should_process_batch(last_batch_time):
                            break
                
                # Process batch if ready
                if self.current_batch and self._should_process_batch(last_batch_time):
                    # Submit batch for processing
                    batch_copy = self.current_batch.copy()
                    self.current_batch.clear()
                    
                    future = self.executor.submit(self._process_batch, batch_copy)
                    future.add_done_callback(self._handle_batch_complete)
                    
                    last_batch_time = datetime.now()
                    
                    # Adaptive adjustment
                    if self.config.strategy == BatchStrategy.ADAPTIVE:
                        self._adjust_parameters()
                
                # Small sleep to prevent busy waiting
                time.sleep(0.01)
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                self._notify_error("processing_loop", e)
    
    def _calculate_wait_time(self) -> int:
        """Calculate wait time based on strategy."""
        if self.config.strategy == BatchStrategy.SIZE_BASED:
            return 10000  # 10 seconds max wait for size-based
        elif self.config.strategy == BatchStrategy.TIME_BASED:
            return self.config.max_wait_time_ms
        else:  # HYBRID or ADAPTIVE
            return self.current_wait_time
    
    def _should_process_batch(self, last_batch_time: datetime) -> bool:
        """Determine if batch should be processed."""
        if not self.current_batch:
            return False
        
        # Size threshold reached
        if len(self.current_batch) >= self.current_batch_size:
            return True
        
        # Time threshold reached
        elapsed_ms = (datetime.now() - last_batch_time).total_seconds() * 1000
        if elapsed_ms >= self.current_wait_time:
            return True
        
        return False
    
    def _process_batch(self, batch: List[BatchItem[T]]) -> BatchResult[R]:
        """Process a batch of items."""
        batch_id = f"{self.name}_{datetime.now().timestamp()}"
        result = BatchResult[R](batch_id=batch_id, status=ProcessingStatus.PROCESSING)
        
        try:
            # Extract data from batch items
            data_items = [item.data for item in batch]
            
            # Process batch
            start_time = time.time()
            processed_results = self.processor_func(data_items)
            processing_time = (time.time() - start_time) * 1000
            
            # Update statistics
            self._update_statistics(len(batch), 0, processing_time)
            
            # Build result
            result.items_processed = len(processed_results)
            result.results = processed_results
            result.complete()
            
            self.logger.debug(f"Processed batch {batch_id}: {len(batch)} items in {processing_time:.2f}ms")
            
        except Exception as e:
            self.logger.error(f"Error processing batch {batch_id}: {e}")
            
            # Handle failed items
            result.items_failed = len(batch)
            result.errors[batch_id] = str(e)
            
            # Retry logic
            for item in batch:
                if item.retries < item.max_retries:
                    item.retries += 1
                    # Calculate retry delay with exponential backoff
                    delay = self.config.retry_delay_ms
                    if self.config.exponential_backoff:
                        delay *= (2 ** item.retries)
                    
                    # Re-queue for retry
                    Thread(
                        target=self._retry_item,
                        args=(item, delay),
                        daemon=True
                    ).start()
                else:
                    self.total_items_failed += 1
            
            result.complete()
            self._notify_error(f"batch_{batch_id}", e)
        
        # Notify callbacks
        self._notify_result(result)
        
        return result
    
    def _retry_item(self, item: BatchItem[T], delay_ms: int) -> None:
        """Retry a failed item after delay."""
        time.sleep(delay_ms / 1000.0)
        if self.processing_active:
            self.pending_items.put(item)
    
    def _handle_batch_complete(self, future: Future) -> None:
        """Handle batch completion."""
        try:
            result = future.result()
            # Result is already handled in _process_batch
        except Exception as e:
            self.logger.error(f"Error handling batch completion: {e}")
    
    def _update_statistics(self, items_processed: int, items_failed: int, latency_ms: float) -> None:
        """Update processing statistics."""
        with self._lock:
            self.total_items_processed += items_processed
            self.total_items_failed += items_failed
            self.total_batches += 1
            
            # Update moving averages
            alpha = 0.1  # Smoothing factor
            self.average_batch_size = (1 - alpha) * self.average_batch_size + alpha * items_processed
            self.average_latency_ms = (1 - alpha) * self.average_latency_ms + alpha * latency_ms
    
    def _adjust_parameters(self) -> None:
        """Adjust batch parameters for adaptive strategy."""
        if self.config.strategy != BatchStrategy.ADAPTIVE:
            return
        
        with self._lock:
            # Adjust batch size based on latency
            if self.average_latency_ms > self.config.target_latency_ms:
                # Reduce batch size if latency is too high
                self.current_batch_size = max(
                    self.config.min_batch_size,
                    int(self.current_batch_size * (1 - self.config.adjustment_factor))
                )
            else:
                # Increase batch size if latency is acceptable
                self.current_batch_size = min(
                    self.config.max_batch_size,
                    int(self.current_batch_size * (1 + self.config.adjustment_factor))
                )
            
            # Adjust wait time based on queue depth
            queue_depth = self.pending_items.qsize()
            if queue_depth > self.current_batch_size * 2:
                # Reduce wait time if queue is building up
                self.current_wait_time = max(
                    100,  # Minimum 100ms
                    int(self.current_wait_time * (1 - self.config.adjustment_factor))
                )
            else:
                # Increase wait time if queue is shallow
                self.current_wait_time = min(
                    self.config.max_wait_time_ms,
                    int(self.current_wait_time * (1 + self.config.adjustment_factor))
                )
    
    def add_result_callback(self, callback: Callable[[BatchResult[R]], None]) -> None:
        """Add callback for batch results."""
        with self._lock:
            self.result_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable[[str, Exception], None]) -> None:
        """Add callback for errors."""
        with self._lock:
            self.error_callbacks.append(callback)
    
    def _notify_result(self, result: BatchResult[R]) -> None:
        """Notify callbacks of batch result."""
        for callback in self.result_callbacks:
            try:
                callback(result)
            except Exception as e:
                self.logger.error(f"Error in result callback: {e}")
    
    def _notify_error(self, context: str, error: Exception) -> None:
        """Notify callbacks of error."""
        for callback in self.error_callbacks:
            try:
                callback(context, error)
            except Exception as e:
                self.logger.error(f"Error in error callback: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        with self._lock:
            success_rate = self.total_items_processed / (self.total_items_processed + self.total_items_failed) \
                if (self.total_items_processed + self.total_items_failed) > 0 else 0.0
            
            return {
                'name': self.name,
                'total_items_processed': self.total_items_processed,
                'total_items_failed': self.total_items_failed,
                'total_batches': self.total_batches,
                'average_batch_size': round(self.average_batch_size, 2),
                'average_latency_ms': round(self.average_latency_ms, 2),
                'success_rate': round(success_rate, 4),
                'current_batch_size': self.current_batch_size,
                'current_wait_time_ms': self.current_wait_time,
                'pending_items': self.pending_items.qsize(),
                'strategy': self.config.strategy.value
            }
    
    def flush(self, timeout: float = 5.0) -> bool:
        """Flush all pending items."""
        start_time = time.time()
        
        while self.pending_items.qsize() > 0 or self.current_batch:
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.1)
        
        return True


# Global batch processors registry
_batch_processors: Dict[str, BatchProcessor] = {}
_processors_lock = RLock()


def get_batch_processor(name: str, 
                       processor_func: Callable[[List[T]], List[R]] = None,
                       config: BatchConfig = None) -> BatchProcessor[T, R]:
    """
    Get or create a named batch processor.
    
    Args:
        name: Processor name
        processor_func: Processing function (required for new processor)
        config: Batch configuration
    
    Returns:
        Batch processor instance
    """
    global _batch_processors
    with _processors_lock:
        if name not in _batch_processors:
            if processor_func is None:
                raise ValueError(f"Processor function required for new batch processor '{name}'")
            _batch_processors[name] = BatchProcessor(processor_func, config, name)
        return _batch_processors[name]


def remove_batch_processor(name: str) -> None:
    """Remove and stop a batch processor."""
    global _batch_processors
    with _processors_lock:
        if name in _batch_processors:
            _batch_processors[name].stop()
            del _batch_processors[name]