# Project Documentation

## Overview
This document summarizes the structure and functions within the Algo Trading App codebase.

## Directory Structure
- `backtest/`: Contains backtesting modules (currently empty).
- `config/`: Configuration files.
- `data/`: Data management and database interactions (currently empty).
- `execution/`: Live and paper trading execution modules.
- `migrations/`: Database migrations.
- `models/`: Data models and market data fetchers.
- `strategies/`: Trading strategies (currently empty).
- `utils/`: Utility scripts (currently empty).
- `main.py`: Main entry point for the application.

## Function & Class Summaries

### Execution Modules

#### `execution/live_trader.py`
Handles interactions with the Robinhood API for live trading.

- **`robinhood_login()`**
  - **Purpose**: Authenticates with Robinhood using credentials and TOTP secret from environment variables.
  - **Inputs**: None (uses `.env`).
  - **Outputs**: Prints login status; exits on failure.

- **`get_my_stock_holdings()`**
  - **Purpose**: Retrieves current stock holdings.
  - **Inputs**: None.
  - **Outputs**: `pandas.DataFrame` of holdings or empty DataFrame on error.

- **`get_total_equity(holdings)`**
  - **Purpose**: Calculates total equity from a holdings DataFrame.
  - **Inputs**: `holdings` (DataFrame).
  - **Outputs**: Float representing total equity.

- **`get_cash_portfolio()`**
  - **Purpose**: Retrieves available cash in the portfolio.
  - **Inputs**: None.
  - **Outputs**: Float of portfolio cash.

- **`buy_stock(ticker, value, extend_hours=True)`**
  - **Purpose**: Places a fractional buy order by price. Retries up to 10 times if order is not filled.
  - **Inputs**: 
    - `ticker` (str): Stock symbol.
    - `value` (float): Amount to buy.
    - `extend_hours` (bool): Whether to trade during extended hours.
  - **Outputs**: Returns `ticker` if successful, `None` otherwise.

- **`sell_stock(ticker, value)`**
  - **Purpose**: Places a fractional sell order by price. Retries up to 10 times.
  - **Inputs**:
    - `ticker` (str): Stock symbol.
    - `value` (float): Amount to sell.
  - **Outputs**: Returns `ticker` if successful, `None` otherwise.

- **`log_record(ticker, action, value)`**
  - **Purpose**: Placeholder for logging trade actions.

### Models & Data

#### `models/market_data.py`
Fetches financial data from Financial Modeling Prep API.

- **`class FinancialDataFetcher`**
  - **`__init__(self)`**: Initializes the session and loads API key from `.env`.
  - **`_request_api(self, endpoint, **params)`**: Private helper to make GET requests to the API.
  - **`get_financial_statement(self, ticker, statement_type, period='quarter')`**: Fetches financial statements (e.g., income statement).
  - **`get_company_profile(self, ticker)`**: Fetches company profile information.

### Entry Point

#### `main.py`
- Serves as the entry point.
- Imports `execution.live_trader` and `execution.robinhood_auth` (though usage of `robinhood_auth` usually maps to `live_trader` functionality in this codebase).
- Demonstrates a login and an example buy order.

### Placeholders / Empty Files
The following files exist but currently contain no functional code or only comments:
- `strategies/base_strategy.py`
- `backtest/backtester.py`
- `data/data_manager.py`
- `data/database.py`
- `execution/paper_trader.py`
- `models/trade_orders.py`
- `models/performance_metrics.py` (Comment only)
- `utils/logger.py`
- `utils/plotter.py`
