from .base_strategy import BaseStrategy
import pandas as pd

class MovingAverageCrossover(BaseStrategy):
    def __init__(self, name, short_window=50, long_window=200):
        super().__init__(name)
        self.short_window = short_window
        self.long_window = long_window
        self.history = []
        self.position = 0 # 0 = flat, 1 = long
        
    def initialize(self, context):
        print(f"Initialized {self.name} (SMA {self.short_window}/{self.long_window})")

    def on_data(self, data):
        # We need historical context to calculate SMA. 
        # In a real live engine, the engine passes current data.
        # This strategy assumes 'data' contains enough history or we build it up.
        # For this simple implementation, we'll assume 'data' is a row with a pre-calculated SMA 
        # OR we maintain a history list.
        
        # Let's maintain history for simplicity in this demo.
        price = data.get('price')
        if price is None:
            return
            
        self.history.append(price)
        
        # Optimize: keep only necessary history
        if len(self.history) > self.long_window + 1:
            self.history.pop(0)

    def should_buy(self, data) -> bool:
        if len(self.history) < self.long_window:
            return False
            
        # Calculate SMAs
        short_sma = sum(self.history[-self.short_window:]) / self.short_window
        long_sma = sum(self.history[-self.long_window:]) / self.long_window
        
        # Crossover Logic: Buy if Short > Long and we are not already long
        if short_sma > long_sma and self.position == 0:
            self.position = 1
            return True
        return False

    def should_sell(self, data) -> bool:
        if len(self.history) < self.long_window:
            return False
            
        short_sma = sum(self.history[-self.short_window:]) / self.short_window
        long_sma = sum(self.history[-self.long_window:]) / self.long_window
        
        # Crossover Logic: Sell if Short < Long and we are long
        if short_sma < long_sma and self.position == 1:
            self.position = 0
            return True
        return False
