from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class StrategyDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    strategy_id: str
    name: str
    version: str
    description: str
    instruments: tuple[str, ...] = ()
    timeframes: tuple[str, ...] = ()
    minimum_rr: Decimal = Field(default=Decimal("2.0"), ge=Decimal("0"))
    status: str = "DISCOVERED"
    parameters: dict[str, str] = Field(default_factory=dict)

class StrategySignal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    strategy_id: str
    strategy_version: str
    direction: str
    entry: Decimal | None = None
    stop_loss: Decimal | None = None
    tp1: Decimal | None = None
    tp2: Decimal | None = None
    rationale: tuple[str, ...] = ()
