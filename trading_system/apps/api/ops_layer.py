from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


class CapitalStatus(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    LOCKED = "locked"
    HEDGED = "hedged"
    PENDING = "pending"


class CapitalBucketView(BaseModel):
    name: str
    amount: float
    status: CapitalStatus


class PortfolioSummary(BaseModel):
    portfolio_id: str
    name: str
    objective: str
    nav: float
    available_capital: float
    locked_capital: float
    realized_pnl: float
    unrealized_pnl: float
    liquidity_score: float = Field(ge=0, le=1)
    capital_efficiency: float = Field(ge=0, le=1)


class DashboardSnapshot(BaseModel):
    generated_at: datetime
    total_nav: float
    daily_pnl: float
    realized_pnl: float
    unrealized_pnl: float
    risk_mode: str
    exchange_trust_state: str
    open_orders: int
    fills_last_15m: int
    approval_queue: int
    latency_health: float
    reconciliation_health: float
    capital_buckets: list[CapitalBucketView]
    portfolios: list[PortfolioSummary]


class PortfolioDetail(BaseModel):
    summary: PortfolioSummary
    sleeves: dict[str, float]
    strategy_allocations: dict[str, float]
    transfers_24h: list[dict]
    risk_budget_used: float
    what_changed: dict[str, float]


class TreasuryTransferPreviewRequest(BaseModel):
    source_portfolio: str
    destination_portfolio: str
    asset: str
    amount: float = Field(gt=0)
    rationale: str


class TreasuryTransferPreview(BaseModel):
    preview_id: str
    source_portfolio: str
    destination_portfolio: str
    asset: str
    amount: float
    approvals_required: list[str]
    resulting_liquidity_change: dict[str, float]
    resulting_risk_budget_change: dict[str, float]
    rollback_guidance: str


class TreasuryTransferExecuteRequest(BaseModel):
    preview_id: str


class LiquidityRecommendation(BaseModel):
    recommendation_id: str
    action: str
    expected_efficiency_delta: float
    expected_liquidity_score_delta: float
    confidence: float


class LiquidityMapNode(BaseModel):
    node_id: str
    node_type: Literal["portfolio", "sleeve", "asset"]
    utilization: float
    productive: bool


class LiquidityMapEdge(BaseModel):
    source: str
    target: str
    suggested_move: float


class LiquidityMapSnapshot(BaseModel):
    as_of: datetime
    nodes: list[LiquidityMapNode]
    edges: list[LiquidityMapEdge]


class OrderPreviewRequest(BaseModel):
    portfolio_id: str
    sleeve_id: str
    strategy_id: str
    product_id: str
    side: Literal["buy", "sell"]
    order_type: Literal["market", "limit"]
    size: float = Field(gt=0)
    limit_price: float | None = None


class OrderPreviewResponse(BaseModel):
    preview_id: str
    estimated_commission: float
    estimated_slippage: float
    expected_fee_impact: float
    resulting_exposure: float
    resulting_risk_usage: float
    approval_required: bool
    confidence: float


class SubmitOrderRequest(BaseModel):
    preview_id: str


class OrderRecord(BaseModel):
    order_id: str
    preview_id: str
    strategy_id: str
    portfolio_id: str
    sleeve_id: str
    product_id: str
    side: str
    size: float
    remaining_size: float
    order_type: str
    status: str
    maker_taker_expectation: str
    queue_age_s: int
    created_at: datetime


class FillRecord(BaseModel):
    fill_id: str
    order_id: str
    product_id: str
    size: float
    price: float
    slippage_bps: float
    fee: float
    at: datetime


class InMemoryOpsStore:
    def __init__(self) -> None:
        self.portfolios: dict[str, PortfolioDetail] = {}
        self.preview_cache: dict[str, TreasuryTransferPreview | OrderPreviewResponse] = {}
        self.orders: dict[str, OrderRecord] = {}
        self.fills: list[FillRecord] = []
        self.audit_events: list[dict] = []
        self._seed()

    def _seed(self) -> None:
        p1 = PortfolioSummary(
            portfolio_id="cb-core-mm",
            name="Coinbase Core MM",
            objective="market_making",
            nav=2_500_000,
            available_capital=1_350_000,
            locked_capital=610_000,
            realized_pnl=42_300,
            unrealized_pnl=8_100,
            liquidity_score=0.82,
            capital_efficiency=0.75,
        )
        p2 = PortfolioSummary(
            portfolio_id="cb-hedge",
            name="Coinbase Hedge",
            objective="hedge",
            nav=1_100_000,
            available_capital=790_000,
            locked_capital=120_000,
            realized_pnl=13_200,
            unrealized_pnl=-2200,
            liquidity_score=0.71,
            capital_efficiency=0.66,
        )
        self.portfolios[p1.portfolio_id] = PortfolioDetail(
            summary=p1,
            sleeves={"maker": 0.55, "taker": 0.1, "inventory": 0.35},
            strategy_allocations={"adaptive_spread_mm": 0.44, "stair_step_mm": 0.31, "basis_carry": 0.25},
            transfers_24h=[{"from": "treasury", "to": "cb-core-mm", "asset": "USDC", "amount": 150_000}],
            risk_budget_used=0.61,
            what_changed={"5m": 0.003, "1h": 0.011, "1d": 0.024, "session": 0.018},
        )
        self.portfolios[p2.portfolio_id] = PortfolioDetail(
            summary=p2,
            sleeves={"delta_hedge": 0.65, "tail_protection": 0.35},
            strategy_allocations={"hybrid_hedge": 0.72, "vol_breakout": 0.28},
            transfers_24h=[{"from": "cb-core-mm", "to": "cb-hedge", "asset": "USDC", "amount": 85_000}],
            risk_budget_used=0.42,
            what_changed={"5m": -0.001, "1h": 0.002, "1d": -0.006, "session": -0.002},
        )

    def dashboard(self) -> DashboardSnapshot:
        portfolio_summaries = [d.summary for d in self.portfolios.values()]
        return DashboardSnapshot(
            generated_at=datetime.now(timezone.utc),
            total_nav=sum(p.nav for p in portfolio_summaries),
            daily_pnl=sum(p.realized_pnl + p.unrealized_pnl for p in portfolio_summaries),
            realized_pnl=sum(p.realized_pnl for p in portfolio_summaries),
            unrealized_pnl=sum(p.unrealized_pnl for p in portfolio_summaries),
            risk_mode="MARKET_MAKING_PRO",
            exchange_trust_state="HEALTHY",
            open_orders=len(self.orders),
            fills_last_15m=len(self.fills),
            approval_queue=2,
            latency_health=0.96,
            reconciliation_health=0.98,
            capital_buckets=[
                CapitalBucketView(name="locked_reserve", amount=900_000, status=CapitalStatus.LOCKED),
                CapitalBucketView(name="active_trading", amount=1_450_000, status=CapitalStatus.WORKING),
                CapitalBucketView(name="hedging", amount=500_000, status=CapitalStatus.HEDGED),
                CapitalBucketView(name="cash_buffer", amount=750_000, status=CapitalStatus.IDLE),
                CapitalBucketView(name="pending_transfer", amount=125_000, status=CapitalStatus.PENDING),
            ],
            portfolios=portfolio_summaries,
        )


store = InMemoryOpsStore()
router = APIRouter(prefix="/ops", tags=["ops"])


@router.get("/dashboard/snapshot", response_model=DashboardSnapshot)
def dashboard_snapshot() -> DashboardSnapshot:
    return store.dashboard()


@router.get("/portfolios", response_model=list[PortfolioSummary])
def list_portfolios() -> list[PortfolioSummary]:
    return [d.summary for d in store.portfolios.values()]


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioDetail)
def get_portfolio_detail(portfolio_id: str) -> PortfolioDetail:
    detail = store.portfolios.get(portfolio_id)
    if not detail:
        raise HTTPException(status_code=404, detail="portfolio not found")
    return detail


@router.post("/treasury/preview", response_model=TreasuryTransferPreview)
def treasury_preview(req: TreasuryTransferPreviewRequest) -> TreasuryTransferPreview:
    if req.source_portfolio == req.destination_portfolio:
        raise HTTPException(status_code=400, detail="source and destination must differ")

    preview = TreasuryTransferPreview(
        preview_id=f"tr-prev-{uuid4().hex[:10]}",
        source_portfolio=req.source_portfolio,
        destination_portfolio=req.destination_portfolio,
        asset=req.asset,
        amount=req.amount,
        approvals_required=["treasury_officer", "risk_desk"],
        resulting_liquidity_change={req.source_portfolio: -req.amount, req.destination_portfolio: req.amount},
        resulting_risk_budget_change={req.source_portfolio: -0.04, req.destination_portfolio: 0.03},
        rollback_guidance="Submit reverse transfer using original preview id lineage and freeze non-essential orders.",
    )
    store.preview_cache[preview.preview_id] = preview
    return preview


@router.post("/treasury/execute")
def treasury_execute(req: TreasuryTransferExecuteRequest) -> dict:
    preview = store.preview_cache.get(req.preview_id)
    if not isinstance(preview, TreasuryTransferPreview):
        raise HTTPException(status_code=404, detail="transfer preview not found")

    source = store.portfolios.get(preview.source_portfolio)
    destination = store.portfolios.get(preview.destination_portfolio)
    if not source or not destination:
        raise HTTPException(status_code=404, detail="portfolio not found")

    source.summary.available_capital -= preview.amount
    destination.summary.available_capital += preview.amount
    store.audit_events.append(
        {
            "type": "treasury_transfer_executed",
            "preview_id": preview.preview_id,
            "source": preview.source_portfolio,
            "destination": preview.destination_portfolio,
            "amount": preview.amount,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    return {"status": "executed", "preview_id": preview.preview_id}


@router.get("/liquidity/map", response_model=LiquidityMapSnapshot)
def liquidity_map() -> LiquidityMapSnapshot:
    return LiquidityMapSnapshot(
        as_of=datetime.now(timezone.utc),
        nodes=[
            LiquidityMapNode(node_id="cb-core-mm", node_type="portfolio", utilization=0.78, productive=True),
            LiquidityMapNode(node_id="cb-hedge", node_type="portfolio", utilization=0.54, productive=True),
            LiquidityMapNode(node_id="maker", node_type="sleeve", utilization=0.83, productive=True),
            LiquidityMapNode(node_id="USDC", node_type="asset", utilization=0.49, productive=False),
        ],
        edges=[
            LiquidityMapEdge(source="cb-core-mm", target="cb-hedge", suggested_move=120_000),
            LiquidityMapEdge(source="USDC", target="maker", suggested_move=75_000),
        ],
    )


@router.get("/liquidity/recommendations", response_model=list[LiquidityRecommendation])
def liquidity_recommendations() -> list[LiquidityRecommendation]:
    return [
        LiquidityRecommendation(
            recommendation_id="liq-001",
            action="Move 120k USDC from cb-core-mm to cb-hedge delta sleeve",
            expected_efficiency_delta=0.07,
            expected_liquidity_score_delta=0.05,
            confidence=0.82,
        ),
        LiquidityRecommendation(
            recommendation_id="liq-002",
            action="Cancel stale BTC-USD maker inventory and recycle 80k capital",
            expected_efficiency_delta=0.04,
            expected_liquidity_score_delta=0.03,
            confidence=0.76,
        ),
    ]


@router.post("/orders/preview", response_model=OrderPreviewResponse)
def preview_order(req: OrderPreviewRequest) -> OrderPreviewResponse:
    if req.order_type == "limit" and req.limit_price is None:
        raise HTTPException(status_code=400, detail="limit price required for limit order")
    notional = req.size * (req.limit_price or 100)
    preview = OrderPreviewResponse(
        preview_id=f"ord-prev-{uuid4().hex[:10]}",
        estimated_commission=notional * 0.0008,
        estimated_slippage=notional * 0.0006,
        expected_fee_impact=notional * 0.0014,
        resulting_exposure=notional * (1 if req.side == "buy" else -1),
        resulting_risk_usage=0.57,
        approval_required=notional > 250_000,
        confidence=0.88,
    )
    store.preview_cache[preview.preview_id] = preview
    return preview


@router.post("/orders/submit", response_model=OrderRecord)
def submit_order(req: SubmitOrderRequest) -> OrderRecord:
    preview = store.preview_cache.get(req.preview_id)
    if not isinstance(preview, OrderPreviewResponse):
        raise HTTPException(status_code=404, detail="order preview not found")

    order = OrderRecord(
        order_id=f"ord-{uuid4().hex[:10]}",
        preview_id=preview.preview_id,
        strategy_id="adaptive_spread_mm",
        portfolio_id="cb-core-mm",
        sleeve_id="maker",
        product_id="BTC-USD",
        side="buy",
        size=0.5,
        remaining_size=0.5,
        order_type="limit",
        status="open",
        maker_taker_expectation="maker",
        queue_age_s=0,
        created_at=datetime.now(timezone.utc),
    )
    store.orders[order.order_id] = order
    store.audit_events.append({"type": "order_submitted", "order_id": order.order_id, "preview_id": preview.preview_id})
    return order


@router.get("/orders/open", response_model=list[OrderRecord])
def open_orders() -> list[OrderRecord]:
    return list(store.orders.values())


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str) -> dict:
    order = store.orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    order.status = "canceled"
    order.remaining_size = 0
    store.audit_events.append({"type": "order_canceled", "order_id": order_id})
    return {"status": "canceled", "order_id": order_id}


@router.get("/fills", response_model=list[FillRecord])
def fills() -> list[FillRecord]:
    return store.fills


@router.get("/risk/summary")
def risk_summary() -> dict:
    return {
        "mode": "MARKET_MAKING_PRO",
        "drawdown": 0.021,
        "limit_usage": {"portfolio": 0.61, "strategy": 0.55},
        "warnings": ["minor liquidity-quality warning on ETH-USD"],
        "exchange_trust_state": "HEALTHY",
    }


@router.get("/approvals")
def approvals() -> list[dict]:
    return [
        {
            "approval_id": "appr-100",
            "type": "treasury_move",
            "summary": "Move 120k USDC to hedge sleeve",
            "capital_affected": 120_000,
            "liquidity_impact": "positive",
            "risk_impact": "moderate",
            "expiration": datetime.now(timezone.utc).isoformat(),
        }
    ]


@router.get("/alerts")
def alerts() -> list[dict]:
    return [{"alert_id": "al-1", "severity": "medium", "summary": "Maker queue age drift on BTC-USD", "acknowledged": False}]


@router.get("/incidents")
def incidents() -> list[dict]:
    return [{"incident_id": "inc-1", "severity": "low", "summary": "Temporary reconciliation lag", "status": "monitoring"}]


@router.get("/audit")
def audit_events() -> list[dict]:
    return store.audit_events
