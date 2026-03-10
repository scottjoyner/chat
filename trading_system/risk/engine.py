from dataclasses import dataclass
from core.models.domain import CapitalBucketType, OrderIntent


@dataclass
class RiskPolicy:
    max_order_notional: float = 5_000
    max_open_orders: int = 20
    stale_data_block: bool = True


class RiskEngine:
    def __init__(self, policy: RiskPolicy) -> None:
        self.policy = policy
        self.open_orders = 0
        self.kill_switch = False

    def evaluate(self, intent: OrderIntent, mark_price: float, stale_data: bool = False) -> tuple[bool, str]:
        if self.kill_switch:
            return False, "global kill switch enabled"
        if stale_data and self.policy.stale_data_block:
            return False, "stale market data"
        if intent.bucket == CapitalBucketType.LOCKED_RESERVE:
            return False, "locked reserve cannot be traded"
        if self.open_orders >= self.policy.max_open_orders:
            return False, "max open orders reached"
        notional = intent.size * (intent.price or mark_price)
        if notional > self.policy.max_order_notional:
            return False, "order exceeds max notional"
        return True, "approved"
