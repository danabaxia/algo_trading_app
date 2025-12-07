import robin_stocks.robinhood as rh
import os
import pyotp
from dotenv import load_dotenv
from .base_broker import Broker

class RobinhoodBroker(Broker):
    def __init__(self):
        load_dotenv()
        self.username = os.getenv("RH_USERNAME")
        self.password = os.getenv("RH_PASSWORD")
        self.totp = os.getenv("RH_TOTP") # Time-based One Time Password string
        self.is_logged_in = False
        
    def login(self):
        if not self.username or not self.password:
            raise ValueError("RH_USERNAME or RH_PASSWORD not set in .env")
        
        # If using TOTP (2FA), robin_stocks can generate the code automatically
        if self.totp:
            totp_code = pyotp.TOTP(self.totp).now()
            rh.login(self.username, self.password, mfa_code=totp_code)
        else:
            # Interactive or SMS login might trigger here if not handled
            rh.login(self.username, self.password)
            
        self.is_logged_in = True
        print("Logged into Robinhood!")

    def get_cash_balance(self) -> float:
        if not self.is_logged_in: self.login()
        profile = rh.profiles.load_account_profile()
        return float(profile.get('buying_power', 0.0))

    def get_holdings(self, ticker: str) -> float:
        if not self.is_logged_in: self.login()
        # Returns a dictionary or list
        positions = rh.account.build_holdings()
        # positions key is ticker symbol?
        if ticker in positions:
            return float(positions[ticker]['quantity'])
        return 0.0

    def place_order(self, ticker: str, quantity: float, side: str, order_type: str = "market", price: float = None):
        if not self.is_logged_in: self.login()
        
        # robin_stocks requires integer quantity for stocks usually, unless fractional
        # We'll assume integer for now
        quantity = int(quantity)
        
        print(f"[Robinhood] Placing {side.upper()} order for {quantity} {ticker}...")
        
        order = None
        if side.lower() == 'buy':
            if order_type == 'market':
                order = rh.orders.order_buy_market(ticker, quantity)
            elif order_type == 'limit':
                order = rh.orders.order_buy_limit(ticker, quantity, price)
        elif side.lower() == 'sell':
            if order_type == 'market':
                order = rh.orders.order_sell_market(ticker, quantity)
            elif order_type == 'limit':
                order = rh.orders.order_sell_limit(ticker, quantity, price)
                
        return order
