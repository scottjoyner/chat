# Trading System (Coinbase Advanced Trade)

Production-oriented modular scaffold for a Coinbase-focused algorithmic trading and research platform with explicit risk and approvals.

## Highlights
- Event-driven modular architecture with API, worker, backtester, replay engine, and paper exchange apps
- Expanded risk model with explicit high-risk modes and mode-specific gating
- Exchange reconciliation hardening with trust score (`HEALTHY/DEGRADED/UNTRUSTED`)
- Queue-position-aware execution model interface for replay/backtests
- Compute backend router (NumPy first, optional CuPy/PyTorch fallback)
- Strategy plugin interface and **50+ registered strategies/modules/overlays**
- Experiment tracker with reproducible run manifests
- Voice-agent approval payload support and operational notification categories

## Quickstart
```bash
cd trading_system
cp .env.example .env
pip install -e .[dev]
pytest -q
uvicorn apps.api.main:app --reload
```

## Operator API
See `/docs` and OpenAPI served by FastAPI at `/docs`.

## Safety Defaults
- Live trading disabled by default
- Approval required mode available
- Locked reserve is non-tradable
- `RESEARCH_ONLY` mode cannot submit live orders
- `UNTRUSTED` exchange trust score blocks risk-increasing orders
