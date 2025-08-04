"""Demo script for the tutorial system."""

from rich.console import Console
from rich.panel import Panel

from .tutorials import (
    Tutorial, TutorialStep, TutorialLevel,
    TutorialManager, TutorialPlayer, InteractiveTutorial
)
from .tutorial_demos import get_demo
from .onboarding import OnboardingWizard, show_quick_start


def demo_tutorial_creation():
    """Demo creating a custom tutorial."""
    console = Console()
    
    console.clear()
    console.print("[bold]Tutorial Creation Demo[/bold]\n")
    
    # Create a sample tutorial
    tutorial = Tutorial(
        id="demo_tutorial",
        name="Demo Tutorial",
        description="This demonstrates tutorial creation",
        category="Demo",
        level=TutorialLevel.BEGINNER,
        duration_minutes=3,
        steps=[
            TutorialStep(
                title="Welcome",
                content="This is a demo tutorial to show how tutorials work."
            ),
            TutorialStep(
                title="Interactive Steps",
                content="Steps can have actions that users can try.",
                action="Press Space to see a demo",
                demo=lambda: console.print("[green]Demo action executed![/green]")
            ),
            TutorialStep(
                title="Validation",
                content="Steps can validate if completed correctly.",
                action="Complete this step",
                demo=lambda: True,
                validation=lambda: True,
                hint="This step always validates as complete"
            ),
            TutorialStep(
                title="Complete",
                content="You've completed the demo tutorial!"
            )
        ]
    )
    
    console.print("Created tutorial with:")
    console.print(f"  Name: {tutorial.name}")
    console.print(f"  Steps: {len(tutorial.steps)}")
    console.print(f"  Duration: {tutorial.duration_minutes} minutes")
    
    if console.input("\n[bold]Play this tutorial? (y/n):[/bold] ").lower() == 'y':
        player = TutorialPlayer(tutorial)
        player.play()


def demo_tutorial_manager():
    """Demo tutorial manager functionality."""
    console = Console()
    
    console.clear()
    console.print("[bold]Tutorial Manager Demo[/bold]\n")
    
    manager = TutorialManager()
    
    # Show available tutorials
    tutorials = manager.list_tutorials()
    console.print(f"Available tutorials: {len(tutorials)}\n")
    
    # Group by category
    categories = {}
    for tutorial in tutorials:
        if tutorial.category not in categories:
            categories[tutorial.category] = []
        categories[tutorial.category].append(tutorial)
    
    for category, tuts in categories.items():
        console.print(f"[cyan]{category}:[/cyan]")
        for tut in tuts:
            status = "✓" if manager.is_completed(tut.id) else "○"
            console.print(f"  {status} {tut.name} ({tut.level.value})")
    
    console.input("\nPress Enter to continue...")


def demo_tutorial_player():
    """Demo tutorial player features."""
    console = Console()
    
    console.clear()
    console.print("[bold]Tutorial Player Demo[/bold]\n")
    
    console.print("The tutorial player provides:")
    console.print("• Step-by-step guidance")
    console.print("• Interactive demos")
    console.print("• Progress tracking")
    console.print("• Note-taking ability")
    console.print("• Navigation controls")
    
    console.print("\n[cyan]Controls:[/cyan]")
    console.print("  → Next step")
    console.print("  ← Previous step")
    console.print("  Space - Try action")
    console.print("  n - Add note")
    console.print("  q - Quit")
    
    if console.input("\n[bold]Launch a tutorial? (y/n):[/bold] ").lower() == 'y':
        manager = TutorialManager()
        tutorial = manager.get_tutorial("keyboard_shortcuts")
        
        if tutorial:
            player = TutorialPlayer(tutorial)
            player.play()


def demo_interactive_tutorial():
    """Demo the full interactive tutorial system."""
    console = Console()
    
    console.clear()
    console.print("[bold]Interactive Tutorial System Demo[/bold]\n")
    
    console.print("The interactive tutorial system provides:")
    console.print("• Tutorial selection menu")
    console.print("• Progress tracking")
    console.print("• Prerequisite checking")
    console.print("• Completion certificates")
    
    if console.input("\n[bold]Launch tutorial system? (y/n):[/bold] ").lower() == 'y':
        tutorial_app = InteractiveTutorial()
        tutorial_app.run()


def demo_onboarding():
    """Demo onboarding wizard."""
    console = Console()
    
    console.clear()
    console.print("[bold]Onboarding Wizard Demo[/bold]\n")
    
    console.print("The onboarding wizard guides new users through:")
    console.print("• Profile setup")
    console.print("• Initial configuration")
    console.print("• Preference customization")
    console.print("• Getting started tutorial")
    
    console.print("\n[yellow]Note: This is a demo - it won't save real config[/yellow]")
    
    if console.input("\n[bold]Run onboarding wizard? (y/n):[/bold] ").lower() == 'y':
        # Create demo wizard (won't actually save)
        wizard = OnboardingWizard()
        wizard.config_path = Path("/tmp/demo_onboarding")
        wizard.run()


def demo_tutorial_progress():
    """Demo tutorial progress tracking."""
    console = Console()
    
    console.clear()
    console.print("[bold]Tutorial Progress Demo[/bold]\n")
    
    # Create mock progress data
    from datetime import datetime, timedelta
    import json
    from pathlib import Path
    
    # Mock completion data
    completions = [
        {
            "tutorial_id": "getting_started",
            "completed_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "duration_minutes": 12,
            "notes": ["Great introduction!", "Loved the examples"]
        },
        {
            "tutorial_id": "keyboard_shortcuts",
            "completed_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "duration_minutes": 8,
            "notes": []
        }
    ]
    
    # Display progress
    console.print("[cyan]Completed Tutorials:[/cyan]\n")
    
    from rich.table import Table
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Tutorial", style="cyan")
    table.add_column("Completed", style="green")
    table.add_column("Duration", style="yellow")
    table.add_column("Notes", style="dim")
    
    for comp in completions:
        table.add_row(
            comp["tutorial_id"].replace("_", " ").title(),
            comp["completed_at"][:10],
            f"{comp['duration_minutes']} min",
            f"{len(comp['notes'])} notes"
        )
    
    console.print(table)
    
    # Show overall progress
    total_tutorials = 5
    completed = len(completions)
    percentage = int((completed / total_tutorials) * 100)
    
    console.print(f"\n[bold]Overall Progress:[/bold] {completed}/{total_tutorials} ({percentage}%)")
    
    # Progress bar
    from rich.progress import Progress, BarColumn, TextColumn
    
    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task("Tutorial Completion", total=total_tutorials)
        progress.update(task, completed=completed)
    
    console.input("\nPress Enter to continue...")


def demo_quick_start():
    """Demo quick start guide."""
    console = Console()
    
    console.clear()
    console.print("[bold]Quick Start Guide Demo[/bold]\n")
    
    console.print("The quick start guide provides:")
    console.print("• Essential commands")
    console.print("• Common workflows")
    console.print("• Tips and tricks")
    
    if console.input("\n[bold]Show quick start guide? (y/n):[/bold] ").lower() == 'y':
        show_quick_start()


def demo_custom_tutorial_with_actions():
    """Demo creating tutorial with linked actions."""
    console = Console()
    
    console.clear()
    console.print("[bold]Tutorial with Actions Demo[/bold]\n")
    
    # Create tutorial with actual demo functions
    tutorial = Tutorial(
        id="actions_demo",
        name="Interactive Actions Demo",
        description="Tutorial showing interactive actions",
        category="Demo",
        level=TutorialLevel.INTERMEDIATE,
        duration_minutes=5,
        steps=[
            TutorialStep(
                title="Menu Navigation",
                content="Learn to navigate menus efficiently.",
                action="Try menu navigation",
                demo=get_demo("main_menu")
            ),
            TutorialStep(
                title="File Selection",
                content="Select files for processing.",
                action="Browse files",
                demo=get_demo("file_processing")
            ),
            TutorialStep(
                title="Query Building",
                content="Build powerful search queries.",
                action="Build a query",
                demo=get_demo("query_interface")
            ),
            TutorialStep(
                title="Results",
                content="You've learned the interactive features!"
            )
        ]
    )
    
    console.print("This tutorial includes real interactive demos!")
    
    if console.input("\n[bold]Play tutorial? (y/n):[/bold] ").lower() == 'y':
        player = TutorialPlayer(tutorial)
        player.play()


def main():
    """Run tutorial demos."""
    console = Console()
    
    demos = [
        ("Tutorial Creation", demo_tutorial_creation),
        ("Tutorial Manager", demo_tutorial_manager),
        ("Tutorial Player", demo_tutorial_player),
        ("Interactive Tutorial System", demo_interactive_tutorial),
        ("Onboarding Wizard", demo_onboarding),
        ("Progress Tracking", demo_tutorial_progress),
        ("Quick Start Guide", demo_quick_start),
        ("Tutorial with Actions", demo_custom_tutorial_with_actions),
    ]
    
    while True:
        console.clear()
        console.print("[bold cyan]Tutorial System Demo Suite[/bold cyan]\n")
        
        for i, (name, _) in enumerate(demos, 1):
            console.print(f"{i}. {name}")
        
        console.print("\nPress number to run demo, 'q' to quit")
        
        choice = console.input("\nSelect demo: ")
        
        if choice == 'q':
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            _, demo_func = demos[int(choice) - 1]
            demo_func()
        else:
            console.print("[red]Invalid choice![/red]")
            console.input("Press Enter to continue...")
    
    console.print("\n[dim]Goodbye![/dim]")


if __name__ == "__main__":
    main()