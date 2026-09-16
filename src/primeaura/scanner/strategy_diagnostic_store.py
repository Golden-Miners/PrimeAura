import json
from dataclasses import asdict
from pathlib import Path

class StrategyDiagnosticStore:
    def __init__(self,path="data/signals/strategy_diagnostics.json"):
        self.path=Path(path)
    def save(self,instrument,results):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        data=self.load()
        data[instrument]=[{"strategy_id":r.strategy_id,"status":r.status,"has_signal":r.signal is not None,"reason":r.reason} for r in results]
        self.path.write_text(json.dumps(data,indent=2),encoding="utf-8")
    def load(self):
        if not self.path.exists(): return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
