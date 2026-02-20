"""
Table layout screen for Flet UI.

Visual grid display of table occupancy states.
"""

import flet as ft
from typing import Callable
from core import TableLayoutService, TableState
from ui_flet.compat import Colors, FontWeight, TextAlign, CrossAxisAlignment, MainAxisAlignment, ScrollMode, alignment


def create_table_layout_screen(
    page: ft.Page,
    table_layout_service: TableLayoutService,
    filter_context,
    on_navigate_to_reservations: Callable
):
    """Create the table layout screen."""
    
    # Store table containers for updates
    table_containers = {}
    
    def refresh_tables():
        """Refresh table states."""
        selected_dt = filter_context.get_selected_datetime()
        table_states = table_layout_service.get_table_states_for_context(selected_dt)
        
        for table_num, container in table_containers.items():
            state, info = table_states[table_num]
            
            # Update button color and label
            button = container.content.controls[0]
            label = container.content.controls[1]
            
            if state == TableState.OCCUPIED:
                button.bgcolor = Colors.RED_400
                button.color = Colors.WHITE
                label.value = ""
            elif state == TableState.SOON_30:
                button.bgcolor = Colors.ORANGE_400
                button.color = Colors.WHITE
                if info:
                    label.value = f"Заета в {info.strftime('%H:%M')}"
                else:
                    label.value = "Заета скоро"
            else:  # FREE
                button.bgcolor = Colors.GREEN_400
                button.color = Colors.WHITE
                label.value = ""
        
        page.update()
    
    # Build table grid
    table_grid = []
    for row_idx in range(10):  # 10 rows
        row_containers = []
        for col_idx in range(5):  # 5 columns
            table_num = row_idx * 5 + col_idx + 1
            
            button = ft.Container(
                content=ft.Text(f"Маса {table_num}", size=14, weight=FontWeight.BOLD),
                bgcolor=Colors.GREEN_400,
                padding=15,
                border_radius=8,
                alignment=alignment.center,
            )
            
            label = ft.Text("", size=10, text_align=TextAlign.CENTER, color=Colors.ORANGE_700)
            
            container = ft.Container(
                content=ft.Column([button, label], spacing=5, horizontal_alignment=CrossAxisAlignment.CENTER),
                width=120,
            )
            
            table_containers[table_num] = container
            row_containers.append(container)
        
        table_grid.append(ft.Row(row_containers, spacing=10, alignment=MainAxisAlignment.CENTER))
    
    # Initial load
    refresh_tables()
    
    # Filter context display
    def get_filter_text():
        month = filter_context.selected_month
        day = filter_context.selected_day
        hour = filter_context.selected_hour
        minute = filter_context.selected_minute
        
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
    
    filter_label = ft.Text(
        f"Дата и час: {get_filter_text()}",
        size=16,
        weight=FontWeight.W_500
    )
    
    # Build screen
    return ft.Column(
        [
            # Header
            ft.Container(
                content=ft.Text("Разпределение на масите", size=24, weight=FontWeight.BOLD),
                padding=20,
                bgcolor=Colors.SURFACE_VARIANT,
            ),
            
            # Filter context and legend
            ft.Container(
                content=ft.Column([
                    filter_label,
                    ft.Divider(height=20),
                    ft.Row([
                        ft.Text("Легенда:", weight=FontWeight.BOLD, size=14),
                        ft.Row([
                            ft.Container(width=15, height=15, bgcolor=Colors.GREEN_400, border_radius=3),
                            ft.Text("Свободна", size=12),
                        ], spacing=5),
                        ft.Row([
                            ft.Container(width=15, height=15, bgcolor=Colors.RED_400, border_radius=3),
                            ft.Text("Заета сега", size=12),
                        ], spacing=5),
                        ft.Row([
                            ft.Container(width=15, height=15, bgcolor=Colors.ORANGE_400, border_radius=3),
                            ft.Text("Заета след 30 мин", size=12),
                        ], spacing=5),
                    ], spacing=15),
                ]),
                padding=20,
            ),
            
            # Back button
            ft.Container(
                content=ft.OutlinedButton(
                    "← Към резервации",
                    on_click=on_navigate_to_reservations
                ),
                padding=ft.padding.only(left=20, right=20, bottom=10),
            ),
            
            # Table grid
            ft.Container(
                content=ft.Column(
                    table_grid,
                    spacing=10,
                    scroll=ScrollMode.AUTO,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                expand=True,
                padding=20,
            ),
        ],
        expand=True,
    )

