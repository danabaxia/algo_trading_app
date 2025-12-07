import os
import sys

sys.path.append(os.getcwd())

from models.database import engine, Base
# Import models
from models.trade_orders import Trade
from models.portfolio import AccountBalance, StrategyHolding

def reset():
    print("Dropping all tables to allow clean Initial Migration generation...")
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")

if __name__ == "__main__":
    reset()
