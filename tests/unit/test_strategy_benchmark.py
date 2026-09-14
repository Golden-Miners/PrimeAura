from decimal import Decimal
from primeaura.research.strategy_benchmark import benchmark

def test_small_sample_remains_research_only():
 r=benchmark("momentum","XAUUSD",[Decimal("1"),Decimal("-1")]); assert r.validation_status=="RESEARCH_ONLY"

def test_candidate_requires_large_positive_sample():
 r=benchmark("momentum","XAUUSD",[Decimal("1.5")]*100); assert r.validation_status=="CANDIDATE_FOR_OOS"
