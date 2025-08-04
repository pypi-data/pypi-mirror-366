"""
Test configuration for Ansera monitoring system tests.

This module provides common test utilities and configurations.
"""

import os
import tempfile
from pathlib import Path


class TestConfig:
    """Common test configuration."""
    
    # Test timeouts
    DEFAULT_TIMEOUT = 5
    LONG_TIMEOUT = 30
    
    # Mock data
    MOCK_QDRANT_URL = "http://localhost:6333"
    MOCK_DOCKER_CONTAINER = "qdrant-test"
    
    # Sample job data
    SAMPLE_JOBS = [
        {
            "job_id": "job_20240101_120000_1234",
            "document_path": "/test/doc1.pdf",
            "status": "pending"
        },
        {
            "job_id": "job_20240101_120100_5678",
            "document_path": "/test/doc2.pdf",
            "status": "processing",
            "started_at": "2024-01-01T12:01:00"
        },
        {
            "job_id": "job_20240101_120200_9999",
            "document_path": "/test/doc3.pdf",
            "status": "completed",
            "started_at": "2024-01-01T12:02:00",
            "completed_at": "2024-01-01T12:02:30"
        }
    ]
    
    @staticmethod
    def create_temp_dir():
        """Create a temporary directory for testing."""
        return tempfile.mkdtemp(prefix="ansera_test_")
    
    @staticmethod
    def create_test_log_files(log_dir: Path, count: int = 3):
        """Create test log files."""
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_files = []
        for i in range(count):
            log_file = log_dir / f"test_{i}.log"
            log_file.write_text(f"Test log entry {i}\n" * 10)
            log_files.append(log_file)
        
        return log_files
    
    @staticmethod
    def mock_system_metrics():
        """Return mock system metrics."""
        return {
            "cpu_percent": 45.5,
            "memory_percent": 60.0,
            "memory_used_gb": 8.0,
            "memory_total_gb": 16.0,
            "disk_percent": 25.0,
            "disk_used_gb": 125.0,
            "disk_total_gb": 500.0,
            "process_count": 150
        }
    
    @staticmethod
    def mock_pm2_process():
        """Return mock PM2 process data."""
        return {
            "name": "ansera-test-service",
            "pm_id": 0,
            "pm2_env": {
                "status": "online",
                "pm_uptime": 3600000,
                "restart_time": 0
            },
            "monit": {
                "cpu": 10.5,
                "memory": 52428800  # 50MB
            },
            "pid": 12345
        }


# Test fixtures
def setup_test_environment():
    """Set up test environment variables."""
    os.environ["ANSERA_TEST_MODE"] = "true"
    os.environ["QDRANT_URL"] = TestConfig.MOCK_QDRANT_URL


def teardown_test_environment():
    """Clean up test environment."""
    if "ANSERA_TEST_MODE" in os.environ:
        del os.environ["ANSERA_TEST_MODE"]
    if "QDRANT_URL" in os.environ:
        del os.environ["QDRANT_URL"]