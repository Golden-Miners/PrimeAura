from decimal import Decimal
from datetime import datetime,timezone
import pytest
from primeaura.backtest.pipeline import run_backtest
from primeaura.data.models import OHLCVBar

def bars(n=3): return [OHLCVBar(instrument="XAUUSD",timeframe="M15",timestamp=datetime.fromtimestamp(i,tz=timezone.utc),open=Decimal("100"),high=Decimal("102"),low=Decimal("99"),close=Decimal("101")) for i in range(n)]

def signal(data,i):
    if i==1: return __import__("primeaura.backtest.pipeline",fromlist=["CandidateTrade"]).CandidateTrade(i,"BUY",Decimal("100"),Decimal("102"),Decimal("1"),1)
    return None

def test_pipeline_generates_only_index_matched_trades():
    trades=run_backtest(bars(),signal); assert len(trades)==1 and trades[0].pnl==Decimal("2")

def test_pipeline_rejects_lookahead_index():
    def bad(data,i):
        if i==0: return __import__("primeaura.backtest.pipeline",fromlist=["CandidateTrade"]).CandidateTrade(1,"BUY",Decimal("100"),Decimal("102"),Decimal("1"),1)
    with pytest.raises(ValueError): run_backtest(bars(),bad)

def test_end_to_end_scanner_pipeline_exists():
    from primeaura.scanner.pipeline import generate_from_bars
    assert callable(generate_from_bars)
