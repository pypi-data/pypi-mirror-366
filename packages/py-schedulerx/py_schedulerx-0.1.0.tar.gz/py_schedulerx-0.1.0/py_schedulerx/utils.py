import time
from typing import Union


def sleep_until(target_time: float) -> None:
    sleep_duration = target_time - time.time()
    if sleep_duration > 0:
        time.sleep(sleep_duration)


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"


def validate_interval(interval: Union[str, int, float]) -> bool:
    try:
        from .interval import IntervalParser
        IntervalParser.parse(interval)
        return True
    except (ValueError, TypeError):
        return False
