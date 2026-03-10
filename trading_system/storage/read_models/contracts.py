from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ReadModelEnvelope(BaseModel):
    stream: str
    sequence: int
    as_of: datetime
    payload: dict


class DashboardReadModel(BaseModel):
    total_nav: float
    daily_pnl: float
    risk_mode: str
    exchange_trust_state: str


class PortfolioReadModel(BaseModel):
    portfolio_id: str
    nav: float
    available_capital: float
    liquidity_score: float


class LiquidityMapReadModel(BaseModel):
    nodes: list[dict]
    edges: list[dict]


class OpenOrdersReadModel(BaseModel):
    total_open: int
    by_strategy: dict[str, int]


class ApprovalQueueReadModel(BaseModel):
    pending_count: int
    urgent_count: int
