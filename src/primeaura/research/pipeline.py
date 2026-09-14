from dataclasses import dataclass
from decimal import Decimal
from ..backtest.replay import resolve_signal_on_bars
from ..backtest.metrics import calculate_metrics
from ..research.validation import ValidationPolicy,ValidationDecision,validate

@dataclass(frozen=True)
class ResearchRun:
    strategy_id:str
    instrument:str
    trade_count:int
    net_r:Decimal
    profit_factor:Decimal|None
    validation:ValidationDecision

def run_research(strategy_id,instrument,bars,signals,policy=ValidationPolicy()):
    trades=[]
    for s in signals:
        result=resolve_signal_on_bars(s,[b for b in bars if b.timestamp>s.detected_at])
        if result is not None: trades.append(result)
    metrics=calculate_metrics(trades)
    decision=validate(metrics,fold_count=0,positive_oos_folds=0,policy=policy)
    return ResearchRun(strategy_id,instrument,metrics.trades,metrics.net_r,metrics.profit_factor,decision)
