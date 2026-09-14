from dataclasses import dataclass
from datetime import datetime,timezone
from decimal import Decimal

@dataclass(frozen=True)
class HistoryRequest:
    instrument:str
    timeframe:str
    bars:int=5000

class MT5HistoryProvider:
    """Read-only MT5 historical provider. No order/trading methods are exposed."""
    def __init__(self,mt5,resolver): self.mt5=mt5; self.resolver=resolver
    def history(self,request:HistoryRequest):
        symbol=self.resolver.resolve(request.instrument)
        tf=getattr(self.mt5,f"TIMEFRAME_{request.timeframe}",None)
        if tf is None: raise ValueError(f"Unsupported timeframe: {request.timeframe}")
        rows=self.mt5.copy_rates_from_pos(symbol,tf,0,request.bars)
        if rows is None: raise RuntimeError(f"MT5 returned no history for {symbol}/{request.timeframe}")
        return tuple({"instrument":request.instrument,"timeframe":request.timeframe,"timestamp":datetime.fromtimestamp(int(x["time"]),tz=timezone.utc),"open":Decimal(str(x["open"])),"high":Decimal(str(x["high"])),"low":Decimal(str(x["low"])),"close":Decimal(str(x["close"])),"volume":int(x["tick_volume"])} for x in rows)
