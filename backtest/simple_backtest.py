import sys
import os
import pandas as pd
from sqlalchemy import asc
import importlib

sys.path.append(os.getcwd())

from models.database import SessionLocal
from models.ohlcv import OHLCV
from models.strategy_config import StrategyConfig
from strategies.moving_average import MovingAverageCrossover # Ensure this is imported for now, or use dynamic loading

def get_strategy_class(class_name):
    # For now, simplistic mapping or dynamic import
    if class_name == "MovingAverageCrossover":
        return MovingAverageCrossover
    # Add other mappings here or use importlib to load from string "module.ClassName"
    raise ValueError(f"Unknown strategy class: {class_name}")

def run_backtest(ticker, strategy_db_name, initial_capital=10000.0):
    print(f"--- Running Backtest for {ticker} using {strategy_db_name} ---")
    
    db = SessionLocal()
    
    # 1. Load Strategy Config
    config = db.query(StrategyConfig).filter_by(name=strategy_db_name).first()
    if not config:
        print(f"Strategy '{strategy_db_name}' not found in DB.")
        db.close()
        return

    print(f"Loaded Config: {config.parameters}")
    StrategyClass = get_strategy_class(config.class_name)
    
    # Instantiate with parameters from DB
    params = config.parameters if config.parameters else {}
    strategy = StrategyClass(config.name, **params)
    strategy.initialize({})

    # 2. Load Data
    rows = db.query(OHLCV).filter_by(ticker=ticker).order_by(asc(OHLCV.timestamp)).all()
    if not rows:
        print("No market data found!")
        db.close()
        return

    prices = [r.close for r in rows]
    dates = [r.timestamp for r in rows]
    print(f"Loaded {len(prices)} days of data.")
    
    # 3. Simulate Loop
    cash = initial_capital
    holdings = 0
    trades = 0
    history_equity = []
    
    for i, (date, price) in enumerate(zip(dates, prices)):
        data_point = {"price": price, "timestamp": date}
        strategy.on_data(data_point)
        
        if strategy.should_buy(data_point):
            if cash > price:
                shares = int(cash // price)
                cash -= shares * price
                holdings += shares
                trades += 1
                print(f"[{date.date()}] BUY  {shares} @ ${price:.2f}")

        elif strategy.should_sell(data_point):
            if holdings > 0:
                cash += holdings * price
                holdings = 0
                trades += 1
                print(f"[{date.date()}] SELL ALL @ ${price:.2f}")
        
        equity = cash + (holdings * price)
        history_equity.append(equity)
    
    # 4. Results
    final_equity = history_equity[-1]
    ret = ((final_equity - initial_capital) / initial_capital) * 100
    
    print("\n--- Results ---")
    print(f"Strategy:        {config.name}")
    print(f"Parameters:      {params}")
    print(f"Initial Capital: ${initial_capital:.2f}")
    print(f"Final Equity:    ${final_equity:.2f}")
    print(f"Total Return:    {ret:.2f}%")
    print(f"Total Trades:    {trades}")
    print("---------------------------------")
    
    db.close()

def setup_demo_strategy():
    """Helper to insert a demo strategy into DB if not exists"""
    db = SessionLocal()
    name = "GoldenCross_Msg_Config"
    exists = db.query(StrategyConfig).filter_by(name=name).first()
    if not exists:
        print(f"Creating demo strategy {name}...")
        s = StrategyConfig(
            name=name,
            class_name="MovingAverageCrossover",
            parameters={"short_window": 20, "long_window": 50}, # Different params than default
            description="A database-configured SMA strategy"
        )
        db.add(s)
        db.commit()
    db.close()
    return name

if __name__ == "__main__":
    # Ensure we have a strategy in the DB to test
    strat_name = setup_demo_strategy()
    run_backtest("AAPL", strat_name)
