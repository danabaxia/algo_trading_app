import time
import logging
from datetime import datetime
from models.database import SessionLocal
from models.trade_orders import Trade
from models.portfolio import AccountBalance, StrategyHolding
from models.market_data import MarketDataFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TradingEngine")

class TradingEngine:
    def __init__(self, strategies, tickers, interval=60, paper_trading=True, broker=None, session_id=None):
        """
        Initializes the Trading Engine.
        :param session_id: Link to the specific trading session in DB.
        """
        self.strategies = strategies
        self.tickers = tickers
        self.interval = interval
        self.paper_trading = paper_trading
        self.broker = broker
        self.session_id = session_id # New: Specific session ID
        self.is_running = False
        self.db = SessionLocal()
        self.data_fetcher = MarketDataFetcher()
        
        # Initialize Account if needed
        self._ensure_account_exists()

    def _ensure_account_exists(self):
        """Ensure an account row exists for the current session."""
        
        # If session_id is provided, use it. Otherwise fall back to mode (legacy support)
        if self.session_id:
            account = self.db.query(AccountBalance).filter_by(session_id=self.session_id).first()
            if not account:
                logger.info(f"Initializing new Account for Session {self.session_id}")
                # Use mode from session_id logic or default
                mode_str = "PAPER" if self.paper_trading else "LIVE"
                acc = AccountBalance(session_id=self.session_id, mode=mode_str, cash_balance=10000.0, total_equity=10000.0)
                self.db.add(acc)
                self.db.commit()
        else:
            # Legacy Logic
            mode_str = "PAPER" if self.paper_trading else "LIVE"
            account = self.db.query(AccountBalance).filter_by(mode=mode_str).first()
            if not account:
                acc = AccountBalance(mode=mode_str, cash_balance=10000.0, total_equity=10000.0)
                self.db.add(acc)
                self.db.commit()

    def run(self):
        self.is_running = True
        logger.info(f"Trading Engine started (Session: {self.session_id}, Paper: {self.paper_trading})")
        
        try:
            while self.is_running:
                logger.info("Starting new scan cycle...")
                for ticker in self.tickers:
                    self.process_ticker(ticker)
                
                # Sleep for the interval
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("Stopping Trading Engine...")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.shutdown()

    def process_ticker(self, ticker):
        try:
            # 1. Fetch Market Data
            price = self.data_fetcher.get_price(ticker)
            if not price:
                logger.warning(f"Could not fetch price for {ticker}. Skipping.")
                return

            data = {"price": price, "symbol": ticker, "timestamp": datetime.utcnow()}
            logger.info(f"Analying {ticker} @ ${price}")
            
            # 2. Check Strategies
            for strategy in self.strategies:
                if strategy.should_buy(data):
                    logger.info(f"Strategy {strategy.name} signaled BUY for {ticker}")
                    self.execute_trade(ticker, "BUY", 1, price, strategy.name)
                    
                elif strategy.should_sell(data):
                    logger.info(f"Strategy {strategy.name} signaled SELL for {ticker}")
                    self.execute_trade(ticker, "SELL", 1, price, strategy.name)

        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")

    def execute_trade(self, ticker, action, quantity, price, strategy_name):
        """
        Executes trade linked to the specific session_id.
        """
        try:
            total_cost = quantity * price
            mode_str = "PAPER" if self.paper_trading else "LIVE"
            
            # --- LIVE TRADING ---
            if not self.paper_trading:
                if not self.broker:
                    logger.error("Live trading requested but no Broker instance provided!")
                    return
                # Execute on Broker
                logger.info(f"Sending {action} order to Broker...")
                order = self.broker.place_order(ticker, quantity, action, order_type="market")
                if not order:
                    logger.error("Broker order failed.")
                    return
                logger.info(f"Broker Order Placed: {order}")

            # --- DB RECORDING ---
            
            # 1. Update Balances (Paper Logic)
            if self.paper_trading:
                # Query by session_id if available, else mode
                if self.session_id:
                    account = self.db.query(AccountBalance).filter_by(session_id=self.session_id).first()
                else:
                    account = self.db.query(AccountBalance).filter_by(mode=mode_str).first() # Fallback

                if action == "BUY":
                    if account.cash_balance < total_cost:
                        logger.warning(f"INSUFFICIENT FUNDS: Need ${total_cost}, have ${account.cash_balance}")
                        return
                    account.cash_balance -= total_cost
                elif action == "SELL":
                    # Check holdings by session
                    query = self.db.query(StrategyHolding).filter_by(strategy_name=strategy_name, ticker=ticker)
                    if self.session_id:
                        query = query.filter_by(session_id=self.session_id)
                    else:
                        query = query.filter_by(mode=mode_str)
                    
                    holding = query.first()
                    if not holding or holding.quantity < quantity:
                        logger.warning(f"INSUFFICIENT SHARES: Need {quantity}, have {holding.quantity if holding else 0}")
                        return
                    account.cash_balance += total_cost

            # 2. Record Trade in DB
            # Use session_id if available
            trade = Trade(
                session_id=self.session_id,
                mode=mode_str,
                ticker=ticker,
                action=action,
                quantity=quantity,
                price=price,
                total_cost=total_cost,
                strategy_name=strategy_name,
                status="FILLED" if self.paper_trading else "SUBMITTED"
            )
            self.db.add(trade)
            
            # 3. Update Holdings (Paper Mode)
            if self.paper_trading:
                query = self.db.query(StrategyHolding).filter_by(strategy_name=strategy_name, ticker=ticker)
                if self.session_id:
                    query = query.filter_by(session_id=self.session_id)
                else:
                    query = query.filter_by(mode=mode_str)
                holding = query.first()
                
                if not holding:
                    holding = StrategyHolding(
                        session_id=self.session_id,
                        mode=mode_str,
                        strategy_name=strategy_name, 
                        ticker=ticker, 
                        quantity=0, 
                        average_price=0
                    )
                    self.db.add(holding)
                
                if action == "BUY":
                    current_val = holding.quantity * holding.average_price
                    new_val = quantity * price
                    holding.quantity += quantity
                    holding.average_price = (current_val + new_val) / holding.quantity
                elif action == "SELL":
                    holding.quantity -= quantity
            
            self.db.commit()
            if self.paper_trading:
                # Re-fetch account for logging
                if self.session_id:
                     updated_acc = self.db.query(AccountBalance).filter_by(session_id=self.session_id).first()
                else:
                     updated_acc = self.db.query(AccountBalance).filter_by(mode=mode_str).first()
                logger.info(f"[Session {self.session_id}] Executed {action} {quantity} {ticker}. Cash: ${updated_acc.cash_balance:.2f}")
            else:
                logger.info(f"[{mode_str}] Trade recorded in DB.")
            
        except Exception as e:
            logger.error(f"Failed to record trade: {e}")
            self.db.rollback()

    def shutdown(self):
        self.is_running = False
        self.db.close()
        logger.info("Trading Engine shutdown complete.")
