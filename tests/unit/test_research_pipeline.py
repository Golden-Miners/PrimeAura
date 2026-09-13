from decimal import Decimal
from primeaura.research.research_pipeline import ResearchPipeline
from primeaura.research.research_agent import StrategyCandidate
from primeaura.research.strategy_registry import StrategyMetadata
from primeaura.research.validation import ValidationPolicy

def test_pipeline_returns_a_decision():
 c=StrategyCandidate(StrategyMetadata("x","1","X","",("XAUUSD",),("M15",)),"test","h",("rule",))
 class S:
  def fit(self,b): return self
  def signal(self,b,i): return None
 r=ResearchPipeline(ValidationPolicy(min_trades=2,min_walkforward_folds=1)).evaluate(c,S(),[])
 assert r.decision.status=="REJECTED"
