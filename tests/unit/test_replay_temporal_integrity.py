from datetime import datetime, timedelta, timezone
from decimal import Decimal

from primeaura.backtest.replay import resolve_signal_on_bars
from primeaura.data.models import OHLCVBar
from primeaura.signals.models import Signal


def _bar(ts: datetime, price: Decimal) -> OHLCVBar:
    return OHLCVBar(
        timestamp=ts,
        open=price,
        high=price + Decimal("10"),
        low=price - Decimal("10"),
        close=price,
        volume=Decimal("1"),
    )


def test_replay_ignores_bars_before_decision_time():
    decision = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    signal = Signal(
        instrument="XAUUSD",
        timestamp=decision,
        direction="BUY",
        strategy_id="test",
        strategy_version="1.0.0",
        entry=Decimal("100"),
        stop_loss=Decimal("90"),
        tp1=Decimal("120"),
        rr_tp1=Decimal("2"),
        confidence=Decimal("80"),
        reasoning=("test",),
    )
    bars = [
        _bar(decision - timedelta(minutes=5), Decimal("100")),
        _bar(decision, Decimal("100")),
        _bar(decision + timedelta(minutes=5), Decimal("120")),
    ]

    result = resolve_signal_on_bars(signal, [b for b in bars if b.timestamp >= decision])
    assert result is not None
    assert result.bars_held == 2


def test_replay_does_not_use_future_beyond_supplied_boundary():
    decision = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    signal = Signal(
        instrument="XAUUSD",
        timestamp=decision,
        direction="BUY",
        strategy_id="test",
        strategy_version="1.0.0",
        entry=Decimal("100"),
        stop_loss=Decimal("90"),
        tp1=Decimal("120"),
        rr_tp1=Decimal("2"),
        confidence=Decimal("80"),
        reasoning=("test",),
    )
    bars = [_bar(decision + timedelta(minutes=5), Decimal("100"))]
    assert resolve_signal_on_bars(signal, bars) is None
