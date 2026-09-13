from datetime import datetime

from .mt5 import MT5DataSource

class MarketDataService:
    def __init__(self, source: MT5DataSource | None = None):
        self.source = source or MT5DataSource()

    def connect(self):
        self.source.connect()

    def fetch_multi_timeframe(self, instrument: str, count: int = 500):
        return {
            tf: self.source.bars(instrument, tf, count).bars
            for tf in ("H1", "M15", "M5")
        }

    def fetch_multi_timeframe_range(self, instrument: str, start: datetime, end: datetime):
        return {
            tf: self.source.bars_range(instrument, tf, start, end).bars
            for tf in ("H1", "M15", "M5")
        }

    def close(self):
        self.source.shutdown()
