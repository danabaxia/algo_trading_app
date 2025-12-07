import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from .trade_orders import Trade

class PerformanceAnalyzer:
    """
    Analyzes trade history and calculates performance metrics.
    Serves as the feedback loop for strategy optimization.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def fetch_trades(self, limit: int = 1000) -> pd.DataFrame:
        """
        Fetches trades from the database and returns them as a DataFrame.
        """
        trades = self.db.query(Trade).filter(Trade.status == 'FILLED').limit(limit).all()
        if not trades:
            return pd.DataFrame()
        
        data = [
            {
                "id": t.id,
                "ticker": t.ticker,
                "action": t.action,
                "quantity": t.quantity,
                "price": t.price,
                "timestamp": t.timestamp,
                "strategy": t.strategy_name
            }
            for t in trades
        ]
        return pd.DataFrame(data)

    def calculate_metrics(self) -> dict:
        """
        Calculates key performance metrics from the trade history.
        """
        df = self.fetch_trades()
        if df.empty:
            return {"message": "No filled trades found for analysis."}

        # Calculate PnL per trade (Simplified: assumes FIFO or paired trades for accurate PnL, 
        # but here we approximate by assuming Sell Price - Buy Price for same ticker sequence)
        # Note: A proper PnL requires a ledger system. For this summary, we track finished round trips.
        
        # Determine strict PnL requires matching Buys and Sells. 
        # For a simple metric, we can check realized PnL from closed positions.
        # This implementation requires a more complex accounting, but we will start with 
        # checking "Total Buy Vol" vs "Total Sell Vol" and "Current Equity".
        
        # Let's stick to simple stats for now:
        total_trades = len(df)
        buys = df[df['action'] == 'BUY']
        sells = df[df['action'] == 'SELL']
        
        avg_buy_price = buys['price'].mean() if not buys.empty else 0
        avg_sell_price = sells['price'].mean() if not sells.empty else 0
        
        # A rough "win rate" estimate is hard without knowing which sell matched which buy.
        # So we will return basic stats:
        
        metrics = {
            "total_trades": total_trades,
            "total_buy_orders": len(buys),
            "total_sell_orders": len(sells),
            "avg_buy_price": round(avg_buy_price, 2),
            "avg_sell_price": round(avg_sell_price, 2),
            "last_trade_time": df['timestamp'].max()
        }
        
        return metrics

    def calculate_drawdown(self, equity_curve: list) -> float:
        """
        Calculates the maximum drawdown from an equity curve.
        :param equity_curve: List of portfolio values over time.
        :return: Max drawdown percentage.
        """
        if not equity_curve:
            return 0.0
            
        peak = equity_curve[0]
        max_drawdown = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                
        return max_drawdown