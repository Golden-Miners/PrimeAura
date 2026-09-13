from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class SignalReport:
    signal_id: str
    instrument: str
    direction: str
    strategy_id: str
    strategy_version: str
    entry: Decimal
    stop_loss: Decimal
    take_profit: Decimal
    rr: Decimal
    confidence: Decimal
    thesis: str
    confluences: tuple[str, ...]
    risk_factors: tuple[str, ...]
    timestamp: str
    status: str = "ACTIVE"
    take_profit_2: Decimal | None = None
    rr_2: Decimal | None = None

    def as_dict(self):
        return {
            "signal_id": self.signal_id,
            "instrument": self.instrument,
            "direction": self.direction,
            "strategy": {"id": self.strategy_id, "version": self.strategy_version},
            "entry": str(self.entry),
            "stop_loss": str(self.stop_loss),
            "take_profit": str(self.take_profit),
            "rr": str(self.rr),
            "take_profit_2": str(self.take_profit_2) if self.take_profit_2 is not None else None,
            "rr_2": str(self.rr_2) if self.rr_2 is not None else None,
            "confidence": str(self.confidence),
            "thesis": self.thesis,
            "confluences": self.confluences,
            "risk_factors": self.risk_factors,
            "timestamp": self.timestamp,
            "status": self.status,
        }
