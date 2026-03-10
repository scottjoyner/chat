from analytics.metrics.performance import basic_metrics


def test_metrics():
    m = basic_metrics([0.01, -0.005, 0.01])
    assert 'sharpe' in m
