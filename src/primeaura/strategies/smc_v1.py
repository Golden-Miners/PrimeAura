from decimal import Decimal
from ..analysis.structure import detect_swings
from ..analysis.smc import detect_bos, detect_fvg, find_equal_levels
from ..analysis.advanced_smc import detect_order_blocks
from ..backtest.pipeline import CandidateTrade
from ..data.models import OHLCVBar

STRATEGY_ID="smc-confluence-v1"

def signal(bars:list[OHLCVBar], index:int)->CandidateTrade|None:
    """Research prototype: only evaluates information available through `index`."""
    if index<20: return None
    data=bars[:index+1]
    swings=detect_swings(data)
    bos=detect_bos(data,swings)
    fvgs=detect_fvg(data)
    liquidity=find_equal_levels(data,swings)
    bullish_bos=[x for x in bos if x.kind=="BULLISH_BOS" and x.index==index]
    bearish_bos=[x for x in bos if x.kind=="BEARISH_BOS" and x.index==index]
    if not bullish_bos and not bearish_bos: return None
    obs=detect_order_blocks(data,[x.index for x in bos])
    current=data[-1]
    if bullish_bos and any(x.kind=="BULLISH_OB" for x in obs) and any(x.kind=="BULLISH_FVG" for x in fvgs) and any(x.kind=="SELL_SIDE" for x in liquidity):
        risk=current.close*Decimal("0.001")
        return CandidateTrade(index,"BUY",current.close,current.close+risk*Decimal("2"),risk,1)
    if bearish_bos and any(x.kind=="BEARISH_OB" for x in obs) and any(x.kind=="BEARISH_FVG" for x in fvgs) and any(x.kind=="BUY_SIDE" for x in liquidity):
        risk=current.close*Decimal("0.001")
        return CandidateTrade(index,"SELL",current.close,current.close-risk*Decimal("2"),risk,1)
    return None
