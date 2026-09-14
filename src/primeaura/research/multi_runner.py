from dataclasses import dataclass
from .pipeline import ResearchRun,run_research
from .research_catalog import research_strategy_catalog
from ..strategies.pullback_reversion import trend_pullback,mean_reversion
from ..strategies.rule_based import momentum_continuation,volatility_breakout
from ..strategies.breakout_retest import breakout_retest

ADAPTERS={"trend-pullback":trend_pullback,"breakout-retest":breakout_retest,"momentum":momentum_continuation,"mean-reversion":mean_reversion,"volatility-breakout":volatility_breakout}

@dataclass(frozen=True)
class MultiResearchReport:
    runs:tuple[ResearchRun,...]

class MultiStrategyResearchRunner:
    """Runs each available strategy independently; no strategy is silently blended."""
    def run(self,instrument:str,bars,policy=None):
        runs=[]
        for spec in research_strategy_catalog():
            adapter=ADAPTERS.get(spec.strategy_id)
            if adapter is None: continue
            signals=[]
            for i in range(30,len(bars)):
                b=bars[:i+1]
                c={"close":[x.close for x in b],"high":[x.high for x in b],"low":[x.low for x in b]}
                result=adapter(instrument,c)
                if result:
                    from ..signals.models import Signal
                    signals.append(Signal(instrument=instrument,direction=result["direction"],strategy_id=spec.strategy_id,strategy_version=spec.version,entry=result["entry"],stop_loss=result["stop_loss"],tp1=result["tp1"],rr_tp1=result["rr"],confidence=50,reasoning=tuple(result.get("reasoning",()))))
            runs.append(run_research(spec.strategy_id,instrument,bars,signals,policy) if policy else run_research(spec.strategy_id,instrument,bars,signals))
        return MultiResearchReport(tuple(runs))
