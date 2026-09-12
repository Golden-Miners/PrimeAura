from dataclasses import dataclass
from decimal import Decimal
from ..data.models import OHLCVBar
from .models import TradeResult

@dataclass(frozen=True)
class ExecutionCosts:
    spread: Decimal = Decimal("0")
    slippage: Decimal = Decimal("0")
    fee: Decimal = Decimal("0")

def apply_costs(price: Decimal, direction: str, costs: ExecutionCosts) -> Decimal:
    adjustment=costs.spread+costs.slippage
    return price + adjustment if direction=="SELL" else price-adjustment

def simulate_fixed_exit(entry: Decimal, target: Decimal, direction: str, risk_per_unit: Decimal, bars_held: int, costs: ExecutionCosts=ExecutionCosts()) -> TradeResult:
    if direction not in {"BUY","SELL"}: raise ValueError("direction must be BUY or SELL")
    if risk_per_unit<=0: raise ValueError("risk_per_unit must be positive")
    effective_exit=apply_costs(target,direction,costs)
    effective_entry=apply_costs(entry,"SELL" if direction=="BUY" else "BUY",costs)
    pnl=(effective_exit-effective_entry) if direction=="BUY" else (effective_entry-effective_exit)
    pnl-=costs.fee
    return TradeResult(entry=effective_entry,exit=effective_exit,direction=direction,pnl=pnl,r_multiple=pnl/risk_per_unit,bars_held=bars_held)

def chronological_split(bars: list[OHLCVBar], train_ratio: Decimal=Decimal("0.7")) -> tuple[list[OHLCVBar],list[OHLCVBar]]:
    if not (Decimal("0.5")<=train_ratio<Decimal("1")): raise ValueError("train_ratio must be between 0.5 and 1")
    cut=int(len(bars)*float(train_ratio))
    return bars[:cut],bars[cut:]

# Phase 6 note: execution costs and chronological splitting are intentionally explicit.
