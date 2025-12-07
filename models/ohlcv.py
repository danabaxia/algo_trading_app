from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from models.database import Base

class OHLCV(Base):
    """
    Market Data Table: Open, High, Low, Close, Volume.
    One row per ticker per timestamp.
    """
    __tablename__ = "ohlcv"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    interval = Column(String(10), default="1d") # '1d', '1min', etc.
    
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    
    # Ensure we don't duplicate data for the same candle
    __table_args__ = (
        UniqueConstraint('ticker', 'timestamp', 'interval', name='uq_ticker_time_interval'),
    )

    def __repr__(self):
        return f"<OHLCV({self.ticker}, {self.timestamp}, {self.close})>"
