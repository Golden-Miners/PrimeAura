from dataclasses import dataclass
from datetime import datetime,timezone
from ..data.validator import validate_bars
from .config import ScanConfig

@dataclass(frozen=True)
class ScanResult:
    instrument: str
    timestamp: datetime
    data_valid: bool
    signal: object | None
    reason: str

class MarketScanner:
    """Signal-only scanner. It never exposes or calls any trading/order API."""
    def __init__(self,provider,config:ScanConfig=ScanConfig()): self.provider=provider; self.config=config
    def scan_once(self,now:datetime|None=None):
        now=now or datetime.now(timezone.utc); results=[]
        for instrument in self.config.instruments:
            bars_by_tf={}
            valid=True
            for tf in self.config.timeframes:
                bars=self.provider.recent(instrument,tf,self.config.lookback_bars)
                report=validate_bars(bars)
                if not report.valid: valid=False
                bars_by_tf[tf]=bars
            results.append(ScanResult(instrument,now,valid,None,"Data quality failed" if not valid else "Analysis hook ready"))
        return tuple(results)
