from datetime import datetime
from decimal import Decimal
from ..signals.models import Signal
from ..strategies.breakout_retest import breakout_retest
from ..strategies.pullback_reversion import trend_pullback, mean_reversion
from ..strategies.rule_based import momentum_continuation, volatility_breakout
from ..strategies.additional import ema_crossover, liquidity_sweep_ifvg
from ..scanner.pipeline import generate_from_bars

STRATEGIES={
    "smc-confluence": None,
    "trend-pullback": trend_pullback,
    "liquidity-sweep-ifvg": liquidity_sweep_ifvg,
    "breakout-retest": breakout_retest,
    "ema-crossover": ema_crossover,
    "momentum": momentum_continuation,
    "mean-reversion": mean_reversion,
    "volatility-breakout": volatility_breakout,
}

class StrategyScan:
    def __init__(self,strategy_id,status,signal=None,reason=""):
        self.strategy_id=strategy_id; self.status=status; self.signal=signal; self.reason=reason

def _series(bars):
    return {"close":[b.close for b in bars],"high":[b.high for b in bars],"low":[b.low for b in bars]}

def _to_signal(raw,instrument,timestamp):
    if raw is None: return None
    rr=Decimal(str(raw["rr"]))
    return Signal(instrument=instrument,timestamp=timestamp,direction=raw["direction"],strategy_id=raw["strategy_id"],strategy_version="0.1.0",entry=Decimal(str(raw["entry"])),stop_loss=Decimal(str(raw["stop_loss"])),tp1=Decimal(str(raw["tp1"])),rr_tp1=rr,confidence=Decimal("70"),reasoning=tuple(raw.get("reasoning",())),risk_factors=("Research strategy; validate out-of-sample before relying on it",))

def evaluate_strategies(instrument:str,bars_by_tf:dict[str,list],selected:tuple[str,...]|None=None):
    selected=selected or tuple(STRATEGIES)
    detected_at=datetime.now().astimezone()
    results=[]; signals=[]
    if "smc-confluence" in selected:
        try:
            smc=generate_from_bars(instrument,bars_by_tf)
            if smc:
                signals.extend(smc); results.extend(StrategyScan("smc-confluence","FORMALIZED",s,"Full MTF SMC confluence") for s in smc)
            else:
                results.append(StrategyScan("smc-confluence","FORMALIZED",None,"No complete SMC confluence setup"))
        except Exception as exc:
            results.append(StrategyScan("smc-confluence","ERROR",None,f"{type(exc).__name__}: {exc}"))
    series=_series(bars_by_tf["M15"])
    for sid in selected:
        if sid=="smc-confluence": continue
        fn=STRATEGIES.get(sid)
        if fn is None:
            results.append(StrategyScan(sid,"UNAVAILABLE",None,"No strategy adapter")); continue
        try:
            raw=fn(instrument,series)
            sig=_to_signal(raw,instrument,detected_at)
            results.append(StrategyScan(sid,"RESEARCH_ONLY",sig,"Signal generated" if sig else "No setup"))
            if sig: signals.append(sig)
        except Exception as exc:
            results.append(StrategyScan(sid,"ERROR",None,f"{type(exc).__name__}: {exc}"))
    return tuple(signals),tuple(results)
