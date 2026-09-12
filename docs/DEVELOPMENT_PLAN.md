# PrimeAura Development Plan

## Phase sequence

0. Foundation and specification lock
1. Development environment and resource management
2. Market-data engine
3. Deterministic market-analysis engine
4. Market-regime engine
5. Strategy framework
6. Backtesting and anti-overfitting validation
7. Basic signal engine
8. Signal lifecycle, deduplication, attribution, and audit trail
9. LangGraph research and multi-agent workflows
10. Strategy library and quantitative ranking
11. Outcome tracking and controlled learning
12. Self-improvement and strategy versioning
13. Market scanner
14. UI/UX and observability
15. Full adversarial/regression audit
16. PC migration and production validation

## Development loop

For each phase:

1. Define the contract.
2. Implement the smallest testable unit.
3. Add unit tests.
4. Add integration tests.
5. Add adversarial/edge-case tests where applicable.
6. Run the regression suite.
7. Document decisions and limitations.
8. Freeze the phase only after acceptance criteria pass.

## First useful milestone

The first basic signal milestone is deliberately earlier than the full agent system:

Market data → deterministic analysis → one formally specified strategy → basic backtest → signal output.

The initial signal system must clearly distinguish development/test signals from validated strategy performance.

## Research/self-improvement

No unrestricted self-modification. Proposed changes move through:

DISCOVERED → FORMALIZED → BACKTESTED → ROBUSTNESS TESTED → WALK-FORWARD TESTED → CANDIDATE → HUMAN REVIEW → ACTIVE/RETIRED

## Hardware strategy

Develop and test on the low-resource laptop first. The PC is the later daily-use target. The codebase must remain reproducible across both machines.
