# Trading System (Coinbase Advanced Trade)

Production-oriented modular scaffold for a Coinbase-focused algorithmic trading platform with explicit risk and approvals.

## Highlights
- Event-driven modular architecture with API, worker, backtester, and paper exchange apps
- Capital buckets with locked reserve enforcement
- Centralized risk engine with fail-closed behavior
- Strategy plugin interface and 14 implemented strategy plugins
- Voice-agent approval payload adapter and notification categories
- Backtesting and paper trading entry points
- FastAPI control plane

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
- Risk checks required before execution
