from dataclasses import dataclass
from .multi_runner import MultiStrategyResearchRunner,MultiResearchReport
from ..data.mt5_history import MT5HistoryProvider,HistoryRequest

@dataclass(frozen=True)
class InstrumentResearch:
    instrument:str
    timeframe:str
    bars:int
    report:MultiResearchReport

class MT5ResearchRunner:
    """Read-only research orchestration over MT5 history."""
    def __init__(self,provider:MT5HistoryProvider,runner=None): self.provider=provider; self.runner=runner or MultiStrategyResearchRunner()
    def run(self,instrument:str,timeframe:str="M15",bars:int=5000):
        raw=self.provider.history(HistoryRequest(instrument,timeframe,bars))
        # Convert provider dictionaries to lightweight candle objects expected by strategies.
        from types import SimpleNamespace
        candles=tuple(SimpleNamespace(**x) for x in raw)
        return InstrumentResearch(instrument,timeframe,len(candles),self.runner.run(instrument,candles))
