from dataclasses import dataclass
from decimal import Decimal
from ..data.models import OHLCVBar
from .indicators import atr, sma

@dataclass(frozen=True)
class MarketRegime:
    label: str
    volatility: str
    confidence: Decimal
    evidence: tuple[str, ...]


def classify_regime(bars: list[OHLCVBar], atr_period: int=14, trend_period: int=20) -> MarketRegime:
    if len(bars) < max(atr_period, trend_period):
        return MarketRegime("INSUFFICIENT_DATA","UNKNOWN",Decimal("0"),("Insufficient bars",))
    highs=[b.high for b in bars]; lows=[b.low for b in bars]; closes=[b.close for b in bars]
    a=atr(highs,lows,closes,atr_period)
    mean=sma(closes,trend_period)
    last=closes[-1]
    recent_range=max(highs[-trend_period:])-min(lows[-trend_period:])
    volatility="HIGH" if a >= recent_range/Decimal(trend_period)*Decimal("1.5") else "NORMAL"
    slope=closes[-1]-closes[-trend_period]
    if slope > a*Decimal("2"): label="TRENDING_BULLISH"
    elif slope < -a*Decimal("2"): label="TRENDING_BEARISH"
    elif recent_range <= a*Decimal("4"): label="RANGING"
    else: label="CONSOLIDATING"
    distance=abs(last-mean)/mean*Decimal("100")
    confidence=min(Decimal("100"),Decimal("50")+distance*Decimal("10"))
    return MarketRegime(label,volatility,confidence,(f"ATR={a}",f"close-vs-SMA distance={distance:.4f}%"))
