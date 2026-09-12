from datetime import datetime, timezone
from decimal import Decimal
from primeaura.analysis.smc import detect_bos, detect_fvg, find_equal_levels
from primeaura.analysis.structure import SwingPoint
from primeaura.data.models import OHLCVBar

def b(i,o,h,l,c): return OHLCVBar(instrument="XAUUSD",timeframe="M15",timestamp=datetime.fromtimestamp(i,tz=timezone.utc),open=Decimal(str(o)),high=Decimal(str(h)),low=Decimal(str(l)),close=Decimal(str(c)))

def test_equal_high_liquidity():
    bars=[b(0,10,10,9,9),b(1,9,12,8,10),b(2,10,12.005,9,11)]
    swings=[SwingPoint(1,Decimal("12"),"HIGH"),SwingPoint(2,Decimal("12.005"),"HIGH")]
    p=find_equal_levels(bars,swings)
    assert len(p)==1 and p[0].kind=="BUY_SIDE" and p[0].touches==2

def test_bos_uses_close_not_wick():
    bars=[b(0,10,11,9,10),b(1,10,12,9,10.5),b(2,10.5,12.5,10,12.0)]
    swings=[SwingPoint(1,Decimal("12"),"HIGH")]
    assert detect_bos(bars,swings)[0].kind=="BULLISH_BOS"

def test_fvg():
    bars=[b(0,10,10,9,9.5),b(1,9.5,12,9.4,11.5),b(2,11.5,13,10.1,12.5)]
    gaps=detect_fvg(bars,min_size_pct=Decimal("0.001"))
    assert gaps and gaps[0].kind=="BULLISH_FVG"
