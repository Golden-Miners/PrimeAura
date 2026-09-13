from primeaura.research.discovery import StrategyDiscoveryAgent

class M:
    def propose(self,ctx):
        return [{"strategy_id":"gold-momentum","version":"0.1","name":"Gold Momentum","instruments":["XAUUSD","BTCUSD"],"timeframes":["M15","D1"],"rules":["close above EMA"]}]

def test_discovery_filters_unsupported_scope():
    x=StrategyDiscoveryAgent(M()).discover("research")
    assert len(x)==1 and x[0].metadata.instruments==("XAUUSD",) and x[0].metadata.timeframes==("M15",)
