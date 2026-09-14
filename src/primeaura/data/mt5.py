from datetime import datetime, timedelta, timezone
from decimal import Decimal
import os
from pathlib import Path
import sys

from .models import MarketSnapshot, OHLCVBar

TIMEFRAME_MAP = {"M5": "TIMEFRAME_M5", "M15": "TIMEFRAME_M15", "H1": "TIMEFRAME_H1"}

def _decimal(value) -> Decimal:
    return Decimal(str(value))


def _server_offset(rates) -> timedelta:
    """Resolve an MT5 broker-server clock offset for live bar timestamps.

    MetaTrader feeds can expose broker-local candle epochs. PrimeAura stores
    timestamps as UTC, so an explicit PRIMEAURA_MT5_SERVER_OFFSET_HOURS value
    takes precedence. Otherwise, when the newest closed bar is in the future
    by roughly a whole number of hours, infer that whole-hour offset. If the
    feed already looks like UTC, leave it unchanged.
    """
    configured = os.getenv("PRIMEAURA_MT5_SERVER_OFFSET_HOURS")
    if configured is not None:
        try:
            return timedelta(hours=int(configured))
        except ValueError as exc:
            raise RuntimeError(
                "PRIMEAURA_MT5_SERVER_OFFSET_HOURS must be an integer number of hours"
            ) from exc

    if rates is None or len(rates) == 0:
        return timedelta(0)

    latest_raw = datetime.fromtimestamp(int(rates[-1]["time"]), tz=timezone.utc)
    future_hours = (latest_raw - datetime.now(timezone.utc)).total_seconds() / 3600
    if 1.0 <= future_hours <= 12.0:
        rounded = round(future_hours)
        if abs(future_hours - rounded) <= 0.25:
            return timedelta(hours=rounded)
    return timedelta(0)

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

        # Session times are broker-server seconds from midnight. Normalize
        # them to the same UTC clock used by PrimeAura's OHLCV bars.
        probe = mt5.copy_rates_from_pos(
            instrument, getattr(mt5, TIMEFRAME_MAP["M5"]), 1, 1
        )
        offset = _server_offset(probe)
        offset_seconds = int(offset.total_seconds())

        def normalize_second(value: int) -> int:
            return (int(value) - offset_seconds) % 86400

        sessions = {}
        for day in range(7):
            day_sessions = []
            index = 0
            while True:
                session = mt5.symbol_info_session_trade(instrument, day, index)
                if session is None:
                    break
                day_sessions.append({
                    "from": normalize_second(session[0]),
                    "to": normalize_second(session[1]),
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

    def _snapshot(self, instrument: str, timeframe: str, rates, offset: timedelta = timedelta(0)) -> MarketSnapshot:
        bars = tuple(
            OHLCVBar(
                instrument=instrument,
                timeframe=timeframe,
                timestamp=datetime.fromtimestamp(int(row["time"]), tz=timezone.utc) - offset,
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
        return self._snapshot(instrument, timeframe, rates, _server_offset(rates))

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
        # MT5 broker feeds may expose broker-local epochs. Normalize them to
        # PrimeAura UTC before integrity checks and chronological replay.
        return self._snapshot(instrument, timeframe, rates, _server_offset(rates))
