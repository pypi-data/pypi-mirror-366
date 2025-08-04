"""
Entry point for running the monitoring dashboard with proper module imports.

This file serves as a bridge to run the dashboard module with streamlit
while maintaining proper Python module structure for imports.
"""

import sys
import os

# Add the src directory to Python path so imports work correctly
src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import and run the dashboard
from vector_db_query.monitoring.dashboard import run_dashboard

if __name__ == "__main__":
    run_dashboard()