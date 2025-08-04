"""Interactive CLI components for enhanced user experience.

This module provides rich interactive components including:
- Enhanced menu system with keyboard navigation
- File browser with preview capabilities
- Interactive query builder with suggestions
- Progress tracking for long operations
- Visual configuration editor
- Rich result visualization
"""

from .menu import InteractiveMenu, MenuBuilder, MenuItem
from .styles import get_custom_style, get_rich_theme, THEME_STYLES, get_icon
from .base import (
    BaseUIComponent,
    UIConfig,
    ProgressTracker,
    LoadingSpinner,
    ErrorDisplay
)
from .config import InteractiveConfig, ThemeManager
from .animations import MenuAnimations, TransitionEffect, LoadingAnimation, MenuDecorations
from .keyboard import KeyboardHandler, Key, KeyBinding
from .navigation import NavigationManager, NavigationItem, Breadcrumb, NavigationHistory
from .shortcuts import ShortcutContext, ShortcutManager, Shortcut, shortcut_manager, show_shortcuts
from .hotkeys import HotkeyHandler, HotkeyMixin, get_hotkey_handler
from .file_browser import FileBrowser, FilePreview, FileSearch, FileInfo
from .query_builder import (
    QueryBuilder, QueryWizard, QueryTemplate,
    QueryHistory, QueryHistoryItem, QuerySuggester
)
from .progress import (
    ProgressManager, MultiProgressDisplay, ProgressGroup,
    ProgressTask, TaskStatus, create_file_progress
)
from .config_ui import (
    ConfigEditor, ConfigWizard, ConfigSection, ConfigField,
    ConfigType
)
from .results import ResultViewer, SearchResult, ResultFormatter
from .app import InteractiveApp, create_app
from .preferences import (
    PreferencesManager, PreferenceItem, PreferenceType,
    UserPreferences, get_preferences, get_preference, set_preference
)
from .preferences_ui import (
    PreferencesEditor, PreferencesQuickMenu, apply_preferences
)
from .tutorials import (
    Tutorial, TutorialStep, TutorialLevel,
    TutorialManager, TutorialPlayer, InteractiveTutorial
)
from .onboarding import (
    OnboardingWizard, should_run_onboarding, run_onboarding,
    show_quick_start
)
from .optimization import (
    PerformanceMonitor, perf_monitor, CacheManager, cache_manager,
    LazyLoader, lazy_loader, MemoryOptimizer, BatchProcessor,
    RenderOptimizer, render_optimizer, optimize_startup
)
from .polish import (
    UsageAnalytics, SmartSuggestions, StatusBar, WelcomeScreen,
    ExitConfirmation, FeatureHighlight, get_polished_error
)

__all__ = [
    # Menu components
    "InteractiveMenu",
    "MenuBuilder",
    "MenuItem",
    
    # Base components
    "BaseUIComponent",
    "UIConfig",
    "ProgressTracker",
    "LoadingSpinner",
    "ErrorDisplay",
    
    # Styling
    "get_custom_style",
    "get_rich_theme",
    "get_icon",
    "THEME_STYLES",
    
    # Configuration
    "InteractiveConfig",
    "ThemeManager",
    
    # Animations
    "MenuAnimations",
    "TransitionEffect",
    "LoadingAnimation",
    "MenuDecorations",
    
    # Keyboard handling
    "KeyboardHandler",
    "Key",
    "KeyBinding",
    
    # Navigation
    "NavigationManager",
    "NavigationItem",
    "Breadcrumb",
    "NavigationHistory",
    
    # Shortcuts
    "ShortcutContext",
    "ShortcutManager",
    "Shortcut",
    "shortcut_manager",
    "show_shortcuts",
    
    # Hotkeys
    "HotkeyHandler",
    "HotkeyMixin",
    "get_hotkey_handler",
    
    # File browser
    "FileBrowser",
    "FilePreview",
    "FileSearch",
    "FileInfo",
    
    # Query builder
    "QueryBuilder",
    "QueryWizard",
    "QueryTemplate",
    "QueryHistory",
    "QueryHistoryItem",
    "QuerySuggester",
    
    # Progress management
    "ProgressManager",
    "MultiProgressDisplay",
    "ProgressGroup",
    "ProgressTask",
    "TaskStatus",
    "create_file_progress",
    
    # Configuration UI
    "ConfigEditor",
    "ConfigWizard",
    "ConfigSection",
    "ConfigField",
    "ConfigType",
    
    # Result viewer
    "ResultViewer",
    "SearchResult",
    "ResultFormatter",
    
    # Main app
    "InteractiveApp",
    "create_app",
    
    # Preferences
    "PreferencesManager",
    "PreferenceItem",
    "PreferenceType",
    "UserPreferences",
    "get_preferences",
    "get_preference",
    "set_preference",
    "PreferencesEditor",
    "PreferencesQuickMenu",
    "apply_preferences",
    
    # Tutorials
    "Tutorial",
    "TutorialStep",
    "TutorialLevel",
    "TutorialManager",
    "TutorialPlayer",
    "InteractiveTutorial",
    
    # Onboarding
    "OnboardingWizard",
    "should_run_onboarding",
    "run_onboarding",
    "show_quick_start",
    
    # Optimization
    "PerformanceMonitor",
    "perf_monitor",
    "CacheManager",
    "cache_manager",
    "LazyLoader",
    "lazy_loader",
    "MemoryOptimizer",
    "BatchProcessor",
    "RenderOptimizer",
    "render_optimizer",
    "optimize_startup",
    
    # Polish
    "UsageAnalytics",
    "SmartSuggestions",
    "StatusBar",
    "WelcomeScreen",
    "ExitConfirmation",
    "FeatureHighlight",
    "get_polished_error",
]

__version__ = "1.0.0"