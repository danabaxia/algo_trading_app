"""
Bollinger Bands Mean Reversion Strategy
Buys when price touches lower band, sells when price touches upper band
"""
from .base_strategy import BaseStrategy
from collections import deque
import math

class BollingerBandsStrategy(BaseStrategy):
    def __init__(self, name, period=20, num_std=2):
        super().__init__(name)
        self.period = period
        self.num_std = num_std
        self.price_history = deque(maxlen=period)
        self.position = None
    
    def initialize(self, context):
        """Initialize strategy"""
        pass
    
    def on_data(self, data):
        """Process new data"""
        price = data.get("price")
        if price:
            self.price_history.append(price)
        
    def calculate_bands(self):
        """Calculate Bollinger Bands"""
        if len(self.price_history) < self.period:
            return None, None, None
        
        prices = list(self.price_history)
        sma = sum(prices) / len(prices)
        
        # Calculate standard deviation
        variance = sum((p - sma) ** 2 for p in prices) / len(prices)
        std_dev = math.sqrt(variance)
        
        upper_band = sma + (self.num_std * std_dev)
        lower_band = sma - (self.num_std * std_dev)
        
        return upper_band, sma, lower_band
    
    def should_buy(self, data):
        upper, middle, lower = self.calculate_bands()
        
        if lower is None:
            return False
        
        price = data.get("price")
        if not price: return False

        # Buy when price touches or goes below lower band (oversold)
        if price <= lower and self.position is None:
            self.position = "LONG"
            return True
        return False
    
    def should_sell(self, data):
        upper, middle, lower = self.calculate_bands()
        
        if upper is None:
            return False
            
        price = data.get("price")
        if not price: return False
        
        # Sell when price touches or goes above upper band (overbought)
        if price >= upper and self.position == "LONG":
            self.position = None
            return True
        return False
