import json
from pathlib import Path
from .research_agent import StrategyCandidate

class ResearchStore:
    def __init__(self,path:str="data/research/strategy_candidates.jsonl"):
        self.path=Path(path)

    def append(self,candidate:StrategyCandidate):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        record={"strategy_id":candidate.metadata.strategy_id,"version":candidate.metadata.version,"name":candidate.metadata.name,"description":candidate.metadata.description,"instruments":candidate.metadata.instruments,"timeframes":candidate.metadata.timeframes,"source":candidate.source,"hypothesis":candidate.hypothesis,"rules":candidate.rules,"validation_status":candidate.validation_status}
        with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(record)+"\n")

    def read_all(self):
        if not self.path.exists(): return ()
        with self.path.open("r",encoding="utf-8") as f: return tuple(json.loads(x) for x in f if x.strip())
