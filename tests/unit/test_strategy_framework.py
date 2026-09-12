from decimal import Decimal
import pytest
from primeaura.strategies.governance import promote
from primeaura.strategies.models import StrategyDefinition
from primeaura.strategies.registry import StrategyRegistry

def strategy(): return StrategyDefinition(strategy_id="smc-001",name="SMC Test",version="1.0",description="test",minimum_rr=Decimal("2"))

def test_registry_versioning():
    r=StrategyRegistry(); s=strategy(); r.register(s); assert r.get("smc-001","1.0")==s

def test_duplicate_rejected():
    r=StrategyRegistry(); s=strategy(); r.register(s)
    with pytest.raises(ValueError): r.register(s)

def test_governance_requires_ordered_validation():
    s=strategy(); s=promote(s,"FORMALIZED")
    with pytest.raises(ValueError): promote(s,"ACTIVE")
