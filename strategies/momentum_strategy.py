"""
Momentum Strategy
Buys when price momentum is positive, sells when negative
"""
from .base_strategy import BaseStrategy
from collections import deque

class MomentumStrategy(BaseStrategy):
    def __init__(self, name, lookback_period=10, threshold=0.02):
        super().__init__(name)
        self.lookback_period = lookback_period
        self.threshold = threshold  # 2% momentum threshold
        self.price_history = deque(maxlen=lookback_period + 1)
        self.position = None
    
    def initialize(self, context):
        """Initialize strategy"""
        pass
    
    def on_data(self, data):
        """Process new data"""
        pass
        
    def calculate_momentum(self):
        """Calculate price momentum as percentage change"""
        if len(self.price_history) < self.lookback_period + 1:
            return 0
        
        current_price = self.price_history[-1]
        past_price = self.price_history[0]
        
        if past_price == 0:
            return 0
        
        momentum = (current_price - past_price) / past_price
        return momentum
    
    def should_buy(self, data):
        price = data.get("price")
        if not price:
            return False
            
        self.price_history.append(price)
        
        if len(self.price_history) < self.lookback_period + 1:
            return False
        
        momentum = self.calculate_momentum()
        
        # Buy when positive momentum exceeds threshold
        if momentum > self.threshold and self.position is None:
            self.position = "LONG"
            return True
        return False
    
    def should_sell(self, data):
        price = data.get("price")
        if not price:
            return False
        
        if price not in self.price_history:
            self.price_history.append(price)
        
        if len(self.price_history) < self.lookback_period + 1:
            return False
        
        momentum = self.calculate_momentum()
        
        # Sell when momentum turns negative or drops below threshold
        if momentum < -self.threshold and self.position == "LONG":
            self.position = None
            return True
        return False
