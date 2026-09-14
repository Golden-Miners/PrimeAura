from dataclasses import dataclass
from datetime import datetime

@dataclass
class SignalState:
    last_keys:dict[str,tuple]=None
    def __post_init__(self):
        if self.last_keys is None: self.last_keys={}
    def is_new(self,instrument:str,strategy_id:str,signal:dict)->bool:
        key=(signal.get("direction"),signal.get("entry"),signal.get("stop_loss"),signal.get("tp1"))
        if self.last_keys.get(f"{instrument}:{strategy_id}")==key: return False
        self.last_keys[f"{instrument}:{strategy_id}"]=key
        return True
