from decimal import Decimal
from primeaura.backtest.models import TradeResult
from primeaura.backtest.robustness import bootstrap_r_multiple

def t(r): return TradeResult(entry=Decimal("100"),exit=Decimal("101"),direction="BUY",pnl=Decimal(str(r)),r_multiple=Decimal(str(r)),bars_held=1)

def test_bootstrap_is_reproducible():
    a=bootstrap_r_multiple([t(1),t(-1),t(2)],100,7); b=bootstrap_r_multiple([t(1),t(-1),t(2)],100,7)
    assert a==b and a["p05"]<=a["median"]<=a["p95"]
