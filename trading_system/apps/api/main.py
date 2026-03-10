from fastapi import FastAPI, HTTPException
from core.config.settings import Settings
from core.models.domain import OrderIntent
from risk.engine import RiskEngine, RiskPolicy

app = FastAPI(title="Trading System Control API")
settings = Settings.from_env()
risk_engine = RiskEngine(RiskPolicy())

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.get("/mode")
def mode() -> dict:
    return {"mode": settings.trading_mode}

@app.post("/risk/evaluate")
def evaluate(intent: OrderIntent, mark_price: float = 0.0) -> dict:
    allowed, reason = risk_engine.evaluate(intent, mark_price=mark_price)
    if not allowed:
        raise HTTPException(status_code=400, detail=reason)
    return {"allowed": allowed, "reason": reason}
