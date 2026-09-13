from datetime import datetime, timedelta, timezone

from ..data.models import OHLCVBar
from ..signals.models import Signal
from ..scanner.pipeline import generate_from_bars
from .metrics import calculate_metrics
from .models import BacktestMetrics, TradeResult
from .replay import resolve_signal_on_bars

_TIMEFRAME_MINUTES = {"M5": 5, "M15": 15, "H1": 60}

def _closed_as_of(bars: list[OHLCVBar], decision_time: datetime, timeframe: str) -> list[OHLCVBar]:
    duration = timedelta(minutes=_TIMEFRAME_MINUTES[timeframe])
    return [bar for bar in bars if bar.timestamp + duration <= decision_time]

def _future_after(bars: list[OHLCVBar], decision_time: datetime) -> list[OHLCVBar]:
    return [bar for bar in bars if bar.timestamp >= decision_time]

def run_historical(
    instrument: str,
    bars_by_tf: dict[str, list[OHLCVBar]],
    warmup: int = 250,
    max_signals: int | None = None,
) -> tuple[tuple[tuple[Signal, TradeResult], ...], BacktestMetrics]:
    """Run the locked signal engine chronologically without future-data leakage.

    The decision is made only from candles that were fully closed at the M5
    decision time. Future M5 candles are passed only to the outcome resolver.
    """
    m5 = sorted(bars_by_tf["M5"], key=lambda x: x.timestamp)
    h1 = sorted(bars_by_tf["H1"], key=lambda x: x.timestamp)
    m15 = sorted(bars_by_tf["M15"], key=lambda x: x.timestamp)

    paired: list[tuple[Signal, TradeResult]] = []
    last_exit_time: datetime | None = None
    last_decision_time: datetime | None = None

    for i in range(warmup, len(m5)):
        decision_bar = m5[i]
        if last_decision_time is not None and decision_bar.timestamp <= last_decision_time:
            continue
        decision_time = decision_bar.timestamp + timedelta(minutes=5)
        if last_exit_time is not None and decision_time < last_exit_time:
            continue

        history = {
            "H1": _closed_as_of(h1, decision_time, "H1")[-500:],
            "M15": _closed_as_of(m15, decision_time, "M15")[-500:],
            "M5": m5[max(0, i - 499):i + 1],
        }
        if min(map(len, history.values())) < 20:
            continue

        signals = generate_from_bars(instrument, history)
        if not signals:
            continue

        future = _future_after(m5, decision_time)
        for signal in signals:
            result = resolve_signal_on_bars(signal, future)
            if result is not None:
                paired.append((signal, result))
                last_exit_time = decision_time + timedelta(minutes=5 * result.bars_held)
                last_decision_time = decision_time
                if max_signals is not None and len(paired) >= max_signals:
                    return tuple(paired), calculate_metrics([x[1] for x in paired])

    return tuple(paired), calculate_metrics([x[1] for x in paired])
