from datetime import datetime,timezone
from decimal import Decimal
from uuid import uuid4
from .report import SignalReport

def build_signal_report(instrument,direction,strategy_id,strategy_version,entry,stop_loss,take_profit,confidence,thesis,confluences,risk_factors):
    risk=abs(entry-stop_loss)
    reward=abs(take_profit-entry)
    if risk<=0: raise ValueError("Signal risk must be positive")
    rr=reward/risk
    if rr<Decimal("2"): raise ValueError("Signal RR below PrimeAura minimum of 2.0")
    return SignalReport(str(uuid4()),instrument,direction,strategy_id,strategy_version,entry,stop_loss,take_profit,rr,confidence,thesis,tuple(confluences),tuple(risk_factors),datetime.now(timezone.utc).isoformat())
