from primeaura.research.strategy_registry import StrategyRegistry,StrategyMetadata

class S:
    def __init__(self,i,v): self.metadata=StrategyMetadata(i,v,i,"",("XAUUSD",),("M15",))
    def fit(self,b): return self
    def signal(self,b,i): return None

def test_registry_versions_are_distinct():
 r=StrategyRegistry(); a=S("smc","1.0"); b=S("smc","2.0"); r.register(a); r.register(b)
 assert r.get("smc","1.0") is a and r.get("smc","2.0") is b
