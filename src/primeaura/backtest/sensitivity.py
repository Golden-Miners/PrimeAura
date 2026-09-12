from decimal import Decimal

def stable_parameter_ranges(results: dict[str, Decimal], minimum_profit_factor: Decimal=Decimal("1.0")) -> tuple[str,...]:
    """Return parameter labels meeting a robustness floor; caller supplies OOS results."""
    return tuple(k for k,v in results.items() if v >= minimum_profit_factor)
