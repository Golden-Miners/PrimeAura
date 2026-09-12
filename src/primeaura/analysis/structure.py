from dataclasses import dataclass
from decimal import Decimal
from ..data.models import OHLCVBar

@dataclass(frozen=True)
class SwingPoint:
    index: int
    price: Decimal
    kind: str

def detect_swings(bars: list[OHLCVBar], left: int = 2, right: int = 2) -> list[SwingPoint]:
    """Non-repainting confirmed swings using a 2-left/2-right default window."""
    if left < 1 or right < 1: raise ValueError("left/right must be positive")
    points=[]
    for i in range(left, len(bars)-right):
        h=bars[i].high; l=bars[i].low
        if all(h > bars[j].high for j in range(i-left,i)) and all(h > bars[j].high for j in range(i+1,i+right+1)):
            points.append(SwingPoint(i,h,"HIGH"))
        if all(l < bars[j].low for j in range(i-left,i)) and all(l < bars[j].low for j in range(i+1,i+right+1)):
            points.append(SwingPoint(i,l,"LOW"))
    return points
