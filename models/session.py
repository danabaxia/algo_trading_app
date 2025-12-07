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
    def __repr__(self):
        return f"<TradingSession(id={self.id}, name='{self.name}', status='{self.status}')>"
