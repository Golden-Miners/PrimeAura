from .models import StrategyDefinition

class StrategyRegistry:
    def __init__(self) -> None:
        self._items: dict[tuple[str,str], StrategyDefinition] = {}

    def register(self, strategy: StrategyDefinition) -> None:
        key=(strategy.strategy_id,strategy.version)
        if key in self._items: raise ValueError(f"Strategy version already registered: {key}")
        self._items[key]=strategy

    def get(self, strategy_id: str, version: str) -> StrategyDefinition:
        return self._items[(strategy_id,version)]

    def all(self) -> tuple[StrategyDefinition, ...]:
        return tuple(self._items.values())
