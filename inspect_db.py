from sqlalchemy import create_engine, inspect
from config.settings import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

print("Columns in account_balance:")
for col in inspector.get_columns("account_balance"):
    print(f"- {col['name']}")

print("\nColumns in strategy_holdings:")
for col in inspector.get_columns("strategy_holdings"):
    print(f"- {col['name']}")

print("\nTables:")
print(inspector.get_table_names())
