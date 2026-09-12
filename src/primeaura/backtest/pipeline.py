from dataclasses import dataclass
from decimal import Decimal
from collections.abc import Callable
from ..data.models import OHLCVBar
from .engine import ExecutionCosts, simulate_fixed_exit
from .metrics import calculate_metrics
from .models import BacktestMetrics, TradeResult
from .validation import validate_out_of_sample

@dataclass(frozen=True)
class CandidateTrade:
    index: int
    direction: str
    entry: Decimal
    exit: Decimal
    risk_per_unit: Decimal
    bars_held: int

SignalFn = Callable[[list[OHLCVBar], int], CandidateTrade | None]

def run_backtest(bars:list[OHLCVBar], signal_fn:SignalFn, costs:ExecutionCosts=ExecutionCosts()) -> tuple[TradeResult,...]:
    """Execute a deterministic historical signal function without look-ahead."""
    trades=[]
    for i in range(len(bars)):
        candidate=signal_fn(bars,i)
        if candidate is None: continue
        if candidate.index != i: raise ValueError("signal index must equal evaluation index")
        trades.append(simulate_fixed_exit(candidate.entry,candidate.exit,candidate.direction,candidate.risk_per_unit,candidate.bars_held,costs))
    return tuple(trades)

def evaluate_backtest(trades:list[TradeResult], min_trades:int=100) -> BacktestMetrics:
    metrics=calculate_metrics(trades)
    result=validate_out_of_sample(metrics,min_trades=min_trades)
    if not result.passed: raise ValueError("Backtest did not pass validation: "+"; ".join(result.notes))
    return metrics
