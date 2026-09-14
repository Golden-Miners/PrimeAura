from datetime import datetime, timezone
from decimal import Decimal
import os
from pathlib import Path
import sys

from .models import MarketSnapshot, OHLCVBar

TIMEFRAME_MAP = {"M5": "TIMEFRAME_M5", "M15": "TIMEFRAME_M15", "H1": "TIMEFRAME_H1"}

def _decimal(value) -> Decimal:
    return Decimal(str(value))

class MT5DataSource:
    """Read-only MT5 adapter; initialization occurs only when requested."""

    def __init__(self, terminal_path: str | None = None):
        self.terminal_path = terminal_path or os.getenv("PRIMEAURA_MT5_PATH")

    def _discover_terminal_path(self) -> str | None:
        """Find a local MT5 terminal when no explicit path is configured."""
        if self.terminal_path:
            return self.terminal_path
        if sys.platform != "win32":
            return None

        candidates = [
            Path(os.environ.get("PROGRAMFILES", "")) / "MetaTrader 5" / "terminal64.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "MetaTrader 5" / "terminal64.exe",
        ]
        for root_name in ("LOCALAPPDATA", "APPDATA"):
            root = Path(os.environ.get(root_name, ""))
            candidates.extend(root.glob("MetaQuotes/Terminal/*/terminal64.exe"))

        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
        return None

    def connect(self) -> None:
        try:
            import MetaTrader5 as mt5
        except ImportError as exc:
            raise RuntimeError("MetaTrader5 package is not installed") from exc
        terminal_path = self._discover_terminal_path()
        # initialize() connects to an existing terminal or starts it when required.
        kwargs = {"path": terminal_path} if terminal_path else {}
        if not mt5.initialize(**kwargs):
            raise RuntimeError(
                f"MT5 initialization failed: {mt5.last_error()}. "
                "Set PRIMEAURA_MT5_PATH if your terminal is installed in a custom location."
            )

    def shutdown(self) -> None:
        import MetaTrader5 as mt5
        mt5.shutdown()

    def session_info(self, instrument: str) -> dict:
        """Return broker-provided symbol/session metadata without placing orders."""
        import MetaTrader5 as mt5

        if not mt5.symbol_select(instrument, True):
            raise RuntimeError(f"MT5 symbol is unavailable: {instrument}")
        info = mt5.symbol_info(instrument)
        if info is None:
            raise RuntimeError(f"MT5 symbol_info failed for {instrument}: {mt5.last_error()}")

        sessions = {}
        for day in range(7):
            day_sessions = []
            index = 0
            while True:
                session = mt5.symbol_info_session_trade(instrument, day, index)
                if session is None:
                    break
                day_sessions.append({
                    "from": session[0],
                    "to": session[1],
                })
                index += 1
            sessions[day] = day_sessions

        return {
            "name": info.name,
            "trade_mode": info.trade_mode,
            "digits": info.digits,
            "point": float(info.point),
            "sessions": sessions,
        }

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
        # copy_rates_range is bounded by the requested UTC interval; PrimeAura
        # also requests only closed bars at scan time. Keep the adapter read-only.
        return self._snapshot(instrument, timeframe, rates)
