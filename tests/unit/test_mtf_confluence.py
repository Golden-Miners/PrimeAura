from decimal import Decimal

from primeaura.analysis.activation import ActiveZone, LiquiditySweep
from primeaura.analysis.multi_timeframe import TimeframeContext, MultiTimeframeContext
from primeaura.analysis.regime import MarketRegime
from primeaura.analysis.smc import LiquidityPool, StructureBreak
from primeaura.signals.mtf_confluence import evaluate_locked_confluence

def ctx():
    r = MarketRegime("TRENDING_BULLISH", "NORMAL", Decimal("80"), ("test",))
    return MultiTimeframeContext(
        TimeframeContext("H1", "BULLISH", "BULLISH", r),
        TimeframeContext("M15", "BULLISH", "BULLISH", r),
        TimeframeContext("M5", "BULLISH", "BULLISH", r),
    )

def test_bullish_requires_every_locked_component():
    e = evaluate_locked_confluence(
        ctx(),
        "BUY",
        [LiquidityPool("SELL_SIDE", Decimal("100"), 1, 2, 2)],
        [StructureBreak("BULLISH_BOS", 3, Decimal("101"), 2)],
        [LiquiditySweep("BULLISH_SWEEP", 4, Decimal("100"), Decimal("100.5"))],
        [ActiveZone("BULLISH_OB", Decimal("99"), Decimal("101"), 3, True)],
        [ActiveZone("BULLISH_FVG", Decimal("101"), Decimal("102"), 3, True)],
    )
    assert e.missing == ()

def test_wrong_bias_is_missing():
    c = ctx()
    c = MultiTimeframeContext(
        TimeframeContext("H1", "BEARISH", "BEARISH", c.higher.regime),
        c.structure,
        c.entry,
    )
    e = evaluate_locked_confluence(c, "BUY", [], [], [], [], [])
    assert "H1 bias" in e.missing
