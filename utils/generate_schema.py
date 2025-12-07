import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from sqlalchemy.schema import CreateTable
from models.database import engine, Base
# Import models to register them with Base.metadata
from models.trade_orders import Trade
from models.portfolio import AccountBalance, StrategyHolding
from models.ohlcv import OHLCV
from models.strategy_config import StrategyConfig

def generate_ddl():
    """
    Generates raw SQL CREATE TABLE statements for all defined models
    and writes them to schema.sql.
    """
    print("Generating schema.sql...")
    
    output_file = os.path.join("database", "schema.sql")
    with open(output_file, 'w') as f:
        f.write("-- Auto-generated schema from SQLAlchemy models\n")
        f.write(f"-- Generated at: {os.popen('date /t').read().strip()}\n\n")
        
        # Sort tables by dependency (though usually not strictly needed for just dumping DDL if no FK constraints interfere cyclically)
        for table in Base.metadata.sorted_tables:
            # Compile the DDL using the MySQL dialect configured in 'engine'
            ddl = CreateTable(table).compile(engine)
            f.write(str(ddl).strip())
            f.write(";\n\n")
            
    print(f"Successfully wrote schema.sql with {len(Base.metadata.sorted_tables)} tables.")

if __name__ == "__main__":
    generate_ddl()
