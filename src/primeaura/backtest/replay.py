from ..data.models import OHLCVBar
from ..signals.models import Signal
from .engine import ExecutionCosts, apply_costs
from .models import TradeResult

def resolve_signal_on_bars(
    signal: Signal,
    future_bars: list[OHLCVBar],
    costs: ExecutionCosts = ExecutionCosts(),
) -> TradeResult | None:
    """Resolve the first SL/TP1 touch after a confirmed signal.

    Conservative rule: if SL and TP1 are both touched by the same candle,
    SL wins because OHLC data cannot establish intrabar order.
    """
    risk = abs(signal.entry - signal.stop_loss)
    if risk <= 0:
        return None

    entry = apply_costs(signal.entry, "SELL" if signal.direction == "BUY" else "BUY", costs)
    for index, bar in enumerate(future_bars, start=1):
        if signal.direction == "BUY":
            stop_hit = bar.low <= signal.stop_loss
            target_hit = bar.high >= signal.tp1
            if stop_hit:
                raw_exit = signal.stop_loss
            elif target_hit:
                raw_exit = signal.tp1
            else:
                continue
        elif signal.direction == "SELL":
            stop_hit = bar.high >= signal.stop_loss
            target_hit = bar.low <= signal.tp1
            if stop_hit:
                raw_exit = signal.stop_loss
            elif target_hit:
                raw_exit = signal.tp1
            else:
                continue
        else:
            raise ValueError("signal direction must be BUY or SELL")

        exit_price = apply_costs(raw_exit, signal.direction, costs)
        pnl = (
            exit_price - entry
            if signal.direction == "BUY"
            else entry - exit_price
        ) - costs.fee
        return TradeResult(
            entry=entry,
            exit=exit_price,
            direction=signal.direction,
            pnl=pnl,
            r_multiple=pnl / risk,
            bars_held=index,
        )

    return None

def run_replay(
    signals: list[tuple[Signal, list[OHLCVBar]]],
    costs: ExecutionCosts = ExecutionCosts(),
) -> tuple[TradeResult, ...]:
    """Evaluate pre-generated historical signals without changing the strategy."""
    results = []
    for signal, future_bars in signals:
        result = resolve_signal_on_bars(signal, future_bars, costs)
        if result is not None:
            results.append(result)
    return tuple(results)
