-- Auto-generated schema from SQLAlchemy models
-- Generated at: Sat 12/06/2025

CREATE TABLE account_balance (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	cash_balance FLOAT, 
	total_equity FLOAT, 
	last_updated DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE ohlcv (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	ticker VARCHAR(20) NOT NULL, 
	timestamp DATETIME NOT NULL, 
	`interval` VARCHAR(10), 
	open FLOAT, 
	high FLOAT, 
	low FLOAT, 
	close FLOAT, 
	volume FLOAT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_ticker_time_interval UNIQUE (ticker, timestamp, `interval`)
);

CREATE TABLE strategies (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(100) NOT NULL, 
	class_name VARCHAR(100) NOT NULL, 
	parameters JSON, 
	is_active BOOL, 
	created_at DATETIME, 
	updated_at DATETIME, 
	description TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE TABLE strategy_holdings (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	strategy_name VARCHAR(100) NOT NULL, 
	ticker VARCHAR(20) NOT NULL, 
	quantity FLOAT, 
	average_price FLOAT, 
	current_price FLOAT, 
	unrealized_pnl FLOAT, 
	last_updated DATETIME, 
	PRIMARY KEY (id)
);

CREATE TABLE trades (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	ticker VARCHAR(20) NOT NULL, 
	action VARCHAR(10) NOT NULL, 
	quantity FLOAT NOT NULL, 
	price FLOAT NOT NULL, 
	total_cost FLOAT, 
	fees FLOAT, 
	order_id VARCHAR(100), 
	timestamp DATETIME, 
	strategy_name VARCHAR(100) NOT NULL, 
	status VARCHAR(20), 
	PRIMARY KEY (id), 
	UNIQUE (order_id)
);

