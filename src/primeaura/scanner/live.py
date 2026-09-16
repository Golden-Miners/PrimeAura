from datetime import datetime
from ..data.market_service import MarketDataService
from ..data.integrity import validate_multitimeframe
from ..signals.report import SignalReport
from ..signals.store import SignalStore
from .diagnostic_store import DiagnosticStore
from .strategy_diagnostic_store import StrategyDiagnosticStore
from .diagnostics import diagnose_from_bars
from .multi_strategy import STRATEGIES, evaluate_strategies

class LiveScanner:
    """Read-only live scanner; evaluates every selected strategy independently."""
    def __init__(self,market=None,store=None,diagnostic_store=None,strategy_diagnostic_store=None):
        self.market=market or MarketDataService()
        self.store=store or SignalStore()
        self.diagnostic_store=diagnostic_store or DiagnosticStore()
        self.strategy_diagnostic_store=strategy_diagnostic_store or StrategyDiagnosticStore()

    def scan(self,instrument:str,count:int=500,selected_strategies=None):
        self.market.connect()
        try:
            bars=self.market.fetch_multi_timeframe(instrument,count)
            integrity=validate_multitimeframe(bars)
            if not integrity["valid"]:
                raise RuntimeError("MT5 data integrity failed: "+"; ".join(f"{tf}: {issue}" for tf,issues in integrity["issues"].items() for issue in issues[:5]))
            self.diagnostic_store.save(instrument,diagnose_from_bars(bars))
            selected=tuple(selected_strategies or STRATEGIES)
            signals,strategy_results=evaluate_strategies(instrument,bars,selected)
            self.strategy_diagnostic_store.save(instrument,strategy_results)
            reports=[]
            detected_at=datetime.now().astimezone()
            for s in signals:
                report=SignalReport(
                    signal_id=f"{instrument}-{s.strategy_id}-{s.strategy_version}-{s.direction}-{s.entry}",
                    instrument=s.instrument,direction=s.direction,strategy_id=s.strategy_id,
                    strategy_version=s.strategy_version,entry=s.entry,stop_loss=s.stop_loss,
                    take_profit=s.tp1,rr=s.rr_tp1,confidence=s.confidence,
                    thesis="; ".join(s.reasoning),confluences=s.reasoning,risk_factors=s.risk_factors,
                    timestamp=detected_at.isoformat(),take_profit_2=s.tp2,rr_2=s.rr_tp2,
                )
                self.store.append(report); reports.append(report)
            return tuple(reports),tuple(strategy_results)
        finally:
            self.market.close()
