import re
from typing import Union


class IntervalParser:
    
    TIME_UNITS = {
        's': 1,
        'sec': 1,
        'second': 1,
        'seconds': 1,
        'm': 60,
        'min': 60,
        'minute': 60,
        'minutes': 60,
        'h': 3600,
        'hour': 3600,
        'hours': 3600,
        'd': 86400,
        'day': 86400,
        'days': 86400,
        'w': 604800,
        'week': 604800,
        'weeks': 604800,
    }
    
    @classmethod
    def parse(cls, interval: Union[str, int, float]) -> float:
        if isinstance(interval, (int, float)):
            return float(interval)
        
        if not isinstance(interval, str):
            raise ValueError(f"Invalid interval type: {type(interval)}")
        
        interval = interval.strip().lower()
        
        pattern = r'^(\d+(?:\.\d+)?)\s*([a-z]+)$'
        match = re.match(pattern, interval)
        
        if not match:
            raise ValueError(f"Invalid interval format: {interval}")
        
        value, unit = match.groups()
        value = float(value)
        
        if unit not in cls.TIME_UNITS:
            raise ValueError(f"Unknown time unit: {unit}")
        
        return value * cls.TIME_UNITS[unit]
