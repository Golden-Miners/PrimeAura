from dataclasses import dataclass
from ..strategies.research_catalog import research_strategy_catalog

@dataclass(frozen=True)
class StrategyEvaluation:
    strategy_id:str
    status:str
    signal:object|None
    reason:str

class StrategyRunner:
    """Runs registered strategies independently; candidates never become live signals merely by being catalogued."""
    def __init__(self, strategies=None): self.strategies=tuple(strategies or research_strategy_catalog())
    def evaluate(self,instrument:str, market_context:dict)->tuple[StrategyEvaluation,...]:
        out=[]
        for s in self.strategies:
            if instrument not in s.instruments: continue
            out.append(StrategyEvaluation(s.strategy_id,s.status,None,"Strategy adapter not implemented/validated yet"))
        return tuple(out)
