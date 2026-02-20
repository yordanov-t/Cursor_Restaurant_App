"""
Action Panel - Right-side animated panel for Create/Edit/Delete actions.

Replaces popups with a smooth slide-in panel from the right.
Supports internationalization.
"""

import flet as ft
from datetime import datetime, date
from typing import Callable, Optional, Dict, Any
from enum import Enum
from ui_flet.theme import Colors, Spacing, Radius, Typography, heading, label, body_text
from ui_flet.compat import icons, FontWeight
from ui_flet.i18n import t


class PanelMode(Enum):
    """Action panel modes."""
    HIDDEN = "hidden"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    VIEW = "view"  # Read-only view of reservation details


class ActionPanel:
    """
    Right-side action panel with slide-in animation.
    
    Provides a better UX than popups for Create/Edit/Delete operations.
    """
    
    def __init__(
        self,
        page: ft.Page,
        on_close: Callable,
        on_save: Callable,
        on_delete: Callable,
        get_waiters: Callable,
    ):
        """
        Initialize action panel.
        
        Args:
            page: Flet page instance
            on_close: Callback when panel closes
            on_save: Callback for save action (reservation_data)
            on_delete: Callback for delete action (reservation_id)
            get_waiters: Callback to get list of waiters
        """
        self.page = page
        self.on_close = on_close
        self.on_save = on_save
        self.on_delete = on_delete
        self.get_waiters = get_waiters
        
        self.mode = PanelMode.HIDDEN
        self.reservation_data = None
        
        # Form fields
        self.table_dropdown = None
        self.date_field = None
        self.hour_dropdown = None
        self.minute_dropdown = None
        self.customer_name_field = None
        self.phone_field = None
        self.notes_field = None
        self.waiter_dropdown = None
        
        # Build panel
        self.panel_content = ft.Column(spacing=0, expand=True)
        self.container = ft.Container(
            content=self.panel_content,
            width=0,  # Hidden by default
            bgcolor=Colors.SURFACE,
            border=ft.border.only(left=ft.BorderSide(1, Colors.BORDER)),
            padding=0,
            animate=300,  # Animation duration in milliseconds (simple form)
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
    
    def _build_create_edit_form(self) -> ft.Column:
        """Build create/edit reservation form."""
        # Get waiters for dropdown
        waiters = self.get_waiters()
        waiter_options = [ft.dropdown.Option(text=w["name"], key=str(w["id"])) for w in waiters]
        
        # Table dropdown
        self.table_dropdown = ft.Dropdown(
            label=t("table"),
            options=[ft.dropdown.Option(text=f"{t('table')} {i}", key=str(i)) for i in range(1, 51)],
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        )
        
        # Date field with calendar picker
        self.date_field = ft.TextField(
            label=t("date"),
            hint_text=t("select_date"),
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            color=Colors.TEXT_PRIMARY,
            read_only=True,  # Prevent manual typing
            on_click=lambda e: self._open_date_picker(),
            suffix=ft.IconButton(
                icon=icons.CALENDAR_TODAY,
                icon_color=Colors.ACCENT_PRIMARY,
                tooltip=t("select_date"),
                on_click=lambda e: self._open_date_picker(),
            ),
        )
        
        # Hour dropdown (00-23)
        self.hour_dropdown = ft.Dropdown(
            label=t("hour"),
            options=[ft.dropdown.Option(text=f"{h:02d}", key=f"{h:02d}") for h in range(24)],
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
            value="18",  # Default to 18:00
        )
        
        # Minute dropdown (00, 15, 30, 45)
        self.minute_dropdown = ft.Dropdown(
            label=t("minutes"),
            options=[ft.dropdown.Option(text=m, key=m) for m in ["00", "15", "30", "45"]],
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
            value="00",  # Default to :00
        )
        
        # Customer name
        self.customer_name_field = ft.TextField(
            label=t("customer_name"),
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            color=Colors.TEXT_PRIMARY,
        )
        
        # Phone
        self.phone_field = ft.TextField(
            label=t("phone"),
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            color=Colors.TEXT_PRIMARY,
            keyboard_type=ft.KeyboardType.PHONE,
        )
        
        # Notes
        self.notes_field = ft.TextField(
            label=t("notes"),
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            color=Colors.TEXT_PRIMARY,
        )
        
        # Waiter dropdown
        self.waiter_dropdown = ft.Dropdown(
            label=t("waiter"),
            options=waiter_options,
            width=None,
            bgcolor=Colors.SURFACE_GLASS,
            border_color=Colors.BORDER,
            text_style=ft.TextStyle(color=Colors.TEXT_PRIMARY),
        )
        
        # Buttons
        save_button = ft.ElevatedButton(
            text=t("save"),
            icon=icons.SAVE,
            bgcolor=Colors.SUCCESS,
            color=Colors.TEXT_PRIMARY,
            on_click=lambda e: self._handle_save(),
            expand=True,
        )
        
        cancel_button = ft.OutlinedButton(
            text=t("cancel"),
            icon=icons.CANCEL,
            on_click=lambda e: self.close(),
            expand=True,
        )
        
        # Time row with hour and minute dropdowns side by side
        time_row = ft.Row(
            [
                ft.Container(content=self.hour_dropdown, expand=True),
                ft.Container(content=self.minute_dropdown, expand=True),
            ],
            spacing=Spacing.SM,
        )
        
        return ft.Column(
            [
                ft.Container(height=Spacing.LG),
                self.table_dropdown,
                ft.Container(height=Spacing.SM),
                self.date_field,
                ft.Container(height=Spacing.SM),
                label(t("hour"), color=Colors.TEXT_SECONDARY),
                time_row,
                ft.Container(height=Spacing.SM),
                self.customer_name_field,
                ft.Container(height=Spacing.SM),
                self.phone_field,
                ft.Container(height=Spacing.SM),
                self.notes_field,
                ft.Container(height=Spacing.SM),
                self.waiter_dropdown,
                ft.Container(height=Spacing.XL),
                ft.Row(
                    [save_button, cancel_button],
                    spacing=Spacing.MD,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _build_delete_confirm(self) -> ft.Column:
        """Build delete confirmation UI."""
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
                    t("delete_reservation_confirm"),
                    size=Typography.SIZE_MD,
                    color=Colors.TEXT_PRIMARY,
                    weight=FontWeight.MEDIUM,
                ),
                ft.Container(height=Spacing.SM),
                body_text(
                    t("action_cannot_be_undone"),
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
    
    def _build_view_details(self, waiter_name: str = "") -> ft.Column:
        """Build read-only reservation details view."""
        from ui_flet.i18n import get_month_name
        
        data = self.reservation_data
        if not data:
            return ft.Column([body_text(t("error"))])
        
        # Parse time slot for display
        time_display = data.get("time_slot", "")
        date_display = ""
        try:
            dt = datetime.strptime(data["time_slot"], "%Y-%m-%d %H:%M")
            month_name = get_month_name(dt.month)
            date_display = f"{dt.day} {month_name} {dt.year}"
            time_display = dt.strftime("%H:%M")
        except:
            pass
        
        # Calculate end time (90 min duration)
        duration_display = f"90 {t('minutes_abbr')}"
        
        # Status
        status = data.get("status", "Reserved")
        status_display = t("reserved") if status == "Reserved" else t("cancelled")
        status_color = Colors.SUCCESS if status == "Reserved" else Colors.DANGER
        
        def detail_row(lbl: str, value: str, value_color: str = Colors.TEXT_PRIMARY) -> ft.Container:
            """Build a single detail row."""
            return ft.Container(
                content=ft.Column(
                    [
                        label(lbl, color=Colors.TEXT_SECONDARY),
                        body_text(value or "-", color=value_color, weight=FontWeight.MEDIUM),
                    ],
                    spacing=2,
                ),
                padding=ft.padding.only(bottom=Spacing.MD),
            )
        
        return ft.Column(
            [
                ft.Container(height=Spacing.MD),
                
                # Table number (prominent)
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(icons.TABLE_RESTAURANT, color=Colors.ACCENT_PRIMARY, size=32),
                            ft.Container(width=Spacing.SM),
                            heading(f"{t('table')} #{data.get('table_number', '?')}", size=Typography.SIZE_XL),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(bottom=Spacing.LG),
                    alignment=ft.alignment.center,
                ),
                
                ft.Divider(height=1, color=Colors.BORDER),
                ft.Container(height=Spacing.MD),
                
                # Date & Time
                detail_row(t("date"), date_display),
                detail_row(t("time"), time_display),
                detail_row(t("duration"), duration_display),
                
                ft.Divider(height=1, color=Colors.BORDER),
                ft.Container(height=Spacing.MD),
                
                # Customer info
                detail_row(t("customer"), data.get("customer_name", "")),
                detail_row(t("phone"), data.get("phone_number", "") or data.get("phone", "")),
                
                ft.Divider(height=1, color=Colors.BORDER),
                ft.Container(height=Spacing.MD),
                
                # Waiter & Status
                detail_row(t("waiter"), waiter_name),
                ft.Container(
                    content=ft.Column(
                        [
                            label(t("status"), color=Colors.TEXT_SECONDARY),
                            ft.Container(
                                content=body_text(status_display, size=Typography.SIZE_SM),
                                bgcolor=status_color + "40",
                                border_radius=Radius.SM,
                                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.only(bottom=Spacing.MD),
                ),
                
                # Notes (if any)
                ft.Container(
                    content=ft.Column(
                        [
                            label(t("notes"), color=Colors.TEXT_SECONDARY),
                            body_text(
                                data.get("additional_info", "") or data.get("notes", "") or "-",
                                color=Colors.TEXT_PRIMARY if (data.get("additional_info") or data.get("notes")) else Colors.TEXT_DISABLED,
                            ),
                        ],
                        spacing=2,
                    ),
                    padding=ft.padding.only(bottom=Spacing.LG),
                ),
                
                ft.Container(expand=True),  # Spacer
                
                # Close button only (no edit actions)
                ft.ElevatedButton(
                    text=t("close"),
                    icon=icons.CLOSE,
                    bgcolor=Colors.SURFACE_ELEVATED,
                    color=Colors.TEXT_PRIMARY,
                    on_click=lambda e: self.close(),
                    width=None,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _handle_save(self):
        """Handle save button click."""
        # Validate fields
        if not self.table_dropdown.value:
            self._show_error(t("please_select_table"))
            return
        
        if not self.date_field.value:
            self._show_error(t("please_select_date"))
            return
        
        if not self.hour_dropdown.value or not self.minute_dropdown.value:
            self._show_error(t("please_select_time"))
            return
        
        if not self.customer_name_field.value:
            self._show_error(t("please_enter_name"))
            return
        
        # Parse date and time
        try:
            # date_field.value is always "YYYY-MM-DD" (10 chars), take only the first 10 chars
            date_str = str(self.date_field.value).strip()[:10]
            date_parts = date_str.split("-")

            year = int(date_parts[0])
            month = int(date_parts[1])
            day = int(date_parts[2])
            hour = int(str(self.hour_dropdown.value).strip())
            minute = int(str(self.minute_dropdown.value).strip())

            reservation_datetime = datetime(year, month, day, hour, minute)
        except Exception:
            self._show_error(t("invalid_date_time"))
            return
        
        # Build reservation data
        data = {
            "table_number": int(self.table_dropdown.value),
            "time_slot": reservation_datetime.strftime("%Y-%m-%d %H:%M"),
            "customer_name": self.customer_name_field.value,
            "phone": self.phone_field.value or "",
            "notes": self.notes_field.value or "",
            "waiter_id": int(self.waiter_dropdown.value) if self.waiter_dropdown.value else None,
        }
        
        # Add ID if editing
        if self.mode == PanelMode.EDIT and self.reservation_data:
            data["id"] = self.reservation_data["id"]
        
        # Call save callback
        self.on_save(data)
        self.close()
    
    def _handle_delete(self):
        """Handle delete confirmation."""
        if self.reservation_data and "id" in self.reservation_data:
            self.on_delete(self.reservation_data["id"])
        self.close()
    
    def _show_error(self, message: str):
        """Show error snackbar."""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message, color=Colors.TEXT_PRIMARY),
            bgcolor=Colors.DANGER,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _open_date_picker(self):
        """Open the date picker dialog."""
        # Parse current date if set
        current_date = date.today()
        if self.date_field.value:
            try:
                parts = self.date_field.value.split("-")
                current_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except:
                pass
        
        def handle_date_change(e):
            if e.control.value:
                selected_date = e.control.value
                try:
                    # e.control.value can be a date, datetime, or string depending on Flet version
                    if hasattr(selected_date, 'strftime'):
                        self.date_field.value = selected_date.strftime("%Y-%m-%d")
                    else:
                        # String form: take only the date part (first 10 chars)
                        self.date_field.value = str(selected_date)[:10]
                except Exception:
                    self.date_field.value = str(selected_date)[:10]
                self.page.update()
        
        def handle_dismiss(e):
            pass  # Do nothing on dismiss
        
        date_picker = ft.DatePicker(
            first_date=date(2020, 1, 1),
            last_date=date(2030, 12, 31),
            value=current_date,
            on_change=handle_date_change,
            on_dismiss=handle_dismiss,
        )
        
        self.page.overlay.append(date_picker)
        date_picker.open = True
        self.page.update()
    
    def _pre_fill_form(self, data: Dict[str, Any]):
        """Pre-fill form with reservation data (for edit mode)."""
        # Parse time_slot
        try:
            dt = datetime.strptime(data["time_slot"], "%Y-%m-%d %H:%M")
            self.date_field.value = dt.strftime("%Y-%m-%d")
            self.hour_dropdown.value = f"{dt.hour:02d}"
            # Round minute to nearest 15
            minute_val = (dt.minute // 15) * 15
            self.minute_dropdown.value = f"{minute_val:02d}"
        except:
            self.date_field.value = ""
            self.hour_dropdown.value = "18"
            self.minute_dropdown.value = "00"
        
        self.table_dropdown.value = str(data.get("table_number", ""))
        self.customer_name_field.value = data.get("customer_name", "")
        self.phone_field.value = data.get("phone_number", "") or data.get("phone", "")
        self.notes_field.value = data.get("additional_info", "") or data.get("notes", "")
        self.waiter_dropdown.value = str(data.get("waiter_id", "")) if data.get("waiter_id") else None
    
    def _pre_fill_from_context(self, app_state):
        """Pre-fill date/time from current filter context."""
        # Get selected date/time
        selected_dt = app_state.get_selected_datetime()
        if selected_dt:
            self.date_field.value = selected_dt.strftime("%Y-%m-%d")
            self.hour_dropdown.value = f"{selected_dt.hour:02d}"
            # Round minute to nearest 15
            minute_val = (selected_dt.minute // 15) * 15
            self.minute_dropdown.value = f"{minute_val:02d}"
        else:
            # Default to today
            today = date.today()
            self.date_field.value = today.strftime("%Y-%m-%d")
            self.hour_dropdown.value = "18"
            self.minute_dropdown.value = "00"
        
        # Auto-fill current waiter if set
        if app_state.current_waiter_id:
            self.waiter_dropdown.value = str(app_state.current_waiter_id)
    
    def open_create(self, app_state):
        """Open panel in create mode."""
        self.mode = PanelMode.CREATE
        self.reservation_data = None
        
        # Build panel
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("create_reservation")))
        form = self._build_create_edit_form()
        self._pre_fill_from_context(app_state)
        self.panel_content.controls.append(
            ft.Container(content=form, padding=Spacing.LG, expand=True)
        )
        
        # Animate open
        self.container.width = 450
        self.page.update()
    
    def open_edit(self, reservation: Dict[str, Any]):
        """Open panel in edit mode."""
        self.mode = PanelMode.EDIT
        self.reservation_data = reservation
        
        # Build panel
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("edit_reservation")))
        form = self._build_create_edit_form()
        self._pre_fill_form(reservation)
        self.panel_content.controls.append(
            ft.Container(content=form, padding=Spacing.LG, expand=True)
        )
        
        # Animate open
        self.container.width = 450
        self.page.update()
    
    def open_delete(self, reservation: Dict[str, Any]):
        """Open panel in delete mode."""
        self.mode = PanelMode.DELETE
        self.reservation_data = reservation
        
        # Build panel
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("delete_reservation")))
        confirm_ui = self._build_delete_confirm()
        self.panel_content.controls.append(
            ft.Container(content=confirm_ui, padding=Spacing.LG, expand=True)
        )
        
        # Animate open
        self.container.width = 450
        self.page.update()
    
    def open_view(self, reservation: Dict[str, Any], waiter_name: str = ""):
        """
        Open panel in read-only view mode.
        
        Used for viewing reservation details from Table Layout when clicking
        on occupied or soon-occupied tables.
        
        Args:
            reservation: Reservation data dictionary
            waiter_name: Pre-resolved waiter name (to avoid DB lookup in panel)
        """
        self.mode = PanelMode.VIEW
        self.reservation_data = reservation
        
        # Build panel
        self.panel_content.controls.clear()
        self.panel_content.controls.append(self._build_header(t("reservation_details")))
        view_ui = self._build_view_details(waiter_name)
        self.panel_content.controls.append(
            ft.Container(content=view_ui, padding=Spacing.LG, expand=True)
        )
        
        # Animate open
        self.container.width = 400
        self.page.update()
    
    def close(self):
        """Close panel with animation."""
        self.mode = PanelMode.HIDDEN
        self.container.width = 0
        self.page.update()
        
        # Call close callback
        if self.on_close:
            self.on_close()
    
    def is_open(self) -> bool:
        """Check if panel is open."""
        return self.mode != PanelMode.HIDDEN
