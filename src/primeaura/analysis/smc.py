from dataclasses import dataclass
from decimal import Decimal
from .structure import SwingPoint
from ..data.models import OHLCVBar

@dataclass(frozen=True)
class LiquidityPool:
    kind: str
    price: Decimal
    first_index: int
    last_index: int
    touches: int

@dataclass(frozen=True)
class StructureBreak:
    kind: str
    index: int
    level: Decimal
    swing_index: int

@dataclass(frozen=True)
class FairValueGap:
    kind: str
    index: int
    low: Decimal
    high: Decimal


def find_equal_levels(bars: list[OHLCVBar], swings: list[SwingPoint], tolerance_pct: Decimal = Decimal("0.001"), lookback: int = 50, min_touches: int = 2) -> list[LiquidityPool]:
    """Find equal swing highs/lows within tolerance. Defaults implement the locked 0.10%/50-bar rule."""
    if not (Decimal("0") < tolerance_pct < Decimal("1")): raise ValueError("tolerance_pct must be between 0 and 1")
    recent=[s for s in swings if s.index >= max(0,len(bars)-lookback)]
    pools=[]
    for kind in ("HIGH","LOW"):
        same=[s for s in recent if s.kind==kind]
        used=set()
        for i,s in enumerate(same):
            if i in used: continue
            cluster=[s]
            for j,t in enumerate(same[i+1:],i+1):
                if abs(t.price-s.price)/s.price <= tolerance_pct: cluster.append(t); used.add(j)
            if len(cluster)>=min_touches:
                pools.append(LiquidityPool("BUY_SIDE" if kind=="HIGH" else "SELL_SIDE",sum(x.price for x in cluster)/Decimal(len(cluster)),cluster[0].index,cluster[-1].index,len(cluster)))
    return pools


def detect_bos(bars: list[OHLCVBar], swings: list[SwingPoint]) -> list[StructureBreak]:
    """BOS requires a candle body close beyond the latest confirmed swing."""
    out=[]
    for s in swings:
        for i in range(s.index+1,len(bars)):
            if s.kind=="HIGH" and bars[i].close>s.price: out.append(StructureBreak("BULLISH_BOS",i,s.price,s.index)); break
            if s.kind=="LOW" and bars[i].close<s.price: out.append(StructureBreak("BEARISH_BOS",i,s.price,s.index)); break
    return out


def detect_fvg(bars: list[OHLCVBar], min_size_pct: Decimal = Decimal("0.001")) -> list[FairValueGap]:
    """Three-candle gap: C1 high < C3 low (bullish) or C1 low > C3 high (bearish)."""
    out=[]
    for i in range(2,len(bars)):
        a,c=bars[i-2],bars[i]
        if a.high<c.low and (c.low-a.high)/c.close>=min_size_pct: out.append(FairValueGap("BULLISH_FVG",i,a.high,c.low))
        if a.low>c.high and (a.low-c.high)/c.close>=min_size_pct: out.append(FairValueGap("BEARISH_FVG",i,c.high,a.low))
    return out
