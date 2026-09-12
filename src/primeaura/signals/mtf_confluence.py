from dataclasses import dataclass
from decimal import Decimal
from ..analysis.multi_timeframe import MultiTimeframeContext
from ..analysis.smc import LiquidityPool, StructureBreak, FairValueGap
from ..analysis.advanced_smc import OrderBlock
from .engine import build_signal
from .models import Signal

@dataclass(frozen=True)
class ConfluenceEvidence:
    direction: str
    reasons: tuple[str,...]
    missing: tuple[str,...]

def evaluate_locked_confluence(context: MultiTimeframeContext, direction: str, liquidity:list[LiquidityPool], bos:list[StructureBreak], order_blocks:list[OrderBlock], fvgs:list[FairValueGap]) -> ConfluenceEvidence:
    required=[]; missing=[]
    bullish=direction=="BUY"
    if (context.higher.bias=="BULLISH") != bullish: missing.append("H1 bias")
    if (context.structure.structure=="BULLISH") != bullish: missing.append("M15 structure")
    required_bos="BULLISH_BOS" if bullish else "BEARISH_BOS"
    if not any(x.kind==required_bos for x in bos): missing.append("confirmed BOS")
    ob_kind="BULLISH_OB" if bullish else "BEARISH_OB"
    if not any(x.kind==ob_kind for x in order_blocks): missing.append("active order block")
    fvg_kind="BULLISH_FVG" if bullish else "BEARISH_FVG"
    if not any(x.kind==fvg_kind for x in fvgs): missing.append("active FVG")
    liq_kind="SELL_SIDE" if bullish else "BUY_SIDE"
    if not any(x.kind==liq_kind for x in liquidity): missing.append("liquidity sweep/evidence")
    reasons=["H1 bias aligned","M15 structure aligned","confirmed BOS","active order block","active FVG","required liquidity evidence"]
    return ConfluenceEvidence(direction,tuple(reasons if not missing else [x for x in reasons if x not in missing]),tuple(missing))
