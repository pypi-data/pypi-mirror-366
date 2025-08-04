"""Final polish and enhancements for interactive CLI."""

from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

from .styles import get_icon
from .animations import LoadingAnimation, TransitionEffect


class UsageAnalytics:
    """Track usage patterns for improving UX."""
    
    def __init__(self, analytics_path: Optional[Path] = None):
        """Initialize usage analytics.
        
        Args:
            analytics_path: Path to store analytics data
        """
        self.analytics_path = analytics_path or (
            Path.home() / ".vector_db_query" / "usage_analytics.json"
        )
        self.session_data: Dict[str, Any] = {
            "session_id": datetime.now().isoformat(),
            "actions": [],
            "errors": [],
            "performance": {}
        }
        self.enabled = True
    
    def track_action(self, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Track user action.
        
        Args:
            action: Action name
            details: Additional details
        """
        if not self.enabled:
            return
        
        self.session_data["actions"].append({
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        })
    
    def track_error(self, error: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Track error occurrence.
        
        Args:
            error: Error message
            context: Error context
        """
        if not self.enabled:
            return
        
        self.session_data["errors"].append({
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        })
    
    def track_performance(self, operation: str, duration: float) -> None:
        """Track operation performance.
        
        Args:
            operation: Operation name
            duration: Duration in seconds
        """
        if not self.enabled:
            return
        
        if operation not in self.session_data["performance"]:
            self.session_data["performance"][operation] = []
        
        self.session_data["performance"][operation].append(duration)
    
    def save_session(self) -> None:
        """Save session analytics."""
        if not self.enabled:
            return
        
        try:
            # Load existing analytics
            analytics = []
            if self.analytics_path.exists():
                with open(self.analytics_path, 'r') as f:
                    analytics = json.load(f)
            
            # Add current session
            analytics.append(self.session_data)
            
            # Keep only last 100 sessions
            analytics = analytics[-100:]
            
            # Save
            self.analytics_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.analytics_path, 'w') as f:
                json.dump(analytics, f, indent=2)
        except:
            pass  # Silent fail for analytics
    
    def get_insights(self) -> Dict[str, Any]:
        """Get usage insights.
        
        Returns:
            Analytics insights
        """
        if not self.analytics_path.exists():
            return {}
        
        try:
            with open(self.analytics_path, 'r') as f:
                analytics = json.load(f)
            
            # Analyze patterns
            total_sessions = len(analytics)
            total_actions = sum(len(s.get("actions", [])) for s in analytics)
            total_errors = sum(len(s.get("errors", [])) for s in analytics)
            
            # Most common actions
            action_counts = {}
            for session in analytics:
                for action in session.get("actions", []):
                    name = action["action"]
                    action_counts[name] = action_counts.get(name, 0) + 1
            
            most_common = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "total_sessions": total_sessions,
                "total_actions": total_actions,
                "total_errors": total_errors,
                "error_rate": total_errors / total_actions if total_actions > 0 else 0,
                "most_common_actions": most_common
            }
        except:
            return {}


class SmartSuggestions:
    """Provide context-aware suggestions."""
    
    def __init__(self, analytics: Optional[UsageAnalytics] = None):
        """Initialize smart suggestions.
        
        Args:
            analytics: Usage analytics for personalization
        """
        self.analytics = analytics
        self.suggestions: Dict[str, List[str]] = {
            "first_time": [
                "Run the Getting Started tutorial",
                "Configure your API keys",
                "Process your first document",
                "Try a sample query"
            ],
            "after_processing": [
                "Query your indexed documents",
                "Browse processed files",
                "Check processing statistics",
                "Process more documents"
            ],
            "after_query": [
                "Refine your search query",
                "Export results",
                "Try advanced filters",
                "Save query as template"
            ],
            "errors": {
                "api_key": "Configure your API key in Settings",
                "connection": "Check if Qdrant is running",
                "file_not_found": "Verify file path exists",
                "permission": "Check file permissions"
            }
        }
    
    def get_suggestions(self, context: str) -> List[str]:
        """Get suggestions for current context.
        
        Args:
            context: Current context
            
        Returns:
            List of suggestions
        """
        base_suggestions = self.suggestions.get(context, [])
        
        # Add personalized suggestions based on usage
        if self.analytics:
            insights = self.analytics.get_insights()
            
            # If user hasn't used certain features
            if insights.get("total_sessions", 0) > 5:
                common_actions = [a[0] for a in insights.get("most_common_actions", [])]
                
                if "process_documents" not in common_actions:
                    base_suggestions.insert(0, "Try processing some documents")
                elif "query_database" not in common_actions:
                    base_suggestions.insert(0, "Search your indexed documents")
        
        return base_suggestions[:4]  # Limit to 4 suggestions
    
    def get_error_suggestion(self, error: str) -> Optional[str]:
        """Get suggestion for error.
        
        Args:
            error: Error message
            
        Returns:
            Suggestion or None
        """
        error_lower = error.lower()
        
        for key, suggestion in self.suggestions["errors"].items():
            if key in error_lower:
                return suggestion
        
        return None


class StatusBar:
    """Enhanced status bar with live updates."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize status bar.
        
        Args:
            console: Console instance
        """
        self.console = console or Console()
        self.items: Dict[str, str] = {}
        self.visible = True
    
    def update(self, **kwargs) -> None:
        """Update status items.
        
        Args:
            **kwargs: Status items to update
        """
        self.items.update(kwargs)
    
    def render(self) -> str:
        """Render status bar.
        
        Returns:
            Rendered status
        """
        if not self.visible or not self.items:
            return ""
        
        parts = []
        for key, value in self.items.items():
            if value:
                parts.append(f"[dim]{key}:[/dim] {value}")
        
        return " | ".join(parts)
    
    def show(self) -> None:
        """Show status bar."""
        self.visible = True
    
    def hide(self) -> None:
        """Hide status bar."""
        self.visible = False


class WelcomeScreen:
    """Enhanced welcome screen with tips."""
    
    def __init__(self, user_name: Optional[str] = None):
        """Initialize welcome screen.
        
        Args:
            user_name: User's name
        """
        self.user_name = user_name or "User"
        self.console = Console()
        self.tips = [
            "Press '?' anytime to see keyboard shortcuts",
            "Use Tab for autocompletion in queries",
            "Enable dark mode in preferences for night work",
            "Process documents in batches for efficiency",
            "Save frequently used queries as templates"
        ]
    
    def show(self, analytics: Optional[UsageAnalytics] = None) -> None:
        """Show welcome screen.
        
        Args:
            analytics: Usage analytics for insights
        """
        # Get time-based greeting
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        welcome_text = f"{greeting}, {self.user_name}!"
        
        # Get usage stats
        stats_text = ""
        if analytics:
            insights = analytics.get_insights()
            if insights.get("total_sessions", 0) > 0:
                stats_text = f"""
[dim]Your activity:[/dim]
• Sessions: {insights.get('total_sessions', 0)}
• Actions: {insights.get('total_actions', 0)}
• Most used: {insights.get('most_common_actions', [['N/A', 0]])[0][0]}"""
        
        # Random tip
        import random
        tip = random.choice(self.tips)
        
        # Create layout
        layout = Layout()
        
        # Welcome panel
        welcome_panel = Panel(
            Align.center(f"[bold cyan]{welcome_text}[/bold cyan]\n\n{stats_text}"),
            title="[bold]Vector DB Query[/bold]",
            border_style="cyan"
        )
        
        # Tip panel
        tip_panel = Panel(
            f"{get_icon('tip')} [yellow]Tip:[/yellow] {tip}",
            border_style="yellow"
        )
        
        layout.split_column(
            Layout(welcome_panel, size=10),
            Layout(tip_panel, size=3)
        )
        
        self.console.print(layout)


class ExitConfirmation:
    """Enhanced exit confirmation with session summary."""
    
    def __init__(self, analytics: Optional[UsageAnalytics] = None):
        """Initialize exit confirmation.
        
        Args:
            analytics: Usage analytics
        """
        self.analytics = analytics
        self.console = Console()
    
    def confirm(self) -> bool:
        """Show exit confirmation.
        
        Returns:
            True to exit
        """
        # Show session summary
        if self.analytics and self.analytics.session_data["actions"]:
            self.console.print("\n[bold]Session Summary[/bold]")
            
            # Actions performed
            action_counts = {}
            for action in self.analytics.session_data["actions"]:
                name = action["action"]
                action_counts[name] = action_counts.get(name, 0) + 1
            
            table = Table(show_header=False, box=None)
            table.add_column("Action", style="cyan")
            table.add_column("Count", style="yellow")
            
            for action, count in sorted(action_counts.items()):
                table.add_row(action.replace("_", " ").title(), str(count))
            
            self.console.print(table)
            
            # Session duration
            start_time = datetime.fromisoformat(self.analytics.session_data["session_id"])
            duration = datetime.now() - start_time
            minutes = int(duration.total_seconds() / 60)
            
            self.console.print(f"\n[dim]Session duration: {minutes} minutes[/dim]")
        
        # Confirm exit
        import questionary
        return questionary.confirm(
            "\nExit Vector DB Query?",
            default=False
        ).ask()


class UpdateChecker:
    """Check for updates (mock implementation)."""
    
    @staticmethod
    def check_updates() -> Optional[str]:
        """Check for available updates.
        
        Returns:
            Update message or None
        """
        # In a real implementation, this would check GitHub releases
        # or a version endpoint
        return None  # No updates for demo


class FeatureHighlight:
    """Highlight new or underused features."""
    
    def __init__(self, analytics: Optional[UsageAnalytics] = None):
        """Initialize feature highlight.
        
        Args:
            analytics: Usage analytics
        """
        self.analytics = analytics
        self.features = {
            "mcp_integration": {
                "name": "MCP Integration",
                "description": "Connect AI assistants to your knowledge base",
                "min_sessions": 5
            },
            "batch_processing": {
                "name": "Batch Processing",
                "description": "Process entire directories efficiently",
                "min_sessions": 3
            },
            "query_templates": {
                "name": "Query Templates",
                "description": "Save and reuse common search patterns",
                "min_sessions": 7
            },
            "export_results": {
                "name": "Export Results",
                "description": "Export search results in multiple formats",
                "min_sessions": 10
            }
        }
        self.console = Console()
    
    def get_highlight(self) -> Optional[Dict[str, str]]:
        """Get feature to highlight.
        
        Returns:
            Feature info or None
        """
        if not self.analytics:
            return None
        
        insights = self.analytics.get_insights()
        sessions = insights.get("total_sessions", 0)
        
        if sessions == 0:
            return None
        
        # Find features not used yet
        used_actions = [a[0] for a in insights.get("most_common_actions", [])]
        
        for feature_id, feature in self.features.items():
            if sessions >= feature["min_sessions"] and feature_id not in used_actions:
                return feature
        
        return None
    
    def show_highlight(self) -> None:
        """Show feature highlight."""
        feature = self.get_highlight()
        if not feature:
            return
        
        panel = Panel(
            f"[bold]{feature['name']}[/bold]\n\n{feature['description']}\n\n"
            f"[dim]Try it from the main menu![/dim]",
            title="[bold yellow]Feature Spotlight[/bold yellow]",
            border_style="yellow"
        )
        
        self.console.print(panel)
        self.console.input("\nPress Enter to continue...")


# Polished error messages
ERROR_MESSAGES = {
    "file_not_found": {
        "message": "The specified file could not be found.",
        "suggestions": [
            "Check the file path for typos",
            "Ensure the file exists",
            "Try using absolute paths"
        ]
    },
    "api_key_missing": {
        "message": "API key is not configured.",
        "suggestions": [
            "Add your API key to the configuration",
            "Check environment variables",
            "Run 'vector-db-query config' to set up"
        ]
    },
    "connection_failed": {
        "message": "Could not connect to the vector database.",
        "suggestions": [
            "Ensure Qdrant is running",
            "Check the connection settings",
            "Verify network connectivity"
        ]
    },
    "permission_denied": {
        "message": "Permission denied accessing the resource.",
        "suggestions": [
            "Check file permissions",
            "Run with appropriate privileges",
            "Verify ownership of files"
        ]
    }
}


def get_polished_error(error_type: str, details: Optional[str] = None) -> Panel:
    """Get polished error panel.
    
    Args:
        error_type: Error type
        details: Additional details
        
    Returns:
        Error panel
    """
    error_info = ERROR_MESSAGES.get(error_type, {
        "message": "An unexpected error occurred.",
        "suggestions": ["Check the logs for details"]
    })
    
    content = f"[bold red]{error_info['message']}[/bold red]"
    
    if details:
        content += f"\n\n[dim]Details: {details}[/dim]"
    
    if error_info.get("suggestions"):
        content += "\n\n[yellow]Suggestions:[/yellow]"
        for suggestion in error_info["suggestions"]:
            content += f"\n• {suggestion}"
    
    return Panel(
        content,
        title="[bold red]Error[/bold red]",
        border_style="red"
    )