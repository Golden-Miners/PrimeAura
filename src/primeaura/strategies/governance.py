from .models import StrategyDefinition

VALID_TRANSITIONS={
    "DISCOVERED":{"FORMALIZED"},
    "FORMALIZED":{"BACKTESTED"},
    "BACKTESTED":{"ROBUSTNESS_TESTED"},
    "ROBUSTNESS_TESTED":{"WALK_FORWARD_TESTED"},
    "WALK_FORWARD_TESTED":{"CANDIDATE"},
    "CANDIDATE":{"ACTIVE","RETIRED"},
    "ACTIVE":{"RETIRED"},
    "RETIRED":set(),
}

def promote(strategy: StrategyDefinition, new_status: str) -> StrategyDefinition:
    allowed=VALID_TRANSITIONS.get(strategy.status,set())
    if new_status not in allowed: raise ValueError(f"Invalid transition {strategy.status} -> {new_status}")
    return strategy.model_copy(update={"status":new_status})
