from risk.engine import RiskEngine, RiskPolicy
from core.models.domain import OrderIntent, CapitalBucketType


def test_locked_reserve_blocked():
    engine = RiskEngine(RiskPolicy())
    intent = OrderIntent(strategy_id="s", product_id="BTC-USD", side="BUY", order_type="LIMIT", size=0.1, price=30000, bucket=CapitalBucketType.LOCKED_RESERVE, rationale="test")
    allowed, reason = engine.evaluate(intent, mark_price=30000)
    assert not allowed
    assert "locked reserve" in reason


def test_small_order_allowed():
    engine = RiskEngine(RiskPolicy(max_order_notional=10000))
    intent = OrderIntent(strategy_id="s", product_id="BTC-USD", side="BUY", order_type="LIMIT", size=0.01, price=30000, rationale="test")
    allowed, _ = engine.evaluate(intent, mark_price=30000)
    assert allowed
