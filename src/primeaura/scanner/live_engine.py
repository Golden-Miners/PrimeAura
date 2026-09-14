from dataclasses import dataclass
from datetime import datetime
from ..scanner.clock import local_now
from ..strategies.breakout_retest import breakout_retest
from ..strategies.pullback_reversion import trend_pullback,mean_reversion
from ..strategies.rule_based import momentum_continuation,volatility_breakout
from ..strategies.smc_v1 import signal as smc_signal

@dataclass(frozen=True)
class ScanSignal:
    instrument:str
    strategy_id:str
    signal:object
    detected_at:datetime

STRATEGY_FUNCTIONS={"trend-pullback":trend_pullback,"breakout-retest":breakout_retest,"momentum":momentum_continuation,"mean-reversion":mean_reversion,"volatility-breakout":None}

class LiveSignalEngine:
    """Read-only scanner. It evaluates configured strategies independently."""
    def __init__(self,provider,instruments=("XAUUSD","XAGUSD")): self.provider=provider; self.instruments=tuple(instruments)
    def scan_instrument(self,instrument:str)->tuple[ScanSignal,...]:
        context={}
        for tf in ("H1","M15","M5"):
            context[tf]=self.provider.recent(instrument,tf,500)
        # Common rule strategies consume the selected timeframe series.
        series={"close":[b.close for b in context["M15"]],"high":[b.high for b in context["M15"]],"low":[b.low for b in context["M15"]]}
        results=[]
        for sid,fn in STRATEGY_FUNCTIONS.items():
            if fn is None: continue
            sig=fn(instrument,series)
            if sig is not None: results.append(ScanSignal(instrument,sid,sig,local_now()))
        return tuple(results)
    def scan_all(self):
        return tuple(x for i in self.instruments for x in self.scan_instrument(i))
