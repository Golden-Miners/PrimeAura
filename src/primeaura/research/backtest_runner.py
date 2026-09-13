from dataclasses import dataclass
from decimal import Decimal
from ..data.models import OHLCVBar
from .execution_model import ExecutionConfig,simulate_exit
from .evaluation import EvaluationMetrics,evaluate_r_multiples

@dataclass(frozen=True)
class BacktestTrade:
    index:int
    direction:str
    entry:Decimal
    stop_loss:Decimal
    take_profit:Decimal
    exit_price:Decimal
    outcome:str
    r_multiple:Decimal

def run_signal_backtest(bars:list[OHLCVBar],strategy,execution:ExecutionConfig=ExecutionConfig(),start_index:int=1)->tuple[list[BacktestTrade],EvaluationMetrics]:
    trades=[]
    for i in range(max(1,start_index),len(bars)):
        signal=strategy.signal(bars[:i+1],i)
        if signal is None: continue
        if signal.entry != bars[i].close: raise ValueError("Signal entry must use information available at signal index")
        outcome=simulate_exit(signal.entry,signal.direction,signal.stop_loss,signal.take_profit,bars[i+1:],execution)
        if outcome is None: continue
        risk=abs(signal.entry-signal.stop_loss)
        pnl=(outcome.exit_price-signal.entry) if signal.direction=="BUY" else (signal.entry-outcome.exit_price)
        r=Decimal(pnl)/Decimal(risk) if risk else Decimal("0")
        trades.append(BacktestTrade(i,signal.direction,signal.entry,signal.stop_loss,signal.take_profit,outcome.exit_price,outcome.reason,r))
    return trades,evaluate_r_multiples([x.r_multiple for x in trades])
