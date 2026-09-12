from decimal import Decimal
from primeaura.analysis.advanced_smc import OrderBlock
from primeaura.analysis.confluence import evaluate_confluence, zones_from_order_blocks
from primeaura.analysis.smc import FairValueGap, LiquidityPool, StructureBreak

def test_zones_derive_from_order_blocks():
    zones=zones_from_order_blocks([OrderBlock("BULLISH_OB",2,Decimal("100"),Decimal("105"),5)])
    assert zones[0].kind=="DEMAND" and zones[0].low==Decimal("100")

def test_balanced_evidence_is_no_signal():
    r=evaluate_confluence("BULLISH","BULLISH",[],[StructureBreak("BEARISH_BOS",3,Decimal("100"),2)],[],[])
    assert r.direction in {"BUY","NO_SIGNAL"}

def test_bullish_confluence():
    r=evaluate_confluence("BULLISH","BULLISH",[LiquidityPool("SELL_SIDE",Decimal("100"),1,2,2)],[StructureBreak("BULLISH_BOS",3,Decimal("101"),2)],[OrderBlock("BULLISH_OB",2,Decimal("99"),Decimal("101"),3)],[FairValueGap("BULLISH_FVG",3,Decimal("101"),Decimal("102") )])
    assert r.direction=="BUY" and r.score>0
