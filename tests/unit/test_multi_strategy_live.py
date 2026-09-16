from datetime import datetime, timezone
from decimal import Decimal
from primeaura.scanner.multi_strategy import evaluate_strategies, STRATEGIES
from primeaura.data.models import OHLCVBar

def bars(n=60):
    out=[]
    for i in range(n):
        close=Decimal("100")+Decimal(i)/Decimal("10")
        out.append(OHLCVBar(instrument="XAUUSD",timeframe="M15",timestamp=datetime(2026,1,1,tzinfo=timezone.utc),open=close,high=close+Decimal("1"),low=close-Decimal("1"),close=close,volume=Decimal("1")))
    return out

def test_catalog_has_all_discussed_live_strategies():
    expected={"smc-confluence","trend-pullback","liquidity-sweep-ifvg","breakout-retest","ema-crossover","momentum","mean-reversion","volatility-breakout"}
    assert expected.issubset(STRATEGIES)

def test_selected_strategy_is_evaluated_independently():
    b=bars(); bars_by_tf={"H1":b,"M15":b,"M5":b}
    signals,results=evaluate_strategies("XAUUSD",bars_by_tf,("ema-crossover","momentum"))
    assert {r.strategy_id for r in results}=={"ema-crossover","momentum"}
    assert all(r.status=="RESEARCH_ONLY" for r in results)
