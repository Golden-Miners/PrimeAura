from dataclasses import dataclass
from pathlib import Path
import json
from .research_pipeline import ResearchResult

@dataclass(frozen=True)
class CatalogRecord:
    strategy_id:str
    version:str
    name:str
    instrument:str
    status:str
    net_r:str
    profit_factor:str|None
    max_drawdown_r:str
    trades:int
    evidence:str
    rejection_reasons:tuple[str,...]

class StrategyCatalog:
    def __init__(self,path:str="data/research/strategy_catalog.jsonl"): self.path=Path(path)
    def record(self,result:ResearchResult,instrument:str):
        m=result.aggregate_metrics; d=result.decision
        rec=CatalogRecord(result.candidate.metadata.strategy_id,result.candidate.metadata.version,result.candidate.metadata.name,instrument,d.status,str(m.net_r),str(m.profit_factor) if m.profit_factor is not None else None,str(m.max_drawdown_r),m.trades,result.candidate.source,d.reasons)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(rec.__dict__)+"\n")
    def all(self):
        if not self.path.exists(): return ()
        with self.path.open(encoding="utf-8") as f: return tuple(json.loads(x) for x in f if x.strip())
