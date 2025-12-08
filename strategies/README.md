# Trading Strategy Architecture

This document defines the core components of the trading strategies used in the Algo Trading App. All strategies are designed to be explicitly described, configurable, and modular.

## 1. Stock Selection Strategy

The Stock Selection Strategy determines *which* assets the system monitors and trades.

*   **Logic**: Currently, the system operates on a **Watchlist-based selection**.
    *   Users manually select tickers (e.g., AAPL, GOOGL) during Session creation or via the "Ticker Management" interface.
    *   The **Trading Engine** iterates through this list of valid `SessionTicker`s.
*   **Algorithmic Screening**: 
    *   Future versions will support dynamic stock selection (Screeners) that populate the `SessionTicker` list automatically based on criteria (e.g., "Top Gainers", "High Volume").
    *   Implementation: A `StockSelector` class would interface with the Market Data API to filter symbols and update the session's ticker list before each scan cycle.

## 2. Buy Strategy

The Buy Strategy defines the precise conditions required to enter a position (LONG).

*   **Interface**: `should_buy(data) -> bool`
*   **Execution**: The Engine calls this method for every ticker in the watchlist on every interval.
*   **Implementations**:
    *   **Golden Cross (SMA)**: Buys when the Short SMA crosses *above* the Long SMA.
        *   *Parameters*: `short_window` (default: 10), `long_window` (default: 30).
    *   **RSI Mean Reversion**: Buys when RSI drops below the distinct "Oversold" threshold.
        *   *Parameters*: `period` (14), `oversold` (30).
    *   **Momentum Breakout**: Buys when the price momentum (percentage change over lookback) exceeds a positive threshold.
        *   *Parameters*: `lookback_period` (10), `threshold` (0.02 or 2%).
    *   **Bollinger Bands**: Buys when price touches or crosses below the Lower Band (Mean Reversion).
        *   *Parameters*: `period` (20), `num_std` (2).

## 3. Sell Strategy

The Sell Strategy defines the conditions to exit a position.

*   **Interface**: `should_sell(data) -> bool`
*   **Execution**: The Engine calls this method if a position currently exists (implied or explicit).
*   **Implementations**:
    *   **Golden Cross (SMA)**: Sells when the Short SMA crosses *below* the Long SMA.
    *   **RSI Mean Reversion**: Sells when RSI rises above the "Overbought" threshold.
        *   *Parameters*: `overbought` (70).
    *   **Momentum Breakout**: Sells when momentum drops below a negative threshold (trend reversal).
        *   *Parameters*: `threshold` (same logic as buy, usually symmetric or specific).
    *   **Bollinger Bands**: Sells when price touches or crosses above the Upper Band.

## Configuration

Strategies are configured dynamically via the `strategies` database table. 
*   **Class Name**: Maps to the Python implementation (e.g., `MovingAverageCrossover`).
*   **Parameters**: A JSON object (e.g., `{"short_window": 50, "long_window": 200}`) that injects settings at runtime.
*   **Activation**: Strategies can be toggled per session.

## Adding New Strategies

1. Inherit from `BaseStrategy`.
2. Implement `should_buy` and `should_sell`.
3. Register the strategy in `models/strategy_config.py` (or via API seeding).
4. Update `strategies/factory.py` to handle the new class instantiation.
