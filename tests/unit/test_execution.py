from decimal import Decimal
from datetime import datetime,timezone
from primeaura.backtest.engine import ExecutionCosts, simulate_fixed_exit, chronological_split
from primeaura.data.models import OHLCVBar

def test_costs_reduce_long_pnl():
    t=simulate_fixed_exit(Decimal("100"),Decimal("110"),"BUY",Decimal("5"),2,ExecutionCosts(Decimal("1"),Decimal("0.5"),Decimal("0.2")))
    assert t.pnl < Decimal("10")

def test_chronological_split_has_no_shuffle():
    bars=[OHLCVBar(instrument="XAUUSD",timeframe="M15",timestamp=datetime.fromtimestamp(i,tz=timezone.utc),open=Decimal(i),high=Decimal(i+1),low=Decimal(i),close=Decimal(i+1)) for i in range(10)]
    a,b=chronological_split(bars)
    assert len(a)==7 and a[-1].timestamp < b[0].timestamp
