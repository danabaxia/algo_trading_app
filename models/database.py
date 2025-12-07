from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.settings import settings

# Create the SQLAlchemy engine
# Note: pool_recycle is recommended for MySQL to prevent connection timeouts
engine = create_engine(settings.DATABASE_URL, pool_recycle=3600)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for our models to inherit from
Base = declarative_base()

def init_db():
    """
    Initializes the database by creating all tables defined in models.
    """
    # Import models here to ensure they are registered with Base.metadata
    from models.trade_orders import Trade
    from models.portfolio import AccountBalance, StrategyHolding
    from models.session import TradingSession
    
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency helper to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
