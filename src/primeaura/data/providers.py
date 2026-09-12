from abc import ABC, abstractmethod
from datetime import datetime
from .models import MarketSnapshot

class MarketDataProvider(ABC):
    @abstractmethod
    def get_bars(self, instrument: str, timeframe: str, start: datetime, end: datetime) -> MarketSnapshot:
        raise NotImplementedError
