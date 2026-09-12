# Phase 6 — Backtesting Foundation

Implemented:
- Immutable trade-result model.
- Backtest metrics: trade count, wins/losses, win rate, net PnL, drawdown, profit factor.
- Explicit out-of-sample validation gate with minimum trade-count and profitability thresholds.
- Tests for metric calculation and rejection of undersized samples.

This is a foundation, not a complete backtester. Historical execution semantics, spread/slippage, fees, intrabar ambiguity, train/test partitioning, walk-forward analysis, Monte Carlo robustness, and leakage controls remain mandatory before strategy promotion.

**Alhamdulillah — Phase 6 foundation implemented.**
