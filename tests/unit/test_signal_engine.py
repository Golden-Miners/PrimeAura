from decimal import Decimal
from primeaura.analysis.advanced_smc import OrderBlock
from primeaura.analysis.smc import FairValueGap,LiquidityPool
from primeaura.signals.engine import build_signal

def test_rr_gate_rejects_signal():
    ob=OrderBlock("BULLISH_OB",1,Decimal("99"),Decimal("100"),2)
    liq=[LiquidityPool("BUY_SIDE",Decimal("101"),3,3,2)]
    assert build_signal("XAUUSD","BUY","s","1",Decimal("100"),ob,liq,None) is None

def test_signal_contains_strategy_and_exit():
    ob=OrderBlock("BULLISH_OB",1,Decimal("99"),Decimal("100"),2)
    liq=[LiquidityPool("BUY_SIDE",Decimal("105"),3,3,2),LiquidityPool("BUY_SIDE",Decimal("110"),4,4,2)]
    fvg=FairValueGap("BULLISH_FVG",3,Decimal("100"),Decimal("102"))
    s=build_signal("XAUUSD","BUY","smc","1.0",Decimal("100"),ob,liq,fvg,Decimal("80"))
    assert s and s.strategy_id=="smc" and s.tp1==Decimal("105") and s.tp2==Decimal("110")
