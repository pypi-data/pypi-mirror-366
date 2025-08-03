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
    - ISO week format: YYYY-Www-ddd
    - Ordinal day of the year

    Format:
        'YYYY-MMM-DDD HHH.MMM.SSS.NNNNNNNNN TZ_NAME YYYY-Www-ddd YYYY-DDD'

    Example:
        >>> date_time_stamp()
        '2025-007-030 016.035.051.000000000 America/New_York 2025-W031-003 2025-211'

    Returns:
        str: Formatted timestamp string with nanosecond precision and multiple calendar representations.
    """
    local_timezone: ZoneInfo = tzlocal.get_localzone()
    now: datetime = datetime.now(ZoneInfo(local_timezone.key))

    # Format components
    date_part: str = f"{now.year}-{now.month:03d}-{now.day:03d}"  # YYYY-MMM-DDD
    time_part: str = f"{now.hour:03d}.{now.minute:03d}.{now.second:03d}.{now.microsecond * 1000:09d}"  # HHH.MMM.SSS.NNNNNNNNN
    time_zone: str = local_timezone.key

    iso_year: int
    iso_week: int
    iso_weekday: int
    iso_year, iso_week, iso_weekday = now.isocalendar()
    iso_week_str: str = f"{iso_week:03d}"
    iso_weekday_str: str = f"{iso_weekday:03d}"

    day_of_year: str = f"{now.timetuple().tm_yday:03d}"
    gregorian_year: str = str(now.year)

    return (
        f"{date_part} {time_part} {time_zone} "
        f"{iso_year:04d}-W{iso_week_str}-{iso_weekday_str} {gregorian_year}-{day_of_year}"
    )

def generate_pdb_name_from_timestamp() -> str:
    """
    Generates a dynamic PDB name in the format:
    pdb_<YYYY>_<MMM>_<DDD>_<HHH>_<MMM>_<SSS>

    Example:
        pdb_2025_007_031_017_020_008

    Returns:
        str: Dynamically constructed PDB name based on the current local time.
    """
    # Get the local time zone using tzlocal and zoneinfo
    local_tz: ZoneInfo = tzlocal.get_localzone()
    
    # Get the current local datetime with time zone awareness
    now: datetime = datetime.now(ZoneInfo(local_tz.key))

    # Extract and format each datetime component as 3-digit strings (except year)
    year: str = f"{now.year}"        # e.g. "2025"
    month: str = f"{now.month:03d}"  # e.g. "007" for July
    day: str = f"{now.day:03d}"      # e.g. "031" for the 31st
    hour: str = f"{now.hour:03d}"    # e.g. "017" for 5 PM
    minute: str = f"{now.minute:03d}"# e.g. "020"
    second: str = f"{now.second:03d}"# e.g. "008"

    # Assemble the PDB name string
    return f"pdb_{year}_{month}_{day}_{hour}_{minute}_{second}"