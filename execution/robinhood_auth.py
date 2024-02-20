import os
from dotenv import load_dotenv
import robin_stocks as r

def robinhood_login():
    load_dotenv()  # Load environment variables from .env file
    
    username = os.getenv('ACCOUNT_NAME')
    password = os.getenv('ACCOUNT_PASSWORD')
    
    # Perform login
    login_result = r.login(username, password)
    
    return login_result

