"""
Table layout service - implements occupancy state logic.

This service determines table states (FREE, OCCUPIED, SOON_30) based on
selected date/time context.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from enum import Enum
from db import DBManager
from .time_utils import (
    parse_time_slot,
    calculate_reservation_end,
    is_reservation_ongoing,
    is_reservation_soon,
    get_current_sofia_time
)


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
    
    def __init__(self, db_manager: DBManager):
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
        num_tables: int = 50
    ) -> Dict[int, tuple]:
        """
        Get table states for the given context.
        
        Args:
            selected_time: Selected specific time (if None, show future reservations)
            selected_date: Selected date (constrains to this date only)
            num_tables: Total number of tables
            
        Returns:
            Dictionary mapping table_number to (state, info)
            - state: TableState enum
            - info: Additional info (e.g., start time for SOON_30)
        """
        all_reservations = self.db.get_reservations()
        
        # Initialize all tables as FREE
        table_states = {i: (TableState.FREE, None) for i in range(1, num_tables + 1)}
        
        # Track occupied and soon-occupied tables
        occupied_tables = {}  # table_num -> res_start
        soon_tables = {}  # table_num -> res_start
        
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
            
            if selected_time is not None:
                # Specific time selected - check occupancy at that time
                selected_naive = selected_time.replace(tzinfo=None)
                
                # Check if occupied at selected time
                if is_reservation_ongoing(res_start, res_end, selected_naive):
                    occupied_tables[table_num] = res_start
                # Check if soon occupied (only if not already occupied)
                elif table_num not in occupied_tables:
                    if is_reservation_soon(res_start, selected_naive, threshold_minutes=30):
                        soon_tables[table_num] = res_start
            else:
                # No specific time - show future reservations (within selected date)
                now = get_current_sofia_time().replace(tzinfo=None)
                if res_start >= now:
                    occupied_tables[table_num] = res_start
        
        # Update table states
        for table_num, res_start in occupied_tables.items():
            table_states[table_num] = (TableState.OCCUPIED, res_start)
        
        for table_num, res_start in soon_tables.items():
            # Only mark as SOON if not already OCCUPIED
            if table_states[table_num][0] == TableState.FREE:
                table_states[table_num] = (TableState.SOON_30, res_start)
        
        return table_states

