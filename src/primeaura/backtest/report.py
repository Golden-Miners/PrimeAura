from dataclasses import dataclass
from decimal import Decimal

from .models import BacktestMetrics, TradeResult

@dataclass(frozen=True)
class EquityPoint:
    trade_number: int
    cumulative_pnl: Decimal
    drawdown: Decimal

def build_equity_curve(trades: list[TradeResult] | tuple[TradeResult, ...]) -> tuple[EquityPoint, ...]:
    equity = Decimal("0")
    peak = Decimal("0")
    curve = []
    for number, trade in enumerate(trades, start=1):
        equity += trade.pnl
        peak = max(peak, equity)
        curve.append(EquityPoint(
            trade_number=number,
            cumulative_pnl=equity,
            drawdown=peak - equity,
        ))
    return tuple(curve)

@dataclass(frozen=True)
class BacktestReport:
    metrics: BacktestMetrics
    equity_curve: tuple[EquityPoint, ...]
    trades: tuple[TradeResult, ...]

def build_report(trades: list[TradeResult] | tuple[TradeResult, ...]) -> BacktestReport:
    from .metrics import calculate_metrics
    ordered = tuple(trades)
    return BacktestReport(
        metrics=calculate_metrics(ordered),
        equity_curve=build_equity_curve(ordered),
        trades=ordered,
    )
