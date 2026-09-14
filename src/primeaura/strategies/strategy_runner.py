from dataclasses import dataclass
from typing import Callable
from .research_catalog import research_strategy_catalog

@dataclass(frozen=True)
class StrategyResult:
    strategy_id: str
    status: str
    signal: object | None
    reason: str

StrategyAdapter=Callable[[str,dict],object|None]

class MultiStrategyEngine:
    """Evaluates strategies independently and preserves strategy attribution."""
    def __init__(self, adapters:dict[str,StrategyAdapter]|None=None):
        self.adapters=adapters or {}
        self.catalog={s.strategy_id:s for s in research_strategy_catalog()}
    def evaluate(self,instrument:str,context:dict)->tuple[StrategyResult,...]:
        results=[]
        for sid,spec in self.catalog.items():
            if instrument not in spec.instruments: continue
            adapter=self.adapters.get(sid)
            if adapter is None:
                results.append(StrategyResult(sid,spec.status,None,"Strategy adapter pending implementation/validation")); continue
            try:
                signal=adapter(instrument,context)
                results.append(StrategyResult(sid,spec.status,signal,"Signal generated" if signal is not None else "No setup"))
            except Exception as exc:
                results.append(StrategyResult(sid,spec.status,None,f"Strategy evaluation error: {type(exc).__name__}"))
        return tuple(results)
