from decimal import Decimal
from primeaura.strategies.rule_based import momentum_continuation,volatility_breakout

def test_momentum_needs_history():
 c={'close':[Decimal('100')]*10,'high':[Decimal('101')]*10,'low':[Decimal('99')]*10}; assert momentum_continuation('XAUUSD',c) is None

def test_volatility_breakout_needs_lookback():
 c={'close':[Decimal(str(x)) for x in range(1,10)],'high':[Decimal(str(x+1)) for x in range(1,10)],'low':[Decimal(str(x-1)) for x in range(1,10)]}; assert volatility_breakout('XAUUSD',c) is None
