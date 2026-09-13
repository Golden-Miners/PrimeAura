from datetime import datetime, timedelta, timezone
from ..data.mt5_provider import MT5MarketDataProvider

class MT5RecentProvider:
    """Small adapter used by the scanner; read-only market data only."""
    def __init__(self, provider: MT5MarketDataProvider):
        self.provider = provider

    def recent(self, instrument: str, timeframe: str, bars: int):
        minutes = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}.get(timeframe)
        if minutes is None:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        end = datetime.now(timezone.utc)
        start = end - timedelta(minutes=minutes * (bars + 5))
        return self.provider.history(instrument, timeframe, start, end)[-bars:]
