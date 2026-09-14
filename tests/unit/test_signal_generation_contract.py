from datetime import datetime, timezone
from decimal import Decimal

from src.primeaura.analysis.activation import ActiveZone, LiquiditySweep
from src.primeaura.analysis.multi_timeframe import (
    MultiTimeframeContext,
    TimeframeContext,
)
from src.primeaura.analysis.regime import MarketRegime
from src.primeaura.analysis.smc import LiquidityPool, StructureBreak
from src.primeaura.signals.prime_signal import generate_locked_signal


def _ctx() -> MultiTimeframeContext:
    regime = MarketRegime("TRENDING_BULLISH", "NORMAL", Decimal("90"), ())
    return MultiTimeframeContext(
        higher=TimeframeContext("H1", "BULLISH", "BULLISH", regime),
        structure=TimeframeContext("M15", "BULLISH", "BULLISH", regime),
        entry=TimeframeContext("M5", "BULLISH", "BULLISH", regime),
    )


def test_fully_qualified_buy_produces_signal():
    entry = Decimal("100")
    pools = [
        LiquidityPool("SELL_SIDE", Decimal("99"), 1, 10, 2),
        LiquidityPool("BUY_SIDE", Decimal("106"), 5, 12, 2),
        LiquidityPool("BUY_SIDE", Decimal("110"), 7, 14, 2),
    ]
    bos = [StructureBreak("BULLISH_BOS", 20, Decimal("103"), 15)]
    sweeps = [LiquiditySweep("BULLISH_SWEEP", 18, Decimal("99"), Decimal("100.5"))]
    obs = [ActiveZone("BULLISH_OB", Decimal("98"), Decimal("99.5"), 19, True)]
    fvgs = [ActiveZone("BULLISH_FVG", Decimal("100.2"), Decimal("101"), 20, True)]

    signal = generate_locked_signal(
        "TEST",
        _ctx(),
        "BUY",
        entry,
        sweeps,
        bos,
        obs,
        fvgs,
        pools,
        timestamp=datetime(2026, 9, 14, tzinfo=timezone.utc),
    )

    assert signal is not None
    assert signal.direction == "BUY"
    assert signal.entry == entry
    assert signal.stop_loss == Decimal("98") * (Decimal("1") - Decimal("0.0005"))
    assert signal.tp1 == Decimal("106")
    assert signal.tp2 == Decimal("110")
    assert signal.rr_tp1 >= Decimal("2.0")
    assert signal.rr_tp2 is not None


def test_missing_liquidity_sweep_blocks_signal():
    entry = Decimal("100")
    pools = [
        LiquidityPool("SELL_SIDE", Decimal("99"), 1, 10, 2),
        LiquidityPool("BUY_SIDE", Decimal("106"), 5, 12, 2),
    ]
    bos = [StructureBreak("BULLISH_BOS", 20, Decimal("103"), 15)]
    obs = [ActiveZone("BULLISH_OB", Decimal("98"), Decimal("99.5"), 19, True)]
    fvgs = [ActiveZone("BULLISH_FVG", Decimal("100.2"), Decimal("101"), 20, True)]

    signal = generate_locked_signal(
        "TEST",
        _ctx(),
        "BUY",
        entry,
        [],
        bos,
        obs,
        fvgs,
        pools,
    )

    assert signal is None
