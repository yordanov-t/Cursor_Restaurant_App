"""
Admin screen for Flet UI.

Admin panel with login, waiter management, reports, and backup/restore.
"""

import flet as ft
from typing import Callable, List
from db import DBManager
from ui_flet.compat import Colors, icons, FontWeight, CrossAxisAlignment, MainAxisAlignment, alignment


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"


def create_admin_screen(
    page: ft.Page,
    db: DBManager,
    admin_logged_in: List[bool],
    on_navigate_to_reservations: Callable
):
    """Create the admin screen."""
    
    if not admin_logged_in[0]:
        # Show login form
        username_field = ft.TextField(label="Потребителско име", width=300)
        password_field = ft.TextField(label="Парола", password=True, can_reveal_password=True, width=300)
        
        def attempt_login(e):
            if username_field.value == ADMIN_USERNAME and password_field.value == ADMIN_PASSWORD:
                admin_logged_in[0] = True
                page.snack_bar = ft.SnackBar(ft.Text("Добре дошли, Администратор!"), bgcolor=Colors.SUCCESS)
                page.snack_bar.open = True
                on_navigate_to_reservations()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Невалидни администраторски данни"), bgcolor=Colors.ERROR)
                page.snack_bar.open = True
                page.update()
        
        return ft.Column(
            [
                ft.Container(
                    content=ft.Text("Администраторски панел", size=24, weight=FontWeight.BOLD),
                    padding=20,
                    bgcolor=Colors.SURFACE_VARIANT,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Вход за администратор", size=20, weight=FontWeight.W_500),
                        ft.Divider(height=20),
                        username_field,
                        password_field,
                        ft.Row([
                            ft.ElevatedButton("Вход", on_click=attempt_login),
                            ft.TextButton("Отказ", on_click=on_navigate_to_reservations),
                        ], spacing=10),
                    ], horizontal_alignment=CrossAxisAlignment.CENTER),
                    padding=40,
                    alignment=alignment.center,
                    expand=True,
                ),
            ],
            expand=True,
        )
    
    # Logged in - show admin functions
    def logout(e):
        admin_logged_in[0] = False
        on_navigate_to_reservations()
    
    # Waiter management
    waiters_list = ft.ListView(spacing=10, padding=20)
    
    def refresh_waiters():
        waiters = db.get_waiters()
        waiters_list.controls.clear()
        for w in waiters:
            waiters_list.controls.append(
                ft.ListTile(
                    title=ft.Text(w["name"]),
                    subtitle=ft.Text(f"ID: {w['id']}"),
                    trailing=ft.IconButton(
                        icon=icons.DELETE,
                        on_click=lambda e, wid=w["id"]: delete_waiter(wid)
                    ),
                )
            )
        page.update()
    
    def add_waiter(e):
        def save_waiter(e):
            if name_field.value:
                db.add_waiter(name_field.value)
                refresh_waiters()
                page.dialog.open = False
                page.snack_bar = ft.SnackBar(ft.Text("Сервитьорът е добавен"), bgcolor=Colors.SUCCESS)
                page.snack_bar.open = True
                page.update()
        
        name_field = ft.TextField(label="Име на сервитьор", width=300)
        dialog = ft.AlertDialog(
            title=ft.Text("Добави сервитьор"),
            content=name_field,
            actions=[
                ft.TextButton("Запази", on_click=save_waiter),
                ft.TextButton("Отказ", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def delete_waiter(waiter_id):
        db.remove_waiter(waiter_id)
        refresh_waiters()
        page.snack_bar = ft.SnackBar(ft.Text("Сервитьорът е изтрит"), bgcolor=Colors.SUCCESS)
        page.snack_bar.open = True
        page.update()
    
    refresh_waiters()
    
    return ft.Column(
        [
            # Header with logout
            ft.Container(
                content=ft.Row([
                    ft.Text("Администраторски панел", size=24, weight=FontWeight.BOLD),
                    ft.IconButton(
                        icon=icons.LOGOUT,
                        tooltip="Излез",
                        on_click=logout,
                    ),
                ], alignment=MainAxisAlignment.SPACE_BETWEEN),
                padding=20,
                bgcolor=Colors.SURFACE_VARIANT,
            ),
            
            # Admin functions
            ft.Container(
                content=ft.Tabs(
                    selected_index=0,
                    tabs=[
                        ft.Tab(
                            text="Управление на сервитьори",
                            content=ft.Column([
                                ft.Container(
                                    content=ft.ElevatedButton(
                                        "Добави сервитьор",
                                        icon=icons.ADD,
                                        on_click=add_waiter
                                    ),
                                    padding=20,
                                ),
                                ft.Container(
                                    content=waiters_list,
                                    expand=True,
                                ),
                            ]),
                        ),
                        ft.Tab(
                            text="Отчети",
                            content=ft.Container(
                                content=ft.Text("Отчети ще бъдат добавени скоро", size=16),
                                padding=20,
                            ),
                        ),
                        ft.Tab(
                            text="Архивиране",
                            content=ft.Container(
                                content=ft.Column([
                                    ft.ElevatedButton("Архивирай базата", icon=icons.BACKUP),
                                    ft.ElevatedButton("Възстанови базата", icon=icons.RESTORE),
                                ], spacing=10),
                                padding=20,
                            ),
                        ),
                    ],
                ),
                expand=True,
                padding=20,
            ),
        ],
        expand=True,
    )

