from execution.engine import TradingEngine
from strategies.base_strategy import BaseStrategy

# Temporary Simple Strategy until we implement a real one
class SimpleTestStrategy(BaseStrategy):
    def initialize(self, context): pass
    def on_data(self, data): pass
    def should_buy(self, data): return False # Safety first
    def should_sell(self, data): return False

def main():
    print("Initializing 24/7 Trading Bot...")
    
    # 1. Setup Strategies
    strategies = [SimpleTestStrategy("SimpleTest")]
    
    # 2. Setup Watchlist
    tickers = ["AAPL", "GOOGL", "TSLA"]
    
    # 3. Initialize Engine
    engine = TradingEngine(strategies, tickers, interval=5) # 5 seconds for testing
    
    # 4. Run
    engine.run()

if __name__ == "__main__":
    main()