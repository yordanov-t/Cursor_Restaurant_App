"""
Section Action Panel - Right-side animated panel for Section management in Admin.

Provides Create/Edit/Assign Tables/Delete functionality for sections.
"""

import flet as ft
from typing import Callable, Optional, Dict, Any, List, Set, Union
from enum import Enum
from ui_flet.theme import Colors, Spacing, Radius, Typography, heading, label, body_text
from ui_flet.compat import icons, FontWeight, ScrollMode


class SectionPanelMode(Enum):
    """Section action panel modes."""
    HIDDEN = "hidden"
    CREATE = "create"
    EDIT = "edit"
    ASSIGN_TABLES = "assign_tables"
    DELETE = "delete"


class SectionActionPanel:
    """
    Right-side action panel for section management.
    
    Provides a better UX than popups for Create/Edit/Assign Tables/Delete operations.
    """
    
    def __init__(
        self,
        page: ft.Page,
        on_close: Callable,
        on_create: Callable[[str, List[int]], bool],  # (name, tables) -> success
        on_update: Callable[[int, str], bool],  # (id, name) -> success
        on_assign_tables: Callable[[int, List[int]], None],  # (id, tables)
        on_delete: Callable[[int], None],  # (id)
    ):
        """
        Initialize section action panel.
        
        Args:
            page: Flet page instance
            on_close: Callback when panel closes
            on_create: Callback for create action (name, tables) -> success
            on_update: Callback for update action (id, name) -> success
            on_assign_tables: Callback for assign tables action (id, tables)
            on_delete: Callback for delete action (id)
        """
        self.page = page
        self.on_close = on_close
        self.on_create = on_create
        self.on_update = on_update
        self.on_assign_tables = on_assign_tables
        self.on_delete = on_delete
        
        self.mode = SectionPanelMode.HIDDEN
        self.section_data: Optional[Dict[str, Any]] = None
        
        # Form fields
        self.name_field: Optional[ft.TextField] = None
        self.selected_tables: Set[int] = set()
        self.checkbox_refs: Dict[int, ft.Checkbox] = {}
        
        # Build panel
        self.panel_content = ft.Column(spacing=0, expand=True)
        self.container = ft.Container(
            content=self.panel_content,
            width=0,  # Hidden by default
            bgcolor=Colors.SURFACE,
            border=ft.border.only(left=ft.BorderSide(1, Colors.BORDER)),
            padding=0,
            animate=300,  # Animation duration in milliseconds
        )
    
    def _build_header(self, title: str) -> ft.Container:
        """Build panel header with title and close button."""
        return ft.Container(
            content=ft.Row(
                [
                    heading(title, size=Typography.SIZE_LG, weight=FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=icons.CLOSE,
                        icon_color=Colors.TEXT_SECONDARY,
                        tooltip="Затвори",
                        on_click=lambda e: self.close(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=Spacing.LG,
            border=ft.border.only(bottom=ft.BorderSide(1, Colors.BORDER)),
        )
    
    def _build_table_grid(self, get_available_tables: Callable = None) -> ft.Column:
        """Build the table selection grid with scrolling support."""
        self.checkbox_refs.clear()
        table_grid = []
        
        # Get available tables (default 1-50 if no callback provided)
        if get_available_tables:
            available_tables = get_available_tables()
        else:
            available_tables = list(range(1, 51))
        
        # Build rows with 5 tables each
        current_row = []
        for table_num in sorted(available_tables):
            def make_toggle_handler(tn: int):
                def toggle(e):
                    if e.control.value:
                        self.selected_tables.add(tn)
                    else:
                        self.selected_tables.discard(tn)
                return toggle
            
            cb = ft.Checkbox(
                label=str(table_num),
                value=table_num in self.selected_tables,
                on_change=make_toggle_handler(table_num),
                fill_color={
                    ft.ControlState.SELECTED: Colors.ACCENT_PRIMARY,
                },
            )
            self.checkbox_refs[table_num] = cb
            current_row.append(
                ft.Container(
                    content=cb,
                    width=70,
                )
            )
            
            if len(current_row) >= 5:
                table_grid.append(ft.Row(current_row, spacing=Spacing.XS))
                current_row = []
        
        # Add remaining items
        if current_row:
            table_grid.append(ft.Row(current_row, spacing=Spacing.XS))
        
        # Return scrollable column
        return ft.Column(table_grid, spacing=Spacing.XS, scroll=ScrollMode.AUTO)
    
    def _select_all_tables(self, e):
        """Select all tables."""
        for tn, cb in self.checkbox_refs.items():
            cb.value = True
            self.selected_tables.add(tn)
        self.page.update()
    
    def _clear_all_tables(self, e):
        """Clear all table selections."""
        for tn, cb in self.checkbox_refs.items():
            cb.value = False
        self.selected_tables.clear()
        self.page.update()
    
    def _build_create_form(self) -> ft.Column:
        """Build create section form."""
        self.name_field = ft.TextField(
            label="Име на секция",
            hint_text="Въведете име...",
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            color=Colors.TEXT_PRIMARY,
            autofocus=True,
        )
        
        table_grid = self._build_table_grid()
        
        return ft.Column(
            [
                ft.Container(height=Spacing.LG),
                self.name_field,
                ft.Container(height=Spacing.LG),
                ft.Divider(height=1, color=Colors.BORDER),
                ft.Container(height=Spacing.MD),
                body_text("Изберете маси за секцията:", weight=FontWeight.MEDIUM),
                ft.Container(height=Spacing.SM),
                ft.Row([
                    ft.TextButton(
                        "Избери всички",
                        on_click=self._select_all_tables,
                        style=ft.ButtonStyle(color=Colors.ACCENT_PRIMARY),
                    ),
                    ft.TextButton(
                        "Изчисти",
                        on_click=self._clear_all_tables,
                        style=ft.ButtonStyle(color=Colors.TEXT_SECONDARY),
                    ),
                ], spacing=Spacing.SM),
                ft.Container(height=Spacing.SM),
                ft.Container(
                    content=table_grid,
                    expand=True,
                    border=ft.border.all(1, Colors.BORDER),
                    border_radius=Radius.SM,
                    padding=Spacing.SM,
                ),
                ft.Container(height=Spacing.MD),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Създай",
                            icon=icons.ADD,
                            bgcolor=Colors.SUCCESS,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: self._handle_create(),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            text="Отказ",
                            icon=icons.CANCEL,
                            on_click=lambda e: self.close(),
                            expand=True,
                        ),
                    ],
                    spacing=Spacing.MD,
                ),
            ],
            expand=True,
        )
    
    def _build_edit_form(self) -> ft.Column:
        """Build edit section name form."""
        self.name_field = ft.TextField(
            label="Име на секция",
            value=self.section_data.get("name", "") if self.section_data else "",
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            color=Colors.TEXT_PRIMARY,
            autofocus=True,
        )
        
        return ft.Column(
            [
                ft.Container(height=Spacing.LG),
                self.name_field,
                ft.Container(height=Spacing.XL),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Запази",
                            icon=icons.SAVE,
                            bgcolor=Colors.SUCCESS,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: self._handle_update(),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            text="Отказ",
                            icon=icons.CANCEL,
                            on_click=lambda e: self.close(),
                            expand=True,
                        ),
                    ],
                    spacing=Spacing.MD,
                ),
            ],
            scroll=ScrollMode.AUTO,
            expand=True,
        )
    
    def _build_assign_tables_form(self) -> ft.Column:
        """Build assign tables form."""
        section_name = self.section_data.get("name", "") if self.section_data else ""
        table_grid = self._build_table_grid()
        
        return ft.Column(
            [
                ft.Container(height=Spacing.LG),
                body_text(f"Секция: {section_name}", weight=FontWeight.BOLD, size=Typography.SIZE_MD),
                ft.Container(height=Spacing.MD),
                ft.Divider(height=1, color=Colors.BORDER),
                ft.Container(height=Spacing.SM),
                body_text("Изберете маси за секцията:", weight=FontWeight.MEDIUM),
                ft.Container(height=Spacing.XS),
                ft.Row([
                    ft.TextButton(
                        "Избери всички",
                        on_click=self._select_all_tables,
                        style=ft.ButtonStyle(color=Colors.ACCENT_PRIMARY),
                    ),
                    ft.TextButton(
                        "Изчисти",
                        on_click=self._clear_all_tables,
                        style=ft.ButtonStyle(color=Colors.TEXT_SECONDARY),
                    ),
                ], spacing=Spacing.SM),
                ft.Container(height=Spacing.XS),
                ft.Container(
                    content=table_grid,
                    expand=True,
                    border=ft.border.all(1, Colors.BORDER),
                    border_radius=Radius.SM,
                    padding=Spacing.SM,
                ),
                ft.Container(height=Spacing.MD),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Запази",
                            icon=icons.SAVE,
                            bgcolor=Colors.SUCCESS,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: self._handle_assign_tables(),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            text="Отказ",
                            icon=icons.CANCEL,
                            on_click=lambda e: self.close(),
                            expand=True,
                        ),
                    ],
                    spacing=Spacing.MD,
                ),
            ],
            expand=True,
        )
    
    def _build_delete_confirm(self) -> ft.Column:
        """Build delete confirmation UI."""
        section_name = self.section_data.get("name", "") if self.section_data else ""
        tables_count = len(self.section_data.get("tables", [])) if self.section_data else 0
        
        return ft.Column(
            [
                ft.Container(height=Spacing.XL),
                ft.Icon(
                    name=icons.WARNING,
                    color=Colors.DANGER,
                    size=64,
                ),
                ft.Container(height=Spacing.LG),
                body_text(
                    f"Изтриване на секция '{section_name}'",
                    size=Typography.SIZE_MD,
                    color=Colors.TEXT_PRIMARY,
                    weight=FontWeight.BOLD,
                ),
                ft.Container(height=Spacing.SM),
                body_text(
                    "Сигурни ли сте, че искате да изтриете тази секция?",
                    size=Typography.SIZE_SM,
                    color=Colors.TEXT_SECONDARY,
                ),
                ft.Container(height=Spacing.SM),
                body_text(
                    f"Съдържа {tables_count} маси, които ще бъдат освободени.",
                    size=Typography.SIZE_SM,
                    color=Colors.WARNING,
                ) if tables_count > 0 else ft.Container(),
                ft.Container(height=Spacing.XL),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text="Изтрий",
                            icon=icons.DELETE_FOREVER,
                            bgcolor=Colors.DANGER,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: self._handle_delete(),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            text="Отказ",
                            icon=icons.CANCEL,
                            on_click=lambda e: self.close(),
                            expand=True,
                        ),
                    ],
                    spacing=Spacing.MD,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
    
    def _handle_create(self):
        """Handle create button click."""
        name = self.name_field.value.strip() if self.name_field else ""
        
        if not name:
            self._show_error("Името не може да бъде празно")
            return
        
        tables = list(self.selected_tables)
        success = self.on_create(name, tables)
        
        if success:
            self._show_success("Секцията е създадена")
            self.close()
        else:
            self._show_error("Секция с това име вече съществува")
    
    def _handle_update(self):
        """Handle update button click."""
        name = self.name_field.value.strip() if self.name_field else ""
        
        if not name:
            self._show_error("Името не може да бъде празно")
            return
        
        if not self.section_data:
            self._show_error("Грешка: няма данни за секцията")
            return
        
        section_id = self.section_data["id"]
        success = self.on_update(section_id, name)
        
        if success:
            self._show_success("Секцията е обновена")
            self.close()
        else:
            self._show_error("Секция с това име вече съществува")
    
    def _handle_assign_tables(self):
        """Handle assign tables button click."""
        if not self.section_data:
            self._show_error("Грешка: няма данни за секцията")
            return
        
        section_id = self.section_data["id"]
        tables = list(self.selected_tables)
        self.on_assign_tables(section_id, tables)
        self._show_success("Масите са зададени")
        self.close()
    
    def _handle_delete(self):
        """Handle delete confirmation."""
        if not self.section_data:
            self._show_error("Грешка: няма данни за секцията")
            return
        
        section_id = self.section_data["id"]
        self.on_delete(section_id)
        self._show_success("Секцията е изтрита")
        self.close()
    
    def _show_error(self, message: str):
        """Show error snackbar."""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message, color=Colors.TEXT_PRIMARY),
            bgcolor=Colors.DANGER,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _show_success(self, message: str):
        """Show success snackbar."""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message, color=Colors.TEXT_PRIMARY),
            bgcolor=Colors.SUCCESS,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def open_create(self):
        """Open panel in create mode."""
        self.mode = SectionPanelMode.CREATE
        self.section_data = None
        self.selected_tables.clear()
        
        # Build panel
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header("Нова секция"))
        form = self._build_create_form()
        self.panel_content.controls.append(
            ft.Container(content=form, padding=Spacing.LG, expand=True)
        )
        
        # Animate open
        self.container.width = 420
        self.page.update()
    
    def open_edit(self, section: Dict[str, Any]):
        """Open panel in edit mode."""
        self.mode = SectionPanelMode.EDIT
        self.section_data = section
        
        # Build panel
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header("Редактирай секция"))
        form = self._build_edit_form()
        self.panel_content.controls.append(
            ft.Container(content=form, padding=Spacing.LG, expand=True)
        )
        
        # Animate open
        self.container.width = 420
        self.page.update()
    
    def open_assign_tables(self, section: Dict[str, Any]):
        """Open panel in assign tables mode."""
        self.mode = SectionPanelMode.ASSIGN_TABLES
        self.section_data = section
        self.selected_tables = set(section.get("tables", []))
        
        # Build panel
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header("Промени маси"))
        form = self._build_assign_tables_form()
        self.panel_content.controls.append(
            ft.Container(content=form, padding=Spacing.LG, expand=True)
        )
        
        # Animate open
        self.container.width = 420
        self.page.update()
    
    def open_delete(self, section: Dict[str, Any]):
        """Open panel in delete mode."""
        self.mode = SectionPanelMode.DELETE
        self.section_data = section
        
        # Build panel
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header("Изтрий секция"))
        confirm_ui = self._build_delete_confirm()
        self.panel_content.controls.append(
            ft.Container(content=confirm_ui, padding=Spacing.LG, expand=True)
        )
        
        # Animate open
        self.container.width = 420
        self.page.update()
    
    def close(self):
        """Close panel with animation."""
        self.mode = SectionPanelMode.HIDDEN
        self.container.width = 0
        self.page.update()
        
        # Call close callback
        if self.on_close:
            self.on_close()
    
    def is_open(self) -> bool:
        """Check if panel is open."""
        return self.mode != SectionPanelMode.HIDDEN

