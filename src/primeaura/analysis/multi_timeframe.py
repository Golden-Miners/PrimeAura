from dataclasses import dataclass
from .regime import MarketRegime

@dataclass(frozen=True)
class TimeframeContext:
    timeframe: str
    bias: str
    structure: str
    regime: MarketRegime

@dataclass(frozen=True)
class MultiTimeframeContext:
    higher: TimeframeContext
    structure: TimeframeContext
    entry: TimeframeContext


def build_context(higher: TimeframeContext, structure: TimeframeContext, entry: TimeframeContext) -> MultiTimeframeContext:
    """Package independently verified timeframe analyses; does not infer trades."""
    for x in (higher, structure, entry):
        if not x.timeframe: raise ValueError("timeframe is required")
    return MultiTimeframeContext(higher, structure, entry)
