from dataclasses import dataclass
from decimal import Decimal
from .advanced_smc import ChangeOfCharacter
from .smc import StructureBreak
from .structure import SwingPoint

@dataclass(frozen=True)
class StructureState:
    bias: str
    structure: str
    evidence: tuple[str,...]

def classify_structure(swings:list[SwingPoint], bos:list[StructureBreak], choch:list[ChangeOfCharacter]) -> StructureState:
    highs=[x for x in swings if x.kind=="HIGH"]
    lows=[x for x in swings if x.kind=="LOW"]
    if len(highs)<2 or len(lows)<2:
        return StructureState("UNKNOWN","UNKNOWN",("Insufficient confirmed swings",))
    hh=highs[-1].price>highs[-2].price
    hl=lows[-1].price>lows[-2].price
    lh=highs[-1].price<highs[-2].price
    ll=lows[-1].price<lows[-2].price
    bull_bos=any(x.kind=="BULLISH_BOS" for x in bos)
    bear_bos=any(x.kind=="BEARISH_BOS" for x in bos)
    bull_choch=any(x.kind=="BULLISH_CHOCH" for x in choch)
    bear_choch=any(x.kind=="BEARISH_CHOCH" for x in choch)
    if hh and hl and bull_bos and not bear_choch: return StructureState("BULLISH","BULLISH",("HH+HL","Bullish BOS","No bearish CHOCH"))
    if lh and ll and bear_bos and not bull_choch: return StructureState("BEARISH","BEARISH",("LH+LL","Bearish BOS","No bullish CHOCH"))
    if bull_choch: return StructureState("BULLISH_TRANSITION","BULLISH","Bullish CHOCH")
    if bear_choch: return StructureState("BEARISH_TRANSITION","BEARISH","Bearish CHOCH")
    return StructureState("NEUTRAL","NEUTRAL",("Structure not sufficiently directional",))
