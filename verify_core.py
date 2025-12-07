import sys
import os

# Ensure the project root is in the path
sys.path.append(os.getcwd())

from models.database import init_db, get_db
from models.trade_orders import Trade
from models.portfolio import AccountBalance, StrategyHolding
from strategies.base_strategy import BaseStrategy

# 1. Test Database Setup
print("Initializing database...")
init_db()
print("Database initialized.")

# 2. Test Trade Persistence & Portfolio Schema
print("Testing persistence...")
db = next(get_db())
try:
    # 2a. Test Account
    account = db.query(AccountBalance).first()
    if not account:
        print("Creating initial account...")
        account = AccountBalance(cash_balance=10000.0, total_equity=10000.0)
        db.add(account)
        db.commit()
    print(f"Current Account: {account}")

    # 2b. Test Trade
    new_trade = Trade(
        ticker="AAPL", 
        action="BUY", 
        quantity=10, 
        price=150.0, 
        total_cost=1500.0,
        strategy_name="TestStrategy"
    )
    db.add(new_trade)
    db.commit()
    print(f"Added trade: {new_trade}")

    # 2c. Test Holding Update (Mocking logic usually done in engine)
    holding = db.query(StrategyHolding).filter_by(strategy_name="TestStrategy", ticker="AAPL").first()
    if not holding:
        holding = StrategyHolding(strategy_name="TestStrategy", ticker="AAPL", quantity=0, average_price=0)
        db.add(holding)
    
    # Update holding
    holding.quantity += 10
    holding.average_price = 150.0 # Simple avg for test
    db.commit()
    
    print(f"Updated Holding: {holding}")

    # Read back trade
    trade = db.query(Trade).filter_by(strategy_name="TestStrategy").first()
    if trade:
        print(f"Retrieved trade: {trade}")
    else:
        print("Failed to retrieve trade.")
finally:
    db.close()



# 3. Test Strategy Interface
print("Testing Strategy Interface...")
class TestStrategy(BaseStrategy):
    def initialize(self, context):
        pass
    def on_data(self, data):
        pass
    def should_buy(self, data) -> bool:
        return True
    def should_sell(self, data) -> bool:
        return False

ts = TestStrategy("MyTestStrategy")
print(f"Successfully instantiated {ts.name}")
print("Verification complete.")
