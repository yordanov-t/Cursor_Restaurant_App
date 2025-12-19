"""
Table layout screen for Flet UI - V2 with left sidebar and sections feature.

Features:
- Left sidebar (~20%) with controls, legend, and section selector
- Right side (~80%) with section-grouped table visualization
- Section dropdown to filter view
- Click on occupied/soon tables shows reservation details
- Internationalization support
"""

import flet as ft
from typing import Callable, Dict, List, Optional, Tuple
from core import TableLayoutService, TableState
from db import DBManager
from ui_flet.theme import (Colors, Spacing, Radius, Typography, heading, label, body_text,
                             glass_container, glass_button)
from ui_flet.compat import icons, FontWeight, ScrollMode
from ui_flet.i18n import t
from ui_flet.action_panel import ActionPanel


def create_table_layout_screen(
    page: ft.Page,
    table_layout_service: TableLayoutService,
    app_state,
    refresh_callback: Callable
):
    """Create the table layout screen with left sidebar and sections."""
    
    # Get db reference from the service
    db = table_layout_service.db
    
    # Store table containers for updates
    table_containers: Dict[int, ft.Container] = {}
    
    # Store table states for click handling (table_num -> (state, reservation_info))
    current_table_states: Dict[int, Tuple[TableState, Optional[dict]]] = {}
    
    # Currently selected table (for highlight)
    selected_table: Dict[str, Optional[int]] = {"num": None}
    
    # Section containers for the right side
    sections_column = ft.Column(spacing=Spacing.LG, scroll=ScrollMode.AUTO, expand=True)
    
    # Current section filter
    current_section_filter = {"value": t("all")}
    
    # ==========================================
    # Table Color Helper (with selection support)
    # ==========================================
    
    def get_table_color(state: TableState, is_selected: bool = False) -> str:
        """Get the appropriate table color based on state and selection."""
        if state == TableState.OCCUPIED:
            return Colors.TABLE_OCCUPIED_SELECTED if is_selected else Colors.TABLE_OCCUPIED
        elif state == TableState.SOON_30:
            return Colors.TABLE_SOON_SELECTED if is_selected else Colors.TABLE_SOON
        else:  # FREE
            return Colors.TABLE_FREE_SELECTED if is_selected else Colors.TABLE_FREE
    
    def update_table_selection(new_selected: Optional[int]):
        """Update the visual selection state for tables."""
        old_selected = selected_table["num"]
        selected_table["num"] = new_selected
        
        # Update old selection (if any) to remove highlight
        if old_selected is not None and old_selected in table_containers:
            if old_selected in current_table_states:
                state, _ = current_table_states[old_selected]
                button = table_containers[old_selected].content.controls[0]
                button.bgcolor = get_table_color(state, is_selected=False)
                # Remove selection border
                button.border = None
        
        # Update new selection (if any) to add highlight
        if new_selected is not None and new_selected in table_containers:
            if new_selected in current_table_states:
                state, _ = current_table_states[new_selected]
                button = table_containers[new_selected].content.controls[0]
                button.bgcolor = get_table_color(state, is_selected=True)
                # Add selection border
                button.border = ft.border.all(2, Colors.BORDER_SELECTED)
        
        page.update()
    
    # ==========================================
    # Action Panel for viewing reservation details
    # ==========================================
    
    def handle_panel_close():
        """Handle panel close - clear selection."""
        update_table_selection(None)
    
    def handle_save(data):
        """Not used - view-only panel."""
        pass
    
    def handle_delete(res_id):
        """Not used - view-only panel."""
        pass
    
    action_panel = ActionPanel(
        page=page,
        on_close=handle_panel_close,
        on_save=handle_save,
        on_delete=handle_delete,
        get_waiters=lambda: db.get_waiters(),
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
    
    def on_table_click(table_num: int):
        """Handle click on a table button."""
        # Check if this table has reservation data
        if table_num not in current_table_states:
            return
        
        state, res_data = current_table_states[table_num]
        
        # Only show details for occupied or soon tables
        if state in (TableState.OCCUPIED, TableState.SOON_30) and res_data:
            # Update selection highlight
            update_table_selection(table_num)
            
            # Open details panel
            waiter_name = get_waiter_name(res_data.get("waiter_id"))
            action_panel.open_view(res_data, waiter_name)
    
    def get_filter_text():
        """Get filter context display text."""
        month = app_state.selected_month
        day = app_state.selected_day
        hour = app_state.selected_hour
        minute = app_state.selected_minute
        
        text_parts = []
        if month != "Всички" or day != "Всички":
            if month == "Всички":
                text_parts.append(f"{t('date')}: {day}")
            elif day == "Всички":
                text_parts.append(f"{month}")
            else:
                text_parts.append(f"{day} {month}")
        else:
            text_parts.append(t("all_days"))
        
        if hour != "Всички" and minute != "Всички":
            text_parts.append(f"{hour}:{minute}")
        elif hour != "Всички":
            text_parts.append(f"{t('hour')} {hour}")
        
        return " ".join(text_parts)
    
    filter_label = body_text(
        f"{get_filter_text()}",
        size=Typography.SIZE_SM,
    )
    
    def build_table_button(table_num: int) -> ft.Container:
        """Build a single table button with shape from DB and click handler."""
        # Get table shape from database
        shape = db.get_table_shape(table_num)
        
        # Determine dimensions and border radius based on shape
        if shape == "ROUND":
            width = 50
            height = 50
            border_radius = 25  # Full circle
        elif shape == "SQUARE":
            width = 50
            height = 50
            border_radius = Radius.SM
        else:  # RECTANGLE (default)
            width = 55
            height = 45
            border_radius = Radius.SM
        
        button = ft.Container(
            content=body_text(
                f"{table_num}",
                size=Typography.SIZE_SM,
                weight=FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=Colors.TABLE_FREE,
            padding=Spacing.SM,
            border_radius=border_radius,
            alignment=ft.alignment.center,
            width=width,
            height=height,
            on_click=lambda e, tn=table_num: on_table_click(tn),
            ink=True,  # Ripple effect on click
        )
        
        status_label = body_text(
            "",
            size=8,
            text_align=ft.TextAlign.CENTER,
            color=Colors.WARNING,
        )
        
        container = ft.Container(
            content=ft.Column(
                [button, status_label],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=65,
        )
        
        table_containers[table_num] = container
        return container
    
    def build_section_box(section_name: str, table_numbers: List[int]) -> ft.Container:
        """Build a section container with its tables."""
        # Build table grid for this section (up to 5 per row)
        table_rows = []
        current_row = []
        
        for table_num in sorted(table_numbers):
            current_row.append(build_table_button(table_num))
            if len(current_row) >= 5:
                table_rows.append(
                    ft.Row(current_row, spacing=Spacing.SM, wrap=True)
                )
                current_row = []
        
        if current_row:
            table_rows.append(
                ft.Row(current_row, spacing=Spacing.SM, wrap=True)
            )
        
        return glass_container(
            content=ft.Column(
                [
                    # Section header
                    ft.Container(
                        content=heading(section_name, size=Typography.SIZE_LG, weight=FontWeight.BOLD),
                        padding=ft.padding.only(bottom=Spacing.SM),
                    ),
                    ft.Divider(height=1, color=Colors.BORDER),
                    # Tables grid
                    ft.Container(
                        content=ft.Column(
                            table_rows,
                            spacing=Spacing.SM,
                        ),
                        padding=ft.padding.only(top=Spacing.MD),
                    ),
                ],
                spacing=Spacing.XS,
            ),
            padding=Spacing.LG,
            border_radius=Radius.LG,
        )
    
    def refresh_tables():
        """Refresh table states based on current filter context."""
        selected_dt = app_state.get_selected_datetime()
        selected_date = app_state.get_selected_date()
        
        # Get table states with full reservation data for click handling
        table_states = table_layout_service.get_table_states_for_context(
            selected_time=selected_dt,
            selected_date=selected_date,
            include_reservation_data=True  # Get full reservation dict
        )
        
        # Store for click handling
        current_table_states.clear()
        current_table_states.update(table_states)
        
        # Update filter label
        filter_label.value = f"{get_filter_text()}"
        
        # Get current selection
        current_selected = selected_table["num"]
        
        for table_num, container in table_containers.items():
            # Check if table_num exists in table_states (might be deleted)
            if table_num not in table_states:
                continue
                
            state, info = table_states[table_num]
            
            # Get the button and label from the container
            button = container.content.controls[0]
            status_label = container.content.controls[1]
            
            # Check if this table is selected
            is_selected = (table_num == current_selected)
            
            # Update color based on state and selection
            button.bgcolor = get_table_color(state, is_selected)
            
            # Update border for selection
            if is_selected:
                button.border = ft.border.all(2, Colors.BORDER_SELECTED)
            else:
                button.border = None
            
            # Update status label
            if state == TableState.OCCUPIED:
                status_label.value = ""
            elif state == TableState.SOON_30:
                # info is now a dict, extract time_slot for display
                if info and isinstance(info, dict):
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(info.get("time_slot", ""), "%Y-%m-%d %H:%M")
                        status_label.value = dt.strftime("%H:%M")
                    except:
                        status_label.value = t("occupied_soon")[:5]
                else:
                    status_label.value = t("occupied_soon")[:5]
                status_label.color = Colors.WARNING
            else:  # FREE
                status_label.value = ""
        
        page.update()
    
    def rebuild_sections_view():
        """Rebuild the sections view based on current filter."""
        table_containers.clear()
        sections_column.controls.clear()
        
        sections = db.get_all_section_tables()
        selected_section = current_section_filter["value"]
        
        # Check if "All" selected (in any language)
        is_all = selected_section == t("all") or selected_section == "Всички" or selected_section == "All"
        
        if is_all:
            # Show all sections
            for section in sections:
                if section["tables"]:  # Only show sections with tables
                    section_box = build_section_box(section["name"], section["tables"])
                    sections_column.controls.append(section_box)
        else:
            # Show only selected section
            for section in sections:
                if section["name"] == selected_section and section["tables"]:
                    section_box = build_section_box(section["name"], section["tables"])
                    sections_column.controls.append(section_box)
                    break
        
        # Initial table state refresh
        refresh_tables()
    
    def on_section_change(e):
        """Handle section dropdown change."""
        current_section_filter["value"] = e.control.value
        rebuild_sections_view()
    
    # Build section dropdown options
    sections = db.get_all_section_tables()
    section_options = [ft.dropdown.Option(t("all"))]
    for section in sections:
        section_options.append(ft.dropdown.Option(section["name"]))
    
    section_dropdown = ft.Dropdown(
        label=t("section"),
        value=t("all"),
        options=section_options,
        on_change=on_section_change,
        width=None,
        text_size=Typography.SIZE_SM,
        dense=True,
        bgcolor=Colors.SURFACE_GLASS,
        border_color=Colors.BORDER,
    )
    
    # Legend component
    legend = ft.Column(
        [
            body_text(t("legend"), weight=FontWeight.BOLD, size=Typography.SIZE_SM),
            ft.Container(height=Spacing.XS),
            ft.Row([
                ft.Container(
                    width=14,
                    height=14,
                    bgcolor=Colors.TABLE_FREE,
                    border_radius=3,
                ),
                body_text(t("free"), size=Typography.SIZE_XS),
            ], spacing=Spacing.XS),
            ft.Row([
                ft.Container(
                    width=14,
                    height=14,
                    bgcolor=Colors.TABLE_OCCUPIED,
                    border_radius=3,
                ),
                body_text(t("occupied"), size=Typography.SIZE_XS),
            ], spacing=Spacing.XS),
            ft.Row([
                ft.Container(
                    width=14,
                    height=14,
                    bgcolor=Colors.TABLE_SOON,
                    border_radius=3,
                ),
                body_text(t("occupied_soon"), size=Typography.SIZE_XS),
            ], spacing=Spacing.XS),
        ],
        spacing=Spacing.XS,
    )
    
    # Left sidebar
    left_sidebar = ft.Container(
        content=glass_container(
            content=ft.Column(
                [
                    # Title
                    heading(t("layout"), size=Typography.SIZE_LG, weight=FontWeight.BOLD),
                    ft.Divider(height=1, color=Colors.BORDER),
                    
                    # Date/time info
                    ft.Container(
                        content=ft.Column([
                            label(t("date_and_time"), color=Colors.TEXT_SECONDARY),
                            filter_label,
                        ], spacing=2),
                        padding=ft.padding.only(top=Spacing.SM),
                    ),
                    
                    ft.Container(height=Spacing.MD),
                    
                    # Section selector
                    section_dropdown,
                    
                    ft.Container(height=Spacing.MD),
                    
                    # Legend
                    legend,
                    
                    ft.Container(expand=True),  # Spacer
                    
                    # Navigation button
                    glass_button(
                        t("back_to_reservations"),
                        on_click=lambda e: app_state.navigate_to("reservations"),
                        variant="secondary",
                        width=None,
                    ),
                ],
                spacing=Spacing.SM,
                expand=True,
            ),
            padding=Spacing.LG,
        ),
        width=220,
        padding=Spacing.MD,
    )
    
    # Right side - sections visualization
    right_content = ft.Container(
        content=ft.Column(
            [
                # Header
                ft.Container(
                    content=heading(t("tables"), size=Typography.SIZE_XL, weight=FontWeight.BOLD),
                    padding=ft.padding.only(bottom=Spacing.MD),
                ),
                # Sections column
                sections_column,
            ],
            spacing=0,
            expand=True,
        ),
        expand=True,
        padding=Spacing.LG,
    )
    
    # Initial build
    rebuild_sections_view()
    
    # Build screen with left/right layout + action panel
    return ft.Row(
        [
            left_sidebar,
            right_content,
            action_panel.container,  # Right-side panel for reservation details
        ],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
