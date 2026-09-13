from dataclasses import dataclass
from typing import Protocol
from ..data.models import OHLCVBar

@dataclass(frozen=True)
class StrategyMetadata:
    strategy_id:str
    version:str
    name:str
    description:str
    instruments:tuple[str,...]
    timeframes:tuple[str,...]

class ResearchStrategy(Protocol):
    metadata:StrategyMetadata
    def fit(self,bars:list[OHLCVBar]): ...
    def signal(self,bars:list[OHLCVBar],index:int): ...

class StrategyRegistry:
    def __init__(self): self._strategies={}
    def register(self,strategy:ResearchStrategy):
        key=(strategy.metadata.strategy_id,strategy.metadata.version)
        if key in self._strategies: raise ValueError(f"Strategy already registered: {key}")
        self._strategies[key]=strategy
    def get(self,strategy_id:str,version:str): return self._strategies[(strategy_id,version)]
    def all(self): return tuple(self._strategies.values())
