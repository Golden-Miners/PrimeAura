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
