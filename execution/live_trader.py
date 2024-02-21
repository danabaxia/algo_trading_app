 # Module for live trading execution.
import os
import sys
import time
import pyotp
from dotenv import load_dotenv
import robin_stocks.robinhood as r
import pandas as pd

def robinhood_login():
    try:
        load_dotenv()  # Ensures it's loaded only once by checking if called earlier
        totp = pyotp.TOTP(os.getenv('ROBINHOOD_TOTP_SECRET')).now()
        login_result = r.login(os.getenv('ROBINHOOD_USERNAME'),
                               os.getenv('ROBINHOOD_PASSWORD'),
                               store_session=True, mfa_code=totp)
        if "access_token" in login_result:
            print("Logged in to Robinhood.")
        else:
            print("Failed to login to Robinhood. Check credentials and TOTP.")
    except Exception as e:
        print(f"An error occurred during Robinhood login: {e}")
        sys.exit(1)

def get_my_stock_holdings():
    try:
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)
        my_stock_info = r.build_holdings()
        p = pd.DataFrame.from_dict(my_stock_info, orient='index')
        return p
    except Exception as e:
        print(f"Error fetching holdings: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

def get_total_equity(holdings):
    return holdings['equity'].astype(float).sum()

def get_cash_portfolio():
    try:
        data = r.profiles.load_account_profile()
        return float(data['portfolio_cash'])
    except Exception as e:
        print(f"Error fetching cash portfolio: {e}")
        return 0
    
"""#Stock transaction functions 
def checkCap(tker, cap):   
    total_equity = get_cash_portfolio()
    invest = t.getTotalInvest()
    if tker in t.getMyStockList():
        equity = t.getEquity(tker)
        print('total equity',total_equity, 'tker',tker, 'cap', cap,'invest', invest, 'equity',equity)
        if total_equity/invest < 0.8 and equity < cap:
            print('qualified to buy')
            return True
        else: 
            print('unqaulified to buy')
            return False
    else :
        if total_equity/invest < 0.8:
            print('qualified to buy')
            return True
        else:
            print('no more funds to invest')
            return False"""


"""def logRecord(tker,action,amount):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open('log/log.csv', 'a') as csvfile:
        fieldnames = ['time', 'tiker','action','amount']
        writer = csv.writer(csvfile)
        writer.writerow([now,tker, action, amount])"""


def buy_stock(ticker, value, extend_hours=True):
    """
    Buys a stock with options for during market hours, after-market hours, or 24/7.

    Parameters:
    - ticker: The stock symbol to buy.
    - value: The dollar amount of the stock to buy.
    - trading_window: "market_hours", "after_market_hours", or "24_7" trading.
    """
    max_attempts = 10
    attempt = 0
    order_id = None

    while attempt < max_attempts:
        if not order_id:  # If no order has been placed yet or needs to retry
            try:
                result = r.orders.order_buy_fractional_by_price(ticker, value, timeInForce='gfd', extendedHours=extend_hours)
                order_id = result.get('id')
                print(f"Order placed for {ticker}. Order ID: {order_id}")
            except Exception as e:
                print(f"Error placing order for {ticker}: {e}")
                return None

        # Check order status
        try:
            order_info = r.orders.get_stock_order_info(order_id)
            order_state = order_info.get('state')
            print(f"Order {order_id} state: {order_state}")

            if order_state == 'filled':
                print('Buy order is complete.')
                log_record(ticker, 'buy', value)
                return ticker
            elif order_state == 'cancelled':
                print('Order has been cancelled.')
                return None
        except Exception as e:
            print(f"Error fetching order {order_id} info: {e}")

        time.sleep(15)
        attempt += 1
        print(f'Attempt {attempt}/{max_attempts}')

    #may need this code later 
    """if attempt == max_attempts:
        try:
            cancel_result = r.orders.cancel_stock_order(order_id)
            if cancel_result:
                print(f"Order {order_id} cancelled after exceeding max attempts.")
            else:
                print(f"Failed to cancel order {order_id}.")
        except Exception as e:
            print(f"Error cancelling order {order_id}: {e}")"""
    print('Sell order did not complete within max attempts.')
    #here needs log function to record incomplete order 
    return None

def sell_stock(ticker, value):
    max_attempts = 10
    attempt = 0
    order_id = None

    while attempt < max_attempts:
        if not order_id:  # If no order has been placed yet or needs to retry
            try:
                result = r.orders.order_sell_fractional_by_price(ticker, value, timeInForce='gfd', extendedHours=False)
                order_id = result.get('id')
                print(f"Order placed to sell {ticker}. Order ID: {order_id}")
            except Exception as e:
                print(f"Error placing sell order for {ticker}: {e}")
                break  # Exit if order placement fails

        # Check the status of the order
        try:
            order_info = r.orders.get_stock_order_info(order_id)
            order_state = order_info.get('state')
            print(f"Order {order_id} state: {order_state}")

            if order_state == 'filled':
                print('Sell order is complete.')
                log_record(ticker, 'sell', value)
                return ticker
            elif order_state == 'cancelled':
                print('Order has been cancelled, attempting to sell again...')
                order_id = None  # Reset order_id to attempt a new sell
            else:
                print('Checking state later...')
        except Exception as e:
            print(f"Error fetching order {order_id} info: {e}")

        time.sleep(15)  # Pause before the next attempt or check
        attempt += 1
        print(f'Attempt {attempt}/{max_attempts}')

    print('Sell order did not complete within max attempts.')
    #here needs log function to record incomplete order 
    return None

def log_record(ticker, action, value):
    # Implement logging logic here, such as appending to a file or logging to a database
    pass

def main():
    robinhood_login()
    my_holdings = get_my_stock_holdings()
    if not my_holdings.empty:
        print(f"My Total Equity: {get_total_equity(my_holdings)}")
        print(f"Cash Portfolio: {get_cash_portfolio()}")
    else:
        print("No holdings found or unable to fetch.")
    
    buy_stock('GOOGL', 10)

if __name__ == "__main__":
    main()

