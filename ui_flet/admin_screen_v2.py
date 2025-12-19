"""
Admin screen for Flet UI - V2 with full functionality, glassmorphism, and management panels.

Uses right-side Action Panel pattern for all operations (no popups).
Includes: Waiters, Sections, Tables management.
"""

import flet as ft
from typing import Callable, List
from db import DBManager
from ui_flet.theme import (Colors, Spacing, Radius, Typography, heading, label,
                             body_text, glass_container, glass_button, glass_card)
from ui_flet.compat import icons, ScrollMode, FontWeight
from ui_flet.section_action_panel import SectionActionPanel
from ui_flet.admin_action_panel import AdminActionPanel, TABLE_SHAPES


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
                                tooltip="Редактирай",
                                icon_color=Colors.ACCENT_PRIMARY,
                                on_click=lambda e, w=waiter_copy: admin_panel.open_waiter_edit(w),
                            ),
                            ft.IconButton(
                                icon=icons.DELETE,
                                tooltip="Изтрий",
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
                tables_text = ", ".join(str(t) for t in section_tables[:10])
                if len(section_tables) > 10:
                    tables_text += f" ... (+{len(section_tables) - 10})"
            else:
                tables_text = "Няма маси"
            
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
    
    # ==========================================
    # Tables Management Tab (with Action Panel)
    # ==========================================
    tables_list = ft.Column(spacing=Spacing.SM, scroll=ScrollMode.AUTO)
    
    def refresh_tables():
        """Refresh the tables list."""
        tables = db.get_all_tables()
        tables_list.controls.clear()
        
        for t in tables:
            table_num = t["table_number"]
            shape = t["shape"]
            shape_display = TABLE_SHAPES.get(shape, shape)
            table_copy = dict(t)
            
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
                                tooltip="Промени форма",
                                icon_color=Colors.ACCENT_PRIMARY,
                                on_click=lambda e, t=table_copy: admin_panel.open_table_edit(t),
                            ),
                            ft.IconButton(
                                icon=icons.DELETE,
                                tooltip="Изтрий",
                                icon_color=Colors.DANGER,
                                on_click=lambda e, t=table_copy: admin_panel.open_table_delete(t),
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
    
    # Initial data load
    refresh_waiters()
    refresh_sections()
    refresh_tables()
    
    # ==========================================
    # Build Admin Screen with Tabs
    # ==========================================
    
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
                                    content=ft.Row([
                                        glass_button(
                                            "Нов сервитьор",
                                            icon=icons.ADD,
                                            on_click=lambda e: admin_panel.open_waiter_create(),
                                            variant="primary",
                                        ),
                                        ft.Container(
                                            content=body_text(
                                                "Управлявайте сервитьорите на ресторанта.",
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
                        
                        # Tables Tab (NEW)
                        ft.Tab(
                            text="Маси",
                            icon=icons.TABLE_RESTAURANT,
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Row([
                                        glass_button(
                                            "Добави маса",
                                            icon=icons.ADD,
                                            on_click=lambda e: admin_panel.open_table_create(db.get_next_available_table_number()),
                                            variant="primary",
                                        ),
                                        ft.Container(
                                            content=body_text(
                                                "Управлявайте масите и техните форми.",
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
    
    # Combined panels container (section panel OR admin panel can be open)
    # We'll use a Stack approach - only one panel should be open at a time
    panels_row = ft.Row([
        section_panel.container,
        admin_panel.container,
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
