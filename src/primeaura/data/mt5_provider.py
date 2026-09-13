from datetime import datetime
from decimal import Decimal
from ..data.models import OHLCVBar

class MT5MarketDataProvider:
    """Read-only MetaTrader 5 historical OHLCV adapter. Never sends orders."""
    def __init__(self, symbol_aliases:dict[str,str]|None=None):
        self.symbol_aliases=symbol_aliases or {"XAUUSD":"XAUUSD","XAGUSD":"XAGUSD"}
        self._mt5=None

    def connect(self)->None:
        import MetaTrader5 as mt5
        if not mt5.initialize(): raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
        self._mt5=mt5

    def shutdown(self)->None:
        if self._mt5 is not None: self._mt5.shutdown(); self._mt5=None

    def history(self,instrument:str,timeframe:str,start:datetime,end:datetime)->list[OHLCVBar]:
        if self._mt5 is None: raise RuntimeError("Call connect() first")
        symbol=self.symbol_aliases.get(instrument,instrument)
        tf=getattr(self._mt5,f"TIMEFRAME_{timeframe}",None)
        if tf is None: raise ValueError(f"Unsupported MT5 timeframe: {timeframe}")
        import pandas as pd
        rates=self._mt5.copy_rates_range(symbol,tf,start,end)
        if rates is None: raise RuntimeError(f"MT5 history failed: {self._mt5.last_error()}")
        bars=[]
        for row in rates:
            dt=pd.Timestamp(int(row["time"]),unit="s",tz="UTC").to_pydatetime()
            bars.append(OHLCVBar(instrument=instrument,timeframe=timeframe,timestamp=dt,open=Decimal(str(row["open"])),high=Decimal(str(row["high"])),low=Decimal(str(row["low"])),close=Decimal(str(row["close"])),volume=Decimal(str(row.get("tick_volume",0)))))
        return bars
