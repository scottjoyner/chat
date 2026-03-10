from fastapi import FastAPI, HTTPException

from core.config.settings import Settings
from core.models.domain import ExchangeTrustScore, OrderIntent, RiskMode
from exchange.coinbase.reconciliation.service import ExchangeStateReconciler
from risk.engine import RiskEngine, RiskPolicy
from strategies.registry.registry import load_strategies

app = FastAPI(title="Trading System Control API")
settings = Settings.from_env()
risk_engine = RiskEngine(RiskPolicy())
reconciler = ExchangeStateReconciler()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/mode")
def mode() -> dict:
    return {"mode": settings.trading_mode}


@app.get("/strategies/catalog")
def strategy_catalog() -> dict:
    strategies = load_strategies()
    return {"count": len(strategies), "strategies": [s.metadata() for s in strategies]}


@app.post("/risk/mode/{mode}/enable")
def enable_risk_mode(mode: RiskMode) -> dict:
    risk_engine.enable_mode(mode)
    return {"enabled_modes": sorted(m.value for m in risk_engine.enabled_modes)}


@app.get("/reconciliation/trust-score")
def reconciliation_trust_score() -> dict:
    trust = reconciler.reconcile_open_orders(reconciler.snapshot.open_orders_remote)
    risk_engine.set_exchange_trust(trust)
    return {"trust_score": trust.value, "snapshot": reconciler.snapshot.__dict__}


@app.post("/risk/evaluate")
def evaluate(intent: OrderIntent, mark_price: float = 0.0) -> dict:
    allowed, reason = risk_engine.evaluate(intent, mark_price=mark_price)
    if not allowed:
        raise HTTPException(status_code=400, detail=reason)
    return {"allowed": allowed, "reason": reason, "exchange_trust": risk_engine.exchange_trust_score.value}


@app.post("/ops/unsafe/untrusted")
def set_untrusted() -> dict:
    risk_engine.set_exchange_trust(ExchangeTrustScore.UNTRUSTED)
    return {"ok": True}
