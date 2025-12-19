"""
Backup Action Panel - Right-side panel for backup/restore operations.

Provides confirmation UI for:
- Deleting backups
- Restoring from backups
Supports internationalization.
"""

import flet as ft
from typing import Callable, Optional, Dict, Any
from enum import Enum
from ui_flet.theme import Colors, Spacing, Radius, Typography, heading, label, body_text
from ui_flet.compat import icons, FontWeight
from ui_flet.i18n import t


class BackupPanelMode(Enum):
    """Backup action panel modes."""
    HIDDEN = "hidden"
    DELETE = "delete"
    RESTORE = "restore"


class BackupActionPanel:
    """
    Right-side action panel for backup operations.
    
    Provides confirmation dialogs for:
    - Delete backup
    - Restore from backup
    """
    
    def __init__(
        self,
        page: ft.Page,
        on_close: Callable,
        on_delete: Callable[[str], bool],
        on_restore: Callable[[str], bool],
    ):
        """
        Initialize backup action panel.
        
        Args:
            page: Flet page instance
            on_close: Callback when panel closes
            on_delete: Callback for delete action (filename) -> success
            on_restore: Callback for restore action (filename) -> success
        """
        self.page = page
        self.on_close = on_close
        self.on_delete = on_delete
        self.on_restore = on_restore
        
        self.mode = BackupPanelMode.HIDDEN
        self.backup_data: Optional[Dict[str, Any]] = None
        
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
    
    def _build_delete_confirm(self) -> ft.Column:
        """Build delete confirmation UI."""
        backup = self.backup_data or {}
        timestamp_str = backup.get("timestamp_str", "")
        size_str = backup.get("size_str", "")
        
        return ft.Column(
            [
                ft.Container(height=Spacing.XL),
                ft.Icon(
                    name=icons.DELETE_FOREVER,
                    color=Colors.DANGER,
                    size=64,
                ),
                ft.Container(height=Spacing.LG),
                body_text(
                    t("delete_backup_confirm"),
                    size=Typography.SIZE_MD,
                    color=Colors.TEXT_PRIMARY,
                    weight=FontWeight.MEDIUM,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=Spacing.MD),
                body_text(
                    f"{t('date')}: {timestamp_str}",
                    size=Typography.SIZE_SM,
                    color=Colors.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                body_text(
                    f"{t('size')}: {size_str}",
                    size=Typography.SIZE_SM,
                    color=Colors.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=Spacing.SM),
                body_text(
                    t("action_cannot_be_undone"),
                    size=Typography.SIZE_SM,
                    color=Colors.DANGER,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=Spacing.XL),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text=t("delete"),
                            icon=icons.DELETE_FOREVER,
                            bgcolor=Colors.DANGER,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: self._handle_delete(),
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
    
    def _build_restore_confirm(self) -> ft.Column:
        """Build restore confirmation UI."""
        backup = self.backup_data or {}
        timestamp_str = backup.get("timestamp_str", "")
        size_str = backup.get("size_str", "")
        counts = backup.get("counts", {})
        
        # Build counts display
        counts_items = []
        if counts.get("reservations", 0) > 0:
            counts_items.append(f"{t('reservations')}: {counts['reservations']}")
        if counts.get("waiters", 0) > 0:
            counts_items.append(f"{t('waiters')}: {counts['waiters']}")
        if counts.get("tables", 0) > 0:
            counts_items.append(f"{t('tables')}: {counts['tables']}")
        if counts.get("sections", 0) > 0:
            counts_items.append(f"{t('sections')}: {counts['sections']}")
        
        counts_text = ", ".join(counts_items) if counts_items else ""
        
        return ft.Column(
            [
                ft.Container(height=Spacing.XL),
                ft.Icon(
                    name=icons.RESTORE,
                    color=Colors.WARNING,
                    size=64,
                ),
                ft.Container(height=Spacing.LG),
                body_text(
                    t("restore_backup"),
                    size=Typography.SIZE_LG,
                    color=Colors.TEXT_PRIMARY,
                    weight=FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=Spacing.MD),
                ft.Container(
                    content=ft.Column([
                        body_text(
                            f"{t('date')}: {timestamp_str}",
                            size=Typography.SIZE_SM,
                            color=Colors.TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        body_text(
                            f"{t('size')}: {size_str}",
                            size=Typography.SIZE_SM,
                            color=Colors.TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        body_text(
                            counts_text,
                            size=Typography.SIZE_SM,
                            color=Colors.TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ) if counts_text else ft.Container(),
                    ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=Colors.SURFACE_GLASS,
                    border=ft.border.all(1, Colors.BORDER),
                    border_radius=Radius.MD,
                    padding=Spacing.MD,
                ),
                ft.Container(height=Spacing.LG),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(icons.WARNING, color=Colors.WARNING, size=24),
                        ft.Container(height=Spacing.XS),
                        body_text(
                            t("warning"),
                            size=Typography.SIZE_MD,
                            color=Colors.WARNING,
                            weight=FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        body_text(
                            t("restore_warning"),
                            size=Typography.SIZE_SM,
                            color=Colors.TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    bgcolor=Colors.WARNING + "20",
                    border=ft.border.all(1, Colors.WARNING),
                    border_radius=Radius.MD,
                    padding=Spacing.MD,
                ),
                ft.Container(height=Spacing.XL),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            text=t("restore"),
                            icon=icons.RESTORE,
                            bgcolor=Colors.WARNING,
                            color=Colors.TEXT_PRIMARY,
                            on_click=lambda e: self._handle_restore(),
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
            scroll=ft.ScrollMode.AUTO,
        )
    
    def _handle_delete(self):
        """Handle delete confirmation."""
        if self.backup_data:
            filename = self.backup_data.get("filename")
            if filename:
                success = self.on_delete(filename)
                if success:
                    self._show_success(t("backup_deleted"))
                else:
                    self._show_error(t("error"))
        self.close()
    
    def _handle_restore(self):
        """Handle restore confirmation."""
        if self.backup_data:
            filename = self.backup_data.get("filename")
            if filename:
                success = self.on_restore(filename)
                if success:
                    self._show_success(t("backup_restored"))
                else:
                    self._show_error(t("error"))
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
    
    def open_delete(self, backup: Dict[str, Any]):
        """Open panel in delete mode."""
        self.mode = BackupPanelMode.DELETE
        self.backup_data = backup
        
        # Build panel
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("delete_backup")))
        confirm_ui = self._build_delete_confirm()
        self.panel_content.controls.append(
            ft.Container(content=confirm_ui, padding=Spacing.LG, expand=True)
        )
        
        # Animate open
        self.container.width = 400
        self.page.update()
    
    def open_restore(self, backup: Dict[str, Any]):
        """Open panel in restore mode."""
        self.mode = BackupPanelMode.RESTORE
        self.backup_data = backup
        
        # Build panel
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("restore_backup")))
        confirm_ui = self._build_restore_confirm()
        self.panel_content.controls.append(
            ft.Container(content=confirm_ui, padding=Spacing.LG, expand=True)
        )
        
        # Animate open
        self.container.width = 420
        self.page.update()
    
    def close(self):
        """Close panel with animation."""
        self.mode = BackupPanelMode.HIDDEN
        self.container.width = 0
        self.page.update()
        
        # Call close callback
        if self.on_close:
            self.on_close()
    
    def is_open(self) -> bool:
        """Check if panel is open."""
        return self.mode != BackupPanelMode.HIDDEN
