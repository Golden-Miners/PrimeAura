from dataclasses import dataclass
from typing import Protocol
from .research_agent import StrategyCandidate
from .strategy_registry import StrategyMetadata

class StrategyProposalModel(Protocol):
    def propose(self, research_context:str)->list[dict]: ...

@dataclass(frozen=True)
class DiscoveryPolicy:
    allowed_instruments:tuple[str,...]=("XAUUSD","XAGUSD")
    allowed_timeframes:tuple[str,...]=("H1","M15","M5")
    max_candidates_per_run:int=10

class StrategyDiscoveryAgent:
    """Turns LLM research proposals into strictly typed candidates; it never validates profitability."""
    def __init__(self, model:StrategyProposalModel, policy:DiscoveryPolicy=DiscoveryPolicy()):
        self.model=model; self.policy=policy

    def discover(self, research_context:str)->tuple[StrategyCandidate,...]:
        raw=self.model.propose(research_context)[:self.policy.max_candidates_per_run]
        out=[]
        for item in raw:
            instruments=tuple(x for x in item.get("instruments",()) if x in self.policy.allowed_instruments)
            timeframes=tuple(x for x in item.get("timeframes",()) if x in self.policy.allowed_timeframes)
            if not instruments or not timeframes or not item.get("rules"): continue
            meta=StrategyMetadata(str(item["strategy_id"]),str(item["version"]),str(item["name"]),str(item.get("description","")),instruments,timeframes)
            out.append(StrategyCandidate(meta,str(item.get("source","LLM research")),str(item.get("hypothesis","")),tuple(map(str,item["rules"]))))
        return tuple(out)
