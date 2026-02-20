"""
Reservations screen for Flet UI - V2 with full functionality and glassmorphism.
"""

import flet as ft
from datetime import datetime, date
from typing import Callable
from core import ReservationService, TableLayoutService
from db import DBManager
from ui_flet.theme import (Colors, Spacing, Radius, Typography, glass_container,
                             glass_button, heading, label, body_text)
from ui_flet.compat import icons, FontWeight, ScrollMode


# Bulgarian constants
BULGARIAN_MONTHS = [
    "Януари", "Февруари", "Март", "Април", "Май", "Юни",
    "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"
]


def create_reservations_screen(
    page: ft.Page,
    reservation_service: ReservationService,
    table_layout_service: TableLayoutService,
    db: DBManager,
    app_state,
    refresh_callback: Callable
):
    """Create the reservations screen with full functionality."""
    
    # Reservations list container
    reservations_list = ft.Column(spacing=Spacing.SM, scroll=ScrollMode.AUTO)
    
    def get_waiter_name(waiter_id):
        """Get waiter name by ID."""
        if waiter_id is None:
            return ""
        waiters = db.get_waiters()
        for w in waiters:
            if w["id"] == waiter_id:
                return w["name"]
        return ""
    
    def refresh_reservations():
        """Refresh the reservations list based on current filters."""
        # Get filter parameters
        selected_date = app_state.get_selected_date()
        selected_dt = app_state.get_selected_datetime()
        
        # Convert status filter
        status_filter = None
        if app_state.selected_status != "Всички":
            status_filter = "Reserved" if app_state.selected_status == "Резервирана" else "Cancelled"
        
        # Convert table filter
        table_filter = None
        if app_state.selected_table != "Всички":
            try:
                table_filter = int(app_state.selected_table)
            except:
                pass
        
        # Get filtered reservations with date constraint
        reservations = reservation_service.list_reservations_for_context(
            selected_date=selected_date,
            selected_time=selected_dt,
            status_filter=status_filter,
            table_filter=table_filter
        )
        
        # Store in app state
        app_state.reservations = reservations
        
        # Build list items
        reservations_list.controls.clear()
        
        if not reservations:
            reservations_list.controls.append(
                ft.Container(
                    content=body_text("Няма резервации за избраните филтри", color=Colors.TEXT_SECONDARY),
                    padding=Spacing.XL,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for res in reservations:
                # Status display
                status_display = "Резервирана" if res["status"] == "Reserved" else "Отменена"
                status_color = Colors.SUCCESS if res["status"] == "Reserved" else Colors.DANGER
                
                # Build reservation card
                card = glass_container(
                    content=ft.Row(
                        [
                            # Table number
                            ft.Container(
                                content=body_text(f"#{res['table_number']}", weight=FontWeight.BOLD),
                                width=60,
                            ),
                            # Time
                            ft.Container(
                                content=ft.Column(
                                    [
                                        label("Час"),
                                        body_text(res["time_slot"]),
                                    ],
                                    spacing=2,
                                ),
                                width=150,
                            ),
                            # Customer
                            ft.Container(
                                content=ft.Column(
                                    [
                                        label("Клиент"),
                                        body_text(res["customer_name"]),
                                    ],
                                    spacing=2,
                                ),
                                expand=True,
                            ),
                            # Phone
                            ft.Container(
                                content=ft.Column(
                                    [
                                        label("Телефон"),
                                        body_text(res["phone_number"] or "-"),
                                    ],
                                    spacing=2,
                                ),
                                width=130,
                            ),
                            # Waiter
                            ft.Container(
                                content=ft.Column(
                                    [
                                        label("Сервитьор"),
                                        body_text(get_waiter_name(res["waiter_id"])),
                                    ],
                                    spacing=2,
                                ),
                                width=120,
                            ),
                            # Status
                            ft.Container(
                                content=ft.Container(
                                    content=body_text(status_display, size=Typography.SIZE_SM),
                                    bgcolor=status_color + "33",
                                    border=ft.border.all(1, status_color),
                                    border_radius=Radius.SM,
                                    padding=ft.padding.symmetric(horizontal=Spacing.SM, vertical=4),
                                ),
                                width=120,
                            ),
                            # Actions
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=icons.EDIT,
                                        tooltip="Промени",
                                        icon_color=Colors.ACCENT_PRIMARY,
                                        on_click=lambda e, r=res: open_edit_dialog(r)
                                    ),
                                    ft.IconButton(
                                        icon=icons.DELETE,
                                        tooltip="Изтрий",
                                        icon_color=Colors.DANGER,
                                        on_click=lambda e, r=res: delete_reservation(r["id"])
                                    ),
                                ],
                                spacing=0,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=Spacing.MD,
                )
                
                reservations_list.controls.append(card)
        
        page.update()
    
    def delete_reservation(res_id):
        """Delete a reservation with confirmation."""
        def confirm_delete(e):
            if e.control.text == "Да":
                reservation_service.cancel_reservation(res_id)
                refresh_reservations()
                refresh_callback()  # Refresh table layout too
                page.snack_bar = ft.SnackBar(
                    ft.Text("Резервацията е отменена"),
                    bgcolor=Colors.SUCCESS
                )
                page.snack_bar.open = True
            page.dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=heading("Потвърждение", size=Typography.SIZE_LG),
            content=body_text("Наистина ли искате да отмените тази резервация?"),
            actions=[
                ft.TextButton("Да", on_click=confirm_delete),
                ft.TextButton("Не", on_click=confirm_delete),
            ],
            bgcolor=Colors.SURFACE,
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def open_add_dialog(e=None):
        """Open dialog to add new reservation."""
        # Get waiters
        waiters = db.get_waiters()
        waiter_options = [ft.dropdown.Option(str(w["id"]), w["name"]) for w in waiters]
        
        # Form fields
        table_field = ft.Dropdown(
            label="Маса",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 51)],
            value="1",
        )
        date_field = ft.TextField(
            label="Дата (YYYY-MM-DD)",
            value=datetime.now().strftime("%Y-%m-%d"),
        )
        time_field = ft.TextField(
            label="Час (HH:MM)",
            value="19:00",
        )
        name_field = ft.TextField(label="Име на клиент")
        phone_field = ft.TextField(label="Телефон")
        notes_field = ft.TextField(label="Допълнителна информация", multiline=True)
        waiter_field = ft.Dropdown(
            label="Сервитьор",
            options=waiter_options,
            value=waiter_options[0].key if waiter_options else None,
        )
        
        def save_reservation(e):
            try:
                # Combine date + time
                time_slot = f"{date_field.value} {time_field.value}"
                
                success = reservation_service.create_reservation(
                    table_number=int(table_field.value),
                    time_slot=time_slot,
                    customer_name=name_field.value,
                    phone_number=phone_field.value,
                    additional_info=notes_field.value,
                    waiter_id=int(waiter_field.value) if waiter_field.value else None
                )
                
                if success:
                    refresh_reservations()
                    refresh_callback()
                    page.dialog.open = False
                    page.snack_bar = ft.SnackBar(ft.Text("Резервацията е създадена"), bgcolor=Colors.SUCCESS)
                    page.snack_bar.open = True
                else:
                    page.snack_bar = ft.SnackBar(
                        ft.Text("Грешка: Препокриване с друга резервация"),
                        bgcolor=Colors.DANGER
                    )
                    page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Грешка: {str(ex)}"), bgcolor=Colors.DANGER)
                page.snack_bar.open = True
                page.update()
        
        dialog = ft.AlertDialog(
            title=heading("Създай резервация", size=Typography.SIZE_LG),
            content=ft.Container(
                content=ft.Column(
                    [
                        table_field,
                        date_field,
                        time_field,
                        name_field,
                        phone_field,
                        notes_field,
                        waiter_field,
                    ],
                    spacing=Spacing.MD,
                    scroll=ScrollMode.AUTO,
                ),
                width=500,
                height=400,
            ),
            actions=[
                ft.TextButton("Запази", on_click=save_reservation),
                ft.TextButton("Отказ", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
            ],
            bgcolor=Colors.SURFACE,
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def open_edit_dialog(res):
        """Open dialog to edit reservation."""
        # Get waiters
        waiters = db.get_waiters()
        waiter_options = [ft.dropdown.Option(str(w["id"]), w["name"]) for w in waiters]
        
        # Parse existing time slot
        try:
            dt = datetime.strptime(res["time_slot"], "%Y-%m-%d %H:%M")
            date_val = dt.strftime("%Y-%m-%d")
            time_val = dt.strftime("%H:%M")
        except:
            date_val = datetime.now().strftime("%Y-%m-%d")
            time_val = "19:00"
        
        # Form fields (pre-filled)
        table_field = ft.Dropdown(
            label="Маса",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 51)],
            value=str(res["table_number"]),
        )
        date_field = ft.TextField(label="Дата (YYYY-MM-DD)", value=date_val)
        time_field = ft.TextField(label="Час (HH:MM)", value=time_val)
        name_field = ft.TextField(label="Име на клиент", value=res["customer_name"])
        phone_field = ft.TextField(label="Телефон", value=res["phone_number"] or "")
        notes_field = ft.TextField(label="Допълнителна информация", value=res["additional_info"] or "", multiline=True)
        waiter_field = ft.Dropdown(
            label="Сервитьор",
            options=waiter_options,
            value=str(res["waiter_id"]) if res["waiter_id"] else (waiter_options[0].key if waiter_options else None),
        )
        status_field = ft.Dropdown(
            label="Статус",
            options=[
                ft.dropdown.Option("Reserved", "Резервирана"),
                ft.dropdown.Option("Cancelled", "Отменена"),
            ],
            value=res["status"],
        )
        
        def save_changes(e):
            try:
                # Combine date + time
                time_slot = f"{date_field.value} {time_field.value}"
                
                success = reservation_service.update_reservation(
                    reservation_id=res["id"],
                    table_number=int(table_field.value),
                    time_slot=time_slot,
                    customer_name=name_field.value,
                    phone_number=phone_field.value,
                    additional_info=notes_field.value,
                    waiter_id=int(waiter_field.value) if waiter_field.value else None,
                    status=status_field.value
                )
                
                if success:
                    refresh_reservations()
                    refresh_callback()
                    page.dialog.open = False
                    page.snack_bar = ft.SnackBar(ft.Text("Резервацията е променена"), bgcolor=Colors.SUCCESS)
                    page.snack_bar.open = True
                else:
                    page.snack_bar = ft.SnackBar(
                        ft.Text("Грешка: Препокриване с друга резервация"),
                        bgcolor=Colors.DANGER
                    )
                    page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Грешка: {str(ex)}"), bgcolor=Colors.DANGER)
                page.snack_bar.open = True
                page.update()
        
        dialog = ft.AlertDialog(
            title=heading(f"Промени резервация #{res['id']}", size=Typography.SIZE_LG),
            content=ft.Container(
                content=ft.Column(
                    [
                        table_field,
                        date_field,
                        time_field,
                        name_field,
                        phone_field,
                        notes_field,
                        waiter_field,
                        status_field,
                    ],
                    spacing=Spacing.MD,
                    scroll=ScrollMode.AUTO,
                ),
                width=500,
                height=450,
            ),
            actions=[
                ft.TextButton("Запази", on_click=save_changes),
                ft.TextButton("Отказ", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
            ],
            bgcolor=Colors.SURFACE,
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    # Filter controls
    month_dropdown = ft.Dropdown(
        label="Месец",
        value=app_state.selected_month,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(m) for m in BULGARIAN_MONTHS],
        on_change=lambda e: app_state.update_filter(selected_month=e.control.value) or refresh_reservations(),
        width=150,
        text_size=Typography.SIZE_SM,
    )
    
    day_dropdown = ft.Dropdown(
        label="Ден",
        value=app_state.selected_day,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(str(d)) for d in range(1, 32)],
        on_change=lambda e: app_state.update_filter(selected_day=e.control.value) or refresh_reservations(),
        width=100,
        text_size=Typography.SIZE_SM,
    )
    
    hour_dropdown = ft.Dropdown(
        label="Час",
        value=app_state.selected_hour,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(f"{h:02d}") for h in range(24)],
        on_change=lambda e: app_state.update_filter(selected_hour=e.control.value) or refresh_reservations(),
        width=100,
        text_size=Typography.SIZE_SM,
    )
    
    minute_dropdown = ft.Dropdown(
        label="Минути",
        value=app_state.selected_minute,
        options=[ft.dropdown.Option(m) for m in ["00", "15", "30", "45"]],  # No "Всички"
        on_change=lambda e: app_state.update_filter(selected_minute=e.control.value) or refresh_reservations(),
        width=100,
        text_size=Typography.SIZE_SM,
    )
    
    status_dropdown = ft.Dropdown(
        label="Статус",
        value=app_state.selected_status,
        options=[ft.dropdown.Option(s) for s in ["Резервирана", "Отменена", "Всички"]],
        on_change=lambda e: app_state.update_filter(selected_status=e.control.value) or refresh_reservations(),
        width=150,
        text_size=Typography.SIZE_SM,
    )
    
    table_dropdown = ft.Dropdown(
        label="Маса",
        value=app_state.selected_table,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(str(i)) for i in range(1, 51)],
        on_change=lambda e: app_state.update_filter(selected_table=e.control.value) or refresh_reservations(),
        width=100,
        text_size=Typography.SIZE_SM,
    )
    
    # Initial load
    refresh_reservations()
    
    # Build screen
    return ft.Container(
        content=ft.Column(
            [
                # Header
                ft.Container(
                    content=heading("Резервации"),
                    padding=Spacing.XL,
                ),
                
                # Filters in glass container
                ft.Container(
                    content=glass_container(
                        content=ft.Column([
                            ft.Row([
                                month_dropdown,
                                day_dropdown,
                                hour_dropdown,
                                minute_dropdown,
                            ], spacing=Spacing.MD, wrap=True),
                            ft.Row([
                                status_dropdown,
                                table_dropdown,
                            ], spacing=Spacing.MD),
                        ], spacing=Spacing.MD),
                        padding=Spacing.LG,
                    ),
                    padding=ft.padding.symmetric(horizontal=Spacing.XL),
                ),
                
                # Action buttons
                ft.Container(
                    content=ft.Row([
                        glass_button(
                            "Създай резервация",
                            icon=icons.ADD,
                            on_click=open_add_dialog,
                            variant="primary",
                        ),
                        glass_button(
                            "Разпределение на масите",
                            icon=icons.GRID_VIEW,
                            on_click=lambda e: app_state.navigate_to("table_layout"),
                            variant="secondary",
                        ),
                    ], spacing=Spacing.MD),
                    padding=ft.padding.symmetric(horizontal=Spacing.XL, vertical=Spacing.LG),
                ),
                
                # Reservations list
                ft.Container(
                    content=reservations_list,
                    padding=ft.padding.symmetric(horizontal=Spacing.XL),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        ),
        expand=True,
    )

