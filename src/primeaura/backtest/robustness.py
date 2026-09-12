from decimal import Decimal
from .models import TradeResult

def bootstrap_r_multiple(trades: list[TradeResult], samples: int=1000, seed: int=42) -> dict[str,Decimal]:
    """Deterministic bootstrap summary for reproducible research tests."""
    if not trades or samples<1: raise ValueError("trades and samples required")
    import random
    rng=random.Random(seed)
    distributions=[]
    for _ in range(samples):
        draw=rng.choices(trades,k=len(trades))
        distributions.append(sum((x.r_multiple for x in draw),Decimal("0")))
    distributions.sort()
    return {"p05":distributions[int(samples*.05)],"median":distributions[int(samples*.50)],"p95":distributions[min(samples-1,int(samples*.95))]}
