"""
Flet compatibility layer.

Provides version-agnostic color, icon, and enum definitions and API wrappers
to ensure compatibility across all Flet versions.
"""

import flet as ft

# Detect Flet version for debugging
try:
    FLET_VERSION = ft.__version__ if hasattr(ft, '__version__') else "unknown"
except:
    FLET_VERSION = "unknown"


# ============================================================================
# COLORS - Material Design hex codes (cross-version compatible)
# ============================================================================

class Colors:
    """Color constants compatible with all Flet versions."""
    
    # Primary colors
    GREEN = "#4CAF50"
    GREEN_400 = "#66BB6A"
    RED = "#F44336"
    RED_400 = "#EF5350"
    ORANGE_400 = "#FFA726"
    ORANGE_700 = "#F57C00"
    WHITE = "#FFFFFF"
    TRANSPARENT = "#00000000"  # Fully transparent (RGBA)
    
    # Theme colors
    SURFACE_VARIANT = "#2C2C2C"  # Dark theme surface variant
    
    # Status colors
    SUCCESS = GREEN
    ERROR = RED
    WARNING = ORANGE_400


# ============================================================================
# ICONS - Detect correct icon namespace (ft.icons vs ft.Icons)
# ============================================================================

# Try to detect the correct icons namespace
if hasattr(ft, 'icons'):
    # Lowercase 'icons' namespace (older Flet versions)
    icons = ft.icons
    ICONS_API = "ft.icons"
elif hasattr(ft, 'Icons'):
    # Uppercase 'Icons' namespace (newer Flet versions)
    icons = ft.Icons
    ICONS_API = "ft.Icons"
else:
    # Fallback: create a minimal icons object with common icons as strings
    class _IconsFallback:
        # Navigation
        BOOK = "book"
        BOOK_OUTLINED = "book_outlined"
        GRID_VIEW = "grid_view"
        GRID_VIEW_OUTLINED = "grid_view_outlined"
        ADMIN_PANEL_SETTINGS = "admin_panel_settings"
        ADMIN_PANEL_SETTINGS_OUTLINED = "admin_panel_settings_outlined"
        
        # Actions
        ADD = "add"
        EDIT = "edit"
        DELETE = "delete"
        LOGOUT = "logout"
        BACKUP = "backup"
        RESTORE = "restore"
    
    icons = _IconsFallback()
    ICONS_API = "fallback (string names)"


# ============================================================================
# ENUMS - Detect correct enum namespaces
# ============================================================================

# FontWeight - with safe member access
if hasattr(ft, 'FontWeight'):
    _FontWeightBase = ft.FontWeight
    
    # Create a wrapper that provides consistent weight names
    class FontWeight:
        """FontWeight with cross-version compatibility."""
        # Standard weights that exist in most Flet versions
        NORMAL = getattr(_FontWeightBase, 'NORMAL', 'normal')
        BOLD = getattr(_FontWeightBase, 'BOLD', 'bold')
        
        # Numeric weights (CSS standard)
        W_100 = getattr(_FontWeightBase, 'W_100', '100')
        W_200 = getattr(_FontWeightBase, 'W_200', '200')
        W_300 = getattr(_FontWeightBase, 'W_300', '300')
        W_400 = getattr(_FontWeightBase, 'W_400', '400')
        W_500 = getattr(_FontWeightBase, 'W_500', '500')
        W_600 = getattr(_FontWeightBase, 'W_600', '600')
        W_700 = getattr(_FontWeightBase, 'W_700', '700')
        W_800 = getattr(_FontWeightBase, 'W_800', '800')
        W_900 = getattr(_FontWeightBase, 'W_900', '900')
        
        # Semantic aliases (map to numeric weights)
        LIGHT = W_300
        REGULAR = W_400
        MEDIUM = W_500  # ← MEDIUM maps to W_500
        SEMIBOLD = W_600
        # BOLD already defined above
        
elif hasattr(ft, 'fontweight'):
    FontWeight = ft.fontweight
else:
    # Fallback to string-based weights
    class FontWeight:
        NORMAL = "normal"
        BOLD = "bold"
        W_100 = "100"
        W_200 = "200"
        W_300 = "300"
        W_400 = "400"
        W_500 = "500"
        W_600 = "600"
        W_700 = "700"
        W_800 = "800"
        W_900 = "900"
        LIGHT = "300"
        REGULAR = "400"
        MEDIUM = "500"
        SEMIBOLD = "600"

# Alignment
if hasattr(ft, 'alignment'):
    alignment = ft.alignment
elif hasattr(ft, 'Alignment'):
    alignment = ft.Alignment
else:
    class _AlignmentFallback:
        center = "center"
    alignment = _AlignmentFallback()

# TextAlign
if hasattr(ft, 'TextAlign'):
    TextAlign = ft.TextAlign
elif hasattr(ft, 'textalign'):
    TextAlign = ft.textalign
else:
    class _TextAlignFallback:
        CENTER = "center"
        LEFT = "left"
        RIGHT = "right"
    TextAlign = _TextAlignFallback()

# MainAxisAlignment
if hasattr(ft, 'MainAxisAlignment'):
    MainAxisAlignment = ft.MainAxisAlignment
elif hasattr(ft, 'mainaxisalignment'):
    MainAxisAlignment = ft.mainaxisalignment
else:
    class _MainAxisAlignmentFallback:
        CENTER = "center"
        START = "start"
        END = "end"
        SPACE_BETWEEN = "spaceBetween"
    MainAxisAlignment = _MainAxisAlignmentFallback()

# CrossAxisAlignment
if hasattr(ft, 'CrossAxisAlignment'):
    CrossAxisAlignment = ft.CrossAxisAlignment
elif hasattr(ft, 'crossaxisalignment'):
    CrossAxisAlignment = ft.crossaxisalignment
else:
    class _CrossAxisAlignmentFallback:
        CENTER = "center"
        START = "start"
        END = "end"
    CrossAxisAlignment = _CrossAxisAlignmentFallback()

# ScrollMode
if hasattr(ft, 'ScrollMode'):
    ScrollMode = ft.ScrollMode
elif hasattr(ft, 'scrollmode'):
    ScrollMode = ft.scrollmode
else:
    class _ScrollModeFallback:
        AUTO = "auto"
        ALWAYS = "always"
        HIDDEN = "hidden"
    ScrollMode = _ScrollModeFallback()

# ThemeMode
if hasattr(ft, 'ThemeMode'):
    ThemeMode = ft.ThemeMode
elif hasattr(ft, 'thememode'):
    ThemeMode = ft.thememode
else:
    class _ThemeModeFallback:
        DARK = "dark"
        LIGHT = "light"
        SYSTEM = "system"
    ThemeMode = _ThemeModeFallback()


# ============================================================================
# ANIMATION - Cross-version animation helpers
# ============================================================================

def get_animation(duration_ms: int = 300, curve: str = "easeOut"):
    """
    Get animation configuration compatible with installed Flet version.
    
    Args:
        duration_ms: Animation duration in milliseconds
        curve: Animation curve (easeOut, easeIn, linear, etc.)
    
    Returns:
        Animation configuration compatible with this Flet version
    """
    # Check if Animation class exists at top level
    if hasattr(ft, 'Animation'):
        # Try to use Animation class
        try:
            if hasattr(ft, 'AnimationCurve'):
                # Full animation support with curve
                curve_enum = getattr(ft.AnimationCurve, curve.upper(), None)
                if curve_enum:
                    return ft.Animation(duration_ms, curve_enum)
            # Animation class exists but no curve enum
            return ft.Animation(duration_ms)
        except:
            pass
    
    # Fallback: simple duration (many Flet versions accept int for animate)
    return duration_ms


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_flet_version() -> str:
    """Get Flet version string for debugging."""
    return FLET_VERSION


def log_compatibility_info():
    """Log Flet version and API detection info at startup."""
    print(f"[Flet Compat] Flet version: {FLET_VERSION}")
    print(f"[Flet Compat] Icons API: {ICONS_API}")
    print(f"[Flet Compat] Animation: {'Full support' if hasattr(ft, 'Animation') else 'Basic support'}")
    print(f"[Flet Compat] FontWeight: {len([a for a in dir(FontWeight) if not a.startswith('_')])} members available")
    print(f"[Flet Compat] Using compatibility layer for cross-version support")

