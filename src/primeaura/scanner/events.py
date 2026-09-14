from dataclasses import dataclass,asdict
from datetime import datetime
import json

@dataclass(frozen=True)
class SignalEvent:
    instrument:str
    strategy_id:str
    direction:str
    entry:object
    stop_loss:object
    tp1:object
    rr:object
    reasoning:tuple[str,...]
    detected_at:datetime
    def to_dict(self):
        d=asdict(self); d["detected_at"]=self.detected_at.isoformat(); d["reasoning"]=list(self.reasoning); return d
    def to_json(self): return json.dumps(self.to_dict(),default=str,sort_keys=True)

def signal_event_from_result(result,detected_at:datetime)->SignalEvent:
    s=result.signal
    return SignalEvent(result.instrument,result.strategy_id,s["direction"],s["entry"],s["stop_loss"],s["tp1"],s["rr"],tuple(s.get("reasoning",())),detected_at)
