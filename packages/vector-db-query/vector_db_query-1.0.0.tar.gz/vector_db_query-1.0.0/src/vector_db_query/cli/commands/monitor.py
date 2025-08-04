"""
Monitoring dashboard command for Ansera CLI.

This command launches the monitoring dashboard for viewing
system metrics, process status, and queue information.
"""

import click
import subprocess
import sys
from pathlib import Path


@click.command()
@click.option(
    '--port',
    default=8501,
    help='Port to run the dashboard on (default: 8501)'
)
@click.option(
    '--host',
    default='localhost',
    help='Host to bind the dashboard to (default: localhost)'
)
@click.option(
    '--browser/--no-browser',
    default=True,
    help='Open browser automatically (default: True)'
)
def monitor(port: int, host: str, browser: bool):
    """Launch the Ansera monitoring dashboard.
    
    This starts a Streamlit web server with the monitoring dashboard
    that shows system metrics, process status, and queue information.
    
    Examples:
        vdq monitor
        vdq monitor --port 8080
        vdq monitor --no-browser --host 0.0.0.0
    """
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        click.echo("❌ Error: Streamlit is not installed!", err=True)
        click.echo("\nStreamlit is required for the monitoring dashboard.")
        click.echo("Please install it using one of the following commands:\n")
        click.echo("  Using pip:")
        click.echo("    pip install streamlit\n")
        click.echo("  Using conda:")
        click.echo("    conda install -c conda-forge streamlit\n")
        click.echo("  Or install all monitoring dependencies:")
        click.echo("    pip install vector-db-query[monitoring]")
        click.echo("\n  For zsh users (if you get 'no matches found'):")
        click.echo("    pip install \"vector-db-query[monitoring]\"")
        click.echo("    # or")
        click.echo("    pip install vector-db-query\\[monitoring\\]")
        sys.exit(1)
    
    click.echo("🚀 Starting Ansera Monitoring Dashboard...")
    
    # Get the dashboard runner module path
    dashboard_path = Path(__file__).parent.parent.parent / "monitoring" / "run_dashboard.py"
    
    if not dashboard_path.exists():
        click.echo(f"❌ Dashboard module not found at {dashboard_path}", err=True)
        click.echo("\nCreating a basic dashboard module...")
        # Create the monitoring directory if it doesn't exist
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        # We'll create the dashboard module next
        sys.exit(1)
    
    # Build streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path),
        "--server.port", str(port),
        "--server.address", host,
        "--browser.gatherUsageStats", "false"
    ]
    
    if not browser:
        cmd.extend(["--server.headless", "true"])
    
    click.echo(f"📊 Dashboard will be available at http://{host}:{port}")
    
    try:
        # Run streamlit
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            click.echo(f"❌ Dashboard exited with code {result.returncode}", err=True)
    except KeyboardInterrupt:
        click.echo("\n👋 Dashboard stopped.")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error running streamlit: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error starting dashboard: {e}", err=True)
        sys.exit(1)
