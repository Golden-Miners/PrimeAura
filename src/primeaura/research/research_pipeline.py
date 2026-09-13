from dataclasses import dataclass
from decimal import Decimal
from .evaluation import EvaluationMetrics
from .research_agent import StrategyCandidate
from .strategy_registry import ResearchStrategy
from .validation import ValidationDecision, ValidationPolicy, validate
from .walkforward import run_walk_forward

@dataclass(frozen=True)
class ResearchResult:
    candidate: StrategyCandidate
    decision: ValidationDecision
    walk_forward: object
    aggregate_metrics: EvaluationMetrics

class ResearchPipeline:
    def __init__(self, policy: ValidationPolicy = ValidationPolicy()):
        self.policy = policy

    def evaluate(self, candidate: StrategyCandidate, strategy: ResearchStrategy, bars):
        train_size = self.policy.min_trades
        test_size = max(1, self.policy.min_trades // 2)
        step = test_size
        walk_forward = run_walk_forward(bars, strategy, train_size, test_size, step)

        net_r = sum((m.net_r for m in walk_forward.metrics), Decimal("0"))
        trades = sum(m.trades for m in walk_forward.metrics)
        wins = sum(m.wins for m in walk_forward.metrics)
        losses = sum(m.losses for m in walk_forward.metrics)
        max_dd = max((m.max_drawdown_r for m in walk_forward.metrics), default=Decimal("0"))

        profit_factors = [m.profit_factor for m in walk_forward.metrics if m.profit_factor is not None]
        profit_factor = min(profit_factors) if profit_factors else None
        avg_r = net_r / trades if trades else Decimal("0")
        win_rate = Decimal(wins) / Decimal(trades) * Decimal("100") if trades else Decimal("0")

        metrics = EvaluationMetrics(
            trades=trades,
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            net_r=net_r,
            avg_r=avg_r,
            max_drawdown_r=max_dd,
            profit_factor=profit_factor,
        )
        decision = validate(metrics, len(walk_forward.folds), self.policy)
        return ResearchResult(candidate, decision, walk_forward, metrics)
