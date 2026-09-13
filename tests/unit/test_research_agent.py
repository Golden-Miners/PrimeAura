from primeaura.research.research_agent import ResearchAgent,StrategyCandidate
from primeaura.research.strategy_registry import StrategyMetadata,StrategyRegistry

def c(rules=("close above high",)):
 return StrategyCandidate(StrategyMetadata("candidate","0.1","Candidate","test",("XAUUSD",),("M15",)),"manual","test",rules)
def test_candidate_requires_explicit_rules():
 a=ResearchAgent(StrategyRegistry())
 assert a.submit_candidate(c()).validation_status=="UNTESTED"
 assert a.admissible_for_backtest(c())
