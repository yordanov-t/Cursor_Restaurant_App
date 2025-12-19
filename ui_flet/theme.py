"""
Glassmorphism / Liquid Glass Design System for Flet UI.

Modern 2026 design with consistent spacing, colors, and glass effects.
"""

import flet as ft


# ============================================================================
# COLOR PALETTE - Glassmorphism / Dark Theme
# ============================================================================

class Colors:
    """Color tokens for glassmorphism design."""
    
    # Base colors
    BACKGROUND = "#0A0E1A"  # Deep dark blue-black (fallback)
    SURFACE = "#141B2D"  # Slightly lighter surface
    SURFACE_GLASS = "rgba(20, 27, 45, 0.7)"  # Translucent glass
    SURFACE_GLASS_HOVER = "rgba(30, 37, 55, 0.85)"  # Glass on hover
    
    # Gradient colors (for background)
    GRADIENT_START = "#1E3A8A"  # Deep blue
    GRADIENT_MID = "#6B21A8"     # Purple
    GRADIENT_END = "#4C1D95"     # Dark purple
    
    # Text colors
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#B0B8CC"
    TEXT_DISABLED = "#6B7280"
    
    # Accent colors
    ACCENT_PRIMARY = "#3B82F6"  # Blue
    ACCENT_SECONDARY = "#8B5CF6"  # Purple
    
    # Status colors
    SUCCESS = "#10B981"  # Green
    SUCCESS_GLASS = "rgba(16, 185, 129, 0.2)"
    WARNING = "#F59E0B"  # Orange/Amber
    WARNING_GLASS = "rgba(245, 158, 11, 0.2)"
    DANGER = "#EF4444"  # Red
    DANGER_GLASS = "rgba(239, 68, 68, 0.2)"
    
    # Table states (from existing compat)
    TABLE_FREE = "#10B981"  # Green
    TABLE_OCCUPIED = "#EF4444"  # Red
    TABLE_SOON = "#F59E0B"  # Orange
    
    # Borders & overlays
    BORDER = "rgba(255, 255, 255, 0.1)"
    BORDER_FOCUS = "rgba(59, 130, 246, 0.5)"
    OVERLAY = "rgba(0, 0, 0, 0.5)"


# ============================================================================
# SPACING SCALE (4px base)
# ============================================================================

class Spacing:
    """Consistent spacing scale."""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    XXXL = 48


# ============================================================================
# BORDER RADIUS SCALE
# ============================================================================

class Radius:
    """Border radius scale for glass containers."""
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    FULL = 9999


# ============================================================================
# TYPOGRAPHY SCALE
# ============================================================================

class Typography:
    """Text size and weight scale."""
    
    # Sizes
    SIZE_XS = 12
    SIZE_SM = 14
    SIZE_MD = 16
    SIZE_LG = 18
    SIZE_XL = 20
    SIZE_XXL = 24
    SIZE_XXXL = 32
    
    # Weights (using strings for compatibility)
    WEIGHT_NORMAL = "normal"
    WEIGHT_MEDIUM = "500"
    WEIGHT_SEMIBOLD = "600"
    WEIGHT_BOLD = "bold"


# ============================================================================
# GLASS CONTAINER STYLES
# ============================================================================

def glass_container(
    content,
    padding: int = Spacing.LG,
    border_radius: int = Radius.MD,
    blur: int = 10,
    **kwargs
):
    """
    Create a glassmorphism container.
    
    Args:
        content: Flet control to wrap
        padding: Padding value
        border_radius: Border radius
        blur: Backdrop blur amount
        **kwargs: Additional Container properties
    """
    return ft.Container(
        content=content,
        bgcolor=Colors.SURFACE_GLASS,
        border=ft.border.all(1, Colors.BORDER),
        border_radius=border_radius,
        padding=padding,
        blur=blur,
        **kwargs
    )


def glass_button(
    text: str,
    icon=None,
    on_click=None,
    variant: str = "primary",  # primary, secondary, danger, success
    width: int = None,
    **kwargs
):
    """
    Create a glassmorphism button.
    
    Args:
        text: Button text
        icon: Optional icon
        on_click: Click handler
        variant: Button style variant
        width: Optional fixed width
        **kwargs: Additional button properties
    """
    colors = {
        "primary": Colors.ACCENT_PRIMARY,
        "secondary": Colors.SURFACE_GLASS_HOVER,
        "danger": Colors.DANGER,
        "success": Colors.SUCCESS,
        "warning": Colors.WARNING,
    }
    
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        width=width,
        bgcolor=colors.get(variant, Colors.ACCENT_PRIMARY),
        color=Colors.TEXT_PRIMARY,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=Radius.SM),
            padding=ft.padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
        ),
        **kwargs
    )


def glass_card(
    content,
    padding: int = Spacing.XL,
    **kwargs
):
    """
    Create a glass card (larger padding, more prominent).
    
    Args:
        content: Card content
        padding: Card padding
        **kwargs: Additional container properties
    """
    return glass_container(
        content=content,
        padding=padding,
        border_radius=Radius.LG,
        blur=15,
        **kwargs
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
#
# IMPORTANT: To prevent "got multiple values for keyword argument" errors,
# these helpers use a safe merge pattern that removes conflicting keys from
# **kwargs before passing to ft.Text(). This allows callers to override
# defaults like size, weight, color without causing duplicate keyword errors.
#

def _safe_text_kwargs(defaults: dict, kwargs: dict) -> dict:
    """
    Safely merge text kwargs, removing any keys from kwargs that are
    already in defaults to prevent duplicate keyword argument errors.
    
    Args:
        defaults: Default key-value pairs to apply
        kwargs: User-provided kwargs that may override defaults
        
    Returns:
        Merged dict with no duplicate keys
    """
    # Remove conflicting keys from kwargs
    clean_kwargs = {k: v for k, v in kwargs.items() if k not in defaults}
    # Merge: defaults first, then overrides from original kwargs
    result = {**defaults, **{k: v for k, v in kwargs.items() if k in defaults}}
    # Add non-conflicting kwargs
    result.update(clean_kwargs)
    return result


def heading(text: str, size: int = Typography.SIZE_XXL, **kwargs):
    """
    Create a heading text.
    
    Args:
        text: Text content
        size: Font size (default: SIZE_XXL)
        **kwargs: Additional Text properties (weight, color, etc.)
    """
    defaults = {
        'size': size,
        'weight': Typography.WEIGHT_BOLD,
        'color': Colors.TEXT_PRIMARY,
    }
    merged = _safe_text_kwargs(defaults, kwargs)
    return ft.Text(text, **merged)


def label(text: str, **kwargs):
    """
    Create a label text (small, secondary color).
    
    Args:
        text: Text content
        **kwargs: Additional Text properties (can override size, weight, color)
    """
    defaults = {
        'size': Typography.SIZE_SM,
        'weight': Typography.WEIGHT_MEDIUM,
        'color': Colors.TEXT_SECONDARY,
    }
    merged = _safe_text_kwargs(defaults, kwargs)
    return ft.Text(text, **merged)


def body_text(text: str, **kwargs):
    """
    Create body text (default size, primary color).
    
    Args:
        text: Text content
        **kwargs: Additional Text properties (can override size, color, weight)
    """
    defaults = {
        'size': Typography.SIZE_MD,
        'color': Colors.TEXT_PRIMARY,
    }
    merged = _safe_text_kwargs(defaults, kwargs)
    return ft.Text(text, **merged)

