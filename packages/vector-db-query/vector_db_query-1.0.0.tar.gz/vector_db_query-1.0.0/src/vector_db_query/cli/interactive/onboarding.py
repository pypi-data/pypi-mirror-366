"""First-time user onboarding experience."""

from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
import questionary

from .base import BaseUIComponent
from .styles import VECTOR_DB_HEADER, get_icon
from .config_ui import ConfigWizard, ConfigSection, ConfigField, ConfigType
from .preferences import get_preferences, set_preference
from .tutorials import TutorialManager, TutorialPlayer


class OnboardingWizard(BaseUIComponent):
    """Guide new users through initial setup."""
    
    def __init__(self):
        """Initialize onboarding wizard."""
        super().__init__()
        self.completed_steps = []
        self.user_data = {}
        self.config_path = Path.home() / ".vector_db_query"
    
    def run(self) -> bool:
        """Run onboarding wizard.
        
        Returns:
            True if completed successfully
        """
        # Check if onboarding is needed
        if not self._needs_onboarding():
            return True
        
        # Welcome screen
        if not self._show_welcome():
            return False
        
        # Run onboarding steps
        steps = [
            ("profile", "User Profile", self._setup_profile),
            ("config", "Initial Configuration", self._setup_config),
            ("preferences", "Preferences", self._setup_preferences),
            ("tutorial", "Quick Tutorial", self._offer_tutorial),
            ("complete", "Complete Setup", self._complete_setup),
        ]
        
        for step_id, step_name, step_func in steps:
            self.console.clear()
            self.console.print(f"[bold cyan]Step: {step_name}[/bold cyan]\n")
            
            if not step_func():
                # User cancelled
                return self._handle_cancel()
            
            self.completed_steps.append(step_id)
        
        return True
    
    def _needs_onboarding(self) -> bool:
        """Check if onboarding is needed.
        
        Returns:
            True if onboarding should run
        """
        # Check for onboarding completion marker
        marker_file = self.config_path / ".onboarding_complete"
        if marker_file.exists():
            return False
        
        # Check if config exists
        config_file = self.config_path / "config.yaml"
        if config_file.exists():
            # Existing user, don't force onboarding
            return False
        
        return True
    
    def _show_welcome(self) -> bool:
        """Show welcome screen.
        
        Returns:
            True to continue
        """
        self.console.clear()
        
        # Animated header
        self.console.print(Align.center(VECTOR_DB_HEADER))
        
        welcome_text = """
[bold cyan]Welcome to Vector DB Query![/bold cyan]

Transform your documents into an AI-powered knowledge base.

This wizard will help you:
• Set up your profile
• Configure the system
• Customize your preferences  
• Learn the basics

It only takes a few minutes!
"""
        
        panel = Panel(
            Align.center(welcome_text),
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        return questionary.confirm(
            "\nReady to get started?",
            default=True
        ).ask()
    
    def _setup_profile(self) -> bool:
        """Set up user profile.
        
        Returns:
            True to continue
        """
        self.console.print("Let's set up your profile.\n")
        
        # Get user information
        self.user_data["name"] = questionary.text(
            "What should I call you?",
            default="User"
        ).ask()
        
        if not self.user_data["name"]:
            return False
        
        # Experience level
        self.user_data["experience"] = questionary.select(
            f"\nHi {self.user_data['name']}! What's your experience level?",
            choices=[
                "Beginner - New to vector databases",
                "Intermediate - Some experience with search/AI",
                "Advanced - Familiar with embeddings and LLMs"
            ]
        ).ask()
        
        # Primary use case
        self.user_data["use_case"] = questionary.select(
            "\nWhat's your primary use case?",
            choices=[
                "Personal knowledge management",
                "Code/documentation search",
                "Research and analysis",
                "AI assistant integration",
                "Other"
            ]
        ).ask()
        
        self.console.print(f"\n[green]Great! Profile created for {self.user_data['name']}[/green]")
        return True
    
    def _setup_config(self) -> bool:
        """Set up initial configuration.
        
        Returns:
            True to continue
        """
        self.console.print("Now let's configure the core settings.\n")
        
        # Define minimal config schema
        schema = [
            ConfigSection(
                name="database",
                title="Vector Database",
                description="Configure your vector database connection",
                fields=[
                    ConfigField(
                        key="qdrant.host",
                        name="Database Host",
                        description="Where is Qdrant running? (use 'localhost' for local)",
                        type=ConfigType.STRING,
                        default="localhost",
                        required=True
                    ),
                    ConfigField(
                        key="qdrant.port",
                        name="Database Port",
                        description="Qdrant port number",
                        type=ConfigType.INTEGER,
                        default=6333,
                        required=True
                    ),
                ]
            ),
            ConfigSection(
                name="embeddings",
                title="Embeddings",
                description="Configure text embedding generation",
                fields=[
                    ConfigField(
                        key="embeddings.provider",
                        name="Provider",
                        description="Which embedding provider to use",
                        type=ConfigType.CHOICE,
                        choices=["google", "openai", "local"],
                        default="google",
                        required=True
                    ),
                    ConfigField(
                        key="embeddings.api_key",
                        name="API Key",
                        description="Your API key (leave empty for local)",
                        type=ConfigType.STRING,
                        required=False,
                        sensitive=True
                    ),
                ]
            ),
        ]
        
        # Run config wizard
        wizard = ConfigWizard(schema)
        config_data = wizard.run()
        
        if not config_data:
            return False
        
        # Save configuration
        self._save_config(config_data)
        
        self.console.print("\n[green]✓ Configuration saved![/green]")
        return True
    
    def _setup_preferences(self) -> bool:
        """Set up user preferences.
        
        Returns:
            True to continue
        """
        self.console.print("Let's customize your experience.\n")
        
        # Quick preference setup
        prefs = [
            ("theme", "Color Theme", ["monokai", "dracula", "github-dark", "solarized-dark"]),
            ("show_icons", "Show Icons", None),  # Boolean
            ("use_animations", "Enable Animations", None),  # Boolean
            ("page_size", "Results per Page", ["10", "20", "50"]),
        ]
        
        for key, name, choices in prefs:
            if choices is None:
                # Boolean preference
                value = questionary.confirm(f"{name}?", default=True).ask()
            elif all(c.isdigit() for c in choices):
                # Numeric choice
                value = questionary.select(f"{name}:", choices=choices).ask()
                value = int(value)
            else:
                # String choice
                value = questionary.select(f"{name}:", choices=choices).ask()
            
            set_preference(key, value)
        
        # Enable beginner-friendly settings based on experience
        if "Beginner" in self.user_data.get("experience", ""):
            set_preference("show_keyboard_hints", True)
            set_preference("confirm_exit", True)
            self.console.print("\n[dim]Enabled beginner-friendly settings[/dim]")
        
        get_preferences().save()
        self.console.print("\n[green]✓ Preferences saved![/green]")
        return True
    
    def _offer_tutorial(self) -> bool:
        """Offer to run getting started tutorial.
        
        Returns:
            True to continue
        """
        self.console.print("Would you like a quick tour of the main features?\n")
        
        if questionary.confirm("Run the Getting Started tutorial?", default=True).ask():
            # Get tutorial
            manager = TutorialManager()
            tutorial = manager.get_tutorial("getting_started")
            
            if tutorial:
                # Play tutorial
                player = TutorialPlayer(tutorial)
                player.play()
            
        return True
    
    def _complete_setup(self) -> bool:
        """Complete onboarding setup.
        
        Returns:
            True (always)
        """
        # Save onboarding data
        self._save_onboarding_data()
        
        # Show completion screen
        self.console.clear()
        
        completion_text = f"""
[bold green]🎉 Setup Complete![/bold green]

Welcome aboard, {self.user_data.get('name', 'User')}!

You're all set to start using Vector DB Query.

[cyan]Quick tips to get started:[/cyan]
• Use 'vector-db-query' to launch the app
• Press '?' anytime to see keyboard shortcuts
• Check out the tutorials for advanced features

[dim]Your configuration has been saved to:
{self.config_path}[/dim]
"""
        
        panel = Panel(
            Align.center(completion_text),
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        # Mark onboarding complete
        marker_file = self.config_path / ".onboarding_complete"
        marker_file.touch()
        
        self.console.input("\nPress Enter to start using Vector DB Query...")
        return True
    
    def _handle_cancel(self) -> bool:
        """Handle onboarding cancellation.
        
        Returns:
            False (cancelled)
        """
        self.console.clear()
        self.console.print("[yellow]Onboarding cancelled[/yellow]\n")
        
        if self.completed_steps:
            self.console.print(f"Completed steps: {', '.join(self.completed_steps)}")
            
            if questionary.confirm("\nSave partial progress?").ask():
                self._save_onboarding_data()
                self.console.print("[green]Progress saved![/green]")
        
        self.console.print("\nYou can run onboarding again anytime with:")
        self.console.print("[cyan]vector-db-query onboarding[/cyan]")
        
        return False
    
    def _save_config(self, config_data: Dict[str, Any]) -> None:
        """Save configuration data.
        
        Args:
            config_data: Configuration data
        """
        import yaml
        
        # Create full config structure
        full_config = {
            "app": {
                "name": "Vector DB Query",
                "version": "1.0.0"
            },
            "qdrant": config_data.get("qdrant", {}),
            "embeddings": config_data.get("embeddings", {}),
            "processing": {
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "file_extensions": [".txt", ".md", ".pdf", ".doc", ".docx"]
            },
            "mcp": {
                "enabled": False,
                "port": 8080,
                "auth_required": True
            }
        }
        
        # Save to file
        self.config_path.mkdir(parents=True, exist_ok=True)
        config_file = self.config_path / "config.yaml"
        
        with open(config_file, 'w') as f:
            yaml.dump(full_config, f, default_flow_style=False)
    
    def _save_onboarding_data(self) -> None:
        """Save onboarding data."""
        import json
        
        data = {
            "completed_at": datetime.now().isoformat(),
            "completed_steps": self.completed_steps,
            "user_data": self.user_data
        }
        
        data_file = self.config_path / ".onboarding_data.json"
        
        try:
            self.config_path.mkdir(parents=True, exist_ok=True)
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass


class QuickStart(BaseUIComponent):
    """Quick start guide for returning users."""
    
    def show(self) -> None:
        """Show quick start guide."""
        self.console.clear()
        
        guide_text = """
[bold cyan]Quick Start Guide[/bold cyan]

[yellow]1. Start Qdrant:[/yellow]
   docker run -p 6333:6333 qdrant/qdrant

[yellow]2. Process Documents:[/yellow]
   vector-db-query process /path/to/docs

[yellow]3. Query Your Data:[/yellow]
   vector-db-query query "your question"

[yellow]4. Interactive Mode:[/yellow]
   vector-db-query interactive

[yellow]5. MCP Integration:[/yellow]
   vector-db-query mcp start

[dim]For detailed help: vector-db-query --help[/dim]
"""
        
        panel = Panel(
            guide_text,
            title="[bold]Vector DB Query Quick Start[/bold]",
            border_style="blue"
        )
        
        self.console.print(panel)
        self.console.input("\nPress Enter to continue...")


def should_run_onboarding() -> bool:
    """Check if onboarding should run.
    
    Returns:
        True if onboarding is needed
    """
    wizard = OnboardingWizard()
    return wizard._needs_onboarding()


def run_onboarding() -> bool:
    """Run the onboarding wizard.
    
    Returns:
        True if completed successfully
    """
    wizard = OnboardingWizard()
    return wizard.run()


def show_quick_start() -> None:
    """Show quick start guide."""
    guide = QuickStart()
    guide.show()