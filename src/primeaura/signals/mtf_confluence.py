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
    bos: list[StructureBreak],
    sweeps: list[LiquiditySweep],
    order_blocks: list[ActiveZone],
    fvgs: list[ActiveZone],
) -> ConfluenceEvidence:
    """Apply the locked PrimeAura confluence gate using current active evidence."""
    missing = []
    bullish = direction == "BUY"

    if (context.higher.bias == "BULLISH") != bullish:
        missing.append("H1 bias")
    if (context.structure.structure == "BULLISH") != bullish:
        missing.append("M15 structure")

    required_bos = "BULLISH_BOS" if bullish else "BEARISH_BOS"
    if not any(x.kind == required_bos for x in bos):
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

    reason_map = (
        ("H1 bias", "H1 bias aligned"),
        ("M15 structure", "M15 structure aligned"),
        ("confirmed BOS", "confirmed BOS"),
        ("active order block", "active order block"),
        ("active FVG", "active FVG"),
        ("liquidity sweep", "liquidity sweep confirmed"),
    )
    reasons = tuple(text for key, text in reason_map if key not in missing)
    return ConfluenceEvidence(direction, reasons, tuple(missing))
