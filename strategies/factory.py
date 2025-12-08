from models.database import SessionLocal
from models.strategy_config import StrategyConfig
from strategies.moving_average import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.momentum_strategy import MomentumStrategy
import logging

logger = logging.getLogger("StrategyFactory")

class StrategyFactory:
    @staticmethod
    def create_strategy(strategy_name: str, db_session=None):
        """
        Creates a strategy instance based on the configuration in the database.
        """
        local_db = False
        if db_session is None:
            db_session = SessionLocal()
            local_db = True
            
        try:
            config = db_session.query(StrategyConfig).filter_by(name=strategy_name).first()
            if not config:
                logger.warning(f"Strategy config for '{strategy_name}' not found. Using defaults if possible.")
                # Fallback for legacy hardcoded names if DB lookup fails
                if strategy_name == "GoldenCross_SMA":
                    return MovingAverageCrossover(strategy_name, 10, 30)
                elif strategy_name == "RSI_Oscillator":
                    return RSIStrategy(strategy_name, 14, 30, 70)
                elif strategy_name == "MACD_Crossover":
                    return MACDStrategy(strategy_name, 12, 26, 9)
                elif strategy_name == "Bollinger_MeanReversion":
                    return BollingerBandsStrategy(strategy_name, 20, 2)
                elif strategy_name == "Momentum_Breakout":
                    return MomentumStrategy(strategy_name, 10, 0.02)
                return None

            params = config.parameters or {}
            class_name = config.class_name
            
            if class_name == "MovingAverageCrossover":
                return MovingAverageCrossover(
                    strategy_name, 
                    short_window=params.get("short_window", 10), 
                    long_window=params.get("long_window", 30)
                )
            elif class_name == "RSIStrategy":
                return RSIStrategy(
                    strategy_name, 
                    period=params.get("period", 14), 
                    oversold=params.get("oversold", 30), 
                    overbought=params.get("overbought", 70)
                )
            elif class_name == "MACDStrategy":
                return MACDStrategy(
                    strategy_name, 
                    fast_period=params.get("fast_period", 12), 
                    slow_period=params.get("slow_period", 26), 
                    signal_period=params.get("signal_period", 9)
                )
            elif class_name == "BollingerBandsStrategy":
                return BollingerBandsStrategy(
                    strategy_name, 
                    period=params.get("period", 20), 
                    num_std=params.get("num_std", 2)
                )
            elif class_name == "MomentumStrategy":
                return MomentumStrategy(
                    strategy_name, 
                    lookback_period=params.get("lookback_period", 10), 
                    threshold=params.get("threshold", 0.02)
                )
            elif class_name == "NoActionStrategy":
                from strategies.no_action import NoActionStrategy
                return NoActionStrategy(strategy_name)
            
            logger.error(f"Unknown strategy class: {class_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error creating strategy {strategy_name}: {e}")
            return None
        finally:
            if local_db:
                db_session.close()
