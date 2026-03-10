# Test Matrix

| Subsystem | Test type | Files | Status before | Status after | Notes |
|---|---|---|---|---|---|
| Config safety | Unit | `tests/unit/test_settings.py` | Not covered | Passing | New regression coverage added this pass. |
| API health/ops | Integration | `tests/integration/test_api_health.py`, `tests/integration/test_ops_api.py` | Passing | Passing | No regressions observed. |
| Risk engine | Unit | `tests/unit/test_risk_engine.py` | Passing | Passing | Existing coverage retained. |
| Onchain path/policy | Unit | `tests/unit/test_onchain_*` | Passing | Passing | No interface breaks from config hardening. |
| CLMM math | Unit | `tests/clmm/test_clmm_math.py` | Ruff lint fail | Passing | Variable rename resolved lint error. |
| Replay/backtest | Sim/replay | `tests/sim/*`, `tests/replay/*` | Passing | Passing | Smoke stability preserved. |
| Repo-wide static analysis | Lint/typecheck | entire repo | Ruff fail, mypy fail | Passing | mypy config alignment + typing fixes. |
