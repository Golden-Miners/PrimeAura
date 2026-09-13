from datetime import datetime, timezone
from decimal import Decimal
import os

from .models import MarketSnapshot, OHLCVBar

TIMEFRAME_MAP = {"M5": "TIMEFRAME_M5", "M15": "TIMEFRAME_M15", "H1": "TIMEFRAME_H1"}

def _decimal(value) -> Decimal:
    return Decimal(str(value))

class MT5DataSource:
    """Read-only MT5 adapter; initialization occurs only when requested."""

    def __init__(self, terminal_path: str | None = None):
        self.terminal_path = terminal_path or os.getenv("PRIMEAURA_MT5_PATH")

    def connect(self) -> None:
        try:
            import MetaTrader5 as mt5
        except ImportError as exc:
            raise RuntimeError("MetaTrader5 package is not installed") from exc
        kwargs = {"path": self.terminal_path} if self.terminal_path else {}
        if not mt5.initialize(**kwargs):
            raise RuntimeError(f"MT5 initialization failed: {mt5.last_error()}")

    def shutdown(self) -> None:
        import MetaTrader5 as mt5
        mt5.shutdown()

    def _snapshot(self, instrument: str, timeframe: str, rates) -> MarketSnapshot:
        bars = tuple(
            OHLCVBar(
                instrument=instrument,
                timeframe=timeframe,
                timestamp=datetime.fromtimestamp(int(row["time"]), tz=timezone.utc),
                open=_decimal(row["open"]),
                high=_decimal(row["high"]),
                low=_decimal(row["low"]),
                close=_decimal(row["close"]),
                volume=_decimal(int(row["tick_volume"])),
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

    def bars(self, instrument: str, timeframe: str, count: int = 500) -> MarketSnapshot:
        if timeframe not in TIMEFRAME_MAP:
            raise ValueError(f"Unsupported PrimeAura timeframe: {timeframe}")
        if count <= 0:
            raise ValueError("count must be positive")
        import MetaTrader5 as mt5
        if not mt5.symbol_select(instrument, True):
            raise RuntimeError(f"MT5 symbol is unavailable: {instrument}")
        rates = mt5.copy_rates_from_pos(
            instrument, getattr(mt5, TIMEFRAME_MAP[timeframe]), 1, count
        )
        if rates is None:
            raise RuntimeError(
                f"MT5 returned no rates for {instrument} {timeframe}: {mt5.last_error()}"
            )
        return self._snapshot(instrument, timeframe, rates)

    def bars_range(
        self,
        instrument: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> MarketSnapshot:
        """Fetch closed historical candles for a bounded UTC date range."""
        if timeframe not in TIMEFRAME_MAP:
            raise ValueError(f"Unsupported PrimeAura timeframe: {timeframe}")
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("start and end must be timezone-aware")
        if start >= end:
            raise ValueError("start must be before end")

        import MetaTrader5 as mt5
        if not mt5.symbol_select(instrument, True):
            raise RuntimeError(f"MT5 symbol is unavailable: {instrument}")

        rates = mt5.copy_rates_range(
            instrument,
            getattr(mt5, TIMEFRAME_MAP[timeframe]),
            start.astimezone(timezone.utc),
            end.astimezone(timezone.utc),
        )
        if rates is None:
            raise RuntimeError(
                f"MT5 returned no historical rates for {instrument} {timeframe}: "
                f"{mt5.last_error()}"
            )
        # Exclude any candle that is still forming at the end boundary.
        return self._snapshot(instrument, timeframe, rates)
