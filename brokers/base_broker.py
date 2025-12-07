from abc import ABC, abstractmethod

class Broker(ABC):
    @abstractmethod
    def get_cash_balance(self) -> float:
        pass

    @abstractmethod
    def get_holdings(self, ticker: str) -> float:
        pass

    @abstractmethod
    def place_order(self, ticker: str, quantity: float, side: str, order_type: str = "market", price: float = None):
        """
        :param side: 'buy' or 'sell'
        """
        pass
