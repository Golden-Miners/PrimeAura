from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class Signal(BaseModel):
    model_config=ConfigDict(frozen=True,extra="forbid")
    instrument: str
    timestamp: datetime | None = None
    direction: str
    strategy_id: str
    strategy_version: str
    entry: Decimal
    stop_loss: Decimal
    tp1: Decimal
    tp2: Decimal | None = None
    rr_tp1: Decimal = Field(gt=0)
    rr_tp2: Decimal | None = None
    confidence: Decimal = Field(ge=0,le=100)
    reasoning: tuple[str,...]
    risk_factors: tuple[str,...]=()
