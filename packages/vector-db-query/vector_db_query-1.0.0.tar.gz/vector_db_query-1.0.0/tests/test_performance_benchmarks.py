"""Performance benchmark tests for document processing."""

import pytest
import time
import tempfile
import shutil
from pathlib import Path
import psutil
import json
import csv
import random
import string
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

from vector_db_query.document_processor import DocumentProcessor
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceMetrics:
    """Track performance metrics during tests."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.peak_memory = None
        self.files_processed = 0
        self.total_chunks = 0
        self.total_bytes = 0
        
    def start(self):
        """Start tracking metrics."""
        self.start_time = time.time()
        self.start_memory = self._get_memory_usage()
        
    def stop(self):
        """Stop tracking and calculate results."""
        self.end_time = time.time()
        self.peak_memory = self._get_memory_usage()
        
    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
        
    @property
    def duration(self):
        """Get duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
        
    @property
    def memory_increase(self):
        """Get memory increase in MB."""
        if self.start_memory and self.peak_memory:
            return self.peak_memory - self.start_memory
        return 0
        
    @property
    def files_per_second(self):
        """Calculate files processed per second."""
        if self.duration > 0:
            return self.files_processed / self.duration
        return 0
        
    @property
    def mb_per_second(self):
        """Calculate MB processed per second."""
        if self.duration > 0:
            return (self.total_bytes / 1024 / 1024) / self.duration
        return 0
        
    def report(self):
        """Generate performance report."""
        return {
            "duration_seconds": round(self.duration, 2),
            "files_processed": self.files_processed,
            "total_chunks": self.total_chunks,
            "total_mb": round(self.total_bytes / 1024 / 1024, 2),
            "files_per_second": round(self.files_per_second, 2),
            "mb_per_second": round(self.mb_per_second, 2),
            "memory_increase_mb": round(self.memory_increase, 2),
            "chunks_per_file": round(self.total_chunks / max(self.files_processed, 1), 2)
        }


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path, ignore_errors=True)
        
    @pytest.fixture
    def benchmark_files(self, temp_dir):
        """Create files for benchmarking."""
        files = {}
        
        # Small text files (100 files, ~1KB each)
        files['small_text'] = []
        for i in range(100):
            file_path = temp_dir / f"small_{i}.txt"
            content = f"Small text file {i}\n" * 50
            file_path.write_text(content)
            files['small_text'].append(file_path)
            
        # Medium documents (50 files, ~100KB each)
        files['medium_docs'] = []
        for i in range(50):
            file_path = temp_dir / f"medium_{i}.md"
            content = self._generate_markdown_content(100)
            file_path.write_text(content)
            files['medium_docs'].append(file_path)
            
        # Large files (10 files, ~1MB each)
        files['large_files'] = []
        for i in range(10):
            file_path = temp_dir / f"large_{i}.txt"
            content = self._generate_large_content(1000)
            file_path.write_text(content)
            files['large_files'].append(file_path)
            
        # Mixed formats (20 files each)
        files['mixed_formats'] = []
        for i in range(20):
            # JSON
            json_file = temp_dir / f"data_{i}.json"
            json_data = {
                "id": i,
                "data": [{"value": j} for j in range(100)],
                "metadata": {"created": "2025-07-31", "size": "medium"}
            }
            json_file.write_text(json.dumps(json_data, indent=2))
            files['mixed_formats'].append(json_file)
            
            # CSV
            csv_file = temp_dir / f"data_{i}.csv"
            with csv_file.open('w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Value', 'Status'])
                for j in range(100):
                    writer.writerow([j, f'Item_{j}', random.randint(1, 1000), 'Active'])
            files['mixed_formats'].append(csv_file)
            
        return files
        
    def _generate_markdown_content(self, kb_size):
        """Generate markdown content of approximately kb_size KB."""
        content = []
        content.append("# Large Document\n\n")
        
        # Generate sections
        sections = ['Introduction', 'Background', 'Methods', 'Results', 'Discussion', 'Conclusion']
        
        target_chars = kb_size * 1024
        current_chars = 0
        
        while current_chars < target_chars:
            section = random.choice(sections)
            content.append(f"## {section}\n\n")
            
            # Add paragraphs
            for _ in range(random.randint(3, 7)):
                paragraph = self._generate_paragraph()
                content.append(f"{paragraph}\n\n")
                current_chars += len(paragraph)
                
            # Add list
            content.append("Key points:\n")
            for _ in range(random.randint(3, 6)):
                point = f"- {self._generate_sentence()}\n"
                content.append(point)
                current_chars += len(point)
                
        return ''.join(content)
        
    def _generate_large_content(self, kb_size):
        """Generate large text content."""
        words = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog',
                 'lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing']
        
        target_chars = kb_size * 1024
        content = []
        current_chars = 0
        
        while current_chars < target_chars:
            line = ' '.join(random.choices(words, k=20)) + '\n'
            content.append(line)
            current_chars += len(line)
            
        return ''.join(content)
        
    def _generate_sentence(self):
        """Generate a random sentence."""
        words = ['analysis', 'processing', 'document', 'system', 'performance',
                 'benchmark', 'testing', 'integration', 'quality', 'metrics']
        return ' '.join(random.choices(words, k=random.randint(8, 15))).capitalize() + '.'
        
    def _generate_paragraph(self):
        """Generate a random paragraph."""
        sentences = [self._generate_sentence() for _ in range(random.randint(3, 6))]
        return ' '.join(sentences)
        
    def test_small_files_performance(self, benchmark_files):
        """Benchmark processing many small files."""
        processor = DocumentProcessor(chunk_size=500)
        metrics = PerformanceMetrics()
        
        files = benchmark_files['small_text']
        
        metrics.start()
        
        for file_path in files:
            doc = processor.process_file(file_path)
            metrics.files_processed += 1
            metrics.total_chunks += len(doc.chunks)
            metrics.total_bytes += file_path.stat().st_size
            
        metrics.stop()
        
        report = metrics.report()
        logger.info(f"Small files benchmark: {report}")
        
        # Performance assertions (adjusted for real-world processing with embeddings)
        assert metrics.files_per_second > 1, f"Too slow: {metrics.files_per_second} files/sec"
        assert metrics.memory_increase < 200, f"Too much memory: {metrics.memory_increase} MB"
        
    def test_large_files_performance(self, benchmark_files):
        """Benchmark processing large files."""
        processor = DocumentProcessor(chunk_size=1000)
        metrics = PerformanceMetrics()
        
        files = benchmark_files['large_files']
        
        metrics.start()
        
        for file_path in files:
            doc = processor.process_file(file_path)
            metrics.files_processed += 1
            metrics.total_chunks += len(doc.chunks)
            metrics.total_bytes += file_path.stat().st_size
            
        metrics.stop()
        
        report = metrics.report()
        logger.info(f"Large files benchmark: {report}")
        
        # Performance assertions (adjusted for real-world processing)
        assert metrics.mb_per_second > 0.1, f"Too slow: {metrics.mb_per_second} MB/sec"
        assert metrics.memory_increase < 300, f"Too much memory: {metrics.memory_increase} MB"
        
    def test_mixed_formats_performance(self, benchmark_files):
        """Benchmark processing mixed file formats."""
        processor = DocumentProcessor()
        metrics = PerformanceMetrics()
        
        files = benchmark_files['mixed_formats']
        
        metrics.start()
        
        for file_path in files:
            doc = processor.process_file(file_path)
            metrics.files_processed += 1
            metrics.total_chunks += len(doc.chunks)
            metrics.total_bytes += file_path.stat().st_size
            
        metrics.stop()
        
        report = metrics.report()
        logger.info(f"Mixed formats benchmark: {report}")
        
        # Performance assertions
        assert metrics.files_per_second > 0.5, f"Too slow: {metrics.files_per_second} files/sec"
        
    def test_parallel_processing_performance(self, benchmark_files):
        """Benchmark parallel processing performance."""
        files = benchmark_files['medium_docs']
        
        # Test different worker counts
        worker_counts = [1, 2, 4, 8]
        results = {}
        
        for workers in worker_counts:
            processor = DocumentProcessor()
            metrics = PerformanceMetrics()
            
            metrics.start()
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = []
                for file_path in files:
                    future = executor.submit(processor.process_file, file_path)
                    futures.append(future)
                    
                # Wait for completion
                for future in futures:
                    doc = future.result()
                    metrics.files_processed += 1
                    metrics.total_chunks += len(doc.chunks)
                    
            metrics.stop()
            
            results[workers] = metrics.report()
            logger.info(f"Parallel processing ({workers} workers): {results[workers]}")
            
        # Verify scaling
        # Should see improvement up to a point
        assert results[2]['files_per_second'] > results[1]['files_per_second']
        assert results[4]['files_per_second'] >= results[2]['files_per_second']
        
    def test_memory_efficiency(self, temp_dir):
        """Test memory efficiency with very large file."""
        # Create a very large file (50 MB)
        large_file = temp_dir / "very_large.txt"
        
        # Write in chunks to avoid memory issues during creation
        with large_file.open('w') as f:
            chunk = "x" * 1024 * 1024  # 1 MB chunk
            for _ in range(50):
                f.write(chunk)
                
        processor = DocumentProcessor(chunk_size=1000)
        
        # Monitor memory during processing
        memory_samples = []
        
        def monitor_memory():
            """Sample memory usage during processing."""
            process = psutil.Process()
            while True:
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
                time.sleep(0.1)
                if len(memory_samples) > 100:  # Max 10 seconds
                    break
                    
        # Start memory monitoring in thread
        import threading
        monitor_thread = threading.Thread(target=monitor_memory, daemon=True)
        monitor_thread.start()
        
        # Process file
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        doc = processor.process_file(large_file)
        
        # Wait a bit for final memory sample
        time.sleep(0.5)
        
        # Analyze memory usage
        if memory_samples:
            peak_memory = max(memory_samples)
            memory_increase = peak_memory - start_memory
            
            # Memory increase should be much less than file size
            assert memory_increase < 100, f"Memory increase too high: {memory_increase} MB"
            
            # Should have processed the file
            assert len(doc.chunks) > 0
            assert doc.metadata.file_size > 50 * 1024 * 1024
            
    def test_chunking_performance(self, temp_dir):
        """Test performance impact of different chunk sizes."""
        # Create test file
        test_file = temp_dir / "chunk_test.txt"
        content = self._generate_large_content(500)  # 500 KB
        test_file.write_text(content)
        
        chunk_sizes = [500, 1000, 2000, 5000]
        results = {}
        
        for chunk_size in chunk_sizes:
            processor = DocumentProcessor(
                chunk_size=chunk_size,
                chunk_overlap=int(chunk_size * 0.1)
            )
            
            start_time = time.time()
            doc = processor.process_file(test_file)
            duration = time.time() - start_time
            
            results[chunk_size] = {
                'duration': duration,
                'chunks': len(doc.chunks),
                'avg_chunk_size': sum(len(c.text) for c in doc.chunks) / len(doc.chunks)
            }
            
            logger.info(f"Chunk size {chunk_size}: {results[chunk_size]}")
            
        # Larger chunks should be faster but produce fewer chunks
        assert results[5000]['chunks'] < results[500]['chunks']
        assert results[5000]['duration'] <= results[500]['duration'] * 1.5
        
    @pytest.mark.slow
    def test_stress_test(self, temp_dir):
        """Stress test with many files."""
        # Create 1000 small files
        files = []
        for i in range(1000):
            file_path = temp_dir / f"stress_{i}.txt"
            file_path.write_text(f"Stress test file {i}\n" * 10)
            files.append(file_path)
            
        processor = DocumentProcessor()
        metrics = PerformanceMetrics()
        
        metrics.start()
        
        # Process all files
        error_count = 0
        for file_path in files:
            try:
                doc = processor.process_file(file_path)
                metrics.files_processed += 1
                metrics.total_chunks += len(doc.chunks)
                metrics.total_bytes += file_path.stat().st_size
            except Exception as e:
                error_count += 1
                logger.error(f"Failed to process {file_path}: {e}")
                
        metrics.stop()
        
        report = metrics.report()
        logger.info(f"Stress test results: {report}")
        logger.info(f"Errors: {error_count}")
        
        # Should handle all files
        assert error_count < 50  # Allow for some failures due to test environment
        assert metrics.files_processed > 950  # Should process most files
        assert metrics.files_per_second > 2  # Reasonable throughput
        
    def test_format_specific_performance(self, temp_dir):
        """Test performance differences between formats."""
        formats_data = {
            'txt': ('plain text ' * 1000, 'w'),
            'json': (json.dumps({"data": ["item"] * 1000}, indent=2), 'w'),
            'xml': (f'<root>{"<item>data</item>" * 1000}</root>', 'w'),
            'csv': (None, 'csv'),  # Special handling
        }
        
        results = {}
        processor = DocumentProcessor()
        
        for fmt, (content, mode) in formats_data.items():
            file_path = temp_dir / f"test.{fmt}"
            
            if mode == 'csv':
                # Create CSV file
                with file_path.open('w', newline='') as f:
                    writer = csv.writer(f)
                    for i in range(1000):
                        writer.writerow([f'col{j}' for j in range(10)])
            else:
                file_path.write_text(content)
                
            # Measure processing time
            start_time = time.time()
            doc = processor.process_file(file_path)
            duration = time.time() - start_time
            
            results[fmt] = {
                'duration': duration,
                'file_size_kb': file_path.stat().st_size / 1024,
                'chunks': len(doc.chunks),
                'kb_per_second': (file_path.stat().st_size / 1024) / duration
            }
            
            logger.info(f"Format {fmt}: {results[fmt]}")
            
        # Compare performance
        # Plain text should generally be fastest
        assert results['txt']['kb_per_second'] >= min(r['kb_per_second'] for r in results.values())
        
    @pytest.mark.skip(reason="Benchmark plots not implemented")
    def test_generate_performance_plots(self, temp_dir, benchmark_files):
        """Generate performance visualization plots."""
        # This would create performance charts
        # Skipped by default to avoid matplotlib dependency
        pass


class TestMemoryLeaks:
    """Test for memory leaks during processing."""
    
    def test_repeated_processing_memory(self, tmp_path):
        """Test memory stability during repeated processing."""
        # Create test file
        test_file = tmp_path / "memory_test.txt"
        test_file.write_text("Test content for memory leak detection\n" * 1000)
        
        processor = DocumentProcessor()
        
        # Get baseline memory
        import gc
        gc.collect()
        baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        memory_samples = []
        
        # Process file many times
        for i in range(50):
            doc = processor.process_file(test_file)
            
            # Force garbage collection
            del doc
            gc.collect()
            
            # Sample memory every 10 iterations
            if i % 10 == 0:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
                
        # Check for memory leak
        memory_increase = memory_samples[-1] - baseline_memory
        
        # Should not continuously increase
        assert memory_increase < 50, f"Possible memory leak: {memory_increase} MB increase"
        
        # Check trend - later samples shouldn't be much higher than earlier ones
        first_half_avg = sum(memory_samples[:len(memory_samples)//2]) / (len(memory_samples)//2)
        second_half_avg = sum(memory_samples[len(memory_samples)//2:]) / (len(memory_samples)//2)
        
        assert second_half_avg - first_half_avg < 20, "Memory appears to be growing over time"


if __name__ == "__main__":
    # Run with: pytest test_performance_benchmarks.py -v -m "not slow"
    # Run slow tests: pytest test_performance_benchmarks.py -v -m slow
    # Run with plots: pytest test_performance_benchmarks.py -v --benchmark-plots
    pytest.main([__file__, "-v"])