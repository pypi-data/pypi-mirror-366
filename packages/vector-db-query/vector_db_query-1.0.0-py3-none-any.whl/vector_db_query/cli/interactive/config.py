"""Configuration for interactive CLI components."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

from ...utils.config import Config


@dataclass
class InteractiveConfig:
    """Configuration for interactive CLI features."""
    
    # Display settings
    theme: str = "default"
    page_size: int = 10
    show_help: bool = True
    show_breadcrumb: bool = True
    use_emoji: bool = True
    auto_clear: bool = False
    
    # Behavior settings
    confirm_destructive: bool = True
    save_history: bool = True
    history_size: int = 100
    auto_complete: bool = True
    
    # File browser settings
    file_preview_lines: int = 20
    show_hidden_files: bool = False
    file_extensions: List[str] = field(default_factory=lambda: [
        ".txt", ".md", ".pdf", ".docx", ".doc",
        ".py", ".js", ".json", ".yaml", ".yml",
        ".csv", ".log", ".xml", ".html"
    ])
    
    # Query settings
    query_history_file: str = "~/.vector_db_query_history"
    max_suggestions: int = 10
    query_templates: Dict[str, str] = field(default_factory=lambda: {
        "simple": "Find documents about {topic}",
        "specific": "Show {type} documents containing {terms}",
        "recent": "Find documents from the last {period} about {topic}",
        "similar": "Find documents similar to {reference}"
    })
    
    # Progress settings
    show_progress_bar: bool = True
    show_time_estimate: bool = True
    update_interval: float = 0.1
    
    # Result display settings
    max_preview_length: int = 500
    highlight_matches: bool = True
    result_formats: List[str] = field(default_factory=lambda: [
        "table", "cards", "json", "csv"
    ])
    
    @classmethod
    def from_config(cls, config: Config) -> 'InteractiveConfig':
        """Create interactive config from main config.
        
        Args:
            config: Main application config
            
        Returns:
            Interactive configuration
        """
        # Extract interactive settings from main config
        ui_config = config.settings.get("ui", {})
        
        return cls(
            theme=ui_config.get("theme", "default"),
            page_size=ui_config.get("page_size", 10),
            show_help=ui_config.get("show_help", True),
            use_emoji=ui_config.get("use_emoji", True),
            auto_clear=ui_config.get("auto_clear", False),
            confirm_destructive=ui_config.get("confirm_destructive", True),
            save_history=ui_config.get("save_history", True),
            file_preview_lines=ui_config.get("file_preview_lines", 20),
            show_hidden_files=ui_config.get("show_hidden_files", False),
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "theme": self.theme,
            "page_size": self.page_size,
            "show_help": self.show_help,
            "show_breadcrumb": self.show_breadcrumb,
            "use_emoji": self.use_emoji,
            "auto_clear": self.auto_clear,
            "confirm_destructive": self.confirm_destructive,
            "save_history": self.save_history,
            "history_size": self.history_size,
            "auto_complete": self.auto_complete,
            "file_preview_lines": self.file_preview_lines,
            "show_hidden_files": self.show_hidden_files,
            "file_extensions": self.file_extensions,
            "query_history_file": self.query_history_file,
            "max_suggestions": self.max_suggestions,
            "show_progress_bar": self.show_progress_bar,
            "show_time_estimate": self.show_time_estimate,
            "update_interval": self.update_interval,
            "max_preview_length": self.max_preview_length,
            "highlight_matches": self.highlight_matches,
            "result_formats": self.result_formats,
        }


class ThemeManager:
    """Manage UI themes and preferences."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize theme manager.
        
        Args:
            config_path: Path to theme config file
        """
        self.config_path = config_path or Path.home() / ".vector_db_theme"
        self.current_theme = "default"
        self._load_preferences()
    
    def _load_preferences(self) -> None:
        """Load theme preferences from file."""
        if self.config_path.exists():
            try:
                import json
                with open(self.config_path) as f:
                    prefs = json.load(f)
                    self.current_theme = prefs.get("theme", "default")
            except Exception:
                # Ignore errors, use defaults
                pass
    
    def save_preferences(self) -> None:
        """Save theme preferences to file."""
        try:
            import json
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception:
            # Ignore save errors
            pass
    
    def set_theme(self, theme: str) -> None:
        """Set current theme.
        
        Args:
            theme: Theme name
        """
        if theme in ["default", "dark", "light"]:
            self.current_theme = theme
            self.save_preferences()
    
    def get_theme(self) -> str:
        """Get current theme."""
        return self.current_theme
    
    def cycle_theme(self) -> str:
        """Cycle to next theme.
        
        Returns:
            New theme name
        """
        themes = ["default", "dark", "light"]
        current_idx = themes.index(self.current_theme)
        next_idx = (current_idx + 1) % len(themes)
        self.set_theme(themes[next_idx])
        return self.current_theme