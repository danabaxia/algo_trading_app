from models.database import init_db, SessionLocal
from models.strategy_config import StrategyConfig

def seed_strategies():
    db = SessionLocal()
    try:
        # 1. Initialize Tables (Create if not exist)
        print("Initializing database tables...")
        init_db()
        
        # 2. Seed Strategies
        if db.query(StrategyConfig).count() == 0:
            print("Seeding default strategies...")
            defaults = [
                {
                    "name": "GoldenCross_SMA",
                    "class_name": "MovingAverageCrossover",
                    "parameters": {"short_window": 10, "long_window": 30},
                    "description": "Simple Moving Average Crossover"
                },
                {
                    "name": "RSI_Oscillator",
                    "class_name": "RSIStrategy",
                    "parameters": {"period": 14, "oversold": 30, "overbought": 70},
                    "description": "RSI Mean Reversion Strategy"
                },
                {
                    "name": "MACD_Crossover",
                    "class_name": "MACDStrategy",
                    "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
                    "description": "MACD Trend Following"
                },
                {
                    "name": "Bollinger_MeanReversion",
                    "class_name": "BollingerBandsStrategy",
                    "parameters": {"period": 20, "num_std": 2},
                    "description": "Bollinger Bands Mean Reversion"
                },
                {
                    "name": "Momentum_Breakout",
                    "class_name": "MomentumStrategy",
                    "parameters": {"lookback_period": 10, "threshold": 0.02},
                    "description": "Momentum Breakout Strategy"
                }
            ]
            
            for s in defaults:
                strat = StrategyConfig(**s)
                db.add(strat)
            db.commit()
            print("Strategies seeded successfully.")
        else:
            print("Strategies already exist.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_strategies()
