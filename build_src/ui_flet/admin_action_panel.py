"""
Admin Action Panel - Right-side animated panel for Admin management tasks.

Provides Create/Edit/Delete functionality for Waiters and Tables.
Supports internationalization.
"""

import flet as ft
from typing import Callable, Optional, Dict, Any, List
from enum import Enum
from ui_flet.theme import Colors, Spacing, Radius, Typography, heading, label, body_text
from ui_flet.compat import icons, FontWeight, ScrollMode
from ui_flet.i18n import t


class AdminPanelMode(Enum):
    """Admin action panel modes."""
    HIDDEN = "hidden"
    # Waiter modes
    WAITER_CREATE = "waiter_create"
    WAITER_EDIT = "waiter_edit"
    WAITER_DELETE = "waiter_delete"
    # Table modes
    TABLE_CREATE = "table_create"
    TABLE_EDIT = "table_edit"
    TABLE_DELETE = "table_delete"


# Table shape keys (values are fetched dynamically via t())
TABLE_SHAPES = {
    "RECTANGLE": "shape_rectangle",
    "SQUARE": "shape_square",
    "ROUND": "shape_round",
}

def get_shape_display(shape_key: str) -> str:
    """Get translated shape name."""
    translation_key = TABLE_SHAPES.get(shape_key, "shape_rectangle")
    return t(translation_key)


class AdminActionPanel:
    """
    Right-side action panel for admin management.
    
    Provides a better UX than popups for Create/Edit/Delete operations on Waiters and Tables.
    """
    
    def __init__(
        self,
        page: ft.Page,
        on_close: Callable,
        # Waiter callbacks
        on_waiter_create: Callable[[str], bool],  # (name) -> success
        on_waiter_update: Callable[[int, str], bool],  # (id, name) -> success
        on_waiter_delete: Callable[[int], None],  # (id)
        # Table callbacks
        on_table_create: Callable[[int, str], bool],  # (table_number, shape) -> success
        on_table_update: Callable[[int, str], bool],  # (table_number, shape) -> success
        on_table_delete: Callable[[int], bool],  # (table_number) -> success (False if has reservations)
    ):
        """Initialize admin action panel."""
        self.page = page
        self.on_close = on_close
        self.on_waiter_create = on_waiter_create
        self.on_waiter_update = on_waiter_update
        self.on_waiter_delete = on_waiter_delete
        self.on_table_create = on_table_create
        self.on_table_update = on_table_update
        self.on_table_delete = on_table_delete
        
        self.mode = AdminPanelMode.HIDDEN
        self.current_data: Optional[Dict[str, Any]] = None
        
        # Form fields
        self.name_field: Optional[ft.TextField] = None
        self.table_number_field: Optional[ft.TextField] = None
        self.shape_dropdown: Optional[ft.Dropdown] = None
        
        # Build panel
        self.panel_content = ft.Column(spacing=0, expand=True)
        self.container = ft.Container(
            content=self.panel_content,
            width=0,  # Hidden by default
            bgcolor=Colors.SURFACE,
            border=ft.border.only(left=ft.BorderSide(1, Colors.BORDER)),
            padding=0,
            animate=300,
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
                        tooltip=t("close"),
                        on_click=lambda e: self.close(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=Spacing.LG,
            border=ft.border.only(bottom=ft.BorderSide(1, Colors.BORDER)),
        )
    
    # ==========================================
    # Waiter Forms
    # ==========================================
    
    def _build_waiter_form(self, is_create: bool = True) -> ft.Column:
        """Build waiter create/edit form."""
        self.name_field = ft.TextField(
            label=t("waiter_name"),
            hint_text="...",
            value="" if is_create else (self.current_data.get("name", "") if self.current_data else ""),
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            color=Colors.TEXT_PRIMARY,
            autofocus=True,
        )
        
        button_text = t("save") if not is_create else t("save")
        button_icon = icons.ADD if is_create else icons.SAVE
        handler = self._handle_waiter_create if is_create else self._handle_waiter_update
        
        return ft.Column(
            [
                ft.Container(height=Spacing.LG),
                self.name_field,
                ft.Container(height=Spacing.XL),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text=button_text,
                            icon=button_icon,
                            bgcolor=Colors.SUCCESS,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: handler(),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            text=t("cancel"),
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
    
    def _build_waiter_delete_confirm(self) -> ft.Column:
        """Build waiter delete confirmation UI."""
        waiter_name = self.current_data.get("name", "") if self.current_data else ""
        
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
                    t("delete_waiter"),
                    size=Typography.SIZE_MD,
                    color=Colors.TEXT_PRIMARY,
                    weight=FontWeight.BOLD,
                ),
                ft.Container(height=Spacing.SM),
                body_text(
                    f"'{waiter_name}'",
                    size=Typography.SIZE_LG,
                    color=Colors.ACCENT_PRIMARY,
                    weight=FontWeight.BOLD,
                ),
                ft.Container(height=Spacing.MD),
                body_text(
                    t("delete_waiter_confirm"),
                    size=Typography.SIZE_SM,
                    color=Colors.TEXT_SECONDARY,
                ),
                ft.Container(height=Spacing.XL),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text=t("delete"),
                            icon=icons.DELETE_FOREVER,
                            bgcolor=Colors.DANGER,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: self._handle_waiter_delete(),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            text=t("cancel"),
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
    
    def _handle_waiter_create(self):
        """Handle waiter create."""
        name = self.name_field.value.strip() if self.name_field else ""
        if not name:
            self._show_error(t("name_required"))
            return
        
        success = self.on_waiter_create(name)
        if success:
            self.close()
        else:
            self._show_error(t("error"))
    
    def _handle_waiter_update(self):
        """Handle waiter update."""
        name = self.name_field.value.strip() if self.name_field else ""
        if not name:
            self._show_error(t("name_required"))
            return
        
        if not self.current_data:
            self._show_error(t("error"))
            return
        
        waiter_id = self.current_data["id"]
        success = self.on_waiter_update(waiter_id, name)
        if success:
            self.close()
        else:
            self._show_error(t("error"))
    
    def _handle_waiter_delete(self):
        """Handle waiter delete."""
        if not self.current_data:
            self._show_error(t("error"))
            return
        
        waiter_id = self.current_data["id"]
        self.on_waiter_delete(waiter_id)
        self.close()
    
    # ==========================================
    # Table Forms
    # ==========================================
    
    def _build_table_create_form(self, next_table_number: int) -> ft.Column:
        """Build table create form."""
        self.table_number_field = ft.TextField(
            label=t("table_number"),
            value=str(next_table_number),
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            color=Colors.TEXT_PRIMARY,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        self.shape_dropdown = ft.Dropdown(
            label=t("table_shape"),
            value="RECTANGLE",
            options=[
                ft.dropdown.Option(key=key, text=get_shape_display(key)) 
                for key in TABLE_SHAPES.keys()
            ],
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
        )
        
        return ft.Column(
            [
                ft.Container(height=Spacing.LG),
                self.table_number_field,
                ft.Container(height=Spacing.MD),
                self.shape_dropdown,
                ft.Container(height=Spacing.XL),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text=t("save"),
                            icon=icons.ADD,
                            bgcolor=Colors.SUCCESS,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: self._handle_table_create(),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            text=t("cancel"),
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
    
    def _build_table_edit_form(self) -> ft.Column:
        """Build table edit form."""
        table_num = self.current_data.get("table_number", 0) if self.current_data else 0
        current_shape = self.current_data.get("shape", "RECTANGLE") if self.current_data else "RECTANGLE"
        
        self.shape_dropdown = ft.Dropdown(
            label=t("table_shape"),
            value=current_shape,
            options=[
                ft.dropdown.Option(key=key, text=get_shape_display(key)) 
                for key in TABLE_SHAPES.keys()
            ],
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
        )
        
        return ft.Column(
            [
                ft.Container(height=Spacing.LG),
                body_text(f"{t('table')} #{table_num}", size=Typography.SIZE_LG, weight=FontWeight.BOLD),
                ft.Container(height=Spacing.MD),
                self.shape_dropdown,
                ft.Container(height=Spacing.XL),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text=t("save"),
                            icon=icons.SAVE,
                            bgcolor=Colors.SUCCESS,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: self._handle_table_update(),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            text=t("cancel"),
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
    
    def _build_table_delete_confirm(self) -> ft.Column:
        """Build table delete confirmation UI."""
        table_num = self.current_data.get("table_number", 0) if self.current_data else 0
        
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
                    f"{t('delete_table')} #{table_num}",
                    size=Typography.SIZE_MD,
                    color=Colors.TEXT_PRIMARY,
                    weight=FontWeight.BOLD,
                ),
                ft.Container(height=Spacing.SM),
                body_text(
                    t("delete_table_confirm"),
                    size=Typography.SIZE_SM,
                    color=Colors.TEXT_SECONDARY,
                ),
                ft.Container(height=Spacing.XL),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text=t("delete"),
                            icon=icons.DELETE_FOREVER,
                            bgcolor=Colors.DANGER,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: self._handle_table_delete(),
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            text=t("cancel"),
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
    
    def _handle_table_create(self):
        """Handle table create."""
        try:
            table_num = int(self.table_number_field.value) if self.table_number_field else 0
        except ValueError:
            self._show_error(t("error"))
            return
        
        if table_num <= 0:
            self._show_error(t("error"))
            return
        
        shape = self.shape_dropdown.value if self.shape_dropdown else "RECTANGLE"
        success = self.on_table_create(table_num, shape)
        
        if success:
            self.close()
        else:
            self._show_error(t("error"))
    
    def _handle_table_update(self):
        """Handle table update."""
        if not self.current_data:
            self._show_error(t("error"))
            return
        
        table_num = self.current_data["table_number"]
        shape = self.shape_dropdown.value if self.shape_dropdown else "RECTANGLE"
        success = self.on_table_update(table_num, shape)
        
        if success:
            self.close()
        else:
            self._show_error(t("error"))
    
    def _handle_table_delete(self):
        """Handle table delete."""
        if not self.current_data:
            self._show_error(t("error"))
            return
        
        table_num = self.current_data["table_number"]
        success = self.on_table_delete(table_num)
        
        if success:
            self.close()
        else:
            self._show_error(t("error"))
    
    # ==========================================
    # Utility Methods
    # ==========================================
    
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
    
    # ==========================================
    # Public Open Methods
    # ==========================================
    
    def open_waiter_create(self):
        """Open panel for waiter creation."""
        self.mode = AdminPanelMode.WAITER_CREATE
        self.current_data = None
        
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("new_waiter")))
        form = self._build_waiter_form(is_create=True)
        self.panel_content.controls.append(
            ft.Container(content=form, padding=Spacing.LG, expand=True)
        )
        
        self.container.width = 400
        self.page.update()
    
    def open_waiter_edit(self, waiter: Dict[str, Any]):
        """Open panel for waiter editing."""
        self.mode = AdminPanelMode.WAITER_EDIT
        self.current_data = waiter
        
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("edit_waiter")))
        form = self._build_waiter_form(is_create=False)
        self.panel_content.controls.append(
            ft.Container(content=form, padding=Spacing.LG, expand=True)
        )
        
        self.container.width = 400
        self.page.update()
    
    def open_waiter_delete(self, waiter: Dict[str, Any]):
        """Open panel for waiter deletion confirmation."""
        self.mode = AdminPanelMode.WAITER_DELETE
        self.current_data = waiter
        
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("delete_waiter")))
        confirm_ui = self._build_waiter_delete_confirm()
        self.panel_content.controls.append(
            ft.Container(content=confirm_ui, padding=Spacing.LG, expand=True)
        )
        
        self.container.width = 400
        self.page.update()
    
    def open_table_create(self, next_table_number: int = 1):
        """Open panel for table creation."""
        self.mode = AdminPanelMode.TABLE_CREATE
        self.current_data = None
        
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("add_table")))
        form = self._build_table_create_form(next_table_number)
        self.panel_content.controls.append(
            ft.Container(content=form, padding=Spacing.LG, expand=True)
        )
        
        self.container.width = 400
        self.page.update()
    
    def open_table_edit(self, table: Dict[str, Any]):
        """Open panel for table editing."""
        self.mode = AdminPanelMode.TABLE_EDIT
        self.current_data = table
        
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("edit_table")))
        form = self._build_table_edit_form()
        self.panel_content.controls.append(
            ft.Container(content=form, padding=Spacing.LG, expand=True)
        )
        
        self.container.width = 400
        self.page.update()
    
    def open_table_delete(self, table: Dict[str, Any]):
        """Open panel for table deletion confirmation."""
        self.mode = AdminPanelMode.TABLE_DELETE
        self.current_data = table
        
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("delete_table")))
        confirm_ui = self._build_table_delete_confirm()
        self.panel_content.controls.append(
            ft.Container(content=confirm_ui, padding=Spacing.LG, expand=True)
        )
        
        self.container.width = 400
        self.page.update()
    
    def close(self):
        """Close panel with animation."""
        self.mode = AdminPanelMode.HIDDEN
        self.container.width = 0
        self.page.update()
        
        if self.on_close:
            self.on_close()
    
    def is_open(self) -> bool:
        """Check if panel is open."""
        return self.mode != AdminPanelMode.HIDDEN
