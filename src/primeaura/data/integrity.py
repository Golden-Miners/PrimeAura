from collections import Counter
from datetime import timedelta
from decimal import Decimal

from .models import OHLCVBar

EXPECTED_MINUTES = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}


def validate_bars(bars: list[OHLCVBar]) -> dict:
    if not bars:
        return {"valid": False, "bar_count": 0, "issues": ["no_bars"]}

    issues: list[str] = []
    ordered = sorted(bars, key=lambda b: b.timestamp)
    timestamps = [b.timestamp for b in ordered]
    duplicates = [ts for ts, count in Counter(timestamps).items() if count > 1]
    if duplicates:
        issues.append(f"duplicate_timestamps:{len(duplicates)}")

    if any(a.timestamp >= b.timestamp for a, b in zip(bars, bars[1:])):
        issues.append("timestamps_not_strictly_increasing")

    for bar in ordered:
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
                issues.append(f"time_gap:{a.timestamp.isoformat()}->{b.timestamp.isoformat()}")

    return {
        "valid": not issues,
        "bar_count": len(bars),
        "timeframe": timeframe,
        "first_timestamp": timestamps[0],
        "last_timestamp": timestamps[-1],
        "issues": issues,
    }


def validate_multitimeframe(bars_by_tf: dict[str, list[OHLCVBar]]) -> dict:
    reports = {tf: validate_bars(bars) for tf, bars in bars_by_tf.items()}
    issues = {tf: report["issues"] for tf, report in reports.items() if report["issues"]}
    return {"valid": not issues, "timeframes": reports, "issues": issues}
