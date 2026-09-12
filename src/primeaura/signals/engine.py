from decimal import Decimal
from ..analysis.advanced_smc import OrderBlock
from ..analysis.smc import FairValueGap,LiquidityPool
from .models import Signal

def build_signal(instrument:str,direction:str,strategy_id:str,strategy_version:str,entry:Decimal,ob:OrderBlock,opposing: list[LiquidityPool],fvg: FairValueGap|None,confidence:Decimal=Decimal("0")) -> Signal|None:
    if direction=="BUY" and ob.kind!="BULLISH_OB": return None
    if direction=="SELL" and ob.kind!="BEARISH_OB": return None
    if not opposing: return None
    if direction=="BUY":
        sl=ob.low*(Decimal("1")-Decimal("0.0005")); targets=sorted([x.price for x in opposing if x.kind=="BUY_SIDE" and x.price>entry])
    else:
        sl=ob.high*(Decimal("1")+Decimal("0.0005")); targets=sorted([x.price for x in opposing if x.kind=="SELL_SIDE" and x.price<entry],reverse=True)
    if not targets: return None
    tp1=targets[0]; risk=abs(entry-sl)
    rr1=abs(tp1-entry)/risk if risk else Decimal("0")
    if rr1<Decimal("2"): return None
    tp2=targets[1] if len(targets)>1 else None
    rr2=abs(tp2-entry)/risk if tp2 is not None else None
    reasons=(f"{direction} signal from {strategy_id} v{strategy_version}",f"Active {ob.kind}",f"Entry {entry}",f"TP1 is nearest opposing liquidity", "Valid FVG present" if fvg else "No FVG evidence supplied")
    risks=("Signal requires live validation before use",)
    return Signal(instrument=instrument,direction=direction,strategy_id=strategy_id,strategy_version=strategy_version,entry=entry,stop_loss=sl,tp1=tp1,tp2=tp2,rr_tp1=rr1,rr_tp2=rr2,confidence=confidence,reasoning=reasons,risk_factors=risks)
