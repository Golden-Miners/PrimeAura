from dataclasses import dataclass
from decimal import Decimal

from ..analysis.activation import active_fvgs, active_order_blocks, detect_liquidity_sweeps
from ..signals.mtf_confluence import evaluate_locked_confluence
from ..signals.prime_signal import BUFFER, MIN_RR
from .prime_analyzer import analyze_m15_components, analyze_timeframes

@dataclass(frozen=True)
class DirectionDiagnostic:
    direction: str
    passed: tuple[str, ...]
    missing: tuple[str, ...]
    final_gate: str
    entry: Decimal | None = None
    stop_loss: Decimal | None = None
    tp1: Decimal | None = None
    rr_tp1: Decimal | None = None
    tp2: Decimal | None = None
    rr_tp2: Decimal | None = None

def diagnose_from_bars(bars_by_tf: dict[str, list]) -> tuple[DirectionDiagnostic, ...]:
    """Explain confluence and the final signal/RR rejection reason."""
    context, _, _ = analyze_timeframes(bars_by_tf)
    m15 = bars_by_tf["M15"]
    _, bos, _, fvgs, pools, obs = analyze_m15_components(m15)
    sweeps = detect_liquidity_sweeps(m15, pools)
    active_obs = active_order_blocks(m15, obs)
    active_fvgs_list = active_fvgs(m15, fvgs)
    entry = Decimal(str(bars_by_tf["M5"][-1].close))

    results = []
    for direction in ("BUY", "SELL"):
        evidence = evaluate_locked_confluence(
            context, direction, pools, bos, sweeps, active_obs, active_fvgs_list
        )
        if evidence.missing:
            results.append(DirectionDiagnostic(
                direction, evidence.reasons, evidence.missing,
                "BLOCKED: confluence requirements incomplete", entry
            ))
            continue

        bullish = direction == "BUY"
        ob_kind = "BULLISH_OB" if bullish else "BEARISH_OB"
        valid_obs = [x for x in active_obs if x.kind == ob_kind and x.active]
        ob = max(valid_obs, key=lambda x: x.source_index)
        sl = ob.low * (1 - BUFFER) if bullish else ob.high * (1 + BUFFER)

        target_kind = "BUY_SIDE" if bullish else "SELL_SIDE"
        targets = [
            p.price for p in pools
            if p.kind == target_kind and ((p.price > entry) if bullish else (p.price < entry))
        ]
        targets = sorted(targets, reverse=not bullish)

        tp1 = tp2 = rr1 = rr2 = None
        if not targets:
            gate = "BLOCKED: no opposing liquidity target"
        else:
            tp1 = targets[0]
            if len(targets) > 1:
                tp2 = targets[1]
            risk = abs(entry - sl)
            if risk <= 0:
                gate = "BLOCKED: invalid stop-loss distance"
            else:
                rr1 = abs(tp1 - entry) / risk
                rr2 = abs(tp2 - entry) / risk if tp2 is not None else None
                gate = (
                    f"PASS: RR1 {rr1:.2f} >= {MIN_RR:.1f}"
                    if rr1 >= MIN_RR
                    else f"BLOCKED: RR1 {rr1:.2f} < {MIN_RR:.1f}"
                )

        results.append(DirectionDiagnostic(
            direction, evidence.reasons, (), gate, entry, sl, tp1, rr1, tp2, rr2
        ))
    return tuple(results)
