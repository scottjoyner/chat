from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_dashboard_and_portfolio_endpoints() -> None:
    dash = client.get('/ops/dashboard/snapshot')
    assert dash.status_code == 200
    payload = dash.json()
    assert payload['total_nav'] > 0
    assert len(payload['portfolios']) >= 2

    portfolio_id = payload['portfolios'][0]['portfolio_id']
    detail = client.get(f'/ops/portfolios/{portfolio_id}')
    assert detail.status_code == 200
    assert 'sleeves' in detail.json()


def test_treasury_preview_and_execute() -> None:
    preview = client.post(
        '/ops/treasury/preview',
        json={
            'source_portfolio': 'cb-core-mm',
            'destination_portfolio': 'cb-hedge',
            'asset': 'USDC',
            'amount': 10000,
            'rationale': 'fund hedge demand',
        },
    )
    assert preview.status_code == 200
    preview_id = preview.json()['preview_id']

    execute = client.post('/ops/treasury/execute', json={'preview_id': preview_id})
    assert execute.status_code == 200
    assert execute.json()['status'] == 'executed'


def test_order_preview_submit_and_cancel() -> None:
    preview = client.post(
        '/ops/orders/preview',
        json={
            'portfolio_id': 'cb-core-mm',
            'sleeve_id': 'maker',
            'strategy_id': 'adaptive_spread_mm',
            'product_id': 'BTC-USD',
            'side': 'buy',
            'order_type': 'limit',
            'size': 0.5,
            'limit_price': 60000,
        },
    )
    assert preview.status_code == 200

    submitted = client.post('/ops/orders/submit', json={'preview_id': preview.json()['preview_id']})
    assert submitted.status_code == 200
    order_id = submitted.json()['order_id']

    open_orders = client.get('/ops/orders/open')
    assert open_orders.status_code == 200
    assert any(order['order_id'] == order_id for order in open_orders.json())

    canceled = client.post(f'/ops/orders/{order_id}/cancel')
    assert canceled.status_code == 200
    assert canceled.json()['status'] == 'canceled'
