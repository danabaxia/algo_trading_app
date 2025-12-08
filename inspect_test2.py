from models.database import SessionLocal
from models.session import TradingSession

def inspect_test2():
    db = SessionLocal()
    try:
        session = db.query(TradingSession).filter(TradingSession.name == "test2").first()
        if not session:
            print("Session 'test2' not found.")
            return

        print(f"Session: {session.name} (ID: {session.id})")
        print(f"Status: {session.status}")
        print(f"Calculated Strategy: Buy={session.buy_strategy_name}, Sell={session.sell_strategy_name}")
        print(f"Ticker Method: {session.ticker_selection_method}")
        
        tickers = [t.symbol for t in session.tickers]
        print(f"Tickers: {tickers}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_test2()
