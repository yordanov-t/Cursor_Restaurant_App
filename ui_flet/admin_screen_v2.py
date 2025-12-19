"""
Admin screen for Flet UI - V2 with full functionality, glassmorphism, and sections management.

Uses right-side Action Panel pattern for section operations (no popups).
"""

import flet as ft
from typing import Callable, List
from db import DBManager
from ui_flet.theme import (Colors, Spacing, Radius, Typography, heading, label,
                             body_text, glass_container, glass_button, glass_card)
from ui_flet.compat import icons, ScrollMode, FontWeight
from ui_flet.section_action_panel import SectionActionPanel


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
        username_field = ft.TextField(
            label="Потребителско име",
            width=300,
            text_size=Typography.SIZE_MD,
        )
        password_field = ft.TextField(
            label="Парола",
            password=True,
            can_reveal_password=True,
            width=300,
            text_size=Typography.SIZE_MD,
        )
        
        def attempt_login(e):
            if username_field.value == ADMIN_USERNAME and password_field.value == ADMIN_PASSWORD:
                app_state.set_admin_logged_in(True)
                page.snack_bar = ft.SnackBar(
                    ft.Text("Добре дошли, Администратор!"),
                    bgcolor=Colors.SUCCESS
                )
                page.snack_bar.open = True
                refresh_callback()
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Невалидни администраторски данни"),
                    bgcolor=Colors.DANGER
                )
                page.snack_bar.open = True
                page.update()
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=heading("Администраторски панел"),
                        padding=Spacing.XL,
                    ),
                    ft.Container(
                        content=glass_card(
                            content=ft.Column([
                                heading("Вход за администратор", size=Typography.SIZE_XL),
                                ft.Divider(height=Spacing.LG, color=Colors.BORDER),
                                username_field,
                                password_field,
                                ft.Row([
                                    glass_button("Вход", on_click=attempt_login, variant="primary"),
                                    glass_button(
                                        "Отказ",
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
    
    def logout(e):
        """Handle logout - only one exit control (top header)."""
        app_state.set_admin_logged_in(False)
        app_state.navigate_to("reservations")
    
    # Main content container (will compress when panel opens)
    main_content = ft.Container(expand=True)
    
    # ==========================================
    # Waiter Management Tab
    # ==========================================
    waiters_list = ft.Column(spacing=Spacing.SM, scroll=ScrollMode.AUTO)
    
    def refresh_waiters():
        waiters = db.get_waiters()
        waiters_list.controls.clear()
        for w in waiters:
            waiter_id = w["id"]
            card = glass_container(
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                body_text(w["name"], weight=FontWeight.BOLD),
                                label(f"ID: {waiter_id}"),
                            ],
                            spacing=2,
                        ),
                        ft.IconButton(
                            icon=icons.DELETE,
                            tooltip="Изтрий",
                            icon_color=Colors.DANGER,
                            on_click=lambda e, wid=waiter_id: delete_waiter(wid)
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=Spacing.MD,
            )
            waiters_list.controls.append(card)
        page.update()
    
    def add_waiter(e):
        name_field = ft.TextField(label="Име на сервитьор", width=300)
        
        def save_waiter(e):
            if name_field.value:
                db.add_waiter(name_field.value)
                refresh_waiters()
                page.dialog.open = False
                page.snack_bar = ft.SnackBar(
                    ft.Text("Сервитьорът е добавен"),
                    bgcolor=Colors.SUCCESS
                )
                page.snack_bar.open = True
                page.update()
        
        dialog = ft.AlertDialog(
            title=heading("Добави сервитьор", size=Typography.SIZE_LG),
            content=name_field,
            actions=[
                ft.TextButton("Запази", on_click=save_waiter),
                ft.TextButton("Отказ", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
            ],
            bgcolor=Colors.SURFACE,
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def delete_waiter(waiter_id):
        db.remove_waiter(waiter_id)
        refresh_waiters()
        page.snack_bar = ft.SnackBar(
            ft.Text("Сервитьорът е изтрит"),
            bgcolor=Colors.SUCCESS
        )
        page.snack_bar.open = True
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
                tables_text = ", ".join(str(t) for t in section_tables[:10])
                if len(section_tables) > 10:
                    tables_text += f" ... (+{len(section_tables) - 10})"
            else:
                tables_text = "Няма маси"
            
            # Create a copy of section data for closures
            section_copy = dict(section)
            
            card = glass_container(
                content=ft.Column([
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    body_text(section_name, weight=FontWeight.BOLD, size=Typography.SIZE_MD),
                                    label(f"Маси ({len(section_tables)}): {tables_text}", color=Colors.TEXT_SECONDARY),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.Row([
                                ft.IconButton(
                                    icon=icons.EDIT,
                                    tooltip="Преименувай",
                                    icon_color=Colors.ACCENT_PRIMARY,
                                    on_click=lambda e, s=section_copy: section_panel.open_edit(s),
                                ),
                                ft.IconButton(
                                    icon=icons.TABLE_CHART,
                                    tooltip="Промени маси",
                                    icon_color=Colors.WARNING,
                                    on_click=lambda e, s=section_copy: section_panel.open_assign_tables(s),
                                ),
                                ft.IconButton(
                                    icon=icons.DELETE,
                                    tooltip="Изтрий",
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
    
    # Section Action Panel callbacks
    def handle_section_panel_close():
        """Handle section panel close."""
        page.update()
    
    def handle_create_section(name: str, tables: List[int]) -> bool:
        """Handle create section from panel."""
        section_id = db.create_section(name)
        if section_id:
            if tables:
                db.assign_tables_to_section(section_id, tables)
            refresh_sections()
            return True
        return False
    
    def handle_update_section(section_id: int, name: str) -> bool:
        """Handle update section from panel."""
        result = db.update_section(section_id, name)
        if result:
            refresh_sections()
        return result
    
    def handle_assign_tables(section_id: int, tables: List[int]):
        """Handle assign tables from panel."""
        db.assign_tables_to_section(section_id, tables)
        refresh_sections()
    
    def handle_delete_section(section_id: int):
        """Handle delete section from panel."""
        db.delete_section(section_id)
        refresh_sections()
    
    # Create section action panel
    section_panel = SectionActionPanel(
        page=page,
        on_close=handle_section_panel_close,
        on_create=handle_create_section,
        on_update=handle_update_section,
        on_assign_tables=handle_assign_tables,
        on_delete=handle_delete_section,
    )
    
    # Initial data load
    refresh_waiters()
    refresh_sections()
    
    # ==========================================
    # Build Admin Screen with Tabs
    # ==========================================
    
    # Build main content with tabs
    main_content.content = ft.Column(
        [
            # Header with logout (single exit control)
            ft.Container(
                content=ft.Row([
                    heading("Администраторски панел"),
                    ft.IconButton(
                        icon=icons.LOGOUT,
                        tooltip="Изход от админ режим",
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
                            text="Сервитьори",
                            icon=icons.PERSON,
                            content=ft.Column([
                                ft.Container(
                                    content=glass_button(
                                        "Добави сервитьор",
                                        icon=icons.ADD,
                                        on_click=add_waiter,
                                        variant="primary",
                                    ),
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
                            text="Секции",
                            icon=icons.GRID_VIEW,
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Row([
                                        glass_button(
                                            "Нова секция",
                                            icon=icons.ADD,
                                            on_click=lambda e: section_panel.open_create(),
                                            variant="primary",
                                        ),
                                        ft.Container(
                                            content=body_text(
                                                "Секциите групират масите в зони.",
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
                        
                        # Reports Tab
                        ft.Tab(
                            text="Отчети",
                            icon=icons.ASSESSMENT,
                            content=ft.Container(
                                content=body_text("Отчети ще бъдат добавени скоро", color=Colors.TEXT_SECONDARY),
                                padding=Spacing.XL,
                            ),
                        ),
                        
                        # Backup Tab
                        ft.Tab(
                            text="Архивиране",
                            icon=icons.BACKUP,
                            content=ft.Container(
                                content=ft.Column([
                                    glass_button("Архивирай базата", icon=icons.BACKUP, variant="secondary"),
                                    glass_button("Възстанови базата", icon=icons.RESTORE, variant="secondary"),
                                ], spacing=Spacing.MD),
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
    
    # Return layout with section action panel on the right
    return ft.Row(
        [
            main_content,
            section_panel.container,
        ],
        spacing=0,
        expand=True,
    )
