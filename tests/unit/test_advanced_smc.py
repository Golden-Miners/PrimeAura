from datetime import datetime, timezone
from decimal import Decimal
from primeaura.analysis.advanced_smc import detect_choch, detect_order_blocks
from primeaura.analysis.structure import SwingPoint
from primeaura.data.models import OHLCVBar

def b(i,o,h,l,c): return OHLCVBar(instrument="XAUUSD",timeframe="M15",timestamp=datetime.fromtimestamp(i,tz=timezone.utc),open=Decimal(str(o)),high=Decimal(str(h)),low=Decimal(str(l)),close=Decimal(str(c)))

def test_bullish_choch_from_bearish_structure():
    bars=[b(0,10,11,9,10),b(1,10,12,9,11),b(2,11,11.5,8,9),b(3,9,13,8.5,13)]
    swings=[SwingPoint(0,Decimal("11"),"HIGH"),SwingPoint(1,Decimal("9"),"LOW"),SwingPoint(2,Decimal("11.5"),"HIGH"),SwingPoint(2,Decimal("8"),"LOW")]
    result=detect_choch(bars,swings)
    assert result and result[0].kind=="BULLISH_CHOCH"

def test_order_block_requires_displacement():
    bars=[b(i,100+i,101+i,99+i,100+i) for i in range(20)]
    # A small body should not qualify as displacement.
    result=detect_order_blocks(bars,[19])
    assert result==[]
