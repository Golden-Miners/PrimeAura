from dataclasses import dataclass

@dataclass(frozen=True)
class ScanConfig:
    instruments: tuple[str,...] = ("XAUUSD","XAGUSD")
    timeframes: tuple[str,...] = ("H1","M15","M5")
    lookback_bars: int = 500
    poll_seconds: int = 15
