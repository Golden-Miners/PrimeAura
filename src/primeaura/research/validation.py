from dataclasses import dataclass
from decimal import Decimal
from .evaluation import EvaluationMetrics

@dataclass(frozen=True)
class ValidationPolicy:
    min_trades:int=100
    min_profit_factor:Decimal=Decimal("1.20")
    min_net_r:Decimal=Decimal("0")
    max_drawdown_r:Decimal=Decimal("20")
    min_walkforward_folds:int=3
    min_oos_positive_folds:int=2

@dataclass(frozen=True)
class ValidationDecision:
    accepted:bool
    status:str
    reasons:tuple[str,...]

def validate(metrics:EvaluationMetrics,fold_count:int,positive_oos_folds:int=0,policy:ValidationPolicy=ValidationPolicy())->ValidationDecision:
    reasons=[]
    if metrics.trades<policy.min_trades: reasons.append("Insufficient trades")
    if metrics.profit_factor is None or metrics.profit_factor<policy.min_profit_factor: reasons.append("Profit factor below threshold")
    if metrics.net_r<=policy.min_net_r: reasons.append("Non-positive net R")
    if metrics.max_drawdown_r>policy.max_drawdown_r: reasons.append("Maximum drawdown exceeds threshold")
    if fold_count<policy.min_walkforward_folds: reasons.append("Insufficient walk-forward folds")
    if positive_oos_folds<policy.min_oos_positive_folds: reasons.append("Insufficient positive OOS folds")
    return ValidationDecision(not reasons,"VALIDATED" if not reasons else "REJECTED",tuple(reasons))
