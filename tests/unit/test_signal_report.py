from decimal import Decimal
import pytest
from primeaura.signals.reporter import build_signal_report

def test_signal_has_strategy_attribution_and_rr():
 r=build_signal_report("XAUUSD","BUY","smc","1.0",Decimal("100"),Decimal("98"),Decimal("104"),Decimal("80"),"test",["BOS"],["news"])
 assert r.strategy_id=="smc" and r.rr==Decimal("2")
def test_rr_gate():
 with pytest.raises(ValueError): build_signal_report("XAUUSD","BUY","smc","1.0",Decimal("100"),Decimal("98"),Decimal("103"),Decimal("80"),"test",[],[])
