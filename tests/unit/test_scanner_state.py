from primeaura.scanner.state import SignalState

def test_duplicate_signal_is_suppressed():
 s=SignalState(); x={"direction":"BUY","entry":100,"stop_loss":98,"tp1":104}; assert s.is_new("XAUUSD","momentum",x); assert not s.is_new("XAUUSD","momentum",x)
def test_different_strategy_is_independent():
 s=SignalState(); x={"direction":"BUY","entry":100,"stop_loss":98,"tp1":104}; assert s.is_new("XAUUSD","momentum",x); assert s.is_new("XAUUSD","trend-pullback",x)
