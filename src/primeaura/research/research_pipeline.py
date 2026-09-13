from dataclasses import dataclass
from .research_agent import StrategyCandidate
from .strategy_registry import ResearchStrategy
from .validation import ValidationDecision,ValidationPolicy,validate
from .walkforward import run_walk_forward

@dataclass(frozen=True)
class ResearchResult:
    candidate:StrategyCandidate
    decision:ValidationDecision
    walk_forward:object

class ResearchPipeline:
    def __init__(self,policy:ValidationPolicy=ValidationPolicy()):
        self.policy=policy

    def evaluate(self,candidate:StrategyCandidate,strategy:ResearchStrategy,bars):
        wf=run_walk_forward(bars,strategy,self.policy.min_trades,self.policy.min_trades//2,max(1,self.policy.min_trades//2))
        combined_net=sum((m.net_r for m in wf.metrics),start=__import__("decimal").Decimal("0"))
        combined_trades=sum(m.trades for m in wf.metrics)
        combined_wins=sum(m.wins for m in wf.metrics)
        combined_losses=sum(m.losses for m in wf.metrics)
        combined_pf=None
        gross_profit=sum((sum((x for x in []),__import__("decimal").Decimal("0")),),__import__("decimal").Decimal("0"))
        if wf.metrics:
            pfs=[m.profit_factor for m in wf.metrics if m.profit_factor is not None]
            combined_pf=min(pfs) if pfs else None
        from .evaluation import EvaluationMetrics
        dd=max((m.max_drawdown_r for m in wf.metrics),default=__import__("decimal").Decimal("0"))
        avg=combined_net/combined_trades if combined_trades else __import__("decimal").Decimal("0")
        metrics=EvaluationMetrics(combined_trades,combined_wins,combined_losses,(__import__("decimal").Decimal(combined_wins)/combined_trades*100 if combined_trades else __import__("decimal").Decimal("0")),combined_net,avg,dd,combined_pf)
        decision=validate(metrics,len(wf.folds),self.policy)
        return ResearchResult(candidate,decision,wf)
