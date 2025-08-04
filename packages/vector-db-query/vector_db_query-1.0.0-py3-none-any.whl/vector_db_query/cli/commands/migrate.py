"""Data migration CLI commands."""

import click
import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta

from ..utils import console, create_panel, format_success, format_error, format_warning
from ...utils.logger import get_logger
from ...utils.config import get_config

logger = get_logger(__name__)


@click.group()
def migrate():
    """Data migration commands."""
    pass


@migrate.command()
@click.option('--sources', '-s', multiple=True, 
              type=click.Choice(['gmail', 'fireflies', 'google_drive', 'all']),
              default=['all'], help='Data sources to migrate')
@click.option('--days', '-d', type=int, default=7, help='Days of history to migrate')
@click.option('--dry-run', is_flag=True, help='Perform dry run without actual migration')
@click.option('--config', '-c', help='Path to configuration file')
def run(sources, days, dry_run, config):
    """Run initial data migration."""
    console.print(create_panel(
        "[bold cyan]🚀 Data Migration[/bold cyan]\n\n"
        f"Migrating {days} days of data from: {', '.join(sources)}",
        title="Migration"
    ))
    
    if dry_run:
        console.print(format_warning("DRY RUN MODE - No data will be migrated\n"))
    
    # Import here to avoid circular imports
    from scripts.migrate_data_sources import DataMigrator
    
    # Load configuration
    config_dict = get_config(config)
    if dry_run:
        config_dict['dry_run'] = True
    
    # Handle 'all' source
    if 'all' in sources:
        sources = ['gmail', 'fireflies', 'google_drive']
    
    # Create and run migrator
    migrator = DataMigrator(config_dict)
    
    try:
        # Run migration
        result = asyncio.run(migrator.run_migration(
            sources=list(sources),
            gmail_days=days,
            fireflies_days=days,
            drive_days=days
        ))
        
        if result['status'] == 'success':
            console.print(format_success("\n✅ Migration completed successfully!"))
        else:
            console.print(format_error(f"\n❌ Migration failed: {result.get('message', 'Unknown error')}"))
            
    except Exception as e:
        console.print(format_error(f"Migration error: {e}"))
        logger.error("Migration failed", exc_info=True)


@migrate.command()
def checklist():
    """Run pre-migration checklist."""
    console.print(create_panel(
        "[bold cyan]📋 Pre-Migration Checklist[/bold cyan]\n\n"
        "Verifying system readiness...",
        title="Checklist"
    ))
    
    import subprocess
    
    try:
        # Run checklist script
        result = subprocess.run(['bash', 'scripts/migration_checklist.sh'], 
                              capture_output=False)
        
        if result.returncode != 0:
            console.print(format_error("\nChecklist failed!"))
        
    except FileNotFoundError:
        console.print(format_error("Checklist script not found. Make sure you're in the project root."))
    except Exception as e:
        console.print(format_error(f"Error running checklist: {e}"))


@migrate.command()
@click.option('--source', '-s', 
              type=click.Choice(['gmail', 'fireflies', 'google_drive']),
              help='Specific source to check')
def status(source):
    """Check migration status."""
    console.print(create_panel(
        "[bold cyan]📊 Migration Status[/bold cyan]\n\n"
        "Checking migration progress...",
        title="Status"
    ))
    
    from ...db.manager import DatabaseManager
    from rich.table import Table
    
    db_manager = DatabaseManager()
    
    try:
        with db_manager.get_session() as session:
            # Create status table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Source", style="cyan")
            table.add_column("Total Items", style="yellow")
            table.add_column("Last Sync", style="green")
            table.add_column("Status", style="blue")
            
            # Query for each source
            sources = [source] if source else ['gmail', 'fireflies', 'google_drive']
            
            for src in sources:
                # Get count
                count = session.execute(
                    "SELECT COUNT(*) FROM data_sources.processed_items WHERE source_type = :source",
                    {'source': src}
                ).scalar()
                
                # Get last sync
                last_sync = session.execute(
                    "SELECT MAX(processed_at) FROM data_sources.processed_items WHERE source_type = :source",
                    {'source': src}
                ).scalar()
                
                # Get sync status
                sync_status = session.execute(
                    "SELECT status FROM data_sources.sync_status WHERE source_type = :source",
                    {'source': src}
                ).scalar()
                
                table.add_row(
                    src.title(),
                    str(count),
                    last_sync.strftime("%Y-%m-%d %H:%M") if last_sync else "Never",
                    sync_status or "Unknown"
                )
            
            console.print("\n")
            console.print(table)
            
            # Show recent errors if any
            error_count = session.execute(
                "SELECT COUNT(*) FROM data_sources.sync_status WHERE errors_count > 0"
            ).scalar()
            
            if error_count > 0:
                console.print(format_warning(f"\n⚠️  {error_count} sources have errors"))
                console.print("Run 'vdq migrate logs --errors' to view details")
                
    except Exception as e:
        console.print(format_error(f"Error checking status: {e}"))
        logger.error("Status check failed", exc_info=True)


@migrate.command()
@click.option('--errors', is_flag=True, help='Show only errors')
@click.option('--source', '-s', 
              type=click.Choice(['gmail', 'fireflies', 'google_drive']),
              help='Filter by source')
@click.option('--lines', '-n', type=int, default=50, help='Number of log lines to show')
def logs(errors, source, lines):
    """View migration logs."""
    console.print(create_panel(
        "[bold cyan]📜 Migration Logs[/bold cyan]\n\n"
        f"Showing last {lines} log entries...",
        title="Logs"
    ))
    
    from ...db.manager import DatabaseManager
    
    db_manager = DatabaseManager()
    
    try:
        with db_manager.get_session() as session:
            # Build query
            query = "SELECT * FROM data_sources.webhook_logs WHERE 1=1"
            params = {}
            
            if errors:
                query += " AND status = 'error'"
            
            if source:
                query += " AND source = :source"
                params['source'] = source
                
            query += " ORDER BY received_at DESC LIMIT :limit"
            params['limit'] = lines
            
            # Execute query
            logs = session.execute(query, params).fetchall()
            
            if not logs:
                console.print("[dim]No logs found[/dim]")
                return
                
            # Display logs
            for log in logs:
                timestamp = log.received_at.strftime("%Y-%m-%d %H:%M:%S")
                status_color = "red" if log.status == "error" else "green"
                
                console.print(f"\n[dim]{timestamp}[/dim] [{status_color}]{log.status}[/{status_color}] {log.source}")
                
                if log.event_type:
                    console.print(f"  Event: {log.event_type}")
                    
                if log.error_message:
                    console.print(f"  [red]Error: {log.error_message}[/red]")
                    
                if log.payload and errors:
                    console.print(f"  [dim]Payload: {json.dumps(log.payload, indent=2)}[/dim]")
                    
    except Exception as e:
        console.print(format_error(f"Error reading logs: {e}"))
        logger.error("Log reading failed", exc_info=True)


@migrate.command()
@click.option('--output', '-o', default='migration_report.json', help='Output file path')
def report(output):
    """Generate migration report."""
    console.print(create_panel(
        "[bold cyan]📊 Migration Report[/bold cyan]\n\n"
        "Generating comprehensive report...",
        title="Report"
    ))
    
    from ...db.manager import DatabaseManager
    from rich.table import Table
    
    db_manager = DatabaseManager()
    report_data = {
        'generated_at': datetime.now().isoformat(),
        'sources': {},
        'summary': {}
    }
    
    try:
        with db_manager.get_session() as session:
            # Gather data for each source
            for source in ['gmail', 'fireflies', 'google_drive']:
                # Get statistics
                stats = session.execute("""
                    SELECT 
                        COUNT(*) as total_items,
                        MIN(processed_at) as first_item,
                        MAX(processed_at) as last_item
                    FROM data_sources.processed_items 
                    WHERE source_type = :source
                """, {'source': source}).first()
                
                # Get sync status
                sync = session.execute("""
                    SELECT * FROM data_sources.sync_status 
                    WHERE source_type = :source
                """, {'source': source}).first()
                
                report_data['sources'][source] = {
                    'total_items': stats.total_items if stats else 0,
                    'first_item': stats.first_item.isoformat() if stats and stats.first_item else None,
                    'last_item': stats.last_item.isoformat() if stats and stats.last_item else None,
                    'last_sync': sync.last_sync_at.isoformat() if sync and sync.last_sync_at else None,
                    'status': sync.status if sync else 'never_synced',
                    'errors': sync.errors_count if sync else 0
                }
            
            # Calculate summary
            report_data['summary'] = {
                'total_items': sum(s['total_items'] for s in report_data['sources'].values()),
                'sources_active': len([s for s in report_data['sources'].values() if s['status'] != 'never_synced']),
                'sources_with_errors': len([s for s in report_data['sources'].values() if s['errors'] > 0])
            }
            
        # Save report
        output_path = Path(output)
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        console.print(format_success(f"\n✅ Report saved to: {output_path}"))
        
        # Display summary
        table = Table(title="Migration Summary", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Total Items", str(report_data['summary']['total_items']))
        table.add_row("Active Sources", f"{report_data['summary']['sources_active']}/3")
        table.add_row("Sources with Errors", str(report_data['summary']['sources_with_errors']))
        
        console.print("\n")
        console.print(table)
        
    except Exception as e:
        console.print(format_error(f"Error generating report: {e}"))
        logger.error("Report generation failed", exc_info=True)


if __name__ == "__main__":
    migrate()