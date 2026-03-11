# STRATEGY_DEPENDENCY_MAP

## Runtime dependency layers

1. Market data feeds (candles, trades, orderbook)
2. Feature/indicator pipeline (ATR, RSI, realized vol, microstructure features)
3. Strategy contract + registry
4. Risk/approvals + capital buckets
5. Execution + treasury sweep hooks

## Strategy-to-subsystem mapping

| Strategy | Data | Risk Gates | Execution Path | Notes |
|---|---|---|---|---|
| Multi-timeframe breakout | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Donchian channel breakout | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| ATR channel breakout | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Moving-average crossover | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| EMA ribbon trend-following | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Supertrend continuation | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| ADX trend-strength breakout | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Trend pullback continuation | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Opening-range breakout | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Volatility expansion breakout | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Turtle-style breakout | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Keltner channel breakout | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Regression-slope momentum | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Time-series momentum | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Cross-sectional momentum rotation | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Z-score mean reversion | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Bollinger band reversion | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| RSI exhaustion reversal | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Short-term reversal after large candle | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |
| Gap-fill mean reversion | candles, trades, orderbook | risk.engine + approvals | execution/router | fill realism depends on latency, partial fills, and queue assumptions |

(First 20 shown; remaining strategies follow same contract and are listed in STRATEGY_CATALOG.)
