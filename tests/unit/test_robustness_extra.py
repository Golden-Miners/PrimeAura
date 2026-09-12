from decimal import Decimal
from primeaura.backtest.models import TradeResult
from primeaura.backtest.monte_carlo import monte_carlo_drawdown
from primeaura.backtest.sensitivity import stable_parameter_ranges

def t(p): return TradeResult(entry=Decimal("1"),exit=Decimal("2"),direction="BUY",pnl=Decimal(str(p)),r_multiple=Decimal(str(p)),bars_held=1)

def test_monte_carlo_reproducible():
    a=monte_carlo_drawdown([t(2),t(-1),t(1)],100,11); b=monte_carlo_drawdown([t(2),t(-1),t(1)],100,11); assert a==b

def test_sensitivity_floor():
    assert stable_parameter_ranges({"p1":Decimal("1.2"),"p2":Decimal("0.8")})==("p1",)
