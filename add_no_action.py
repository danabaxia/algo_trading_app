from models.database import SessionLocal
from models.strategy_config import StrategyConfig

def add_no_action_strategy():
    db = SessionLocal()
    try:
        exists = db.query(StrategyConfig).filter_by(name="No_Action").first()
        if not exists:
            print("Adding No_Action strategy...")
            strat = StrategyConfig(
                name="No_Action",
                class_name="NoActionStrategy",
                parameters={},
                description="Strategy that never trades. Use for testing or passive monitoring."
            )
            db.add(strat)
            db.commit()
            print("Added successfully.")
        else:
            print("No_Action strategy already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_no_action_strategy()
