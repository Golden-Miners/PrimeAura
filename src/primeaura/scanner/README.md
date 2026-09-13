# Scanner integration

`MT5RecentProvider` adapts the read-only MT5 historical provider to the scanner's `recent()` interface. It retrieves recent bars only; it has no order, position, account, or broker-trading methods.

The full signal-generation integration remains gated until the MTF analysis APIs are verified against the repository's existing models. This avoids wiring incompatible assumptions into the live scanner.

**Alhamdulillah.**
