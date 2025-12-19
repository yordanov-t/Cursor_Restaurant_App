"""
Application state management for Flet UI.

Centralized state for filters, reservations, and navigation.
"""

from datetime import date
from typing import Optional, Callable, List, Dict, Any


class AppState:
    """
    Centralized application state.
    
    Manages:
    - Filter context (date, time, status, table)
    - Current reservations data
    - Current table states
    - Navigation state
    - Admin state
    """
    
    def __init__(self):
        # Filter context
        self.selected_month = self._get_current_month_bulgarian()
        self.selected_day = str(date.today().day)
        self.selected_hour = "Всички"
        self.selected_minute = "00"  # Default to 00, no "Всички" option
        self.selected_status = "Резервирана"
        self.selected_table = "Всички"
        
        # Data cache
        self.reservations: List[Dict[str, Any]] = []
        self.table_states: Dict[int, tuple] = {}
        
        # Navigation
        self.current_screen = "reservations"  # reservations, table_layout, admin
        
        # Admin
        self.admin_logged_in = False
        
        # Callbacks for UI refresh
        self.on_state_change: Optional[Callable] = None
    
    def _get_current_month_bulgarian(self) -> str:
        """Get current month in Bulgarian."""
        months = [
            "Януари", "Февруари", "Март", "Април", "Май", "Юни",
            "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"
        ]
        return months[date.today().month - 1]
    
    def get_selected_date(self):
        """
        Get selected date (without time).
        
        Returns None if date not fully specified.
        """
        month_map = {
            "Януари": 1, "Февруари": 2, "Март": 3, "Април": 4,
            "Май": 5, "Юни": 6, "Юли": 7, "Август": 8,
            "Септември": 9, "Октомври": 10, "Ноември": 11, "Декември": 12
        }
        
        if self.selected_month == "Всички" or self.selected_day == "Всички":
            return None
        
        try:
            month_num = month_map.get(self.selected_month)
            day_num = int(self.selected_day)
            year = date.today().year
            return date(year, month_num, day_num)
        except (ValueError, TypeError):
            return None
    
    def get_selected_datetime(self):
        """
        Get combined datetime from filters.
        
        Returns None if not all components selected (including time).
        """
        from core import combine_datetime_components
        
        # Month mapping
        month_map = {
            "Януари": 1, "Февруари": 2, "Март": 3, "Април": 4,
            "Май": 5, "Юни": 6, "Юли": 7, "Август": 8,
            "Септември": 9, "Октомври": 10, "Ноември": 11, "Декември": 12
        }
        
        # Minute must be specified now (no "Всички")
        if (self.selected_month == "Всички" or self.selected_day == "Всички" or
            self.selected_hour == "Всички"):
            return None
        
        try:
            month_num = month_map.get(self.selected_month)
            day_num = int(self.selected_day)
            hour_num = int(self.selected_hour)
            minute_num = int(self.selected_minute)  # Always has value now
            year = date.today().year
            
            return combine_datetime_components(year, month_num, day_num, hour_num, minute_num)
        except (ValueError, TypeError):
            return None
    
    def update_filter(self, **kwargs):
        """
        Update filter values and trigger refresh.
        
        Args:
            **kwargs: Filter key-value pairs to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Trigger refresh callback
        if self.on_state_change:
            self.on_state_change()
    
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

