import requests
import pandas as pd
from dotenv import load_dotenv
import os

class FinancialDataFetcher:
    BASE_URL = 'https://financialmodelingprep.com/api/v3'
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        # Retrieve the API key
        self.api_key = os.getenv('FMP_KEY')
        if not self.api_key:
            raise ValueError("No API key found in .env file")
        self.session = requests.Session()

    def _request_api(self, endpoint, **params):
        """Private method to request data from the API."""
        params['apikey'] = self.api_key  # Add the API key to the parameters
        try:
            response = self.session.get(f"{self.BASE_URL}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_financial_statement(self, ticker, statement_type, period='quarter'):
        """Fetch financial statement data."""
        return self._request_api(f"{statement_type}-statement/{ticker}", period=period)

    def get_company_profile(self, ticker):
        """Fetch company profile data."""
        return self._request_api(f"profile/{ticker}")

    # Define other methods as needed, using the _request_api method to fetch data

def main():
    financial_data = FinancialDataFetcher()

    revenue_data = financial_data.get_financial_statement('AAPL', 'income', period='annual')
    print(revenue_data)

    profile_data = financial_data.get_company_profile('AAPL')
    print(profile_data)

if __name__ == "__main__":
    main()
