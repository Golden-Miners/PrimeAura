from pathlib import Path
import json
from dataclasses import asdict
from .report import SignalReport

class SignalStore:
    def __init__(self,path:str="data/signals/signal_history.jsonl"): self.path=Path(path)
    def append(self,signal:SignalReport):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(asdict(signal))+"\n")
    def recent(self,limit:int=100):
        if limit<=0: return ()
        if not self.path.exists(): return ()
        with self.path.open(encoding="utf-8") as f: rows=[json.loads(x) for x in f if x.strip()]
        return tuple(rows[-limit:][::-1])
