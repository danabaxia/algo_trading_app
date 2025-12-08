import threading
import logging
from typing import Dict, List, Optional
from models.database import SessionLocal
from models.session import TradingSession, SessionStatus
from models.strategy_config import StrategyConfig
from execution.engine import TradingEngine
from strategies.moving_average import MovingAverageCrossover
from brokers.robinhood_broker import RobinhoodBroker

logger = logging.getLogger("SessionManager")

class SessionManager:
    def __init__(self):
        self._engines: Dict[int, TradingEngine] = {}
        self._threads: Dict[int, threading.Thread] = {}
        self._lock = threading.Lock()

    def create_session(self, name: str, strategy_names: List[str], tickers: List[str], initial_balance: float = 10000.0, mode: str = "PAPER", buy_strategy: str = None, sell_strategy: str = None, ticker_method: str = "MANUAL") -> TradingSession:
        db = SessionLocal()
        try:
            logger.info(f"Creating Session '{name}'. Method: {ticker_method}")
            # 1. Create DB Entry with configuration
            session = TradingSession(
                name=name, 
                mode=mode, 
                status=SessionStatus.CREATED, 
                initial_balance=initial_balance,
                buy_strategy_name=buy_strategy,
                sell_strategy_name=sell_strategy,
                ticker_selection_method=ticker_method
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            
            # Save Tickers to DB (if MANUAL)
            from models.session import SessionTicker
            if tickers:
                for ticker in tickers:
                    db_ticker = SessionTicker(session_id=session.id, symbol=ticker)
                    db.add(db_ticker)
            
            # Legacy: Save separate strategies if provided (for view compatibility)
            from models.session import SessionStrategy
            if strategy_names:
                for s_name in strategy_names:
                    db_strat = SessionStrategy(session_id=session.id, strategy_name=s_name, is_active=True)
                    db.add(db_strat)
            elif buy_strategy and sell_strategy:
                 # Add "Composite" virtual entry for viewing
                 db.add(SessionStrategy(session_id=session.id, strategy_name=f"Composite: {buy_strategy}/{sell_strategy}", is_active=True))

            db.commit()
            
            # 2. Instantiate Strategies
            strategies = []
            
            # If explicit buy/sell provided, use Composite
            if buy_strategy and sell_strategy:
                from strategies.composite_strategy import CompositeStrategy
                comp_name = f"{buy_strategy}_{sell_strategy}_Composite"
                comp_strat = CompositeStrategy(comp_name, buy_strategy, sell_strategy)
                strategies.append(comp_strat)
            else:
                 # Legacy list support
                 for s_name in strategy_names:
                    strategy = self._create_strategy(s_name)
                    if strategy:
                        strategies.append(strategy)
            
            if not strategies:
                logger.warning(f"No valid strategies for session {session.id}. Using Default.")
                from strategies.moving_average import MovingAverageCrossover
                strategies.append(MovingAverageCrossover("DefaultGoldenCross", 10, 30))
            
            # Initialize Engine
            engine = self._init_engine(session, strategies, tickers, initial_balance)

            with self._lock:
                self._engines[session.id] = engine
                
            return session
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            db.rollback()
            raise e
        finally:
            db.close()

    def _create_strategy(self, name: str):
        from strategies.factory import StrategyFactory
        return StrategyFactory.create_strategy(name)

    def _init_engine(self, session_obj, strategies, tickers, balance):
        mode_paper = True
        if hasattr(session_obj, 'mode'):
            mode_paper = session_obj.mode == "PAPER"
            
        return TradingEngine(
            strategies=strategies,
            tickers=tickers,
            interval=5, # Fast scanning for demo
            paper_trading=mode_paper,
            session_id=session_obj.id,
            initial_balance=balance
        )
    
    def start_session(self, session_id: int):
        with self._lock:
            if session_id in self._threads and self._threads[session_id].is_alive():
                return # Already running
            
            if session_id not in self._engines:
                # Attempt to revive from DB
                db = SessionLocal()
                try:
                    s = db.query(TradingSession).get(session_id)
                    if not s:
                        raise ValueError("Session not found in DB")
                    
                    # Revive from DB
                    logger.info(f"Reviving session {session_id} from DB")
                    
                    strategies = []
                    
                    # 1. Check for Composite Configuration
                    if s.buy_strategy_name and s.sell_strategy_name:
                         from strategies.composite_strategy import CompositeStrategy
                         comp_name = f"{s.buy_strategy_name}_{s.sell_strategy_name}_Composite"
                         strategies.append(CompositeStrategy(comp_name, s.buy_strategy_name, s.sell_strategy_name))
                    else:
                        # 2. Legacy Strategy List
                        strategy_names = []
                        if s.strategies:
                             strategy_names = [st.strategy_name for st in s.strategies if st.is_active]
                        
                        for name in strategy_names:
                            # Avoid duplicates or composite markers
                            if "Composite:" in name: continue
                            strat = self._create_strategy(name)
                            if strat: strategies.append(strat)
                    
                    if not strategies:
                        logger.info("No active strategies found in DB, using defaults")
                        default_strat = self._create_strategy("GoldenCross_SMA")
                        if default_strat: strategies.append(default_strat)
                    
                    # Load Tickers from DB
                    tickers = []
                    if s.tickers:
                        tickers = [t.symbol for t in s.tickers]
                    
                    if not tickers:
                        logger.warning(f"Session {session_id} has no tickers assigned.")
                    
                    engine = self._init_engine(s, strategies, tickers, s.initial_balance)
                    self._engines[session_id] = engine
                finally:
                    db.close()
            
            engine = self._engines[session_id]
            
            # Update DB status
            db = SessionLocal()
            try:
                s = db.query(TradingSession).get(session_id)
                s.status = SessionStatus.RUNNING
                db.commit()
            finally:
                db.close()
            
            # Start Thread
            if session_id not in self._threads or not self._threads[session_id].is_alive():
                thread = threading.Thread(target=engine.run, daemon=True)
                self._threads[session_id] = thread
                thread.start()

    def stop_session(self, session_id: int):
        with self._lock:
            if session_id in self._engines:
                self._engines[session_id].is_running = False
                # Update DB
                db = SessionLocal()
                s = db.query(TradingSession).get(session_id)
                s.status = SessionStatus.STOPPED
                db.commit()
                db.close()

    def get_active_sessions(self):
        return list(self._engines.keys())
    
    def remove_session(self, session_id: int):
        """Remove session from memory"""
        with self._lock:
            if session_id in self._engines:
                del self._engines[session_id]
            if session_id in self._threads:
                del self._threads[session_id]

    def add_session_ticker(self, session_id: int, ticker: str):
        """Add a ticker to the session"""
        from models.session import SessionTicker
        db = SessionLocal()
        try:
            # Check if exists
            exists = db.query(SessionTicker).filter_by(session_id=session_id, symbol=ticker).first()
            if not exists:
                t = SessionTicker(session_id=session_id, symbol=ticker)
                db.add(t)
                db.commit()
                
            # Update Engine if running
            with self._lock:
                if session_id in self._engines:
                    engine = self._engines[session_id]
                    if ticker not in engine.tickers:
                        # Replace list safely
                        engine.tickers = engine.tickers + [ticker]
        finally:
            db.close()

    def remove_session_ticker(self, session_id: int, ticker: str):
        """Remove a ticker from the session"""
        from models.session import SessionTicker
        db = SessionLocal()
        try:
            # Delete from DB
            db.query(SessionTicker).filter_by(session_id=session_id, symbol=ticker).delete()
            db.commit()
            
            # Update Engine if running
            with self._lock:
                if session_id in self._engines:
                    engine = self._engines[session_id]
                    if ticker in engine.tickers:
                        new_tickers = [t for t in engine.tickers if t != ticker]
                        engine.tickers = new_tickers
        finally:
            db.close()

