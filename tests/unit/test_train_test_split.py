from datetime import datetime, timezone

import pytest

from primeaura.backtest.runner import split_train_test

def test_split_is_chronological_and_non_overlapping():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 2, 1, tzinfo=timezone.utc)
    train, test = split_train_test(start, end, 0.7)
    assert train[0] == start
    assert train[1] == test[0]
    assert test[1] == end

def test_split_rejects_invalid_ratio():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 2, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        split_train_test(start, end, 0)


def test_walk_forward_windows_are_chronological_and_non_overlapping():
    from primeaura.backtest.runner import build_walk_forward_windows

    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 5, 1, tzinfo=timezone.utc)
    windows = build_walk_forward_windows(start, end, train_days=30, test_days=10)

    assert len(windows) == 3
    assert windows[0][0] == start
    assert windows[0][1] == windows[0][2]
    assert windows[-1][3] == end
    for previous, current in zip(windows, windows[1:]):
        assert previous[3] == current[0]


def test_walk_forward_rejects_invalid_ranges():
    from primeaura.backtest.runner import build_walk_forward_windows

    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 2, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        build_walk_forward_windows(start, end, train_days=0, test_days=10)
    with pytest.raises(ValueError):
        build_walk_forward_windows(start, end, train_days=20, test_days=20)


def test_signal_decision_timestamp_is_available_for_oos_partitioning():
    from decimal import Decimal
    from datetime import datetime, timezone
    from primeaura.signals.models import Signal

    timestamp = datetime(2026, 1, 10, tzinfo=timezone.utc)
    signal = Signal(
        instrument="XAUUSD",
        timestamp=timestamp,
        direction="BUY",
        strategy_id="test",
        strategy_version="1.0.0",
        entry=Decimal("4000"),
        stop_loss=Decimal("3990"),
        tp1=Decimal("4020"),
        rr_tp1=Decimal("2"),
        confidence=Decimal("85"),
        reasoning=("test",),
    )
    assert signal.timestamp == timestamp
