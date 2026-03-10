from enum import Enum
from pydantic import BaseModel, Field


class CapitalBucketType(str, Enum):
    LOCKED_RESERVE = "LOCKED_RESERVE"
    ACTIVE_TRADING = "ACTIVE_TRADING"
    MARKET_MAKING = "MARKET_MAKING"
    ACCUMULATION = "ACCUMULATION"
    HEDGING = "HEDGING"
    CASH_BUFFER = "CASH_BUFFER"


class CapitalBucket(BaseModel):
    name: str
    bucket_type: CapitalBucketType
    target_weight: float = Field(ge=0, le=1)
    min_weight: float = Field(ge=0, le=1, default=0)
    max_weight: float = Field(ge=0, le=1, default=1)
    locked: bool = False


class OrderIntent(BaseModel):
    strategy_id: str
    product_id: str
    side: str
    order_type: str
    size: float
    price: float | None = None
    bucket: CapitalBucketType = CapitalBucketType.ACTIVE_TRADING
    rationale: str
