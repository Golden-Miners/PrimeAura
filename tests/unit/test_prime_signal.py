from decimal import Decimal
from primeaura.analysis.activation import ActiveZone,LiquiditySweep
from primeaura.analysis.multi_timeframe import TimeframeContext,MultiTimeframeContext
from primeaura.analysis.regime import MarketRegime
from primeaura.analysis.smc import LiquidityPool,StructureBreak
from primeaura.signals.prime_signal import generate_locked_signal

def ctx():
 r=MarketRegime("TRENDING_BULLISH","NORMAL",Decimal("80"),("test",)); return MultiTimeframeContext(TimeframeContext("H1","BULLISH","BULLISH",r),TimeframeContext("M15","BULLISH","BULLISH",r),TimeframeContext("M5","BULLISH","BULLISH",r))
def test_locked_signal_uses_ob_sl_and_liquidity_tp():
 s=generate_locked_signal("XAUUSD",ctx(),"BUY",Decimal("100"),[LiquiditySweep("BULLISH_SWEEP",5,Decimal("99"),Decimal("100.5"))],[StructureBreak("BULLISH_BOS",6,Decimal("100"),4)],[ActiveZone("BULLISH_OB",Decimal("98"),Decimal("100"),4,True)],[ActiveZone("BULLISH_FVG",Decimal("100"),Decimal("101"),6,True)],[LiquidityPool("BUY_SIDE",Decimal("105"),7,7,2),LiquidityPool("BUY_SIDE",Decimal("110"),8,8,2)])
 assert s and s.stop_loss==Decimal("98")*(Decimal("1")-Decimal("0.0005")) and s.tp1==Decimal("105") and s.rr_tp1>Decimal("2")
def test_missing_sweep_rejects():
 assert generate_locked_signal("XAUUSD",ctx(),"BUY",Decimal("100"),[],[],[],[],[]) is None
