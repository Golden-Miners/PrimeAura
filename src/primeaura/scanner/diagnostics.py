from dataclasses import dataclass
from ..analysis.activation import active_fvgs, active_order_blocks, detect_liquidity_sweeps
from ..signals.mtf_confluence import evaluate_locked_confluence
from .prime_analyzer import analyze_m15_components, analyze_timeframes

@dataclass(frozen=True)
class DirectionDiagnostic:
    direction: str
    passed: tuple[str, ...]
    missing: tuple[str, ...]

def diagnose_from_bars(bars_by_tf: dict[str, list]) -> tuple[DirectionDiagnostic, ...]:
    """Explain the locked confluence gate without creating a trading signal."""
    context, _, _ = analyze_timeframes(bars_by_tf)
    m15 = bars_by_tf["M15"]
    _, bos, _, fvgs, pools, obs = analyze_m15_components(m15)
    sweeps = detect_liquidity_sweeps(m15, pools)
    active_obs = active_order_blocks(m15, obs)
    active_fvgs_list = active_fvgs(m15, fvgs)

    results = []
    for direction in ("BUY", "SELL"):
        evidence = evaluate_locked_confluence(
            context, direction, pools, bos, sweeps, active_obs, active_fvgs_list
        )
        results.append(DirectionDiagnostic(direction, evidence.reasons, evidence.missing))
    return tuple(results)
