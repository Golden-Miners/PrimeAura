from dataclasses import asdict,dataclass
from pathlib import Path
import json
from .self_improvement import Experiment,ImprovementDecision

@dataclass(frozen=True)
class ExperimentEvidence:
    experiment_id:str
    baseline_strategy:str
    baseline_net_r:str
    challenger_net_r:str
    validation_status:str
    decision:str
    notes:tuple[str,...]=()

class ExperimentStore:
    def __init__(self,path:str="data/research/experiments.jsonl"): self.path=Path(path)

    def record(self,evidence:ExperimentEvidence):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(asdict(evidence))+"\n")

    def all(self):
        if not self.path.exists(): return ()
        with self.path.open(encoding="utf-8") as f: return tuple(json.loads(x) for x in f if x.strip())
