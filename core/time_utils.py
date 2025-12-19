"""
Time utilities for consistent datetime handling.

All time operations use Europe/Sofia timezone to avoid naive/aware datetime mixing.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from zoneinfo import ZoneInfo

# Constants
SOFIA_TIMEZONE = "Europe/Sofia"
TIME_SLOT_FORMAT = "%Y-%m-%d %H:%M"
RESERVATION_DURATION_MINUTES = 90  # 1 hour 30 minutes


def get_current_sofia_time() -> datetime:
    """
    Get current time in Europe/Sofia timezone.
    
    Returns:
        Timezone-aware datetime for Sofia
    """
    return datetime.now(ZoneInfo(SOFIA_TIMEZONE))


def parse_time_slot(time_slot: str) -> Optional[datetime]:
    """
    Parse time slot string to naive datetime (assumes Europe/Sofia).
    
    Args:
        time_slot: Time string in format "YYYY-MM-DD HH:MM"
        
    Returns:
        Naive datetime or None if parsing fails
    """
    try:
        return datetime.strptime(time_slot, TIME_SLOT_FORMAT)
    except (ValueError, TypeError):
        return None


def format_time_slot(dt: datetime) -> str:
    """
    Format datetime to time slot string.
    
    Args:
        dt: Datetime object (naive or aware)
        
    Returns:
        Formatted string "YYYY-MM-DD HH:MM"
    """
    if dt.tzinfo is not None:
        # Convert to naive (Sofia time)
        dt = dt.replace(tzinfo=None)
    return dt.strftime(TIME_SLOT_FORMAT)


def combine_datetime_components(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int
) -> datetime:
    """
    Combine date/time components into timezone-aware datetime.
    
    Args:
        year: Year
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59)
        
    Returns:
        Timezone-aware datetime for Europe/Sofia
    """
    return datetime(year, month, day, hour, minute, tzinfo=ZoneInfo(SOFIA_TIMEZONE))


def calculate_reservation_end(start: datetime) -> datetime:
    """
    Calculate reservation end time based on start time.
    
    Args:
        start: Reservation start time (naive or aware)
        
    Returns:
        End time (same timezone awareness as input)
    """
    return start + timedelta(minutes=RESERVATION_DURATION_MINUTES)


def is_reservation_ongoing(
    res_start: datetime,
    res_end: datetime,
    check_time: datetime
) -> bool:
    """
    Check if reservation is ongoing at the given time.
    
    Args:
        res_start: Reservation start time
        res_end: Reservation end time
        check_time: Time to check
        
    Returns:
        True if reservation overlaps check_time
    """
    return res_start <= check_time < res_end


def is_reservation_soon(
    res_start: datetime,
    check_time: datetime,
    threshold_minutes: int = 30
) -> bool:
    """
    Check if reservation starts soon (within threshold).
    
    Args:
        res_start: Reservation start time
        check_time: Current/selected time
        threshold_minutes: Minutes ahead to consider "soon"
        
    Returns:
        True if reservation starts within threshold
    """
    soon_threshold = check_time + timedelta(minutes=threshold_minutes)
    return check_time < res_start <= soon_threshold

