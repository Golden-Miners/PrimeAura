from datetime import datetime,timezone
from decimal import Decimal
from primeaura.analysis.activation import active_fvgs,active_order_blocks,detect_liquidity_sweeps
from primeaura.analysis.advanced_smc import OrderBlock
from primeaura.analysis.smc import FairValueGap,LiquidityPool
from primeaura.data.models import OHLCVBar

def b(i,o,h,l,c): return OHLCVBar(instrument="XAUUSD",timeframe="M15",timestamp=datetime.fromtimestamp(i,tz=timezone.utc),open=Decimal(str(o)),high=Decimal(str(h)),low=Decimal(str(l)),close=Decimal(str(c)))

def test_sell_side_sweep():
    bars=[b(0,100,102,99,101),b(1,101,103,98,101.5)]
    p=[LiquidityPool("SELL_SIDE",Decimal("100"),0,0,2)]
    s=detect_liquidity_sweeps(bars,p); assert s and s[0].kind=="BULLISH_SWEEP"

def test_bullish_ob_invalidated_by_close_below_low():
    blocks=[OrderBlock("BULLISH_OB",0,Decimal("99"),Decimal("101"),0)]
    z=active_order_blocks([b(0,100,101,99,100),b(1,100,101,98,98.5)],blocks)[0]
    assert not z.active and z.invalidated_at==1

def test_bullish_fvg_stays_active_if_not_invalidated():
    f=[FairValueGap("BULLISH_FVG",1,Decimal("100"),Decimal("102"))]
    z=active_fvgs([b(0,99,100,98,99),b(1,99,103,99,102),b(2,102,104,101,103)],f)[0]
    assert z.active
