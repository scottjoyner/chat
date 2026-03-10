# Change Summary

## Files changed
- `core/config/settings.py` — **bugfix/hardening**
  - Added strict env boolean parsing.
  - Added queue model validation and normalization.
  - Added cross-field safety checks for live/canary modes.
- `tests/unit/test_settings.py` — **test**
  - Added six regression tests covering startup config safety and parsing.
- `tests/clmm/test_clmm_math.py` — **test cleanup**
  - Renamed ambiguous variable to satisfy lint quality gate.
- `onchain/strategies/amm_lp/out_of_range_recovery.py` — **typing fix**
  - Replaced weakly typed `options.get` key function with typed lambda.
- `pyproject.toml` — **tooling/config**
  - Added mypy configuration to support current package layout.
- `README.md` — **docs**
  - Replaced stale quickstart assumptions, documented actual run/test commands and known limitations.
- `docs/repo_audit/*`, `docs/testing/*` — **audit + evidence docs**
  - Added architecture map, subsystem inventory, interface map, config surface, gap report, testing plan/results/matrix, CI alignment, and risk tracking.

## Rationale
This pass prioritized startup/runtime safety, static-analysis reliability, and evidence-based repository documentation while preserving existing architecture and tests.
