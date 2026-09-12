from abc import ABC, abstractmethod
from datetime import datetime
from ..data.models import OHLCVBar

class MarketDataProvider(ABC):
    @abstractmethod
    def history(self,instrument:str,timeframe:str,start:datetime,end:datetime)->list[OHLCVBar]: ...

class CsvMarketDataProvider(MarketDataProvider):
    def __init__(self,root:str): self.root=root
    def history(self,instrument:str,timeframe:str,start:datetime,end:datetime)->list[OHLCVBar]:
        from .market_feed import load_ohlcv_csv
        bars=load_ohlcv_csv(f"{self.root}/{instrument}_{timeframe}.csv",instrument,timeframe)
        return [b for b in bars if start<=b.timestamp<end]
