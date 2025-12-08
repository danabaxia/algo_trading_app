"""
MACD (Moving Average Convergence Divergence) Strategy
Buys on bullish crossover, sells on bearish crossover
"""
from .base_strategy import BaseStrategy
from collections import deque

class MACDStrategy(BaseStrategy):
    def __init__(self, name, fast_period=12, slow_period=26, signal_period=9):
        super().__init__(name)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.price_history = deque(maxlen=slow_period + signal_period)
        self.macd_history = deque(maxlen=signal_period)
        self.position = None
        self.prev_macd = None
        self.prev_signal = None
        self.latest_macd = None
        self.latest_signal = None
    
    def initialize(self, context):
        """Initialize strategy"""
        pass
    
    def on_data(self, data):
        """Process new data"""
        price = data.get("price")
        if price:
            self.price_history.append(price)
            self.latest_macd, self.latest_signal = self.calculate_macd()
        
    def calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = sum(list(prices)[:period]) / period
        
        for price in list(prices)[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def calculate_macd(self):
        """Calculate MACD and Signal line"""
        if len(self.price_history) < self.slow_period:
            return None, None
        
        fast_ema = self.calculate_ema(self.price_history, self.fast_period)
        slow_ema = self.calculate_ema(self.price_history, self.slow_period)
        
        if fast_ema is None or slow_ema is None:
            return None, None
        
        macd = fast_ema - slow_ema
        self.macd_history.append(macd)
        
        if len(self.macd_history) < self.signal_period:
            return macd, None
        
        signal = self.calculate_ema(self.macd_history, self.signal_period)
        return macd, signal
    
    def should_buy(self, data):
        macd, signal = self.latest_macd, self.latest_signal
        
        if macd is None or signal is None:
            return False
        
        # Bullish crossover: MACD crosses above signal line
        if (self.prev_macd is not None and self.prev_signal is not None and
            self.prev_macd <= self.prev_signal and macd > signal and
            self.position is None):
            self.prev_macd = macd
            self.prev_signal = signal
            self.position = "LONG"
            return True
        
        self.prev_macd = macd
        self.prev_signal = signal
        return False
    
    def should_sell(self, data):
        macd, signal = self.latest_macd, self.latest_signal
        
        if macd is None or signal is None:
            return False
        
        # Bearish crossover: MACD crosses below signal line
        if (self.prev_macd is not None and self.prev_signal is not None and
            self.prev_macd >= self.prev_signal and macd < signal and
            self.position == "LONG"):
            self.prev_macd = macd
            self.prev_signal = signal
            self.position = None
            return True
        
        self.prev_macd = macd
        self.prev_signal = signal
        return False
