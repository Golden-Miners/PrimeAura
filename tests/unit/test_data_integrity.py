from datetime import datetime, timedelta, timezone
from decimal import Decimal

from primeaura.data.integrity import validate_bars, validate_multitimeframe
from primeaura.data.models import OHLCVBar


def bar(ts, o=100, h=110, l=90, c=105, tf="M5"):
    return OHLCVBar(
        instrument="XAUUSD", timeframe=tf, timestamp=ts,
        open=Decimal(str(o)), high=Decimal(str(h)),
        low=Decimal(str(l)), close=Decimal(str(c)), volume=Decimal("1")
    )


def test_valid_series():
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    report = validate_bars([bar(t), bar(t + timedelta(minutes=5))])
    assert report["valid"] is True


def test_duplicate_timestamp_detected():
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    report = validate_bars([bar(t), bar(t)])
    assert report["valid"] is False
    assert any("duplicate_timestamps" in x for x in report["issues"])


def test_gap_detected():
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    report = validate_bars([bar(t), bar(t + timedelta(minutes=15))])
    assert report["valid"] is False
    assert any("time_gap" in x for x in report["issues"])


def test_invalid_ohlc_detected():
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    report = validate_bars([bar(t, o=120, h=110, l=90, c=100)])
    assert report["valid"] is False


def test_multitimeframe_report():
    t = datetime(2026, 1, 1, tzinfo=timezone.utc)
    report = validate_multitimeframe({
        "M5": [bar(t), bar(t + timedelta(minutes=5))],
        "M15": [bar(t, tf="M15")],
    })
    assert "timeframes" in report
    assert report["valid"] is True
