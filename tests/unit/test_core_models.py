from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from primeaura.core.enums import SignalDirection
from primeaura.core.models import PriceLevels, Signal


def make_signal(**overrides):
    data = {
        "signal_id": "test-001",
        "instrument": "XAUUSD",
        "direction": SignalDirection.BUY,
        "timeframe": "M15",
        "strategy": "Test Strategy",
        "strategy_version": "1.0",
        "levels": {
            "entry": "2500.00",
            "stop_loss": "2490.00",
            "tp1": "2520.00",
            "tp2": "2540.00",
        },
        "rr_tp1": "2.0",
        "rr_tp2": "4.0",
        "confidence": "75",
        "reasoning": "Test reasoning",
        "generated_at": datetime.now(timezone.utc),
    }
    data.update(overrides)
    return Signal(**data)


def test_price_levels_risk():
    levels = PriceLevels(
        entry=Decimal("2500"),
        stop_loss=Decimal("2490"),
        tp1=Decimal("2520"),
        tp2=Decimal("2540"),
    )
    assert levels.risk == Decimal("10")


def test_signal_accepts_no_signal():
    signal = make_signal(
        direction=SignalDirection.NO_SIGNAL,
        rr_tp1="0",
        rr_tp2="0",
    )
    assert signal.direction is SignalDirection.NO_SIGNAL


def test_confidence_is_bounded():
    with pytest.raises(ValidationError):
        make_signal(confidence="101")


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        make_signal(unexpected_field="bad")
