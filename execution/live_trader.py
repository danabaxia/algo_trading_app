 # Module for live trading execution.
import os
import sys
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

def main():
    robinhood_login()
    my_holdings = get_my_stock_holdings()
    if not my_holdings.empty:
        print(f"My Total Equity: {get_total_equity(my_holdings)}")
        print(f"Cash Portfolio: {get_cash_portfolio()}")
    else:
        print("No holdings found or unable to fetch.")

if __name__ == "__main__":
    main()

