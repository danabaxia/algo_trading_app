"""
RSI (Relative Strength Index) Strategy
Buys when RSI < 30 (oversold), sells when RSI > 70 (overbought)
"""
from .base_strategy import BaseStrategy
from collections import deque

class RSIStrategy(BaseStrategy):
    def __init__(self, name, period=14, oversold=30, overbought=70):
        super().__init__(name)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.price_history = deque(maxlen=period + 1)
        self.position = None  # Track if we have a position
    
    def initialize(self, context):
        """Initialize strategy"""
        pass
    
    def on_data(self, data):
        """Process new data"""
        price = data.get("price")
        if price:
            self.price_history.append(price)
        
    def calculate_rsi(self):
        """Calculate RSI from price history"""
        if len(self.price_history) < self.period + 1:
            return 50  # Neutral RSI if not enough data
        
        gains = []
        losses = []
        
        # Use history
        history_list = list(self.price_history)
        
        for i in range(1, len(history_list)):
            change = history_list[i] - history_list[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains) / self.period
        avg_loss = sum(losses) / self.period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def should_buy(self, data):
        if len(self.price_history) < self.period + 1:
            return False
            
        rsi = self.calculate_rsi()
        
        # Buy when oversold and we don't have a position
        if rsi < self.oversold and self.position is None:
            self.position = "LONG"
            return True
        return False
    
    def should_sell(self, data):
        if len(self.price_history) < self.period + 1:
            return False
        
        rsi = self.calculate_rsi()
        
        # Sell when overbought and we have a position
        if rsi > self.overbought and self.position == "LONG":
            self.position = None
            return True
        return False
