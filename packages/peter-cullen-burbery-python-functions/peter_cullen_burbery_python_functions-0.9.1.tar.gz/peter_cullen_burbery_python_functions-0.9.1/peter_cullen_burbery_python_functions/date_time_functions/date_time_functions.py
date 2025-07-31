"""
Date/time utility functions for high-precision local timestamps.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import tzlocal


def date_time_stamp() -> str:
    """
    Returns a high-precision local timestamp string including:

    - Gregorian calendar date
    - Local time with nanosecond precision
    - IANA time zone
    - ISO week format: YYYY-Www-dd
    - Ordinal day of the year

    Format: `YYYY-0MM-0DD 0HH.0MM.0SS.nanoseconds TZ_NAME YYYY-Www-dd YYYY-DDD`

    Example:
        >>> date_time_stamp()
        '2025-007-030 016.035.051.000000000 America/New_York 2025-W031-003 2025-211'

    Returns:
        str: Formatted timestamp string with nanosecond precision and multiple calendar representations.
    """
    local_timezone = tzlocal.get_localzone()
    now = datetime.now(ZoneInfo(local_timezone.key))

    date_part = now.strftime("%Y-0%m-0%d")
    time_part = now.strftime("0%H.0%M.0%S.") + f"{now.microsecond * 1000:09d}"

    iso_year, iso_week, iso_weekday = now.isocalendar()
    iso_week_str = f"{iso_week:03d}"
    iso_weekday_str = f"{iso_weekday:03d}"
    day_of_year = f"{now.timetuple().tm_yday:03d}"
    gregorian_year = now.strftime("%Y")

    return (
        f"{date_part} {time_part} {local_timezone.key} "
        f"{iso_year:04d}-W{iso_week_str}-{iso_weekday_str} {gregorian_year}-{day_of_year}"
    )