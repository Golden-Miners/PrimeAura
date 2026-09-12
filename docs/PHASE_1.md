# Phase 1 — Development Environment & Resource Management

## Objective

Make PrimeAura practical to develop on the low-resource Lenovo laptop while preserving a path to the desktop PC.

## Initial policy

- Keep local LLM inference optional.
- Prefer cloud LLMs when configured on the laptop.
- Limit concurrency to one LLM/agent workflow on the laptop.
- Screen deterministically before invoking expensive LLM workflows.
- Keep resource profiles configuration-driven.
- Never introduce broker/order execution dependencies.

## Acceptance criteria

- Python project metadata exists.
- A laptop resource profile exists.
- A desktop profile exists.
- Environment diagnostics can run without third-party dependencies.
- Resource profile has automated tests.
- Secrets are excluded from Git.

## Result

Phase 1 foundation is implemented. Full environment verification must still be performed on the user's Lenovo because this execution environment is not the user's physical laptop.

**Alhamdulillah — Phase 1 foundation implemented.**
