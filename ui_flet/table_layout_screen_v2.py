"""
Table layout screen for Flet UI - V2 with left sidebar and sections feature.

Features:
- Left sidebar (~20%) with controls, legend, and section selector
- Right side (~80%) with section-grouped table visualization
- Section dropdown to filter view
"""

import flet as ft
from typing import Callable, Dict, List
from core import TableLayoutService, TableState
from db import DBManager
from ui_flet.theme import (Colors, Spacing, Radius, Typography, heading, label, body_text,
                             glass_container, glass_button)
from ui_flet.compat import icons, FontWeight, ScrollMode


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
    
    # Section containers for the right side
    sections_column = ft.Column(spacing=Spacing.LG, scroll=ScrollMode.AUTO, expand=True)
    
    # Current section filter
    current_section_filter = {"value": "Всички"}
    
    def get_filter_text():
        """Get filter context display text."""
        month = app_state.selected_month
        day = app_state.selected_day
        hour = app_state.selected_hour
        minute = app_state.selected_minute
        
        text_parts = []
        if month != "Всички" or day != "Всички":
            if month == "Всички":
                text_parts.append(f"Ден {day}")
            elif day == "Всички":
                text_parts.append(f"{month}")
            else:
                text_parts.append(f"{day} {month}")
        else:
            text_parts.append("Всички дни")
        
        if hour != "Всички" and minute != "Всички":
            text_parts.append(f"в {hour}:{minute}")
        elif hour != "Всички":
            text_parts.append(f"час {hour}")
        
        return " ".join(text_parts)
    
    filter_label = body_text(
        f"{get_filter_text()}",
        size=Typography.SIZE_SM,
    )
    
    def build_table_button(table_num: int) -> ft.Container:
        """Build a single table button."""
        button = ft.Container(
            content=body_text(
                f"{table_num}",
                size=Typography.SIZE_SM,
                weight=FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=Colors.TABLE_FREE,
            padding=Spacing.SM,
            border_radius=Radius.SM,
            alignment=ft.alignment.center,
            width=50,
            height=50,
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
            width=60,
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
        
        # Get table states with strict date boundary
        table_states = table_layout_service.get_table_states_for_context(
            selected_time=selected_dt,
            selected_date=selected_date
        )
        
        # Update filter label
        filter_label.value = f"{get_filter_text()}"
        
        for table_num, container in table_containers.items():
            state, info = table_states[table_num]
            
            # Get the button and label from the container
            button = container.content.controls[0]
            status_label = container.content.controls[1]
            
            if state == TableState.OCCUPIED:
                button.bgcolor = Colors.TABLE_OCCUPIED
                button.color = Colors.TEXT_PRIMARY
                status_label.value = ""
            elif state == TableState.SOON_30:
                button.bgcolor = Colors.TABLE_SOON
                button.color = Colors.TEXT_PRIMARY
                if info:
                    status_label.value = f"{info.strftime('%H:%M')}"
                else:
                    status_label.value = "скоро"
                status_label.color = Colors.WARNING
            else:  # FREE
                button.bgcolor = Colors.TABLE_FREE
                button.color = Colors.TEXT_PRIMARY
                status_label.value = ""
        
        page.update()
    
    def rebuild_sections_view():
        """Rebuild the sections view based on current filter."""
        table_containers.clear()
        sections_column.controls.clear()
        
        sections = db.get_all_section_tables()
        selected_section = current_section_filter["value"]
        
        if selected_section == "Всички":
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
    section_options = [ft.dropdown.Option("Всички")]
    for section in sections:
        section_options.append(ft.dropdown.Option(section["name"]))
    
    section_dropdown = ft.Dropdown(
        label="Секция",
        value="Всички",
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
            body_text("Легенда", weight=FontWeight.BOLD, size=Typography.SIZE_SM),
            ft.Container(height=Spacing.XS),
            ft.Row([
                ft.Container(
                    width=14,
                    height=14,
                    bgcolor=Colors.TABLE_FREE,
                    border_radius=3,
                ),
                body_text("Свободна", size=Typography.SIZE_XS),
            ], spacing=Spacing.XS),
            ft.Row([
                ft.Container(
                    width=14,
                    height=14,
                    bgcolor=Colors.TABLE_OCCUPIED,
                    border_radius=3,
                ),
                body_text("Заета", size=Typography.SIZE_XS),
            ], spacing=Spacing.XS),
            ft.Row([
                ft.Container(
                    width=14,
                    height=14,
                    bgcolor=Colors.TABLE_SOON,
                    border_radius=3,
                ),
                body_text("Заета скоро", size=Typography.SIZE_XS),
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
                    heading("Разпределение", size=Typography.SIZE_LG, weight=FontWeight.BOLD),
                    ft.Divider(height=1, color=Colors.BORDER),
                    
                    # Date/time info
                    ft.Container(
                        content=ft.Column([
                            label("Дата и час", color=Colors.TEXT_SECONDARY),
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
                        "← Резервации",
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
                    content=heading("Маси", size=Typography.SIZE_XL, weight=FontWeight.BOLD),
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
    
    # Build screen with left/right layout
    return ft.Row(
        [
            left_sidebar,
            right_content,
        ],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
