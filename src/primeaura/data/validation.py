from .models import MarketSnapshot

class MarketDataValidationError(ValueError):
    pass

def validate_snapshot(snapshot: MarketSnapshot) -> MarketSnapshot:
    previous_timestamp = None
    for bar in snapshot.bars:
        if bar.instrument != snapshot.instrument: raise MarketDataValidationError("Bar instrument mismatch.")
        if bar.timeframe != snapshot.timeframe: raise MarketDataValidationError("Bar timeframe mismatch.")
        if bar.high < max(bar.open, bar.close, bar.low): raise MarketDataValidationError("High is below an OHLC value.")
        if bar.low > min(bar.open, bar.close, bar.high): raise MarketDataValidationError("Low is above an OHLC value.")
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp: raise MarketDataValidationError("Bars must be strictly chronological.")
        previous_timestamp = bar.timestamp
    return snapshot
