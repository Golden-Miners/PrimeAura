from datetime import datetime
from ..data.models import OHLCVBar

def assert_strictly_before(train: list[OHLCVBar], test: list[OHLCVBar]) -> None:
    if train and test and train[-1].timestamp >= test[0].timestamp:
        raise ValueError("Training data overlaps or follows test data")

def assert_sorted(bars: list[OHLCVBar]) -> None:
    for a,b in zip(bars,bars[1:]):
        if a.timestamp >= b.timestamp: raise ValueError("Data must be strictly chronological")
