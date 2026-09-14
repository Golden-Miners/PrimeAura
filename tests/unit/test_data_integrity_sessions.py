from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.primeaura.data.integrity import validate_bars
from src.primeaura.data.models import OHLCVBar


def bar(ts: datetime) -> OHLCVBar:
    return OHLCVBar(
        instrument="XAUUSD",
        timeframe="M5",
        timestamp=ts,
        open=Decimal("1"),
        high=Decimal("2"),
        low=Decimal("1"),
        close=Decimal("1.5"),
        volume=Decimal("1"),
    )


def test_session_closed_gap_is_warning_not_integrity_failure():
    base = datetime(2026, 9, 10, 22, 0, tzinfo=timezone.utc)
    later = base + timedelta(minutes=30)
    sessions = {day: [] for day in range(7)}
    report = validate_bars([bar(base), bar(later)], sessions)
    assert report["valid"] is True
    assert report["status"] == "WARNING"
    assert report["issues"] == []
    assert report["warnings"]


def test_gap_through_open_session_remains_integrity_failure():
    base = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)
    later = base + timedelta(minutes=30)
    sessions = {day: [] for day in range(7)}
    sessions[(base.weekday() + 1) % 7] = [{"from": 9 * 3600, "to": 17 * 3600}]
    report = validate_bars([bar(base), bar(later)], sessions)
    assert report["valid"] is False
    assert any(issue.startswith("time_gap:") for issue in report["issues"])
