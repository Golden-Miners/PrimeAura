from decimal import Decimal
from primeaura.research.self_improvement import SelfImprovementAgent
from primeaura.research.strategy_registry import StrategyMetadata

def test_failed_validation_cannot_promote():
 a=SelfImprovementAgent(); p=StrategyMetadata("x","1","X","",("XAUUSD",),("M15",)); e=a.propose(p,"increase displacement","exp1")
 d=a.decide(e,Decimal("5"),Decimal("20"),False); assert not d.accepted

def test_improvement_requires_strict_gain():
 a=SelfImprovementAgent(); p=StrategyMetadata("x","1","X","",("XAUUSD",),("M15",)); e=a.propose(p,"change","exp2")
 assert a.decide(e,Decimal("5"),Decimal("5"),True).accepted is False
 assert a.decide(e,Decimal("5"),Decimal("6"),True).accepted is True
