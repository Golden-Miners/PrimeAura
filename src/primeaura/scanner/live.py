from datetime import datetime, timezone

from ..data.market_service import MarketDataService
from ..signals.report import SignalReport
from ..signals.store import SignalStore
from .diagnostic_store import DiagnosticStore
from .diagnostics import diagnose_from_bars
from .pipeline import generate_from_bars

class LiveScanner:
    """Read-only live scanner. MT5 is initialized only when a scan is requested."""
    def __init__(
        self,
        market: MarketDataService | None = None,
        store: SignalStore | None = None,
        diagnostic_store: DiagnosticStore | None = None,
    ):
        self.market = market or MarketDataService()
        self.store = store or SignalStore()
        self.diagnostic_store = diagnostic_store or DiagnosticStore()

    def scan(self, instrument: str, count: int = 500) -> tuple[SignalReport, ...]:
        self.market.connect()
        try:
            bars = self.market.fetch_multi_timeframe(instrument, count)
            diagnostics = diagnose_from_bars(bars)
            self.diagnostic_store.save(instrument, diagnostics)
            signals = generate_from_bars(instrument, bars)
            reports = []
            for s in signals:
                report = SignalReport(
                    signal_id=f"{instrument}-{s.strategy_id}-{s.strategy_version}-{s.entry}",
                    instrument=s.instrument,
                    direction=s.direction,
                    strategy_id=s.strategy_id,
                    strategy_version=s.strategy_version,
                    entry=s.entry,
                    stop_loss=s.stop_loss,
                    take_profit=s.tp1,
                    rr=s.rr_tp1,
                    confidence=s.confidence,
                    thesis="; ".join(s.reasoning),
                    confluences=s.reasoning,
                    risk_factors=s.risk_factors,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    take_profit_2=s.tp2,
                    rr_2=s.rr_tp2,
                )
                self.store.append(report)
                reports.append(report)
            return tuple(reports)
        finally:
            self.market.close()
