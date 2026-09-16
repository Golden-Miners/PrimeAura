from pathlib import Path
import json
from .report import SignalReport

class SignalStore:
    def __init__(self,path:str="data/signals/signal_history.jsonl"): self.path=Path(path)
    def append(self,signal:SignalReport):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        if self.path.exists():
            with self.path.open(encoding="utf-8") as f:
                if any(json.loads(x).get("signal_id")==signal.signal_id for x in f if x.strip()):
                    return
        with self.path.open("a",encoding="utf-8") as f:
            json.dump(signal.as_dict(),f,default=str); f.write("\n")
    def recent(self,limit:int=100):
        if limit<=0 or not self.path.exists(): return ()
        with self.path.open(encoding="utf-8") as f: rows=[json.loads(x) for x in f if x.strip()]
        return tuple(rows[-limit:][::-1])
