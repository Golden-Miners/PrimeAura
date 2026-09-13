from dataclasses import dataclass
from decimal import Decimal
from ..data.models import OHLCVBar

@dataclass(frozen=True)
class ExecutionConfig:
    spread: Decimal = Decimal("0")
    slippage: Decimal = Decimal("0")
    ambiguous_policy: str = "CONSERVATIVE"

@dataclass(frozen=True)
class Outcome:
    exit_price: Decimal
    reason: str

def simulate_exit(entry:Decimal,direction:str,stop:Decimal,tp:Decimal,bars:list[OHLCVBar],config:ExecutionConfig=ExecutionConfig())->Outcome|None:
    if direction not in {"BUY","SELL"}: raise ValueError("direction must be BUY or SELL")
    for b in bars:
        if direction=="BUY":
            stop_hit=b.low<=stop; tp_hit=b.high>=tp
        else:
            stop_hit=b.high>=stop; tp_hit=b.low<=tp
        if stop_hit and tp_hit:
            if config.ambiguous_policy=="OPTIMISTIC":
                return Outcome(tp,"TP_AND_SL_SAME_BAR_OPTIMISTIC")
            return Outcome(stop,"TP_AND_SL_SAME_BAR_CONSERVATIVE")
        if stop_hit: return Outcome(stop,"SL")
        if tp_hit: return Outcome(tp,"TP")
    return None
