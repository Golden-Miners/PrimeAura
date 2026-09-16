from datetime import datetime, timezone, timedelta
from decimal import Decimal
from primeaura.data.integrity import validate_bars
from primeaura.data.models import OHLCVBar

def bar(ts):
    return OHLCVBar(instrument="XAUUSD",timeframe="H1",timestamp=ts,open=Decimal("1"),high=Decimal("2"),low=Decimal("0"),close=Decimal("1"),volume=Decimal("1"))

def test_repeated_same_day_gap_is_warning_not_integrity_failure():
    start=datetime(2026,8,10,20,tzinfo=timezone.utc)
    bars=[]
    for day in range(4):
        d=start+timedelta(days=day)
        bars.extend([bar(d),bar(d.replace(hour=23))])
    report=validate_bars(bars)
    assert report["valid"] is True
    assert report["status"]=="WARNING"
    assert any("recurring_session_gap" in x for x in report["warnings"])

def test_single_same_day_gap_remains_failure():
    d=datetime(2026,8,10,20,tzinfo=timezone.utc)
    report=validate_bars([bar(d),bar(d.replace(hour=23))])
    assert report["valid"] is False
    assert any("time_gap" in x for x in report["issues"])
