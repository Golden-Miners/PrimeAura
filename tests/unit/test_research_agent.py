from primeaura.research.research_agent import ResearchAgent,StrategyCandidate
from primeaura.research.strategy_registry import StrategyMetadata,StrategyRegistry
from decimal import Decimal
from types import SimpleNamespace

def c(rules=("close above high",)):
    return StrategyCandidate(StrategyMetadata("candidate","0.1","Candidate","test",("XAUUSD",),("M15",)),"manual","test",rules)

def test_candidate_requires_explicit_rules():
    a=ResearchAgent(StrategyRegistry())
    assert a.submit_candidate(c()).validation_status=="UNTESTED"
    assert a.admissible_for_backtest(c())

def test_evidence_finding_is_reported():
    a=SimpleNamespace(trades=120,net_r=Decimal("20"),profit_factor=Decimal("1.5"))
    run=SimpleNamespace(strategy_id="momentum",metrics=a,validation_status="CANDIDATE_FOR_OOS")
    research=SimpleNamespace(instrument="XAUUSD",report=SimpleNamespace(runs=(run,)))
    from primeaura.research.agent import ResearchAgent as EvidenceAgent
    finding=EvidenceAgent().analyze(research)[0]
    assert finding.verdict=="CANDIDATE"
    assert "trades=120" in finding.evidence
