import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "algo_trading")
    
    # Fallback for local docker/native mismatch if needed, though strictly we should trust .env
    # (Leaving logic simple here)

    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Robinhood
    RH_USERNAME = os.getenv("RH_USERNAME")
    RH_PASSWORD = os.getenv("RH_PASSWORD")
    RH_TOTP = os.getenv("RH_TOTP")

    # API Keys
    FMP_API_KEY = os.getenv("FMP_API_KEY")

settings = Settings()
