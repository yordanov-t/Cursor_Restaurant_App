"""
Flet UI for Restaurant Management System - Glassmorphism Edition.

Modern, professional UI using Flet framework with full functional parity.
Includes internationalization support for Bulgarian, English, French, and Russian.
Works on both desktop and mobile (Android/iOS) with cross-platform storage.
"""

import flet as ft

# Direct logcat logging for Android debugging
_android_log = None
try:
    from ctypes import cdll, c_int, c_char_p
    _liblog = cdll.LoadLibrary("liblog.so")
    _liblog.__android_log_write.argtypes = [c_int, c_char_p, c_char_p]
    _liblog.__android_log_write.restype = c_int
    _android_log = _liblog.__android_log_write
except Exception:
    pass

def _lc(msg):
    if _android_log:
        try:
            _android_log(4, b"py_flet_app", str(msg).encode("utf-8", errors="replace"))
        except Exception:
            pass

_lc("flet_app.py: importing core...")
from core import ReservationService, TableLayoutService, BackupService, ensure_storage_initialized
_lc("flet_app.py: importing db...")
from db import DBManager
_lc("flet_app.py: importing compat...")
from ui_flet.compat import log_compatibility_info, icons, ThemeMode, Colors as CompatColors
_lc("flet_app.py: importing app_state...")
from ui_flet.app_state import AppState
_lc("flet_app.py: importing theme...")
from ui_flet.theme import Colors, Spacing, Radius
_lc("flet_app.py: importing i18n...")
from ui_flet.i18n import t, get_flag, get_available_languages, LANGUAGES
_lc("flet_app.py: importing theme_manager...")
from ui_flet.theme_manager import get_available_themes, THEMES
_lc("flet_app.py: ALL IMPORTS OK")


def main(page: ft.Page):
    """Main Flet application entry point."""
    
    # Wrap EVERYTHING in try-except to catch startup failures
    try:
        _init_app(page)
    except Exception as e:
        # Show error UI if startup fails
        _show_error_ui(page, e)


def _show_error_ui(page: ft.Page, error: Exception):
    """Show minimal error UI when app startup fails."""
    import traceback
    error_msg = str(error)
    tb_str = traceback.format_exc()
    
    print(f"[FATAL] App startup failed: {error_msg}")
    print(tb_str)
    
    try:
        page.clean()
        page.bgcolor = ft.colors.RED_900
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("App Startup Failed", size=32, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Error: {error_msg}", size=16, color=ft.colors.WHITE, selectable=True),
                    ft.Container(
                        content=ft.Text(tb_str, size=12, color=ft.colors.WHITE, selectable=True),
                        bgcolor=ft.colors.BLACK,
                        padding=10,
                        border_radius=5,
                    ),
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20,
                expand=True,
            )
        )
        page.update()
    except:
        # If even error UI fails, at least we tried
        pass


def _init_app(page: ft.Page):
    """Initialize the app (separated for error handling)."""
    
    _lc("_init_app: start")
    log_compatibility_info()
    
    _lc("_init_app: ensure_storage_initialized...")
    ensure_storage_initialized()
    
    _lc("_init_app: creating DBManager...")
    db = DBManager()
    _lc("_init_app: creating services...")
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

    # Fullscreen mode - hides the Android status bar (clock, battery, notifications)
    try:
        page.window_full_screen = True
    except Exception:
        pass  # Ignore if not supported in this Flet build
    
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
    
    _lc("_init_app: importing screens...")
    from ui_flet.reservations_screen_v3 import create_reservations_screen
    from ui_flet.table_layout_screen_v2 import create_table_layout_screen
    from ui_flet.admin_screen_v2 import create_admin_screen
    from ui_flet.user_settings_screen import create_user_settings_screen
    _lc("_init_app: screens imported OK")
    
    # Main content container
    main_container = ft.Container(expand=True)
    
    # ==========================================
    # User Settings Button (Top-Right, next to Admin)
    # ==========================================
    
    user_settings_button = ft.IconButton(
        icon=icons.SETTINGS,
        tooltip=t("user_settings"),
        icon_color=Colors.ICON_COLOR,
        on_click=lambda e: app_state.navigate_to("user_settings")
    )
    
    # ==========================================
    # Language Switcher (Top-Left, flags only) - REMOVED, moved to User Settings
    # ==========================================
    
    # ==========================================
    # Theme Switcher (Top-Left, next to language) - REMOVED, moved to User Settings
    # ==========================================
    
    # Admin button (top-right) - will NOT be shown when admin is logged in
    # (the admin screen has its own logout button)
    admin_button = ft.IconButton(
        icon=icons.ADMIN_PANEL_SETTINGS,
        tooltip=t("admin"),
        icon_color=Colors.ICON_COLOR,
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
        try:
            _lc(f"refresh_screen: screen={app_state.current_screen}")
            # Update page gradient with current theme colors
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

            # Update button visibility and tooltips
            # Hide admin/settings buttons when in admin or settings screen
            admin_button.visible = app_state.current_screen not in ("admin", "user_settings")
            user_settings_button.visible = app_state.current_screen not in ("admin", "user_settings")
            admin_button.tooltip = t("admin")
            user_settings_button.tooltip = t("user_settings")

            # Update icon colors based on theme
            admin_button.icon_color = Colors.ICON_COLOR
            user_settings_button.icon_color = Colors.ICON_COLOR

            # Update page title
            page.title = t("app_title")

            # Load appropriate screen
            _lc(f"refresh_screen: creating screen content...")
            if app_state.current_screen == "reservations":
                main_container.content = create_reservations_screen(
                    page, reservation_service, table_layout_service, db, app_state, refresh_screen
                )
            elif app_state.current_screen == "table_layout":
                main_container.content = create_table_layout_screen(
                    page, table_layout_service, app_state, refresh_screen, reservation_service
                )
            elif app_state.current_screen == "admin":
                main_container.content = create_admin_screen(
                    page, db, app_state, refresh_screen
                )
            elif app_state.current_screen == "user_settings":
                main_container.content = create_user_settings_screen(
                    page, db, app_state, refresh_screen
                )

            _lc(f"refresh_screen: calling page.update()...")
            page.update()
            _lc(f"refresh_screen: DONE")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            _lc(f"refresh_screen EXCEPTION: {e}")
            _lc(tb[:500])
            # Show error on screen
            try:
                page.clean()
                page.add(ft.Column([
                    ft.Text("Screen Load Error", size=24, color="red", weight="bold"),
                    ft.Text(f"{e}", size=14, selectable=True),
                    ft.Text(tb[:400], size=10, selectable=True, color="grey"),
                ], scroll="auto", spacing=10))
                page.update()
            except Exception:
                pass
    
    # Set state change callback
    app_state.on_state_change = refresh_screen
    
    # Build page layout with user settings + admin buttons on the right
    page.add(
        ft.Column(
            [
                # Top bar with settings + admin buttons on the right
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(expand=True),  # Spacer pushes buttons to right
                            # User settings button
                            user_settings_button,
                            # Admin button
                            admin_button,
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    padding=ft.padding.only(right=12, top=4),  # Reduced padding
                ),
                # Main content
                main_container,
            ],
            spacing=0,
            expand=True,
        )
    )
    
    _lc("_init_app: calling refresh_screen (initial load)...")
    refresh_screen()
    _lc("_init_app: COMPLETE - UI should be visible now")


if __name__ == "__main__":
    ft.app(target=main)
