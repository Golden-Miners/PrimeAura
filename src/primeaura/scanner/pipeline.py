from decimal import Decimal
from ..analysis.activation import active_fvgs, active_order_blocks, detect_liquidity_sweeps
from ..signals.mtf_confluence import evaluate_locked_confluence
from ..signals.prime_signal import generate_locked_signal
from .prime_analyzer import analyze_m15_components, analyze_timeframes

def generate_from_bars(instrument: str, bars_by_tf: dict[str, list]):
    """Generate only fully qualified, confirmed-candle signals."""
    context, _, _ = analyze_timeframes(bars_by_tf)
    m15 = bars_by_tf["M15"]
    _, bos, _, fvgs, pools, obs = analyze_m15_components(m15)

    sweeps = detect_liquidity_sweeps(m15, pools)
    active_obs = active_order_blocks(m15, obs)
    active_fvgs_list = active_fvgs(m15, fvgs)

    candidates = []
    for direction in ("BUY", "SELL"):
        evidence = evaluate_locked_confluence(
            context, direction, pools, bos, sweeps, active_obs, active_fvgs_list
        )
        if evidence.missing:
            continue

        entry = bars_by_tf["M5"][-1].close
        signal = generate_locked_signal(
            instrument,
            context,
            direction,
            Decimal(str(entry)),
            sweeps,
            bos,
            active_obs,
            active_fvgs_list,
            pools,
        )
        if signal:
            candidates.append(signal)

    return tuple(candidates)
