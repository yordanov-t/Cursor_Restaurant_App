"""
Flet UI for Restaurant Management System - Glassmorphism Edition.

Modern, professional UI using Flet framework with full functional parity.
"""

import flet as ft
from db import DBManager
from core import ReservationService, TableLayoutService
from ui_flet.compat import log_compatibility_info, icons, ThemeMode, Colors as CompatColors
from ui_flet.app_state import AppState
from ui_flet.theme import Colors


def main(page: ft.Page):
    """Main Flet application entry point."""
    
    # Log compatibility info
    log_compatibility_info()
    
    # Initialize services
    db = DBManager()
    reservation_service = ReservationService(db)
    table_layout_service = TableLayoutService(db)
    
    # Ensure default waiters exist
    if not db.get_waiters():
        db.add_waiter("John Doe")
        db.add_waiter("Jane Smith")
    
    # Initialize application state
    app_state = AppState()
    
    # Page configuration
    page.title = "Ресторант Хъшове"
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
    
    # Admin button (top-right)
    admin_button = ft.IconButton(
        icon=icons.ADMIN_PANEL_SETTINGS if not app_state.admin_logged_in else icons.LOGOUT,
        tooltip="Админ" if not app_state.admin_logged_in else "Изход от админ режим",
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
        # Update admin button
        admin_button.icon = icons.LOGOUT if app_state.admin_logged_in else icons.ADMIN_PANEL_SETTINGS
        admin_button.tooltip = "Изход от админ режим" if app_state.admin_logged_in else "Админ"
        
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
    
    # Build page layout
    page.add(
        ft.Column(
            [
                # Top bar with admin button
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(expand=True),  # Spacer
                            admin_button,
                        ],
                        alignment=ft.MainAxisAlignment.END,
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
