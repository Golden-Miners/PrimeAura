from decimal import Decimal
from primeaura.analysis.indicators import atr, sma

def test_sma():
    assert sma([Decimal("1"),Decimal("2"),Decimal("3")],2) == Decimal("2.5")

def test_atr():
    h=[Decimal("11"),Decimal("13")]; l=[Decimal("9"),Decimal("10")]; c=[Decimal("10"),Decimal("12")]
    assert atr(h,l,c,2) == Decimal("2.5")
