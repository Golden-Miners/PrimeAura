from decimal import Decimal

def true_range(high: Decimal, low: Decimal, previous_close: Decimal | None) -> Decimal:
    if previous_close is None: return high - low
    return max(high-low, abs(high-previous_close), abs(low-previous_close))

def sma(values: list[Decimal], period: int) -> Decimal:
    if period <= 0 or len(values) < period: raise ValueError("Insufficient values for SMA")
    return sum(values[-period:], Decimal("0")) / Decimal(period)

def atr(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], period: int = 14) -> Decimal:
    if period <= 0 or len(highs) != len(lows) or len(lows) != len(closes) or len(closes) < period: raise ValueError("Invalid ATR input")
    trs=[true_range(highs[i],lows[i],None if i==0 else closes[i-1]) for i in range(len(closes))]
    return sum(trs[-period:], Decimal("0")) / Decimal(period)
