# Project Tasks

## 1. Core Infrastructure & Database
- [x] **Schema Design**: Define detailed data models (Trades, OHLCV, Portfolio).
- [x] **Database Setup**: Configure MySQL with Docker (native install used).
- [x] **ORM Setup**: SQLAlchemy configuration with environment variables.
- [x] **Logging**: Basic logging in `engine.py`.
- [x] **Migrations**: Set up Alembic for database schema migrations (currently `migrations/` is empty).
- [x] **Config Management**: Ensure all secrets (API keys) are loaded safely from `.env`.

## 2. Market Data Layer
- [x] **Real-time Data Fetcher**: Implement a class to fetch live price data (e.g., using `yfinance`, `alpha_vantage`, or `robin_stocks`).
  - *Implemented*: `models/market_data.py` using FMP API.
  - *Integrated*: `execution/engine.py` now uses live prices.
- [x] **Historical Data Loader**: Utility to download and save historical data to DB for backtesting.
  - *Implemented*: `data/load_historical_data.py` (Filled 1 year of daily data for 5 tickers).
- [x] **Data Normalization**: Standardize data format (OHLCV) across different sources.
  - *Done*: `models/ohlcv.py` enforces structure.

## 3. Execution & Broker Integration
- [x] **Broker Interface**: Create an abstract `Broker` class.
  - *Implemented*: `brokers/base_broker.py`.
- [x] **Robinhood Implementation**: Implement `RobinhoodBroker` using `robin_stocks` for:
  - Fetching portfolio/holdings.
  - Placing Buy/Sell orders.
  - checking order status.
  - *Implemented*: `brokers/robinhood_broker.py` (Draft ready).
- [x] **Paper Trading Mode**: Update `execute_trade` in `engine.py` to support a "Paper" mode that tracks simulated balance without calling the API.
  - *Implemented*: Engine supports `paper_trading=True` with full Account and Holding tracking.

## 4. Strategy Development
- [ ] **Strategy Interface**: Refine `BaseStrategy` (inputs, signal generation).
- [ ] **Implement Strategies**:
  - `MovingAverageCrossover`
  - `RSIStrategy`
  - `MeanReversion`
- [ ] **Risk Management**: Add global risk checks (max drawdown, max position size) before strategies execute.

## 5. Backtesting Engine
- [x] **Backtester**: Create a script to run strategies against historical data in the DB.
  - *Implemented*: `backtest/simple_backtest.py`.
- [ ] **Performance Metrics**: Calculate Sharpe Ratio, Max Drawdown, Win Rate.
- [ ] **Reporting**: Generate a simple report/plot of backtest results.

## 6. User Interface
- [x] **API Backend**: Create FastAPI app (`api/main.py`) to serve Account, Portfolio, and Trades.
  - *Implemented*: FastAPI serving on port 8000.
- [x] **Frontend Setup**: Initialize React/Vite project for the dashboard.
  - *Implemented*: `dashboard/` folder with React+Vite.
- [x] **Dashboard Layout**: Display valid paper trading portfolio and live prices.
  - *Implemented*: `App.jsx` connects to API and displays live stats.
- [x] **Controls**: Start/Stop Engine from UI.
  - *Implemented*: `Home.jsx` creates a landing page, `Dashboard.jsx` auto-starts the engine based on mode selection.
