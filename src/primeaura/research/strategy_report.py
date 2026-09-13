from dataclasses import dataclass
from decimal import Decimal
from .evaluation import EvaluationMetrics

@dataclass(frozen=True)
class StrategyReport:
    strategy_id:str
    version:str
    instrument:str
    metrics:EvaluationMetrics
    research_status:str
    notes:tuple[str,...]=()

def rank_reports(reports:list[StrategyReport])->tuple[StrategyReport,...]:
    return tuple(sorted(reports,key=lambda r:(r.metrics.net_r,r.metrics.profit_factor or Decimal("-1"),r.metrics.max_drawdown_r),reverse=True))
