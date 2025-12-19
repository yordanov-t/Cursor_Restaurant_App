"""
Admin screen for Flet UI - V2 with full functionality, glassmorphism, and management panels.

Uses right-side Action Panel pattern for all operations (no popups).
Includes: Waiters, Sections, Tables, Backup management.
Supports internationalization.
"""

import flet as ft
from typing import Callable, List
from db import DBManager
from core import BackupService
from ui_flet.theme import (Colors, Spacing, Radius, Typography, heading, label,
                             body_text, glass_container, glass_button, glass_card)
from ui_flet.compat import icons, ScrollMode, FontWeight
from ui_flet.section_action_panel import SectionActionPanel
from ui_flet.admin_action_panel import AdminActionPanel, TABLE_SHAPES, get_shape_display
from ui_flet.backup_action_panel import BackupActionPanel
from ui_flet.i18n import t


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"


def create_admin_screen(
    page: ft.Page,
    db: DBManager,
    app_state,
    refresh_callback: Callable
):
    """Create the admin screen."""
    
    if not app_state.admin_logged_in:
        # Show login form
        
        def attempt_login(e=None):
            """Attempt login - called by button or Enter key."""
            if username_field.value == ADMIN_USERNAME and password_field.value == ADMIN_PASSWORD:
                app_state.set_admin_logged_in(True)
                page.snack_bar = ft.SnackBar(
                    ft.Text(t("welcome_admin")),
                    bgcolor=Colors.SUCCESS
                )
                page.snack_bar.open = True
                refresh_callback()
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text(t("invalid_credentials")),
                    bgcolor=Colors.DANGER
                )
                page.snack_bar.open = True
                page.update()
        
        username_field = ft.TextField(
            label=t("username"),
            width=300,
            text_size=Typography.SIZE_MD,
            on_submit=attempt_login,  # Enter key support
        )
        password_field = ft.TextField(
            label=t("password"),
            password=True,
            can_reveal_password=True,
            width=300,
            text_size=Typography.SIZE_MD,
            on_submit=attempt_login,  # Enter key support
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=heading(t("admin_panel")),
                        padding=Spacing.XL,
                    ),
                    ft.Container(
                        content=glass_card(
                            content=ft.Column([
                                heading(t("admin_login"), size=Typography.SIZE_XL),
                                ft.Divider(height=Spacing.LG, color=Colors.BORDER),
                                username_field,
                                password_field,
                                ft.Row([
                                    glass_button(t("login"), on_click=attempt_login, variant="primary"),
                                    glass_button(
                                        t("cancel"),
                                        on_click=lambda e: app_state.navigate_to("reservations"),
                                        variant="secondary"
                                    ),
                                ], spacing=Spacing.MD),
                            ], spacing=Spacing.LG, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ),
                        padding=Spacing.XL,
                        alignment=ft.alignment.center,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
        )
    
    # ==========================================
    # Logged in - show admin functions
    # ==========================================
    
    # Initialize backup service
    backup_service = BackupService(db)
    
    def logout(e):
        """Handle logout - single exit control in admin header."""
        app_state.set_admin_logged_in(False)
        app_state.navigate_to("reservations")
    
    # Main content container (will compress when panel opens)
    main_content = ft.Container(expand=True)
    
    # ==========================================
    # Waiter Management Tab (with Action Panel)
    # ==========================================
    waiters_list = ft.Column(spacing=Spacing.SM, scroll=ScrollMode.AUTO)
    
    def refresh_waiters():
        """Refresh the waiters list."""
        waiters = db.get_waiters()
        waiters_list.controls.clear()
        
        for w in waiters:
            waiter_id = w["id"]
            waiter_name = w["name"]
            waiter_copy = {"id": waiter_id, "name": waiter_name}
            
            card = glass_container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                body_text(waiter_name, weight=FontWeight.BOLD),
                                label(f"ID: {waiter_id}"),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Row([
                            ft.IconButton(
                                icon=icons.EDIT,
                                tooltip=t("edit"),
                                icon_color=Colors.ACCENT_PRIMARY,
                                on_click=lambda e, w=waiter_copy: admin_panel.open_waiter_edit(w),
                            ),
                            ft.IconButton(
                                icon=icons.DELETE,
                                tooltip=t("delete"),
                                icon_color=Colors.DANGER,
                                on_click=lambda e, w=waiter_copy: admin_panel.open_waiter_delete(w),
                            ),
                        ], spacing=0),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=Spacing.MD,
            )
            waiters_list.controls.append(card)
        
        page.update()
    
    # ==========================================
    # Sections Management Tab (with Action Panel)
    # ==========================================
    sections_list = ft.Column(spacing=Spacing.MD, scroll=ScrollMode.AUTO)
    
    def refresh_sections():
        """Refresh the sections list."""
        sections = db.get_all_section_tables()
        sections_list.controls.clear()
        
        for section in sections:
            section_id = section["id"]
            section_name = section["name"]
            section_tables = section["tables"]
            
            # Build tables display
            if section_tables:
                tables_text = ", ".join(str(t_num) for t_num in section_tables[:10])
                if len(section_tables) > 10:
                    tables_text += f" ... (+{len(section_tables) - 10})"
            else:
                tables_text = t("no_tables")
            
            section_copy = dict(section)
            
            card = glass_container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    body_text(section_name, weight=FontWeight.BOLD, size=Typography.SIZE_MD),
                                    label(f"{t('tables')} ({len(section_tables)}): {tables_text}", color=Colors.TEXT_SECONDARY),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.Row([
                                ft.IconButton(
                                    icon=icons.EDIT,
                                    tooltip=t("rename"),
                                    icon_color=Colors.ACCENT_PRIMARY,
                                    on_click=lambda e, s=section_copy: section_panel.open_edit(s),
                                ),
                                ft.IconButton(
                                    icon=icons.TABLE_CHART,
                                    tooltip=t("change_tables"),
                                    icon_color=Colors.WARNING,
                                    on_click=lambda e, s=section_copy: section_panel.open_assign_tables(s),
                                ),
                                ft.IconButton(
                                    icon=icons.DELETE,
                                    tooltip=t("delete"),
                                    icon_color=Colors.DANGER,
                                    on_click=lambda e, s=section_copy: section_panel.open_delete(s),
                                ),
                            ], spacing=0),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ]),
                padding=Spacing.MD,
            )
            sections_list.controls.append(card)
        
        page.update()
    
    # ==========================================
    # Tables Management Tab (with Action Panel)
    # ==========================================
    tables_list = ft.Column(spacing=Spacing.SM, scroll=ScrollMode.AUTO)
    
    def refresh_tables():
        """Refresh the tables list."""
        tables = db.get_all_tables()
        tables_list.controls.clear()
        
        for tbl in tables:
            table_num = tbl["table_number"]
            shape = tbl["shape"]
            shape_display = get_shape_display(shape)  # Use localized shape name
            table_copy = dict(tbl)
            
            # Shape indicator
            if shape == "ROUND":
                shape_border_radius = 25
            elif shape == "SQUARE":
                shape_border_radius = 4
            else:  # RECTANGLE
                shape_border_radius = 4
            
            shape_indicator = ft.Container(
                width=30 if shape != "SQUARE" else 20,
                height=20,
                bgcolor=Colors.ACCENT_PRIMARY + "40",
                border=ft.border.all(2, Colors.ACCENT_PRIMARY),
                border_radius=shape_border_radius if shape == "ROUND" else shape_border_radius,
            )
            
            card = glass_container(
                content=ft.Row(
                    [
                        ft.Row([
                            body_text(f"#{table_num}", weight=FontWeight.BOLD, size=Typography.SIZE_MD),
                            ft.Container(width=Spacing.MD),
                            shape_indicator,
                            ft.Container(width=Spacing.SM),
                            label(shape_display, color=Colors.TEXT_SECONDARY),
                        ], spacing=Spacing.XS),
                        ft.Row([
                            ft.IconButton(
                                icon=icons.EDIT,
                                tooltip=t("change_shape"),
                                icon_color=Colors.ACCENT_PRIMARY,
                                on_click=lambda e, tbl=table_copy: admin_panel.open_table_edit(tbl),
                            ),
                            ft.IconButton(
                                icon=icons.DELETE,
                                tooltip=t("delete"),
                                icon_color=Colors.DANGER,
                                on_click=lambda e, tbl=table_copy: admin_panel.open_table_delete(tbl),
                            ),
                        ], spacing=0),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=Spacing.MD,
            )
            tables_list.controls.append(card)
        
        page.update()
    
    # ==========================================
    # Backup Management Tab
    # ==========================================
    backups_list = ft.Column(spacing=Spacing.SM, scroll=ScrollMode.AUTO)
    
    def refresh_backups():
        """Refresh the backups list."""
        backups = backup_service.list_backups(include_counts=True)
        backups_list.controls.clear()
        
        if not backups:
            backups_list.controls.append(
                ft.Container(
                    content=body_text(t("no_backups"), color=Colors.TEXT_SECONDARY),
                    padding=Spacing.XL,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for backup in backups:
                backup_copy = dict(backup)
                timestamp_str = backup.get("timestamp_str", "")
                size_str = backup.get("size_str", "")
                counts = backup.get("counts", {})
                
                # Build counts summary
                counts_parts = []
                if counts.get("reservations", 0) > 0:
                    counts_parts.append(f"{counts['reservations']} {t('reservations')[:3]}.")
                if counts.get("waiters", 0) > 0:
                    counts_parts.append(f"{counts['waiters']} {t('waiters')[:4]}.")
                counts_summary = ", ".join(counts_parts) if counts_parts else ""
                
                card = glass_container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Row([
                                        ft.Icon(icons.BACKUP, color=Colors.ACCENT_PRIMARY, size=20),
                                        ft.Container(width=Spacing.XS),
                                        body_text(timestamp_str, weight=FontWeight.BOLD),
                                    ]),
                                    ft.Row([
                                        label(f"{t('size')}: {size_str}", color=Colors.TEXT_SECONDARY),
                                        ft.Container(width=Spacing.MD),
                                        label(counts_summary, color=Colors.TEXT_SECONDARY) if counts_summary else ft.Container(),
                                    ]),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.Row([
                                ft.IconButton(
                                    icon=icons.RESTORE,
                                    tooltip=t("restore"),
                                    icon_color=Colors.WARNING,
                                    on_click=lambda e, b=backup_copy: backup_panel.open_restore(b),
                                ),
                                ft.IconButton(
                                    icon=icons.DELETE,
                                    tooltip=t("delete"),
                                    icon_color=Colors.DANGER,
                                    on_click=lambda e, b=backup_copy: backup_panel.open_delete(b),
                                ),
                            ], spacing=0),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=Spacing.MD,
                )
                backups_list.controls.append(card)
        
        page.update()
    
    def create_manual_backup(e):
        """Create a manual backup."""
        filename = backup_service.create_backup()
        if filename:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"{t('backup_created')}: {filename}", color=Colors.TEXT_PRIMARY),
                bgcolor=Colors.SUCCESS
            )
            page.snack_bar.open = True
            refresh_backups()
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text(t("backup_error"), color=Colors.TEXT_PRIMARY),
                bgcolor=Colors.DANGER
            )
            page.snack_bar.open = True
        page.update()
    
    # ==========================================
    # Action Panel Callbacks
    # ==========================================
    
    def handle_panel_close():
        """Handle any panel close."""
        page.update()
    
    # Waiter callbacks
    def handle_waiter_create(name: str) -> bool:
        db.add_waiter(name)
        refresh_waiters()
        return True
    
    def handle_waiter_update(waiter_id: int, name: str) -> bool:
        db.update_waiter(waiter_id, name)
        refresh_waiters()
        return True
    
    def handle_waiter_delete(waiter_id: int):
        db.remove_waiter(waiter_id)
        refresh_waiters()
    
    # Section callbacks
    def handle_create_section(name: str, tables: List[int]) -> bool:
        section_id = db.create_section(name)
        if section_id:
            if tables:
                db.assign_tables_to_section(section_id, tables)
            refresh_sections()
            return True
        return False
    
    def handle_update_section(section_id: int, name: str) -> bool:
        result = db.update_section(section_id, name)
        if result:
            refresh_sections()
        return result
    
    def handle_assign_tables(section_id: int, tables: List[int]):
        db.assign_tables_to_section(section_id, tables)
        refresh_sections()
    
    def handle_delete_section(section_id: int):
        db.delete_section(section_id)
        refresh_sections()
    
    # Table callbacks
    def handle_table_create(table_number: int, shape: str) -> bool:
        result = db.create_table(table_number, shape)
        if result:
            refresh_tables()
        return result
    
    def handle_table_update(table_number: int, shape: str) -> bool:
        result = db.update_table_shape(table_number, shape)
        if result:
            refresh_tables()
        return result
    
    def handle_table_delete(table_number: int) -> bool:
        result = db.delete_table(table_number)
        if result:
            refresh_tables()
            refresh_sections()  # Update section table counts
        return result
    
    # Backup callbacks
    def handle_backup_delete(filename: str) -> bool:
        result = backup_service.delete_backup(filename)
        if result:
            refresh_backups()
        return result
    
    def handle_backup_restore(filename: str) -> bool:
        result = backup_service.restore_backup(filename)
        if result:
            # Refresh all data after restore
            refresh_waiters()
            refresh_sections()
            refresh_tables()
            refresh_backups()
            refresh_callback()  # Refresh main app state
        return result
    
    # ==========================================
    # Create Action Panels
    # ==========================================
    
    section_panel = SectionActionPanel(
        page=page,
        on_close=handle_panel_close,
        on_create=handle_create_section,
        on_update=handle_update_section,
        on_assign_tables=handle_assign_tables,
        on_delete=handle_delete_section,
    )
    
    admin_panel = AdminActionPanel(
        page=page,
        on_close=handle_panel_close,
        on_waiter_create=handle_waiter_create,
        on_waiter_update=handle_waiter_update,
        on_waiter_delete=handle_waiter_delete,
        on_table_create=handle_table_create,
        on_table_update=handle_table_update,
        on_table_delete=handle_table_delete,
    )
    
    backup_panel = BackupActionPanel(
        page=page,
        on_close=handle_panel_close,
        on_delete=handle_backup_delete,
        on_restore=handle_backup_restore,
    )
    
    # Initial data load
    refresh_waiters()
    refresh_sections()
    refresh_tables()
    refresh_backups()
    
    # ==========================================
    # Build Admin Screen with Tabs
    # ==========================================
    
    main_content.content = ft.Column(
        [
            # Header with logout (single exit control)
            ft.Container(
                content=ft.Row([
                    heading(t("admin_panel")),
                    ft.IconButton(
                        icon=icons.LOGOUT,
                        tooltip=t("logout_admin"),
                        icon_color=Colors.DANGER,
                        icon_size=28,
                        on_click=logout,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=Spacing.XL,
            ),
            
            # Admin functions with tabs
            ft.Container(
                content=ft.Tabs(
                    selected_index=0,
                    tabs=[
                        # Waiters Tab
                        ft.Tab(
                            text=t("waiters"),
                            icon=icons.PERSON,
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Row([
                                        glass_button(
                                            t("new_waiter"),
                                            icon=icons.ADD,
                                            on_click=lambda e: admin_panel.open_waiter_create(),
                                            variant="primary",
                                        ),
                                        ft.Container(
                                            content=body_text(
                                                t("manage_waiters_desc"),
                                                color=Colors.TEXT_SECONDARY,
                                                size=Typography.SIZE_SM,
                                            ),
                                            expand=True,
                                            padding=ft.padding.only(left=Spacing.LG),
                                        ),
                                    ]),
                                    padding=Spacing.LG,
                                ),
                                ft.Container(
                                    content=waiters_list,
                                    expand=True,
                                    padding=Spacing.LG,
                                ),
                            ]),
                        ),
                        
                        # Sections Tab
                        ft.Tab(
                            text=t("sections"),
                            icon=icons.GRID_VIEW,
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Row([
                                        glass_button(
                                            t("new_section"),
                                            icon=icons.ADD,
                                            on_click=lambda e: section_panel.open_create(),
                                            variant="primary",
                                        ),
                                        ft.Container(
                                            content=body_text(
                                                t("sections_desc"),
                                                color=Colors.TEXT_SECONDARY,
                                                size=Typography.SIZE_SM,
                                            ),
                                            expand=True,
                                            padding=ft.padding.only(left=Spacing.LG),
                                        ),
                                    ]),
                                    padding=Spacing.LG,
                                ),
                                ft.Container(
                                    content=sections_list,
                                    expand=True,
                                    padding=Spacing.LG,
                                ),
                            ]),
                        ),
                        
                        # Tables Tab
                        ft.Tab(
                            text=t("tables"),
                            icon=icons.TABLE_RESTAURANT,
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Row([
                                        glass_button(
                                            t("add_table"),
                                            icon=icons.ADD,
                                            on_click=lambda e: admin_panel.open_table_create(db.get_next_available_table_number()),
                                            variant="primary",
                                        ),
                                        ft.Container(
                                            content=body_text(
                                                t("manage_tables_desc"),
                                                color=Colors.TEXT_SECONDARY,
                                                size=Typography.SIZE_SM,
                                            ),
                                            expand=True,
                                            padding=ft.padding.only(left=Spacing.LG),
                                        ),
                                    ]),
                                    padding=Spacing.LG,
                                ),
                                ft.Container(
                                    content=tables_list,
                                    expand=True,
                                    padding=Spacing.LG,
                                ),
                            ]),
                        ),
                        
                        # Backup Tab
                        ft.Tab(
                            text=t("backup"),
                            icon=icons.BACKUP,
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Row([
                                        glass_button(
                                            t("backup_database"),
                                            icon=icons.BACKUP,
                                            on_click=create_manual_backup,
                                            variant="primary",
                                        ),
                                        ft.Container(
                                            content=body_text(
                                                t("backup_desc"),
                                                color=Colors.TEXT_SECONDARY,
                                                size=Typography.SIZE_SM,
                                            ),
                                            expand=True,
                                            padding=ft.padding.only(left=Spacing.LG),
                                        ),
                                    ]),
                                    padding=Spacing.LG,
                                ),
                                ft.Container(
                                    content=backups_list,
                                    expand=True,
                                    padding=Spacing.LG,
                                ),
                            ]),
                        ),
                        
                        # Reports Tab
                        ft.Tab(
                            text=t("reports"),
                            icon=icons.ASSESSMENT,
                            content=ft.Container(
                                content=body_text(t("reports_coming_soon"), color=Colors.TEXT_SECONDARY),
                                padding=Spacing.XL,
                            ),
                        ),
                    ],
                ),
                expand=True,
                padding=Spacing.LG,
            ),
        ],
        spacing=0,
        expand=True,
    )
    
    # Combined panels container (only one panel should be open at a time)
    panels_row = ft.Row([
        section_panel.container,
        admin_panel.container,
        backup_panel.container,
    ], spacing=0)
    
    # Return layout with action panels on the right
    return ft.Row(
        [
            main_content,
            panels_row,
        ],
        spacing=0,
        expand=True,
    )
