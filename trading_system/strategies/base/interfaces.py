from abc import ABC, abstractmethod
from pydantic import BaseModel


class StrategySignal(BaseModel):
    strategy_id: str
    product_id: str
    score: float
    reason: str


class Strategy(ABC):
    strategy_id: str

    @abstractmethod
    def metadata(self) -> dict: ...

    @abstractmethod
    def generate_signal(self, market_state: dict) -> StrategySignal | None: ...

    @abstractmethod
    def explain_trade(self, signal: StrategySignal) -> str: ...
