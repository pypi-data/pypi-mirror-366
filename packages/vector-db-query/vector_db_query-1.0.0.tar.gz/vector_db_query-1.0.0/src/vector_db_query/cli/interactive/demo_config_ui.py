"""Demo script for configuration UI components."""

from pathlib import Path
from rich.console import Console

from .config_ui import (
    ConfigEditor, ConfigWizard, ConfigSection, ConfigField,
    ConfigType
)


def create_demo_schema() -> list[ConfigSection]:
    """Create demo configuration schema.
    
    Returns:
        List of config sections
    """
    return [
        ConfigSection(
            name="general",
            title="General Settings",
            description="Basic application settings",
            icon="⚙️",
            fields=[
                ConfigField(
                    key="app.name",
                    name="Application Name",
                    description="Name of your application",
                    type=ConfigType.STRING,
                    default="Vector DB Query",
                    pattern=r"^[\w\s-]+$"
                ),
                ConfigField(
                    key="app.debug",
                    name="Debug Mode",
                    description="Enable debug logging",
                    type=ConfigType.BOOLEAN,
                    default=False
                ),
                ConfigField(
                    key="app.max_workers",
                    name="Max Workers",
                    description="Maximum number of worker threads",
                    type=ConfigType.INTEGER,
                    default=4,
                    min_value=1,
                    max_value=16
                ),
            ]
        ),
        ConfigSection(
            name="vector_db",
            title="Vector Database",
            description="Qdrant vector database configuration",
            icon="🗄️",
            fields=[
                ConfigField(
                    key="qdrant.host",
                    name="Host",
                    description="Qdrant server hostname",
                    type=ConfigType.STRING,
                    default="localhost"
                ),
                ConfigField(
                    key="qdrant.port",
                    name="Port",
                    description="Qdrant server port",
                    type=ConfigType.INTEGER,
                    default=6333,
                    min_value=1,
                    max_value=65535
                ),
                ConfigField(
                    key="qdrant.collection",
                    name="Collection Name",
                    description="Default collection name",
                    type=ConfigType.STRING,
                    default="documents"
                ),
                ConfigField(
                    key="qdrant.vector_size",
                    name="Vector Size",
                    description="Embedding vector dimensions",
                    type=ConfigType.CHOICE,
                    choices=[768, 1536, 3072],
                    default=768
                ),
            ]
        ),
        ConfigSection(
            name="embeddings",
            title="Embeddings",
            description="Text embedding model configuration",
            icon="🧮",
            fields=[
                ConfigField(
                    key="embeddings.model",
                    name="Model",
                    description="Embedding model to use",
                    type=ConfigType.CHOICE,
                    choices=["gemini-embedding-001", "text-embedding-ada-002"],
                    default="gemini-embedding-001"
                ),
                ConfigField(
                    key="embeddings.api_key",
                    name="API Key",
                    description="API key for embedding service",
                    type=ConfigType.STRING,
                    required=True
                ),
                ConfigField(
                    key="embeddings.batch_size",
                    name="Batch Size",
                    description="Number of texts to embed at once",
                    type=ConfigType.INTEGER,
                    default=100,
                    min_value=1,
                    max_value=1000
                ),
            ]
        ),
        ConfigSection(
            name="processing",
            title="Document Processing",
            description="Document processing settings",
            icon="📄",
            fields=[
                ConfigField(
                    key="processing.chunk_size",
                    name="Chunk Size",
                    description="Size of text chunks in characters",
                    type=ConfigType.INTEGER,
                    default=1000,
                    min_value=100,
                    max_value=10000
                ),
                ConfigField(
                    key="processing.chunk_overlap",
                    name="Chunk Overlap",
                    description="Overlap between chunks in characters",
                    type=ConfigType.INTEGER,
                    default=200,
                    min_value=0,
                    max_value=500
                ),
                ConfigField(
                    key="processing.file_types",
                    name="Supported File Types",
                    description="File extensions to process",
                    type=ConfigType.LIST,
                    default=[".txt", ".md", ".pdf", ".doc", ".docx"]
                ),
                ConfigField(
                    key="processing.exclude_patterns",
                    name="Exclude Patterns",
                    description="Patterns to exclude from processing",
                    type=ConfigType.LIST,
                    default=["*.tmp", ".*", "__pycache__"]
                ),
            ]
        ),
        ConfigSection(
            name="mcp",
            title="MCP Server",
            description="Model Context Protocol settings",
            icon="🤖",
            fields=[
                ConfigField(
                    key="mcp.enabled",
                    name="Enable MCP",
                    description="Enable MCP server",
                    type=ConfigType.BOOLEAN,
                    default=True
                ),
                ConfigField(
                    key="mcp.port",
                    name="Server Port",
                    description="MCP server port",
                    type=ConfigType.INTEGER,
                    default=8080,
                    min_value=1024,
                    max_value=65535
                ),
                ConfigField(
                    key="mcp.auth_required",
                    name="Require Authentication",
                    description="Require authentication for MCP access",
                    type=ConfigType.BOOLEAN,
                    default=True
                ),
                ConfigField(
                    key="mcp.allowed_clients",
                    name="Allowed Clients",
                    description="List of allowed client IDs",
                    type=ConfigType.LIST,
                    default=["claude", "default"]
                ),
            ]
        ),
        ConfigSection(
            name="paths",
            title="Paths",
            description="File and directory paths",
            icon="📁",
            fields=[
                ConfigField(
                    key="paths.data_dir",
                    name="Data Directory",
                    description="Directory for storing data files",
                    type=ConfigType.PATH,
                    default="~/.vector_db_query/data"
                ),
                ConfigField(
                    key="paths.cache_dir",
                    name="Cache Directory",
                    description="Directory for cache files",
                    type=ConfigType.PATH,
                    default="~/.vector_db_query/cache"
                ),
                ConfigField(
                    key="paths.log_file",
                    name="Log File",
                    description="Path to log file",
                    type=ConfigType.PATH,
                    default="~/.vector_db_query/app.log"
                ),
            ]
        ),
    ]


def demo_config_editor():
    """Demo configuration editor."""
    console = Console()
    
    console.print("\n[bold]Configuration Editor Demo[/bold]\n")
    
    # Create temporary config file
    config_path = Path("/tmp/demo_config.yaml")
    
    # Create editor
    editor = ConfigEditor(
        config_path=config_path,
        schema=create_demo_schema(),
        format="yaml",
        backup=True
    )
    
    # Edit configuration
    saved = editor.edit()
    
    if saved:
        console.print("\n[green]Configuration saved successfully![/green]")
        
        # Show saved config
        with open(config_path) as f:
            console.print("\n[bold]Saved configuration:[/bold]")
            console.print(f.read())
    else:
        console.print("\n[yellow]Configuration not saved[/yellow]")


def demo_config_wizard():
    """Demo configuration wizard."""
    console = Console()
    
    console.print("\n[bold]Configuration Wizard Demo[/bold]\n")
    
    # Create wizard with subset of schema
    wizard_schema = [
        ConfigSection(
            name="basic",
            title="Basic Setup",
            description="Essential settings to get started",
            icon="🚀",
            fields=[
                ConfigField(
                    key="app.name",
                    name="Application Name",
                    description="What would you like to call your application?",
                    type=ConfigType.STRING,
                    default="My Vector Search"
                ),
                ConfigField(
                    key="qdrant.host",
                    name="Database Host",
                    description="Where is your Qdrant database running?",
                    type=ConfigType.STRING,
                    default="localhost"
                ),
                ConfigField(
                    key="embeddings.api_key",
                    name="API Key",
                    description="Enter your embedding API key",
                    type=ConfigType.STRING,
                    required=True
                ),
            ]
        ),
        ConfigSection(
            name="features",
            title="Features",
            description="Choose which features to enable",
            icon="✨",
            fields=[
                ConfigField(
                    key="mcp.enabled",
                    name="Enable MCP Server",
                    description="Enable AI assistant integration?",
                    type=ConfigType.BOOLEAN,
                    default=True
                ),
                ConfigField(
                    key="app.debug",
                    name="Debug Mode",
                    description="Enable debug logging?",
                    type=ConfigType.BOOLEAN,
                    default=False
                ),
            ]
        ),
    ]
    
    # Run wizard
    wizard = ConfigWizard(schema=wizard_schema)
    config_data = wizard.run()
    
    console.print("\n[green]Wizard completed![/green]")
    console.print(f"\nGenerated configuration: {config_data}")


def demo_field_validation():
    """Demo field validation."""
    console = Console()
    
    console.print("\n[bold]Field Validation Demo[/bold]\n")
    
    # Create fields with various validations
    fields = [
        ConfigField(
            key="email",
            name="Email Address",
            description="Valid email required",
            type=ConfigType.STRING,
            pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"
        ),
        ConfigField(
            key="age",
            name="Age",
            description="Must be between 18 and 120",
            type=ConfigType.INTEGER,
            min_value=18,
            max_value=120
        ),
        ConfigField(
            key="percentage",
            name="Percentage",
            description="Value between 0.0 and 1.0",
            type=ConfigType.FLOAT,
            min_value=0.0,
            max_value=1.0
        ),
        ConfigField(
            key="environment",
            name="Environment",
            description="Deployment environment",
            type=ConfigType.CHOICE,
            choices=["development", "staging", "production"],
            default="development"
        ),
    ]
    
    # Test validation
    test_values = [
        ("email", "invalid-email"),
        ("email", "user@example.com"),
        ("age", 15),
        ("age", 25),
        ("percentage", 1.5),
        ("percentage", 0.75),
        ("environment", "testing"),
        ("environment", "production"),
    ]
    
    for field in fields:
        console.print(f"\n[cyan]{field.name}[/cyan] ({field.description})")
        
        # Find test values for this field
        for key, value in test_values:
            if key == field.key:
                valid, error = field.validate(value)
                if valid:
                    console.print(f"  ✓ {value} - [green]Valid[/green]")
                else:
                    console.print(f"  ✗ {value} - [red]{error}[/red]")


def demo_config_search():
    """Demo configuration search."""
    console = Console()
    
    console.print("\n[bold]Configuration Search Demo[/bold]\n")
    
    schema = create_demo_schema()
    
    # Search terms
    search_terms = ["port", "api", "chunk", "enable"]
    
    for term in search_terms:
        console.print(f"\n[yellow]Searching for '{term}':[/yellow]")
        
        found = False
        for section in schema:
            for field in section.fields:
                if (term.lower() in field.name.lower() or
                    term.lower() in field.description.lower() or
                    term.lower() in field.key.lower()):
                    
                    console.print(f"  {section.icon} {section.title} > {field.name}")
                    console.print(f"    [dim]{field.key}: {field.description}[/dim]")
                    found = True
        
        if not found:
            console.print("  [dim]No results found[/dim]")


def main():
    """Run configuration UI demos."""
    console = Console()
    
    demos = [
        ("Configuration Editor", demo_config_editor),
        ("Configuration Wizard", demo_config_wizard),
        ("Field Validation", demo_field_validation),
        ("Configuration Search", demo_config_search),
    ]
    
    console.print("\n[bold cyan]Configuration UI Demo Suite[/bold cyan]\n")
    console.print("Explore configuration management features:\n")
    
    for i, (name, _) in enumerate(demos, 1):
        console.print(f"{i}. {name}")
    
    console.print("\nPress Ctrl+C to exit")
    
    while True:
        try:
            choice = console.input("\nSelect demo (1-4): ")
            if choice.isdigit() and 1 <= int(choice) <= len(demos):
                _, demo_func = demos[int(choice) - 1]
                demo_func()
                console.input("\nPress Enter to continue...")
            else:
                console.print("[red]Invalid choice![/red]")
        except KeyboardInterrupt:
            console.print("\n\n[dim]Goodbye![/dim]")
            break


if __name__ == "__main__":
    main()