from models.database import SessionLocal
from models.strategy_config import StrategyConfig

def list_strategies():
    db = SessionLocal()
    try:
        strats = db.query(StrategyConfig).all()
        print(f"Found {len(strats)} strategies:")
        for s in strats:
            print(f" - {s.name}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_strategies()
