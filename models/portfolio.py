from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class AccountBalance(Base):
    """
    Tracks the global state of the account (Cash + Equity).
    We typically only have ONE row in this table per SESSION.
    """
    __tablename__ = "account_balance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('trading_sessions.id'), nullable=True) # Link to Session
    mode = Column(String(10), default="PAPER", nullable=False) # 'PAPER' or 'LIVE'
    cash_balance = Column(Float, default=0.0)      # Available cash to trade
    total_equity = Column(Float, default=0.0)      # Cash + Market Value of holdings
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Account(session={self.session_id}: cash=${self.cash_balance:.2f}, equity=${self.total_equity:.2f})>"

class StrategyHolding(Base):
    """
    Tracks the portfolio position FOR A SPECIFIC STRATEGY.
    """
    __tablename__ = "strategy_holdings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('trading_sessions.id'), nullable=True)
    mode = Column(String(10), default="PAPER", nullable=False) # 'PAPER' or 'LIVE'
    strategy_name = Column(String(100), index=True, nullable=False)
    ticker = Column(String(20), index=True, nullable=False)
    
    quantity = Column(Float, default=0.0)
    average_price = Column(Float, default=0.0) # Weighted Average Price
    
    # Optional: Track current stats if we update frequently
    current_price = Column(Float, nullable=True) 
    unrealized_pnl = Column(Float, default=0.0)
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Holding(session={self.session_id}: strategy='{self.strategy_name}', ticker='{self.ticker}', qty={self.quantity:.2f}, avg_price=${self.average_price:.2f})>"
