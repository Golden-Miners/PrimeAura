from dataclasses import dataclass
from decimal import Decimal
from .evaluation import evaluate_r_multiples
from .validation import ValidationPolicy,ValidationDecision,validate

@dataclass(frozen=True)
class FoldResult:
    index:int
    train_count:int
    oos_count:int
    oos_net_r:Decimal
    oos_expectancy:Decimal
    decision:ValidationDecision

def walk_forward(results:list[Decimal],folds:int=3,policy:ValidationPolicy=ValidationPolicy())->tuple[FoldResult,...]:
    if folds<1: raise ValueError("folds must be >= 1")
    n=len(results); step=n//(folds+1)
    if step<1: return ()
    out=[]; positive=0
    for i in range(folds):
        train_end=step*(i+1); oos_end=min(step*(i+2),n)
        oos=results[train_end:oos_end]
        if not oos: continue
        m=evaluate_r_multiples(oos); positive += m.net_r>0
        d=validate(m,i+1,int(positive),policy)
        out.append(FoldResult(i+1,train_end,len(oos),m.net_r,m.avg_r,d))
    return tuple(out)
