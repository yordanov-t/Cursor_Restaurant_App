"""
Reservation service - implements business logic for reservation operations.

This service is UI-agnostic and can be used by any UI framework.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from db import DBManager
from .time_utils import (
    parse_time_slot,
    calculate_reservation_end,
    is_reservation_ongoing,
    get_current_sofia_time,
    RESERVATION_DURATION_MINUTES
)


class ReservationService:
    """
    Business logic for reservations.
    
    Implements filtering semantics:
    - Time-aware filtering: ongoing + future reservations
    - Sorting by start time ascending
    """
    
    def __init__(self, db_manager: DBManager):
        """
        Initialize reservation service.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
    
    def list_reservations_for_context(
        self,
        selected_date: Optional[datetime] = None,
        selected_time: Optional[datetime] = None,
        status_filter: Optional[str] = None,
        table_filter: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List reservations with context-aware filtering.
        
        Implements "Reservations tab semantics":
        - Date filter constrains to that specific date ONLY (no cross-day results)
        - Time filter shows ongoing + future reservations within that date
        - Ongoing: started earlier but still active at selected time
        - Future: start at or after selected time
        - Always sorted by start time ascending
        
        Args:
            selected_date: Selected date (constrains to this date boundary)
            selected_time: Selected specific time (for ongoing + future logic)
            status_filter: Status filter ("Reserved", "Cancelled", None for all)
            table_filter: Table number filter (None for all)
            
        Returns:
            List of reservation dictionaries sorted by start time, 
            constrained to selected_date if provided
        """
        all_reservations = self.db.get_reservations()
        filtered = []
        
        for res in all_reservations:
            # Parse reservation time
            res_start = parse_time_slot(res["time_slot"])
            if res_start is None:
                continue
            
            res_end = calculate_reservation_end(res_start)
            
            # FIRST: Date filtering (strict boundary - must be on selected date)
            if selected_date is not None:
                # Only show reservations that start on the selected date
                if res_start.date() != selected_date:
                    continue  # Skip if not on the selected date
            
            # SECOND: Time-aware filtering (within the selected date)
            if selected_time is not None:
                selected_naive = selected_time.replace(tzinfo=None)
                
                # Check if ongoing or future (but already constrained by date above)
                is_ongoing = is_reservation_ongoing(res_start, res_end, selected_naive)
                is_future = res_start >= selected_naive
                
                if not (is_ongoing or is_future):
                    continue  # Filter out past reservations
            
            # Status filtering
            if status_filter is not None and res["status"] != status_filter:
                continue
            
            # Table filtering
            if table_filter is not None and res["table_number"] != table_filter:
                continue
            
            filtered.append(dict(res))
        
        # Sort by start time ascending
        filtered.sort(key=lambda r: parse_time_slot(r["time_slot"]) or datetime.min)
        
        return filtered
    
    def create_reservation(
        self,
        table_number: int,
        time_slot: str,
        customer_name: str,
        phone_number: str,
        additional_info: str,
        waiter_id: int
    ) -> bool:
        """
        Create a new reservation.
        
        Args:
            table_number: Table number
            time_slot: Time slot string "YYYY-MM-DD HH:MM"
            customer_name: Customer name
            phone_number: Phone number
            additional_info: Additional notes
            waiter_id: Waiter ID
            
        Returns:
            True if successful, False if overlap detected
        """
        return self.db.create_reservation(
            table_number=table_number,
            time_slot=time_slot,
            customer_name=customer_name,
            phone_number=phone_number,
            additional_info=additional_info,
            waiter_id=waiter_id
        )
    
    def update_reservation(
        self,
        reservation_id: int,
        table_number: int,
        time_slot: str,
        customer_name: str,
        phone_number: str,
        additional_info: str,
        waiter_id: int,
        status: str
    ) -> bool:
        """
        Update an existing reservation.
        
        Args:
            reservation_id: ID of reservation to update
            table_number: New table number
            time_slot: New time slot
            customer_name: Updated customer name
            phone_number: Updated phone
            additional_info: Updated notes
            waiter_id: Updated waiter ID
            status: Updated status ("Reserved" or "Cancelled")
            
        Returns:
            True if successful, False if overlap detected
        """
        return self.db.update_reservation(
            reservation_id=reservation_id,
            table_number=table_number,
            time_slot=time_slot,
            customer_name=customer_name,
            phone_number=phone_number,
            additional_info=additional_info,
            waiter_id=waiter_id,
            status=status
        )
    
    def cancel_reservation(self, reservation_id: int) -> None:
        """
        Cancel a reservation (mark as Cancelled, preserves history).
        
        Args:
            reservation_id: ID of reservation to cancel
        """
        self.db.delete_reservation(reservation_id)
    
    def get_reservation_by_id(self, reservation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single reservation by ID.
        
        Args:
            reservation_id: Reservation ID
            
        Returns:
            Reservation dictionary or None if not found
        """
        reservations = self.db.get_reservations()
        for res in reservations:
            if res["id"] == reservation_id:
                return dict(res)
        return None

