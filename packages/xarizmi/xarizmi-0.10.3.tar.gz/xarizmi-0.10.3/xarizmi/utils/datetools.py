import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone


def get_current_time_seconds() -> int:
    """Returns current unix timestamp in seconds unit

    Returns
    -------
    int
    """
    return int(time.time())


def get_current_time_miliseconds() -> int:
    """Returns current unix timestamp in milliseconds

    Returns
    -------
    int
    """
    return int(time.time_ns() // 1000000)


def get_current_time_nanoseconds() -> int:
    """Returns current unix timestamp in nanoseconds

    Returns
    -------
    int
    """
    return int(time.time_ns())


def get_current_time_miliseconds_as_string() -> str:
    """Returns current unix timestamp in milliseconds as string.

    Returns
    -------
    str
    """
    return f"{get_current_time_miliseconds()}"


def get_day_timestamps_nanoseconds(
    days_before: int, reference_date: date | None = None
) -> tuple[int, int]:
    """Returns unix start timestamp and end timestamp of given
    day in nano seconds"""
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    # Calculate the target date by subtracting the specified number of days
    target_date = reference_date - timedelta(days=days_before)

    # Define the start and end of the target day in UTC
    start_of_day = datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        0,
        0,
        0,
        tzinfo=timezone.utc,
    )
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

    # Return the timestamps
    return int(start_of_day.timestamp() * 1e9), int(
        end_of_day.timestamp() * 1e9
    )


def get_day_timestamps_seconds(
    days_before: int, reference_date: date | None = None
) -> tuple[int, int]:
    start_of_day, end_of_day = get_day_timestamps_nanoseconds(
        days_before=days_before, reference_date=reference_date
    )
    return int(start_of_day // 1e9), int(end_of_day // 1e9)
