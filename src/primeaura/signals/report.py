from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class SignalReport:
    signal_id:str
    instrument:str
    direction:str
    strategy_id:str
    strategy_version:str
    entry:Decimal
    stop_loss:Decimal
    take_profit:Decimal
    rr:Decimal
    confidence:Decimal
    thesis:str
    confluences:tuple[str,...]
    risk_factors:tuple[str,...]
    timestamp:str
    status:str="ACTIVE"

    def as_dict(self):
        return {"signal_id":self.signal_id,"instrument":self.instrument,"direction":self.direction,"strategy":{"id":self.strategy_id,"version":self.strategy_version},"entry":str(self.entry),"stop_loss":str(self.stop_loss),"take_profit":str(self.take_profit),"rr":str(self.rr),"confidence":str(self.confidence),"thesis":self.thesis,"confluences":self.confluences,"risk_factors":self.risk_factors,"timestamp":self.timestamp,"status":self.status}
