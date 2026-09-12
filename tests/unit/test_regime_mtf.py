from datetime import datetime, timezone
from decimal import Decimal
from primeaura.analysis.multi_timeframe import TimeframeContext, build_context
from primeaura.analysis.regime import MarketRegime

def regime(): return MarketRegime("RANGING","NORMAL",Decimal("50"),("test",))

def test_mtf_context_is_explicit():
    c=build_context(TimeframeContext("H1","BULLISH","BULLISH",regime()),TimeframeContext("M15","BULLISH","BULLISH",regime()),TimeframeContext("M5","BULLISH","BULLISH",regime()))
    assert c.higher.timeframe=="H1" and c.entry.timeframe=="M5"
