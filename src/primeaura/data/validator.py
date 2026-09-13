from dataclasses import dataclass
from datetime import timedelta
from ..data.models import OHLCVBar

@dataclass(frozen=True)
class DataQualityReport:
    valid: bool
    bars: int
    duplicates: int
    gaps: int
    non_positive: int
    issues: tuple[str,...]

def validate_bars(bars:list[OHLCVBar], expected_interval:timedelta|None=None)->DataQualityReport:
    issues=[]; duplicates=gaps=non_positive=0
    for b in bars:
        if min(b.open,b.high,b.low,b.close)<=0: non_positive+=1
    for a,b in zip(bars,bars[1:]):
        delta=b.timestamp-a.timestamp
        if delta<=timedelta(0): duplicates+=1
        if expected_interval is not None and delta!=expected_interval: gaps+=1
    if duplicates: issues.append(f"{duplicates} duplicate/non-increasing timestamps")
    if gaps: issues.append(f"{gaps} interval mismatches/gaps")
    if non_positive: issues.append(f"{non_positive} bars contain non-positive prices")
    return DataQualityReport(not issues,len(bars),duplicates,gaps,non_positive,tuple(issues))
