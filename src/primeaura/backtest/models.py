from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class TradeResult(BaseModel):
    model_config=ConfigDict(frozen=True,extra="forbid")
    entry: Decimal
    exit: Decimal
    direction: str
    pnl: Decimal
    r_multiple: Decimal
    bars_held: int = Field(ge=0)

class BacktestMetrics(BaseModel):
    model_config=ConfigDict(frozen=True,extra="forbid")
    trade_count: int = Field(ge=0)
    wins: int = Field(ge=0)
    losses: int = Field(ge=0)
    win_rate: Decimal = Field(ge=0,le=100)
    net_pnl: Decimal
    max_drawdown: Decimal = Field(ge=0)
    profit_factor: Decimal = Field(ge=0)

class ValidationResult(BaseModel):
    model_config=ConfigDict(frozen=True,extra="forbid")
    stage: str
    passed: bool
    metrics: BacktestMetrics
    notes: tuple[str,...]=()
