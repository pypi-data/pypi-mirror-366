"""Performance tests for data sources system."""

import asyncio
import time
import random
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import pytest
import psutil
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import memory_profiler

from vector_db_query.data_sources.orchestrator import DataSourceOrchestrator
from vector_db_query.data_sources.models import SourceType, ProcessingResult
from vector_db_query.data_sources.gmail import GmailDataSource, GmailConfig
from vector_db_query.data_sources.fireflies import FirefliesDataSource, FirefliesConfig
from vector_db_query.data_sources.googledrive import GoogleDriveDataSource, GoogleDriveConfig
from vector_db_query.utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceMetrics:
    """Track performance metrics during tests."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.processing_times = []
        self.memory_usage = []
        self.cpu_usage = []
        self.items_processed = 0
        self.errors = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
    def start(self):
        """Start tracking metrics."""
        self.start_time = time.time()
        self.initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
    def record_item(self, processing_time: float, error: bool = False):
        """Record processing of an item."""
        self.processing_times.append(processing_time)
        self.items_processed += 1
        if error:
            self.errors += 1
            
        # Record resource usage
        process = psutil.Process()
        self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(process.cpu_percent(interval=0.1))
        
    def stop(self):
        """Stop tracking and calculate final metrics."""
        self.end_time = time.time()
        
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        duration = self.end_time - self.start_time if self.end_time else 0
        
        return {
            'duration_seconds': duration,
            'items_processed': self.items_processed,
            'items_per_second': self.items_processed / duration if duration > 0 else 0,
            'errors': self.errors,
            'error_rate': self.errors / self.items_processed if self.items_processed > 0 else 0,
            'processing_times': {
                'mean': statistics.mean(self.processing_times) if self.processing_times else 0,
                'median': statistics.median(self.processing_times) if self.processing_times else 0,
                'min': min(self.processing_times) if self.processing_times else 0,
                'max': max(self.processing_times) if self.processing_times else 0,
                'p95': np.percentile(self.processing_times, 95) if self.processing_times else 0,
                'p99': np.percentile(self.processing_times, 99) if self.processing_times else 0,
            },
            'memory': {
                'peak_mb': max(self.memory_usage) if self.memory_usage else 0,
                'average_mb': statistics.mean(self.memory_usage) if self.memory_usage else 0,
                'growth_mb': (max(self.memory_usage) - min(self.memory_usage)) if self.memory_usage else 0,
            },
            'cpu': {
                'peak_percent': max(self.cpu_usage) if self.cpu_usage else 0,
                'average_percent': statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
            },
            'cache': {
                'hits': self.cache_hits,
                'misses': self.cache_misses,
                'hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
            }
        }


def generate_test_email(index: int) -> Dict[str, Any]:
    """Generate a test email."""
    subjects = [
        "Meeting notes for project update",
        "Action items from today's standup",
        "Quarterly financial report attached",
        "Customer feedback summary",
        "Technical architecture proposal",
        "Sprint retrospective notes",
        "Product roadmap discussion",
        "Security audit findings",
    ]
    
    senders = [
        "john.doe@example.com",
        "jane.smith@example.com",
        "mike.wilson@example.com",
        "sarah.jones@example.com",
        "tom.brown@example.com",
    ]
    
    body_length = random.randint(500, 5000)
    body = f"This is test email {index}. " + "Lorem ipsum dolor sit amet. " * (body_length // 30)
    
    return {
        'id': f'test_email_{index}',
        'subject': random.choice(subjects),
        'from': random.choice(senders),
        'to': ["test@example.com"],
        'date': datetime.now() - timedelta(days=random.randint(0, 30)),
        'body': body,
        'labels': random.sample(['INBOX', 'IMPORTANT', 'CATEGORY_UPDATES', 'STARRED'], k=random.randint(1, 3)),
        'attachments': [f"attachment_{i}.pdf" for i in range(random.randint(0, 3))],
    }


def generate_test_transcript(index: int) -> Dict[str, Any]:
    """Generate a test meeting transcript."""
    titles = [
        "Weekly Team Sync",
        "Project Planning Session",
        "Customer Review Meeting",
        "Technical Deep Dive",
        "Sprint Planning",
        "Architecture Review",
    ]
    
    duration = random.randint(1800, 7200)  # 30 min to 2 hours
    speakers = random.randint(2, 8)
    
    transcript_lines = []
    for i in range(random.randint(50, 200)):
        speaker = f"Speaker {random.randint(1, speakers)}"
        text = f"This is line {i} of the transcript. " + "Discussion point. " * random.randint(1, 5)
        transcript_lines.append(f"{speaker}: {text}")
    
    return {
        'id': f'test_transcript_{index}',
        'title': random.choice(titles),
        'date': datetime.now() - timedelta(days=random.randint(0, 30)),
        'duration': duration,
        'attendees': [f"person{i}@example.com" for i in range(speakers)],
        'transcript': '\n'.join(transcript_lines),
        'summary': "Meeting summary: " + "Key point discussed. " * random.randint(3, 6),
        'platform': random.choice(['zoom', 'teams', 'meet']),
    }


def generate_test_document(index: int) -> Dict[str, Any]:
    """Generate a test Google Drive document."""
    names = [
        "Notes by Gemini - Project Status",
        "Notes by Gemini - Customer Meeting",
        "Meeting Notes - Q3 Planning",
        "Technical Documentation",
        "Product Specifications",
    ]
    
    content_length = random.randint(1000, 10000)
    content = f"Document {index} content. " + "Important information. " * (content_length // 20)
    
    return {
        'id': f'test_doc_{index}',
        'name': random.choice(names),
        'mimeType': 'application/vnd.google-apps.document',
        'createdTime': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat() + 'Z',
        'modifiedTime': (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat() + 'Z',
        'content': content,
        'owners': [{'emailAddress': 'owner@example.com'}],
        'size': str(len(content)),
    }


class TestDataSourcePerformance:
    """Performance test suite for data sources."""
    
    @pytest.mark.performance
    async def test_orchestrator_throughput(self):
        """Test orchestrator throughput with 500+ items."""
        metrics = PerformanceMetrics()
        orchestrator = DataSourceOrchestrator()
        
        # Generate test data
        num_items = 500
        test_emails = [generate_test_email(i) for i in range(num_items // 3)]
        test_transcripts = [generate_test_transcript(i) for i in range(num_items // 3)]
        test_documents = [generate_test_document(i) for i in range(num_items // 3 + 1)]
        
        # Mock data sources
        class MockGmailSource:
            async def fetch_emails(self, *args, **kwargs):
                return test_emails
                
            async def process_email(self, email):
                await asyncio.sleep(random.uniform(0.01, 0.05))  # Simulate processing
                return ProcessingResult(
                    success=random.random() > 0.05,  # 95% success rate
                    source_type=SourceType.GMAIL,
                    item_id=email['id'],
                    content=email['body'],
                    metadata={'subject': email['subject']}
                )
        
        class MockFirefliesSource:
            async def fetch_transcripts(self, *args, **kwargs):
                return test_transcripts
                
            async def process_transcript(self, transcript):
                await asyncio.sleep(random.uniform(0.02, 0.08))  # Simulate processing
                return ProcessingResult(
                    success=random.random() > 0.05,
                    source_type=SourceType.FIREFLIES,
                    item_id=transcript['id'],
                    content=transcript['transcript'],
                    metadata={'title': transcript['title']}
                )
        
        class MockGoogleDriveSource:
            async def search_files(self, *args, **kwargs):
                return test_documents
                
            async def process_file(self, file):
                await asyncio.sleep(random.uniform(0.01, 0.06))  # Simulate processing
                return ProcessingResult(
                    success=random.random() > 0.05,
                    source_type=SourceType.GOOGLE_DRIVE,
                    item_id=file['id'],
                    content=file['content'],
                    metadata={'name': file['name']}
                )
        
        # Register mock sources
        orchestrator.sources[SourceType.GMAIL] = MockGmailSource()
        orchestrator.sources[SourceType.FIREFLIES] = MockFirefliesSource()
        orchestrator.sources[SourceType.GOOGLE_DRIVE] = MockGoogleDriveSource()
        
        # Run performance test
        metrics.start()
        
        start_time = time.time()
        results = await orchestrator.sync_all(parallel=True)
        end_time = time.time()
        
        metrics.stop()
        
        # Analyze results
        total_processed = sum(len(r) for r in results.values())
        duration = end_time - start_time
        throughput = total_processed / duration
        
        logger.info(f"Processed {total_processed} items in {duration:.2f} seconds")
        logger.info(f"Throughput: {throughput:.2f} items/second")
        
        # Assert performance targets
        assert throughput >= 10, f"Throughput too low: {throughput:.2f} items/second"
        assert duration < 60, f"Processing took too long: {duration:.2f} seconds"
        
        summary = metrics.get_summary()
        logger.info(f"Performance summary: {summary}")
        
        # Check resource usage
        assert summary['memory']['growth_mb'] < 500, "Memory usage grew too much"
        assert summary['cpu']['average_percent'] < 80, "CPU usage too high"
    
    @pytest.mark.performance
    async def test_concurrent_processing(self):
        """Test concurrent processing capabilities."""
        metrics = PerformanceMetrics()
        
        # Test different concurrency levels
        concurrency_levels = [1, 5, 10, 20, 50]
        results = {}
        
        for level in concurrency_levels:
            items = [generate_test_email(i) for i in range(100)]
            
            async def process_item(item):
                start = time.time()
                await asyncio.sleep(random.uniform(0.01, 0.05))  # Simulate work
                duration = time.time() - start
                return duration
            
            # Process with different concurrency
            start_time = time.time()
            
            if level == 1:
                # Sequential processing
                durations = []
                for item in items:
                    durations.append(await process_item(item))
            else:
                # Concurrent processing
                semaphore = asyncio.Semaphore(level)
                
                async def process_with_limit(item):
                    async with semaphore:
                        return await process_item(item)
                
                tasks = [process_with_limit(item) for item in items]
                durations = await asyncio.gather(*tasks)
            
            total_time = time.time() - start_time
            
            results[level] = {
                'total_time': total_time,
                'items_per_second': len(items) / total_time,
                'average_duration': statistics.mean(durations),
            }
            
            logger.info(f"Concurrency {level}: {len(items)} items in {total_time:.2f}s ({results[level]['items_per_second']:.2f} items/s)")
        
        # Verify performance improvements with concurrency
        assert results[10]['items_per_second'] > results[1]['items_per_second'] * 5, "Concurrency not providing expected speedup"
        assert results[20]['items_per_second'] > results[10]['items_per_second'], "Higher concurrency should improve throughput"
    
    @pytest.mark.performance
    @pytest.mark.memory
    def test_memory_efficiency(self):
        """Test memory efficiency with large batches."""
        import tracemalloc
        
        tracemalloc.start()
        
        # Generate large dataset
        large_emails = []
        for i in range(1000):
            email = generate_test_email(i)
            # Make some emails very large
            if i % 10 == 0:
                email['body'] = email['body'] * 100  # 100x larger
            large_emails.append(email)
        
        # Take snapshot before processing
        snapshot1 = tracemalloc.take_snapshot()
        
        # Process in batches
        batch_size = 50
        processed = []
        
        for i in range(0, len(large_emails), batch_size):
            batch = large_emails[i:i + batch_size]
            
            # Simulate processing
            for email in batch:
                processed_email = {
                    'id': email['id'],
                    'hash': hash(email['body']),
                    'size': len(email['body']),
                }
                processed.append(processed_email)
            
            # Clear batch to free memory
            batch.clear()
        
        # Take snapshot after processing
        snapshot2 = tracemalloc.take_snapshot()
        
        # Analyze memory usage
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        total_diff = sum(stat.size_diff for stat in top_stats)
        
        logger.info(f"Memory difference: {total_diff / 1024 / 1024:.2f} MB")
        
        # Memory should not grow excessively
        assert total_diff / 1024 / 1024 < 100, "Memory usage grew too much during processing"
        
        tracemalloc.stop()
    
    @pytest.mark.performance
    async def test_deduplication_performance(self):
        """Test deduplication performance with many duplicates."""
        from vector_db_query.data_sources.deduplication import DeduplicationService
        
        dedup_service = DeduplicationService(similarity_threshold=0.95)
        metrics = PerformanceMetrics()
        
        # Generate items with duplicates
        unique_items = 100
        duplicate_factor = 5  # Each item appears 5 times on average
        total_items = unique_items * duplicate_factor
        
        items = []
        for i in range(unique_items):
            base_email = generate_test_email(i)
            
            # Add original
            items.append(base_email)
            
            # Add near-duplicates
            for j in range(duplicate_factor - 1):
                duplicate = base_email.copy()
                duplicate['id'] = f"{base_email['id']}_dup_{j}"
                # Slightly modify content
                duplicate['body'] = duplicate['body'] + f" (variation {j})"
                items.append(duplicate)
        
        random.shuffle(items)
        
        # Test deduplication performance
        metrics.start()
        
        unique_items_found = []
        duplicate_items_found = []
        
        for item in items:
            start_time = time.time()
            
            is_duplicate = await dedup_service.is_duplicate(
                content=item['body'],
                source_type=SourceType.GMAIL,
                metadata={'subject': item['subject']}
            )
            
            processing_time = time.time() - start_time
            metrics.record_item(processing_time)
            
            if is_duplicate:
                duplicate_items_found.append(item)
                metrics.cache_hits += 1
            else:
                unique_items_found.append(item)
                metrics.cache_misses += 1
                # Add to dedup cache
                await dedup_service.add_item(
                    content=item['body'],
                    source_type=SourceType.GMAIL,
                    item_id=item['id'],
                    metadata={'subject': item['subject']}
                )
        
        metrics.stop()
        
        summary = metrics.get_summary()
        logger.info(f"Deduplication performance: {summary}")
        
        # Verify deduplication effectiveness
        dedup_rate = len(duplicate_items_found) / total_items
        expected_dedup_rate = (duplicate_factor - 1) / duplicate_factor
        
        assert abs(dedup_rate - expected_dedup_rate) < 0.1, f"Deduplication rate {dedup_rate:.2f} far from expected {expected_dedup_rate:.2f}"
        assert summary['processing_times']['mean'] < 0.01, "Deduplication too slow"
        assert summary['cache']['hit_rate'] > 0.7, "Cache hit rate too low"
    
    @pytest.mark.performance
    async def test_nlp_processing_performance(self):
        """Test NLP processing performance."""
        from vector_db_query.data_sources.nlp_extraction import NLPExtractor
        
        nlp_extractor = NLPExtractor()
        metrics = PerformanceMetrics()
        
        # Generate test documents of varying sizes
        documents = []
        for i in range(50):
            size_category = i % 5
            if size_category == 0:
                # Short document
                content = "Short document. " * random.randint(10, 50)
            elif size_category < 3:
                # Medium document
                content = "Medium length document with more content. " * random.randint(50, 200)
            else:
                # Long document
                content = "This is a long document with substantial content for analysis. " * random.randint(200, 500)
            
            documents.append({
                'id': f'doc_{i}',
                'content': content,
            })
        
        # Test NLP processing
        metrics.start()
        
        for doc in documents:
            start_time = time.time()
            
            # Extract entities
            entities = nlp_extractor.extract_entities(doc['content'])
            
            # Analyze sentiment
            sentiment = nlp_extractor.analyze_sentiment(doc['content'])
            
            # Extract key phrases
            key_phrases = nlp_extractor.extract_key_phrases(doc['content'])
            
            processing_time = time.time() - start_time
            metrics.record_item(processing_time)
            
            doc['nlp_results'] = {
                'entities': len(entities),
                'sentiment': sentiment,
                'key_phrases': len(key_phrases),
            }
        
        metrics.stop()
        
        summary = metrics.get_summary()
        logger.info(f"NLP processing performance: {summary}")
        
        # Performance assertions
        assert summary['processing_times']['mean'] < 0.5, "NLP processing too slow on average"
        assert summary['processing_times']['p95'] < 2.0, "NLP processing too slow for large documents"
        assert summary['items_per_second'] > 2, "NLP throughput too low"
    
    @pytest.mark.performance
    @pytest.mark.stress
    async def test_stress_test_500_daily(self):
        """Stress test with 500+ items as per requirements."""
        orchestrator = DataSourceOrchestrator()
        metrics = PerformanceMetrics()
        
        # Generate 500+ items distributed across sources
        num_items = 550  # Slightly more than 500 to stress test
        distribution = {
            SourceType.GMAIL: int(num_items * 0.5),      # 275 emails
            SourceType.FIREFLIES: int(num_items * 0.3),  # 165 transcripts
            SourceType.GOOGLE_DRIVE: int(num_items * 0.2), # 110 documents
        }
        
        # Generate test data
        test_data = {
            SourceType.GMAIL: [generate_test_email(i) for i in range(distribution[SourceType.GMAIL])],
            SourceType.FIREFLIES: [generate_test_transcript(i) for i in range(distribution[SourceType.FIREFLIES])],
            SourceType.GOOGLE_DRIVE: [generate_test_document(i) for i in range(distribution[SourceType.GOOGLE_DRIVE])],
        }
        
        # Mock sources that return test data
        for source_type in SourceType:
            class MockSource:
                def __init__(self, data):
                    self.data = data
                    self.processed = 0
                    
                async def sync(self, *args, **kwargs):
                    results = []
                    for item in self.data:
                        # Simulate processing with realistic delays
                        await asyncio.sleep(random.uniform(0.01, 0.1))
                        self.processed += 1
                        
                        # Simulate occasional errors
                        if random.random() < 0.02:  # 2% error rate
                            continue
                            
                        results.append(ProcessingResult(
                            success=True,
                            source_type=source_type,
                            item_id=item['id'],
                            content=item.get('body', item.get('transcript', item.get('content', ''))),
                            metadata={}
                        ))
                    return results
            
            if source_type in test_data:
                orchestrator.sources[source_type] = MockSource(test_data[source_type])
        
        # Run stress test
        logger.info(f"Starting stress test with {num_items} items...")
        metrics.start()
        
        start_time = time.time()
        
        # Process all items
        results = await orchestrator.sync_all(parallel=True)
        
        end_time = time.time()
        metrics.stop()
        
        # Calculate results
        total_processed = sum(len(r) for r in results.values())
        duration = end_time - start_time
        throughput = total_processed / duration if duration > 0 else 0
        
        # Generate performance report
        report = {
            'total_items': num_items,
            'total_processed': total_processed,
            'duration_seconds': duration,
            'throughput_items_per_second': throughput,
            'estimated_daily_capacity': throughput * 86400,  # Items per day
            'success_rate': total_processed / num_items if num_items > 0 else 0,
            'metrics': metrics.get_summary(),
        }
        
        logger.info(f"Stress test results:")
        logger.info(f"  - Processed: {total_processed}/{num_items} items")
        logger.info(f"  - Duration: {duration:.2f} seconds")
        logger.info(f"  - Throughput: {throughput:.2f} items/second")
        logger.info(f"  - Daily capacity: {report['estimated_daily_capacity']:.0f} items/day")
        logger.info(f"  - Success rate: {report['success_rate']:.2%}")
        
        # Performance requirements
        assert total_processed >= num_items * 0.95, f"Processed only {total_processed}/{num_items} items"
        assert duration < 300, f"Processing took {duration:.2f}s, should be under 5 minutes"
        assert throughput >= 2, f"Throughput {throughput:.2f} items/s is too low"
        assert report['estimated_daily_capacity'] >= 172800, "System cannot handle 500+ items daily"
        
        # Resource constraints
        assert report['metrics']['memory']['peak_mb'] < 2048, "Memory usage too high"
        assert report['metrics']['cpu']['average_percent'] < 70, "CPU usage too high"
        
        return report


if __name__ == "__main__":
    # Run performance tests
    asyncio.run(test_stress_test_500_daily())