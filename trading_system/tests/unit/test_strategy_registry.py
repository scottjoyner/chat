from strategies.registry.registry import load_strategies


def test_has_12_plus_strategies():
    strategies = load_strategies()
    assert len(strategies) >= 12
