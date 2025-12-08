from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class SessionStatus(str, enum.Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"

class TradingSession(Base):
    __tablename__ = "trading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    mode = Column(String(10), default="PAPER") # 'PAPER' or 'LIVE'
    status = Column(String(20), default=SessionStatus.CREATED)
    
    initial_balance = Column(Float, default=10000.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    strategies = relationship("SessionStrategy", back_populates="session", cascade="all, delete-orphan")
    tickers = relationship("SessionTicker", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TradingSession(id={self.id}, name='{self.name}', status='{self.status}')>"

from sqlalchemy import ForeignKey, Boolean

class SessionStrategy(Base):
    __tablename__ = "session_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("trading_sessions.id"))
    strategy_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    
    session = relationship("TradingSession", back_populates="strategies")

class SessionTicker(Base):
    __tablename__ = "session_tickers"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("trading_sessions.id"))
    symbol = Column(String(20), nullable=False)
    
    session = relationship("TradingSession", back_populates="tickers")

