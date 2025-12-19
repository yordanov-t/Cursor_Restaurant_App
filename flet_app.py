"""
Flet UI for Restaurant Management System - Glassmorphism Edition.

Modern, professional UI using Flet framework with full functional parity.
Includes internationalization support for Bulgarian, English, French, and Russian.
"""

import flet as ft
from db import DBManager
from core import ReservationService, TableLayoutService, BackupService
from ui_flet.compat import log_compatibility_info, icons, ThemeMode, Colors as CompatColors
from ui_flet.app_state import AppState
from ui_flet.theme import Colors, Spacing, Radius
from ui_flet.i18n import t, get_flag, get_available_languages, LANGUAGES


def main(page: ft.Page):
    """Main Flet application entry point."""
    
    # Log compatibility info
    log_compatibility_info()
    
    # Initialize services
    db = DBManager()
    reservation_service = ReservationService(db)
    table_layout_service = TableLayoutService(db)
    backup_service = BackupService(db)
    
    # Ensure default waiters exist
    if not db.get_waiters():
        db.add_waiter("John Doe")
        db.add_waiter("Jane Smith")
    
    # ==========================================
    # Daily automatic backup on startup
    # ==========================================
    backup_filename = backup_service.create_daily_backup_if_needed()
    if backup_filename:
        print(f"Daily backup created: {backup_filename}")
    else:
        if backup_service.has_today_backup():
            print("Today's backup already exists.")
        else:
            print("No backup created (check for errors).")
    
    # Clean up old backups (keep last 30)
    deleted_count = backup_service.cleanup_old_backups(keep_count=30)
    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} old backup(s).")
    
    # Initialize application state
    app_state = AppState()
    
    # Page configuration - title will be updated dynamically
    page.title = t("app_title")
    page.theme_mode = ThemeMode.DARK
    
    # Gradient background (elegant blue-to-purple)
    page.bgcolor = CompatColors.TRANSPARENT  # Required for gradient
    page.decoration = ft.BoxDecoration(
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[
                Colors.GRADIENT_START,  # Deep blue
                Colors.GRADIENT_MID,     # Purple
                Colors.GRADIENT_END,     # Dark purple
            ],
        )
    )
    
    page.padding = 0
    page.window_width = 1400
    page.window_height = 900
    
    # Import screens (will be imported dynamically to avoid circular deps)
    from ui_flet.reservations_screen_v3 import create_reservations_screen
    from ui_flet.table_layout_screen_v2 import create_table_layout_screen
    from ui_flet.admin_screen_v2 import create_admin_screen
    
    # Main content container
    main_container = ft.Container(expand=True)
    
    # ==========================================
    # Language Switcher (Top-Left, flags only)
    # ==========================================
    
    def on_language_change(e):
        """Handle language change from dropdown."""
        new_lang = e.control.value
        if new_lang:
            app_state.language = new_lang
            # Update page title
            page.title = t("app_title")
            # Full UI refresh happens via app_state.on_state_change
    
    # Build language dropdown options with flags only
    language_options = [
        ft.dropdown.Option(key=lang_code, text=flag)
        for lang_code, flag in LANGUAGES.items()
    ]
    
    language_dropdown = ft.Dropdown(
        value=app_state.language,
        options=language_options,
        on_change=on_language_change,
        width=90,  # Wider to accommodate EN text and flags
        content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_color=Colors.BORDER,
        bgcolor=Colors.SURFACE_GLASS,
        focused_border_color=Colors.ACCENT_PRIMARY,
    )
    
    # Admin button (top-right) - will NOT be shown when admin is logged in
    # (the admin screen has its own logout button)
    admin_button = ft.IconButton(
        icon=icons.ADMIN_PANEL_SETTINGS,
        tooltip=t("admin"),
        icon_color=Colors.TEXT_PRIMARY,
        on_click=lambda e: toggle_admin()
    )
    
    def toggle_admin():
        """Toggle admin mode."""
        if app_state.admin_logged_in:
            app_state.set_admin_logged_in(False)
            app_state.navigate_to("reservations")
        else:
            app_state.navigate_to("admin")
        refresh_screen()
    
    def refresh_screen():
        """Refresh the current screen based on app state."""
        # Update language dropdown value
        language_dropdown.value = app_state.language
        
        # Update admin button visibility and tooltip
        # Hide admin button when in admin screen (admin has its own logout)
        admin_button.visible = app_state.current_screen != "admin"
        admin_button.tooltip = t("admin")
        
        # Update page title
        page.title = t("app_title")
        
        # Load appropriate screen
        if app_state.current_screen == "reservations":
            main_container.content = create_reservations_screen(
                page, reservation_service, table_layout_service, db, app_state, refresh_screen
            )
        elif app_state.current_screen == "table_layout":
            main_container.content = create_table_layout_screen(
                page, table_layout_service, app_state, refresh_screen
            )
        elif app_state.current_screen == "admin":
            main_container.content = create_admin_screen(
                page, db, app_state, refresh_screen
            )
        
        page.update()
    
    # Set state change callback
    app_state.on_state_change = refresh_screen
    
    # Build page layout with language switcher on the left
    page.add(
        ft.Column(
            [
                # Top bar with language switcher (left) and admin button (right)
                ft.Container(
                    content=ft.Row(
                        [
                            # Language switcher on the left
                            ft.Container(
                                content=language_dropdown,
                                padding=ft.padding.only(left=16),
                            ),
                            ft.Container(expand=True),  # Spacer
                            # Admin button on the right
                            admin_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(right=16, top=8),
                ),
                # Main content
                main_container,
            ],
            spacing=0,
            expand=True,
        )
    )
    
    # Initial screen load
    refresh_screen()


if __name__ == "__main__":
    ft.app(target=main)
