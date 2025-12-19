"""
Application state management for Flet UI.

Centralized state for filters, reservations, navigation, and language.
"""

from datetime import date, datetime
from typing import Optional, Callable, List, Dict, Any
from ui_flet.i18n import get_current_language, set_language as i18n_set_language


class AppState:
    """
    Centralized application state.
    
    Manages:
    - Filter context (date, time, status, table)
    - Current reservations data
    - Current table states
    - Navigation state
    - Admin state
    - Language state
    """
    
    def __init__(self):
        # Filter context - now using a single date instead of month/day
        self._selected_date: date = date.today()  # Single date object
        self.selected_hour = "Всички"
        self.selected_minute = "00"  # Default to 00, no "Всички" option
        self.selected_status = "Резервирана"
        self.selected_table = "Всички"
        
        # Legacy compatibility - keep month/day for table layout screen
        self.selected_month = self._get_month_bulgarian(self._selected_date.month)
        self.selected_day = str(self._selected_date.day)
        
        # Data cache
        self.reservations: List[Dict[str, Any]] = []
        self.table_states: Dict[int, tuple] = {}
        
        # Navigation
        self.current_screen = "reservations"  # reservations, table_layout, admin
        
        # Admin
        self.admin_logged_in = False
        
        # Language - load from i18n module (persisted)
        self._language = get_current_language()
        
        # Callbacks for UI refresh
        self.on_state_change: Optional[Callable] = None
    
    def _get_month_bulgarian(self, month_num: int) -> str:
        """Get month name in Bulgarian by number (1-12)."""
        months = [
            "Януари", "Февруари", "Март", "Април", "Май", "Юни",
            "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"
        ]
        return months[month_num - 1]
    
    def _get_current_month_bulgarian(self) -> str:
        """Get current month in Bulgarian."""
        return self._get_month_bulgarian(date.today().month)
    
    @property
    def language(self) -> str:
        """Get current language code."""
        return self._language
    
    @language.setter
    def language(self, lang: str):
        """Set current language and trigger UI refresh."""
        self._language = lang
        i18n_set_language(lang)
        if self.on_state_change:
            self.on_state_change()
    
    @property
    def filter_date(self) -> date:
        """Get the selected filter date."""
        return self._selected_date
    
    @filter_date.setter
    def filter_date(self, value):
        """Set the filter date and sync legacy fields.
        
        Accepts both date and datetime objects - converts datetime to date.
        """
        # Handle datetime input (e.g., from DatePicker)
        if isinstance(value, datetime):
            value = value.date()
        
        self._selected_date = value
        # Sync legacy month/day fields for table layout screen
        self.selected_month = self._get_month_bulgarian(value.month)
        self.selected_day = str(value.day)
    
    def get_selected_date(self) -> date:
        """
        Get selected date (without time).
        
        Returns the filter date as a date object.
        """
        # Ensure we always return a date object
        if isinstance(self._selected_date, datetime):
            return self._selected_date.date()
        return self._selected_date
    
    def get_selected_datetime(self):
        """
        Get combined datetime from filters.
        
        Returns None if hour is "Всички".
        """
        from core import combine_datetime_components
        
        if self.selected_hour == "Всички":
            return None
        
        try:
            hour_num = int(self.selected_hour)
            minute_num = int(self.selected_minute)
            
            return combine_datetime_components(
                self._selected_date.year,
                self._selected_date.month,
                self._selected_date.day,
                hour_num,
                minute_num
            )
        except (ValueError, TypeError):
            return None
    
    def update_filter(self, **kwargs):
        """
        Update filter values and trigger refresh.
        
        Args:
            **kwargs: Filter key-value pairs to update
        """
        for key, value in kwargs.items():
            if key == "filter_date":
                self.filter_date = value
            elif hasattr(self, key):
                setattr(self, key, value)
                # If updating legacy month/day, sync to filter_date
                if key in ("selected_month", "selected_day"):
                    self._sync_date_from_legacy()
        
        # Trigger refresh callback
        if self.on_state_change:
            self.on_state_change()
    
    def _sync_date_from_legacy(self):
        """Sync filter_date from legacy month/day fields."""
        month_map = {
            "Януари": 1, "Февруари": 2, "Март": 3, "Април": 4,
            "Май": 5, "Юни": 6, "Юли": 7, "Август": 8,
            "Септември": 9, "Октомври": 10, "Ноември": 11, "Декември": 12
        }
        
        if self.selected_month != "Всички" and self.selected_day != "Всички":
            try:
                month_num = month_map.get(self.selected_month)
                day_num = int(self.selected_day)
                year = date.today().year
                self._selected_date = date(year, month_num, day_num)
            except (ValueError, TypeError):
                pass
    
    def navigate_to(self, screen: str):
        """
        Navigate to a different screen.
        
        Args:
            screen: Screen name (reservations, table_layout, admin)
        """
        self.current_screen = screen
        if self.on_state_change:
            self.on_state_change()
    
    def set_admin_logged_in(self, logged_in: bool):
        """Set admin login state."""
        self.admin_logged_in = logged_in
        if self.on_state_change:
            self.on_state_change()
