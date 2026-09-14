from decimal import Decimal
from .models import StrategyDefinition

def research_strategy_catalog()->tuple[StrategyDefinition,...]:
    """Research candidates; none are claimed profitable until validated OOS."""
    common=dict(instruments=("XAUUSD","XAGUSD"),timeframes=("H1","M15","M5"),minimum_rr=Decimal("2.0"),status="RESEARCH_ONLY")
    return tuple(StrategyDefinition(strategy_id=i,name=n,version="0.1.0",description=d,**common) for i,n,d in (
        ("trend-pullback","Trend Pullback","Higher-timeframe trend with pullback and continuation confirmation."),
        ("breakout-retest","Breakout Retest","Confirmed level breakout followed by retest and continuation."),
        ("momentum","Momentum Continuation","Volatility/momentum continuation with regime filters."),
        ("mean-reversion","Mean Reversion","Extreme-to-mean setup with regime filters."),
        ("volatility-breakout","Volatility Breakout","Volatility expansion breakout with independent validation."),
    ))
