from ..analysis.advanced_smc import detect_choch, detect_order_blocks
from ..analysis.bias import classify_structure
from ..analysis.multi_timeframe import TimeframeContext, build_context
from ..analysis.regime import classify_regime
from ..analysis.smc import detect_bos, detect_fvg, find_equal_levels
from ..analysis.structure import detect_swings

def analyze_timeframes(bars_by_tf):
    contexts=[]; swing_map={}; component_map={}
    for tf in ("H1","M15","M5"):
        bars=bars_by_tf[tf]
        swings=detect_swings(bars); bos=detect_bos(bars,swings); choch=detect_choch(bars,swings)
        state=classify_structure(swings,bos,choch)
        swing_map[tf]=swings; component_map[tf]=(bos,choch)
        contexts.append(TimeframeContext(tf,state.bias,state.structure,classify_regime(bars)))
    return build_context(*contexts),swing_map,component_map

def analyze_m15_components(bars):
    swings=detect_swings(bars); bos=detect_bos(bars,swings); choch=detect_choch(bars,swings)
    fvgs=detect_fvg(bars); pools=find_equal_levels(bars,swings); obs=detect_order_blocks(bars,[x.index for x in bos])
    return swings,bos,choch,fvgs,pools,obs
