"""Configuration management CLI commands."""

import os
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.syntax import Syntax

from vector_db_query.utils.config_enhanced import get_config, Config, FileFormatConfig
from vector_db_query.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


@click.group()
def config_group():
    """Manage system configuration."""
    pass


@config_group.command()
@click.option("--format", "-f", type=click.Choice(["yaml", "env", "table"]), default="yaml", 
              help="Output format")
@click.option("--section", "-s", help="Show only specific section")
def show(format: str, section: Optional[str]):
    """Show current configuration."""
    console.print(Panel("[bold cyan]Configuration[/bold cyan]", expand=False))
    
    config_manager = get_config()
    
    if section:
        # Show specific section
        value = config_manager.get(section)
        if value is None:
            console.print(f"[red]Section '{section}' not found[/red]")
            return
            
        if format == "yaml":
            yaml_str = yaml.dump({section: value}, default_flow_style=False, sort_keys=False)
            syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
            console.print(syntax)
        elif format == "env":
            _show_as_env({section: value}, prefix=f"VECTOR_DB_{section.upper()}")
        else:  # table
            _show_as_table({section: value})
    else:
        # Show full configuration
        config_dict = config_manager.config.dict()
        
        if format == "yaml":
            yaml_str = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)
            syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
            console.print(syntax)
        elif format == "env":
            env_vars = config_manager.export_env()
            for key, value in sorted(env_vars.items()):
                console.print(f"export {key}='{value}'")
        else:  # table
            _show_as_table(config_dict)


@config_group.command()
@click.argument("key")
@click.argument("value")
@click.option("--type", "-t", type=click.Choice(["str", "int", "float", "bool", "list"]), 
              default="str", help="Value type")
def set(key: str, value: str, type: str):
    """Set a configuration value."""
    config_manager = get_config()
    
    # Convert value to appropriate type
    try:
        if type == "int":
            converted_value = int(value)
        elif type == "float":
            converted_value = float(value)
        elif type == "bool":
            converted_value = value.lower() in ["true", "1", "yes", "on"]
        elif type == "list":
            converted_value = [v.strip() for v in value.split(",")]
        else:
            converted_value = value
    except ValueError as e:
        console.print(f"[red]Error converting value: {e}[/red]")
        return
        
    try:
        old_value = config_manager.get(key)
        config_manager.set(key, converted_value)
        console.print(f"[green]✓[/green] Set {key} = {converted_value}")
        if old_value is not None:
            console.print(f"  [dim](was: {old_value})[/dim]")
    except Exception as e:
        console.print(f"[red]Error setting configuration: {e}[/red]")


@config_group.command()
@click.argument("key")
def get(key: str):
    """Get a configuration value."""
    config_manager = get_config()
    value = config_manager.get(key)
    
    if value is None:
        console.print(f"[red]Key '{key}' not found[/red]")
    else:
        console.print(f"{key} = {value}")
        console.print(f"Type: {type(value).__name__}")


@config_group.command()
def validate():
    """Validate current configuration."""
    console.print("[bold]Validating configuration...[/bold]\n")
    
    config_manager = get_config()
    issues = config_manager.validate()
    
    if issues:
        console.print(f"[red]Found {len(issues)} issue(s):[/red]\n")
        for i, issue in enumerate(issues, 1):
            console.print(f"  {i}. {issue}")
        console.print("\n[yellow]Please fix these issues for optimal operation.[/yellow]")
    else:
        console.print("[green]✓ Configuration is valid![/green]")


@config_group.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def export(output: Optional[str]):
    """Export configuration to file."""
    config_manager = get_config()
    
    if output:
        output_path = Path(output)
        config_manager.config.save(output_path)
        console.print(f"[green]✓[/green] Configuration exported to: {output_path}")
    else:
        # Export to stdout
        yaml_str = yaml.dump(config_manager.config.dict(), default_flow_style=False, sort_keys=False)
        console.print(yaml_str)


@config_group.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--merge", is_flag=True, help="Merge with existing configuration")
def load(file: str, merge: bool):
    """Load configuration from file."""
    file_path = Path(file)
    
    try:
        # Load new configuration
        with open(file_path, 'r') as f:
            new_config_data = yaml.safe_load(f)
            
        config_manager = get_config()
        
        if merge:
            # Merge with existing
            current_data = config_manager.config.dict()
            _merge_configs(current_data, new_config_data)
            config_manager.config = Config(**current_data)
            console.print(f"[green]✓[/green] Configuration merged from: {file_path}")
        else:
            # Replace entirely
            config_manager.config = Config(**new_config_data)
            console.print(f"[green]✓[/green] Configuration loaded from: {file_path}")
            
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")


@config_group.command()
def formats():
    """Show supported file formats."""
    console.print(Panel("[bold cyan]Supported File Formats[/bold cyan]", expand=False))
    
    config_manager = get_config()
    formats = config_manager.config.document_processing.file_formats
    
    # Create tree view
    tree = Tree("[bold]File Format Configuration[/bold]")
    
    # Add format categories
    categories = [
        ("Documents", formats.documents, "📄"),
        ("Spreadsheets", formats.spreadsheets, "📊"),
        ("Presentations", formats.presentations, "📽️"),
        ("Email", formats.email, "📧"),
        ("Web", formats.web, "🌐"),
        ("Config", formats.config, "⚙️"),
        ("Images (OCR)", formats.images, "🖼️"),
        ("Logs", formats.logs, "📋"),
        ("Data", formats.data, "💾"),
        ("Archives", formats.archives, "📦"),
    ]
    
    total_count = 0
    for category, extensions, icon in categories:
        if extensions:
            branch = tree.add(f"{icon} [bold yellow]{category}[/bold yellow] ({len(extensions)} formats)")
            for ext in sorted(extensions):
                branch.add(f"[green]✓[/green] {ext}")
            total_count += len(extensions)
            
    # Add custom extensions if any
    if formats.custom_extensions:
        custom_branch = tree.add(f"🔧 [bold yellow]Custom[/bold yellow] ({len(formats.custom_extensions)} formats)")
        for ext in sorted(formats.custom_extensions):
            custom_branch.add(f"[green]✓[/green] {ext}")
        total_count += len(formats.custom_extensions)
    
    console.print(tree)
    console.print(f"\n[bold]Total supported formats:[/bold] {total_count}")
    
    # Show OCR status
    ocr_config = config_manager.config.document_processing.ocr
    console.print(f"\n[bold]OCR Configuration:[/bold]")
    console.print(f"  Enabled: {'[green]Yes[/green]' if ocr_config.enabled else '[red]No[/red]'}")
    if ocr_config.enabled:
        console.print(f"  Language: {ocr_config.language}")
        if ocr_config.additional_languages:
            console.print(f"  Additional: {', '.join(ocr_config.additional_languages)}")
        console.print(f"  DPI: {ocr_config.dpi}")
        console.print(f"  Confidence: {ocr_config.confidence_threshold}%")


@config_group.command()
@click.argument("extension")
def add_format(extension: str):
    """Add a custom file format extension."""
    if not extension.startswith("."):
        extension = f".{extension}"
        
    config_manager = get_config()
    formats = config_manager.config.document_processing.file_formats
    
    if extension in formats.all_supported:
        console.print(f"[yellow]Extension {extension} is already supported[/yellow]")
        return
        
    # Add to custom extensions
    if extension not in formats.custom_extensions:
        formats.custom_extensions.append(extension)
        console.print(f"[green]✓[/green] Added custom extension: {extension}")
        
        # Show total count
        total = len(formats.all_supported)
        console.print(f"[dim]Total supported formats: {total}[/dim]")
    else:
        console.print(f"[yellow]Extension {extension} already in custom extensions[/yellow]")


@config_group.command()
def env():
    """Show environment variables that can override configuration."""
    console.print(Panel("[bold cyan]Environment Variable Overrides[/bold cyan]", expand=False))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Environment Variable", style="cyan")
    table.add_column("Config Path", style="yellow")
    table.add_column("Current Value", style="green")
    
    # Define mappings
    mappings = [
        ("VECTOR_DB_LOG_LEVEL", "app.log_level"),
        ("VECTOR_DB_DATA_DIR", "paths.data_dir"),
        ("VECTOR_DB_LOG_DIR", "paths.log_dir"),
        ("EMBEDDING_MODEL", "embedding.model"),
        ("EMBEDDING_DIMENSIONS", "embedding.dimensions"),
        ("QDRANT_HOST", "vector_db.host"),
        ("QDRANT_PORT", "vector_db.port"),
        ("MCP_SERVER_HOST", "mcp.server_host"),
        ("MCP_SERVER_PORT", "mcp.server_port"),
        ("TESSERACT_CMD", "document_processing.ocr.tesseract_cmd"),
        ("OCR_LANGUAGE", "document_processing.ocr.language"),
        ("OCR_ENABLED", "document_processing.ocr.enabled"),
        ("CHUNK_SIZE", "document_processing.chunk_size"),
        ("CHUNK_OVERLAP", "document_processing.chunk_overlap"),
        ("MONITORING_ENABLED", "monitoring.enabled"),
    ]
    
    config_manager = get_config()
    
    for env_var, config_path in mappings:
        current_value = os.getenv(env_var)
        if current_value:
            table.add_row(env_var, config_path, current_value)
        else:
            config_value = config_manager.get(config_path)
            table.add_row(env_var, config_path, f"[dim]{config_value}[/dim]")
            
    console.print(table)
    console.print("\n[dim]Values in green are currently set, dim values show config defaults[/dim]")


def _show_as_table(config_dict: dict, prefix: str = ""):
    """Show configuration as a table."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_column("Type", style="dim")
    
    def add_items(d, path=""):
        for key, value in d.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, dict):
                add_items(value, current_path)
            else:
                if isinstance(value, list):
                    value_str = f"[{len(value)} items]"
                elif isinstance(value, bool):
                    value_str = "✓" if value else "✗"
                else:
                    value_str = str(value)
                    
                table.add_row(current_path, value_str, type(value).__name__)
                
    add_items(config_dict)
    console.print(table)


def _show_as_env(config_dict: dict, prefix: str = "VECTOR_DB"):
    """Show configuration as environment variables."""
    def flatten(obj, current_prefix):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_prefix = f"{current_prefix}_{key.upper()}"
                flatten(value, new_prefix)
        elif isinstance(obj, list):
            console.print(f"export {current_prefix}='{','.join(str(v) for v in obj)}'")
        elif obj is not None:
            console.print(f"export {current_prefix}='{obj}'")
            
    flatten(config_dict, prefix)


def _merge_configs(base: dict, update: dict) -> dict:
    """Recursively merge configuration dictionaries."""
    for key, value in update.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_configs(base[key], value)
        else:
            base[key] = value
    return base


# For interactive menu
def show_configuration_menu():
    """Interactive configuration menu."""
    from questionary import select, confirm
    
    console.print(Panel("[bold]Configuration Management[/bold]", border_style="green"))
    
    while True:
        choice = select(
            "What would you like to do?",
            choices=[
                "Show current configuration",
                "View supported file formats",
                "Validate configuration",
                "Show environment variables",
                "Export configuration",
                "Back to main menu"
            ]
        ).ask()
        
        if choice == "Back to main menu":
            break
        elif choice == "Show current configuration":
            format_choice = select(
                "Select output format:",
                choices=["YAML", "Table", "Environment variables"]
            ).ask()
            
            format_map = {"YAML": "yaml", "Table": "table", "Environment variables": "env"}
            show(format_map[format_choice], None)
        elif choice == "View supported file formats":
            formats()
        elif choice == "Validate configuration":
            validate()
        elif choice == "Show environment variables":
            env()
        elif choice == "Export configuration":
            export(None)
            
        if not confirm("\nContinue with configuration management?", default=True).ask():
            break