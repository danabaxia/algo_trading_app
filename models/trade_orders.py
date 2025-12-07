from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from .database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True, nullable=False)
    action = Column(String(10), nullable=False)  # 'BUY' or 'SELL'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)      # Price per share
    total_cost = Column(Float)                 # (quantity * price) + fees
    fees = Column(Float, default=0.0)
    order_id = Column(String(100), unique=True, nullable=True) # Broker Order ID
    session_id = Column(Integer, ForeignKey('trading_sessions.id'), nullable=True)
    mode = Column(String(10), default="PAPER", nullable=False) # 'PAPER' or 'LIVE'
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    strategy_name = Column(String(100), nullable=False)
    status = Column(String(20), default="PENDING")  # 'FILLED', 'PENDING', 'CANCELLED', 'FAILED'

    def __repr__(self):
        return f"<Trade(id={self.id}, mode='{self.mode}', strategy='{self.strategy_name}', ticker='{self.ticker}', {self.action} {self.quantity}, status='{self.status}')>"
