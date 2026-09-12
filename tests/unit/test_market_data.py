from datetime import datetime, timezone
from decimal import Decimal
import pytest
from primeaura.data.models import MarketSnapshot, OHLCVBar
from primeaura.data.validation import MarketDataValidationError, validate_snapshot

def bar(ts, **kw):
    d={"instrument":"XAUUSD","timeframe":"M15","timestamp":datetime.fromtimestamp(ts,tz=timezone.utc),"open":Decimal("2500"),"high":Decimal("2510"),"low":Decimal("2490"),"close":Decimal("2505")}; d.update(kw); return OHLCVBar(**d)

def snap(*bars): return MarketSnapshot(instrument="XAUUSD",timeframe="M15",bars=tuple(bars),source="test",retrieved_at=datetime.now(timezone.utc))

def test_valid(): assert validate_snapshot(snap(bar(1),bar(2))).bar_count == 2

def test_bad_high():
    with pytest.raises(MarketDataValidationError): validate_snapshot(snap(bar(1,high=Decimal("2480"))))

def test_bad_low():
    with pytest.raises(MarketDataValidationError): validate_snapshot(snap(bar(1,low=Decimal("2520"))))

def test_unsorted():
    with pytest.raises(MarketDataValidationError): validate_snapshot(snap(bar(2),bar(1)))

def test_mismatch():
    with pytest.raises(MarketDataValidationError): validate_snapshot(snap(bar(1,instrument="XAGUSD")))
