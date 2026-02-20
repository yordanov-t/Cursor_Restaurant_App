"""
Glassmorphism / Liquid Glass Design System for Flet UI.

Modern 2026 design with consistent spacing, colors, and glass effects.
Uses theme manager for multi-theme support.
"""

import flet as ft
from ui_flet.theme_manager import get_palette


# ============================================================================
# COLOR PALETTE - Dynamic (from theme manager)
# ============================================================================

class _ColorsProxy:
    """Dynamic proxy for theme colors."""
    
    def __init__(self):
        self._palette = get_palette()
    
    def refresh(self):
        """Refresh colors from current theme palette."""
        self._palette = get_palette()
    
    # Base colors
    @property
    def BACKGROUND(self):
        return self._palette.background
    
    @property
    def SURFACE(self):
        return self._palette.surface
    
    @property
    def SURFACE_GLASS(self):
        return self._palette.surface_glass
    
    @property
    def SURFACE_GLASS_HOVER(self):
        return self._palette.surface_glass_hover
    
    @property
    def SURFACE_ELEVATED(self):
        return self._palette.surface_elevated
    
    # Gradient colors
    @property
    def GRADIENT_START(self):
        return self._palette.gradient_start
    
    @property
    def GRADIENT_MID(self):
        return self._palette.gradient_mid
    
    @property
    def GRADIENT_END(self):
        return self._palette.gradient_end
    
    # Text colors
    @property
    def TEXT_PRIMARY(self):
        return self._palette.text_primary
    
    @property
    def TEXT_SECONDARY(self):
        return self._palette.text_secondary
    
    @property
    def TEXT_DISABLED(self):
        return self._palette.text_disabled
    
    @property
    def BUTTON_TEXT(self):
        return self._palette.button_text
    
    @property
    def INPUT_TEXT(self):
        return self._palette.input_text
    
    @property
    def ICON_COLOR(self):
        return self._palette.icon_color
    
    # Accent colors
    @property
    def ACCENT_PRIMARY(self):
        return self._palette.accent_primary
    
    @property
    def ACCENT_SECONDARY(self):
        return self._palette.accent_secondary
    
    # Status colors
    @property
    def SUCCESS(self):
        return self._palette.success
    
    @property
    def SUCCESS_GLASS(self):
        return self._palette.success_glass
    
    @property
    def WARNING(self):
        return self._palette.warning
    
    @property
    def WARNING_GLASS(self):
        return self._palette.warning_glass
    
    @property
    def DANGER(self):
        return self._palette.danger
    
    @property
    def DANGER_GLASS(self):
        return self._palette.danger_glass
    
    # Table states
    @property
    def TABLE_FREE(self):
        return self._palette.table_free
    
    @property
    def TABLE_OCCUPIED(self):
        return self._palette.table_occupied
    
    @property
    def TABLE_SOON(self):
        return self._palette.table_soon
    
    @property
    def TABLE_FREE_SELECTED(self):
        return self._palette.table_free_selected
    
    @property
    def TABLE_OCCUPIED_SELECTED(self):
        return self._palette.table_occupied_selected
    
    @property
    def TABLE_SOON_SELECTED(self):
        return self._palette.table_soon_selected
    
    # Borders & overlays
    @property
    def BORDER(self):
        return self._palette.border
    
    @property
    def BORDER_FOCUS(self):
        return self._palette.border_focus
    
    @property
    def BORDER_SELECTED(self):
        return self._palette.border_selected
    
    @property
    def OVERLAY(self):
        return self._palette.overlay


# Global Colors instance
Colors = _ColorsProxy()


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
# TOUCH / MOBILE CONSTANTS
# ============================================================================

class Touch:
    """
    Touch-friendly sizing for mobile devices.
    
    Based on WCAG 2.1 and Material Design guidelines:
    - Minimum touch target: 44px (WCAG)
    - Recommended touch target: 48px (Material)
    """
    MIN_TAP_TARGET = 44  # Minimum tappable area
    RECOMMENDED_TAP_TARGET = 48  # Recommended tappable area
    ICON_BUTTON_SIZE = 48  # Size for icon buttons on mobile
    TOUCH_PADDING = 12  # Extra padding for touch targets


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
        color=Colors.BUTTON_TEXT,  # Use button-specific text color
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


def touch_icon_button(
    icon,
    on_click=None,
    tooltip: str = None,
    icon_color: str = Colors.TEXT_PRIMARY,
    icon_size: int = 24,
    **kwargs
):
    """
    Create a touch-friendly icon button with larger tap target.
    
    Wraps ft.IconButton in a Container to ensure minimum touch target size
    for accessibility on mobile devices.
    
    Args:
        icon: Icon to display
        on_click: Click handler
        tooltip: Optional tooltip text
        icon_color: Icon color
        icon_size: Icon size
        **kwargs: Additional IconButton properties
    """
    return ft.Container(
        content=ft.IconButton(
            icon=icon,
            on_click=on_click,
            tooltip=tooltip,
            icon_color=icon_color,
            icon_size=icon_size,
            **kwargs
        ),
        width=Touch.ICON_BUTTON_SIZE,
        height=Touch.ICON_BUTTON_SIZE,
        alignment=ft.alignment.center,
    )


def touch_button(
    text: str,
    on_click=None,
    icon=None,
    variant: str = "primary",
    **kwargs
):
    """
    Create a touch-friendly button with adequate touch target size.
    
    Args:
        text: Button text
        on_click: Click handler
        icon: Optional icon
        variant: Button variant (primary, secondary, danger, success)
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
        bgcolor=colors.get(variant, Colors.ACCENT_PRIMARY),
        color=Colors.BUTTON_TEXT,  # Use button-specific text color
        height=Touch.ICON_BUTTON_SIZE,  # Ensure touch-friendly height
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=Radius.SM),
            padding=ft.padding.symmetric(horizontal=Spacing.LG, vertical=Touch.TOUCH_PADDING),
        ),
        **kwargs
    )

