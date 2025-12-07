# Algo Trading Bot Project

## Overview
This is a full-stack algorithmic trading system capable of:
1.  **Market Data**: Fetching real-time and historical data from Financial Modeling Prep (FMP).
2.  **Strategies**: Configuring strategies (like Moving Average Crossover) via Database.
3.  **Backtesting**: Simulating performance against historical data.
4.  **Execution**: Supporting both **Paper Trading** (simulated) and **Live Trading** (Robinhood).
5.  **User Interface**: A modern React Dashboard to monitor performance and control the bot.

## Quick Start

### 1. Prerequisites
*   Python 3.10+
*   Node.js & npm
*   MySQL Database (or Docker equivalent)
*   FMP API Key (Financial Modeling Prep)
*   Robinhood Account (for Live Trading)

### 2. Installation
1.  **Clone & Setup Python**:
    ```bash
    git clone <repo>
    cd algo_trading_app
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```ini
    DB_HOST=localhost
    DB_PORT=3306
    DB_USER=root
    DB_PASSWORD=your_password
    DB_NAME=algo_trading
    
    FMP_API_KEY=your_fmp_key
    
    RH_USERNAME=your_rh_email
    RH_PASSWORD=your_rh_password
    RH_TOTP=your_2fa_totp_secret
    ```

3.  **Database Migration**:
    Initialize the database schema:
    ```bash
    alembic upgrade head
    ```

4.  **Load Historical Data (Optional)**:
    Populate the DB with past market data for backtesting:
    ```bash
    python data/load_historical_data.py
    ```

### 3. Running the System
You need two terminals open:

**Terminal 1: Backend API**
```bash
venv\Scripts\uvicorn api.main:app --reload --port 8000
```

**Terminal 2: Frontend Dashboard**
```bash
cd dashboard
npm install
npm run dev
```

Visit `http://localhost:5173` to access the Dashboard.

## Project Structure
*   `api/`: FastAPI backend for UI and Engine control.
*   `backtest/`: Scripts for running strategy simulations.
*   `brokers/`: Adapters for Robinhood and Paper trading.
*   `config/`: Centralized settings.
*   `dashboard/`: React + Vite Frontend.
*   `data/`: Scripts for loading historical market data.
*   `execution/`: The core `TradingEngine` loop.
*   `migrations/`: Alembic database migrations.
*   `models/`: SQLAlchemy database models (`Trade`, `OHLCV`, `Portfolio`).
*   `strategies/`: Trading strategy logic.
*   `utils/`: Helper scripts.

## Usage
1.  **Virtual Trading**: Select this mode on the Home page. The bot will trade with $10,000 simulated cash using real-time market prices.
2.  **Live Trading**: Select this mode to connect to Robinhood. **WARNING**: This risks real capital. Ensure your configured strategies and limits are safe.
