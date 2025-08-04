"""MCP server management CLI commands."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ...mcp_integration import (
    MCPServerManager,
    MCPSettings,
    TokenManager,
    create_default_mcp_config,
)


console = Console()


@click.group(name="mcp")
def mcp_group():
    """Manage MCP server for LLM integration."""
    pass


@mcp_group.command(name="init")
@click.option(
    "--config-path",
    type=click.Path(path_type=Path),
    default="config/mcp.yaml",
    help="Path for MCP configuration file"
)
@click.option(
    "--auth-path",
    type=click.Path(path_type=Path),
    default="config/mcp_auth.yaml",
    help="Path for authentication configuration"
)
def init_config(config_path: Path, auth_path: Path):
    """Initialize MCP configuration files."""
    try:
        # Create config directory
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create MCP config if not exists
        if not config_path.exists():
            config = create_default_mcp_config()
            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
            console.print(f"[green]Created MCP config:[/green] {config_path}")
        else:
            console.print(f"[yellow]MCP config already exists:[/yellow] {config_path}")
        
        # Initialize token manager (creates auth config)
        token_manager = TokenManager(auth_path)
        console.print(f"[green]Created auth config:[/green] {auth_path}")
        
        # Create initial client
        console.print("\n[bold]Creating initial MCP client...[/bold]")
        client_info = token_manager.create_client(
            client_id="default-client",
            permissions=["read", "query"],
            rate_limit=100
        )
        
        console.print(f"\n[green]Client created successfully![/green]")
        console.print(f"Client ID: [cyan]{client_info['client_id']}[/cyan]")
        console.print(f"Client Secret: [cyan]{client_info['client_secret']}[/cyan]")
        console.print("\n[yellow]⚠️  Save the client secret securely - it cannot be retrieved later![/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error initializing MCP config:[/red] {str(e)}")
        sys.exit(1)


@mcp_group.command(name="start")
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to MCP configuration file"
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging"
)
def start_server(config: Optional[Path], debug: bool):
    """Start the MCP server."""
    try:
        # Set debug mode
        if debug:
            import os
            os.environ["MCP_DEBUG"] = "1"
        
        console.print("[bold]Starting MCP server...[/bold]")
        console.print("Server will run on stdio (standard input/output)")
        console.print("Press Ctrl+C to stop\n")
        
        # Import here to avoid circular imports
        from ...mcp_integration.lifecycle import run_mcp_server
        
        # Run server
        asyncio.run(run_mcp_server(config))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error starting server:[/red] {str(e)}")
        sys.exit(1)


@mcp_group.command(name="status")
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to MCP configuration file"
)
def server_status(config: Optional[Path]):
    """Check MCP server status and configuration."""
    try:
        # Load settings
        settings = MCPSettings.load_from_file(config)
        
        # Create status table
        table = Table(title="MCP Server Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Host", settings.server_host)
        table.add_row("Port", str(settings.server_port))
        table.add_row("Max Connections", str(settings.max_connections))
        table.add_row("Authentication", "Enabled" if settings.auth_enabled else "Disabled")
        table.add_row("Token Expiry", f"{settings.token_expiry} seconds")
        table.add_row("Max Context Tokens", str(settings.max_context_tokens))
        table.add_row("Caching", "Enabled" if settings.enable_caching else "Disabled")
        table.add_row("Request Logging", "Enabled" if settings.log_requests else "Disabled")
        
        console.print(table)
        
        # Check if vector DB is running
        console.print("\n[bold]Checking vector database status...[/bold]")
        from ...vector_db.docker_manager import QdrantDockerManager
        docker_manager = QdrantDockerManager()
        
        if docker_manager.is_running():
            console.print("[green]✓ Vector database is running[/green]")
        else:
            console.print("[red]✗ Vector database is not running[/red]")
            console.print("  Run 'vector-db-query vector init' to start it")
        
    except Exception as e:
        console.print(f"[red]Error checking status:[/red] {str(e)}")
        sys.exit(1)


@mcp_group.group(name="auth")
def auth_group():
    """Manage MCP authentication."""
    pass


@auth_group.command(name="create-client")
@click.argument("client_id")
@click.option(
    "--permissions",
    multiple=True,
    default=["read"],
    help="Client permissions (can be specified multiple times)"
)
@click.option(
    "--rate-limit",
    type=int,
    default=100,
    help="Rate limit per minute"
)
@click.option(
    "--auth-config",
    type=click.Path(path_type=Path),
    default="config/mcp_auth.yaml",
    help="Path to auth configuration"
)
def create_client(
    client_id: str,
    permissions: tuple,
    rate_limit: int,
    auth_config: Path
):
    """Create a new MCP client."""
    try:
        token_manager = TokenManager(auth_config)
        
        # Create client
        client_info = token_manager.create_client(
            client_id=client_id,
            permissions=list(permissions),
            rate_limit=rate_limit
        )
        
        console.print(f"\n[green]Client created successfully![/green]")
        console.print(f"Client ID: [cyan]{client_info['client_id']}[/cyan]")
        console.print(f"Client Secret: [cyan]{client_info['client_secret']}[/cyan]")
        console.print(f"Permissions: {', '.join(permissions)}")
        console.print(f"Rate Limit: {rate_limit} requests/minute")
        console.print("\n[yellow]⚠️  Save the client secret securely - it cannot be retrieved later![/yellow]")
        
    except ValueError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error creating client:[/red] {str(e)}")
        sys.exit(1)


@auth_group.command(name="list-clients")
@click.option(
    "--auth-config",
    type=click.Path(exists=True, path_type=Path),
    default="config/mcp_auth.yaml",
    help="Path to auth configuration"
)
def list_clients(auth_config: Path):
    """List all MCP clients."""
    try:
        token_manager = TokenManager(auth_config)
        clients = token_manager.list_clients()
        
        if not clients:
            console.print("[yellow]No clients configured[/yellow]")
            return
        
        # Create table
        table = Table(title="MCP Clients")
        table.add_column("Client ID", style="cyan")
        table.add_column("Permissions", style="green")
        table.add_column("Rate Limit", style="yellow")
        
        for client in clients:
            table.add_row(
                client["client_id"],
                ", ".join(client["permissions"]),
                f"{client['rate_limit']} req/min"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing clients:[/red] {str(e)}")
        sys.exit(1)


@auth_group.command(name="generate-token")
@click.argument("client_id")
@click.argument("client_secret")
@click.option(
    "--auth-config",
    type=click.Path(exists=True, path_type=Path),
    default="config/mcp_auth.yaml",
    help="Path to auth configuration"
)
def generate_token(client_id: str, client_secret: str, auth_config: Path):
    """Generate a JWT token for a client."""
    try:
        token_manager = TokenManager(auth_config)
        
        # Generate token
        token = token_manager.generate_token(client_id, client_secret)
        
        console.print(f"\n[green]Token generated successfully![/green]")
        console.print(f"\n[cyan]{token}[/cyan]")
        console.print(f"\n[yellow]Token expires in {token_manager.authenticator.token_expiry} seconds[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error generating token:[/red] {str(e)}")
        sys.exit(1)


@auth_group.command(name="remove-client")
@click.argument("client_id")
@click.option(
    "--auth-config",
    type=click.Path(exists=True, path_type=Path),
    default="config/mcp_auth.yaml",
    help="Path to auth configuration"
)
@click.confirmation_option(prompt="Are you sure you want to remove this client?")
def remove_client(client_id: str, auth_config: Path):
    """Remove an MCP client."""
    try:
        token_manager = TokenManager(auth_config)
        token_manager.remove_client(client_id)
        
        console.print(f"[green]Client '{client_id}' removed successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]Error removing client:[/red] {str(e)}")
        sys.exit(1)


@auth_group.command(name="export-config")
@click.argument("client_id")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    required=True,
    help="Output path for client configuration"
)
@click.option(
    "--auth-config",
    type=click.Path(exists=True, path_type=Path),
    default="config/mcp_auth.yaml",
    help="Path to auth configuration"
)
def export_config(client_id: str, output: Path, auth_config: Path):
    """Export client configuration for distribution."""
    try:
        token_manager = TokenManager(auth_config)
        token_manager.export_client_config(client_id, output)
        
        console.print(f"[green]Client configuration exported to:[/green] {output}")
        console.print("[yellow]⚠️  This file contains sensitive credentials - handle with care![/yellow]")
        
    except ValueError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error exporting config:[/red] {str(e)}")
        sys.exit(1)


@mcp_group.command(name="test")
@click.option(
    "--query",
    default="What is machine learning?",
    help="Test query to send"
)
@click.option(
    "--limit",
    type=int,
    default=5,
    help="Number of results to return"
)
def test_query(query: str, limit: int):
    """Test MCP server with a sample query."""
    console.print("[yellow]Note: This command tests the server locally without MCP protocol[/yellow]")
    console.print(f"\nQuery: [cyan]{query}[/cyan]")
    console.print(f"Limit: [cyan]{limit}[/cyan]\n")
    
    try:
        # Initialize services
        from ...vector_db.service import VectorDBService
        
        vector_service = VectorDBService()
        vector_service.initialize()
        
        # Perform search
        results = vector_service.search_similar(
            query_text=query,
            limit=limit
        )
        
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return
        
        # Display results
        for i, result in enumerate(results, 1):
            panel = Panel(
                f"[white]{result.chunk.content[:200]}...[/white]\n\n"
                f"Score: [green]{result.score:.4f}[/green] | "
                f"Source: [cyan]{Path(result.document.file_path).name}[/cyan]",
                title=f"Result {i}",
                border_style="blue"
            )
            console.print(panel)
        
    except Exception as e:
        console.print(f"[red]Error testing query:[/red] {str(e)}")
        sys.exit(1)


@mcp_group.command(name="metrics")
@click.option(
    "--export",
    type=click.Path(path_type=Path),
    help="Export metrics to JSON file"
)
@click.option(
    "--log-dir",
    type=click.Path(exists=True, path_type=Path),
    default="logs/mcp",
    help="MCP log directory"
)
def show_metrics(export: Optional[Path], log_dir: Path):
    """View MCP server metrics and statistics."""
    try:
        from ...mcp_integration.logging import MCPLogger
        
        # Create logger instance to read metrics
        mcp_logger = MCPLogger(log_dir=log_dir)
        
        if not mcp_logger.enable_metrics:
            console.print("[yellow]Metrics collection is disabled[/yellow]")
            return
        
        # Get metrics summary
        metrics = mcp_logger.get_metrics_summary()
        
        if export:
            # Export to file
            mcp_logger.export_metrics(export)
            console.print(f"[green]Metrics exported to:[/green] {export}")
        else:
            # Display metrics
            console.print(Panel("[bold]MCP Server Metrics[/bold]", border_style="green"))
            
            # Server metrics
            server_metrics = metrics.get("server", {})
            table = Table(title="Server Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in server_metrics.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)
            
            # Tool metrics
            tool_metrics = metrics.get("tools", {})
            if tool_metrics:
                console.print("\n[bold]Tool Statistics:[/bold]")
                for tool, stats in tool_metrics.items():
                    console.print(f"\n[cyan]{tool}:[/cyan]")
                    for key, value in stats.items():
                        console.print(f"  {key.replace('_', ' ').title()}: [green]{value}[/green]")
            
            # Top clients
            top_clients = metrics.get("top_clients", [])
            if top_clients:
                console.print("\n[bold]Top Clients:[/bold]")
                client_table = Table()
                client_table.add_column("Client ID", style="cyan")
                client_table.add_column("Requests", style="yellow")
                client_table.add_column("Tokens", style="green")
                
                for client in top_clients:
                    client_table.add_row(
                        client["client_id"],
                        str(client["requests"]),
                        str(client["tokens"])
                    )
                
                console.print(client_table)
            
            # Recent errors
            recent_errors = metrics.get("recent_errors", [])
            if recent_errors:
                console.print("\n[bold red]Recent Errors:[/bold red]")
                for error in recent_errors[-5:]:  # Show last 5
                    console.print(f"[red]• {error['tool']} - {error['error']}[/red]")
                    console.print(f"  Client: {error['client_id']}, Time: {error['timestamp']}")
    
    except Exception as e:
        console.print(f"[red]Error viewing metrics:[/red] {str(e)}")
        sys.exit(1)


@mcp_group.command(name="test-client")
@click.option(
    "--client-id",
    default="test-client",
    help="Client ID for authentication"
)
@click.option(
    "--client-secret",
    help="Client secret (will prompt if not provided)"
)
@click.option(
    "--auth-config",
    type=click.Path(exists=True, path_type=Path),
    default="config/mcp_auth.yaml",
    help="Path to auth configuration"
)
@click.option(
    "--queries-file",
    type=click.Path(exists=True, path_type=Path),
    help="JSON file with test queries"
)
def test_client(
    client_id: str,
    client_secret: Optional[str],
    auth_config: Path,
    queries_file: Optional[Path]
):
    """Run MCP client tests against the server."""
    try:
        # Get client secret if not provided
        if not client_secret:
            import getpass
            client_secret = getpass.getpass("Client Secret: ")
        
        console.print(Panel(
            "[bold]MCP Client Test Tool[/bold]\n"
            "[dim]Testing MCP server functionality[/dim]",
            border_style="blue"
        ))
        
        # Import test client
        from ...mcp_integration.test_client import test_mcp_server
        
        # Run tests
        import asyncio
        asyncio.run(test_mcp_server(
            client_id=client_id,
            client_secret=client_secret,
            auth_config=auth_config
        ))
        
    except Exception as e:
        console.print(f"[red]Error running tests:[/red] {str(e)}")
        sys.exit(1)


@mcp_group.command(name="example-queries")
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default="example_queries.json",
    help="Output file for example queries"
)
def generate_examples(output: Path):
    """Generate example MCP queries."""
    try:
        from ...mcp_integration.test_client import create_test_queries
        
        queries = create_test_queries()
        
        # Add more examples
        queries.extend([
            {
                "name": "Complex Search with Filters",
                "tool": "query-vectors",
                "params": {
                    "query": "database optimization techniques",
                    "limit": 10,
                    "threshold": 0.6,
                    "filters": {
                        "type": "technical",
                        "year": 2024
                    }
                }
            },
            {
                "name": "Code Example Search",
                "tool": "search-similar",
                "params": {
                    "text": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                    "limit": 3,
                    "include_source": True
                }
            }
        ])
        
        # Save queries
        with open(output, "w") as f:
            json.dump({"queries": queries}, f, indent=2)
        
        console.print(f"[green]Example queries saved to:[/green] {output}")
        
        # Display examples
        console.print("\n[bold]Example Queries:[/bold]\n")
        
        for i, query in enumerate(queries, 1):
            console.print(f"[cyan]{i}. {query['name']}[/cyan]")
            console.print(f"   Tool: {query['tool']}")
            console.print(f"   Params: {json.dumps(query['params'], indent=6)}")
            console.print()
        
    except Exception as e:
        console.print(f"[red]Error generating examples:[/red] {str(e)}")
        sys.exit(1)


# Add mcp group to main CLI
def register_commands(cli):
    """Register MCP commands with main CLI."""
    cli.add_command(mcp_group)