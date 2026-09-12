# PrimeAura Canonical Market Data Contract

The signal/backtest engine consumes OHLCV bars through `MarketDataProvider`.

## Canonical instruments
- XAUUSD
- XAGUSD
- Additional symbols may be configured without changing the signal contract.

## Required fields
`timestamp, open, high, low, close`

`volume` is optional and defaults to zero.

## Integrity rules
- Timestamps must be timezone-aware UTC.
- Bars are strictly chronological.
- Duplicate timestamps are rejected.
- Prices are parsed as `Decimal`, not binary floating point.
- Provider implementations must return only bars within the requested half-open interval `[start, end)`.

## Provider policy
The strategy engine must not depend directly on a vendor SDK. Providers implement the common interface, allowing historical files, a free API, or another approved source to be swapped without rewriting analysis.

No provider is treated as ground truth. Dataset provenance and contract metadata must be recorded before a dataset is used for research or validation.

**Alhamdulillah — canonical data contract documented.**
