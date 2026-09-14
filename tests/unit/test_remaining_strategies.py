from decimal import Decimal
from primeaura.strategies.pullback_reversion import trend_pullback,mean_reversion
from primeaura.strategies.breakout_retest import breakout_retest

def test_strategies_reject_insufficient_history():
 c={'close':[Decimal('100')]*10,'high':[Decimal('101')]*10,'low':[Decimal('99')]*10}
 assert trend_pullback('XAUUSD',c) is None
 assert mean_reversion('XAUUSD',c) is None
 assert breakout_retest('XAUUSD',c) is None
