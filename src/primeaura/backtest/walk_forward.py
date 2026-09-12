from dataclasses import dataclass
from decimal import Decimal
from ..data.models import OHLCVBar

@dataclass(frozen=True)
class WalkForwardWindow:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


def generate_windows(bars: list[OHLCVBar], train_size: int, test_size: int, step: int | None = None) -> tuple[WalkForwardWindow,...]:
    if train_size<1 or test_size<1: raise ValueError("window sizes must be positive")
    step=step or test_size
    if step<1: raise ValueError("step must be positive")
    out=[]; start=0
    while start+train_size+test_size<=len(bars):
        out.append(WalkForwardWindow(start,start+train_size,start+train_size,start+train_size+test_size)); start+=step
    return tuple(out)
