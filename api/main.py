from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Ensure root directory is in path for imports
sys.path.append(os.getcwd())

from models.database import SessionLocal, get_db
from models.portfolio import AccountBalance, StrategyHolding
from models.trade_orders import Trade
from models.strategy_config import StrategyConfig
from models.session import TradingSession, SessionStatus
from execution.session_manager import SessionManager

app = FastAPI(title="Algo Trading Bot API")

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

@app.post("/sessions")
def create_session(
    name: str = Body(...),
    strategies: List[str] = Body(...),
    mode: str = Body("PAPER"),
    db: Session = Depends(get_db_session)
):
    # Check for duplicate name
    existing = db.query(TradingSession).filter_by(name=name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Session name '{name}' already exists. Please choose a different name.")
    
    try:
        session = session_manager.create_session(name, strategies, mode)
        return {"id": session.id, "name": session.name, "status": session.status, "mode": session.mode}
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
    query = db.query(StrategyHolding).filter(StrategyHolding.quantity != 0)
    
    if session_id:
        query = query.filter_by(session_id=session_id)
    elif mode:
        mode_str = "LIVE" if mode.lower() == "live" else "PAPER"
        query = query.filter_by(mode=mode_str)
        
    holdings = query.all()
    return [
        {
            "id": h.id,
            "strategy": h.strategy_name,
            "ticker": h.ticker,
            "quantity": h.quantity,
            "avg_price": h.average_price,
            "current_val": h.quantity * h.average_price
        }
        for h in holdings
    ]

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

# Legacy Control Endpoints (To prevent frontend breaking before update)
# Can redirect to a default session if needed
@app.post("/control/start")
def start_engine_legacy():
    return {"status": "error", "message": "Please use /sessions API"}

