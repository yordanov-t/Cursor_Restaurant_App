"""
Theme Manager for Restaurant Management System.

Provides theme switching between Night, Neon, and Silhouette themes.
Works with cross-platform storage for persistence.
"""

import json
import os
from typing import Dict, Optional

# Import storage utilities for cross-platform path handling
try:
    from core.storage import get_settings_path
except ImportError:
    def get_settings_path(name="settings.json"):
        return name


# Theme names and display icons
THEMES = {
    "night": "🌙",    # Night (DEFAULT)
    "neon": "✨",      # Neon (existing)
    "silhouette": "☀️", # Silhouette (light)
    "misa": "🌸",      # Misa (glassmorphism soft palette)
}

DEFAULT_THEME = "night"


def _get_settings_file() -> str:
    """Get the settings file path (cross-platform)."""
    return get_settings_path("settings.json")


# ==========================================
# Theme Palettes
# ==========================================

class ThemePalette:
    """Base theme palette structure."""
    
    def __init__(
        self,
        # Backgrounds
        background: str,
        surface: str,
        surface_glass: str,
        surface_glass_hover: str,
        surface_elevated: str,
        
        # Gradients
        gradient_start: str,
        gradient_mid: str,
        gradient_end: str,
        
        # Text
        text_primary: str,
        text_secondary: str,
        text_disabled: str,
        button_text: str,  # Button text color (white for most themes)
        input_text: str,   # Input/dropdown text color
        icon_color: str,   # Icon color for top-right buttons
        
        # Accents
        accent_primary: str,
        accent_secondary: str,
        
        # Status colors
        success: str,
        success_glass: str,
        warning: str,
        warning_glass: str,
        danger: str,
        danger_glass: str,
        
        # Table states
        table_free: str,
        table_occupied: str,
        table_soon: str,
        table_free_selected: str,
        table_occupied_selected: str,
        table_soon_selected: str,
        
        # Borders & overlays
        border: str,
        border_focus: str,
        border_selected: str,
        overlay: str,
    ):
        self.background = background
        self.surface = surface
        self.surface_glass = surface_glass
        self.surface_glass_hover = surface_glass_hover
        self.surface_elevated = surface_elevated
        
        self.gradient_start = gradient_start
        self.gradient_mid = gradient_mid
        self.gradient_end = gradient_end
        
        self.text_primary = text_primary
        self.text_secondary = text_secondary
        self.text_disabled = text_disabled
        self.button_text = button_text
        self.input_text = input_text
        self.icon_color = icon_color
        
        self.accent_primary = accent_primary
        self.accent_secondary = accent_secondary
        
        self.success = success
        self.success_glass = success_glass
        self.warning = warning
        self.warning_glass = warning_glass
        self.danger = danger
        self.danger_glass = danger_glass
        
        self.table_free = table_free
        self.table_occupied = table_occupied
        self.table_soon = table_soon
        self.table_free_selected = table_free_selected
        self.table_occupied_selected = table_occupied_selected
        self.table_soon_selected = table_soon_selected
        
        self.border = border
        self.border_focus = border_focus
        self.border_selected = border_selected
        self.overlay = overlay


# Night Theme (DEFAULT) - Dark like ChatGPT with green accents
NIGHT_THEME = ThemePalette(
    # Backgrounds - similar to ChatGPT dark
    background="#212121",  # Dark gray background
    surface="#2F2F2F",     # Slightly lighter surface
    surface_glass="rgba(47, 47, 47, 0.85)",
    surface_glass_hover="rgba(57, 57, 57, 0.95)",
    surface_elevated="#3A3A3A",
    
    # Gradients - dark gray to darker
    gradient_start="#1A1A1A",
    gradient_mid="#212121",
    gradient_end="#2A2A2A",
    
    # Text
    text_primary="#ECECEC",  # Near-white (like ChatGPT)
    text_secondary="#B4B4B4",
    text_disabled="#6B7280",
    button_text="#FFFFFF",   # White text on buttons
    input_text="#ECECEC",    # Light text in inputs/dropdowns
    icon_color="#ECECEC",    # Light icons
    
    # Accents - GREEN borders and highlights
    accent_primary="#10B981",   # Green
    accent_secondary="#34D399", # Lighter green
    
    # Status colors
    success="#10B981",  # Green
    success_glass="rgba(16, 185, 129, 0.2)",
    warning="#F59E0B",  # Orange
    warning_glass="rgba(245, 158, 11, 0.2)",
    danger="#EF4444",   # Red
    danger_glass="rgba(239, 68, 68, 0.2)",
    
    # Table states
    table_free="#10B981",
    table_occupied="#EF4444",
    table_soon="#F59E0B",
    table_free_selected="#0D9668",
    table_occupied_selected="#B91C1C",
    table_soon_selected="#D97706",
    
    # Borders & overlays - GREEN
    border="rgba(16, 185, 129, 0.3)",  # Green border
    border_focus="rgba(16, 185, 129, 0.6)",
    border_selected="rgba(16, 185, 129, 0.8)",
    overlay="rgba(0, 0, 0, 0.7)",
)

# Neon Theme (EXISTING) - Purple/blue neon style
NEON_THEME = ThemePalette(
    # Backgrounds
    background="#0A0E1A",
    surface="#141B2D",
    surface_glass="rgba(20, 27, 45, 0.7)",
    surface_glass_hover="rgba(30, 37, 55, 0.85)",
    surface_elevated="#1F2937",
    
    # Gradients - blue to purple
    gradient_start="#1E3A8A",  # Deep blue
    gradient_mid="#6B21A8",     # Purple
    gradient_end="#4C1D95",     # Dark purple
    
    # Text
    text_primary="#FFFFFF",
    text_secondary="#B0B8CC",
    text_disabled="#6B7280",
    button_text="#FFFFFF",   # White text on buttons
    input_text="#FFFFFF",    # White text in inputs/dropdowns
    icon_color="#FFFFFF",    # White icons
    
    # Accents - Blue/Purple
    accent_primary="#3B82F6",   # Blue
    accent_secondary="#8B5CF6", # Purple
    
    # Status colors
    success="#10B981",
    success_glass="rgba(16, 185, 129, 0.2)",
    warning="#F59E0B",
    warning_glass="rgba(245, 158, 11, 0.2)",
    danger="#EF4444",
    danger_glass="rgba(239, 68, 68, 0.2)",
    
    # Table states
    table_free="#10B981",
    table_occupied="#EF4444",
    table_soon="#F59E0B",
    table_free_selected="#0D9668",
    table_occupied_selected="#B91C1C",
    table_soon_selected="#D97706",
    
    # Borders & overlays
    border="rgba(255, 255, 255, 0.1)",
    border_focus="rgba(59, 130, 246, 0.5)",
    border_selected="rgba(255, 255, 255, 0.4)",
    overlay="rgba(0, 0, 0, 0.5)",
)

# Silhouette Theme (LIGHT) - Light theme with proper contrast
SILHOUETTE_THEME = ThemePalette(
    # Backgrounds
    background="#F9FAFB",  # Very light gray
    surface="#FFFFFF",     # White
    surface_glass="rgba(255, 255, 255, 0.95)",
    surface_glass_hover="rgba(249, 250, 251, 1.0)",
    surface_elevated="#FFFFFF",
    
    # Gradients - subtle light tones
    gradient_start="#F3F4F6",
    gradient_mid="#F9FAFB",
    gradient_end="#F3F4F6",
    
    # Text - DARK for light theme
    text_primary="#111827",    # Very dark gray (almost black) for labels/body
    text_secondary="#6B7280",  # Medium gray
    text_disabled="#D1D5DB",   # Light gray
    button_text="#FFFFFF",     # WHITE text on buttons
    input_text="#111827",      # DARK text in inputs/dropdowns (readable on light)
    icon_color="#111827",      # DARK icons (readable on light)
    
    # Accents - Darker green for buttons (with white text)
    accent_primary="#047857",   # Dark green for buttons
    accent_secondary="#059669", # Medium green
    
    # Status colors - Darker for visibility
    success="#047857",  # Dark green
    success_glass="rgba(4, 120, 87, 0.1)",
    warning="#C2410C",  # Dark orange
    warning_glass="rgba(194, 65, 12, 0.1)",
    danger="#B91C1C",   # Dark red
    danger_glass="rgba(185, 28, 28, 0.1)",
    
    # Table states
    table_free="#059669",
    table_occupied="#DC2626",
    table_soon="#D97706",
    table_free_selected="#047857",
    table_occupied_selected="#991B1B",
    table_soon_selected="#B45309",
    
    # Borders & overlays
    border="rgba(4, 120, 87, 0.25)",  # Green border
    border_focus="rgba(4, 120, 87, 0.5)",
    border_selected="rgba(4, 120, 87, 0.7)",
    overlay="rgba(17, 24, 39, 0.5)",  # Dark overlay on light theme
)


# Misa Theme - Glassmorphism with modern soft color palette
# Inspired by frosted glass: soft lavender/rose/peach gradients, blurred surfaces
MISA_THEME = ThemePalette(
    # Backgrounds - deep muted navy-purple (makes glass pop)
    background="#1A1625",
    surface="#231B2E",
    surface_glass="rgba(255, 220, 230, 0.08)",
    surface_glass_hover="rgba(255, 220, 230, 0.14)",
    surface_elevated="#2C2040",

    # Gradients - soft deep rose to violet to indigo
    gradient_start="#2D1B4E",   # Deep violet
    gradient_mid="#1E1535",     # Dark purple-navy
    gradient_end="#1A1228",     # Very deep indigo

    # Text - soft warm white
    text_primary="#F5E6FF",     # Soft lavender-white
    text_secondary="#C4A8D8",   # Muted lavender
    text_disabled="#6B5880",    # Dim purple-gray
    button_text="#FFFFFF",      # White on buttons
    input_text="#F5E6FF",       # Soft lavender-white in inputs
    icon_color="#E8C8F0",       # Light lavender icons

    # Accents - rose pink and soft coral
    accent_primary="#D45B8A",   # Warm rose pink
    accent_secondary="#F09CB0", # Soft petal pink

    # Status colors - softened for the palette
    success="#5EC99B",          # Soft mint green
    success_glass="rgba(94, 201, 155, 0.18)",
    warning="#F0B86A",          # Warm amber
    warning_glass="rgba(240, 184, 106, 0.18)",
    danger="#E06080",           # Soft rose red
    danger_glass="rgba(224, 96, 128, 0.18)",

    # Table states
    table_free="#5EC99B",
    table_occupied="#E06080",
    table_soon="#F0B86A",
    table_free_selected="#3DAB7E",
    table_occupied_selected="#B84060",
    table_soon_selected="#C8924A",

    # Borders & overlays - glassy rose tint
    border="rgba(212, 91, 138, 0.25)",
    border_focus="rgba(212, 91, 138, 0.55)",
    border_selected="rgba(212, 91, 138, 0.80)",
    overlay="rgba(26, 18, 40, 0.72)",
)


# Map theme codes to palettes
THEME_PALETTES = {
    "night": NIGHT_THEME,
    "neon": NEON_THEME,
    "silhouette": SILHOUETTE_THEME,
    "misa": MISA_THEME,
}


# ==========================================
# Theme Manager (Singleton)
# ==========================================

class ThemeManager:
    """
    Singleton theme manager.
    
    Manages current theme selection and persistence.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current_theme = cls._instance._load_theme()
        return cls._instance
    
    def _load_theme(self) -> str:
        """Load saved theme from settings file."""
        try:
            settings_file = _get_settings_file()
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    theme = settings.get('theme', DEFAULT_THEME)
                    if theme in THEMES:
                        return theme
        except Exception:
            pass
        return DEFAULT_THEME
    
    def _save_theme(self):
        """Save current theme to settings file."""
        try:
            settings_file = _get_settings_file()
            settings = {}
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            settings['theme'] = self._current_theme
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    @property
    def current_theme(self) -> str:
        """Get current theme code."""
        return self._current_theme
    
    @current_theme.setter
    def current_theme(self, theme: str):
        """Set current theme and save to settings."""
        if theme in THEMES:
            self._current_theme = theme
            self._save_theme()
    
    def get_palette(self, theme: Optional[str] = None) -> ThemePalette:
        """Get palette for a theme (current theme if not specified)."""
        if theme is None:
            theme = self._current_theme
        return THEME_PALETTES.get(theme, NIGHT_THEME)
    
    def get_icon(self, theme: Optional[str] = None) -> str:
        """Get icon for a theme."""
        if theme is None:
            theme = self._current_theme
        return THEMES.get(theme, "🌙")
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get available themes with their icons."""
        return THEMES.copy()


# Global instance
_theme_manager = ThemeManager()


# ==========================================
# Public API
# ==========================================

def get_current_theme() -> str:
    """Get current theme code."""
    return _theme_manager.current_theme


def set_theme(theme: str):
    """Set current theme."""
    _theme_manager.current_theme = theme


def get_palette(theme: Optional[str] = None) -> ThemePalette:
    """Get palette for a theme (current theme if not specified)."""
    return _theme_manager.get_palette(theme)


def get_theme_icon(theme: Optional[str] = None) -> str:
    """Get icon for a theme."""
    return _theme_manager.get_icon(theme)


def get_available_themes() -> Dict[str, str]:
    """Get available themes with their icons."""
    return _theme_manager.get_available_themes()
