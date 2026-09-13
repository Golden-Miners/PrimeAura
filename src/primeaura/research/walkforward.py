from dataclasses import dataclass
from decimal import Decimal
from ..data.models import OHLCVBar
from .evaluation import EvaluationMetrics,evaluate_r_multiples

@dataclass(frozen=True)
class Fold:
    train_start:int
    train_end:int
    test_start:int
    test_end:int

@dataclass(frozen=True)
class WalkForwardResult:
    folds:tuple[Fold,...]
    metrics:tuple[EvaluationMetrics,...]

def make_folds(n:int,train_size:int,test_size:int,step:int|None=None)->tuple[Fold,...]:
    if min(train_size,test_size)<=0 or n<train_size+test_size: return ()
    step=step or test_size; out=[]; start=0
    while start+train_size+test_size<=n:
        out.append(Fold(start,start+train_size,start+train_size,start+train_size+test_size)); start+=step
    return tuple(out)

def run_walk_forward(bars:list[OHLCVBar],strategy,train_size:int,test_size:int,step:int|None=None)->WalkForwardResult:
    folds=make_folds(len(bars),train_size,test_size,step); metrics=[]
    for f in folds:
        trained=strategy.fit(bars[f.train_start:f.train_end])
        results=[]
        for i in range(f.test_start,f.test_end):
            trade=trained.signal(bars[:i+1],i)
            if trade is not None:
                if trade.exit_price is None: continue
                risk=abs(trade.entry-trade.stop_loss)
                if risk<=0: continue
                pnl=(trade.exit_price-trade.entry) if trade.direction=="BUY" else (trade.entry-trade.exit_price)
                results.append(Decimal(pnl)/Decimal(risk))
        metrics.append(evaluate_r_multiples(results))
    return WalkForwardResult(folds,tuple(metrics))
