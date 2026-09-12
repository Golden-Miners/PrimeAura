from datetime import datetime, timezone
from decimal import Decimal
import pytest
from primeaura.backtest.walk_forward import generate_windows
from primeaura.backtest.leakage import assert_strictly_before, assert_sorted
from primeaura.data.models import OHLCVBar

def bars(n): return [OHLCVBar(instrument="XAUUSD",timeframe="M15",timestamp=datetime.fromtimestamp(i,tz=timezone.utc),open=Decimal("1"),high=Decimal("2"),low=Decimal("0"),close=Decimal("1")) for i in range(n)]

def test_walk_forward_windows():
    w=generate_windows(bars(20),10,5)
    assert w[0].train_start==0 and w[0].train_end==10 and w[0].test_start==10 and w[0].test_end==15

def test_leakage_guard():
    b=bars(10)
    with pytest.raises(ValueError): assert_strictly_before(b[:6],b[5:])

def test_sorted_guard():
    b=bars(3)
    with pytest.raises(ValueError): assert_sorted([b[1],b[0]])
