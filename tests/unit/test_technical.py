from decimal import Decimal
from primeaura.strategies.technical import atr,sma,breakout_level,momentum

def test_sma(): assert sma([Decimal('1'),Decimal('2'),Decimal('3')],3)==Decimal('2')
def test_atr(): assert atr([Decimal('11'),Decimal('12'),Decimal('13')],[Decimal('9'),Decimal('10'),Decimal('11')],[Decimal('10'),Decimal('11'),Decimal('12')],2)==Decimal('2')
def test_breakout_excludes_current_bar(): assert breakout_level([Decimal(str(x)) for x in range(1,23)],20)==Decimal('21')
def test_momentum(): assert momentum([Decimal('100'),Decimal('110')],1)==Decimal('0.1')
