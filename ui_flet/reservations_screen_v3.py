"""
Reservations screen for Flet UI - V3 with left sidebar layout and Date picker.

Features:
- Left sidebar (~20%) with filters and navigation
- Right content (~80%) with reservations list and action panel
- Single "Дата" calendar picker filter (replaces Month/Day)
- Internationalization support
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
from ui_flet.i18n import t, get_month_name


def create_reservations_screen(
    page: ft.Page,
    reservation_service: ReservationService,
    table_layout_service: TableLayoutService,
    db: DBManager,
    app_state,
    refresh_callback: Callable
):
    """Create the reservations screen with left sidebar and Action Panel integration."""
    
    # Reservations list container (expand=True for proper touch scrolling on mobile)
    reservations_list = ft.Column(spacing=Spacing.SM, scroll=ScrollMode.AUTO, expand=True)
    
    # Right content area (will compress when panel opens)
    right_content = ft.Container(expand=True)
    
    def get_waiter_name(waiter_id):
        """Get waiter name by ID."""
        if waiter_id is None:
            return ""
        waiters = db.get_waiters()
        for w in waiters:
            if w["id"] == waiter_id:
                return w["name"]
        return ""
    
    def get_date_display():
        """Get the current filter date for display (localized)."""
        d = app_state.filter_date
        month_name = get_month_name(d.month)
        return f"{d.day} {month_name} {d.year}"
    
    def refresh_reservations():
        """Refresh the reservations list based on current filters."""
        # Get filter parameters
        selected_date = app_state.get_selected_date()
        selected_dt = app_state.get_selected_datetime()
        
        # Update date display
        date_display_text.value = get_date_display()
        
        # Convert status filter
        status_filter = None
        if app_state.selected_status != "Всички" and app_state.selected_status != t("all"):
            if app_state.selected_status == "Резервирана" or app_state.selected_status == t("reserved"):
                status_filter = "Reserved"
            else:
                status_filter = "Cancelled"
        
        # Convert table filter
        table_filter = None
        if app_state.selected_table != "Всички" and app_state.selected_table != t("all"):
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
                    content=body_text(t("no_reservations"), color=Colors.TEXT_SECONDARY),
                    padding=Spacing.XL,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for res in reservations:
                # Status display
                status_display = t("reserved") if res["status"] == "Reserved" else t("cancelled")
                status_color = Colors.SUCCESS if res["status"] == "Reserved" else Colors.DANGER
                
                # Build reservation card (with correct closure for res_id)
                res_id = res["id"]
                res_copy = dict(res)  # Copy for closure
                
                # Get notes/additional_info for display
                notes_text = res.get("additional_info") or ""
                
                # Build the main row content
                # Uses compact fixed widths + expand on flexible columns so
                # edit/delete buttons are always visible even on scaled tablets.
                main_row_content = [
                    # Table number (compact)
                    ft.Container(
                        content=body_text(f"#{res['table_number']}", weight=FontWeight.BOLD),
                        width=44,
                    ),
                    # Time (fixed - datetime is always same length)
                    ft.Container(
                        content=ft.Column(
                            [
                                label(t("time"), color=Colors.TEXT_SECONDARY),
                                body_text(res["time_slot"], weight=FontWeight.MEDIUM),
                            ],
                            spacing=2,
                        ),
                        width=130,
                    ),
                    # Customer (expand - takes up remaining space)
                    ft.Container(
                        content=ft.Column(
                            [
                                label(t("customer"), color=Colors.TEXT_SECONDARY),
                                body_text(res["customer_name"], weight=FontWeight.MEDIUM),
                            ],
                            spacing=2,
                        ),
                        expand=2,
                    ),
                    # Phone (compact)
                    ft.Container(
                        content=ft.Column(
                            [
                                label(t("phone"), color=Colors.TEXT_SECONDARY),
                                body_text(res["phone_number"] or "-"),
                            ],
                            spacing=2,
                        ),
                        expand=2,
                        visible=not is_narrow_screen,
                    ),
                    # Waiter (hidden on narrow screens to save space)
                    ft.Container(
                        content=ft.Column(
                            [
                                label(t("waiter"), color=Colors.TEXT_SECONDARY),
                                body_text(get_waiter_name(res.get("waiter_id"))),
                            ],
                            spacing=2,
                        ),
                        expand=2,
                        visible=not is_narrow_screen,
                    ),
                    # Notes (hidden on narrow screens)
                    ft.Container(
                        content=ft.Column(
                            [
                                label(t("notes"), color=Colors.TEXT_SECONDARY),
                                body_text(
                                    notes_text if notes_text else "-",
                                    size=Typography.SIZE_SM,
                                    color=Colors.TEXT_PRIMARY if notes_text else Colors.TEXT_DISABLED,
                                ),
                            ],
                            spacing=2,
                        ),
                        expand=2,
                        visible=not is_narrow_screen,
                    ),
                    # Status badge (compact)
                    ft.Container(
                        content=ft.Container(
                            content=body_text(status_display, size=Typography.SIZE_SM),
                            bgcolor=status_color + "40",
                            border_radius=Radius.SM,
                            padding=ft.padding.symmetric(horizontal=6, vertical=4),
                        ),
                        width=90,
                    ),
                    # Actions - always visible, fixed width
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.IconButton(
                                    icon=icons.EDIT,
                                    icon_color=Colors.ACCENT_PRIMARY,
                                    icon_size=20,
                                    tooltip=t("edit"),
                                    on_click=lambda e, r=res_copy: action_panel.open_edit(r),
                                ),
                                ft.IconButton(
                                    icon=icons.DELETE,
                                    icon_color=Colors.DANGER,
                                    icon_size=20,
                                    tooltip=t("delete"),
                                    on_click=lambda e, r=res_copy: action_panel.open_delete(r),
                                ),
                            ],
                            spacing=0,
                            tight=True,
                        ),
                        width=80,
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
                message = t("reservation_updated")
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
                message = t("reservation_created")
            
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
                    ft.Text(t("error_overlap"), color=Colors.TEXT_PRIMARY),
                    bgcolor=Colors.DANGER
                )
                page.snack_bar.open = True
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"{t('error')}: {str(ex)}", color=Colors.TEXT_PRIMARY),
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
            ft.Text(t("reservation_cancelled"), color=Colors.TEXT_PRIMARY),
            bgcolor=Colors.SUCCESS
        )
        page.snack_bar.open = True
        page.update()
    
    def handle_panel_close():
        """Handle action panel close."""
        page.update()
    
    # Create action panel
    action_panel = ActionPanel(
        page=page,
        on_close=handle_panel_close,
        on_save=handle_save,
        on_delete=handle_delete,
        get_waiters=lambda: db.get_waiters(),
    )
    
    # ==========================================
    # Date Picker Setup
    # ==========================================
    
    def open_date_picker(e):
        """Open the date picker dialog."""
        current_date = app_state.filter_date
        
        def handle_date_change(e):
            if e.control.value:
                selected_date = e.control.value
                app_state.update_filter(filter_date=selected_date)
                refresh_reservations()
        
        def handle_dismiss(e):
            pass  # Do nothing on dismiss
        
        date_picker = ft.DatePicker(
            first_date=date(2020, 1, 1),
            last_date=date(2030, 12, 31),
            value=current_date,
            on_change=handle_date_change,
            on_dismiss=handle_dismiss,
        )
        
        page.overlay.append(date_picker)
        date_picker.open = True
        page.update()
    
    # Date display text (updated when filter changes)
    date_display_text = body_text(get_date_display(), weight=FontWeight.MEDIUM)
    
    # Date picker button
    date_picker_field = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=date_display_text,
                    expand=True,
                ),
                ft.Icon(icons.CALENDAR_TODAY, color=Colors.ACCENT_PRIMARY, size=20),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=Colors.SURFACE_GLASS,
        border=ft.border.all(1, Colors.BORDER),
        border_radius=Radius.SM,
        padding=ft.padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.SM),
        on_click=open_date_picker,
        ink=True,
    )
    
    # ==========================================
    # Filter Dropdowns
    # ==========================================
    
    hour_dropdown = ft.Dropdown(
        label=t("hour"),
        value=app_state.selected_hour,
        options=[ft.dropdown.Option(t("all"))] + [ft.dropdown.Option(f"{h:02d}") for h in range(24)],
        on_change=lambda e: app_state.update_filter(selected_hour=e.control.value) or refresh_reservations(),
        width=None,
        text_size=Typography.SIZE_XS,  # Smaller to prevent wrapping
        dense=True,
        bgcolor=Colors.SURFACE_GLASS,
        border_color=Colors.BORDER,
        color=Colors.INPUT_TEXT,
    )
    
    minute_dropdown = ft.Dropdown(
        label=t("minutes"),
        value=app_state.selected_minute,
        options=[ft.dropdown.Option(m) for m in ["00", "15", "30", "45"]],
        on_change=lambda e: app_state.update_filter(selected_minute=e.control.value) or refresh_reservations(),
        width=None,
        text_size=Typography.SIZE_XS,  # Smaller to prevent wrapping
        dense=True,
        bgcolor=Colors.SURFACE_GLASS,
        border_color=Colors.BORDER,
        color=Colors.INPUT_TEXT,
    )
    
    status_dropdown = ft.Dropdown(
        label=t("status"),
        value=app_state.selected_status,
        options=[
            ft.dropdown.Option(t("all")),
            ft.dropdown.Option(t("reserved")),
            ft.dropdown.Option(t("cancelled")),
        ],
        on_change=lambda e: app_state.update_filter(selected_status=e.control.value) or refresh_reservations(),
        width=None,
        text_size=Typography.SIZE_XS,  # Smaller to prevent wrapping
        dense=True,
        bgcolor=Colors.SURFACE_GLASS,
        border_color=Colors.BORDER,
        color=Colors.INPUT_TEXT,
    )
    
    table_dropdown = ft.Dropdown(
        label=t("table"),
        value=app_state.selected_table,
        options=[ft.dropdown.Option(t("all"))] + [ft.dropdown.Option(str(i)) for i in range(1, 51)],
        on_change=lambda e: app_state.update_filter(selected_table=e.control.value) or refresh_reservations(),
        width=None,
        text_size=Typography.SIZE_XS,  # Smaller to prevent wrapping
        dense=True,
        bgcolor=Colors.SURFACE_GLASS,
        border_color=Colors.BORDER,
        color=Colors.INPUT_TEXT,  # Use theme input text color
    )
    
    # ==========================================
    # Left Sidebar (Responsive)
    # ==========================================
    
    # Sidebar content (shared between normal sidebar and drawer)
    sidebar_content = ft.Column(
        [
            # Title
            heading(t("filters"), size=Typography.SIZE_LG, weight=FontWeight.BOLD),
            ft.Divider(height=1, color=Colors.BORDER),
            
            # Date picker
            ft.Container(
                content=ft.Column([
                    label(t("date"), color=Colors.TEXT_SECONDARY),
                    date_picker_field,
                ], spacing=4),
                padding=ft.padding.only(top=Spacing.SM),
            ),
            
            ft.Container(height=Spacing.SM),
            
            # Time filters (hour + minute)
            ft.Row([
                ft.Container(content=hour_dropdown, expand=True),
                ft.Container(content=minute_dropdown, expand=True),
            ], spacing=Spacing.XS),
            
            ft.Container(height=Spacing.SM),
            
            # Status and Table filters - stacked vertically
            status_dropdown,
            
            ft.Container(height=Spacing.XS),
            
            table_dropdown,
            
            ft.Container(expand=True),  # Spacer
            
            ft.Divider(height=1, color=Colors.BORDER),
            
            # Create reservation button
            glass_button(
                t("create_reservation"),
                icon=icons.ADD,
                on_click=lambda e: action_panel.open_create(app_state),
                variant="primary",
                width=None,
            ),
            
        ],
        spacing=Spacing.SM,
        expand=True,
    )
    
    # Determine if we're on a narrow screen (tablet/mobile)
    # Default to wide screen if window_width is not available (desktop usually starts wide)
    try:
        is_narrow_screen = page.window_width and page.window_width < 900
    except:
        is_narrow_screen = False
    
    # Create drawer for narrow screens (filters only, not action buttons)
    drawer_content_filters = ft.Column(
        [
            # Title
            heading(t("filters"), size=Typography.SIZE_LG, weight=FontWeight.BOLD),
            ft.Divider(height=1, color=Colors.BORDER),
            
            # Date picker
            ft.Container(
                content=ft.Column([
                    label(t("date"), color=Colors.TEXT_SECONDARY),
                    date_picker_field,
                ], spacing=4),
                padding=ft.padding.only(top=Spacing.SM),
            ),
            
            ft.Container(height=Spacing.SM),
            
            # Time filters (hour + minute)
            ft.Row([
                ft.Container(content=hour_dropdown, expand=True),
                ft.Container(content=minute_dropdown, expand=True),
            ], spacing=Spacing.XS),
            
            ft.Container(height=Spacing.SM),
            
            # Status and Table filters - stacked vertically
            status_dropdown,
            
            ft.Container(height=Spacing.XS),
            
            table_dropdown,
        ],
        spacing=Spacing.SM,
        scroll=ScrollMode.AUTO,
    )
    
    drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(
                content=glass_container(
                    content=drawer_content_filters,
                    padding=Spacing.LG,
                ),
                padding=Spacing.MD,
                height=page.window_height - 100 if hasattr(page, 'window_height') and page.window_height else 800,
            )
        ],
        bgcolor=Colors.SURFACE + "E6",  # Semi-transparent
    )
    
    def toggle_drawer(e):
        """Toggle the navigation drawer on narrow screens."""
        drawer.open = not drawer.open
        drawer.update()
    
    # Left sidebar (visible on wide screens only)
    left_sidebar = ft.Container(
        content=glass_container(
            content=sidebar_content,
            padding=Spacing.LG,
        ),
        width=240,
        padding=Spacing.MD,
        visible=not is_narrow_screen,
    )
    
    # Top action bar for narrow screens (always visible)
    narrow_top_bar = ft.Container(
        content=glass_container(
            content=ft.Row(
                [
                    # Filter button
                    ft.IconButton(
                        icon=icons.FILTER_LIST,
                        tooltip=t("filters"),
                        on_click=toggle_drawer,
                        icon_color=Colors.ACCENT_PRIMARY,
                    ),
                    
                    ft.Container(expand=True),  # Spacer
                    
                    # Create reservation button
                    glass_button(
                        t("create_reservation"),
                        icon=icons.ADD,
                        on_click=lambda e: action_panel.open_create(app_state),
                        variant="primary",
                        width=None,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=Spacing.MD,
        ),
        padding=ft.padding.only(left=Spacing.MD, right=Spacing.MD, top=Spacing.SM),
        visible=is_narrow_screen,
    )
    
    # ==========================================
    # Right Content Area
    # ==========================================
    
    # Build content column (with or without top bar for narrow screens)
    content_column_items = []
    
    # Add top action bar on narrow screens
    if is_narrow_screen:
        content_column_items.append(narrow_top_bar)
    
    # Add header
    content_column_items.append(
        ft.Container(
            content=heading(t("reservations"), size=Typography.SIZE_XL, weight=FontWeight.BOLD),
            padding=ft.padding.only(left=Spacing.LG, top=Spacing.MD, bottom=Spacing.SM),
        )
    )
    
    # Add reservations list
    content_column_items.append(
        ft.Container(
            content=reservations_list,
            padding=ft.padding.symmetric(horizontal=Spacing.LG),
            expand=True,
        )
    )
    
    right_content.content = ft.Column(
        content_column_items,
        spacing=0,
        expand=True,
    )
    
    # Initial data load
    refresh_reservations()
    
    # Add drawer to page for narrow screens
    if is_narrow_screen:
        page.drawer = drawer
    
    # Build main layout
    main_content = ft.Row(
        [
            left_sidebar,  # Visible on wide screens, hidden on narrow
            right_content,  # Contains top bar on narrow screens
            action_panel.container,
        ],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    # Floating circular button - always on top, bottom-right corner
    # Always visible on all screen sizes - floats above all content via Stack
    fab = ft.Container(
        content=ft.IconButton(
            icon=icons.TABLE_CHART,
            icon_color="#FFFFFF",
            icon_size=28,
            tooltip=t("to_layout"),
            on_click=lambda e: app_state.navigate_to("table_layout"),
            style=ft.ButtonStyle(
                bgcolor=Colors.ACCENT_PRIMARY,
                shape=ft.CircleBorder(),
                padding=ft.padding.all(12),
            ),
        ),
        right=16,
        bottom=16,
    )

    # Wrap in Stack so FAB floats above all content
    return ft.Stack(
        [
            main_content,
            fab,
        ],
        expand=True,
    )
