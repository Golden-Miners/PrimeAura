from datetime import datetime, timezone
from decimal import Decimal

from primeaura.backtest.engine import ExecutionCosts
from primeaura.backtest.replay import resolve_signal_on_bars
from primeaura.data.models import OHLCVBar
from primeaura.signals.models import Signal

def bar(i, high, low):
    return OHLCVBar(
        instrument="XAUUSD",
        timeframe="M5",
        timestamp=datetime.fromtimestamp(i, tz=timezone.utc),
        open=Decimal("100"),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal("100"),
    )

def signal():
    return Signal(
        instrument="XAUUSD",
        direction="BUY",
        strategy_id="smc-confluence",
        strategy_version="1.0.0",
        entry=Decimal("100"),
        stop_loss=Decimal("99"),
        tp1=Decimal("102"),
        rr_tp1=Decimal("2"),
        confidence=Decimal("85"),
        reasoning=(),
    )

def test_first_target_wins_when_only_target_is_touched():
    result = resolve_signal_on_bars(signal(), [bar(1, 101, 99.5), bar(2, 102, 100.5)])
    assert result is not None
    assert result.exit == Decimal("102")
    assert result.r_multiple == Decimal("2")

def test_same_candle_stop_and_target_is_conservatively_a_loss():
    result = resolve_signal_on_bars(signal(), [bar(1, 102, 98)])
    assert result is not None
    assert result.exit == Decimal("99")
    assert result.r_multiple == Decimal("-1")

def test_costs_are_applied():
    result = resolve_signal_on_bars(
        signal(),
        [bar(1, 102, 100)],
        ExecutionCosts(spread=Decimal("0.1"), slippage=Decimal("0.1"), fee=Decimal("0.1")),
    )
    assert result is not None
    assert result.pnl == Decimal("1.7")
