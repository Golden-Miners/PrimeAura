from decimal import Decimal
import random
from ..backtest.models import TradeResult

def max_drawdown_path(trades: list[TradeResult]) -> Decimal:
    equity=peak=dd=Decimal(0)
    for t in trades:
        equity+=t.pnl; peak=max(peak,equity); dd=max(dd,peak-equity)
    return dd

def monte_carlo_drawdown(trades:list[TradeResult], simulations:int=1000, seed:int=42)->dict[str,Decimal]:
    if not trades or simulations<1: raise ValueError("trades and simulations required")
    rng=random.Random(seed); dds=[]
    for _ in range(simulations):
        sample=rng.choices(trades,k=len(trades)); dds.append(max_drawdown_path(sample))
    dds.sort()
    return {"p50":dds[int(simulations*.50)],"p95":dds[min(simulations-1,int(simulations*.95))],"p99":dds[min(simulations-1,int(simulations*.99))]}
