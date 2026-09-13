from decimal import Decimal
from ..analysis.advanced_smc import detect_order_blocks
from ..analysis.multi_timeframe import TimeframeContext, build_context
from ..analysis.regime import classify_regime
from ..analysis.smc import detect_bos, detect_fvg, find_equal_levels
from ..analysis.structure import detect_swings
from .config import ScanConfig

def _bias_and_structure(bars):
    swings=detect_swings(bars)
    highs=[s for s in swings if s.kind=="HIGH"]
    lows=[s for s in swings if s.kind=="LOW"]
    if len(highs)<2 or len(lows)<2:
        return "UNKNOWN","UNKNOWN",swings
    bullish=highs[-1].price>highs[-2].price and lows[-1].price>lows[-2].price
    bearish=highs[-1].price<highs[-2].price and lows[-1].price<lows[-2].price
    if bullish: return "BULLISH","BULLISH",swings
    if bearish: return "BEARISH","BEARISH",swings
    return "NEUTRAL","NEUTRAL",swings

def analyze_timeframes(bars_by_tf):
    contexts=[]
    swing_map={}
    for tf in ("H1","M15","M5"):
        bars=bars_by_tf[tf]
        bias,structure,swings=_bias_and_structure(bars)
        swing_map[tf]=swings
        contexts.append(TimeframeContext(tf,bias,structure,classify_regime(bars)))
    return build_context(*contexts),swing_map

def analyze_m15_components(bars):
    swings=detect_swings(bars)
    bos=detect_bos(bars,swings)
    fvgs=detect_fvg(bars)
    pools=find_equal_levels(bars,swings)
    obs=detect_order_blocks(bars,[x.index for x in bos])
    return swings,bos,fvgs,pools,obs
