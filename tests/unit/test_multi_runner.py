from decimal import Decimal
from primeaura.research.multi_runner import MultiStrategyResearchRunner

def test_runner_returns_independent_strategy_rows():
 bars=[]
 report=MultiStrategyResearchRunner().run("XAUUSD",bars)
 assert report.runs==()
