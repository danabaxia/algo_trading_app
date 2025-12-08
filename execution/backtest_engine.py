import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any
import copy
from models.market_data import MarketDataFetcher

logger = logging.getLogger("BacktestEngine")

class BacktestEngine:
    def __init__(self, strategies, tickers, start_date: str, end_date: str, initial_capital: float = 10000.0):
        """
        :param strategies: List of strategy instances
        :param tickers: List of ticker symbols
        :param start_date: 'YYYY-MM-DD'
        :param end_date: 'YYYY-MM-DD'
        :param initial_capital: float
        """
        self.strategies = strategies
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        
        # Create isolated strategy instances for each ticker to prevents state contamination
        self.ticker_strategies = {
            ticker: [copy.deepcopy(s) for s in strategies] 
            for ticker in tickers
        }
        
        # Initialize all strategies
        for ticker, strats in self.ticker_strategies.items():
            for s in strats:
                try:
                    s.initialize({"ticker": ticker})
                except Exception as e:
                    logger.error(f"Failed to initialize strategy {s.name} for {ticker}: {e}")
        
        self.market_data = MarketDataFetcher()
        self.portfolio_value = initial_capital
        self.cash = initial_capital
        self.holdings = {t: 0 for t in tickers}
        self.equity_curve = [] # List of {date, value}
        self.trades = [] # List of trade dicts
        
        self.data_map = {}

    def run(self) -> Dict[str, Any]:
        """
        Run the backtest.
        """
        logger.info(f"Starting backtest for {self.tickers} from {self.start_date} to {self.end_date}")
        
        # 1. Fetch Data
        for ticker in self.tickers:
            try:
                df = self.market_data.get_daily_history(ticker, days=1825)
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.sort_values('date')
                    # Filter by date range
                    start_dt = pd.to_datetime(self.start_date)
                    end_dt = pd.to_datetime(self.end_date)
                    mask = (df['date'] >= start_dt) & (df['date'] <= end_dt)
                    filtered_df = df.loc[mask].reset_index(drop=True)
                    if not filtered_df.empty:
                        self.data_map[ticker] = filtered_df
                    else:
                        logger.warning(f"No data for {ticker} in range {self.start_date}-{self.end_date}")
            except Exception as e:
                logger.error(f"Error fetching data for backtest ({ticker}): {e}")

        if not self.data_map:
            return {"error": "No data found for any ticker in the specified range"}

        # 2. Synchronize and Loop
        # Find all unique dates across all tickers to simulate a unified timeline
        all_dates = sorted(list(set().union(*[d['date'].tolist() for d in self.data_map.values()])))
        
        # Trackers for Per-Stock Performance
        stock_cash_flow = {t: 0.0 for t in self.tickers}
        stock_curves = {t: [] for t in self.tickers} # List of floats
        stock_trades_count = {t: 0 for t in self.tickers}

        for current_date in all_dates:
            dt_str = current_date.strftime("%Y-%m-%d")
            
            # --- PRE-TRADE VALUATION (Mark to Market) ---
            current_holdings_val = 0
            ticker_prices = {}
            
            for ticker in self.tickers:
                if ticker in self.data_map:
                    # Find price for this date
                    row = self.data_map[ticker][self.data_map[ticker]['date'] == current_date]
                    if not row.empty:
                        price = row.iloc[0]['close']
                        ticker_prices[ticker] = price
                        current_holdings_val += self.holdings[ticker] * price
            
            self.portfolio_value = self.cash + current_holdings_val
            self.equity_curve.append({"date": dt_str, "value": self.portfolio_value})
            
            # --- SNAPSHOT PER-STOCK CURVE ---
            for ticker in self.tickers:
                p = ticker_prices.get(ticker, 0)
                # Value = Cash Flow + Asset Value
                val = stock_cash_flow[ticker] + (self.holdings[ticker] * p)
                stock_curves[ticker].append(val)

            # --- PROCESS STRATEGIES ---
            for ticker in self.tickers:
                if ticker in ticker_prices:
                    price = ticker_prices[ticker]
                    
                    data_point = {
                        "price": price, 
                        "symbol": ticker, 
                        "timestamp": current_date
                    }
                    
                    # Use ticker-specific strategies
                    active_strategies = self.ticker_strategies.get(ticker, [])
                    
                    for strategy in active_strategies:
                        strategy.on_data(data_point)
                        
                        try:
                            if strategy.should_buy(data_point):
                                # BUY SIGNAL
                                amount_to_invest = self.cash * 0.10
                                if amount_to_invest > price:
                                    qty = int(amount_to_invest / price)
                                    if qty > 0:
                                        cost = qty * price
                                        self.cash -= cost
                                        self.holdings[ticker] += qty
                                        self._record_trade(dt_str, ticker, "BUY", price, qty, strategy.name)
                                        
                                        stock_cash_flow[ticker] -= cost
                                        stock_trades_count[ticker] += 1
                                        
                            elif strategy.should_sell(data_point):
                                # SELL SIGNAL
                                qty = self.holdings[ticker]
                                if qty > 0:
                                    proceeds = qty * price
                                    self.cash += proceeds
                                    self.holdings[ticker] = 0
                                    self._record_trade(dt_str, ticker, "SELL", price, qty, strategy.name)
                                    
                                    stock_cash_flow[ticker] += proceeds
                                    stock_trades_count[ticker] += 1
                                    
                        except Exception as e:
                            logger.error(f"Strategy error on {dt_str}: {e}")

        # Final Calculation
        total_return_pct = 0
        if self.initial_capital > 0:
            total_return_pct = ((self.portfolio_value - self.initial_capital) / self.initial_capital) * 100
            
        # Global Drawdown Calc
        max_drawdown = 0
        peak = -999999999
        for point in self.equity_curve:
            val = point['value']
            if val > peak: peak = val
            dd = (peak - val) / peak
            if dd > max_drawdown: max_drawdown = dd
            
        # Per-Stock Metrics Calculation
        per_stock_stats = {}
        for ticker in self.tickers:
            curve = stock_curves[ticker]
            if not curve:
                per_stock_stats[ticker] = {"pnl": 0, "return_pct": 0, "max_drawdown_pct": 0, "trades": 0}
                continue
                
            final_pnl = curve[-1]
            
            # Drawdown of PnL Curve
            s_peak = -999999999
            s_mdd_val = 0
            for v in curve:
                if v > s_peak: s_peak = v
                dd = s_peak - v
                if dd > s_mdd_val: s_mdd_val = dd
            
            # Convert to %? Only if peak > 0. If peak <= 0, MDD is hard to define in %.
            # We'll return MDD% if Peak > 0, else 0.
            s_mdd_pct = 0
            if s_peak > 0:
                s_mdd_pct = (s_mdd_val / s_peak) * 100
                
            per_stock_stats[ticker] = {
                "pnl": round(final_pnl, 2),
                "max_drawdown_pct": round(s_mdd_pct, 2),
                "trades": stock_trades_count[ticker]
            }

        return {
            "initial_capital": self.initial_capital,
            "final_value": self.portfolio_value,
            "total_return_pct": round(total_return_pct, 2),
            "max_drawdown_pct": round(max_drawdown * 100, 2),
            "total_trades": len(self.trades),
            "equity_curve": self.equity_curve,
            "trades": self.trades,
            "per_stock_performance": per_stock_stats,
            "daily_prices": {
                ticker: [
                    {"date": row['date'].strftime("%Y-%m-%d"), "close": row['close']}
                    for _, row in self.data_map[ticker].iterrows()
                ]
                for ticker in self.data_map
            }
        }

    def _record_trade(self, date, ticker, action, price, qty, strategy):
        self.trades.append({
            "date": date,
            "ticker": ticker,
            "action": action,
            "price": price,
            "quantity": qty,
            "cost": price * qty,
            "strategy": strategy
        })
