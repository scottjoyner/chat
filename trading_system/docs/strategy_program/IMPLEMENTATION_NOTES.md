# IMPLEMENTATION_NOTES

- Unified the 100-strategy contract with explicit `mapped_implementation` links to real strategy classes where present.
- Kept non-destructive adapter behavior for research-only items while enforcing honest readiness metadata.
- Added capital orchestration logic with tier caps, drawdown/quality scaling, and reserve-aware deployable budgeting.
