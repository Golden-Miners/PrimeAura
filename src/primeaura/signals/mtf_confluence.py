from dataclasses import dataclass
from ..analysis.multi_timeframe import MultiTimeframeContext
from ..analysis.smc import LiquidityPool, StructureBreak
from ..analysis.activation import LiquiditySweep, ActiveZone

@dataclass(frozen=True)
class ConfluenceEvidence:
    direction: str
    reasons: tuple[str,...]
    missing: tuple[str,...]

def evaluate_locked_confluence(
    context: MultiTimeframeContext,
    direction: str,
    liquidity: list[LiquidityPool],
    sweeps: list[LiquiditySweep],
    order_blocks: list[ActiveZone],
    fvgs: list[ActiveZone],
) -> ConfluenceEvidence:
    """Apply the locked PrimeAura confluence gate using only active evidence."""
    missing = []
    bullish = direction == "BUY"

    if (context.higher.bias == "BULLISH") != bullish:
        missing.append("H1 bias")
    if (context.structure.structure == "BULLISH") != bullish:
        missing.append("M15 structure")

    required_bos = "BULLISH_BOS" if bullish else "BEARISH_BOS"
    if not any(x.kind == required_bos for x in context.structure.breaks):
        missing.append("confirmed BOS")

    ob_kind = "BULLISH_OB" if bullish else "BEARISH_OB"
    if not any(x.kind == ob_kind and x.active for x in order_blocks):
        missing.append("active order block")

    fvg_kind = "BULLISH_FVG" if bullish else "BEARISH_FVG"
    if not any(x.kind == fvg_kind and x.active for x in fvgs):
        missing.append("active FVG")

    sweep_kind = "BULLISH_SWEEP" if bullish else "BEARISH_SWEEP"
    if not any(x.kind == sweep_kind for x in sweeps):
        missing.append("liquidity sweep")

    reasons = (
        "H1 bias aligned",
        "M15 structure aligned",
        "confirmed BOS",
        "active order block",
        "active FVG",
        "liquidity sweep confirmed",
    )
    return ConfluenceEvidence(
        direction,
        tuple(x for x in reasons if x.lower().replace(" ", "_") not in set()),
        tuple(missing),
    )
