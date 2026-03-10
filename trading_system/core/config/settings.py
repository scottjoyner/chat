import os
from enum import Enum

from pydantic import BaseModel


class TradingMode(str, Enum):
    SIMULATION = "SIMULATION"
    PAPER = "PAPER"
    LIVE_APPROVAL_REQUIRED = "LIVE_APPROVAL_REQUIRED"
    LIVE_SEMI_AUTO = "LIVE_SEMI_AUTO"
    LIVE_AUTO = "LIVE_AUTO"
    SHADOW = "SHADOW"
    CANARY = "CANARY"


class Settings(BaseModel):
    app_env: str = "dev"
    trading_mode: TradingMode = TradingMode.PAPER
    coinbase_api_key: str = ""
    coinbase_api_secret: str = ""
    coinbase_passphrase: str = ""
    coinbase_portfolio_ids: str = "default"
    database_url: str = "postgresql://trader:trader@localhost:5432/trading"
    redis_url: str = "redis://localhost:6379/0"
    require_approvals: bool = True
    live_trading_enabled: bool = False
    low_latency_mode: bool = False
    gpu_enabled: bool = False
    queue_model: str = "simple"
    canary_rollout_pct: float = 0.0

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "dev"),
            trading_mode=os.getenv("TRADING_MODE", "PAPER"),
            coinbase_api_key=os.getenv("COINBASE_API_KEY", ""),
            coinbase_api_secret=os.getenv("COINBASE_API_SECRET", ""),
            coinbase_passphrase=os.getenv("COINBASE_PASSPHRASE", ""),
            coinbase_portfolio_ids=os.getenv("COINBASE_PORTFOLIO_IDS", "default"),
            database_url=os.getenv("DATABASE_URL", "postgresql://trader:trader@localhost:5432/trading"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            require_approvals=os.getenv("REQUIRE_APPROVALS", "true").lower() == "true",
            live_trading_enabled=os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true",
            low_latency_mode=os.getenv("LOW_LATENCY_MODE", "false").lower() == "true",
            gpu_enabled=os.getenv("GPU_ENABLED", "false").lower() == "true",
            queue_model=os.getenv("QUEUE_MODEL", "simple"),
            canary_rollout_pct=float(os.getenv("CANARY_ROLLOUT_PCT", "0")),
        )

    def validate_safety(self) -> None:
        if self.trading_mode.name.startswith("LIVE") and not self.live_trading_enabled:
            raise ValueError("Live mode requested while LIVE_TRADING_ENABLED is false")
