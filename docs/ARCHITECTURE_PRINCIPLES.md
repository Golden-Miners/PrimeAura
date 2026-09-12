# PrimeAura Architecture Principles

## 1. Separation of concerns

PrimeAura separates deterministic computation from probabilistic language-model reasoning.

Market facts such as OHLC-derived indicators, structure events, risk calculations, and signal validation should be computed or verified by deterministic code whenever practical.

LLMs interpret evidence, conduct research, challenge hypotheses, and synthesize reasoning. They are not the authoritative source of market facts.

## 2. Layered architecture

Planned layers:

1. Market data
2. Data normalization and quality checks
3. Deterministic market analysis
4. Market regime detection
5. Strategy framework
6. Backtesting and validation
7. Candidate signal generation
8. Agent reasoning/orchestration
9. Signal validation, clustering, and lifecycle
10. Outcome tracking
11. Research and controlled strategy improvement
12. UI/API
13. Observability and resource management

## 3. LangGraph boundary

LangGraph is intended for workflows involving multiple agents, stateful reasoning, branching, critique, research, or iterative agent processes.

It should not be used merely to wrap ordinary Python functions.

## 4. LLM gateway

Agents depend on an abstraction rather than a specific model runtime.

Planned adapters:

- Ollama
- OpenAI-compatible cloud providers
- Additional providers as needed

The application must remain functional when an optional LLM provider is unavailable.

## 5. Signal-only safety boundary

PrimeAura does not require broker APIs and must not place trades.

The signal engine ends at an auditable recommendation:

- BUY
- SELL
- NO SIGNAL

with entry/exit information and supporting evidence.

## 6. Strategy governance

Research agents may propose strategies and revisions. Promotion to active use requires predefined quantitative validation and, initially, human approval.

## 7. Reproducibility

Historical datasets, configuration, strategy versions, and validation results must be traceable. Test fixtures should provide a stable regression baseline.

## 8. Resource awareness

The initial development environment has limited RAM/CPU. Expensive local inference should be optional and controllable. Workloads should be staged so deterministic screening occurs before expensive agent reasoning.
