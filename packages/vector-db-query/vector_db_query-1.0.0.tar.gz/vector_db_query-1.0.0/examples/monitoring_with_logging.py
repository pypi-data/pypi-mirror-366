#!/usr/bin/env python3
"""
Example: Using Ansera Monitoring with Integrated Logging

This example demonstrates how to use the monitoring system with
comprehensive logging for full visibility and traceability.
"""

import time
from pathlib import Path

# Import monitoring components
from vector_db_query.monitoring.metrics import SystemMonitor
from vector_db_query.monitoring.process_manager import QueueMonitor
from vector_db_query.monitoring.controls import ProcessController
from vector_db_query.monitoring.logging import get_monitoring_logger
from vector_db_query.monitoring.logging_integration import (
    with_activity_logging,
    with_metrics_logging,
    with_queue_logging,
    log_metric_collection,
    log_queue_operation
)


def example_basic_logging():
    """Example of basic logging functionality."""
    print("=== Basic Logging Example ===\n")
    
    # Get logger instance
    logger = get_monitoring_logger()
    
    # Log activities
    logger.log_activity("ExampleScript", "startup", "Starting monitoring example")
    
    # Create a snapshot before operations
    snapshot_dir = logger.create_snapshot(
        "pre-monitoring",
        "example",
        "Snapshot before monitoring operations"
    )
    print(f"Created snapshot: {snapshot_dir}")
    
    # Simulate some monitoring
    monitor = SystemMonitor()
    metrics = monitor.get_quick_stats()
    
    # Log the metrics
    logger.log_metrics(metrics)
    logger.log_activity("ExampleScript", "metrics", f"Collected system metrics: CPU={metrics['cpu']}%")
    
    # Log completion
    logger.log_activity("ExampleScript", "complete", "Example completed successfully")
    
    print("\n✅ Basic logging example completed")


def example_queue_monitoring_with_logging():
    """Example of queue monitoring with integrated logging."""
    print("\n=== Queue Monitoring with Logging ===\n")
    
    logger = get_monitoring_logger()
    queue = QueueMonitor()
    
    # Log pre-change state
    pre_log = logger.log_pre_change(
        "QueueExample",
        "queue_processing",
        "Adding test documents to queue"
    )
    
    try:
        # Add documents to queue
        job_ids = []
        for i in range(3):
            job_id = queue.add_to_queue(f"/test/document_{i}.pdf")
            job_ids.append(job_id)
            
            # Log queue event
            logger.log_queue_event(
                "document_added",
                job_id,
                {"document": f"document_{i}.pdf", "index": i}
            )
            print(f"Added document_{i}.pdf to queue: {job_id}")
        
        # Process documents
        for job_id in job_ids:
            # Start processing
            queue.start_processing(job_id)
            logger.log_queue_event("processing_started", job_id, {})
            
            # Simulate processing
            time.sleep(0.5)
            
            # Complete processing
            queue.complete_processing(job_id, success=True)
            logger.log_queue_event("processing_completed", job_id, {"success": True})
            
            print(f"Processed: {job_id}")
        
        # Get final metrics
        metrics = queue.get_queue_metrics()
        logger.log_metrics({"queue_metrics": metrics})
        
        # Log successful completion
        logger.log_post_change(
            pre_log,
            "QueueExample",
            "queue_processing",
            "SUCCESS",
            {"jobs_processed": len(job_ids), "final_metrics": metrics}
        )
        
        print(f"\n✅ Processed {len(job_ids)} documents")
        print(f"Queue status: {metrics['queue_health']}")
        
    except Exception as e:
        # Log failure
        logger.log_post_change(
            pre_log,
            "QueueExample",
            "queue_processing",
            "FAILURE",
            {"error": str(e)}
        )
        logger.log_error("QueueExample", "processing_error", str(e))
        raise


def example_process_monitoring_with_logging():
    """Example of process monitoring with logging."""
    print("\n=== Process Monitoring with Logging ===\n")
    
    logger = get_monitoring_logger()
    controller = ProcessController()
    
    # Get service status
    status = controller.get_service_status()
    
    # Log process status
    for service, info in status.items():
        if service != "timestamp":
            logger.log_process_event(
                service,
                "status_check",
                pid=info.get("pid"),
                details=info
            )
    
    print("Service Status:")
    print(f"  MCP Server: {status['mcp_server']['status']}")
    print(f"  Qdrant: {status['qdrant']['status']}")
    
    # Simulate PM2 operations (if available)
    pm2_status = controller.get_pm2_status()
    if pm2_status.get('pm2_available'):
        print(f"\nPM2 is managing {pm2_status['total_count']} services")
        
        # Log PM2 process info
        for proc in pm2_status.get('processes', []):
            logger.log_process_event(
                proc['name'],
                "pm2_status",
                pid=proc.get('pid'),
                details={
                    'status': proc['status'],
                    'cpu': proc['cpu'],
                    'memory': proc['memory'],
                    'uptime': proc['uptime']
                }
            )


def example_error_handling_with_logging():
    """Example of error handling and logging."""
    print("\n=== Error Handling Example ===\n")
    
    logger = get_monitoring_logger()
    
    try:
        # Simulate an error scenario
        raise ValueError("Simulated monitoring error for demonstration")
        
    except Exception as e:
        # Log the error with full context
        logger.log_error(
            "ErrorExample",
            "simulated_error",
            str(e)
        )
        print(f"❌ Error logged: {e}")
    
    # Check error logs
    from datetime import datetime
    date_str = datetime.now().strftime("%Y%m%d")
    error_log = logger.monitoring_logs_dir / "errors" / f"{date_str}.log"
    
    if error_log.exists():
        print(f"\n📋 Error log created: {error_log}")


def example_reporting():
    """Example of generating monitoring reports."""
    print("\n=== Reporting Example ===\n")
    
    logger = get_monitoring_logger()
    
    # Generate daily report
    report_path = logger.generate_daily_report()
    print(f"📊 Generated report: {report_path}")
    
    # Read and display report summary
    if Path(report_path).exists():
        with open(report_path, 'r') as f:
            lines = f.readlines()[:10]  # First 10 lines
            print("\nReport Preview:")
            print("-" * 40)
            for line in lines:
                print(line.rstrip())
            print("...")


def example_with_decorators():
    """Example using logging decorators."""
    print("\n=== Decorator Example ===\n")
    
    class MonitoringService:
        @with_activity_logging("data_collection")
        def collect_metrics(self):
            """Collect system metrics with automatic logging."""
            monitor = SystemMonitor()
            return monitor.get_quick_stats()
        
        @with_queue_logging("job_processing")
        def process_job(self, job_id):
            """Process a job with automatic queue logging."""
            print(f"Processing job: {job_id}")
            time.sleep(0.2)
            return {"status": "completed", "job_id": job_id}
    
    # Use the decorated methods
    service = MonitoringService()
    
    # This will automatically log the activity
    metrics = service.collect_metrics()
    print(f"Collected metrics: CPU={metrics['cpu']}%")
    
    # This will automatically log queue events
    result = service.process_job("test-job-123")
    print(f"Job result: {result}")


def main():
    """Run all examples."""
    print("🚀 Ansera Monitoring with Logging Examples\n")
    
    # Initialize logging system
    logger = get_monitoring_logger()
    logger.log_activity("Examples", "start", "Starting monitoring examples")
    
    try:
        # Run examples
        example_basic_logging()
        example_queue_monitoring_with_logging()
        example_process_monitoring_with_logging()
        example_error_handling_with_logging()
        example_reporting()
        example_with_decorators()
        
        # Create final snapshot
        logger.create_snapshot(
            "examples-complete",
            "examples",
            "All monitoring examples completed"
        )
        
        print("\n✅ All examples completed successfully!")
        print("\nView logs with: vdq logging view")
        print("Check status with: vdq logging status")
        
    except Exception as e:
        logger.log_error("Examples", "execution_error", str(e))
        print(f"\n❌ Error during examples: {e}")
        raise


if __name__ == "__main__":
    main()