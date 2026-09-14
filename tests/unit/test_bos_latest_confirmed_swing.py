from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.primeaura.analysis.smc import detect_bos
from src.primeaura.analysis.structure import SwingPoint
from src.primeaura.data.models import OHLCVBar


def _bars(closes: list[str]) -> list[OHLCVBar]:
    start = datetime(2026, 9, 14, tzinfo=timezone.utc)
    return [
        OHLCVBar(
            instrument="TEST",
            timeframe="M15",
            timestamp=start + timedelta(minutes=15 * i),
            open=Decimal(close),
            high=Decimal(close) + Decimal("0.5"),
            low=Decimal(close) - Decimal("0.5"),
            close=Decimal(close),
            volume=Decimal("1"),
        )
        for i, close in enumerate(closes)
    ]


def test_bos_uses_latest_confirmed_swing_not_every_historical_swing():
    bars = _bars(["100"] * 12)
    bars[8] = bars[8].model_copy(update={"close": Decimal("105"), "open": Decimal("105")})
    bars[10] = bars[10].model_copy(update={"close": Decimal("111"), "open": Decimal("111")})

    swings = [
        SwingPoint(2, Decimal("100"), "HIGH"),
        SwingPoint(6, Decimal("110"), "HIGH"),
    ]

    bos = detect_bos(bars, swings)

    assert [(x.kind, x.index, x.level, x.swing_index) for x in bos] == [
        ("BULLISH_BOS", 10, Decimal("110"), 6)
    ]


def test_bos_does_not_use_unconfirmed_swing():
    bars = _bars(["100"] * 8)
    bars[3] = bars[3].model_copy(update={"close": Decimal("105"), "open": Decimal("105")})

    swings = [SwingPoint(2, Decimal("110"), "HIGH")]

    assert detect_bos(bars, swings) == []
