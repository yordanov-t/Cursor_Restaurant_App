"""
Reservations screen for Flet UI - V3 with Action Panel and gradient background.

Replaces popup dialogs with right-side animated action panel.
"""

import flet as ft
from datetime import datetime, date
from typing import Callable
from core import ReservationService, TableLayoutService
from db import DBManager
from ui_flet.theme import (Colors, Spacing, Radius, Typography, glass_container,
                             glass_button, heading, label, body_text)
from ui_flet.compat import icons, FontWeight, ScrollMode
from ui_flet.action_panel import ActionPanel


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
    """Create the reservations screen with Action Panel integration."""
    
    # Reservations list container
    reservations_list = ft.Column(spacing=Spacing.SM, scroll=ScrollMode.AUTO)
    
    # Main content area (will compress when panel opens)
    main_content = ft.Container(expand=True)
    
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
                
                # Build reservation card (with correct closure for res_id)
                res_id = res["id"]
                res_copy = dict(res)  # Copy for closure
                
                # Get notes/additional_info for display
                notes_text = res.get("additional_info") or ""
                
                # Build the main row content
                main_row_content = [
                    # Table number
                    ft.Container(
                        content=body_text(f"#{res['table_number']}", weight=FontWeight.BOLD),
                        width=60,
                    ),
                    # Time
                    ft.Container(
                        content=ft.Column(
                            [
                                label("Час", color=Colors.TEXT_SECONDARY),
                                body_text(res["time_slot"], weight=FontWeight.MEDIUM),
                            ],
                            spacing=2,
                        ),
                        width=150,
                    ),
                    # Customer
                    ft.Container(
                        content=ft.Column(
                            [
                                label("Клиент", color=Colors.TEXT_SECONDARY),
                                body_text(res["customer_name"], weight=FontWeight.MEDIUM),
                            ],
                            spacing=2,
                        ),
                        width=140,
                    ),
                    # Phone
                    ft.Container(
                        content=ft.Column(
                            [
                                label("Телефон", color=Colors.TEXT_SECONDARY),
                                body_text(res["phone_number"] or "-"),
                            ],
                            spacing=2,
                        ),
                        width=110,
                    ),
                    # Waiter
                    ft.Container(
                        content=ft.Column(
                            [
                                label("Сервитьор", color=Colors.TEXT_SECONDARY),
                                body_text(get_waiter_name(res.get("waiter_id"))),
                            ],
                            spacing=2,
                        ),
                        width=100,
                    ),
                    # Notes (Бележки) - show if exists
                    ft.Container(
                        content=ft.Column(
                            [
                                label("Бележки", color=Colors.TEXT_SECONDARY),
                                body_text(
                                    notes_text if notes_text else "-",
                                    size=Typography.SIZE_SM,
                                    color=Colors.TEXT_PRIMARY if notes_text else Colors.TEXT_DISABLED,
                                ),
                            ],
                            spacing=2,
                        ),
                        width=120,
                        visible=True,  # Always show the column for consistency
                    ),
                    # Status
                    ft.Container(
                        content=ft.Container(
                            content=body_text(status_display, size=Typography.SIZE_SM),
                            bgcolor=status_color + "40",
                            border_radius=Radius.SM,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        ),
                        width=110,
                    ),
                    # Actions
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=icons.EDIT,
                                icon_color=Colors.ACCENT_PRIMARY,
                                tooltip="Редактирай",
                                on_click=lambda e, r=res_copy: action_panel.open_edit(r),
                            ),
                            ft.IconButton(
                                icon=icons.DELETE,
                                icon_color=Colors.DANGER,
                                tooltip="Изтрий",
                                on_click=lambda e, r=res_copy: action_panel.open_delete(r),
                            ),
                        ],
                        spacing=0,
                    ),
                ]
                
                card = glass_container(
                    content=ft.Row(
                        main_row_content,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=Spacing.MD,
                )
                
                reservations_list.controls.append(card)
        
        page.update()
    
    def handle_save(data: dict):
        """Handle save from action panel (create or edit)."""
        try:
            if "id" in data:
                # Edit existing - preserve status as "Reserved"
                success = reservation_service.update_reservation(
                    reservation_id=data["id"],
                    table_number=data["table_number"],
                    time_slot=data["time_slot"],
                    customer_name=data["customer_name"],
                    phone_number=data["phone"],
                    additional_info=data["notes"],
                    waiter_id=data["waiter_id"],
                    status="Reserved"
                )
                message = "Резервацията е обновена"
            else:
                # Create new
                success = reservation_service.create_reservation(
                    table_number=data["table_number"],
                    time_slot=data["time_slot"],
                    customer_name=data["customer_name"],
                    phone_number=data["phone"],
                    additional_info=data["notes"],
                    waiter_id=data["waiter_id"]
                )
                message = "Резервацията е създадена"
            
            if success:
                refresh_reservations()
                refresh_callback()  # Refresh table layout too
                page.snack_bar = ft.SnackBar(
                    ft.Text(message, color=Colors.TEXT_PRIMARY),
                    bgcolor=Colors.SUCCESS
                )
                page.snack_bar.open = True
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Грешка: Препокриване с друга резервация", color=Colors.TEXT_PRIMARY),
                    bgcolor=Colors.DANGER
                )
                page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Грешка: {str(ex)}", color=Colors.TEXT_PRIMARY),
                bgcolor=Colors.DANGER
            )
            page.snack_bar.open = True
            page.update()
    
    def handle_delete(res_id: int):
        """Handle delete from action panel."""
        reservation_service.cancel_reservation(res_id)
        refresh_reservations()
        refresh_callback()
        page.snack_bar = ft.SnackBar(
            ft.Text("Резервацията е отменена", color=Colors.TEXT_PRIMARY),
            bgcolor=Colors.SUCCESS
        )
        page.snack_bar.open = True
        page.update()
    
    def handle_panel_close():
        """Handle action panel close."""
        # Expand main content back to full width
        main_content.expand = True
        page.update()
    
    # Create action panel
    action_panel = ActionPanel(
        page=page,
        on_close=handle_panel_close,
        on_save=handle_save,
        on_delete=handle_delete,
        get_waiters=lambda: db.get_waiters(),
    )
    
    # Filter dropdowns - compact widths for single-row layout
    month_dropdown = ft.Dropdown(
        label="Месец",
        value=app_state.selected_month,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(m) for m in BULGARIAN_MONTHS],
        on_change=lambda e: app_state.update_filter(selected_month=e.control.value) or refresh_reservations(),
        width=130,
        text_size=Typography.SIZE_SM,
        dense=True,
    )
    
    day_dropdown = ft.Dropdown(
        label="Ден",
        value=app_state.selected_day,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(str(d)) for d in range(1, 32)],
        on_change=lambda e: app_state.update_filter(selected_day=e.control.value) or refresh_reservations(),
        width=85,
        text_size=Typography.SIZE_SM,
        dense=True,
    )
    
    hour_dropdown = ft.Dropdown(
        label="Час",
        value=app_state.selected_hour,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(f"{h:02d}") for h in range(24)],
        on_change=lambda e: app_state.update_filter(selected_hour=e.control.value) or refresh_reservations(),
        width=85,
        text_size=Typography.SIZE_SM,
        dense=True,
    )
    
    minute_dropdown = ft.Dropdown(
        label="Минути",
        value=app_state.selected_minute,
        options=[ft.dropdown.Option(m) for m in ["00", "15", "30", "45"]],  # No "Всички"
        on_change=lambda e: app_state.update_filter(selected_minute=e.control.value) or refresh_reservations(),
        width=90,
        text_size=Typography.SIZE_SM,
        dense=True,
    )
    
    status_dropdown = ft.Dropdown(
        label="Статус",
        value=app_state.selected_status,
        options=[
            ft.dropdown.Option("Всички"),
            ft.dropdown.Option("Резервирана"),
            ft.dropdown.Option("Отменена"),
        ],
        on_change=lambda e: app_state.update_filter(selected_status=e.control.value) or refresh_reservations(),
        width=130,
        text_size=Typography.SIZE_SM,
        dense=True,
    )
    
    table_dropdown = ft.Dropdown(
        label="Маса",
        value=app_state.selected_table,
        options=[ft.dropdown.Option("Всички")] + [ft.dropdown.Option(str(i)) for i in range(1, 51)],
        on_change=lambda e: app_state.update_filter(selected_table=e.control.value) or refresh_reservations(),
        width=95,
        text_size=Typography.SIZE_SM,
        dense=True,
    )
    
    # Filter bar - single row with horizontal scroll
    filter_bar = glass_container(
        content=ft.Row(
            [
                month_dropdown,
                day_dropdown,
                hour_dropdown,
                minute_dropdown,
                status_dropdown,
                table_dropdown,
            ],
            spacing=Spacing.SM,
            scroll=ScrollMode.AUTO,  # Enable horizontal scrolling if needed
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=Spacing.MD,
    )
    
    # Action buttons
    action_buttons = ft.Row(
        [
            glass_button(
                text="Създай резервация",
                icon=icons.ADD,
                on_click=lambda e: action_panel.open_create(app_state),
                variant="primary",
            ),
            glass_button(
                text="Разпределение на масите",
                icon=icons.TABLE_CHART,
                on_click=lambda e: app_state.navigate_to("table_layout"),
                variant="secondary",
            ),
        ],
        spacing=Spacing.MD,
    )
    
    # Build main content
    main_content.content = ft.Column(
        [
            # Header
            ft.Container(
                content=heading("Резервации", size=Typography.SIZE_XL, weight=FontWeight.BOLD),
                padding=ft.padding.only(left=Spacing.LG, top=Spacing.MD, bottom=Spacing.SM),
            ),
            # Filters
            ft.Container(
                content=filter_bar,
                padding=ft.padding.symmetric(horizontal=Spacing.LG),
            ),
            # Actions
            ft.Container(
                content=action_buttons,
                padding=ft.padding.symmetric(horizontal=Spacing.LG, vertical=Spacing.MD),
            ),
            # Reservations list
            ft.Container(
                content=reservations_list,
                padding=ft.padding.symmetric(horizontal=Spacing.LG),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
    
    # Initial data load
    refresh_reservations()
    
    # Return layout with action panel
    return ft.Row(
        [
            main_content,
            action_panel.container,
        ],
        spacing=0,
        expand=True,
    )

