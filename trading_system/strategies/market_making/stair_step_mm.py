from strategies.base.interfaces import Strategy, StrategySignal


class StairStepMarketMakerStrategy(Strategy):
    strategy_id = "StairStepMarketMakerStrategy"

    def metadata(self) -> dict:
        return {"name": self.strategy_id, "paper_mode": True, "live_supported": True}

    def generate_signal(self, market_state: dict) -> StrategySignal | None:
        product = market_state.get("product_id", "BTC-USD")
        score = float(market_state.get("score", 0.0))
        if score <= 0:
            return None
        return StrategySignal(strategy_id=self.strategy_id, product_id=product, score=score, reason="sample positive score")

    def explain_trade(self, signal: StrategySignal) -> str:
        return f"{self.strategy_id} proposes trade on {signal.product_id} with score {signal.score}"
