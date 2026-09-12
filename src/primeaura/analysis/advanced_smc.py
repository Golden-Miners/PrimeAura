from dataclasses import dataclass
from decimal import Decimal
from ..data.models import OHLCVBar
from .structure import SwingPoint
from .indicators import atr

@dataclass(frozen=True)
class ChangeOfCharacter:
    kind: str
    index: int
    level: Decimal

@dataclass(frozen=True)
class OrderBlock:
    kind: str
    index: int
    low: Decimal
    high: Decimal
    bos_index: int


def detect_choch(bars: list[OHLCVBar], swings: list[SwingPoint]) -> list[ChangeOfCharacter]:
    """Detect CHOCH from confirmed swing sequence and body-close breaks.

    State is inferred from the latest confirmed alternating swing structure.
    A bullish CHOCH requires bearish structure and a close above the latest lower high;
    bearish CHOCH is the inverse.
    """
    highs=[s for s in swings if s.kind=="HIGH"]
    lows=[s for s in swings if s.kind=="LOW"]
    out=[]
    if len(highs)>=2 and len(lows)>=2:
        bearish = highs[-1].price < highs[-2].price and lows[-1].price < lows[-2].price
        bullish = highs[-1].price > highs[-2].price and lows[-1].price > lows[-2].price
        if bearish:
            level=highs[-1]
            for i in range(level.index+1,len(bars)):
                if bars[i].close>level.price:
                    out.append(ChangeOfCharacter("BULLISH_CHOCH",i,level.price)); break
        elif bullish:
            level=lows[-1]
            for i in range(level.index+1,len(bars)):
                if bars[i].close<level.price:
                    out.append(ChangeOfCharacter("BEARISH_CHOCH",i,level.price)); break
    return out


def detect_order_blocks(bars: list[OHLCVBar], bos_indices: list[int], atr_period: int=14, displacement_multiple: Decimal=Decimal("1.5")) -> list[OrderBlock]:
    """Find the last opposite candle before a qualifying displacement/BOS."""
    out=[]
    if len(bars)<atr_period: return out
    for bos_i in bos_indices:
        if bos_i<=0 or bos_i>=len(bars): continue
        window=bars[max(0,bos_i-atr_period):bos_i+1]
        a=atr([x.high for x in window],[x.low for x in window],[x.close for x in window],min(atr_period,len(window)))
        move=abs(bars[bos_i].close-bars[bos_i].open)
        if move < displacement_multiple*a: continue
        direction="BULLISH_OB" if bars[bos_i].close>bars[bos_i].open else "BEARISH_OB"
        target=direction=="BULLISH_OB"
        for j in range(bos_i-1,-1,-1):
            opposite = bars[j].close<bars[j].open if target else bars[j].close>bars[j].open
            if opposite:
                out.append(OrderBlock(direction,j,bars[j].low,bars[j].high,bos_i)); break
    return out
