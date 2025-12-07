import sys
import os
from datetime import datetime
import pandas as pd

# Add project root to path
sys.path.append(os.getcwd())

from models.database import SessionLocal
from models.ohlcv import OHLCV
from models.market_data import MarketDataFetcher

def load_data(tickers, days=365):
    db = SessionLocal()
    fetcher = MarketDataFetcher()
    
    total_added = 0
    
    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        try:
            df = fetcher.get_daily_history(ticker, days=days)
            
            if df.empty:
                print(f"No data found for {ticker}")
                continue
                
            entries = []
            # existing_dates = {d[0] for d in db.query(OHLCV.timestamp).filter_by(ticker=ticker).all()}
            
            print(f"Processing {len(df)} rows for {ticker}...")
            
            for index, row in df.iterrows():
                # FMP dates are YYYY-MM-DD
                dt_str = row['date']
                dt = datetime.strptime(dt_str, "%Y-%m-%d")
                
                # Create OHLCV object
                # We use merge or ignore duplicates logic. 
                # For simplicity in this script, we'll try to add. 
                # If UniqueConstraint violation could occur, we should handle it.
                # But typically 'merge' is slower. 
                # Let's check existence first or just rely on 'ignore' if we had bulk methods.
                
                # Check if exists (Naive check for now, can optimize later with bulk upsert)
                exists = db.query(OHLCV).filter_by(ticker=ticker, timestamp=dt, interval="1d").first()
                if exists:
                    # Update?
                    exists.close = row['close']
                    exists.volume = row['volume']
                    continue
                
                candle = OHLCV(
                    ticker=ticker,
                    timestamp=dt,
                    interval="1d",
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume']
                )
                db.add(candle)
                total_added += 1
                
            db.commit()
            print(f"Committed data for {ticker}")
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            db.rollback()
            
    db.close()
    print(f"Job complete. Total new candles added: {total_added}")

if __name__ == "__main__":
    # You can expand this list
    TICKERS = ["AAPL", "GOOGL", "TSLA", "MSFT", "AMZN"]
    load_data(TICKERS, days=365)
