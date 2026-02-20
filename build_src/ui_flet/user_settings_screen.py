"""
User settings screen for Flet UI.

Allows users to configure:
- Language
- Theme
- Default waiter for reservations
"""

import flet as ft
from typing import Callable
from db import DBManager
from ui_flet.theme import (Colors, Spacing, Radius, Typography, heading, label, 
                             glass_container, glass_button)
from ui_flet.compat import icons, FontWeight
from ui_flet.i18n import t, LANGUAGES
from ui_flet.theme_manager import THEMES


def create_user_settings_screen(
    page: ft.Page,
    db: DBManager,
    app_state,
    refresh_callback: Callable
):
    """Create the user settings screen."""
    
    # ==========================================
    # Language Selector
    # ==========================================
    
    def on_language_change(e):
        """Handle language change from dropdown."""
        new_lang = e.control.value
        if new_lang:
            app_state.language = new_lang
            page.title = t("app_title")
            # Trigger full UI refresh
            refresh_callback()
    
    # Build language dropdown options with flags
    language_options = [
        ft.dropdown.Option(key=lang_code, text=f"{flag} {lang_code.upper()}")
        for lang_code, flag in LANGUAGES.items()
    ]
    
    language_dropdown = ft.Dropdown(
        label=t("language"),
        value=app_state.language,
        options=language_options,
        on_change=on_language_change,
        width=None,
        bgcolor=Colors.SURFACE_GLASS,
        border_color=Colors.BORDER,
        focused_border_color=Colors.ACCENT_PRIMARY,
        color=Colors.INPUT_TEXT,  # Use theme input text color
    )
    
    # ==========================================
    # Theme Selector
    # ==========================================
    
    def on_theme_change(e):
        """Handle theme change from dropdown."""
        new_theme = e.control.value
        if new_theme:
            app_state.theme = new_theme
            # Update page gradient background
            page.decoration = ft.BoxDecoration(
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[
                        Colors.GRADIENT_START,
                        Colors.GRADIENT_MID,
                        Colors.GRADIENT_END,
                    ],
                )
            )
            # Trigger full UI refresh
            refresh_callback()
    
    # Build theme dropdown options with icons
    theme_options = [
        ft.dropdown.Option(key=theme_code, text=f"{icon} {t(f'theme_{theme_code}')}")
        for theme_code, icon in THEMES.items()
    ]
    
    theme_dropdown = ft.Dropdown(
        label=t("theme"),
        value=app_state.theme,
        options=theme_options,
        on_change=on_theme_change,
        width=None,
        bgcolor=Colors.SURFACE_GLASS,
        border_color=Colors.BORDER,
        focused_border_color=Colors.ACCENT_PRIMARY,
        color=Colors.INPUT_TEXT,  # Use theme input text color
    )
    
    # ==========================================
    # Current Waiter Selector
    # ==========================================
    
    def on_waiter_change(e):
        """Handle waiter selection change."""
        selected = e.control.value
        # Empty string or None means no waiter selected
        if selected == "" or selected is None:
            app_state.current_waiter_id = None
        else:
            try:
                app_state.current_waiter_id = int(selected)
            except (ValueError, TypeError):
                app_state.current_waiter_id = None
    
    # Build waiter dropdown options
    waiters = db.get_waiters()
    waiter_options = [ft.dropdown.Option(key="", text=t("none"))]
    for waiter in waiters:
        waiter_options.append(
            ft.dropdown.Option(key=str(waiter["id"]), text=waiter["name"])
        )
    
    waiter_dropdown = ft.Dropdown(
        label=t("current_waiter"),
        value=str(app_state.current_waiter_id) if app_state.current_waiter_id else "",
        options=waiter_options,
        on_change=on_waiter_change,
        width=None,
        bgcolor=Colors.SURFACE_GLASS,
        border_color=Colors.BORDER,
        focused_border_color=Colors.ACCENT_PRIMARY,
        color=Colors.INPUT_TEXT,  # Use theme input text color
    )
    
    # ==========================================
    # Build Settings Screen
    # ==========================================
    
    settings_content = ft.Container(
        content=ft.Column(
            [
                # Header
                ft.Container(
                    content=heading(t("user_settings"), size=Typography.SIZE_XXL, weight=FontWeight.BOLD),
                    padding=ft.padding.only(bottom=Spacing.LG),
                ),
                
                # Settings card
                glass_container(
                    content=ft.Column(
                        [
                            # Language setting
                            ft.Container(
                                content=ft.Column([
                                    label(t("language"), color=Colors.TEXT_SECONDARY),
                                    ft.Container(height=Spacing.XS),
                                    language_dropdown,
                                ]),
                                padding=ft.padding.only(bottom=Spacing.LG),
                            ),
                            
                            # Theme setting
                            ft.Container(
                                content=ft.Column([
                                    label(t("theme"), color=Colors.TEXT_SECONDARY),
                                    ft.Container(height=Spacing.XS),
                                    theme_dropdown,
                                ]),
                                padding=ft.padding.only(bottom=Spacing.LG),
                            ),
                            
                            # Waiter setting
                            ft.Container(
                                content=ft.Column([
                                    label(t("current_waiter"), color=Colors.TEXT_SECONDARY),
                                    ft.Container(height=Spacing.XS),
                                    waiter_dropdown,
                                ]),
                            ),
                        ],
                        spacing=0,
                    ),
                    padding=Spacing.XL,
                ),
                
                ft.Container(height=Spacing.XL),
                
                # Back button
                glass_button(
                    t("back_to_reservations"),
                    icon=icons.ARROW_BACK,
                    on_click=lambda e: app_state.navigate_to("reservations"),
                    variant="secondary",
                    width=None,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        padding=Spacing.XL,
        expand=True,
    )
    
    return settings_content
