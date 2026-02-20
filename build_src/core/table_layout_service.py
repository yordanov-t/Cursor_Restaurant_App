"""
Table layout service - implements occupancy state logic.

This service determines table states (FREE, OCCUPIED, SOON_30) based on
selected date/time context.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, TYPE_CHECKING
from enum import Enum
from .time_utils import (
    parse_time_slot,
    calculate_reservation_end,
    is_reservation_ongoing,
    is_reservation_soon,
    get_current_sofia_time
)

# Use TYPE_CHECKING to avoid circular import with db.py
if TYPE_CHECKING:
    from db import DBManager


class TableState(Enum):
    """Table occupancy states."""
    FREE = "free"
    OCCUPIED = "occupied"
    SOON_30 = "soon_30"  # Will be occupied within 30 minutes


class TableLayoutService:
    """
    Business logic for table layout visualization.
    
    Determines table states based on selected context:
    - OCCUPIED: Currently occupied at selected time (Reserved only)
    - SOON_30: Will become occupied within 30 minutes
    - FREE: Available
    """
    
    def __init__(self, db_manager: "DBManager"):
        """
        Initialize table layout service.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def get_table_states_for_context(
        self,
        selected_time: Optional[datetime] = None,
        selected_date: Optional[datetime] = None,
        num_tables: int = 50,
        include_reservation_data: bool = False
    ) -> Dict[int, tuple]:
        """
        Get table states for the given context.
        
        Args:
            selected_time: Selected specific time (if None, show future reservations)
            selected_date: Selected date (constrains to this date only)
            num_tables: Total number of tables
            include_reservation_data: If True, return full reservation dict instead of start time
            
        Returns:
            Dictionary mapping table_number to (state, info)
            - state: TableState enum
            - info: Additional info (start time for display, or full reservation if include_reservation_data)
        """
        all_reservations = self.db.get_reservations()
        
        # Initialize all tables as FREE
        table_states = {i: (TableState.FREE, None) for i in range(1, num_tables + 1)}
        
        # Track occupied and soon-occupied tables
        occupied_tables = {}  # table_num -> (res_start, res_data)
        soon_tables = {}  # table_num -> (res_start, res_data)
        
        for res in all_reservations:
            # Only consider "Reserved" status
            if res["status"] != "Reserved":
                continue
            
            res_start = parse_time_slot(res["time_slot"])
            if res_start is None:
                continue
            
            # CRITICAL: Enforce date boundary (no cross-date leakage)
            if selected_date is not None:
                # Only consider reservations on the selected date
                if res_start.date() != selected_date:
                    continue
            
            res_end = calculate_reservation_end(res_start)
            table_num = res["table_number"]
            res_dict = dict(res)  # Copy for storage
            
            if selected_time is not None:
                # Specific time selected - check occupancy at that time
                selected_naive = selected_time.replace(tzinfo=None)
                
                # Check if occupied at selected time
                if is_reservation_ongoing(res_start, res_end, selected_naive):
                    occupied_tables[table_num] = (res_start, res_dict)
                # Check if soon occupied (only if not already occupied)
                elif table_num not in occupied_tables:
                    if is_reservation_soon(res_start, selected_naive, threshold_minutes=30):
                        soon_tables[table_num] = (res_start, res_dict)
            else:
                # No specific time - show future reservations (within selected date)
                now = get_current_sofia_time().replace(tzinfo=None)
                if res_start >= now:
                    occupied_tables[table_num] = (res_start, res_dict)
        
        # Update table states
        for table_num, (res_start, res_dict) in occupied_tables.items():
            info = res_dict if include_reservation_data else res_start
            table_states[table_num] = (TableState.OCCUPIED, info)
        
        for table_num, (res_start, res_dict) in soon_tables.items():
            # Only mark as SOON if not already OCCUPIED
            if table_states[table_num][0] == TableState.FREE:
                info = res_dict if include_reservation_data else res_start
                table_states[table_num] = (TableState.SOON_30, info)
        
        return table_states

