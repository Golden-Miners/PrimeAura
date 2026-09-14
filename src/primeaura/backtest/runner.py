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
            "M5": m5[max(0, i - 499):i],
        }
        if min(map(len, history.values())) < 20:
            continue

        signals = generate_from_bars(instrument, history)
        if not signals:
            continue

        # Only candles beginning at/after the decision timestamp are eligible
        # for outcome resolution. The decision candle itself is already closed.
        future = _future_after(m5, decision_time)
        for signal in signals:
            if signal.timestamp != decision_time:
                continue
            result = resolve_signal_on_bars(signal, future)
            if result is not None:
                paired.append((signal, result))
                last_exit_time = decision_time + timedelta(minutes=5 * result.bars_held)
                last_decision_time = decision_time
                if max_signals is not None and len(paired) >= max_signals:
                    return tuple(paired), calculate_metrics([x[1] for x in paired])

    return tuple(paired), calculate_metrics([x[1] for x in paired])


def split_train_test(start: datetime, end: datetime, train_ratio: float = 0.7) -> tuple[tuple[datetime, datetime], tuple[datetime, datetime]]:
    """Create a chronological, non-overlapping train/test split."""
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start and end must be timezone-aware")
    if start >= end:
        raise ValueError("start must be before end")
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1")
    duration = end - start
    split = start + duration * train_ratio
    return (start, split), (split, end)

def split_trade_results_by_time(
    paired: tuple[tuple[Signal, TradeResult], ...],
    split_time: datetime,
) -> tuple[tuple[Signal, TradeResult], tuple[Signal, TradeResult]]:
    """Partition completed trades by signal decision time without overlap."""
    train = []
    test = []
    for signal, result in paired:
        signal_time = getattr(signal, "timestamp", None)
        if signal_time is None:
            continue
        (train if signal_time < split_time else test).append((signal, result))
    return tuple(train), tuple(test)


def build_walk_forward_windows(
    start: datetime,
    end: datetime,
    train_days: int,
    test_days: int,
) -> tuple[tuple[datetime, datetime, datetime, datetime], ...]:
    """Build sequential train/test windows for walk-forward robustness analysis."""
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start and end must be timezone-aware")
    if start >= end:
        raise ValueError("start must be before end")
    if train_days <= 0 or test_days <= 0:
        raise ValueError("train_days and test_days must be positive")

    train_delta = timedelta(days=train_days)
    test_delta = timedelta(days=test_days)
    cursor = start
    windows = []
    while cursor + train_delta + test_delta <= end:
        train_end = cursor + train_delta
        test_end = train_end + test_delta
        windows.append((cursor, train_end, train_end, test_end))
        cursor = test_end
    return tuple(windows)


def evaluate_walk_forward_oos(
    bars_by_tf: dict[str, list[OHLCVBar]],
    windows: tuple[tuple[datetime, datetime, datetime, datetime], ...],
    instrument: str,
    warmup: int = 250,
) -> tuple[
    tuple[tuple[datetime, datetime, datetime, datetime], ...],
    tuple[tuple[tuple[Signal, TradeResult], ...], ...],
    BacktestMetrics,
]:
    """Evaluate fixed rules on sequential OOS windows without crossing test boundaries.

    The train portion supplies historical context only; no parameters are
    optimized. Each test window is replayed with data capped at its test end,
    so a trade must both start and resolve inside that OOS window to count.
    """
    results = []
    all_oos: list[tuple[Signal, TradeResult]] = []

    for train_start, train_end, test_start, test_end in windows:
        capped: dict[str, list[OHLCVBar]] = {}
        for timeframe, bars in bars_by_tf.items():
            ordered = sorted(bars, key=lambda x: x.timestamp)
            capped[timeframe] = [bar for bar in ordered if bar.timestamp <= test_end]

        paired, _ = run_historical(
            instrument,
            capped,
            warmup=warmup,
        )

        window_trades = []
        for signal, trade in paired:
            decision_time = signal.timestamp
            if decision_time is None:
                continue
            exit_time = decision_time + timedelta(minutes=5 * trade.bars_held)
            if test_start <= decision_time < test_end and exit_time <= test_end:
                window_trades.append((signal, trade))
                all_oos.append((signal, trade))

        results.append(tuple(window_trades))

    metrics = calculate_metrics([trade for _, trade in all_oos])
    return windows, tuple(results), metrics


def summarize_walk_forward_oos(
    window_results: tuple[tuple[tuple[Signal, TradeResult], ...], ...],
) -> dict[str, int | bool]:
    """Summarize consistency across independent OOS windows.

    A window is considered positive only when it contains at least one
    completed trade and has positive net P&L. This is descriptive, not a
    statistical significance test and does not imply future profitability.
    """
    metrics = [
        calculate_metrics([trade for _, trade in trades])
        for trades in window_results
    ]
    evaluated = [item for item in metrics if item.trade_count > 0]
    positive = sum(item.net_pnl > 0 for item in evaluated)
    return {
        "windows_total": len(metrics),
        "windows_with_trades": len(evaluated),
        "windows_positive": positive,
        "windows_negative": len(evaluated) - positive,
        "all_evaluated_positive": bool(evaluated) and positive == len(evaluated),
    }


def cost_stress_results(
    signals: list[tuple[Signal, list[OHLCVBar]]],
    scenarios: tuple[tuple[str, ExecutionCosts], ...],
) -> tuple[tuple[str, BacktestMetrics], ...]:
    """Run identical signals under deterministic execution-cost scenarios."""
    results = []
    for name, costs in scenarios:
        trades = run_replay(signals, costs)
        results.append((name, calculate_metrics(trades)))
    return tuple(results)
