"""
Logging command for Ansera CLI.

This command provides access to the monitoring logging system,
allowing users to view logs, generate reports, and manage logging.
"""

import click
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ...monitoring.logging import get_monitoring_logger


@click.group()
def logging():
    """Manage Ansera monitoring logs."""
    pass


@logging.command()
def init():
    """Initialize the logging system."""
    logger = get_monitoring_logger()
    click.echo("🔧 Initializing Ansera logging system...")
    
    # Create snapshot of initial state
    snapshot_dir = logger.create_snapshot(
        "initialization",
        "logging-init",
        "Initial logging system setup"
    )
    
    click.echo("✅ Logging system initialized")
    click.echo(f"📁 Logs directory: {logger.logs_dir}")
    click.echo(f"📸 Initial snapshot: {snapshot_dir}")


@logging.command()
@click.option('--lines', '-n', default=20, help='Number of lines to show')
@click.option('--component', '-c', help='Filter by component')
@click.option('--date', '-d', help='Date in YYYYMMDD format (default: today)')
def view(lines: int, component: Optional[str], date: Optional[str]):
    """View recent monitoring logs."""
    logger = get_monitoring_logger()
    
    if not date:
        date = datetime.now().strftime("%Y%m%d")
    
    click.echo(f"📋 Monitoring Logs - {date}")
    click.echo("=" * 60)
    
    if component:
        # Component-specific logs
        log_file = logger.monitoring_logs_dir / "activities" / component / f"{date}.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    click.echo(line.rstrip())
        else:
            click.echo(f"No logs found for component '{component}' on {date}")
    else:
        # All activities
        log_file = logger.monitoring_logs_dir / "activities" / f"{date}.log"
        if log_file.exists():
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    click.echo(line.rstrip())
        else:
            click.echo(f"No activity logs found for {date}")


@logging.command()
@click.argument('search_term')
@click.option('--days', '-d', default=7, help='Number of days to search')
def search(search_term: str, days: int):
    """Search logs for specific terms."""
    logger = get_monitoring_logger()
    
    click.echo(f"🔍 Searching for '{search_term}' in last {days} days...")
    click.echo("=" * 60)
    
    matches = []
    start_date = datetime.now() - timedelta(days=days)
    
    # Search activity logs
    activities_dir = logger.monitoring_logs_dir / "activities"
    for log_file in activities_dir.glob("*.log"):
        try:
            file_date = datetime.strptime(log_file.stem, "%Y%m%d")
            if file_date >= start_date:
                with open(log_file, 'r') as f:
                    for line_no, line in enumerate(f, 1):
                        if search_term.lower() in line.lower():
                            matches.append({
                                'file': str(log_file),
                                'line': line_no,
                                'content': line.strip()
                            })
        except:
            continue
    
    # Display results
    if matches:
        click.echo(f"Found {len(matches)} matches:\n")
        for match in matches[:50]:  # Limit to 50 results
            click.echo(f"📄 {Path(match['file']).name}:{match['line']}")
            click.echo(f"   {match['content']}")
            click.echo()
    else:
        click.echo("No matches found.")


@logging.command()
@click.option('--date', '-d', help='Date in YYYYMMDD format (default: today)')
def report(date: Optional[str]):
    """Generate daily monitoring report."""
    logger = get_monitoring_logger()
    
    if not date:
        date = datetime.now().strftime("%Y%m%d")
    
    click.echo(f"📊 Generating report for {date}...")
    
    report_path = logger.generate_daily_report(date)
    
    if Path(report_path).exists():
        click.echo(f"✅ Report generated: {report_path}")
        click.echo("\n--- Report Content ---")
        with open(report_path, 'r') as f:
            click.echo(f.read())
    else:
        click.echo("❌ Failed to generate report")


@logging.command()
@click.option('--date', '-d', help='Date in YYYYMMDD format (default: today)')
def metrics(date: Optional[str]):
    """View metrics logs."""
    logger = get_monitoring_logger()
    
    if not date:
        date = datetime.now().strftime("%Y%m%d")
    
    metrics_file = logger.monitoring_logs_dir / "metrics" / f"{date}.jsonl"
    
    if metrics_file.exists():
        click.echo(f"📈 Metrics for {date}")
        click.echo("=" * 60)
        
        cpu_values = []
        memory_values = []
        timestamps = []
        
        with open(metrics_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    metrics = data.get('metrics', {})
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    
                    timestamps.append(timestamp)
                    cpu_values.append(metrics.get('cpu', 0))
                    memory_values.append(metrics.get('memory', {}).get('percent', 0))
                except:
                    continue
        
        if cpu_values:
            click.echo(f"\nCPU Usage:")
            click.echo(f"  Average: {sum(cpu_values)/len(cpu_values):.1f}%")
            click.echo(f"  Min: {min(cpu_values):.1f}%")
            click.echo(f"  Max: {max(cpu_values):.1f}%")
            
            click.echo(f"\nMemory Usage:")
            click.echo(f"  Average: {sum(memory_values)/len(memory_values):.1f}%")
            click.echo(f"  Min: {min(memory_values):.1f}%")
            click.echo(f"  Max: {max(memory_values):.1f}%")
            
            click.echo(f"\nTotal samples: {len(cpu_values)}")
            if timestamps:
                click.echo(f"Time range: {timestamps[0].strftime('%H:%M:%S')} - {timestamps[-1].strftime('%H:%M:%S')}")
        else:
            click.echo("No metrics data found.")
    else:
        click.echo(f"No metrics found for {date}")


@logging.command()
@click.option('--date', '-d', help='Date in YYYYMMDD format (default: today)')
def errors(date: Optional[str]):
    """View error logs."""
    logger = get_monitoring_logger()
    
    if not date:
        date = datetime.now().strftime("%Y%m%d")
    
    error_log = logger.monitoring_logs_dir / "errors" / f"{date}.log"
    
    click.echo(f"❌ Errors for {date}")
    click.echo("=" * 60)
    
    if error_log.exists():
        with open(error_log, 'r') as f:
            content = f.read()
            if content.strip():
                click.echo(content)
            else:
                click.echo("No errors logged.")
    else:
        click.echo("No error log found for this date.")
    
    # Also check for detailed error files
    error_files = list((logger.monitoring_logs_dir / "errors").glob(f"{date}-*.json"))
    if error_files:
        click.echo(f"\n📁 Detailed error files: {len(error_files)}")
        for error_file in error_files[:5]:  # Show first 5
            click.echo(f"  - {error_file.name}")


@logging.command()
@click.option('--name', '-n', required=True, help='Snapshot name')
@click.option('--description', '-d', help='Snapshot description')
def snapshot(name: str, description: Optional[str]):
    """Create a snapshot of current state."""
    logger = get_monitoring_logger()
    
    desc = description or f"Manual snapshot: {name}"
    
    click.echo(f"📸 Creating snapshot '{name}'...")
    
    snapshot_dir = logger.create_snapshot(
        name,
        "manual",
        desc
    )
    
    click.echo(f"✅ Snapshot created: {snapshot_dir}")


@logging.command()
def status():
    """Show logging system status."""
    logger = get_monitoring_logger()
    
    click.echo("📊 Ansera Logging System Status")
    click.echo("=" * 60)
    
    # Check directories
    click.echo("\n📁 Directory Structure:")
    for subdir in ['activities', 'changes', 'metrics', 'queue', 'processes', 'errors', 'snapshots', 'reports']:
        dir_path = logger.monitoring_logs_dir / subdir
        if dir_path.exists():
            file_count = len(list(dir_path.glob('*')))
            click.echo(f"  ✅ {subdir}: {file_count} files")
        else:
            click.echo(f"  ❌ {subdir}: not found")
    
    # Check master log
    if logger.master_log.exists():
        size = logger.master_log.stat().st_size
        click.echo(f"\n📋 Master Log: {size:,} bytes")
    
    # Recent activity
    today = datetime.now().strftime("%Y%m%d")
    activity_file = logger.monitoring_logs_dir / "activities" / f"{today}.log"
    if activity_file.exists():
        with open(activity_file, 'r') as f:
            line_count = sum(1 for _ in f)
        click.echo(f"\n📈 Today's Activities: {line_count}")
    
    # Disk usage
    total_size = logger._get_directory_size(logger.monitoring_logs_dir)
    click.echo(f"\n💾 Total Log Size: {total_size / 1024 / 1024:.2f} MB")


@logging.command()
@click.option('--days', '-d', default=30, help='Keep logs from last N days')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without deleting')
def cleanup(days: int, dry_run: bool):
    """Clean up old log files."""
    logger = get_monitoring_logger()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    click.echo(f"🧹 Cleaning logs older than {days} days...")
    if dry_run:
        click.echo("(DRY RUN - no files will be deleted)")
    
    files_to_delete = []
    
    # Find old files
    for log_dir in logger.monitoring_logs_dir.iterdir():
        if log_dir.is_dir():
            for log_file in log_dir.glob('*'):
                if log_file.is_file():
                    try:
                        # Parse date from filename
                        if log_file.stem.startswith('20'):  # Date format YYYYMMDD
                            file_date = datetime.strptime(log_file.stem[:8], "%Y%m%d")
                            if file_date < cutoff_date:
                                files_to_delete.append(log_file)
                    except:
                        continue
    
    # Report findings
    if files_to_delete:
        total_size = sum(f.stat().st_size for f in files_to_delete)
        click.echo(f"\nFound {len(files_to_delete)} files to delete")
        click.echo(f"Total size: {total_size / 1024 / 1024:.2f} MB")
        
        if not dry_run:
            click.confirm("Do you want to proceed?", abort=True)
            
            for f in files_to_delete:
                f.unlink()
            
            click.echo("✅ Cleanup completed")
    else:
        click.echo("No old files found to clean up")


# Add commands to main logging group
logging.add_command(view)
logging.add_command(search)
logging.add_command(report)
logging.add_command(metrics)
logging.add_command(errors)
logging.add_command(snapshot)
logging.add_command(status)
logging.add_command(cleanup)