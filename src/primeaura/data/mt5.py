from datetime import datetime, timezone
from pathlib import Path
import os

from .models import MarketSnapshot, OHLCVBar

TIMEFRAME_MAP = {
    "M5": "TIMEFRAME_M5",
    "M15": "TIMEFRAME_M15",
    "H1": "TIMEFRAME_H1",
}

class MT5DataSource:
    """Read-only MT5 market-data adapter.

    initialize() may start the installed MT5 terminal when the Python
    MetaTrader5 package can locate it. MT5 login/trading credentials are
    intentionally not managed here.
    """

    def __init__(self, terminal_path: str | None = None):
        self.terminal_path = terminal_path or os.getenv("PRIMEAURA_MT5_PATH")

    def connect(self) -> None:
        try:
            import MetaTrader5 as mt5
        except ImportError as exc:
            raise RuntimeError("MetaTrader5 package is not installed") from exc

        kwargs = {"path": self.terminal_path} if self.terminal_path else {}
        if not mt5.initialize(**kwargs):
            code = mt5.last_error()
            raise RuntimeError(f"MT5 initialization failed: {code}")

    def shutdown(self) -> None:
        import MetaTrader5 as mt5
        mt5.shutdown()

    def bars(self, instrument: str, timeframe: str, count: int = 500) -> MarketSnapshot:
        if timeframe not in TIMEFRAME_MAP:
            raise ValueError(f"Unsupported PrimeAura timeframe: {timeframe}")
        if count <= 0:
            raise ValueError("count must be positive")

        import MetaTrader5 as mt5
        if not mt5.symbol_select(instrument, True):
            raise RuntimeError(f"MT5 symbol is unavailable: {instrument}")

        rates = mt5.copy_rates_from_pos(instrument, getattr(mt5, TIMEFRAME_MAP[timeframe]), 0, count)
        if rates is None:
            raise RuntimeError(f"MT5 returned no rates for {instrument} {timeframe}: {mt5.last_error()}")

        bars = tuple(
            OHLCVBar(
                instrument=instrument,
                timeframe=timeframe,
                timestamp=datetime.fromtimestamp(int(row["time"]), tz=timezone.utc),
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["tick_volume"],
            )
            for row in rates
        )
        return MarketSnapshot(
            instrument=instrument,
            timeframe=timeframe,
            bars=bars,
            source="MT5",
            retrieved_at=datetime.now(timezone.utc),
        )
