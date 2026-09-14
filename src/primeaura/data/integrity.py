from collections import Counter
from datetime import datetime, timedelta

from .models import OHLCVBar

EXPECTED_MINUTES = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}


def _session_contains(ts: datetime, sessions: dict | None) -> bool:
    if not sessions:
        return False
    # MT5 session entries are normalized by the adapter to the UTC clock used
    # by PrimeAura bars. Callers should only pass sessions aligned to bar timestamps.
    seconds = ts.hour * 3600 + ts.minute * 60 + ts.second
    weekday = (ts.weekday() + 1) % 7  # Python Mon=0 -> MT5 Sun=0
    for session in sessions.get(weekday, []):
        start, end = session["from"], session["to"]
        if start <= end and start <= seconds <= end:
            return True
        if start > end and (seconds >= start or seconds <= end):
            return True
    return False


def _gap_is_session_closed(start: datetime, end: datetime, expected: timedelta, sessions: dict) -> bool:
    """Return True only when sampled points across a gap are outside trade sessions."""
    cursor = start + expected
    checked = 0
    while cursor < end:
        if _session_contains(cursor, sessions):
            return False
        cursor += expected
        checked += 1
    # A gap with no sampled open-session candle is treated as a session boundary.
    return checked > 0


def validate_bars(
    bars: list[OHLCVBar],
    sessions: dict | None = None,
) -> dict:
    if not bars:
        return {"valid": False, "status": "FAIL", "bar_count": 0, "issues": ["no_bars"], "warnings": []}

    issues: list[str] = []
    warnings: list[str] = []
    ordered = sorted(bars, key=lambda b: b.timestamp)
    timestamps = [b.timestamp for b in ordered]

    duplicates = [ts for ts, count in Counter(timestamps).items() if count > 1]
    if duplicates:
        issues.append(f"duplicate_timestamps:{len(duplicates)}")

    if any(a.timestamp >= b.timestamp for a, b in zip(bars, bars[1:])):
        issues.append("timestamps_not_strictly_increasing")

    for bar in ordered:
        if bar.timestamp.tzinfo is None or bar.timestamp.utcoffset() is None:
            issues.append(f"naive_timestamp:{bar.timestamp.isoformat()}")
        if bar.volume is not None and bar.volume < 0:
            issues.append(f"negative_volume:{bar.timestamp.isoformat()}")
        if not (bar.low <= bar.open <= bar.high and bar.low <= bar.close <= bar.high):
            issues.append(f"invalid_ohlc:{bar.timestamp.isoformat()}")
        if bar.low > bar.high:
            issues.append(f"low_above_high:{bar.timestamp.isoformat()}")

    timeframe = ordered[0].timeframe
    minutes = EXPECTED_MINUTES.get(timeframe)
    if minutes:
        expected = timedelta(minutes=minutes)
        for a, b in zip(ordered, ordered[1:]):
            delta = b.timestamp - a.timestamp
            if delta > expected:
                if sessions and _gap_is_session_closed(a.timestamp, b.timestamp, expected, sessions):
                    warnings.append(
                        f"session_boundary_gap:{a.timestamp.isoformat()}->{b.timestamp.isoformat()}"
                    )
                elif a.timestamp.date() == b.timestamp.date():
                    issues.append(f"time_gap:{a.timestamp.isoformat()}->{b.timestamp.isoformat()}")
                elif sessions:
                    warnings.append(
                        f"session_boundary_gap_unverified:{a.timestamp.isoformat()}->{b.timestamp.isoformat()}"
                    )
                else:
                    warnings.append(
                        f"cross_day_gap_unverified:{a.timestamp.isoformat()}->{b.timestamp.isoformat()}"
                    )

    status = "FAIL" if issues else ("WARNING" if warnings else "PASS")
    return {
        "valid": not issues,
        "status": status,
        "bar_count": len(bars),
        "timeframe": timeframe,
        "first_timestamp": timestamps[0],
        "last_timestamp": timestamps[-1],
        "issues": issues,
        "warnings": warnings,
    }


def validate_multitimeframe(
    bars_by_tf: dict[str, list[OHLCVBar]],
    sessions_by_tf: dict[str, dict] | None = None,
) -> dict:
    sessions_by_tf = sessions_by_tf or {}
    reports = {
        tf: validate_bars(bars, sessions_by_tf.get(tf))
        for tf, bars in bars_by_tf.items()
    }
    issues = {tf: report["issues"] for tf, report in reports.items() if report["issues"]}
    warnings = {tf: report["warnings"] for tf, report in reports.items() if report["warnings"]}
    return {
        "valid": not issues,
        "status": "FAIL" if issues else ("WARNING" if warnings else "PASS"),
        "timeframes": reports,
        "issues": issues,
        "warnings": warnings,
    }
