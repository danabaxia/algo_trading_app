from models.database import SessionLocal
from models.session import TradingSession
from models.trade_orders import Trade
from models.strategy_config import StrategyConfig
from sqlalchemy.orm import joinedload

def inspect_session(session_name="test1"):
    db = SessionLocal()
    try:
        # 1. Find Session
        session = db.query(TradingSession).filter(TradingSession.name == session_name).first()
        if not session:
            print(f"Session '{session_name}' not found.")
            return

        print(f"Session ID: {session.id}")
        print(f"Config: Buy={session.buy_strategy_name}, Sell={session.sell_strategy_name}, TickerMethod={session.ticker_selection_method}")
        
        # 2. List Tickers associated with session
        tickers = [t.symbol for t in session.tickers]
        print(f"Session Tickers: {tickers}")

        # 3. List Trades
        trades = db.query(Trade).filter(Trade.session_id == session.id).all()
        print(f"Total Trades: {len(trades)}")
        for t in trades:
            print(f" - {t.timestamp} | {t.action} | {t.symbol} | Price: {t.price} | Strat: {t.strategy_name}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_session()
