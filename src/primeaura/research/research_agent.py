from dataclasses import dataclass
from .strategy_registry import StrategyMetadata

@dataclass(frozen=True)
class StrategyCandidate:
    metadata: StrategyMetadata
    source: str
    hypothesis: str
    rules: tuple[str,...]
    validation_status: str = "UNTESTED"

class ResearchAgent:
    """Deterministic research workflow boundary; LLMs may propose candidates, never certify profitability."""
    def __init__(self, registry):
        self.registry=registry

    def submit_candidate(self, candidate: StrategyCandidate):
        if not candidate.rules:
            raise ValueError("Strategy candidate must contain explicit rules")
        if candidate.validation_status not in {"UNTESTED","RESEARCHING","VALIDATED","REJECTED"}:
            raise ValueError("Invalid validation status")
        return candidate

    def admissible_for_backtest(self, candidate: StrategyCandidate) -> bool:
        return candidate.validation_status in {"UNTESTED","RESEARCHING"}
