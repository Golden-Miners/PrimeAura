# Phase 5 — Strategy Framework

Implemented:
- Immutable/versioned strategy definitions.
- Strategy registry keyed by strategy ID + version.
- Strategy signal contract for direction and optional entry/exit levels.
- Controlled strategy lifecycle: DISCOVERED → FORMALIZED → BACKTESTED → ROBUSTNESS_TESTED → WALK_FORWARD_TESTED → CANDIDATE → ACTIVE/RETIRED.
- Unit tests for registration, duplicate versions, and governance.

No strategy is being declared profitable. Promotion is deliberately impossible without completing the defined validation stages.

**Alhamdulillah — Phase 5 foundation implemented.**
