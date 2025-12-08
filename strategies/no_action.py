from .base_strategy import BaseStrategy

class NoActionStrategy(BaseStrategy):
    """
    A neutral strategy that never signals a Buy or Sell.
    Useful for testing or for manual-only intervention (if supported).
    """
    def __init__(self, name):
        super().__init__(name)
        
    def initialize(self, context):
        pass

    def on_data(self, data):
        pass

    def should_buy(self, data) -> bool:
        return False

    def should_sell(self, data) -> bool:
        return False
