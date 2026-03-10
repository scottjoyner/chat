# Asset Management + Liquidity Optimization Layer

## Overview

This pass adds an operator-focused Coinbase-centric portfolio operations layer with:

- FastAPI endpoint surface for dashboard, portfolios, treasury preview/execute, liquidity map/recommendations, order preview/submit/cancel, and oversight pages.
- Deterministic liquidity optimization scoring for capital mobility recommendations.
- Read-model contract definitions intended for websocket/event-driven UI hydration.
- Seeded institutional-like data for portfolios, sleeves, allocations, liquidity, approvals, alerts, and incidents.

## API Surface

All endpoints are mounted under `/ops`.

Core groups:

- Dashboard: `/ops/dashboard/snapshot`
- Portfolios: `/ops/portfolios`, `/ops/portfolios/{id}`
- Treasury workflow: `/ops/treasury/preview`, `/ops/treasury/execute`
- Liquidity: `/ops/liquidity/map`, `/ops/liquidity/recommendations`
- Orders and execution: `/ops/orders/preview`, `/ops/orders/submit`, `/ops/orders/open`, `/ops/orders/{id}/cancel`, `/ops/fills`
- Oversight: `/ops/risk/summary`, `/ops/approvals`, `/ops/alerts`, `/ops/incidents`, `/ops/audit`

## Treasury Safety Contract

Treasury actions follow preview-first semantics:

1. Submit transfer intent to preview endpoint.
2. Receive approval requirements and impact estimates.
3. Execute with preview id lineage.
4. Emit immutable audit event with source, destination, amount and timestamp.

## Liquidity Optimization Methodology

`LiquidityOptimizer` computes three operator-facing scores:

- `usefulness`: suitability of an asset for deployment.
- `productivity`: expected productive deployment quality after accounting for idle ratio and friction.
- `transfer_necessity`: urgency to move idle capital.

Inputs include idle/working balances, depth score, spread opportunity, friction, hedgeability, and available risk budget.

## UI Integration Guidance

The API is intentionally modeled for a dense but scannable operator UI with progressive disclosure.

- Start with `/ops/dashboard/snapshot` for top-level cards and badges.
- Drill into `/ops/portfolios/{id}` for sleeve and strategy breakdown.
- Use liquidity recommendations to pre-fill treasury move dialogs.
- Enforce preview-linkage before state-changing actions.

## Known Limitations

- Current implementation is in-memory; production should persist in read stores and event logs.
- Websocket stream and partial update buses are not yet implemented in this pass.
- Market microstructure metrics are synthetic seed values.
