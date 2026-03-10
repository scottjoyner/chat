from strategies.trend.breakout import TrendFollowingBreakoutStrategy
from strategies.mean_reversion.zscore import MeanReversionZScoreStrategy
from strategies.ensemble.rotation import CrossSectionalRelativeStrengthStrategy
from strategies.market_making.stair_step_mm import StairStepMarketMakerStrategy
from strategies.market_making.adaptive_spread_mm import AdaptiveSpreadMMStrategy
from strategies.mean_reversion.grid_capture import GridRebalanceCaptureStrategy
from strategies.microstructure.orderbook_imbalance import OrderBookImbalanceStrategy
from strategies.execution_algos.vwap_twap import VwapTwapExecutionStrategy
from strategies.stat_arb.pairs import PairsTradingStrategy
from strategies.volatility.vol_breakout import VolatilityBreakoutStrategy
from strategies.ensemble.regime_allocator import RegimeSwitchingEnsembleAllocator
from strategies.accumulation.dca import LongHorizonDcaStrategy
from strategies.special.liquidity_snapback import LiquidityVacuumSnapbackStrategy
from strategies.special.basis_carry import BasisCarryDerivativesStrategy


def load_strategies() -> list:
    return [
        TrendFollowingBreakoutStrategy(), MeanReversionZScoreStrategy(), CrossSectionalRelativeStrengthStrategy(),
        StairStepMarketMakerStrategy(), AdaptiveSpreadMMStrategy(), GridRebalanceCaptureStrategy(),
        OrderBookImbalanceStrategy(), VwapTwapExecutionStrategy(), PairsTradingStrategy(),
        VolatilityBreakoutStrategy(), RegimeSwitchingEnsembleAllocator(), LongHorizonDcaStrategy(),
        LiquidityVacuumSnapbackStrategy(), BasisCarryDerivativesStrategy(),
    ]
