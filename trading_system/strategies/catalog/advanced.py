from __future__ import annotations

from dataclasses import dataclass

from strategies.base.interfaces import Strategy, StrategySignal


@dataclass(frozen=True)
class StrategySpec:
    strategy_id: str
    purpose: str
    regime_suitability: str
    required_data: list[str]
    required_latency_budget_ms: float
    sizing_model: str
    risk_ceilings: str
    expected_holding_horizon: str
    execution_style: str
    failure_modes: list[str]
    disable_criteria: list[str]
    cooldown_logic: str
    explainability_output: str
    backtest_caveats: str
    live_deployment_prerequisites: list[str]


class GenericSpecStrategy(Strategy):
    def __init__(self, spec: StrategySpec) -> None:
        self.spec = spec
        self.strategy_id = spec.strategy_id

    def metadata(self) -> dict:
        return self.spec.__dict__.copy()

    def generate_signal(self, market_state: dict) -> StrategySignal | None:
        product = market_state.get("product_id", "BTC-USD")
        score = float(market_state.get("score", 0.0))
        threshold = float(market_state.get("threshold", 0.1))
        if score <= threshold:
            return None
        return StrategySignal(
            strategy_id=self.strategy_id,
            product_id=product,
            score=score,
            reason=f"{self.spec.purpose}; regime={self.spec.regime_suitability}",
        )

    def explain_trade(self, signal: StrategySignal) -> str:
        return f"{self.strategy_id} score={signal.score:.4f} style={self.spec.execution_style} risk={self.spec.risk_ceilings}"


def advanced_specs() -> list[StrategySpec]:
    rows = [
        ("AvellanedaStoikovInventoryMM", "inventory-aware quoting", "range/2-sided liquid", ["book", "vol"], 25),
        ("QueueReactiveFillProbabilityMM", "queue-reactive maker", "stable spread", ["book", "fills", "queue"], 15),
        ("VolatilityScaledSkewMM", "vol-scaled skew maker", "volatile/mean reverting", ["book", "vol"], 20),
        ("MomentumIgnitionDetector", "detect/avoid ignition", "toxic burst", ["trades", "book"], 10),
        ("TradeFlowImbalanceMeanReversion", "short horizon reversion", "microstructure noisy", ["trades", "delta"], 8),
        ("OrderFlowToxicityFilterVPIN", "toxic-flow filter", "adverse selection", ["vpin_proxy", "book"], 12),
        ("KalmanDynamicHedgePairs", "dynamic hedge-ratio stat-arb", "cointegrated pairs", ["mid", "spreads"], 200),
        ("CointegrationBasketArb", "basket cointegration arb", "cross-product dispersion", ["bars", "features"], 500),
        ("CrossExchangeShadowArb", "shadow arb abstraction", "venue dislocations", ["coinbase", "shadow"], 50),
        ("FundingBasisRegimeAllocator", "funding/basis allocator", "carry regimes", ["basis", "funding"], 1_000),
        ("GammaLikeVolHarvest", "vol harvesting approximation", "choppy high vol", ["vol", "book"], 200),
        ("AtrChannelBreakoutVolTarget", "ATR breakout vol-targeted", "trend expansion", ["candles", "atr"], 150),
        ("OpeningRangeSessionBreakout", "opening-range breakout", "session transitions", ["session", "book"], 100),
        ("TrendPullbackContinuation", "trend pullback continuation", "persistent trend", ["candles", "ema"], 300),
        ("ProbabilisticRegimeClassifier", "probabilistic regime model", "all", ["returns", "vol", "liquidity"], 500),
        ("MetaStrategySelector", "select best strategy by quality", "portfolio adaptive", ["strategy_metrics"], 1_000),
        ("ExhaustionMoveReversal", "reversal after exhaustion", "spike extremes", ["trades", "rsi"], 80),
        ("MarketMicroburstMomentum", "microburst momentum", "high-impulse", ["subsec_trades", "book"], 5),
        ("QuoteFadeCancelPressurePredictor", "predict fade pressure", "maker adverse", ["cancel_rates", "book"], 10),
        ("LiquidityShelfReaction", "support/resistance shelf reaction", "book cliffs", ["depth", "imbalances"], 20),
        ("InventoryHedgingOverlay", "inventory hedge overlay", "inventory stress", ["inventory", "hedge_px"], 30),
        ("DynamicTreasurySleeveAllocator", "dynamic treasury between sleeves", "multi-objective", ["sleeve_pnl", "risk"], 5_000),
        ("CrashResponseAccumulator", "opportunistic crash accumulator", "crash events", ["drawdown", "liquidity"], 250),
        ("VolCompressionExpansionDetector", "compression->expansion detector", "pre-breakout", ["realized_vol"], 120),
        ("CorrelationBreakdownDefense", "contagion defense", "regime breaks", ["corr", "beta"], 1_000),
        ("TailRiskHedgeTrigger", "tail-risk hedge overlay", "left-tail elevated", ["skew", "vol"], 500),
        ("ExecutionShortfallMinimizer", "minimize execution shortfall", "large parent orders", ["book", "fills"], 25),
        ("AdaptiveParticipationAlgo", "adaptive participation", "execution participation", ["volume_curve", "book"], 50),
        ("ReinforcementLearningHarness", "RL research harness", "research only", ["feature_store"], 5_000),
        ("BayesianParameterAdaptation", "bayesian parameter adaptation", "slowly changing regimes", ["priors", "perf"], 2_000),
        ("CrossSectionalIntradayDispersion", "cross-sectional dispersion", "intraday dispersion", ["universe_returns"], 500),
        ("MakerTakerSwitcher", "switch maker/taker by fill quality", "dynamic spread", ["fill_quality", "book"], 10),
        ("OrderbookResiliencyRefillSpeed", "resiliency/refill-speed", "liquidity shocks", ["book_updates"], 15),
        ("LatencyArbResearchSimulator", "latency-arb simulator", "research only", ["timestamps", "book"], 1),
        ("SweepDetectionResponse", "sweep detection", "aggressive sweep", ["trade_prints", "book"], 5),
        ("PortfolioDynamicConvexityAllocator", "dynamic convexity allocator", "tail-risk adaptive", ["portfolio_greeks_proxy"], 1_000),
    ]
    out: list[StrategySpec] = []
    for sid, purpose, regime, data, latency in rows:
        out.append(
            StrategySpec(
                strategy_id=sid,
                purpose=purpose,
                regime_suitability=regime,
                required_data=data,
                required_latency_budget_ms=float(latency),
                sizing_model="volatility_target + risk_budget",
                risk_ceilings="per-strategy VaR + drawdown + stress limits",
                expected_holding_horizon="sub-second to multi-day depending on strategy",
                execution_style="maker/taker adaptive",
                failure_modes=["stale data", "regime misclassification", "exchange degraded"],
                disable_criteria=["trust score UNTRUSTED", "drawdown breach", "latency budget breach"],
                cooldown_logic="cooldown window increases after repeated stops",
                explainability_output="signal drivers + regime + risk budget utilization",
                backtest_caveats="queue assumptions and latency injection sensitivity",
                live_deployment_prerequisites=["paper pass", "shadow pass", "canary approval"],
            )
        )
    return out
