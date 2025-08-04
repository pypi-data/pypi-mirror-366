"""Enhanced main application with interactive flow."""

import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from rich.console import Console

from .menu import MenuBuilder, InteractiveMenu
from .styles import VECTOR_DB_HEADER, WELCOME_MESSAGE, get_icon
from .file_browser import FileBrowser
from .query_builder import QueryBuilder, QueryWizard
from .progress import ProgressManager, ProgressGroup
from .config_ui import ConfigEditor, ConfigWizard
from .results import ResultViewer, SearchResult
from .navigation import NavigationManager
from .base import UIConfig, LoadingSpinner, ErrorDisplay
from .preferences import get_preferences, get_preference
from .preferences_ui import PreferencesEditor, PreferencesQuickMenu, apply_preferences
from .tutorials import InteractiveTutorial
from .onboarding import should_run_onboarding, run_onboarding
from .optimization import (
    optimize_startup, perf_monitor, cache_manager, MemoryOptimizer
)
from .polish import (
    UsageAnalytics, SmartSuggestions, StatusBar, WelcomeScreen,
    ExitConfirmation, FeatureHighlight, get_polished_error
)

from ...vector_db.service import VectorDBService
from ...document_processor.processor import DocumentProcessor
from ...utils.config import Config
from ...mcp_integration.server import VectorQueryMCPServer


class InteractiveApp:
    """Main interactive application."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize interactive app.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or Path.home() / ".vector_db_query" / "config.yaml"
        self.console = Console()
        self.ui_config = UIConfig()
        self.navigation = NavigationManager(self.console)
        self.config: Optional[Config] = None
        self.vector_service: Optional[VectorDBService] = None
        self.doc_processor: Optional[DocumentProcessor] = None
        self.mcp_server: Optional[VectorQueryMCPServer] = None
        self._session_data: Dict[str, Any] = {}
        
        # Load and apply preferences
        self.preferences = get_preferences()
        apply_preferences(self.preferences)
        self._session_data['start_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Initialize polish features
        self.analytics = UsageAnalytics()
        self.suggestions = SmartSuggestions(self.analytics)
        self.status_bar = StatusBar(self.console)
        
        # Optimize startup
        optimize_startup()
    
    async def initialize(self) -> bool:
        """Initialize application.
        
        Returns:
            Success flag
        """
        try:
            # Check for config
            if not self.config_path.exists():
                self.console.print("\n[yellow]No configuration found.[/yellow]")
                if self._confirm("Run setup wizard?", default=True):
                    await self._run_setup_wizard()
                else:
                    return False
            
            # Load config
            with LoadingSpinner("Loading configuration..."):
                self.config = Config.from_yaml(self.config_path)
            
            # Initialize services
            await self._initialize_services()
            
            return True
            
        except Exception as e:
            error_display = ErrorDisplay(
                e,
                title="Initialization Error",
                suggestions=[
                    "Check your configuration file",
                    "Verify Qdrant is running",
                    "Check API keys are valid"
                ]
            )
            error_display.render()
            return False
    
    async def _initialize_services(self) -> None:
        """Initialize backend services."""
        # Vector DB
        self.console.print("Initializing services...")
        
        with LoadingSpinner("Connecting to vector database..."):
            self.vector_service = VectorDBService(self.config)
            await self.vector_service.initialize()
        
        # Document processor
        self.doc_processor = DocumentProcessor(self.config)
        
        # MCP server (optional)
        if self.config.mcp_config.enabled:
            self.mcp_server = VectorQueryMCPServer(
                self.vector_service,
                self.config.mcp_config
            )
        
        self.console.print("[green]✓ Services initialized[/green]")
    
    async def run(self) -> None:
        """Run interactive application."""
        # Check for first-time setup
        if should_run_onboarding():
            if run_onboarding():
                self.console.print("\n[green]Setup complete! Starting application...[/green]")
                await asyncio.sleep(2)
            else:
                self.console.print("\n[yellow]Setup skipped. Some features may not work properly.[/yellow]")
                return
        
        # Initialize
        if not await self.initialize():
            return
        
        # Show welcome
        self._show_welcome()
        
        # Create main menu
        menu_builder = MenuBuilder(theme=self.ui_config.theme)
        main_menu = self._create_main_menu(menu_builder)
        
        # Run main loop
        while True:
            try:
                selection = main_menu.show()
                
                if selection is None:
                    # Check if exit confirmation is needed
                    if get_preference('confirm_exit', True):
                        if self._confirm("Exit application?"):
                            break
                    else:
                        break
                
                # Handle selection
                await self._handle_menu_selection(selection)
                
            except KeyboardInterrupt:
                if self._confirm("\nExit application?"):
                    break
            except Exception as e:
                # Track error
                self.analytics.track_error(str(e), {"context": "main_loop"})
                
                # Show polished error
                error_panel = get_polished_error("application_error", str(e))
                self.console.print(error_panel)
                
                if self._confirm("Continue?", default=True):
                    continue
                else:
                    break
        
        # Cleanup
        if await self._cleanup():
            self.console.print("\n[dim]Thank you for using Vector DB Query![/dim]")
    
    def _show_welcome(self) -> None:
        """Show welcome screen."""
        self.console.clear()
        self.console.print(VECTOR_DB_HEADER, style="bold cyan", justify="center")
        self.console.print(WELCOME_MESSAGE, justify="center")
        self.console.print()
        
        # Show stats
        if self.vector_service:
            stats = asyncio.run(self.vector_service.get_statistics())
            if stats:
                self.console.print(f"[dim]Database: {stats.get('vectors_count', 0)} vectors indexed[/dim]", justify="center")
        
        self.console.print()
    
    def _create_main_menu(self, builder: MenuBuilder) -> InteractiveMenu:
        """Create main application menu.
        
        Args:
            builder: Menu builder
            
        Returns:
            Main menu
        """
        main = builder.create_menu("main", "Main Menu")
        
        # Process documents
        builder.add_item(
            "main", "process", "Process Documents",
            handler=lambda: asyncio.run(self._process_documents()),
            description="Index new documents",
            icon=get_icon("process")
        )
        
        # Query database
        builder.add_item(
            "main", "query", "Query Database",
            handler=lambda: asyncio.run(self._query_database()),
            description="Search indexed documents",
            icon=get_icon("query")
        )
        
        # Browse documents
        builder.add_item(
            "main", "browse", "Browse Documents",
            handler=self._browse_documents,
            description="View indexed documents",
            icon=get_icon("folder")
        )
        
        builder.add_separator("main")
        
        # MCP Server
        if self.config and self.config.mcp_config.enabled:
            builder.add_item(
                "main", "mcp", "MCP Server",
                handler=self._manage_mcp,
                description="Manage AI integration",
                icon=get_icon("mcp"),
                submenu_name="mcp"
            )
            
            # MCP submenu
            mcp = builder.create_menu("mcp", "MCP Server", parent="main")
            builder.add_item(
                "mcp", "status", "Server Status",
                handler=self._mcp_status,
                description="Check server status"
            )
            builder.add_item(
                "mcp", "start", "Start Server",
                handler=lambda: asyncio.run(self._start_mcp()),
                description="Start MCP server"
            )
            builder.add_item(
                "mcp", "stop", "Stop Server",
                handler=self._stop_mcp,
                description="Stop MCP server"
            )
        
        builder.add_separator("main")
        
        # Settings
        builder.add_item(
            "main", "settings", "Settings",
            handler=self._edit_settings,
            description="Configure application",
            icon=get_icon("config"),
            submenu_name="settings"
        )
        
        # Settings submenu
        settings = builder.create_menu("settings", "Settings", parent="main")
        builder.add_item(
            "settings", "config", "Edit Configuration",
            handler=self._edit_config,
            description="Edit application configuration"
        )
        builder.add_item(
            "settings", "preferences", "User Preferences",
            handler=self._edit_preferences,
            description="Customize UI and behavior"
        )
        builder.add_item(
            "settings", "quick_prefs", "Quick Preferences",
            handler=self._quick_preferences,
            description="Toggle common settings"
        )
        
        # System status
        builder.add_item(
            "main", "status", "System Status",
            handler=lambda: asyncio.run(self._show_status()),
            description="View system information",
            icon=get_icon("status")
        )
        
        # Help
        builder.add_item(
            "main", "help", "Help & Tutorials",
            handler=self._show_help,
            description="View documentation",
            icon=get_icon("help"),
            submenu_name="help"
        )
        
        # Help submenu
        help_menu = builder.create_menu("help", "Help & Tutorials", parent="main")
        builder.add_item(
            "help", "docs", "Documentation",
            handler=self._show_documentation,
            description="View help documentation"
        )
        builder.add_item(
            "help", "tutorials", "Interactive Tutorials",
            handler=self._launch_tutorials,
            description="Learn with guided tutorials"
        )
        builder.add_item(
            "help", "shortcuts", "Keyboard Shortcuts",
            handler=self._show_shortcuts,
            description="View all shortcuts"
        )
        
        return main
    
    async def _handle_menu_selection(self, selection: str) -> None:
        """Handle menu selection.
        
        Args:
            selection: Selected menu item
        """
        # Navigation tracking
        self.navigation.navigate_to(selection, f"/{selection}")
    
    async def _process_documents(self) -> None:
        """Process documents workflow."""
        self.console.clear()
        self.console.print("[bold]Document Processing[/bold]\n")
        
        # Select files/folders
        browser = FileBrowser(
            filters=self.config.processing_config.file_extensions,
            allow_multiple=True,
            preview_enabled=True,
            show_hidden=get_preference('show_hidden_files', False),
            max_preview_lines=get_preference('file_preview_lines', 50),
            sort_by=get_preference('file_browser_sort', 'name')
        )
        
        selected_paths = browser.browse()
        
        if not selected_paths:
            self.console.print("[yellow]No files selected[/yellow]")
            return
        
        # Collect all files
        all_files = []
        for path in selected_paths:
            if path.is_dir():
                # Recursively find files
                for pattern in self.config.processing_config.file_extensions:
                    all_files.extend(path.rglob(f"*{pattern}"))
            else:
                all_files.append(path)
        
        if not all_files:
            self.console.print("[yellow]No processable files found[/yellow]")
            return
        
        # Confirm processing
        self.console.print(f"\n[cyan]Found {len(all_files)} files to process[/cyan]")
        if not self._confirm("Proceed with processing?"):
            return
        
        # Process files
        await self._process_files(all_files)
    
    async def _process_files(self, files: List[Path]) -> None:
        """Process files with progress tracking.
        
        Args:
            files: Files to process
        """
        manager = ProgressManager()
        manager.start()
        
        try:
            # Create progress group
            process_group = ProgressGroup("processing", manager)
            
            # Add tasks
            read_task = process_group.add_task("Reading files", len(files))
            chunk_task = process_group.add_task("Creating chunks", len(files) * 10)  # Estimate
            embed_task = process_group.add_task("Generating embeddings", len(files) * 10)
            store_task = process_group.add_task("Storing vectors", len(files) * 10)
            
            processed_count = 0
            error_count = 0
            
            for i, file_path in enumerate(files):
                try:
                    # Read file
                    manager.update_task(read_task, advance=1)
                    
                    # Process document
                    documents = await self.doc_processor.process_file(file_path)
                    
                    # Update chunk task
                    manager.update_task(chunk_task, advance=len(documents))
                    
                    # Process chunks
                    for doc in documents:
                        # Generate embedding
                        manager.update_task(embed_task, advance=1)
                        
                        # Store in vector DB
                        await self.vector_service.add_document(doc)
                        manager.update_task(store_task, advance=1)
                    
                    processed_count += 1
                    
                except Exception as e:
                    error_count += 1
                    self.console.print(f"[red]Error processing {file_path}: {e}[/red]")
            
            # Complete tasks
            manager.complete_task(read_task)
            manager.complete_task(chunk_task)
            manager.complete_task(embed_task)
            manager.complete_task(store_task)
            
            # Show summary
            self.console.print(f"\n[green]Processing complete![/green]")
            self.console.print(f"Processed: {processed_count} files")
            if error_count > 0:
                self.console.print(f"Errors: {error_count} files")
            
        finally:
            manager.stop()
        
        self._wait_for_enter()
    
    async def _query_database(self) -> None:
        """Query database workflow."""
        self.console.clear()
        self.console.print("[bold]Query Database[/bold]\n")
        
        # Build query
        builder = QueryBuilder()
        query = builder.build_query()
        
        if not query:
            return
        
        # Execute query
        self.console.print("\n[cyan]Searching...[/cyan]")
        
        try:
            results = await self.vector_service.search(
                query=query,
                limit=20
            )
            
            if not results:
                self.console.print("[yellow]No results found[/yellow]")
                self._wait_for_enter()
                return
            
            # Convert to SearchResult objects
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    id=result.id,
                    content=result.content,
                    score=result.score,
                    metadata=result.metadata
                ))
            
            # Display results
            viewer = ResultViewer(
                results=search_results,
                query=query,
                page_size=get_preference('page_size', 20),
                highlight_matches=get_preference('highlight_matches', True),
                default_format=get_preference('default_result_format', 'cards')
            )
            
            selected = viewer.display()
            
            if selected:
                # Show full document
                await self._view_document(selected)
            
        except Exception as e:
            self.console.print(f"[red]Search error: {e}[/red]")
            self._wait_for_enter()
    
    async def _view_document(self, result: SearchResult) -> None:
        """View full document.
        
        Args:
            result: Search result
        """
        self.console.clear()
        self.console.print(f"[bold]{result.title}[/bold]\n")
        
        # Show metadata
        for key, value in result.metadata.items():
            if key not in ["content", "embedding"]:
                self.console.print(f"[cyan]{key}:[/cyan] {value}")
        
        self.console.print(f"\n[dim]Score: {result.score:.4f}[/dim]")
        self.console.print("\n" + "─" * 80 + "\n")
        
        # Show content
        self.console.print(result.content)
        
        self._wait_for_enter()
    
    def _browse_documents(self) -> None:
        """Browse indexed documents."""
        self.console.print("[yellow]Browse feature not fully implemented[/yellow]")
        self._wait_for_enter()
    
    def _manage_mcp(self) -> None:
        """MCP management menu is handled by submenu."""
        pass
    
    def _mcp_status(self) -> None:
        """Show MCP server status."""
        self.console.clear()
        self.console.print("[bold]MCP Server Status[/bold]\n")
        
        if self.mcp_server:
            status = "Running" if hasattr(self.mcp_server, '_running') else "Stopped"
            self.console.print(f"Status: [green]{status}[/green]")
            self.console.print(f"Port: {self.config.mcp_config.port}")
            self.console.print(f"Auth Required: {self.config.mcp_config.auth_required}")
        else:
            self.console.print("[red]MCP server not initialized[/red]")
        
        self._wait_for_enter()
    
    async def _start_mcp(self) -> None:
        """Start MCP server."""
        if not self.mcp_server:
            self.console.print("[red]MCP server not initialized[/red]")
            self._wait_for_enter()
            return
        
        self.console.print("[cyan]Starting MCP server...[/cyan]")
        
        try:
            # Start server in background
            asyncio.create_task(self.mcp_server.start())
            self.console.print("[green]MCP server started![/green]")
        except Exception as e:
            self.console.print(f"[red]Failed to start server: {e}[/red]")
        
        self._wait_for_enter()
    
    def _stop_mcp(self) -> None:
        """Stop MCP server."""
        self.console.print("[yellow]MCP stop not implemented[/yellow]")
        self._wait_for_enter()
    
    def _edit_settings(self) -> None:
        """Settings menu is handled by submenu."""
        pass
    
    def _edit_config(self) -> None:
        """Edit application configuration."""
        editor = ConfigEditor(
            config_path=self.config_path,
            format="yaml"
        )
        
        if editor.edit():
            # Reload config
            self.console.print("[cyan]Reloading configuration...[/cyan]")
            self.config = Config.from_yaml(self.config_path)
            self.console.print("[green]Configuration reloaded![/green]")
            self._wait_for_enter()
    
    def _edit_preferences(self) -> None:
        """Edit user preferences."""
        editor = PreferencesEditor(self.preferences)
        
        if editor.edit():
            # Apply new preferences
            apply_preferences(self.preferences)
            self.console.print("[green]Preferences updated![/green]")
            self._wait_for_enter()
    
    def _quick_preferences(self) -> None:
        """Show quick preferences menu."""
        menu = PreferencesQuickMenu(self.preferences)
        
        if menu.show():
            # Apply changes
            apply_preferences(self.preferences)
            self.console.print("[green]Preferences updated![/green]")
            self._wait_for_enter()
    
    async def _show_status(self) -> None:
        """Show system status."""
        self.console.clear()
        self.console.print("[bold]System Status[/bold]\n")
        
        # Vector DB status
        if self.vector_service:
            stats = await self.vector_service.get_statistics()
            self.console.print("[cyan]Vector Database:[/cyan]")
            self.console.print(f"  Vectors: {stats.get('vectors_count', 0)}")
            self.console.print(f"  Collections: {stats.get('collections_count', 0)}")
            
            # Get collection info
            collection_info = await self.vector_service.get_collection_info()
            if collection_info:
                self.console.print(f"  Vector size: {collection_info.get('vector_size', 'Unknown')}")
        
        # MCP status
        self.console.print(f"\n[cyan]MCP Server:[/cyan]")
        if self.config.mcp_config.enabled:
            status = "Enabled"
            if self.mcp_server:
                status += " (Initialized)"
            self.console.print(f"  Status: {status}")
            self.console.print(f"  Port: {self.config.mcp_config.port}")
        else:
            self.console.print("  Status: Disabled")
        
        # System info
        self.console.print(f"\n[cyan]System:[/cyan]")
        self.console.print(f"  Config: {self.config_path}")
        self.console.print(f"  Session started: {self._session_data.get('start_time', 'Unknown')}")
        
        self._wait_for_enter()
    
    def _show_help(self) -> None:
        """Help menu is handled by submenu."""
        pass
    
    def _show_documentation(self) -> None:
        """Show help documentation."""
        self.console.clear()
        self.console.print("[bold]Help & Documentation[/bold]\n")
        
        help_text = """
[cyan]Quick Start:[/cyan]
1. Process Documents - Index your files into the vector database
2. Query Database - Search your indexed documents
3. Browse Documents - View and manage indexed content

[cyan]Tips:[/cyan]
• Use natural language queries for best results
• Process documents in batches for efficiency  
• Configure embedding settings for your use case
• Enable MCP for AI assistant integration

[cyan]Keyboard Shortcuts:[/cyan]
• Arrow keys - Navigate menus
• Enter - Select option
• Esc - Go back
• Ctrl+C - Exit application
• h - Show help in any menu

[cyan]Configuration:[/cyan]
Edit settings through the Settings menu or directly edit:
~/.vector_db_query/config.yaml

[cyan]Support:[/cyan]
View logs at: ~/.vector_db_query/logs/
Report issues: https://github.com/your-repo/issues
"""
        
        self.console.print(help_text)
        self._wait_for_enter()
    
    def _launch_tutorials(self) -> None:
        """Launch interactive tutorials."""
        self.console.clear()
        tutorial_app = InteractiveTutorial()
        tutorial_app.run()
    
    def _show_shortcuts(self) -> None:
        """Show keyboard shortcuts."""
        from .shortcuts import show_shortcuts
        show_shortcuts()
        self._wait_for_enter()
    
    async def _run_setup_wizard(self) -> None:
        """Run initial setup wizard."""
        from .config_ui import ConfigSection, ConfigField, ConfigType
        
        # Define minimal schema for wizard
        schema = [
            ConfigSection(
                name="database",
                title="Database Setup",
                description="Configure your vector database connection",
                fields=[
                    ConfigField(
                        key="qdrant.host",
                        name="Qdrant Host",
                        description="Hostname where Qdrant is running",
                        type=ConfigType.STRING,
                        default="localhost"
                    ),
                    ConfigField(
                        key="qdrant.port",
                        name="Qdrant Port",
                        description="Port number for Qdrant",
                        type=ConfigType.INTEGER,
                        default=6333
                    ),
                ]
            ),
            ConfigSection(
                name="embeddings",
                title="Embeddings Setup",
                description="Configure text embedding model",
                fields=[
                    ConfigField(
                        key="embeddings.api_key",
                        name="API Key",
                        description="Your Google AI API key for embeddings",
                        type=ConfigType.STRING,
                        required=True
                    ),
                ]
            ),
        ]
        
        wizard = ConfigWizard(schema)
        config_data = wizard.run()
        
        if config_data:
            # Save configuration
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create full config
            full_config = {
                "app": {"name": "Vector DB Query"},
                "qdrant": config_data.get("qdrant", {}),
                "embeddings": config_data.get("embeddings", {}),
                "processing": {
                    "chunk_size": 1000,
                    "chunk_overlap": 200,
                    "file_extensions": [".txt", ".md", ".pdf", ".doc", ".docx"]
                },
                "mcp": {
                    "enabled": False,
                    "port": 8080
                }
            }
            
            import yaml
            with open(self.config_path, 'w') as f:
                yaml.dump(full_config, f, default_flow_style=False)
            
            self.console.print("\n[green]Configuration saved![/green]")
    
    async def _cleanup(self) -> bool:
        """Cleanup resources.
        
        Returns:
            True if cleanup completed and exit confirmed
        """
        # Save analytics
        self.analytics.save_session()
        
        # Show exit confirmation with summary
        if self.preferences.get('show_exit_summary', True):
            exit_confirm = ExitConfirmation(self.analytics)
            if not exit_confirm.confirm():
                return False
        
        # Cleanup resources
        if self.vector_service:
            # Any cleanup needed
            pass
        
        # Clear caches
        cache_manager.clear()
        MemoryOptimizer.collect_garbage()
        
        return True
    
    def _confirm(self, message: str, default: bool = False) -> bool:
        """Get confirmation from user."""
        import questionary
        return questionary.confirm(message, default=default).ask()
    
    def _wait_for_enter(self) -> None:
        """Wait for user to press enter."""
        self.console.input("\nPress Enter to continue...")


def create_app(config_path: Optional[Path] = None) -> InteractiveApp:
    """Create interactive application.
    
    Args:
        config_path: Configuration file path
        
    Returns:
        Application instance
    """
    return InteractiveApp(config_path)