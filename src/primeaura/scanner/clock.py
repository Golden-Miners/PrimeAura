from datetime import datetime
from zoneinfo import ZoneInfo

def local_now()->datetime:
    """Return the machine/user local time; timezone is discovered from the OS."""
    return datetime.now().astimezone()

def utc_now()->datetime:
    """Internal UTC timestamp when UTC is explicitly required for market data."""
    from datetime import timezone
    return datetime.now(timezone.utc)
