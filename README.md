# PrimeAura

PrimeAura is a research-driven, multi-agent market intelligence system designed to generate BUY / SELL / NO SIGNAL outputs with entry, stop loss, targets, strategy attribution, and auditable reasoning.

## Scope

- Primary focus: Gold (XAUUSD) and Silver (XAGUSD)
- User-selectable instruments and watchlists
- Signal generation only; no broker connectivity and no trade execution
- Deterministic market analysis separated from LLM reasoning
- Python core with LangGraph used only for agent workflows where orchestration is useful
- Local LLM support through Ollama, with pluggable cloud API providers
- Research, backtesting, validation, learning, and controlled strategy improvement

## Development status

Phase 0 — Project foundation: IN PROGRESS

This repository is intentionally being built incrementally. Production trading claims are not made by the software merely because a strategy backtests well.

## Principles

1. No order execution.
2. No LLM-generated market facts without deterministic verification.
3. NO SIGNAL is a valid first-class result.
4. Strategy promotion requires quantitative validation.
5. Research/self-improvement is controlled and versioned.
6. Anti-overfitting and leakage prevention are mandatory.
7. Every signal must have an audit trail.

## Hardware targets

- Development: low-resource Windows laptop
- Daily-use/production target: Windows desktop PC

## License

License to be decided before public release.
