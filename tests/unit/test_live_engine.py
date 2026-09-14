from decimal import Decimal
from datetime import datetime,timezone
from primeaura.scanner.live_engine import LiveSignalEngine
from primeaura.data.models import OHLCVBar

class P:
 def recent(self,i,tf,n):
  return [OHLCVBar(instrument=i,timeframe=tf,timestamp=datetime(2026,1,1,tzinfo=timezone.utc),open=Decimal('100'),high=Decimal('101'),low=Decimal('99'),close=Decimal('100'))]*n

def test_scanner_is_read_only_and_returns_empty_when_no_setup():
 e=LiveSignalEngine(P(),('XAUUSD',)); assert e.scan_all()==()
