"""Custom styles and themes for interactive CLI."""

from typing import Dict

from questionary import Style
from rich.theme import Theme


# Questionary styles for prompts
THEME_STYLES = {
    "default": Style([
        ('question', 'fg:#5F87FF bold'),
        ('answer', 'fg:#00D7FF'),
        ('pointer', 'fg:#FF5F5F bold'),
        ('highlighted', 'fg:#5FFF5F'),
        ('selected', 'fg:#5FFF5F'),
        ('separator', 'fg:#6C6C6C'),
        ('instruction', 'fg:#AEAEAE'),
        ('text', 'fg:#FFFFFF'),
        ('disabled', 'fg:#858585 italic'),
    ]),
    "dark": Style([
        ('question', 'fg:#7B68EE bold'),
        ('answer', 'fg:#00CED1'),
        ('pointer', 'fg:#FF6347 bold'),
        ('highlighted', 'fg:#32CD32'),
        ('selected', 'fg:#32CD32'),
        ('separator', 'fg:#696969'),
        ('instruction', 'fg:#A9A9A9'),
        ('text', 'fg:#F5F5F5'),
        ('disabled', 'fg:#808080 italic'),
    ]),
    "light": Style([
        ('question', 'fg:#4169E1 bold'),
        ('answer', 'fg:#008B8B'),
        ('pointer', 'fg:#DC143C bold'),
        ('highlighted', 'fg:#228B22'),
        ('selected', 'fg:#228B22'),
        ('separator', 'fg:#A9A9A9'),
        ('instruction', 'fg:#696969'),
        ('text', 'fg:#000000'),
        ('disabled', 'fg:#C0C0C0 italic'),
    ]),
}


# Rich themes for console output
RICH_THEMES = {
    "default": Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "red",
        "success": "green",
        "prompt": "bold cyan",
        "menu.title": "bold magenta",
        "menu.border": "bright_blue",
        "progress.description": "white",
        "progress.percentage": "bright_green",
        "table.header": "bold magenta",
        "table.row": "white",
        "table.row.odd": "bright_black",
    }),
    "dark": Theme({
        "info": "dark_cyan",
        "warning": "dark_goldenrod",
        "error": "dark_red",
        "success": "dark_green",
        "prompt": "bold medium_purple",
        "menu.title": "bold medium_purple",
        "menu.border": "steel_blue",
        "progress.description": "grey93",
        "progress.percentage": "green3",
        "table.header": "bold medium_purple",
        "table.row": "grey93",
        "table.row.odd": "grey23",
    }),
    "light": Theme({
        "info": "blue",
        "warning": "dark_orange",
        "error": "red3",
        "success": "green4",
        "prompt": "bold blue",
        "menu.title": "bold blue",
        "menu.border": "steel_blue3",
        "progress.description": "black",
        "progress.percentage": "green4",
        "table.header": "bold blue",
        "table.row": "black",
        "table.row.odd": "grey74",
    }),
}


def get_custom_style(theme: str = "default") -> Style:
    """Get custom style for questionary prompts.
    
    Args:
        theme: Theme name (default, dark, light)
        
    Returns:
        Questionary Style object
    """
    return THEME_STYLES.get(theme, THEME_STYLES["default"])


def get_rich_theme(theme: str = "default") -> Theme:
    """Get Rich theme for console output.
    
    Args:
        theme: Theme name (default, dark, light)
        
    Returns:
        Rich Theme object
    """
    return RICH_THEMES.get(theme, RICH_THEMES["default"])


# ASCII art for headers
VECTOR_DB_HEADER = """
╦  ╦┌─┐┌─┐┌┬┐┌─┐┬─┐  ╔╦╗╔╗   ╔═╗ ┬ ┬┌─┐┬─┐┬ ┬
╚╗╔╝├┤ │   │ │ │├┬┘   ║║╠╩╗  ║═╬╗│ │├┤ ├┬┘└┬┘
 ╚╝ └─┘└─┘ ┴ └─┘┴└─  ═╩╝╚═╝  ╚═╝╚└─┘└─┘┴└─ ┴ 
"""

WELCOME_MESSAGE = """
Welcome to Vector DB Query System!

Query your documents using AI-powered semantic search.
All data is stored locally for privacy and security.
"""


# Menu icons
MENU_ICONS = {
    "process": "📄",
    "query": "🔍",
    "mcp": "🤖",
    "config": "⚙️",
    "status": "📊",
    "help": "❓",
    "exit": "🚪",
    "back": "⬅️",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "folder": "📁",
    "file": "📄",
    "database": "🗄️",
    "rocket": "🚀",
}


def get_icon(name: str, fallback: str = "•") -> str:
    """Get icon for menu item.
    
    Args:
        name: Icon name
        fallback: Fallback character if icon not found
        
    Returns:
        Icon character or fallback
    """
    return MENU_ICONS.get(name, fallback)


# Color schemes for different message types
MESSAGE_COLORS = {
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "prompt": "bright_blue",
    "highlight": "magenta",
}


def get_color(message_type: str) -> str:
    """Get color for message type.
    
    Args:
        message_type: Type of message
        
    Returns:
        Color name for Rich
    """
    return MESSAGE_COLORS.get(message_type, "white")