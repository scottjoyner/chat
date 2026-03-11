from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class StrategyRuntimeFlags(BaseModel):
    backtest_enabled: bool = True
    paper_enabled: bool = True
    live_enabled: bool = False


class StrategyConfig(BaseModel):
    strategy_id: str
    enabled: bool = False
    supported_products: list[str] = Field(default_factory=lambda: ["BTC-USD"])
    risk_tier: str
    max_capital_fraction: float = Field(ge=0.0, le=1.0)
    sizing_model: str
    min_size: float = Field(gt=0.0)
    max_size: float = Field(gt=0.0)
    entry_threshold: float
    exit_threshold: float
    stop_loss_bps: float = Field(ge=0.0)
    take_profit_bps: float = Field(ge=0.0)
    trailing_take_profit_bps: float = Field(ge=0.0)
    cooldown_bars: int = Field(ge=0)
    warmup_bars: int = Field(ge=0)
    approvals_required: bool = False
    telemetry_enabled: bool = True
    runtime_flags: StrategyRuntimeFlags = Field(default_factory=StrategyRuntimeFlags)

    @model_validator(mode="after")
    def validate_thresholds(self) -> "StrategyConfig":
        if self.max_size < self.min_size:
            raise ValueError("max_size must be >= min_size")
        if self.exit_threshold > self.entry_threshold:
            raise ValueError("exit_threshold must be <= entry_threshold")
        if not self.supported_products:
            raise ValueError("supported_products must not be empty")
        if self.runtime_flags.live_enabled and not self.approvals_required:
            raise ValueError("live_enabled requires approvals_required")
        if self.take_profit_bps == 0 and self.trailing_take_profit_bps > 0:
            raise ValueError("trailing take profit requires non-zero take_profit_bps")
        return self
