from strategies.catalog.advanced import CATALOG_100, advanced_specs
from strategies.catalog.config_schema import StrategyConfig, StrategyRuntimeFlags


def test_catalog_has_exactly_100_named_strategies():
    assert len(CATALOG_100) == 100
    assert len(set(CATALOG_100)) == 100


def test_advanced_specs_has_complete_contract():
    specs = advanced_specs()
    assert len(specs) == 100
    for spec in specs:
        assert spec.strategy_id
        assert spec.risk_tier.startswith("TIER_")
        assert 0 <= spec.max_capital_fraction <= 1
        assert spec.max_size >= spec.min_size


def test_strategy_config_validation_rejects_unsafe_live_enablement():
    try:
        StrategyConfig(
            strategy_id="S001",
            enabled=True,
            risk_tier="TIER_3_HIGH_RISK",
            max_capital_fraction=0.1,
            sizing_model="fixed_fraction",
            min_size=0.01,
            max_size=1.0,
            entry_threshold=1.5,
            exit_threshold=1.0,
            stop_loss_bps=20,
            take_profit_bps=30,
            trailing_take_profit_bps=0,
            cooldown_bars=5,
            warmup_bars=100,
            approvals_required=False,
            runtime_flags=StrategyRuntimeFlags(live_enabled=True),
        )
        raised = False
    except ValueError:
        raised = True
    assert raised
