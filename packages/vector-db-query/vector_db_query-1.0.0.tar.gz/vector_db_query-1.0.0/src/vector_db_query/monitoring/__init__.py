"""
Ansera Monitoring Module

Provides comprehensive monitoring capabilities for the Ansera Vector DB Query System.

Components:
- SystemMonitor: System resource monitoring (CPU, memory, disk)
- QueueMonitor: Document processing queue tracking
- ProcessController: Service control operations
- Dashboard: Streamlit-based web UI

Usage:
    from vector_db_query.monitoring import SystemMonitor, QueueMonitor, run_dashboard
    
    # Get system metrics
    monitor = SystemMonitor()
    stats = monitor.get_quick_stats()
    
    # Check queue status
    queue = QueueMonitor()
    metrics = queue.get_queue_metrics()
    
    # Run dashboard
    run_dashboard()
"""

from .metrics import SystemMonitor
from .process_manager import QueueMonitor
from .controls import ProcessController, get_controller
from .dashboard import run_dashboard
from . import widgets
from . import security
from . import audit

__all__ = [
    'SystemMonitor',
    'QueueMonitor',
    'ProcessController',
    'get_controller',
    'run_dashboard',
    'widgets',
    'security',
    'audit'
]

__version__ = '1.0.0'