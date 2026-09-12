from dataclasses import dataclass
from decimal import Decimal
from .advanced_smc import OrderBlock
from .smc import FairValueGap, LiquidityPool, StructureBreak

@dataclass(frozen=True)
class Zone:
    kind: str
    low: Decimal
    high: Decimal
    source_index: int

@dataclass(frozen=True)
class ConfluenceResult:
    direction: str
    score: int
    reasons: tuple[str, ...]
    conflicts: tuple[str, ...]


def zones_from_order_blocks(order_blocks: list[OrderBlock]) -> list[Zone]:
    return [Zone("DEMAND" if x.kind=="BULLISH_OB" else "SUPPLY",x.low,x.high,x.index) for x in order_blocks]


def evaluate_confluence(h1_bias: str, m15_structure: str, liquidity: list[LiquidityPool], bos: list[StructureBreak], order_blocks: list[OrderBlock], fvgs: list[FairValueGap]) -> ConfluenceResult:
    """Deterministic first-pass confluence scorer. It never creates an entry price."""
    reasons=[]; conflicts=[]; bull=0; bear=0
    if h1_bias=="BULLISH": bull+=1; reasons.append("H1 bullish bias")
    elif h1_bias=="BEARISH": bear+=1; reasons.append("H1 bearish bias")
    if m15_structure=="BULLISH": bull+=1; reasons.append("M15 bullish structure")
    elif m15_structure=="BEARISH": bear+=1; reasons.append("M15 bearish structure")
    if any(x.kind=="BULLISH_BOS" for x in bos): bull+=1; reasons.append("Bullish BOS")
    if any(x.kind=="BEARISH_BOS" for x in bos): bear+=1; reasons.append("Bearish BOS")
    if any(x.kind=="BULLISH_OB" for x in order_blocks): bull+=1; reasons.append("Bullish order block")
    if any(x.kind=="BEARISH_OB" for x in order_blocks): bear+=1; reasons.append("Bearish order block")
    if any(x.kind=="BULLISH_FVG" for x in fvgs): bull+=1; reasons.append("Bullish FVG")
    if any(x.kind=="BEARISH_FVG" for x in fvgs): bear+=1; reasons.append("Bearish FVG")
    if any(x.kind=="SELL_SIDE" for x in liquidity): bull+=1; reasons.append("Sell-side liquidity present")
    if any(x.kind=="BUY_SIDE" for x in liquidity): bear+=1; reasons.append("Buy-side liquidity present")
    if bull>bear: direction="BUY"; score=round(100*bull/6); 
    elif bear>bull: direction="SELL"; score=round(100*bear/6)
    else: direction="NO_SIGNAL"; score=0
    if bull and bear: conflicts.append(f"Opposing evidence: bullish={bull}, bearish={bear}")
    return ConfluenceResult(direction, min(score,100), tuple(reasons), tuple(conflicts))
