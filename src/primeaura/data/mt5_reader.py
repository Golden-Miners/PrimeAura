from datetime import datetime,timezone
from decimal import Decimal
from importlib import import_module
from ..data.models import OHLCVBar,MarketSnapshot

_TIMEFRAMES={"M1":"TIMEFRAME_M1","M5":"TIMEFRAME_M5","M15":"TIMEFRAME_M15","M30":"TIMEFRAME_M30","H1":"TIMEFRAME_H1","H4":"TIMEFRAME_H4","D1":"TIMEFRAME_D1"}

class MT5ReadOnly:
    """Read-only MT5 market-data adapter. No order API is exposed."""
    def __init__(self, mt5_module=None):
        self.mt5=mt5_module or import_module("MetaTrader5")

    def initialize(self):
        if not self.mt5.initialize():
            raise RuntimeError(f"MT5 initialize failed: {self.mt5.last_error()}")

    def shutdown(self):
        self.mt5.shutdown()

    def bars(self,instrument:str,timeframe:str,count:int=500)->MarketSnapshot:
        if timeframe not in _TIMEFRAMES: raise ValueError(f"Unsupported timeframe: {timeframe}")
        if count<1: raise ValueError("count must be positive")
        if not self.mt5.symbol_select(instrument,True):
            raise RuntimeError(f"Unable to select MT5 symbol: {instrument}")
        rows=self.mt5.copy_rates_from_pos(instrument,getattr(self.mt5,_TIMEFRAMES[timeframe]),0,count)
        if rows is None: raise RuntimeError(f"MT5 rates request failed: {self.mt5.last_error()}")
        parsed=tuple(OHLCVBar(instrument=instrument,timeframe=timeframe,timestamp=datetime.fromtimestamp(int(r["time"]),tz=timezone.utc),open=Decimal(str(r["open"])),high=Decimal(str(r["high"])),low=Decimal(str(r["low"])),close=Decimal(str(r["close"])),volume=Decimal(str(r["tick_volume"])) if "tick_volume" in r.dtype.names else None) for r in rows)
        return MarketSnapshot(instrument=instrument,timeframe=timeframe,bars=parsed,source="MT5",retrieved_at=datetime.now(timezone.utc))
