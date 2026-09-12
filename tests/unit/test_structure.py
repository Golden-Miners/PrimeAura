from datetime import datetime, timezone
from decimal import Decimal
from primeaura.analysis.structure import detect_swings
from primeaura.data.models import OHLCVBar

def bars(highs,lows):
    return [OHLCVBar(instrument="XAUUSD",timeframe="M15",timestamp=datetime.fromtimestamp(i,tz=timezone.utc),open=Decimal(str(lows[i]+1)),high=Decimal(str(highs[i])),low=Decimal(str(lows[i])),close=Decimal(str(lows[i]+1))) for i in range(len(highs))]

def test_two_left_two_right_confirmed_swings():
    b=bars([1,2,3,5,3,2,1],[0,-1,-2,-3,-2,-1,0])
    p=detect_swings(b)
    assert [(x.index,x.kind) for x in p] == [(3,"HIGH")]
