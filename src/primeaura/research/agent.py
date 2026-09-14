from dataclasses import dataclass
from decimal import Decimal
from .mt5_runner import InstrumentResearch

@dataclass(frozen=True)
class ResearchFinding:
    instrument:str
    strategy_id:str
    verdict:str
    evidence:tuple[str,...]

class ResearchAgent:
    """Evidence-first analyst. It reports findings; it cannot mutate strategy code or execute trades."""
    def analyze(self,research:InstrumentResearch)->tuple[ResearchFinding,...]:
        findings=[]
        for run in research.report.runs:
            m=run.metrics; evidence=[f"trades={m.trades}",f"net_r={m.net_r}",f"profit_factor={m.profit_factor}"]
            if run.validation_status=="CANDIDATE_FOR_OOS": verdict="CANDIDATE"
            else: verdict="RESEARCH_ONLY"
            findings.append(ResearchFinding(research.instrument,run.strategy_id,verdict,tuple(evidence)))
        return tuple(findings)
