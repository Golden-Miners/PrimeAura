from decimal import Decimal
from ..analysis.activation import ActiveZone, LiquiditySweep
from ..analysis.multi_timeframe import MultiTimeframeContext
from ..analysis.smc import FairValueGap, LiquidityPool, StructureBreak
from ..analysis.advanced_smc import OrderBlock
from .models import Signal

BUFFER=Decimal("0.0005")
MIN_RR=Decimal("2.0")

def generate_locked_signal(instrument:str,context:MultiTimeframeContext,direction:str,entry:Decimal,sweeps:list[LiquiditySweep],bos:list[StructureBreak],obs:list[ActiveZone],fvgs:list[ActiveZone],pools:list[LiquidityPool],strategy_id:str="smc-confluence",strategy_version:str="1.0.0") -> Signal|None:
    bullish=direction=="BUY"
    if direction not in {"BUY","SELL"}: return None
    if (context.higher.bias=="BULLISH") != bullish or (context.structure.structure=="BULLISH") != bullish: return None
    bos_kind="BULLISH_BOS" if bullish else "BEARISH_BOS"; sweep_kind="BULLISH_SWEEP" if bullish else "BEARISH_SWEEP"; ob_kind="BULLISH_OB" if bullish else "BEARISH_OB"; fvg_kind="BULLISH_FVG" if bullish else "BEARISH_FVG"
    if not any(x.kind==bos_kind for x in bos): return None
    if not any(x.kind==sweep_kind for x in sweeps): return None
    valid_obs=[x for x in obs if x.kind==ob_kind and x.active]
    valid_fvgs=[x for x in fvgs if x.kind==fvg_kind and x.active]
    if not valid_obs or not valid_fvgs: return None
    ob=max(valid_obs,key=lambda x:x.source_index)
    sl=ob.low*(1-BUFFER) if bullish else ob.high*(1+BUFFER)
    targets=[p.price for p in pools if p.kind==("BUY_SIDE" if bullish else "SELL_SIDE") and ((p.price>entry) if bullish else (p.price<entry))]
    targets=sorted(targets,reverse=not bullish)
    if not targets: return None
    risk=abs(entry-sl)
    if risk<=0: return None
    tp1=targets[0]; rr1=abs(tp1-entry)/risk
    if rr1<MIN_RR: return None
    tp2=targets[1] if len(targets)>1 else None
    rr2=abs(tp2-entry)/risk if tp2 is not None else None
    confidence=Decimal("100") if len(valid_fvgs)>1 else Decimal("85")
    return Signal(instrument=instrument,direction=direction,strategy_id=strategy_id,strategy_version=strategy_version,entry=entry,stop_loss=sl,tp1=tp1,tp2=tp2,rr_tp1=rr1,rr_tp2=rr2,confidence=confidence,reasoning=("H1 bias aligned","M15 structure aligned","Liquidity sweep confirmed",f"{bos_kind} confirmed","Active order block","Active FVG","TP1 selected from opposing liquidity"),risk_factors=("Execution costs and spread are not represented in this live signal contract",))
