"""
Time utilities for consistent datetime handling.

All time operations work with naive datetimes assumed to be in Europe/Sofia local time.
We avoid ZoneInfo / pytz entirely because Android's bundled Python (Serious Python)
does not ship tzdata, so ZoneInfo("Europe/Sofia") raises KeyError at runtime.
All comparisons are done with naive datetimes — this is safe because every datetime
in the system originates from user input (already local time) and is stored/compared
consistently without crossing timezone boundaries.
"""

from datetime import datetime, timedelta
from typing import Optional

# Constants
SOFIA_TIMEZONE = "Europe/Sofia"  # kept for reference only — not used at runtime
TIME_SLOT_FORMAT = "%Y-%m-%d %H:%M"
RESERVATION_DURATION_MINUTES = 90  # 1 hour 30 minutes


def get_current_sofia_time() -> datetime:
    """
    Get current local time as a naive datetime.

    Previously used ZoneInfo("Europe/Sofia") but tzdata is not available on
    Android's bundled Python runtime. Returns naive local time instead — all
    datetimes in the system are naive and compared consistently.

    Returns:
        Naive datetime representing current local time
    """
    return datetime.now()


def parse_time_slot(time_slot: str) -> Optional[datetime]:
    """
    Parse time slot string to naive datetime (assumes Europe/Sofia local time).

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
        dt: Datetime object (naive or aware — tzinfo is stripped)

    Returns:
        Formatted string "YYYY-MM-DD HH:MM"
    """
    if dt.tzinfo is not None:
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
    Combine date/time components into a naive datetime.

    Previously returned a ZoneInfo-aware datetime, but tzdata is unavailable
    on Android's bundled Python. Returns naive datetime instead — all comparisons
    in reservation_service.py already strip tzinfo before comparing, so this is safe.

    Args:
        year: Year
        month: Month (1-12)
        day: Day (1-31)
        hour: Hour (0-23)
        minute: Minute (0-59)

    Returns:
        Naive datetime (local time, Europe/Sofia context)
    """
    return datetime(year, month, day, hour, minute)


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
