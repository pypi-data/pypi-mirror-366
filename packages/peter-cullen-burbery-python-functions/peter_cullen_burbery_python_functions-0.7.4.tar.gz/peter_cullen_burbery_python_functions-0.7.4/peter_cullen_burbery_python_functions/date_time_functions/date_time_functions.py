from datetime import datetime
from zoneinfo import ZoneInfo
import tzlocal

def date_time_stamp() -> str:
    local_tz = tzlocal.get_localzone()
    now = datetime.now(ZoneInfo(local_tz.key))

    date_part = now.strftime("%Y-0%m-0%d")
    time_part = now.strftime("0%H.0%M.0%S.") + f"{now.microsecond * 1000:09d}"
    iso_year, iso_week, iso_weekday = now.isocalendar()
    iso_week_str = f"{iso_week:03d}"
    iso_weekday_str = f"{iso_weekday:03d}"
    day_of_year = f"{now.timetuple().tm_yday:03d}"
    gregorian_year = now.strftime("%Y")

    return f"{date_part} {time_part} {local_tz.key} {iso_year:04d}-W{iso_week_str}-{iso_weekday_str} {gregorian_year}-{day_of_year}"
