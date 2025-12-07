from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config.settings import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# List of tables to drop in order (child first)
tables = [
    "trades",
    "strategy_holdings",
    "account_balance",
    "strategies",
    "trading_sessions",
    "ohlcv",
    "alembic_version"
]

print("Starting forceful cleanup...")
with engine.connect() as conn:
    # Disable FK checks to allow dropping parents
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    
    for t in tables:
        try:
            print(f"Dropping {t}...")
            conn.execute(text(f"DROP TABLE IF EXISTS {t}"))
            print(f"Dropped {t}")
        except Exception as e:
            print(f"Error dropping {t}: {e}")
            
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    conn.commit()

print("Cleanup complete.")
