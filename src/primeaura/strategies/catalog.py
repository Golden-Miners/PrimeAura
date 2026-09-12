from decimal import Decimal
from .models import StrategyDefinition
from .smc_v1 import STRATEGY_ID

def built_in_strategies() -> tuple[StrategyDefinition,...]:
    return (StrategyDefinition(strategy_id=STRATEGY_ID,name="SMC Confluence Research Prototype",version="0.1.0",description="Experimental deterministic SMC confluence strategy for research/backtesting only.",instruments=("XAUUSD","XAGUSD"),timeframes=("H1","M15","M5"),minimum_rr=Decimal("2.0"),status="FORMALIZED"),)
