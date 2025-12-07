from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    Ensures that all strategies implement the necessary methods for the execution engine.
    """

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def initialize(self, context):
        """
        Initialize the strategy with any necessary context or data.
        """
        pass

    @abstractmethod
    def on_data(self, data):
        """
        Main logic called when new data is received (e.g., every minute or tick).
        :param data: Dictionary or object containing market data (price, volume, etc.)
        """
        pass

    @abstractmethod
    def should_buy(self, data) -> bool:
        """
        Determine if a buy order should be placed.
        :return: True if buy condition is met, False otherwise.
        """
        pass

    @abstractmethod
    def should_sell(self, data) -> bool:
        """
        Determine if a sell order should be placed.
        :return: True if sell condition is met, False otherwise.
        """
        pass
