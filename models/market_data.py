import requests
import pandas as pd
from datetime import datetime
from config.settings import settings

class MarketDataFetcher:
    BASE_URL = 'https://financialmodelingprep.com/api/v3'
    
    def __init__(self):
        self.api_key = settings.FMP_API_KEY
        if not self.api_key:
            print("Warning: FMP_API_KEY is not set. Market Data will fail.")
        self.session = requests.Session()

    def _request_api(self, endpoint, **params):
        """Private method to request data from the API."""
        if not self.api_key:
            raise ValueError("API Key missing")
            
        params['apikey'] = self.api_key
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e} | Response: {response.text}")
            return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def get_price(self, ticker):
        """
        Fetch the current real-time price for a ticker.
        Endpoint: /quote-short/{ticker} or /quote/{ticker}
        """
        data = self._request_api(f"quote-short/{ticker}")
        if data and isinstance(data, list) and len(data) > 0:
            return data[0].get('price')
        return None

    def get_prices(self, tickers):
        """
        Fetch real-time prices for multiple tickers in one request.
        Returns dict: {'AAPL': 150.0, ...}
        """
        if not tickers: return {}
        # FMP supports comma separated tickers
        ticker_str = ",".join(tickers)
        data = self._request_api(f"quote-short/{ticker_str}")
        if data and isinstance(data, list):
            return {item.get('symbol'): item.get('price') for item in data}
        return {}

    def get_historical_candles(self, ticker, interval="1min", limit=100):
        """
        Fetch historical OHLCV candles (intraday).
        Endpoint: /historical-chart/{interval}/{ticker}
        """
        endpoint = f"historical-chart/{interval}/{ticker}"
        data = self._request_api(endpoint)
        if data and isinstance(data, list):
            df = pd.DataFrame(data)
            return df
        return pd.DataFrame()

    def get_daily_history(self, ticker, days=365):
        """
        Fetch daily historical prices for long durations.
        Endpoint: /historical-price-full/{ticker}?timeseries={days}
        """
        endpoint = f"historical-price-full/{ticker}"
        data = self._request_api(endpoint, timeseries=days)
        
        # FMP returns: {"symbol": "AAPL", "historical": [...]}
        if data and "historical" in data:
            df = pd.DataFrame(data["historical"])
            return df
        return pd.DataFrame()

    def get_technical_indicator(self, ticker, indicator_type="rsi", period=14, interval="daily"):
        """
        Fetch pre-calculated indicators from FMP.
        indicator_type: 'sma', 'ema', 'rsi', 'adx', 'standardDeviation'
        interval: 'daily', '1min', '5min', '15min'
        """
        # Construction: /technical_indicator/{interval}/{ticker}
        endpoint = f"technical_indicator/{interval}/{ticker}"
        params = {"type": indicator_type, "period": period}
        
        data = self._request_api(endpoint, **params)
        if data and isinstance(data, list):
            df = pd.DataFrame(data)
            return df
        return pd.DataFrame()

    def get_company_profile(self, ticker):
        """Fetch company profile data."""
        return self._request_api(f"profile/{ticker}")

def main():
    fetcher = MarketDataFetcher()
    ticker = "AAPL"
    
    # 1. Price
    print(f"Fetching price for {ticker}...")
    print(f"Current: {fetcher.get_price(ticker)}")
    
    # 2. Daily History (Last 5 days)
    print(f"\nFetching last 5 days daily history...")
    daily = fetcher.get_daily_history(ticker, days=5)
    if not daily.empty:
        print(daily[['date', 'close', 'volume']].head())
    
    # 3. RSI Indicator
    print(f"\nFetching Daily RSI(14)...")
    rsi = fetcher.get_technical_indicator(ticker, indicator_type='rsi', period=14)
    if not rsi.empty:
        print(rsi[['date', 'rsi']].head())

if __name__ == "__main__":
    main()
