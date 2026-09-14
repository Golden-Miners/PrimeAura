from datetime import datetime,timezone
from decimal import Decimal
from types import SimpleNamespace
from primeaura.scanner.events import signal_event_from_result

def test_signal_event_serializes():
 r=SimpleNamespace(instrument="XAUUSD",strategy_id="momentum",signal={"direction":"BUY","entry":Decimal("2500"),"stop_loss":Decimal("2490"),"tp1":Decimal("2520"),"rr":Decimal("2"),"reasoning":["momentum"]})
 e=signal_event_from_result(r,datetime(2026,1,1,tzinfo=timezone.utc)); assert e.to_dict()["instrument"]=="XAUUSD" and "detected_at" in e.to_dict()
