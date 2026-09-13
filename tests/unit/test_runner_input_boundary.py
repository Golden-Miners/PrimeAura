from datetime import datetime, timedelta, timezone
from decimal import Decimal

from primeaura.backtest.runner import _closed_as_of
from primeaura.data.models import OHLCVBar

def make_bar(offset: int):
    return OHLCVBar(
        instrument="XAUUSD", timeframe="M5",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=5 * offset),
        open=Decimal("100"), high=Decimal("101"), low=Decimal("99"),
        close=Decimal("100"), volume=Decimal("1"),
    )

def test_decision_boundary_excludes_forming_bar():
    bars = [make_bar(0), make_bar(1), make_bar(2)]
    decision_time = bars[2].timestamp + timedelta(minutes=2)
    closed = _closed_as_of(bars, decision_time, "M5")
    assert len(closed) == 2
    assert closed[-1].timestamp == bars[1].timestamp
