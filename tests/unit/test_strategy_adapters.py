from decimal import Decimal
from primeaura.strategies.simple_adapters import trend_pullback,breakout_retest

def base(): return {"entry":Decimal("100"),"stop_loss":Decimal("98"),"tp1":Decimal("105"),"rr":Decimal("2.5")}
def test_trend_pullback_requires_confirmation():
 c=base(); c.update(trend="BULLISH",pullback_confirmed=True); assert trend_pullback("XAUUSD",c)["direction"]=="BUY"
def test_breakout_retest_requires_all_confirmations():
 c=base(); c.update(breakout_confirmed=True,retest_confirmed=True,continuation_confirmed=True,direction="SELL"); assert breakout_retest("XAGUSD",c)["direction"]=="SELL"
