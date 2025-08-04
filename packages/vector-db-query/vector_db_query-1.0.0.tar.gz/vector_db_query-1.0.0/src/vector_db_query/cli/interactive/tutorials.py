"""Interactive tutorial system for guiding users through features."""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.align import Align
import questionary

from .base import BaseUIComponent
from .keyboard import KeyboardHandler, Key
from .styles import get_icon
from .animations import TransitionEffect


class TutorialLevel(Enum):
    """Tutorial difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class TutorialStep:
    """Individual tutorial step."""
    title: str
    content: str
    action: Optional[str] = None
    demo: Optional[Callable] = None
    validation: Optional[Callable[[], bool]] = None
    hint: Optional[str] = None
    
    def has_action(self) -> bool:
        """Check if step has an action."""
        return self.action is not None or self.demo is not None


@dataclass
class Tutorial:
    """Tutorial definition."""
    id: str
    name: str
    description: str
    category: str
    level: TutorialLevel
    steps: List[TutorialStep]
    duration_minutes: int = 5
    prerequisites: List[str] = None
    
    def __post_init__(self):
        """Initialize prerequisites."""
        if self.prerequisites is None:
            self.prerequisites = []


class TutorialPlayer(BaseUIComponent):
    """Interactive tutorial player."""
    
    def __init__(self, tutorial: Tutorial):
        """Initialize tutorial player.
        
        Args:
            tutorial: Tutorial to play
        """
        super().__init__()
        self.tutorial = tutorial
        self.current_step = 0
        self.completed_steps = set()
        self.keyboard = KeyboardHandler(self.console)
        self.transition = TransitionEffect()
        self.start_time = None
        self.notes: List[str] = []
    
    def play(self) -> bool:
        """Play the tutorial.
        
        Returns:
            True if completed successfully
        """
        self._show_intro()
        
        if not self._confirm_start():
            return False
        
        self.start_time = self._get_timestamp()
        
        while self.current_step < len(self.tutorial.steps):
            if not self._play_step():
                # User quit
                return self._handle_quit()
            
            self.current_step += 1
        
        return self._show_completion()
    
    def _show_intro(self) -> None:
        """Show tutorial introduction."""
        self.console.clear()
        
        # Create intro panel
        intro_content = f"""
# {self.tutorial.name}

{self.tutorial.description}

**Category:** {self.tutorial.category}  
**Level:** {self.tutorial.level.value.title()}  
**Duration:** ~{self.tutorial.duration_minutes} minutes  
**Steps:** {len(self.tutorial.steps)}
"""
        
        if self.tutorial.prerequisites:
            intro_content += f"\n**Prerequisites:**\n"
            for prereq in self.tutorial.prerequisites:
                intro_content += f"• {prereq}\n"
        
        panel = Panel(
            Markdown(intro_content),
            title=f"[bold cyan]Tutorial: {self.tutorial.name}[/bold cyan]",
            border_style="cyan"
        )
        
        self.console.print(panel)
    
    def _confirm_start(self) -> bool:
        """Confirm tutorial start."""
        return questionary.confirm(
            "\nReady to start the tutorial?",
            default=True
        ).ask()
    
    def _play_step(self) -> bool:
        """Play a single tutorial step.
        
        Returns:
            True to continue, False to quit
        """
        step = self.tutorial.steps[self.current_step]
        
        # Show step with animation
        self.transition.play("slide", 0.3)
        self._display_step(step)
        
        # Handle step action
        if step.has_action():
            if not self._handle_step_action(step):
                return False
        
        # Wait for navigation
        return self._navigate_step()
    
    def _display_step(self, step: TutorialStep) -> None:
        """Display tutorial step."""
        self.console.clear()
        
        # Progress header
        progress_text = f"Step {self.current_step + 1} of {len(self.tutorial.steps)}"
        self.console.print(
            f"[dim]{self.tutorial.name} • {progress_text}[/dim]\n"
        )
        
        # Step content
        content_panel = Panel(
            Markdown(step.content),
            title=f"[bold]{step.title}[/bold]",
            border_style="green" if self.current_step in self.completed_steps else "blue"
        )
        
        self.console.print(content_panel)
        
        # Show action hint
        if step.action:
            self.console.print(f"\n[cyan]Action:[/cyan] {step.action}")
        
        if step.hint:
            self.console.print(f"[dim]Hint: {step.hint}[/dim]")
        
        # Navigation hints
        self.console.print(
            "\n[dim]→ Next • ← Previous • Space Try It • n Notes • q Quit[/dim]"
        )
    
    def _handle_step_action(self, step: TutorialStep) -> bool:
        """Handle step action.
        
        Args:
            step: Current step
            
        Returns:
            True to continue
        """
        if step.demo:
            # Run demo
            self.console.print("\n[yellow]Press Space to try this step...[/yellow]")
            
            with self.keyboard.raw_mode():
                while True:
                    key = self.keyboard.read_key()
                    
                    if key == Key.SPACE.value:
                        self.console.clear()
                        try:
                            step.demo()
                            self.completed_steps.add(self.current_step)
                            
                            if step.validation and step.validation():
                                self.console.print("\n[green]✓ Step completed successfully![/green]")
                            else:
                                self.console.print("\n[yellow]Step completed[/yellow]")
                            
                            self.console.input("\nPress Enter to continue...")
                            return True
                            
                        except Exception as e:
                            self.console.print(f"\n[red]Error: {e}[/red]")
                            self.console.input("\nPress Enter to continue...")
                            return True
                    
                    elif key == Key.ESCAPE.value or key == 'q':
                        return False
                    elif key == Key.RIGHT.value:
                        # Skip action
                        return True
        
        return True
    
    def _navigate_step(self) -> bool:
        """Navigate between steps.
        
        Returns:
            True to continue, False to quit
        """
        with self.keyboard.raw_mode():
            while True:
                key = self.keyboard.read_key()
                
                if key == Key.RIGHT.value or key == Key.ENTER.value:
                    # Next step
                    return True
                elif key == Key.LEFT.value:
                    # Previous step
                    if self.current_step > 0:
                        self.current_step -= 2  # Will be incremented
                    return True
                elif key == Key.SPACE.value:
                    # Retry action
                    step = self.tutorial.steps[self.current_step]
                    if step.has_action():
                        self._handle_step_action(step)
                        self._display_step(step)
                elif key == 'n':
                    # Add note
                    self._add_note()
                    self._display_step(self.tutorial.steps[self.current_step])
                elif key == Key.ESCAPE.value or key == 'q':
                    return False
                elif key == '?':
                    self._show_help()
                    self._display_step(self.tutorial.steps[self.current_step])
    
    def _add_note(self) -> None:
        """Add a note for current step."""
        self.console.clear()
        note = questionary.text(
            f"Add note for step {self.current_step + 1}:",
            multiline=True
        ).ask()
        
        if note:
            self.notes.append(f"Step {self.current_step + 1}: {note}")
            self.console.print("[green]Note saved![/green]")
            self.console.input("\nPress Enter to continue...")
    
    def _show_help(self) -> None:
        """Show tutorial help."""
        help_text = """
[bold cyan]Tutorial Controls[/bold cyan]

[yellow]Navigation:[/yellow]
  → / Enter    Next step
  ←           Previous step
  
[yellow]Actions:[/yellow]
  Space       Try the step action
  n           Add a note
  
[yellow]General:[/yellow]
  ?           Show this help
  q / Esc     Quit tutorial
"""
        self.console.clear()
        self.console.print(Panel(help_text, title="Help", border_style="cyan"))
        self.console.input("\nPress Enter to continue...")
    
    def _handle_quit(self) -> bool:
        """Handle tutorial quit.
        
        Returns:
            False (tutorial not completed)
        """
        if questionary.confirm("Save progress before quitting?").ask():
            self._save_progress()
        
        self.console.print("\n[yellow]Tutorial paused[/yellow]")
        self.console.print(f"Completed {len(self.completed_steps)} of {len(self.tutorial.steps)} steps")
        
        return False
    
    def _show_completion(self) -> bool:
        """Show tutorial completion.
        
        Returns:
            True (tutorial completed)
        """
        self.console.clear()
        
        duration = self._calculate_duration()
        
        completion_text = f"""
# 🎉 Tutorial Complete!

**Tutorial:** {self.tutorial.name}  
**Duration:** {duration} minutes  
**Steps Completed:** {len(self.completed_steps)}/{len(self.tutorial.steps)}

Well done! You've completed the {self.tutorial.name} tutorial.
"""
        
        if self.notes:
            completion_text += "\n**Your Notes:**\n"
            for note in self.notes:
                completion_text += f"• {note}\n"
        
        panel = Panel(
            Markdown(completion_text),
            title="[bold green]Congratulations![/bold green]",
            border_style="green"
        )
        
        self.console.print(panel)
        
        # Save completion
        self._save_completion()
        
        self.console.input("\nPress Enter to continue...")
        return True
    
    def _save_progress(self) -> None:
        """Save tutorial progress."""
        progress_file = self._get_progress_file()
        progress_data = {
            "tutorial_id": self.tutorial.id,
            "current_step": self.current_step,
            "completed_steps": list(self.completed_steps),
            "notes": self.notes,
            "timestamp": self._get_timestamp()
        }
        
        try:
            progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            self.console.print(f"[red]Failed to save progress: {e}[/red]")
    
    def _save_completion(self) -> None:
        """Save tutorial completion."""
        completion_file = self._get_completion_file()
        completion_data = {
            "tutorial_id": self.tutorial.id,
            "completed_at": self._get_timestamp(),
            "duration_minutes": self._calculate_duration(),
            "notes": self.notes
        }
        
        try:
            # Load existing completions
            completions = []
            if completion_file.exists():
                with open(completion_file, 'r') as f:
                    completions = json.load(f)
            
            # Add new completion
            completions.append(completion_data)
            
            # Save
            completion_file.parent.mkdir(parents=True, exist_ok=True)
            with open(completion_file, 'w') as f:
                json.dump(completions, f, indent=2)
        except Exception as e:
            self.console.print(f"[red]Failed to save completion: {e}[/red]")
    
    def _get_progress_file(self) -> Path:
        """Get progress file path."""
        return Path.home() / ".vector_db_query" / "tutorial_progress" / f"{self.tutorial.id}.json"
    
    def _get_completion_file(self) -> Path:
        """Get completion file path."""
        return Path.home() / ".vector_db_query" / "tutorial_completions.json"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _calculate_duration(self) -> int:
        """Calculate tutorial duration in minutes."""
        if self.start_time:
            from datetime import datetime
            start = datetime.fromisoformat(self.start_time)
            end = datetime.now()
            return int((end - start).total_seconds() / 60)
        return 0


class TutorialManager(BaseUIComponent):
    """Manage and launch tutorials."""
    
    def __init__(self):
        """Initialize tutorial manager."""
        super().__init__()
        self.tutorials: Dict[str, Tutorial] = {}
        self.completed_tutorials: List[str] = []
        self._load_tutorials()
        self._load_completions()
    
    def _load_tutorials(self) -> None:
        """Load available tutorials."""
        # Create built-in tutorials
        self._create_builtin_tutorials()
    
    def _create_builtin_tutorials(self) -> None:
        """Create built-in tutorials."""
        # Getting Started tutorial
        self.add_tutorial(Tutorial(
            id="getting_started",
            name="Getting Started",
            description="Learn the basics of Vector DB Query system",
            category="Basics",
            level=TutorialLevel.BEGINNER,
            duration_minutes=10,
            steps=[
                TutorialStep(
                    title="Welcome to Vector DB Query",
                    content="""
Welcome to the Vector DB Query interactive tutorial!

This system helps you:
• Process documents into searchable vectors
• Query your documents using natural language
• Integrate with AI assistants via MCP

Let's start by exploring the main menu.
"""
                ),
                TutorialStep(
                    title="Understanding the Main Menu",
                    content="""
The main menu provides access to all features:

1. **Process Documents** - Convert files to vectors
2. **Query Database** - Search your documents
3. **Browse Documents** - View indexed content
4. **Settings** - Configure the application
5. **System Status** - Check system health

Navigate using arrow keys and Enter to select.
""",
                    action="Try navigating the menu",
                    hint="Use ↑↓ arrows and Enter"
                ),
                TutorialStep(
                    title="Processing Your First Document",
                    content="""
To process documents:

1. Select "Process Documents" from the main menu
2. Browse and select files to process
3. Confirm processing
4. Watch the progress bars

The system will:
• Read your files
• Split them into chunks
• Generate embeddings
• Store in the vector database
""",
                    action="Process a sample document"
                ),
                TutorialStep(
                    title="Querying Your Documents",
                    content="""
Once documents are processed, you can query them:

1. Select "Query Database"
2. Enter a natural language question
3. View results in different formats
4. Export results if needed

The system uses semantic search to find relevant content.
""",
                    action="Try a sample query"
                ),
                TutorialStep(
                    title="Congratulations!",
                    content="""
You've completed the basics! 

**Next steps:**
• Process more documents
• Try advanced queries
• Configure your preferences
• Set up MCP integration

Check out the other tutorials for more advanced features.
"""
                )
            ]
        ))
        
        # File Processing tutorial
        self.add_tutorial(Tutorial(
            id="file_processing",
            name="File Processing Deep Dive",
            description="Master document processing and chunking strategies",
            category="Processing",
            level=TutorialLevel.INTERMEDIATE,
            duration_minutes=15,
            prerequisites=["Getting Started"],
            steps=[
                TutorialStep(
                    title="File Types and Formats",
                    content="""
Vector DB Query supports multiple file formats:

• **Text files**: .txt, .md, .rst
• **Documents**: .pdf, .doc, .docx
• **Code files**: .py, .js, .java, etc.
• **Data files**: .csv, .json, .xml

Each format has specialized processors for optimal results.
"""
                ),
                TutorialStep(
                    title="Understanding Chunking",
                    content="""
Documents are split into chunks for processing:

• **Chunk Size**: Number of tokens per chunk (default: 1000)
• **Overlap**: Tokens shared between chunks (default: 200)

Chunking strategies:
• Semantic: Preserve meaning boundaries
• Fixed-size: Consistent chunk sizes
• Sentence-based: Natural language boundaries
""",
                    action="View chunking configuration"
                ),
                TutorialStep(
                    title="Batch Processing",
                    content="""
Process multiple files efficiently:

1. Select entire directories
2. Use filters for specific file types
3. Preview files before processing
4. Monitor progress with detailed stats

**Tip**: Process similar documents together for better organization.
""",
                    action="Try batch processing"
                ),
                TutorialStep(
                    title="Metadata Extraction",
                    content="""
Metadata enhances search capabilities:

• File name and path
• Creation/modification dates
• Document title and author
• Custom tags and categories

Metadata is searchable and helps filter results.
"""
                ),
                TutorialStep(
                    title="Processing Best Practices",
                    content="""
**Best practices:**

1. Organize files by topic before processing
2. Use consistent naming conventions
3. Set appropriate chunk sizes for your content
4. Monitor processing errors
5. Verify results with test queries

Regular maintenance keeps your database optimal.
"""
                )
            ]
        ))
        
        # Query Mastery tutorial
        self.add_tutorial(Tutorial(
            id="query_mastery",
            name="Query Mastery",
            description="Advanced query techniques and search strategies",
            category="Querying",
            level=TutorialLevel.INTERMEDIATE,
            duration_minutes=12,
            prerequisites=["Getting Started"],
            steps=[
                TutorialStep(
                    title="Natural Language Queries",
                    content="""
Write queries as you would ask a colleague:

• "What are the main features of the authentication system?"
• "How do I configure database connections?"
• "Show me examples of error handling"

The system understands context and intent.
""",
                    action="Try natural language queries"
                ),
                TutorialStep(
                    title="Query Templates",
                    content="""
Use templates for consistent queries:

• **Code Search**: "Find {language} code for {feature}"
• **Documentation**: "Explain how to {task}"
• **Troubleshooting**: "Debug {error} in {component}"

Save frequently used templates for quick access.
""",
                    action="Create a query template"
                ),
                TutorialStep(
                    title="Advanced Filters",
                    content="""
Refine results with filters:

• **Date Range**: Recent documents only
• **File Type**: Specific formats
• **Metadata**: Tags, authors, categories
• **Score Threshold**: Minimum relevance

Combine filters for precise results.
""",
                    action="Apply search filters"
                ),
                TutorialStep(
                    title="Result Analysis",
                    content="""
Analyze search results effectively:

1. **Score**: Higher = more relevant (0.0-1.0)
2. **Context**: Surrounding text for clarity
3. **Source**: Original file location
4. **Metadata**: Additional information

Export results for further analysis.
""",
                    action="Analyze search results"
                ),
                TutorialStep(
                    title="Query Optimization",
                    content="""
**Tips for better queries:**

• Be specific with technical terms
• Include context when needed
• Use examples in your queries
• Iterate and refine based on results
• Save successful queries for reuse

Practice improves query quality!
"""
                )
            ]
        ))
        
        # MCP Integration tutorial
        self.add_tutorial(Tutorial(
            id="mcp_integration",
            name="MCP Integration",
            description="Connect AI assistants to your knowledge base",
            category="Integration",
            level=TutorialLevel.ADVANCED,
            duration_minutes=20,
            prerequisites=["Getting Started", "Query Mastery"],
            steps=[
                TutorialStep(
                    title="Understanding MCP",
                    content="""
Model Context Protocol (MCP) enables AI integration:

• **Purpose**: Let AI assistants query your documents
• **Security**: Token-based authentication
• **Protocol**: Structured request/response format
• **Clients**: Claude, custom implementations

MCP bridges your knowledge base with AI tools.
"""
                ),
                TutorialStep(
                    title="Server Configuration",
                    content="""
Configure the MCP server:

1. Set server port (default: 8080)
2. Enable authentication
3. Configure CORS if needed
4. Set rate limits

Security is crucial for production use.
""",
                    action="View MCP configuration"
                ),
                TutorialStep(
                    title="Starting the Server",
                    content="""
Launch the MCP server:

```bash
vector-db-query mcp start
```

The server will:
• Initialize on configured port
• Load authentication tokens
• Start accepting connections
• Log all requests

Monitor logs for debugging.
""",
                    action="Start MCP server"
                ),
                TutorialStep(
                    title="Client Authentication",
                    content="""
Create client credentials:

```bash
vector-db-query mcp auth create-client --name "claude"
```

This generates:
• Client ID
• Authentication token
• Configuration snippet

Keep tokens secure!
""",
                    action="Create test client"
                ),
                TutorialStep(
                    title="Testing Integration",
                    content="""
Test the MCP connection:

1. Use the built-in test command
2. Send a sample query
3. Verify response format
4. Check server logs

```bash
vector-db-query mcp test
```

Successful tests confirm proper setup.
""",
                    action="Run connection test"
                ),
                TutorialStep(
                    title="Production Deployment",
                    content="""
**Production checklist:**

✓ Enable HTTPS/TLS
✓ Set strong authentication
✓ Configure rate limiting
✓ Set up monitoring
✓ Regular token rotation
✓ Audit logging

Security and reliability are paramount.
"""
                )
            ]
        ))
        
        # Keyboard Shortcuts tutorial
        self.add_tutorial(Tutorial(
            id="keyboard_shortcuts",
            name="Keyboard Shortcuts",
            description="Master keyboard navigation for efficiency",
            category="Navigation",
            level=TutorialLevel.BEGINNER,
            duration_minutes=8,
            steps=[
                TutorialStep(
                    title="Basic Navigation",
                    content="""
Essential navigation keys:

• **↑↓**: Move up/down in lists
• **←→**: Navigate between panels
• **Enter**: Select/confirm
• **Esc**: Go back/cancel
• **Tab**: Next field

These work throughout the application.
""",
                    action="Practice navigation keys"
                ),
                TutorialStep(
                    title="Menu Shortcuts",
                    content="""
Quick menu access:

• **1-9**: Select menu items directly
• **/**: Search menu items
• **h**: Show help
• **b**: Show breadcrumbs
• **q**: Quit/back

Speed up your workflow!
""",
                    action="Try menu shortcuts"
                ),
                TutorialStep(
                    title="File Browser Shortcuts",
                    content="""
File operations:

• **Space**: Toggle selection
• **a**: Select all
• **d**: Done selecting
• **p**: Toggle preview
• **h**: Show/hide hidden files
• **s**: Change sort order

Navigate files efficiently.
""",
                    action="Use file browser shortcuts"
                ),
                TutorialStep(
                    title="Query Builder Shortcuts",
                    content="""
Query shortcuts:

• **Ctrl+H**: Show history
• **Ctrl+T**: Templates
• **Ctrl+S**: Save query
• **Ctrl+L**: Clear
• **Tab**: Suggestions

Build queries faster!
""",
                    action="Try query shortcuts"
                ),
                TutorialStep(
                    title="Global Shortcuts",
                    content="""
Available everywhere:

• **?**: Show help/shortcuts
• **Ctrl+C**: Exit application
• **Ctrl+L**: Clear screen

**Tip**: Enable Vim bindings in preferences for advanced users.
"""
                )
            ]
        ))
    
    def add_tutorial(self, tutorial: Tutorial) -> None:
        """Add a tutorial.
        
        Args:
            tutorial: Tutorial to add
        """
        self.tutorials[tutorial.id] = tutorial
    
    def _load_completions(self) -> None:
        """Load completed tutorials."""
        completion_file = Path.home() / ".vector_db_query" / "tutorial_completions.json"
        
        if completion_file.exists():
            try:
                with open(completion_file, 'r') as f:
                    completions = json.load(f)
                    self.completed_tutorials = [c["tutorial_id"] for c in completions]
            except:
                pass
    
    def list_tutorials(self) -> List[Tutorial]:
        """List available tutorials.
        
        Returns:
            List of tutorials
        """
        return list(self.tutorials.values())
    
    def get_tutorial(self, tutorial_id: str) -> Optional[Tutorial]:
        """Get a tutorial by ID.
        
        Args:
            tutorial_id: Tutorial ID
            
        Returns:
            Tutorial or None
        """
        return self.tutorials.get(tutorial_id)
    
    def is_completed(self, tutorial_id: str) -> bool:
        """Check if tutorial is completed.
        
        Args:
            tutorial_id: Tutorial ID
            
        Returns:
            True if completed
        """
        return tutorial_id in self.completed_tutorials
    
    def show_menu(self) -> Optional[Tutorial]:
        """Show tutorial selection menu.
        
        Returns:
            Selected tutorial or None
        """
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold cyan]Interactive Tutorials[/bold cyan]\n"
            "[dim]Learn Vector DB Query features step by step[/dim]",
            border_style="cyan"
        ))
        
        # Group by category
        categories: Dict[str, List[Tutorial]] = {}
        for tutorial in self.tutorials.values():
            if tutorial.category not in categories:
                categories[tutorial.category] = []
            categories[tutorial.category].append(tutorial)
        
        # Build choices
        choices = []
        for category in sorted(categories.keys()):
            choices.append(f"\n[{category}]")
            
            for tutorial in categories[category]:
                # Status icon
                if self.is_completed(tutorial.id):
                    status = "[green]✓[/green]"
                else:
                    status = "○"
                
                # Level indicator
                level_color = {
                    TutorialLevel.BEGINNER: "green",
                    TutorialLevel.INTERMEDIATE: "yellow",
                    TutorialLevel.ADVANCED: "red"
                }[tutorial.level]
                
                level_str = f"[{level_color}]{tutorial.level.value}[/{level_color}]"
                
                choice = f"{status} {tutorial.name} ({level_str}) - {tutorial.duration_minutes}min"
                choices.append(choice)
        
        choices.extend(["", "View Progress", "Reset Progress", "Exit"])
        
        # Show menu
        choice = questionary.select(
            "Select a tutorial:",
            choices=choices
        ).ask()
        
        if choice == "Exit" or not choice:
            return None
        elif choice == "View Progress":
            self._show_progress()
            return self.show_menu()
        elif choice == "Reset Progress":
            if self._reset_progress():
                self.console.print("[yellow]Progress reset![/yellow]")
                self.console.input("\nPress Enter to continue...")
            return self.show_menu()
        elif choice and not choice.startswith("["):
            # Extract tutorial name
            name = choice.split(" - ")[0].split(" ", 1)[1].rsplit(" (", 1)[0]
            
            # Find tutorial
            for tutorial in self.tutorials.values():
                if tutorial.name == name:
                    return tutorial
        
        return None
    
    def _show_progress(self) -> None:
        """Show tutorial progress."""
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold cyan]Tutorial Progress[/bold cyan]",
            border_style="cyan"
        ))
        
        total = len(self.tutorials)
        completed = len(self.completed_tutorials)
        percentage = int((completed / total) * 100) if total > 0 else 0
        
        self.console.print(f"\nCompleted: {completed}/{total} ({percentage}%)\n")
        
        # Show completion details
        completion_file = Path.home() / ".vector_db_query" / "tutorial_completions.json"
        
        if completion_file.exists():
            try:
                with open(completion_file, 'r') as f:
                    completions = json.load(f)
                
                from rich.table import Table
                
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Tutorial", style="cyan")
                table.add_column("Completed", style="green")
                table.add_column("Duration", style="yellow")
                
                for comp in completions:
                    tutorial = self.get_tutorial(comp["tutorial_id"])
                    if tutorial:
                        table.add_row(
                            tutorial.name,
                            comp["completed_at"][:10],
                            f"{comp['duration_minutes']} min"
                        )
                
                self.console.print(table)
            except:
                pass
        
        self.console.input("\nPress Enter to continue...")
    
    def _reset_progress(self) -> bool:
        """Reset all progress.
        
        Returns:
            True if reset
        """
        if not questionary.confirm("Reset all tutorial progress?").ask():
            return False
        
        # Clear completion file
        completion_file = Path.home() / ".vector_db_query" / "tutorial_completions.json"
        if completion_file.exists():
            completion_file.unlink()
        
        # Clear progress files
        progress_dir = Path.home() / ".vector_db_query" / "tutorial_progress"
        if progress_dir.exists():
            for file in progress_dir.glob("*.json"):
                file.unlink()
        
        self.completed_tutorials.clear()
        return True


class InteractiveTutorial:
    """Main tutorial interface."""
    
    def __init__(self):
        """Initialize tutorial interface."""
        self.manager = TutorialManager()
        self.console = Console()
    
    def run(self) -> None:
        """Run tutorial interface."""
        while True:
            tutorial = self.manager.show_menu()
            
            if not tutorial:
                break
            
            # Check prerequisites
            if tutorial.prerequisites:
                missing = [p for p in tutorial.prerequisites 
                          if not any(t.name == p and self.manager.is_completed(t.id) 
                                   for t in self.manager.list_tutorials())]
                
                if missing:
                    self.console.print(f"\n[yellow]Missing prerequisites: {', '.join(missing)}[/yellow]")
                    if not questionary.confirm("Continue anyway?").ask():
                        continue
            
            # Play tutorial
            player = TutorialPlayer(tutorial)
            if player.play():
                self.console.print("\n[green]Tutorial completed successfully![/green]")
            else:
                self.console.print("\n[yellow]Tutorial paused[/yellow]")
            
            self.console.input("\nPress Enter to continue...")
        
        self.console.print("\n[dim]Thanks for learning![/dim]")