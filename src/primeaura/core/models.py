from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from .enums import SignalDirection, SignalStatus


class PriceLevels(BaseModel):
    model_config = ConfigDict(frozen=True)

    entry: Decimal
    stop_loss: Decimal
    tp1: Decimal
    tp2: Decimal

    @property
    def risk(self) -> Decimal:
        return abs(self.entry - self.stop_loss)


class Signal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    signal_id: str
    instrument: str
    direction: SignalDirection
    status: SignalStatus = SignalStatus.GENERATED
    timeframe: str
    strategy: str
    strategy_version: str
    levels: PriceLevels
    rr_tp1: Decimal = Field(ge=Decimal("0"))
    rr_tp2: Decimal = Field(ge=Decimal("0"))
    confidence: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))
    reasoning: str
    supporting_evidence: list[str] = Field(default_factory=list)
    conflicting_evidence: list[str] = Field(default_factory=list)
    generated_at: datetime
    valid_until: datetime | None = None
    invalidation_reason: str | None = None
