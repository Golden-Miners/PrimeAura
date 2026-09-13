from dataclasses import dataclass
from decimal import Decimal
from statistics import mean

@dataclass(frozen=True)
class EvaluationMetrics:
    trades:int
    wins:int
    losses:int
    win_rate:Decimal
    net_r:Decimal
    avg_r:Decimal
    max_drawdown_r:Decimal
    profit_factor:Decimal|None

def evaluate_r_multiples(results:list[Decimal])->EvaluationMetrics:
    wins=sum(x>0 for x in results); losses=sum(x<0 for x in results)
    gross_profit=sum((x for x in results if x>0),Decimal("0"))
    gross_loss=abs(sum((x for x in results if x<0),Decimal("0")))
    equity=peak=Decimal("0"); dd=Decimal("0")
    for x in results:
        equity+=x; peak=max(peak,equity); dd=max(dd,peak-equity)
    return EvaluationMetrics(len(results),wins,losses,Decimal(wins)/Decimal(len(results))*100 if results else Decimal("0"),sum(results,Decimal("0")),Decimal(mean(results)) if results else Decimal("0"),dd,gross_profit/gross_loss if gross_loss else None)
