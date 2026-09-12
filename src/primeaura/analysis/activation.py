from dataclasses import dataclass
from decimal import Decimal
from ..data.models import OHLCVBar
from .advanced_smc import OrderBlock
from .smc import FairValueGap, LiquidityPool

@dataclass(frozen=True)
class LiquiditySweep:
    kind: str
    index: int
    pool_price: Decimal
    close: Decimal

@dataclass(frozen=True)
class ActiveZone:
    kind: str
    low: Decimal
    high: Decimal
    source_index: int
    active: bool
    invalidated_at: int | None = None

def detect_liquidity_sweeps(bars:list[OHLCVBar], pools:list[LiquidityPool]) -> list[LiquiditySweep]:
    out=[]
    for p in pools:
        for i in range(p.last_index+1,len(bars)):
            b=bars[i]
            if p.kind=="SELL_SIDE" and b.low<p.price and b.close>p.price:
                out.append(LiquiditySweep("BULLISH_SWEEP",i,p.price,b.close)); break
            if p.kind=="BUY_SIDE" and b.high>p.price and b.close<p.price:
                out.append(LiquiditySweep("BEARISH_SWEEP",i,p.price,b.close)); break
    return out

def active_order_blocks(bars:list[OHLCVBar], blocks:list[OrderBlock]) -> list[ActiveZone]:
    out=[]
    for ob in blocks:
        invalid=None
        for i in range(ob.bos_index+1,len(bars)):
            if ob.kind=="BULLISH_OB" and bars[i].close<ob.low: invalid=i; break
            if ob.kind=="BEARISH_OB" and bars[i].close>ob.high: invalid=i; break
        out.append(ActiveZone(ob.kind,ob.low,ob.high,ob.index,invalid is None,invalid))
    return out

def active_fvgs(bars:list[OHLCVBar], fvgs:list[FairValueGap]) -> list[ActiveZone]:
    out=[]
    for f in fvgs:
        invalid=None
        for i in range(f.index+1,len(bars)):
            if f.kind=="BULLISH_FVG" and bars[i].close<f.low: invalid=i; break
            if f.kind=="BEARISH_FVG" and bars[i].close>f.high: invalid=i; break
        out.append(ActiveZone(f.kind,f.low,f.high,f.index,invalid is None,invalid))
    return out
