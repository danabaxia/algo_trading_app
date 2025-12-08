from .base_strategy import BaseStrategy

class CompositeStrategy(BaseStrategy):
    """
    A strategy that acts as a wrapper, delegating 'should_buy' to one strategy
    and 'should_sell' to another.
    """
    def __init__(self, name, buy_strategy_name, sell_strategy_name):
        super().__init__(name)
        self.buy_strategy_name = buy_strategy_name
        self.sell_strategy_name = sell_strategy_name
        self.buy_strategy = None
        self.sell_strategy = None
        
    def initialize(self, context):
        from .factory import StrategyFactory
        # Instantiate the components
        self.buy_strategy = StrategyFactory.create_strategy(self.buy_strategy_name)
        self.sell_strategy = StrategyFactory.create_strategy(self.sell_strategy_name)
        
        if self.buy_strategy:
            self.buy_strategy.initialize(context)
        if self.sell_strategy:
            self.sell_strategy.initialize(context)
            
        print(f"Initialized Composite Strategy: Buy={self.buy_strategy_name}, Sell={self.sell_strategy_name}")

    def on_data(self, data):
        # Forward data to both
        if self.buy_strategy:
            self.buy_strategy.on_data(data)
        # Avoid double processing if they are the same instance (unlikely with Factory creating new ones)
        if self.sell_strategy and self.sell_strategy_name != self.buy_strategy_name:
            self.sell_strategy.on_data(data)
        elif self.sell_strategy:
            # If same name, they are distinct instances in current factory logic, so we update both
            self.sell_strategy.on_data(data)

    def should_buy(self, data) -> bool:
        if self.buy_strategy:
            return self.buy_strategy.should_buy(data)
        return False

    def should_sell(self, data) -> bool:
        if self.sell_strategy:
            return self.sell_strategy.should_sell(data)
        return False
