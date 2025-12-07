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

    def create_session(self, name: str, strategy_names: List[str], tickers: List[str], initial_balance: float = 10000.0, mode: str = "PAPER") -> TradingSession:
        db = SessionLocal()
        try:
            # 1. Create DB Entry with initial balance
            session = TradingSession(name=name, mode=mode, status=SessionStatus.CREATED, initial_balance=initial_balance)
            db.add(session)
            db.commit()
            db.refresh(session)
            
            # 2. Instantiate Strategies based on names
            strategies = []
            for s_name in strategy_names:
                strategy = self._create_strategy(s_name)
                if strategy:
                    strategies.append(strategy)
            
            if not strategies:
                logger.warning(f"No valid strategies for session {session.id}")
                # Use default strategy
                from strategies.moving_average import MovingAverageCrossover
                strategies.append(MovingAverageCrossover("DefaultGoldenCross", 10, 30))
            
            # Initialize Engine with custom tickers and initial balance
            engine = self._init_engine(session, strategies, tickers, initial_balance)
            with self._lock:
                self._engines[session.id] = engine
                
            return session
        finally:
            db.close()

    def _create_strategy(self, strategy_name: str):
        """Factory method to create strategy instances"""
        from strategies.moving_average import MovingAverageCrossover
        from strategies.rsi_strategy import RSIStrategy
        from strategies.macd_strategy import MACDStrategy
        from strategies.bollinger_bands import BollingerBandsStrategy
        from strategies.momentum_strategy import MomentumStrategy
        
        # Map strategy names to classes
        if "GoldenCross" in strategy_name or "SMA" in strategy_name:
            return MovingAverageCrossover(strategy_name, short_window=10, long_window=30)
        elif "RSI" in strategy_name:
            return RSIStrategy(strategy_name, period=14, oversold=30, overbought=70)
        elif "MACD" in strategy_name:
            return MACDStrategy(strategy_name, fast_period=12, slow_period=26, signal_period=9)
        elif "Bollinger" in strategy_name:
            return BollingerBandsStrategy(strategy_name, period=20, num_std=2)
        elif "Momentum" in strategy_name:
            return MomentumStrategy(strategy_name, lookback_period=10, threshold=0.02)
        else:
            logger.warning(f"Unknown strategy: {strategy_name}")
            return None

    def _init_engine(self, session: TradingSession, strategies: list, tickers: List[str], initial_balance: float) -> TradingEngine:
        broker = None
        paper = (session.mode == "PAPER")
        
        if not paper:
             # Live Broker Setup (Simplified for one global login for now)
             broker = RobinhoodBroker()
             broker.login()

        engine = TradingEngine(
            strategies=strategies,
            tickers=tickers,  # Use custom tickers
            interval=5,
            paper_trading=paper,
            broker=broker,
            session_id=session.id,  # Pass session_id in constructor
            initial_balance=initial_balance  # Use custom initial balance
        )
        return engine

    def start_session(self, session_id: int):
        with self._lock:
            if session_id in self._threads and self._threads[session_id].is_alive():
                return # Already running
            
            if session_id not in self._engines:
                # Try to revive from DB? (Advanced)
                # For now assumes created in memory
                raise ValueError("Session not found in memory")
            
            engine = self._engines[session_id]
            
            # Update DB status
            db = SessionLocal()
            s = db.query(TradingSession).get(session_id)
            s.status = SessionStatus.RUNNING
            db.commit()
            db.close()
            
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

