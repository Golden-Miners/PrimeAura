from datetime import datetime,timezone
from decimal import Decimal
from primeaura.strategies.catalog import built_in_strategies
from primeaura.strategies.smc_v1 import STRATEGY_ID, signal
from primeaura.data.models import OHLCVBar

def test_catalog_contains_prototype():
    s=built_in_strategies()[0]; assert s.strategy_id==STRATEGY_ID and "XAUUSD" in s.instruments

def test_strategy_has_no_lookahead_at_insufficient_history():
    bars=[OHLCVBar(instrument="XAUUSD",timeframe="M15",timestamp=datetime.fromtimestamp(i,tz=timezone.utc),open=Decimal("100"),high=Decimal("101"),low=Decimal("99"),close=Decimal("100")) for i in range(20)]
    assert signal(bars,19) is None
