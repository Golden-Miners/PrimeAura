from primeaura.scanner.scanner import MarketScanner
from primeaura.scanner.config import ScanConfig
class P:
 def recent(self,instrument,tf,n): return []
def test_scanner_is_signal_only():
 r=MarketScanner(P(),ScanConfig(instruments=("XAUUSD",),timeframes=("M15",))).scan_once(); assert r[0].signal is None and r[0].reason=="Analysis hook ready"
