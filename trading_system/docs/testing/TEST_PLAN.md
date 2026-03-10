# Test Plan

## Test layers present
- **Unit**: `tests/unit`, `tests/clmm`, `tests/lp`, `tests/hedging`, `tests/route_sim`.
- **Integration/API**: `tests/integration` (FastAPI TestClient-based).
- **Replay/Simulation**: `tests/sim`, `tests/replay`.
- **Performance smoke**: `tests/performance`.
- **Static quality**: Ruff + mypy.

## Canonical local commands
| Category | Command | Dependencies | Runtime (observed) | Pass criteria | Run in this pass |
|---|---|---|---|---|---|
| Full pytest suite | `pytest -q` | Python deps installed | ~2-4s | All tests pass | Yes |
| Lint | `ruff check .` | ruff | <1s | No violations | Yes |
| Type-check | `mypy .` | mypy | ~20-25s | No type errors | Yes |

## CI-suitable split (recommended)
1. `ruff check .`
2. `mypy .`
3. `pytest -q`

## Known problematic/flaky suites
- None observed in this pass.
- `tests/performance/test_maker_benchmark.py` is a smoke threshold check, not a true long-run benchmark.

## Critical no-regression areas
- Risk mode gating and trust-score behavior.
- Settings/env validation for live/canary safety paths.
- Onchain route analysis and approval packet generation.
- Replay/backtest runners and fixture parsing.
