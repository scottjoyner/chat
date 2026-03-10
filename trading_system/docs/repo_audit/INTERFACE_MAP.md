# Interface Map

## Backend API contracts (`apps/api/main.py`)
- `GET /health` -> `{status}` liveness response.
- `GET /mode` -> `{mode}` from `Settings.trading_mode`.
- `GET /strategies/catalog` -> strategy metadata list.
- `POST /risk/mode/{mode}/enable` -> enabled mode set.
- `GET /reconciliation/trust-score` -> trust score + snapshot dictionary.
- `POST /risk/evaluate` -> allow/deny decision for `OrderIntent`.
- Onchain routes:
  - `/onchain/contracts/register`
  - `/onchain/tokens/register`
  - `/onchain/opportunities/rank`
  - `/onchain/path/analyze`
  - `/onchain/approvals/build`
  - `/onchain/hedge/coinbase`
  - `/onchain/profit/sweep`

## Operator API contracts (`apps/api/ops_layer.py`)
- Typed Pydantic read models for:
  - dashboard snapshot/delta
  - portfolio details
  - treasury transfer preview + execution request
  - order preview + submit
  - feed health and strategy status
- Boundary is currently **in-memory store**, no DB-backed persistence.

## Websocket/realtime contracts
- No websocket endpoints are exposed in FastAPI entrypoints during this pass; realtime semantics are represented as pollable typed responses in ops layer.

## Internal service boundaries
- Risk policy decisions encapsulated by `risk.engine.RiskEngine`.
- Exchange trust set via reconciliation service and consumed by risk engine.
- Onchain path analysis boundary: registry/safety engines + simulator -> plan object.
- Strategy discovery boundary: `strategies.registry.registry.load_strategies()` used by API and backtester.

## Known contract mismatches / drift risks
- `/mode` currently returns enum object value via JSON serialization; consumers should treat as string, but this is not explicitly versioned.
- Ops read models are richer than persisted state (none), so refresh/restart loses operator context.
- `docker-compose.yml` declares API image build but repository lacks a Dockerfile, making compose contract incomplete.
- Alembic migration path is incomplete (`alembic/env.py` absent), so DB migration contract is partially wired.
