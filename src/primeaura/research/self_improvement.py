from dataclasses import dataclass
from datetime import datetime,timezone
from .strategy_registry import StrategyMetadata

@dataclass(frozen=True)
class Experiment:
    experiment_id:str
    parent_strategy_id:str
    parent_version:str
    proposed_change:str
    created_at:str
    status:str="PROPOSED"

@dataclass(frozen=True)
class ImprovementDecision:
    experiment_id:str
    accepted:bool
    reason:str

class SelfImprovementAgent:
    """Proposes versioned changes; promotion is external and evidence-gated."""
    def propose(self,parent:StrategyMetadata,change:str,experiment_id:str)->Experiment:
        if not change.strip(): raise ValueError("Improvement change cannot be empty")
        return Experiment(experiment_id,parent.strategy_id,parent.version,change,datetime.now(timezone.utc).isoformat())

    def decide(self,experiment:Experiment,baseline_net_r,challenger_net_r,validated:bool)->ImprovementDecision:
        if not validated: return ImprovementDecision(experiment.experiment_id,False,"Challenger did not pass validation")
        if challenger_net_r<=baseline_net_r: return ImprovementDecision(experiment.experiment_id,False,"Challenger did not improve net R")
        return ImprovementDecision(experiment.experiment_id,True,"Challenger improved net R and passed validation")
