from dataclasses import dataclass
from decimal import Decimal
from ..research.evaluation import EvaluationMetrics,evaluate_r_multiples

@dataclass(frozen=True)
class StrategyBenchmark:
    strategy_id:str
    instrument:str
    metrics:EvaluationMetrics
    validation_status:str

def benchmark(strategy_id:str,instrument:str,r_multiples:list[Decimal])->StrategyBenchmark:
    metrics=evaluate_r_multiples(r_multiples)
    status="RESEARCH_ONLY"
    if metrics.trades>=100 and metrics.net_r>0 and metrics.profit_factor is not None and metrics.profit_factor>=Decimal("1.2"):
        status="CANDIDATE_FOR_OOS"
    return StrategyBenchmark(strategy_id,instrument,metrics,status)
