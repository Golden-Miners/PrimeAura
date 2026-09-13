from datetime import datetime, timezone
from decimal import Decimal

from primeaura.backtest.runner import _closed_as_of

from primeaura.data.models import OHLCVBar

def make_bar(minute: int):
    return OHLCVBar(
        instrument="XAUUSD",
        timeframe="M5",
        timestamp=datetime.fromtimestamp(minute * 60, tz=timezone.utc),
        open=Decimal("100"), high=Decimal("101"), low=Decimal("99"),
        close=Decimal("100"), volume=Decimal("1"),
    )

def test_only_fully_closed_bars_are_available_at_decision_time():
    bars = [make_bar(0), make_bar(5), make_bar(10)]
    decision = datetime.fromtimestamp(15 * 60, tz=timezone.utc)
    closed = _closed_as_of(bars, decision, "M5")
    assert [b.timestamp.minute for b in closed] == [0, 5, 10]
