from __future__ import annotations

from dataclasses import asdict, dataclass

from strategies.base.interfaces import Strategy, StrategySignal


@dataclass(frozen=True)
class StrategySpec:
    strategy_id: str
    canonical_name: str
    family: str
    purpose: str
    regime_suitability: str
    supported_products: list[str]
    risk_tier: str
    required_data: list[str]
    required_indicators: list[str]
    warmup_bars: int
    required_latency_budget_ms: float
    sizing_model: str
    risk_ceilings: str
    min_size: float
    max_size: float
    max_capital_fraction: float
    max_exposure_by_asset: float
    max_exposure_by_correlated_group: float
    max_turnover: float
    expected_holding_horizon: str
    execution_style: str
    take_profit_model: str
    trailing_exit: bool
    compound_profits: bool
    min_net_edge_bps: float
    approvals_required: bool
    failure_modes: list[str]
    disable_criteria: list[str]
    cooldown_logic: str
    explainability_output: str
    backtest_caveats: str
    live_deployment_prerequisites: list[str]
    implementation_status: str
    unit_tested: bool
    backtest_ready: bool
    replay_ready: bool
    paper_ready: bool
    live_safe: bool


class GenericSpecStrategy(Strategy):
    def __init__(self, spec: StrategySpec) -> None:
        self.spec = spec
        self.strategy_id = spec.strategy_id

    def metadata(self) -> dict:
        return asdict(self.spec)

    def generate_signal(self, market_state: dict) -> StrategySignal | None:
        product = market_state.get("product_id", self.spec.supported_products[0])
        score = float(market_state.get("score", 0.0))
        threshold = float(market_state.get("threshold", 0.1))
        if score <= threshold:
            return None
        return StrategySignal(
            strategy_id=self.strategy_id,
            product_id=product,
            score=score,
            reason=f"{self.spec.canonical_name}: {self.spec.purpose}",
        )

    def explain_trade(self, signal: StrategySignal) -> str:
        return (
            f"{self.spec.canonical_name} score={signal.score:.4f} tier={self.spec.risk_tier} "
            f"tp={self.spec.take_profit_model} edge_bps={self.spec.min_net_edge_bps}"
        )


CATALOG_100: list[str] = [
    "Multi-timeframe breakout",
    "Donchian channel breakout",
    "ATR channel breakout",
    "Moving-average crossover",
    "EMA ribbon trend-following",
    "Supertrend continuation",
    "ADX trend-strength breakout",
    "Trend pullback continuation",
    "Opening-range breakout",
    "Volatility expansion breakout",
    "Turtle-style breakout",
    "Keltner channel breakout",
    "Regression-slope momentum",
    "Time-series momentum",
    "Cross-sectional momentum rotation",
    "Z-score mean reversion",
    "Bollinger band reversion",
    "RSI exhaustion reversal",
    "Short-term reversal after large candle",
    "Gap-fill mean reversion",
    "VWAP reversion intraday",
    "Reversion to anchored VWAP",
    "Range-bound fade",
    "Channel-touch reversal",
    "Order-block rejection reversion",
    "Market overextension snapback",
    "Liquidity vacuum snapback",
    "Exhaustion-volume reversal",
    "Session close reversion",
    "Micro pullback reversion",
    "Pairs trading with fixed hedge ratio",
    "Pairs trading with Kalman hedge ratio",
    "Cointegration basket arbitrage",
    "Residual spread z-score arb",
    "Cross-exchange spot arbitrage abstraction",
    "CEX-DEX arbitrage abstraction",
    "Triangular arbitrage",
    "Stablecoin imbalance arbitrage",
    "Basis arbitrage",
    "Carry trade allocator",
    "Funding-rate differential strategy",
    "Dispersion trading across correlated assets",
    "Correlation breakdown arb",
    "Lead-lag relative value strategy",
    "ETF/index proxy relative value abstraction",
    "Stair-step market maker",
    "Adaptive spread market maker",
    "Inventory-skewed market maker",
    "Avellaneda-Stoikov-inspired market maker",
    "Queue-reactive market maker",
    "Volatility-scaled market maker",
    "Microprice-driven quote engine",
    "Toxic-flow-aware market maker",
    "Spread floor/ceiling market maker",
    "Post-only maker with fade logic",
    "Maker ladder with quote clustering controls",
    "Dynamic quote refresh policy strategy",
    "Inventory liquidation overlay",
    "Maker pause under stress overlay",
    "Maker-taker switcher",
    "Order book imbalance strategy",
    "Trade-flow imbalance strategy",
    "Queue pressure predictive strategy",
    "Sweep detection momentum",
    "Refill-speed resiliency strategy",
    "Quote fade/cancel pressure predictor",
    "Microburst momentum strategy",
    "Bid-ask bounce capture",
    "Short-horizon microprice drift strategy",
    "Spread collapse event strategy",
    "TWAP execution algo",
    "VWAP execution algo",
    "Adaptive participation algo",
    "Arrival-price shortfall minimizer",
    "Iceberg replenishment strategy",
    "Laddered entry/exit execution",
    "Dynamic pegged execution abstraction",
    "Liquidity-seeking execution strategy",
    "Impact-aware rebalancer",
    "Passive-first then aggressive execution overlay",
    "Volatility compression then expansion",
    "Realized-vol breakout",
    "Volatility mean reversion",
    "Regime-switching allocator",
    "Hidden-Markov market regime classifier",
    "Trend/chop classifier with strategy routing",
    "Panic-mode defensive allocator",
    "Tail-risk hedge trigger overlay",
    "Convexity allocator",
    "Volatility targeting portfolio overlay",
    "Risk parity allocator",
    "Minimum variance allocator",
    "Equal risk contribution allocator",
    "Momentum-weighted sleeve allocator",
    "Drawdown-aware capital decay allocator",
    "Strategy leaderboard allocator",
    "Meta-strategy selector",
    "Profit-sweep treasury allocator",
    "Dynamic reserve deployment allocator",
    "Crash-response opportunistic accumulator",
]


def _family(index: int) -> str:
    bounds = [15, 30, 45, 60, 70, 80, 90, 100]
    labels = [
        "trend_momentum",
        "mean_reversion",
        "relative_value",
        "market_making",
        "microstructure",
        "execution",
        "volatility_regime",
        "portfolio_treasury",
    ]
    for b, l in zip(bounds, labels, strict=True):
        if index <= b:
            return l
    return "research"


def _status(name: str) -> tuple[str, bool, bool, bool, bool, bool]:
    implemented = {
        "Z-score mean reversion",
        "Cross-sectional momentum rotation",
        "Stair-step market maker",
        "Adaptive spread market maker",
        "Order book imbalance strategy",
        "VWAP execution algo",
        "TWAP execution algo",
        "Pairs trading with fixed hedge ratio",
        "Realized-vol breakout",
        "Regime-switching allocator",
        "Liquidity vacuum snapback",
        "Basis arbitrage",
        "Crash-response opportunistic accumulator",
    }
    partial = {
        "Trend pullback continuation",
        "Opening-range breakout",
        "Cointegration basket arbitrage",
        "Maker-taker switcher",
        "Adaptive participation algo",
        "Meta-strategy selector",
    }
    if name in implemented:
        return ("implemented", True, True, True, True, True)
    if name in partial:
        return ("partial", False, True, True, True, False)
    return ("research_only", False, False, False, True, False)


def _risk_tier(family: str, status: str) -> str:
    if status == "research_only":
        return "TIER_5_RESEARCH_ONLY"
    if family in {"portfolio_treasury", "execution"}:
        return "TIER_1_LOW_RISK"
    if family in {"trend_momentum", "mean_reversion", "relative_value"}:
        return "TIER_2_MODERATE_RISK"
    if family == "market_making":
        return "TIER_3_HIGH_RISK"
    if family == "microstructure":
        return "TIER_4_EXPERT_HIGH_RISK"
    return "TIER_2_MODERATE_RISK"


def advanced_specs() -> list[StrategySpec]:
    specs: list[StrategySpec] = []
    for i, name in enumerate(CATALOG_100, start=1):
        family = _family(i)
        status, unit, backtest, replay, paper, live = _status(name)
        tier = _risk_tier(family, status)
        strategy_id = f"S{i:03d}_{name.lower().replace(' ', '_').replace('-', '_').replace('/', '_')}"
        specs.append(
            StrategySpec(
                strategy_id=strategy_id,
                canonical_name=name,
                family=family,
                purpose=f"{family} alpha or execution objective for {name.lower()}",
                regime_suitability="regime-aware with disable-on-stress controls",
                supported_products=["BTC-USD", "ETH-USD"],
                risk_tier=tier,
                required_data=["candles", "trades", "orderbook"],
                required_indicators=["atr", "rsi", "realized_vol"],
                warmup_bars=200,
                required_latency_budget_ms=100.0,
                sizing_model="volatility_targeting",
                risk_ceilings="per-strategy VaR + drawdown + stress limits",
                min_size=0.001,
                max_size=2.0,
                max_capital_fraction=0.1,
                max_exposure_by_asset=0.2,
                max_exposure_by_correlated_group=0.3,
                max_turnover=5.0,
                expected_holding_horizon="intraday to swing",
                execution_style="maker_taker_adaptive",
                take_profit_model="laddered_partial_plus_trailing",
                trailing_exit=True,
                compound_profits=False,
                min_net_edge_bps=5.0,
                approvals_required=tier in {"TIER_3_HIGH_RISK", "TIER_4_EXPERT_HIGH_RISK"},
                failure_modes=["stale data", "slippage shock", "regime shift"],
                disable_criteria=["drawdown breach", "latency breach", "risk engine halt"],
                cooldown_logic="exponential cooldown after consecutive losses",
                explainability_output="signal drivers, regime, sizing and risk gate verdict",
                backtest_caveats="fill realism depends on latency, partial fills, and queue assumptions",
                live_deployment_prerequisites=["unit tests", "replay smoke", "paper canary", "approvals"],
                implementation_status=status,
                unit_tested=unit,
                backtest_ready=backtest,
                replay_ready=replay,
                paper_ready=paper,
                live_safe=live,
            )
        )
    return specs
