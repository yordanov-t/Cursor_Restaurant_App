"""
Reservations screen for Flet UI.

Displays filterable list of reservations with add/edit/delete functionality.
"""

import flet as ft
from datetime import date
from typing import Callable
from core import ReservationService
from db import DBManager
from ui_flet.compat import Colors, icons, FontWeight, ScrollMode


# Bulgarian constants
BULGARIAN_MONTHS = [
    "Януари", "Февруари", "Март", "Април", "Май", "Юни",
    "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"
]

BULGARIAN_MONTH_TO_NUM = {
    "Януари": 1, "Февруари": 2, "Март": 3, "Април": 4,
    "Май": 5, "Юни": 6, "Юли": 7, "Август": 8,
    "Септември": 9, "Октомври": 10, "Ноември": 11, "Декември": 12
}


def create_reservations_screen(
    page: ft.Page,
    reservation_service: ReservationService,
    db: DBManager,
    filter_context,
    on_navigate_to_layout: Callable
):
    """Create the reservations screen."""
    
    # Data table for reservations
    reservations_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Маса", weight=FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Час", weight=FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Клиент", weight=FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Телефон", weight=FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Сервитьор", weight=FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Статус", weight=FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Действия", weight=FontWeight.BOLD)),
        ],
        rows=[],
    )
    
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
        """Refresh the reservations table."""
        # Get filter parameters
        selected_dt = filter_context.get_selected_datetime()
        
        # Convert status filter
        status_filter = None
        if filter_context.selected_status != "Всички":
            status_filter = "Reserved" if filter_context.selected_status == "Резервирана" else "Cancelled"
        
        # Convert table filter
        table_filter = None
        if filter_context.selected_table != "Всички":
            table_filter = int(filter_context.selected_table)
        
        # Get filtered reservations
        reservations = reservation_service.list_reservations_for_context(
            selected_time=selected_dt,
            status_filter=status_filter,
            table_filter=table_filter
        )
        
        # Build table rows
        rows = []
        for res in reservations:
            # Status display
            status_display = "Резервирана" if res["status"] == "Reserved" else "Отменена"
            status_color = Colors.GREEN if res["status"] == "Reserved" else Colors.RED
            
            # Action buttons
            def make_edit_handler(res_id):
                return lambda e: open_edit_dialog(res_id)
            
            def make_delete_handler(res_id):
                return lambda e: delete_reservation(res_id)
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(res["table_number"]))),
                        ft.DataCell(ft.Text(res["time_slot"])),
                        ft.DataCell(ft.Text(res["customer_name"])),
                        ft.DataCell(ft.Text(res["phone_number"] or "")),
                        ft.DataCell(ft.Text(get_waiter_name(res["waiter_id"]))),
                        ft.DataCell(ft.Text(status_display, color=status_color)),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=icons.EDIT,
                                    tooltip="Промени",
                                    on_click=make_edit_handler(res["id"])
                                ),
                                ft.IconButton(
                                    icon=icons.DELETE,
                                    tooltip="Изтрий",
                                    on_click=make_delete_handler(res["id"])
                                ),
                            ], spacing=5)
                        ),
                    ]
                )
            )
        
        reservations_table.rows = rows
        page.update()
    
    def delete_reservation(res_id):
        """Delete a reservation."""
        def confirm_delete(e):
            if e.control.text == "Да":
                reservation_service.cancel_reservation(res_id)
                refresh_reservations()
                page.dialog.open = False
                page.snack_bar = ft.SnackBar(ft.Text("Резервацията е отменена"), bgcolor=Colors.SUCCESS)
                page.snack_bar.open = True
            else:
                page.dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Потвърждение"),
            content=ft.Text("Наистина ли искате да отмените тази резервация?"),
            actions=[
                ft.TextButton("Да", on_click=confirm_delete),
                ft.TextButton("Не", on_click=confirm_delete),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def open_add_dialog(e=None):
        """Open dialog to add new reservation."""
        # Will be implemented with full form
        page.snack_bar = ft.SnackBar(ft.Text("Функцията 'Създай резервация' ще бъде добавена скоро"))
        page.snack_bar.open = True
        page.update()
    
    def open_edit_dialog(res_id):
        """Open dialog to edit reservation."""
        # Will be implemented with full form
        page.snack_bar = ft.SnackBar(ft.Text("Функцията 'Промени резервация' ще бъде добавена скоро"))
        page.snack_bar.open = True
        page.update()
    
    # Filter controls
    month_dropdown = ft.Dropdown(
        label="Месец",
        value=filter_context.selected_month,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(m) for m in BULGARIAN_MONTHS],
        on_change=lambda e: setattr(filter_context, 'selected_month', e.control.value) or refresh_reservations(),
        width=150
    )
    
    day_dropdown = ft.Dropdown(
        label="Ден",
        value=filter_context.selected_day,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(str(d)) for d in range(1, 32)],
        on_change=lambda e: setattr(filter_context, 'selected_day', e.control.value) or refresh_reservations(),
        width=100
    )
    
    hour_dropdown = ft.Dropdown(
        label="Час",
        value=filter_context.selected_hour,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(f"{h:02d}") for h in range(24)],
        on_change=lambda e: setattr(filter_context, 'selected_hour', e.control.value) or refresh_reservations(),
        width=100
    )
    
    minute_dropdown = ft.Dropdown(
        label="Минути",
        value=filter_context.selected_minute,
        options=[ft.dropdown.Option(m) for m in ["Всички", "00", "15", "30", "45"]],
        on_change=lambda e: setattr(filter_context, 'selected_minute', e.control.value) or refresh_reservations(),
        width=100
    )
    
    status_dropdown = ft.Dropdown(
        label="Статус",
        value=filter_context.selected_status,
        options=[ft.dropdown.Option(s) for s in ["Резервирана", "Отменена", "Всички"]],
        on_change=lambda e: setattr(filter_context, 'selected_status', e.control.value) or refresh_reservations(),
        width=150
    )
    
    table_dropdown = ft.Dropdown(
        label="Маса",
        value=filter_context.selected_table,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(str(i)) for i in range(1, 51)],
        on_change=lambda e: setattr(filter_context, 'selected_table', e.control.value) or refresh_reservations(),
        width=100
    )
    
    # Initial load
    refresh_reservations()
    
    # Build screen
    return ft.Column(
        [
            # Header
            ft.Container(
                content=ft.Text("Резервации", size=24, weight=FontWeight.BOLD),
                padding=20,
                bgcolor=Colors.SURFACE_VARIANT,
            ),
            
            # Filters
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        month_dropdown,
                        day_dropdown,
                        hour_dropdown,
                        minute_dropdown,
                    ], spacing=10),
                    ft.Row([
                        status_dropdown,
                        table_dropdown,
                    ], spacing=10),
                ]),
                padding=20,
            ),
            
            # Action buttons
            ft.Container(
                content=ft.Row([
                    ft.ElevatedButton(
                        "Създай резервация",
                        icon=icons.ADD,
                        on_click=open_add_dialog
                    ),
                    ft.OutlinedButton(
                        "Разпределение на масите",
                        icon=icons.GRID_VIEW,
                        on_click=on_navigate_to_layout
                    ),
                ], spacing=10),
                padding=ft.padding.only(left=20, right=20, bottom=10),
            ),
            
            # Reservations table
            ft.Container(
                content=ft.Column([
                    reservations_table,
                ], scroll=ScrollMode.AUTO),
                expand=True,
                padding=20,
            ),
        ],
        expand=True,
    )

