 # Module for live trading execution.
import os
import pyotp
from dotenv import load_dotenv
import robin_stocks.robinhood as r

def robinhood_login():
    load_dotenv()  # Load environment variables from .env file
    totp = pyotp.TOTP('NWPG3QHOSEVVNVKP').now()
    username = os.getenv('ACCOUNT_NAME')
    password = os.getenv('ACCOUNT_PASSWORD')
    
    # Perform login
    login_result = r.login(username, password, store_session=True, mfa_code=totp)
    
    return login_result

def place_buy_order(symbol, quantity):
    """
    Places a buy order for a given symbol and quantity.
    """
    # Ensure we are logged in
    robinhood_login()
    
    # Place buy order (market order as an example)
    order_result = r.order_buy_market(symbol, quantity)
    
    return order_result

def place_sell_order(symbol, quantity):
    """
    Places a sell order for a given symbol and quantity.
    """
    # Ensure we are logged in
    robinhood_login()
    
    # Place sell order (market order as an example)
    order_result = r.order_sell_market(symbol, quantity)
    
    return order_result


if __name__ == "__main__":
    result = robinhood_login()
    print(result)