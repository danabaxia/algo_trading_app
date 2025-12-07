from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from .database import Base

class StrategyConfig(Base):
    """
    Table to register strategies and their dynamic configuration.
    This allows the Engine to load 'Active' strategies from DB instead of hardcoding.
    """
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False) # e.g. "GoldenCross_AAPL"
    
    class_name = Column(String(100), nullable=False) # e.g. "MovingAverageCrossover"
    
    # Store parameters as JSON: {"short_window": 10, "long_window": 30}
    parameters = Column(JSON, nullable=True) 
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<StrategyConfig(name='{self.name}', class='{self.class_name}', active={self.is_active})>"
