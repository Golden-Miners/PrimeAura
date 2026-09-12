from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class OHLCVBar(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    instrument: str
    timeframe: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None = None

class MarketSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    instrument: str
    timeframe: str
    bars: tuple[OHLCVBar, ...]
    source: str
    retrieved_at: datetime
    @property
    def bar_count(self) -> int:
        return len(self.bars)
