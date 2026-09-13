from decimal import Decimal
from datetime import datetime,timezone
from primeaura.data.models import OHLCVBar
from primeaura.research.execution_model import simulate_exit,ExecutionConfig

def b(h,l): return OHLCVBar(instrument="XAUUSD",timeframe="M5",timestamp=datetime.now(timezone.utc),open=Decimal("100"),high=Decimal(str(h)),low=Decimal(str(l)),close=Decimal("100"))
def test_conservative_ambiguous_bar_hits_stop():
 o=simulate_exit(Decimal("100"),"BUY",Decimal("98"),Decimal("102"),[b(103,97)])
 assert o and o.reason.endswith("CONSERVATIVE") and o.exit_price==Decimal("98")
def test_sell_tp():
 o=simulate_exit(Decimal("100"),"SELL",Decimal("102"),Decimal("98"),[b(101,97)])
 assert o and o.reason=="TP"
