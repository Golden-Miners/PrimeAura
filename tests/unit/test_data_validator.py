from datetime import datetime,timezone,timedelta
from decimal import Decimal
from primeaura.data.models import OHLCVBar
from primeaura.data.validator import validate_bars

def b(i):
 return OHLCVBar(instrument="XAUUSD",timeframe="M15",timestamp=datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=15*i),open=Decimal("1"),high=Decimal("2"),low=Decimal("0.5"),close=Decimal("1.5"))
def test_valid_series(): assert validate_bars([b(0),b(1),b(2)],timedelta(minutes=15)).valid
def test_gap_is_rejected(): assert not validate_bars([b(0),b(2)],timedelta(minutes=15)).valid
