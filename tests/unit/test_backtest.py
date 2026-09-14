from decimal import Decimal
from primeaura.backtest.metrics import calculate_metrics
from primeaura.backtest.models import TradeResult
from primeaura.backtest.validation import validate_out_of_sample
from primeaura.research.backtest import SimpleSignalBacktester
from types import SimpleNamespace
from datetime import datetime,timezone,timedelta
from primeaura.data.models import OHLCVBar

def t(p): return TradeResult(entry=Decimal("100"),exit=Decimal("101") if p>0 else Decimal("99"),direction="BUY",pnl=Decimal(str(p)),r_multiple=Decimal(str(p)),bars_held=1)

def test_metrics():
    m=calculate_metrics([t(2),t(-1),t(3)])
    assert m.trade_count==3 and m.wins==2 and m.losses==1 and m.max_drawdown==Decimal("1")

def test_oos_rejects_small_sample():
    r=validate_out_of_sample(calculate_metrics([t(1)]),min_trades=100)
    assert not r.passed

def test_future_bar_hits_target():
    bar=OHLCVBar("XAUUSD","M15",datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(minutes=15),Decimal("100"),Decimal("103"),Decimal("99"),Decimal("100"))
    sig=SimpleNamespace(direction="BUY",stop_loss=Decimal("98"),tp1=Decimal("102"),detected_at=datetime(2026,1,1,tzinfo=timezone.utc))
    stats=SimpleSignalBacktester().run([bar],[sig])
    assert stats.trades==1 and stats.wins==1
