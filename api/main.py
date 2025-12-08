from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import sys
import os

# Ensure root directory is in path for imports
sys.path.append(os.getcwd())

from models.database import SessionLocal, get_db, init_db
from models.portfolio import AccountBalance, StrategyHolding
from models.trade_orders import Trade
from models.strategy_config import StrategyConfig
from models.session import TradingSession, SessionStatus
from execution.session_manager import SessionManager
from execution.backtest_engine import BacktestEngine
from strategies.moving_average import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.momentum_strategy import MomentumStrategy

app = FastAPI(title="Algo Trading Bot API")

@app.on_event("startup")
def startup_event():
    init_db()
    # Seed Strategies
    db = SessionLocal()
    try:
        if db.query(StrategyConfig).count() == 0:
            print("Seeding default strategies...")
            defaults = [
                {
                    "name": "GoldenCross_SMA",
                    "class_name": "MovingAverageCrossover",
                    "parameters": {"short_window": 10, "long_window": 30},
                    "description": "Simple Moving Average Crossover"
                },
                {
                    "name": "RSI_Oscillator",
                    "class_name": "RSIStrategy",
                    "parameters": {"period": 14, "oversold": 30, "overbought": 70},
                    "description": "RSI Mean Reversion Strategy"
                },
                {
                    "name": "MACD_Crossover",
                    "class_name": "MACDStrategy",
                    "parameters": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
                    "description": "MACD Trend Following"
                },
                {
                    "name": "Bollinger_MeanReversion",
                    "class_name": "BollingerBandsStrategy",
                    "parameters": {"period": 20, "num_std": 2},
                    "description": "Bollinger Bands Mean Reversion"
                },
                {
                    "name": "Momentum_Breakout",
                    "class_name": "MomentumStrategy",
                    "parameters": {"lookback_period": 10, "threshold": 0.02},
                    "description": "Momentum Breakout Strategy"
                }
            ]
            
            for s in defaults:
                strat = StrategyConfig(**s)
                db.add(strat)
            db.commit()
            print("Strategies seeded.")
    except Exception as e:
        print(f"Error seeding strategies: {e}")
    finally:
        db.close()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency ---
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Global Session Manager ---
session_manager = SessionManager()

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Algo Trading Bot API v2 (Sessions)"}

# --- Session Management ---

# --- Helper ---
def validate_stock_symbols(tickers: List[str]) -> List[str]:
    """Validates a list of tickers using MarketDataFetcher. Raises 400 if invalid."""
    if not tickers: return []
    
    clean_tickers = list(set([t.upper().strip() for t in tickers if t.strip()]))
    if not clean_tickers: return []
    
    from models.market_data import MarketDataFetcher
    fetcher = MarketDataFetcher()
    
    # Check existence via Price API (Batch)
    prices = fetcher.get_prices(clean_tickers)
    
    # Identify missing
    invalid = [t for t in clean_tickers if t not in prices]
    
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid or unsupported ticker symbol(s): {', '.join(invalid)}")
        
    return clean_tickers

@app.post("/sessions")
def create_session(
    name: str = Body(...),
    strategies: List[str] = Body(None),
    buy_strategy: str = Body(None),
    sell_strategy: str = Body(None),
    ticker_selection_method: str = Body("MANUAL"),
    tickers: List[str] = Body(None),  # Default None
    initial_balance: float = Body(10000.0),  # Default $10,000
    mode: str = Body("PAPER"),
    db: Session = Depends(get_db_session)
):
    # Validate Tickers
    valid_tickers = validate_stock_symbols(tickers)

    # Check for duplicate name
    existing = db.query(TradingSession).filter_by(name=name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Session name '{name}' already exists. Please choose a different name.")
    
    try:
        session = session_manager.create_session(
            name, 
            strategies or [], 
            valid_tickers, 
            initial_balance, 
            mode,
            buy_strategy=buy_strategy,
            sell_strategy=sell_strategy,
            ticker_method=ticker_selection_method
        )
        return {"id": session.id, "name": session.name, "status": session.status, "mode": session.mode, "initial_balance": session.initial_balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
def list_sessions(db: Session = Depends(get_db_session)):
    sessions = db.query(TradingSession).order_by(TradingSession.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "status": s.status,
            "mode": s.mode,
            "created_at": s.created_at,
            # Check if running in memory
            "is_running_memory": s.id in session_manager.get_active_sessions()
        }
        for s in sessions
    ]

@app.get("/sessions/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db_session)):
    session = db.query(TradingSession).get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.post("/sessions/{session_id}/start")
def start_session_endpoint(session_id: int):
    try:
        session_manager.start_session(session_id)
        return {"status": "started", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sessions/{session_id}/stop")
def stop_session_endpoint(session_id: int):
    try:
        session_manager.stop_session(session_id)
        return {"status": "stopped", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/sessions/{session_id}")
def delete_session_endpoint(session_id: int, db: Session = Depends(get_db_session)):
    try:
        # Stop the session if running
        session_manager.stop_session(session_id)
        
        # Delete from database
        session = db.query(TradingSession).get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete related data
        db.query(Trade).filter_by(session_id=session_id).delete()
        db.query(StrategyHolding).filter_by(session_id=session_id).delete()
        db.query(AccountBalance).filter_by(session_id=session_id).delete()
        
        # Delete session
        db.delete(session)
        db.commit()
        
        # Remove from memory
        session_manager.remove_session(session_id)
        
        return {"status": "deleted", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



# --- Data Endpoints (Session Scoped) ---

@app.get("/account")
def get_account(session_id: Optional[int] = None, mode: Optional[str] = None, db: Session = Depends(get_db_session)):
    # Prioritize session_id
    if session_id:
        account = db.query(AccountBalance).filter_by(session_id=session_id).first()
    elif mode:
         mode_str = "LIVE" if mode.lower() == "live" else "PAPER"
         # Look for legacy account without session_id first? Or just any with that mode?
         # For backward compatibility, check mode only
         account = db.query(AccountBalance).filter_by(mode=mode_str).first()
    else:
        # Default fallback
        account = db.query(AccountBalance).first()

    if not account:
        return {"cash_balance": 0.0, "total_equity": 0.0}
    return {
        "cash_balance": account.cash_balance,
        "total_equity": account.total_equity,
        "last_updated": account.last_updated
    }

@app.get("/holdings")
def get_holdings(session_id: Optional[int] = None, mode: Optional[str] = None, db: Session = Depends(get_db_session)):
    query = db.query(StrategyHolding)
    
    if session_id:
        query = query.filter_by(session_id=session_id)
    elif mode:
        mode_str = "LIVE" if mode.lower() == "live" else "PAPER"
        query = query.filter_by(mode=mode_str)
        
    holdings = {h.ticker: h for h in query.all()}
    
    # Get Watched Tickers
    watched = []
    if session_id:
        from models.session import SessionTicker
        watched = [t.symbol for t in db.query(SessionTicker).filter_by(session_id=session_id).all()]
    
    # Union identifiers
    all_tickers = list(set(holdings.keys()) | set(watched))
    
    from models.market_data import MarketDataFetcher
    fetcher = MarketDataFetcher()
    
    # Batch Fetch Prices to prevent threadpool starvation
    price_map = fetcher.get_prices(all_tickers)
    
    results = []
    
    for ticker in all_tickers:
        h = holdings.get(ticker)
        qty = h.quantity if h else 0
        avg = h.average_price if h else 0
        strategy_name = h.strategy_name if h else "Watchlist"
        
        # Get price from batch results
        current_price = price_map.get(ticker) or 0
        
        val = qty * current_price
        pnl = (current_price - avg) * qty if qty > 0 else 0
        
        results.append({
            "id": h.id if h else ticker,
            "strategy": strategy_name,
            "ticker": ticker,
            "quantity": qty,
            "avg_price": avg,
            "current_price": current_price,
            "current_val": val,
            "unrealized_pl": pnl
        })
        
    return sorted(results, key=lambda x: x['current_val'], reverse=True)

@app.get("/trades")
def get_trades(session_id: Optional[int] = None, mode: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db_session)):
    query = db.query(Trade)
    
    if session_id:
        query = query.filter_by(session_id=session_id)
    elif mode:
        mode_str = "LIVE" if mode.lower() == "live" else "PAPER"
        query = query.filter_by(mode=mode_str)
        
    trades = query.order_by(Trade.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": t.id,
            "ticker": t.ticker,
            "action": t.action,
            "quantity": t.quantity,
            "price": t.price,
            "status": t.status,
            "strategy": t.strategy_name,
            "timestamp": t.timestamp,
            "total_cost": t.total_cost
        }
        for t in trades
    ]

@app.get("/strategies")
def get_strategies(db: Session = Depends(get_db_session)):
    configs = db.query(StrategyConfig).all()
    results = []
    for c in configs:
        results.append({
            "name": c.name,
            "class_name": c.class_name,
            "active": c.is_active,
            "parameters": c.parameters
        })
    return results

# --- Backtesting ---

from strategies.factory import StrategyFactory

def create_strategy_instance(strategy_name: str):
    return StrategyFactory.create_strategy(strategy_name)

from models.session import SessionStrategy

@app.get("/sessions/{session_id}/strategies")
def get_session_strategies(session_id: int, db: Session = Depends(get_db_session)):
    session = db.query(TradingSession).get(session_id)
    if not session: raise HTTPException(404, "Session not found")
    
    # Auto-populate strategies for legacy sessions
    if not session.strategies:
        defaults = ["GoldenCross_SMA", "RSI_Oscillator", "MACD_Crossover", "Bollinger_Bands", "Momentum_Strategy"]
        for name in defaults:
            db.add(SessionStrategy(session_id=session.id, strategy_name=name, is_active=True))
        db.commit()
        db.refresh(session)
        
    return [
        {"id": s.id, "name": s.strategy_name, "is_active": s.is_active}
        for s in session.strategies
    ]

@app.post("/sessions/{session_id}/strategies/{strategy_name}/toggle")
def toggle_session_strategy(session_id: int, strategy_name: str, db: Session = Depends(get_db_session)):
    strat = db.query(SessionStrategy).filter_by(session_id=session_id, strategy_name=strategy_name).first()
    if not strat:
         raise HTTPException(404, "Strategy not found in session")
    
    strat.is_active = not strat.is_active
    db.commit()
    return {"status": "success", "is_active": strat.is_active}

@app.post("/sessions/{session_id}/backtest")
def run_backtest(
    session_id: int,
    start_date: str = Body(...),
    end_date: str = Body(...),
    strategies: List[str] = Body(None), # Optional
    tickers: List[str] = Body(None),
    initial_balance: float = Body(10000.0),
    db: Session = Depends(get_db_session)
):
    try:
        # Resolve Strategies from Session if not provided
        strat_instances = []
        
        # Resolve Strategies
        if not strategies:
            session = db.query(TradingSession).get(session_id)
            if session:
                # 1. Check for Composite
                if session.buy_strategy_name and session.sell_strategy_name:
                    from strategies.composite_strategy import CompositeStrategy
                    comp = CompositeStrategy("BacktestComposite", session.buy_strategy_name, session.sell_strategy_name)
                    strat_instances.append(comp)
                
                # 2. Check for Legacy Strategies (if no composite or mixed usage)
                elif session.strategies:
                    strategies = [s.strategy_name for s in session.strategies if s.is_active]
        
        # If we didn't create a composite, populate from 'strategies' list
        if not strat_instances and strategies:
             for s_name in strategies:
                # Skip "Composite:" markers if they exist in legacy list
                if "Composite:" in s_name: continue
                s = create_strategy_instance(s_name)
                if s:
                    strat_instances.append(s)
        
        # Fallback if still empty
        if not strat_instances and not strategies:
             # Try default
             s = create_strategy_instance("GoldenCross_SMA")
             if s: strat_instances.append(s)
             
        # Resolve Tickers
        if not tickers:
             from models.session import SessionTicker
             db_tickers = db.query(SessionTicker).filter_by(session_id=session_id).all()
             if db_tickers:
                 tickers = [t.symbol for t in db_tickers]

        if not tickers:
             tickers = ["AAPL", "GOOGL", "TSLA"]

        if not strat_instances:
            raise HTTPException(status_code=400, detail="No valid strategies provided or recognized")
        
        engine = BacktestEngine(strat_instances, tickers, start_date, end_date, initial_balance)
        results = engine.run()
        
        if "error" in results:
             raise HTTPException(status_code=400, detail=results["error"])
             
        return results
    except Exception as e:
        print(f"Backtest error: {e}") 
        raise HTTPException(status_code=500, detail=str(e))

# Legacy Control Endpoints (To prevent frontend breaking before update)
# Can redirect to a default session if needed
@app.post("/control/start")
def start_engine_legacy():
    return {"status": "error", "message": "Please use /sessions API"}

# --- Stock Search ---
import requests
from config.settings import settings

@app.get("/stocks/search")
def search_stocks(query: str):
    """Search for stocks using FMP API"""
    if not query or len(query) < 1:
        return []
    
    try:
        api_key = settings.FMP_API_KEY
        if not api_key:
            raise HTTPException(status_code=500, detail="FMP API key not configured")
        
        # FMP Search endpoint
        url = f"https://financialmodelingprep.com/api/v3/search?query={query}&limit=10&apikey={api_key}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        results = response.json()
        
        # Format results
        stocks = []
        for item in results:
            stocks.append({
                "symbol": item.get("symbol", ""),
                "name": item.get("name", ""),
                "exchange": item.get("exchangeShortName", ""),
                "type": item.get("type", "")
            })
        
        # Filter to only stocks (not ETFs, indices, etc.)
        stocks = [s for s in stocks if s["type"] in ["stock", ""] and s["exchange"] in ["NASDAQ", "NYSE", "AMEX", ""]]
        
        return stocks[:10]
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Ticker Management Endpoints ---
class TickerAddRequest(BaseModel):
    symbol: str

@app.get("/sessions/{session_id}/tickers")
def get_session_tickers(session_id: int, db: Session = Depends(get_db_session)):
    from models.session import SessionTicker
    tickers = db.query(SessionTicker).filter_by(session_id=session_id).all()
    return [t.symbol for t in tickers]

@app.post("/sessions/{session_id}/tickers")
def add_session_ticker(session_id: int, request: TickerAddRequest, db: Session = Depends(get_db_session)): 
    symbol = request.symbol.upper().strip()
    if not symbol: raise HTTPException(status_code=400, detail="Symbol required")
    
    # Validate using shared helper
    validate_stock_symbols([symbol])

    session_manager.add_session_ticker(session_id, symbol)
    return {"status": "added", "symbol": symbol}

@app.delete("/sessions/{session_id}/tickers/{symbol}")
def remove_session_ticker(session_id: int, symbol: str, db: Session = Depends(get_db_session)):
    session_manager.remove_session_ticker(session_id, symbol)
    return {"status": "removed", "symbol": symbol}




@app.get("/strategies")
def get_strategies(db: Session = Depends(get_db_session)):
    from models.strategy_config import StrategyConfig
    strategies = db.query(StrategyConfig).all()
    results = []
    for s in strategies:
        results.append({
            "name": s.name,
            "description": s.description,
            "parameters": s.parameters
        })
    return results
