from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Callable

@dataclass(frozen=True)
class ReplaySignal:
    strategy_id:str
    instrument:str
    detected_at:datetime
    direction:str
    entry:Decimal
    stop_loss:Decimal
    tp1:Decimal

@dataclass(frozen=True)
class ReplayResult:
    strategy_id:str
    instrument:str
    signals:tuple[ReplaySignal,...]

class HistoricalReplay:
    """Candle-by-candle replay. Strategy receives only candles available at that point."""
    def run(self,instrument:str,strategy_id:str,bars:list,adapter:Callable)->ReplayResult:
        signals=[]
        for i in range(len(bars)):
            context=bars[:i+1]
            if len(context)<30: continue
            result=adapter(instrument,{"close":[b.close for b in context],"high":[b.high for b in context],"low":[b.low for b in context]})
            if not result: continue
            signals.append(ReplaySignal(strategy_id,instrument,bars[i].timestamp,result["direction"],result["entry"],result["stop_loss"],result["tp1"]))
        return ReplayResult(strategy_id,instrument,tuple(signals))
